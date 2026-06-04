#!/usr/bin/env python3
"""check.py <transcript> — score a council transcript against the fixture's planted defects.

Given the text a council / `/plugin-critique` run produced over the `mega-helper` fixture
(build-fixture.py), assert it surfaced each PLANTED judgment defect. Matching is concept-level (any of
several phrasings) because the council is an LLM panel — this reports a **catch-rate**, it is not a
deterministic CI gate (the structural defect classes are gated by behavioral-gates.py instead).

Usage: check.py <transcript-file>     (exit 0 = every planted defect caught)
Stdlib only.
"""
import re
import sys

# planted defect -> phrasings that count as "the council caught it"
PLANTED = {
    "P3 kitchen-sink (four unrelated domains in one plugin)": [
        r"kitchen.?sink", r"unrelated", r"four .*domains?", r"two jobs", r"boundary cohesion",
        r"\bp3\b", r"split (?:it|the plugin|into|out)", r"does too (?:much|many)", r"grab.?bag",
        r"belong(?:s)? in (?:separate|different)", r"distinct plugins?",
    ],
    "P2 API-wrapper MCP (1:1 REST endpoints)": [
        r"api.?wrapper", r"1:1", r"one tool per endpoint", r"endpoint-shaped", r"wraps?\b[^.]*\bapi",
        r"\bp2\b", r"passthrough", r"\bcrud\b", r"(?:25|twenty.?five|too many) tools", r"task-level",
    ],
}


def main(path):
    text = open(path, encoding="utf-8", errors="replace").read().lower()
    caught, missed = [], []
    for defect, pats in PLANTED.items():
        hit = next((p for p in pats if re.search(p, text)), None)
        (caught if hit else missed).append((defect, hit))
    for d, p in caught:
        print(f"  CAUGHT  {d}\n            (matched /{p}/)")
    for d, _ in missed:
        print(f"  MISSED  {d}")
    print(f"\ncouncil-calibration: {len(caught)}/{len(PLANTED)} planted defects caught")
    return 0 if not missed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check.py <transcript-file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
