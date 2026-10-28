#!/usr/bin/env python3
"""Make a project folder from the templates, filling {{name}} and {{date}}.

Usage: new_project.py <name> [--parent DIR] [--templates DIR] [--dry-run]
Refuses when the folder exists. Checks that no {{ is left in the result.
"""
import argparse
import os
import re
import shutil
import sys
from datetime import date

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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
    ap.add_argument("--parent", default=os.getcwd())
    ap.add_argument("--templates", default=os.path.join(os.path.expanduser("~"), "agents", "templates"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    files = build(a.name, a.parent, a.templates, date.today().isoformat(), a.dry_run)
    print(("Would make " if a.dry_run else "Made ") + os.path.join(a.parent, a.name))
    for rel in sorted(files):
        print("  " + rel.replace(os.sep, "/"))


if __name__ == "__main__":
    sys.exit(main())
