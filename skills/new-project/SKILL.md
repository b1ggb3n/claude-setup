---
name: new-project
description: Start a project folder from the templates. Use when the user says "start a project called X", "new project X" or "set up a project", or runs /new-project. Works on Windows, Linux and macOS.
---

# Start a project

Makes a project folder with the standard file set (`README.md`, `PROJECT.md`,
`TODO.md`, `docs/`), from the templates in `~/agents/templates/`. The
standard is in `~/agents/projects.md`.

1. Get the name from the user: lowercase letters, digits and dashes only
   (`my-project`). If it is not clear, ask.
2. Decide the parent folder: the folder you were opened in, unless the user
   names another. The project goes in `<parent>/<name>`.
3. Run the script. On Linux or macOS:

       python3 ~/.claude/skills/new-project/scripts/new_project.py <name> --parent <parent>

   On Windows (PowerShell):

       $cfg = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { "$env:USERPROFILE\.claude" }
       py -3 "$cfg\skills\new-project\scripts\new_project.py" <name> --parent <parent>

   On Linux or macOS, if `CLAUDE_CONFIG_DIR` is set, the skill is under that
   folder instead of `~/.claude`. Add `--dry-run` first if the user wants to
   see the files before they are made.
4. The script refuses when `<parent>/<name>` already exists. Tell the user
   and stop; never overwrite.
5. Tell the user the folder path and the file list. Say that the next step
   is `TODO.md` task 1: set the goal and scope together. Offer to start it.

This skill makes no server and no git repo. Do not commit or push.
