<#
.SYNOPSIS
Install or update the claude-setup files for Claude Code.

.DESCRIPTION
Clones or pulls the setup repo, then copies:
  AGENTS.md, agents\           into your home folder
  CLAUDE.md, skills\, hooks\   into the Claude config folder
($env:CLAUDE_CONFIG_DIR, or $HOME\.claude when it is unset). A file that
exists and differs is backed up as <file>.bak-<time> before it is replaced.
Saves the projects root (-ProjectsRoot) and creates that folder. Then adds
the two hooks to settings.json when Python is found, leaving every
other setting and hook as it is (settings.json is backed up first).
Safe to re-run: a second run with nothing new changes nothing.
Works in Windows PowerShell 5.1 and PowerShell 7.

.PARAMETER DryRun
Print every change, make none.

.PARAMETER Source
Use this folder as the setup files instead of cloning (tests, offline use).

.PARAMETER ProjectsRoot
The folder that holds your projects, INDEX.md and archive\. Saved in
agents\projects-root.txt on the first run (default $HOME\projects); pass it
again to change it.
#>
param(
    [switch]$DryRun,
    [string]$Source,
    [string]$ProjectsRoot,
    [string]$HomeDir = $HOME,
    [string]$ConfigDir,
    [string]$RepoDir,
    [string]$RepoUrl = "https://github.com/b1ggb3n/claude-setup.git"
)
$ErrorActionPreference = "Stop"

if (-not $ConfigDir) {
    if ($env:CLAUDE_CONFIG_DIR) { $ConfigDir = $env:CLAUDE_CONFIG_DIR }
    else { $ConfigDir = Join-Path $HomeDir ".claude" }
}
if (-not $RepoDir) { $RepoDir = Join-Path $HomeDir "claude-setup" }
$TempClone = $null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Utf8 = New-Object System.Text.UTF8Encoding $false
$script:Changes = 0

function Say($msg) {
    if ($DryRun) { Write-Host "would $msg" } else { Write-Host $msg }
    $script:Changes++
}

# 1. Get the setup files.
if ($Source) {
    $src = (Resolve-Path -LiteralPath $Source).Path
} elseif (Test-Path -LiteralPath (Join-Path $RepoDir ".git")) {
    $src = $RepoDir
    if ($DryRun) { Write-Host "would pull $RepoDir (dry run uses it as it is)" }
    else { git -C $RepoDir pull --ff-only --quiet; if ($LASTEXITCODE) { throw "git pull failed in $RepoDir" } }
} elseif (Test-Path -LiteralPath $RepoDir) {
    throw "$RepoDir exists and is not a git clone; move it or pass -RepoDir"
} else {
    $target = $RepoDir
    if ($DryRun) {
        Write-Host "would clone $RepoUrl to $RepoDir (dry run clones to a temp folder)"
        $target = Join-Path ([IO.Path]::GetTempPath()) "claude-setup-$Stamp"
    }
    git clone --quiet $RepoUrl $target; if ($LASTEXITCODE) { throw "git clone failed" }
    $src = $target
    if ($DryRun) { $TempClone = $target }
}

# 2. Find a working Python. "python3" on Windows can be the Microsoft Store
# alias, so each candidate is test-run.
$Python = $null
foreach ($cand in @(@("py", "-3"), @("python3"), @("python"))) {
    if (-not (Get-Command $cand[0] -ErrorAction SilentlyContinue)) { continue }
    $pyArgs = @($cand | Select-Object -Skip 1) + @("-c", "print(1)")
    try { $out = & $cand[0] @pyArgs 2>$null } catch { continue }
    if ($LASTEXITCODE -eq 0 -and "$out".Trim() -eq "1") { $Python = $cand; break }
}

# Adds the hook groups to settings.json. Python's json keeps every other
# setting as it is; a file that does not parse stops the install untouched.
# Args: settings path, python command, hook folder, dry (0/1), stamp.
$MergePy = @'
import json, os, shutil, sys
path, py, hook_dir, dry, stamp = sys.argv[1:6]
dry = dry == "1"
HOOKS = [("UserPromptSubmit", None, "context_alarm.py"),
         ("PostToolUse", "Edit|Write", "post_edit_check.py")]
settings = {}
if os.path.exists(path):
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    if raw.strip():
        try:
            settings = json.loads(raw)
        except ValueError as e:
            sys.exit(f"{path} is not valid JSON ({e}); fix it, then run again. Nothing changed.")
    if not isinstance(settings, dict):
        sys.exit(f"{path} is not a JSON object; nothing changed.")
hooks = settings.setdefault("hooks", {})
added = []
for event, matcher, script in HOOKS:
    groups = hooks.setdefault(event, [])
    # Already there (any command naming the script, as installed or by hand)?
    if any(script in str(h.get("command", "")) for g in groups for h in g.get("hooks", [])):
        continue
    group = {"matcher": matcher} if matcher else {}
    group["hooks"] = [{"type": "command", "command": f'{py} -I "{hook_dir}/{script}"', "timeout": 10}]
    groups.append(group)
    added.append(f"add the {script} hook to {event} in {path}")
