# claude-setup

A portable setup for Claude Code: a project standard, templates, working
rules, two small hooks and six skills. Use it as it is, or read it to see
how the pieces fit.

## Why it works this way

- **The docs are the memory, not the chat.** Every project keeps its state,
  next step and history in the same few files. Any fresh session, or any
  person, can pick it up cold. Nothing depends on remembering an old chat.
- **Short sessions.** Claude re-reads the whole conversation every turn, so
  a long session costs more and more. Work goes in phases. At the end of
  each phase, `/wrap` writes the handoff and a new session starts clean.
- **One standard everywhere.** Every project has the same files in the same
  shape. You always know where to look, and scripts can read them (the root
  todo, `status`).
- **Plain English for people first.** The docs are written for the user.
  Claude reads the same files; there is no second copy for agents.
- **Ask before anything hard to undo.** Deleting, overwriting, pushing or
  sending anything outside needs a clear yes. Exploring an idea is never a
  go signal.
- **Another model checks the work.** A second model reviews builds and
  answers research, because one model reviewing itself misses its own
  mistakes. Its output is treated as data: each finding is checked before
  anything is fixed.
- **Tests first for logic, honest reports.** Rules, math and parsing get a
  failing test before the code. A failed test or a skipped step is reported
  as it is.
- **Secrets are never opened, printed or committed.**

## What each piece does

### Rules (always loaded)

| Piece | What it does | When it matters |
|---|---|---|
| `CLAUDE.md` | Claude-specific notes; loads `AGENTS.md`. | Every session, automatically. |
| `AGENTS.md` | Rules for any AI agent: where to start, hard rules, which module to read. | Every session. Written so other agents can follow it too. |
| `agents/projects.md` | The project standard: the files, the `State:` line, the TODO format, phases and wrap-up. | Starting a project, changing its docs, ending a session. |
| `agents/working.md` | How to work with the user: when to act and when to ask, tests first, keeping usage down. | All the time. |
| `agents/secrets.md` | How to treat credentials, `.env` files and keys. | Anywhere near a secret. |
| `agents/templates/` | The starting text for every project file. | Used by `new-project`. |
| `agents/root-todo.py` | Builds one list of every project's state and next task into `~/TODO.md`. | Used by `status` and `/wrap`; run it any time. |

### Skills (Claude uses them when the request fits, or you call them by name)

| Skill | What it does | Use it when |
|---|---|---|
| `new-project` | Makes a project folder with the full file set, fills in name and date, adds its line to `INDEX.md`. | "Start a project called X." |
| `wrap` | Brings the project docs up to date (State line, TODO, logs, index), writes the "Next session" handoff, and lists friction worth fixing. | `/wrap`, "let's stop", "new session", end of a phase, or when the context alarm fires. |
| `status` | Lists every project by state: priority first, then your tasks, active, waiting and paused; suggests the next task. | "What's open?", start of the day, choosing what to work on. |
| `second-opinion` | Sends a diff, plan or idea to another model for review, checks each finding, fixes only the confirmed ones. Needs another model's CLI (`codex`, `gemini`, `agy`, or similar). | After a build step, before calling it done; for math or logic checks; "what would another model think?" |
| `research` | Asks another model a research question, brings back findings with sources, checks the ones that matter. Needs another model's CLI. | Open questions, docs lookups, comparisons, "look into X". |
| `archive-project` | Folds a finished project's state into its README, moves it into `archive/`, and updates `INDEX.md` and `archive/README.md`. | `/archive-project <name>` when a project is done or dropped. Manual only. |

### Hooks (run on their own)

| Hook | What it does | Why |
|---|---|---|
| `context_alarm.py` | Warns once a session's context passes 200k tokens. | Long sessions cost the most; this is the cue to `/wrap`. |
| `post_edit_check.py` | Syntax-checks Python, shell and JSON files right after Claude edits them, and tells Claude at once on an error. | A broken file is caught at the edit, not later. |

### Install

| Piece | What it does |
|---|---|
| `install.ps1` | Installs or updates everything above on Windows (also runs in PowerShell 7 on Linux or macOS). Details below. |

## How projects are laid out

All projects sit in one folder, the projects root (set at install; default
`~/projects`, stored in `~/agents/projects-root.txt`):

    <projects root>/
      INDEX.md          the map: one line per project, plus the archive
      archive/          retired projects, listed in archive/README.md
      <project>/
        README.md       what it is, how to run it, its files
        PROJECT.md      State line, goal, scope, phases, next session, status log
        TODO.md         ordered tasks with owner and "done when"
        docs/
          DECISIONS.md  decisions and why (ADRs)
          BUILD-LOG.md  what was built or changed, and how
          ISSUES.md     problems hit and how they were solved (troubleshooting)
          RUNBOOKS.md   recurring jobs, exact commands

The full standard is `agents/projects.md`.

## Install on Windows

Needs git. Python (`py -3`, `python3` or `python`) is needed for the hooks
and the `new-project` skill; without it the hooks are not switched on. In
PowerShell:

    git clone https://github.com/b1ggb3n/claude-setup.git $HOME\claude-setup
    powershell -ExecutionPolicy Bypass -File $HOME\claude-setup\install.ps1 -DryRun -ProjectsRoot "<folder for your projects>"
    powershell -ExecutionPolicy Bypass -File $HOME\claude-setup\install.ps1 -ProjectsRoot "<folder for your projects>"

`-ProjectsRoot` is needed only on the first run (default `$HOME\projects`);
later runs keep the saved one unless you pass it again.

The dry run prints every change and makes none. The install copies
`AGENTS.md` and `agents\` into your home folder, and `CLAUDE.md`, `skills\`
and `hooks\` into the Claude config folder (`$env:CLAUDE_CONFIG_DIR`, or
`$HOME\.claude`). A file that differs is backed up as `<file>.bak-<time>`
first. The two hooks are added to `settings.json`; your other settings and
hooks stay as they are, and the old file is backed up.

To update, run `install.ps1` again: it pulls the repo and changes only what
is new. A second run with nothing new changes nothing. Files removed from
the repo are not removed from your folders.

On Linux or macOS, `pwsh install.ps1` does the same, or copy the files by
hand to the same places.

This repo is generated from a private setup. Do not edit it by hand.
