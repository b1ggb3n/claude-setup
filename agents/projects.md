# Project standard

Every project follows this from day one. The docs are written for the user first, in plain English, and
Claude reads the same files. There is no second copy for agents; a project
`CLAUDE.md`, if any, is a thin pointer plus gotchas.

Templates for every file: `~/agents/templates/` (`{{name}}` and `{{date}}`
are filled in by the `new-project` skill). Archived projects keep only their README.

## The files

| File | What goes in it |
|---|---|
| `README.md` | What it is, how to run or use it, its files. Stable, no dated log. |
| `PROJECT.md` | `State:` line, Goal, Scope, Phases, Open questions, Next session, dated Status log. |
| `TODO.md` | Ordered tasks for the current and next phase (format below). |
| `docs/DECISIONS.md` | What was decided, why, what else was considered. |
| `docs/BUILD-LOG.md` | What was built or changed, and how. |
| `docs/RUNBOOKS.md` | How to do recurring jobs, exact commands. Kept current. |
| `docs/ISSUES.md` | Problems hit and how they were solved. Open ones marked **Open**. |

The `docs/` logs use dated entries (`## 2026-10-27: title`), newest last,
append-only: to change an old decision, add a new entry that replaces it.
Runbooks are the exception: one section per job, edited in place, with the
date of the last update in its heading.

## The State line

One line under the title, in this form:

    State: <Label>, <last-touched date>. <current phase and next step>

Labels: **Active**, **Paused**, **Waiting**, **Done**. A project the user puts first adds `**Priority: <why>**` after the date; the root todo lists it at the top. For an order, number them: `**Priority 2: <why>**` (no number counts as 1). Paused and Waiting
give a reason in brackets; Waiting names who or what:
`State: Waiting (on the user: router password), 2026-10-27. Phase 2 ...`.
Update it whenever you add a Status entry. Dates are absolute
(`2026-10-27`), never "yesterday".

## TODO.md format

A script builds the root todo from it, so keep this shape:

    - [ ] 7. **Short task title** (owner: user)
      What to do, in enough detail that a fresh chat can do it.
      Done when: a check anyone can run.

- Owner is `user`, `Claude`, or `user and Claude`.
- When done: tick the box and add the date after the owner:
  `- [x] 7. **Title** (owner: user) Done 2026-10-27.` Keep done tasks of the
  current phase; fold older phases' done tasks into one Status log line.
- Numbers never repeat within a project, so "task 7" stays unambiguous.
- The first unticked task is "the next step" in the root todo.

## Where chats run

- Work on a project in its own folder. State lives in `TODO.md` and
  `PROJECT.md`, so a fresh chat there picks up without old history.

## When you change a project

- Tick or add tasks in `TODO.md`; add a dated Status entry and update the
  `State:` line.
- Log decisions, builds, issues and runbook changes in `docs/`.
- Propose changes to Goal or Scope; don't make them unasked.
- Drafts for the user to review go in the project folder, never in a
  session scratchpad: the scratchpad is gone when the session ends.

## Phases and wrap-up

Work goes in phases, so the user never has to remember where things stand
and a long job can stop at any point without losing anything.

- `## Phases` in `PROJECT.md`: one line per phase with a short "done when";
  mark the current one.
- `## Next session`: at most five lines: next step, open decisions, files
  to read first, anything half-done. Replace it at each wrap-up.
- At the start of a session, read `PROJECT.md` and `TODO.md` and tell the
  user where things stand and what's next, in a line or two.
- **Wrap up** (Claude: the `/wrap` skill) when a phase ends, when the user
  says "break this up", "new session", "let's stop" or "wrap up", or when
  the context alarm fires (session past 200k tokens). If the user asks to
  stop, say "I'll finish the docs first", then do it.
- Why: a session's whole context is re-sent every turn. One 36-hour session
  reached 737k tokens and used up the 5-hour limit.