if added and not dry:
    if os.path.exists(path):
        shutil.copy2(path, f"{path}.bak-{stamp}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")
print("\n".join(added))
'@
$MergeFile = Join-Path ([IO.Path]::GetTempPath()) "claude-setup-merge-$Stamp.py"
[IO.File]::WriteAllText($MergeFile, $MergePy, $Utf8)
# Forward slashes: Claude Code on Windows runs hooks through Git Bash.
$hookDir = (Join-Path $ConfigDir "hooks") -replace '\\', '/'
$settingsPath = Join-Path $ConfigDir "settings.json"

function Merge-Settings($dry) {
    $pyArgs = @($Python | Select-Object -Skip 1) + @("-I", $MergeFile, $settingsPath, ($Python -join " "), $hookDir, $dry, $Stamp)
    $out = & $Python[0] @pyArgs
    if ($LASTEXITCODE) { throw "settings.json merge failed (see above)" }
    return @($out | Where-Object { $_ })
}

try {
    # Check settings.json first (dry), so a bad file stops before any copy.
    if ($Python) { $planned = Merge-Settings "1" }

    # 3. Copy files. (repo path, destination root)
    $Map = @(
        @("AGENTS.md", $HomeDir),
        @("agents", $HomeDir),
        @("CLAUDE.md", $ConfigDir),
        @("skills", $ConfigDir),
        @("hooks", $ConfigDir)
    )

    function Install-File($from, $to) {
        if (Test-Path -LiteralPath $to) {
            if ((Get-FileHash -LiteralPath $from).Hash -eq (Get-FileHash -LiteralPath $to).Hash) { return }
            Say "back up $to to $to.bak-$Stamp and replace it"
            if (-not $DryRun) { Copy-Item -LiteralPath $to "$to.bak-$Stamp" }
        } else {
            Say "copy $to"
        }
        if (-not $DryRun) {
            New-Item -ItemType Directory -Force (Split-Path $to) | Out-Null
            Copy-Item -LiteralPath $from $to -Force
        }
    }

    foreach ($m in $Map) {
        $from = Join-Path $src $m[0]
        if (-not (Test-Path -LiteralPath $from)) { throw "missing in the setup files: $($m[0])" }
        if (Test-Path -LiteralPath $from -PathType Container) {
            $base = (Resolve-Path -LiteralPath $from).Path
            foreach ($f in Get-ChildItem -LiteralPath $from -Recurse -File) {
                $rel = $f.FullName.Substring($base.Length).TrimStart('\', '/')
                Install-File $f.FullName (Join-Path (Join-Path $m[1] $m[0]) $rel)
            }
        } else {
            Install-File $from (Join-Path $m[1] $m[0])
        }
    }

    # 4. Projects root: saved once, changed only when -ProjectsRoot is passed.
    $rootFile = Join-Path (Join-Path $HomeDir "agents") "projects-root.txt"
    $savedRoot = $null
    if (Test-Path -LiteralPath $rootFile) { $savedRoot = ([IO.File]::ReadAllText($rootFile)).Trim() }
    $root = $savedRoot
    # Save an absolute path: the scripts that read it run from other folders.
    if ($ProjectsRoot) { $ProjectsRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ProjectsRoot) }
    if ($ProjectsRoot -and $ProjectsRoot -ne $savedRoot) {
        $root = $ProjectsRoot
        if ($savedRoot) { Say "change the projects root from $savedRoot to $root in $rootFile" }
        else { Say "save the projects root $root in $rootFile" }
        if (-not $DryRun) { [IO.File]::WriteAllText($rootFile, "$root`n", $Utf8) }
    } elseif (-not $savedRoot) {
        $root = Join-Path $HomeDir "projects"
        Say "save the projects root $root in $rootFile (default; pass -ProjectsRoot to choose)"
        if (-not $DryRun) { [IO.File]::WriteAllText($rootFile, "$root`n", $Utf8) }
    }
    if (-not (Test-Path -LiteralPath $root)) {
        Say "create the projects folder $root"
        if (-not $DryRun) { New-Item -ItemType Directory -Force $root | Out-Null }
    }

    # 5. Hooks in settings.json.
    if (-not $Python) {
        Write-Host "Python not found: hooks not added to settings.json (the files are copied)."
    } elseif ($DryRun) {
        foreach ($l in $planned) { Write-Host "would $l"; $script:Changes++ }
    } else {
        foreach ($l in (Merge-Settings "0")) { Write-Host $l; $script:Changes++ }
    }
} finally {
    Remove-Item -LiteralPath $MergeFile -Force -ErrorAction SilentlyContinue
    if ($TempClone) { Remove-Item -LiteralPath $TempClone -Recurse -Force -ErrorAction SilentlyContinue }
}

if ($script:Changes -eq 0) { Write-Host "Up to date: nothing to change." }
elseif ($DryRun) { Write-Host "Dry run: $($script:Changes) changes, none made." }
else { Write-Host "Done: $($script:Changes) changes. Open a new Claude Code session to load them." }
