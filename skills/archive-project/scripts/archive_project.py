#!/usr/bin/env python3
"""Move a project into <root>/archive/ and record it in the index.

Usage: archive_project.py <name> --reason "<why it stopped>" [--dry-run]
<root> is the projects root (~/agents/projects-root.txt, default ~/projects).
Creates <root>/archive/ and its README.md when missing, refuses when
archive/<name> exists, moves the folder, adds a row to archive/README.md and
moves the project's line in <root>/INDEX.md from "## Projects" to "## Archive".
Folding PROJECT.md into the README is done before this, by the skill.
"""
import argparse
import os
import re
import shutil
import sys
from datetime import date

HOME = os.path.expanduser("~")
ARCHIVE_README = """# Archive

Retired projects, one folder each. Each keeps its README: what it was, why
it stopped, its last state and how to revive it. Added by the
`archive-project` skill; newest last.

| Project | Archived | Why it stopped |
|---|---|---|
"""


def projects_root():
    """The folder that holds the projects, INDEX.md and archive/."""
    try:
        with open(os.path.join(HOME, "agents", "projects-root.txt"), encoding="utf-8-sig") as f:
            root = f.read().strip()
    except FileNotFoundError:
        root = ""
    return os.path.expanduser(root) if root else os.path.join(HOME, "projects")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def update_index(text, name, today):
    """Move the project's line from ## Projects to ## Archive, keeping its goal."""
    line_re = re.compile(rf"^- `{re.escape(name)}`:[ \t]*(.*)\n?", re.M)
    m = line_re.search(text)
    goal = m.group(1).strip().rstrip(".") if m else ""
    if m:
        text = text[:m.start()] + text[m.end():]
    entry = f"- `archive/{name}`: {goal + '. ' if goal else ''}Archived {today}.\n"
    if not re.search(r"^## Archive\s*$", text, re.M):
        text = text.rstrip("\n") + "\n\n## Archive\n\n"
    # Insert at the end of the ## Archive section.
    lines = text.splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if l.strip() == "## Archive")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    if end == start + 1:
        lines.insert(end, "\n")
        end += 1
    if not lines[end - 1].endswith("\n"):
        lines[end - 1] += "\n"
    if not lines[end - 1].startswith(("- ", "\n")):
        lines.insert(end, "\n")  # blank line between prose and the list
        end += 1
    lines.insert(end, entry)
    return "".join(lines)


def add_row(text, row):
    """Insert a row after the last row of the first table."""
    lines = text.splitlines(keepends=True)
    rows = [i for i, l in enumerate(lines) if l.startswith("|")]
    if not rows:
        return text.rstrip("\n") + "\n\n| Project | Archived | Why it stopped |\n|---|---|---|\n" + row
    last = rows[0]
    while last + 1 < len(lines) and lines[last + 1].startswith("|"):
        last += 1
    if not lines[last].endswith("\n"):
        lines[last] += "\n"
    lines.insert(last + 1, row)
    return "".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    root = projects_root()
    src = os.path.join(root, a.name)
    archive = os.path.join(root, "archive")
    dest = os.path.join(archive, a.name)
    index = os.path.join(root, "INDEX.md")
    readme = os.path.join(archive, "README.md")
    today = date.today().isoformat()
    if a.name in ("archive", "") or os.sep in a.name or "/" in a.name:
        raise SystemExit(f"bad project name: {a.name!r}")
    if not os.path.isdir(src):
        raise SystemExit(f"no project folder {src}; nothing changed")
    if os.path.exists(dest):
        raise SystemExit(f"{dest} already exists; nothing changed")
    reason = a.reason.replace("|", "/").replace("\n", " ").strip()
    plan = []
    if not os.path.isdir(archive):
        plan.append(f"create {archive} with README.md")
    plan.append(f"move {src} to {dest}")
    plan.append(f"add a row to {readme}")
    plan.append(f"move its line in {index} to ## Archive" if os.path.exists(index)
                else f"create {index} with its line under ## Archive")
    if a.dry_run:
        print("\n".join("would " + p for p in plan))
        return 0
    # Prepare both edits first, so a bad file stops before anything moves.
    old_readme = read(readme) if os.path.exists(readme) else ARCHIVE_README
    new_readme = add_row(old_readme, f"| [`{a.name}`]({a.name}/README.md) | {today} | {reason} |\n")
    old_index = read(index) if os.path.exists(index) else "# Index\n\n## Projects\n\n## Archive\n"
    new_index = update_index(old_index, a.name, today)
    os.makedirs(archive, exist_ok=True)
    shutil.move(src, dest)
    try:
        write(readme, new_readme)
        write(index, new_index)
    except OSError:
        shutil.move(dest, src)  # put the project back
        if os.path.exists(readme):
            write(readme, old_readme)
        raise
    print("\n".join(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
