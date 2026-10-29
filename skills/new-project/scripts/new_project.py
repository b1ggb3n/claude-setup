#!/usr/bin/env python3
"""Make a project folder from the templates, filling {{name}} and {{date}}.

Usage: new_project.py <name> [--parent DIR] [--templates DIR] [--dry-run]
Refuses when the folder exists. Checks that no {{ is left in the result.
The default parent is the projects root (~/agents/projects-root.txt, default
~/projects). Adds the project's line to INDEX.md in the projects root,
creating it when missing.
"""
import argparse
import os
import re
import shutil
import sys
from datetime import date

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HOME = os.path.expanduser("~")
INDEX_HEAD = """# Index

The map of the projects here. Read it before searching. Keep it current:
`new-project` adds a line, `archive-project` moves it, `/wrap` fixes it when
something is added, moved or retired. One line each: name and goal.

## Projects

"""
INDEX_TAIL = """## Archive

Retired projects are in `archive/`, listed in `archive/README.md`.
"""


def projects_root():
    """The folder that holds the projects, INDEX.md and archive/."""
    try:
        with open(os.path.join(HOME, "agents", "projects-root.txt"), encoding="utf-8-sig") as f:
            root = f.read().strip()
    except FileNotFoundError:
        root = ""
    return os.path.expanduser(root) if root else os.path.join(HOME, "projects")


def index_line(root, target):
    """Add '- `<path>`: goal not set yet' under ## Projects in <root>/INDEX.md.
    Returns the INDEX.md path."""
    path = os.path.join(root, "INDEX.md")
    try:
        rel = os.path.relpath(target, root)
    except ValueError:  # Windows: another drive
        rel = ".."
    shown = rel if not rel.startswith("..") else os.path.abspath(target)
    line = f"- `{shown.replace(os.sep, '/')}`: goal not set yet\n"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = (INDEX_HEAD + INDEX_TAIL).splitlines(keepends=True)
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Projects")
    except StopIteration:
        lines += ["\n## Projects\n", "\n"]
        start = len(lines) - 2
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    if end == start + 1:
        lines.insert(end, "\n")
        end += 1
    if lines[end - 1] and not lines[end - 1].endswith("\n"):
        lines[end - 1] += "\n"
    lines.insert(end, line)
    os.makedirs(root, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)
    return path


def build(name, parent, templates, today, dry_run=False):
    """Return the list of files made (relative to the project folder)."""
    if not NAME_RE.fullmatch(name):
        raise SystemExit(f"bad name {name!r}: use lowercase letters, digits and dashes")
    if not os.path.isdir(templates):
        raise SystemExit(f"templates folder not found: {templates}")
    target = os.path.join(parent, name)
    if os.path.exists(target):
        raise SystemExit(f"{target} already exists; nothing changed")
    made = []
    for root, dirs, files in os.walk(templates):
        for fn in sorted(files):
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, templates)
            with open(src, encoding="utf-8") as f:
                text = f.read().replace("{{name}}", name).replace("{{date}}", today)
            if "{{" in text:
                raise SystemExit(f"unfilled placeholder in template {rel}; nothing changed")
            made.append((rel, text))
    if dry_run:
        return [rel for rel, _ in made]
    try:
        for rel, text in made:
            dest = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise
    return [rel for rel, _ in made]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--parent", default=None, help="default: the projects root")
    ap.add_argument("--templates", default=os.path.join(os.path.expanduser("~"), "agents", "templates"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-index", action="store_true", help="don't touch INDEX.md (tests)")
    a = ap.parse_args()
    root = projects_root()
    parent = a.parent or root
    files = build(a.name, parent, a.templates, date.today().isoformat(), a.dry_run)
    target = os.path.join(parent, a.name)
    print(("Would make " if a.dry_run else "Made ") + target)
    for rel in sorted(files):
        print("  " + rel.replace(os.sep, "/"))
    if not a.no_index:
        if a.dry_run:
            print("Would add its line to " + os.path.join(root, "INDEX.md"))
        else:
            print("Added its line to " + index_line(root, target))


if __name__ == "__main__":
    sys.exit(main())
