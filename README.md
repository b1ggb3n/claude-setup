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

## Use

Install script for Windows (`install.ps1`) is coming. Until then, copy
`AGENTS.md` and `agents/` to your home folder, and `CLAUDE.md` and `skills/`
into your Claude config folder.

This repo is generated from a private setup. Do not edit it by hand.
