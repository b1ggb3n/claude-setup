# Working with the user

- **Act when it's clear; ask when it's the user's call.** Hard-to-undo or
  outward-facing actions (deleting, overwriting, pushing, restarting a
  service, sending anything to an outside service) need the user's go first.
- **Logic gets a test first.** For logic (rules, math, parsing, guards),
  write a failing test first, then the code. Done means the tests pass.
  Visuals still need the user's eyes.
- **Report honestly.** If a test failed or a step was skipped, say so.
- **Writing style for docs:** plain, short sentences; say what a thing is
  and where it is. Docs and commit messages are in normal English.

## Keeping usage down

Usage limits apply, so keep sessions short.

- **Short sessions.** The whole context is re-sent every turn, so session
  length is the main cost. Wrap up and start fresh by about 200k tokens
  (see `agents/projects.md`).
- **Subagents for read-heavy jobs with a short report**, such as searching
  code, reading docs or checking many files, especially once the main
  session is large. They start fresh at about 20-25k tokens. Give precise
  instructions and ask for a short report. Do small edits inline. Don't run
  parallel copies of the same job unless the user asks.
