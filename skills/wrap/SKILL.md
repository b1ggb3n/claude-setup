---
name: wrap
description: End a phase or session cleanly. Bring the project docs up to date, write the handoff note, then offer a fresh session. Use for /wrap, and whenever the user says "break this up", "new session", "let's stop", "wrap up", "pick this up later", or when the context alarm fires.
---

# Wrap up a phase

The goal: the next session can start cold from the docs alone, so nobody has
to remember anything and the old context can be dropped.

Do these in order. Keep each edit short. Don't re-read files you already have
in context.

1. **PROJECT.md** (the project folder you're working in):
   - Add a dated Status entry: what got done this session, in 1-3 lines.
   - Update the `State:` line to match (form in `~/agents/projects.md`).
   - Update the `## Phases` section: tick finished phases, mark the current
     one. If the section is missing, add it (format in `~/agents/projects.md`).
   - Rewrite the `## Next session` section (replace it, don't append): the
     next step, any open decision for the user, files to read first, anything
     half-done and where it stopped. Five lines at most.
   - Move answered open questions out; add new ones.
2. **TODO.md**: tick finished tasks with the date, add new ones (owner and
   "done when"), and make sure the first open task is the real next step.
3. **`docs/` logs**: one dated entry each for what this session decided
   (`DECISIONS.md`), built or changed (`BUILD-LOG.md`), and hit and solved
   (`ISSUES.md`); update `RUNBOOKS.md` if a procedure changed. Skip the
   ones with nothing new.
4. **Root todo**: run `~/agents/root-todo.py` so `~/TODO.md` shows this
   project's new state and next task.
5. **README.md**: only if files, commands or how-to-run changed.
7. **Lessons**: for each non-obvious gotcha hit this session (a wrong flag,
   a trap in a service, a fix that took several tries), write one line where
   the next session will read it: the project's `CLAUDE.md` or README
   "Gotchas", or a memory for user preferences. Skip what the code or git
   history already shows. None found: skip.
8. **Retro.** List up to 3 points of friction from this session: repeated
   mistakes, missing info, slow steps, rules that got in the way. For each,
   propose one durable fix (a line in AGENTS.md or a module, a hook, a script
   or a skill change) and say what it prevents. This is not a report card:
   the aim is to change the setup so the same mistake becomes impossible or
   cheap to catch. Apply only what the user approves. If nothing was hard,
   say "no friction" and skip.
9. Tell the user in two or three lines what you updated, then say:
   "Docs are current. Start a fresh session for the next phase."

Don't start the next phase's work after wrapping. Don't commit unless the user
asks.
