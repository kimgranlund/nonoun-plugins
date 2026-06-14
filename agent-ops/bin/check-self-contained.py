#!/usr/bin/env python3
"""check-self-contained.py — the de-repo / self-containment gate for agent-ops.

agent-ops was carved from four global skills (ops-repo, arch-repo-review, core-agent-loops,
core-agentic-ux-best-practices) and de-repo'd into a self-contained catalog plugin. "Zero cross-plugin
paths" is the plugin's loudest invariant — this gate ENFORCES it instead of asserting it. (The v0.1
red-team caught two leftovers a green CI had passed over: a foreign-namespace `$id` and a dead `.docs`
harvest path. This is the trip-wire that makes the next one impossible to ship.)

It scans only the FUNCTIONAL surface (skills/ · agents/ · bin/ · commands/ · hooks/ · schemas/) — NOT
the narrative docs (README / CHANGELOG / ROADMAP / reviews), which legitimately name the source skills
as provenance ("carved from ops-repo"). In the functional surface it flags de-repo leftovers:
  - a SOURCE-SKILL name (ops-repo · core-agent-loops · core-agentic-ux · arch-repo-review) — all four
    were renamed to the plugin's own siblings (repo-ops · agent-loops · agentic-ux · repo-review);
  - a FOREIGN NAMESPACE (adia.ai / schemas.adia);
  - a harvest-source `.docs/` path or a `scripts/<x>.py` path (the plugin's executables ship in bin/).

Usage:
  check-self-contained.py <plugin-dir>   # exit 0 if clean, 1 if any leftover, 2 on bad invocation
  check-self-contained.py selftest
Stdlib only (Python 3.8+).
"""
import os
import re
import sys

FUNCTIONAL = ("skills", "agents", "bin", "commands", "hooks", "schemas")
SCAN_EXTS = (".md", ".json", ".py")
LEFTOVERS = [
    (re.compile(r"\bops-repo\b"), "source-skill name 'ops-repo' (renamed to repo-ops)"),
    (re.compile(r"core-agent-loops"), "source-skill name 'core-agent-loops' (renamed to agent-loops)"),
    (re.compile(r"core-agentic-ux"), "source-skill name 'core-agentic-ux' (renamed to agentic-ux)"),
    (re.compile(r"arch-repo-review"), "source-skill name 'arch-repo-review' (renamed to repo-review)"),
    (re.compile(r"adia\.ai|schemas\.adia"), "foreign namespace (adia.ai)"),
    (re.compile(r"\.docs/"), "harvest-source path '.docs/'"),
    (re.compile(r"\bscripts/[\w./-]+\.py"), "scripts/<x>.py path (executables ship in bin/)"),
]


def check(root):
    root = os.path.abspath(root)
    findings = []
    for sub in FUNCTIONAL:
        for dp, _dirs, files in os.walk(os.path.join(root, sub)):
            for fn in sorted(files):
                if not fn.endswith(SCAN_EXTS) or fn == "check-self-contained.py":
                    continue  # the gate's own source names the patterns it searches for
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, root)
                for i, line in enumerate(open(fp, encoding="utf-8", errors="replace"), 1):
                    for rule, why in LEFTOVERS:
                        if rule.search(line):
                            findings.append((rel, i, why))
    return findings


def _selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        sk = os.path.join(d, "skills", "x")
        os.makedirs(sk)
        open(os.path.join(sk, "bad.md"), "w").write(
            "see core-agent-loops and ops-repo, id https://schemas.adia.ai/x, path ../../.docs/y.md and scripts/z.py\n")
        open(os.path.join(sk, "good.md"), "w").write(
            "see agent-loops and repo-ops; the audited repo's docs/adrs/ and .agents/brain/ are fine; bin/check_blueprint.py\n")
        # narrative docs must be EXEMPT even with a source name (provenance)
        os.makedirs(os.path.join(d, "ignored-narrative"), exist_ok=True)
        open(os.path.join(d, "README.md"), "w").write("Carved from ops-repo and core-agent-loops.\n")
        rels = {r for r, _, _ in check(d)}
        if "skills/x/bad.md" not in rels:
            ok = False
            print("selftest: failed to flag skills/x/bad.md", file=sys.stderr)
        for clean in ("skills/x/good.md", "README.md"):
            if clean in rels:
                ok = False
                print(f"selftest: false-flagged {clean}", file=sys.stderr)
        # bad.md should hit ≥5 distinct leftover reasons
        whys = {w for r, _, w in check(d) if r == "skills/x/bad.md"}
        if len(whys) < 5:
            ok = False
            print(f"selftest: bad.md only hit {len(whys)} leftover classes (want ≥5)", file=sys.stderr)
    print("selftest: PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def main(argv):
    if argv and argv[0] == "selftest":
        return _selftest()
    args = [a for a in argv if not a.startswith("-")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: check-self-contained.py <plugin-dir>", file=sys.stderr)
        return 2
    findings = check(args[0])
    for rel, ln, why in findings:
        print(f"  {rel}:{ln}: {why}")
    print(f"RESULT: {'PASS' if not findings else 'FAIL'} ({len(findings)} de-repo leftover(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
