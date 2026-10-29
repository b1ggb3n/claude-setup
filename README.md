# claude-setup

A portable setup for Claude Code: a project standard, templates, working
rules, two small hooks and six skills. Use it as it is, or read it to see
how the pieces fit.

## What is in it

| Path | What it is |
|---|---|
| `AGENTS.md` | Rules for any AI agent: where to start, hard rules, modules. |
| `CLAUDE.md` | Claude-specific notes; imports `AGENTS.md`. |
| `agents/projects.md` | The project standard: files, State line, TODO format, wrap-up. |
| `agents/working.md`, `agents/secrets.md` | How to work with the user; how to treat secrets. |
| `agents/templates/` | Templates for every project file (below). |
| `agents/root-todo.py` | Builds one todo list from every project's State line and first open task. |
| `skills/new-project/` | Start a project folder from the templates and add it to `INDEX.md`. |
| `skills/wrap/` | `/wrap`: end a phase or session, bring the docs and index up to date, write the handoff. |
| `skills/status/` | "What's open?": every project's state and next task. |
| `skills/archive-project/` | `/archive-project <name>`: retire a project into `archive/` and update the index. |
| `skills/second-opinion/` | Have another model review a change or plan, then check its findings. Needs another model's CLI. |
| `skills/research/` | Ask another model a research question; findings with sources. Needs another model's CLI. |
| `hooks/context_alarm.py` | Warns when a session's context grows past 200k tokens. |
| `hooks/post_edit_check.py` | Syntax-checks a file right after Claude edits it. |
| `install.ps1` | Installs or updates all of the above. |

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
