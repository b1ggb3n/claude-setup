# claude-setup

A portable setup for Claude Code: a project standard, templates, working
rules, two small hooks and two skills. Use it as it is, or read it to see
how the pieces fit.

## What is in it

| Path | What it is |
|---|---|
| `AGENTS.md` | Rules for any AI agent: where to start, hard rules, modules. |
| `CLAUDE.md` | Claude-specific notes; imports `AGENTS.md`. |
| `agents/projects.md` | The project standard: files, State line, TODO format, wrap-up. |
| `agents/working.md`, `agents/secrets.md` | How to work with the user; how to treat secrets. |
| `agents/templates/` | Templates for every project file. |
| `agents/root-todo.py` | Builds one todo list from every project's State line and first open task. |
| `skills/wrap/` | `/wrap`: end a phase or session and write the handoff. |
| `skills/new-project/` | Start a project folder from the templates. |
| `hooks/context_alarm.py` | Warns when a session's context grows past 200k tokens. |
| `hooks/post_edit_check.py` | Syntax-checks a file right after Claude edits it. |
| `install.ps1` | Installs or updates all of the above. |

## Install on Windows

Needs git. Python (`py -3`, `python3` or `python`) is needed for the hooks
and the `new-project` skill; without it the hooks are not switched on. In
PowerShell:

    git clone https://github.com/b1ggb3n/claude-setup.git $HOME\claude-setup
    powershell -ExecutionPolicy Bypass -File $HOME\claude-setup\install.ps1 -DryRun
    powershell -ExecutionPolicy Bypass -File $HOME\claude-setup\install.ps1

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
