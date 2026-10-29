---
name: status
description: Show where every project stands and what is next. Use for /status, "what's open", "what projects are open", "where are we", "what should I work on", or at the start of a day.
---

# Status of every project

Answers from the docs alone; no project is changed.

1. Build the root todo and print it. On Linux or macOS:

       python3 ~/agents/root-todo.py -

   On Windows (PowerShell): `py -3 "$HOME\agents\root-todo.py" -`

   It lists every project under the projects root (the folder named in
   `~/agents/projects-root.txt`, default `~/projects`) by its `State:` line
   and first open task. Run it again without `-` to also refresh `~/TODO.md`.
2. Read `INDEX.md` in the projects root. A project listed there but missing
   from the root todo has no `PROJECT.md` or no valid `State:` line: name it.
3. Answer in this order, one line per project, at most about 15 lines:
   - **Priority** projects first, in their order.
   - **Your turn**: tasks owned by the user.
   - **Active**, then **Waiting** (on whom), then **Paused** (why).
   - Projects not touched in over 30 days: one line, "stale".
4. End with one suggestion: the next task you would pick, and why.

Read a full `PROJECT.md` only if the user asks about that project. If
`root-todo.py` is missing or fails, say so and fall back to reading each
project's `State:` line from `INDEX.md`'s list.
