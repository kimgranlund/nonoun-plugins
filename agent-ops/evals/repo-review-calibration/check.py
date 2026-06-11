#!/usr/bin/env python3
"""check.py <transcript> — score a repo-review transcript against the seeded repo's planted smells.

The companion of build-seeded-repo.py. Given the review package a `repo-review` run produced over the
synthetic `seeded-smell-repo`, assert it surfaced each PLANTED smell somewhere in its backlog. Matching
is concept-level (any of several phrasings) because the review is an LLM pipeline — this reports a
catch-rate, the behavioral coverage the real-repo audit (2026-06-11) found missing for this surface.

Usage: check.py <transcript-file>     (exit 0 = every planted smell caught)
Stdlib only.
"""
import re
import sys

PLANTED = {
    "S1 god module — parsing + db + http + rendering in one file (no separation)": [
        r"god (?:module|object|class|file)", r"does everything", r"separation of concerns",
        r"single responsibilit", r"too many (?:responsibilit|concerns|jobs)", r"all in one (?:file|module|place)",
        r"mix(?:es|ing|ed) (?:db|database|http|parsing|rendering)", r"\bapp\.py\b.{0,40}(?:everything|monolith|god|split)",
        r"split .{0,20}app\.py", r"one (?:huge|giant|massive) (?:file|module)", r"layering",
    ],
    "S2 naming drift — camelCase and snake_case mixed in one module": [
        r"naming (?:drift|inconsisten|convention)", r"camel.?case", r"snake.?case", r"mixed (?:naming|case|convention)",
        r"getuserdata", r"inconsistent (?:naming|case)", r"camel.{0,15}snake", r"two (?:naming )?conventions",
        r"casing (?:convention|drift)", r"convention drifts?",
    ],
    "S3 declared-vs-actual contradiction — README 'stdlib only' but imports requests": [
        r"declared.?(?:vs|versus|against).?actual", r"stdlib only", r"\brequests\b", r"contradict",
        r"readme (?:claims?|says?).{0,40}(?:stdlib|no dep|zero dep)", r"external dependenc",
        r"no dependenc.{0,30}(?:but|yet|however|while)", r"the repo (?:contradicts|breaks) its own",
        r"declared contract", r"claim.{0,30}(?:false|untrue|contradict)",
    ],
    "S4 duplicated logic — _is_valid_email copy-pasted across two files": [
        r"duplicat", r"copy.?paste", r"_is_valid_email", r"same (?:function|logic|code) .{0,20}(?:two|both|twice)",
        r"\bdry\b", r"no single source of truth", r"drift .{0,20}(?:copy|duplicate)", r"repeated (?:function|logic)",
        r"two copies", r"validate\.py.{0,30}app\.py", r"app\.py.{0,30}validate\.py",
    ],
    "S5 command injection — unsanitized input shells out (trust boundary)": [
        r"command injection", r"shell injection", r"os\.system", r"injection", r"unsanitiz",
        r"untrusted (?:input|arg|branch).{0,30}(?:shell|command|os\.system)", r"trust boundary",
        r"shell(?:s|ing)? out", r"interpolat\w+ .{0,20}shell", r"\bdeploy\.py\b.{0,40}(?:inject|shell|unsafe|sanitiz)",
        r"rm -rf", r"arbitrary (?:command|code) execution", r"security (?:smell|hole|risk|vuln)",
    ],
    "S6 no agent memory / no tests — no AGENTS.md, no CHANGELOG, no tests, 'well-tested' is false": [
        r"no (?:agents?\.md|claude\.md|agent (?:memory|docs))", r"no (?:tests?|test suite|coverage)",
        r"no changelog", r"untested", r"zero (?:tests?|memory|coverage)", r"missing (?:agents?\.md|tests?|changelog)",
        r"well-tested.{0,20}(?:false|untrue|claim|but)", r"claims? .{0,20}tested", r"no (?:repo )?memory",
        r"agent.?facing (?:docs|memory)", r"repo-ops", r"no .{0,15}(?:onboarding|runbook)",
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
    print(f"\nrepo-review calibration: {len(caught)}/{len(PLANTED)} planted smells caught")
    return 0 if not missed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check.py <transcript-file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
