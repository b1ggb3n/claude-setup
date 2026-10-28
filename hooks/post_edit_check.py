"""PostToolUse hook (Edit|Write): syntax-check the file Claude just changed.

Reads the hook JSON on stdin and checks tool_input.file_path: Python with
compile() (no __pycache__ written), shell with `bash -n`, JSON with json.load.
Silent when the file is fine or of another type. On a syntax error it prints a
short message to stderr and exits 2, which hands the message to Claude. Any
failure of the hook itself exits 0, so it never gets in the way.
"""
import json, os, subprocess, sys

SHELL_EXT = (".sh", ".bash")


def shebang_is_shell(path):
    with open(path, "rb") as f:
        first = f.readline(200)
    if not first.startswith(b"#!"):
        return False
    words = first[2:].decode("utf-8", "replace").split()
    # "#!/bin/bash" or "#!/usr/bin/env bash"
    names = [os.path.basename(w) for w in words[:2]]
    return any(n in ("bash", "sh") for n in names)


def check(path):
    """Return an error message, or None when the file is fine or not checked."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        with open(path, "rb") as f:
            source = f.read()
        try:
            compile(source, path, "exec")
        except SyntaxError as e:
            return f"{path}:{e.lineno}: Python syntax error: {e.msg}"
        except ValueError as e:  # e.g. null bytes in the source
            return f"{path}: Python syntax error: {e}"
        return None
    if ext == ".json":
        with open(path, encoding="utf-8") as f:
            try:
                json.load(f)
            except json.JSONDecodeError as e:
                return f"{path}:{e.lineno}: JSON error: {e.msg}"
        return None
    if ext in SHELL_EXT or shebang_is_shell(path):
        r = subprocess.run(["bash", "-n", path], capture_output=True, text=True, timeout=5)
        if r.returncode != 0:
            lines = r.stderr.strip().splitlines()
            return "Shell syntax error:\n" + "\n".join(lines[:5])
        return None
    return None


def main():
    try:
        data = json.load(sys.stdin)
        path = (data.get("tool_input") or {}).get("file_path")
        if not path or not os.path.isfile(path):
            return 0
        error = check(path)
    except Exception:
        return 0
    if error:
        print(error + "\nThe edit was applied; fix the file.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
