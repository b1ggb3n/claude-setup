#!/usr/bin/env python3
"""Build the root todo (~/TODO.md) from every project's State line and TODO.md.

Format of both: ~/agents/projects.md. Run by /wrap; safe to run any time.
Usage: root-todo.py [output path]   (default ~/TODO.md; "-" prints to stdout)
Project folders: globs in ~/agents/root-todo.conf (default projects/*/PROJECT.md).
"""
import glob
import os
import re
import sys
from datetime import date

HOME = os.path.expanduser("~")
CONF = os.path.join(HOME, "agents", "root-todo.conf")
DEFAULT_GLOBS = ["projects/*/PROJECT.md"]


def load_globs():
    """Project folders: one glob per line (relative to ~) in root-todo.conf."""
    try:
        with open(CONF) as f:
            globs = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return DEFAULT_GLOBS
    return globs or DEFAULT_GLOBS
STATE_RE = re.compile(r"^State: (Active|Paused|Waiting|Done)(?: \(([^)]*)\))?, (\d{4}-\d\d-\d\d)\. ?(.*)$")
TASK_RE = re.compile(r"^- \[ \] (\d+)\. \*\*(.+?)\*\* \(owner: ([^)]+)\)")


def first_open_task(todo_path):
    try:
        with open(todo_path) as f:
            for line in f:
                m = TASK_RE.match(line)
                if m:
                    return m.groups()
    except FileNotFoundError:
        pass
    return None


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, "TODO.md")
    groups = {"priority": [], "you": [], "active": [], "waiting": [], "paused": [], "old": []}
    paths = sorted({p for g in load_globs() for p in glob.glob(os.path.join(HOME, g))})
    for path in paths:
        folder = os.path.dirname(path)
        name = os.path.relpath(folder, HOME)
        with open(path) as f:
            state = next((l.rstrip("\n") for l in f if l.startswith("State:")), "")
        m = STATE_RE.match(state)
        if not m:
            groups["old"].append(f"- `{name}`")
            continue
        label, reason, touched, _ = m.groups()
        if label == "Done":
            continue
        task = first_open_task(os.path.join(folder, "TODO.md"))
        if task:
            num, title, owner = task
            nxt = f"task {num}: {title} ({owner})"
        else:
            owner, nxt = "", "no open task in TODO.md"
        why = f" ({reason})" if reason else ""
        line = f"- `{name}`, {touched}{why}: {nxt}"
        if label != "Paused" and "**Priority" in state:
            rank = re.search(r"\*\*Priority (\d+)", state)
            groups["priority"].append((int(rank.group(1)) if rank else 1, line))
        elif label == "Waiting" and reason and "user" in reason.lower():
            groups["you"].append(line)
        elif label == "Active" and owner.strip().lower() == "user":
            groups["you"].append(line)
        else:
            groups[label.lower()].append(line)

    groups["priority"] = [line for _, line in sorted(groups["priority"])]
    sections = [("Priority", "priority"), ("Waiting on you", "you"), ("Active", "active"),
                ("Waiting on something else", "waiting"), ("Paused", "paused"),
                ("Not on the standard yet", "old")]
    text = [f"# Root todo\n\nGenerated {date.today()} by `~/agents/root-todo.py` "
            "from each project's `State:` line and first open task. "
            "Don't edit by hand; edit the project's `PROJECT.md` or `TODO.md` and re-run.\n"]
    for title, key in sections:
        if groups[key]:
            text.append(f"## {title}\n\n" + "\n".join(groups[key]) + "\n")
    result = "\n".join(text)
    if out_path == "-":
        sys.stdout.write(result)
    else:
        with open(out_path, "w") as f:
            f.write(result)


if __name__ == "__main__":
    main()
