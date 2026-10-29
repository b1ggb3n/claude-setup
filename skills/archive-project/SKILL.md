---
name: archive-project
description: Retire a finished or dropped project - move it into the archive folder and update every doc that points at it. Manual only; run with /archive-project <name>.
disable-model-invocation: true
---

# Archive a project

`$ARGUMENTS` is the project name. Projects live in the projects root (the
folder named in `~/agents/projects-root.txt`, default `~/projects`); the
archive is `archive/` inside it, made on first use. Every step that stops,
deletes or moves something needs the user's go first.

## 1. Survey (read-only)

Read the project's `README.md`, `PROJECT.md`, `TODO.md` and `CLAUDE.md` (if
any). Collect:

- **What it runs**: scheduled tasks, services, open ports, anything started
  outside the folder. Ask the user if the docs don't say.
- **Secrets** it uses: file paths only, from its docs; never open them.
- **Open tasks** in `TODO.md` that someone may still want.

Show the user one short list: what will stop, what gets folded into the
README, where the folder goes. Wait for a yes. Then run the script with
`--dry-run` (step 3) and show its plan.

## 2. Fold the docs

Archived projects keep only their README plus `docs/` (the standard,
`~/agents/projects.md`). Add a `## Archived` section to `README.md`:

- What it was and why it stopped (one or two lines).
- Last state, from the `State:` line and the last Status entries.
- Open tasks that were left, from `TODO.md`, one line each.
- What is left elsewhere (accounts, installed tools, files outside the
  folder) and how to revive it.

Then delete `PROJECT.md` and `TODO.md`. Secrets: don't open, move or delete
them; list them by path for the user to revoke or move, and wait until they
say it's handled.

## 3. Move it and record it

Linux or macOS:

    python3 ~/.claude/skills/archive-project/scripts/archive_project.py <name> --reason "<why it stopped>"

Windows (PowerShell):

    $cfg = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { "$HOME\.claude" }
    py -3 "$cfg\skills\archive-project\scripts\archive_project.py" <name> --reason "<why it stopped>"

Add `--dry-run` first. The script creates `archive/` and its `README.md`
when missing, refuses if `archive/<name>` exists, moves the folder, adds a
row (name, date, reason) to `archive/README.md`, and moves the project's
line in the root `INDEX.md` from `## Projects` to `## Archive`, keeping
its goal.

If the projects root is a git repo, the move shows as deletions and new
files; don't commit unless the user asks.

## 4. Update the rest

- Rebuild the root todo so `~/TODO.md` drops the project:
  `python3 ~/agents/root-todo.py` (Windows: `py -3 "$HOME\agents\root-todo.py"`).
- Any other doc that names the project's old path (another project's
  README, a runbook): point it at `archive/<name>/`.

## 5. Report

Two or three lines: what stopped, where it lives now, which docs changed,
and anything left for the user (secrets, accounts, open tasks).
