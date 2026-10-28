"""UserPromptSubmit hook: warn when the session's context passes a threshold.

Reads the hook JSON on stdin, finds the last assistant turn's token usage in
the transcript, and if the context is over THRESHOLD, tells Claude (and the
user) to wrap up the phase and start a fresh session. Prints nothing below
the threshold. Never prints transcript content.
"""
import json, os, sys

THRESHOLD = int(os.environ.get("CONTEXT_ALARM_TOKENS", "200000"))
TAIL_BYTES = 4 * 1024 * 1024


def last_context(path):
    # Read the tail first; widen it if no complete assistant record is in it
    # (a huge tool result, e.g. images, can fill the whole window).
    window = TAIL_BYTES
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        while True:
            f.seek(max(0, size - window))
            tokens = scan(f.read().splitlines())
            if tokens or window >= size:
                return tokens
            window *= 4


def scan(lines):
    for line in reversed(lines):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("isSidechain"):
            continue
        u = (r.get("message") or {}).get("usage")
        if r.get("type") == "assistant" and u:
            return sum(u.get(k) or 0 for k in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return 0


def main():
    try:
        data = json.load(sys.stdin)
        tokens = last_context(data["transcript_path"])
    except Exception:
        return
    if tokens < THRESHOLD:
        return
    k = tokens // 1000
    context = (
        f"Context alarm: this session's context is about {k}k tokens "
        f"(threshold {THRESHOLD // 1000}k). Every turn now re-sends all of it. "
        "Finish the current step, then offer the user /wrap: bring the project docs "
        "up to date, write the handoff note, and start a fresh session. "
        "If you already offered it in your last reply, mention it in one line only."
    )
    print(json.dumps({
        "systemMessage": f"Context is about {k}k tokens. Time to /wrap and start a fresh session.",
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context},
    }))


if __name__ == "__main__":
    main()
