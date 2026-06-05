#!/usr/bin/env python3
"""check-sourcing.py — the council provenance gate for agent-ops.

agent-ops's council renders lenses distilled from real, widely recognized software / AI-agent
engineering practitioners. Their identifying attributions, bios, and sources are kept OUT of the
committed files by design and live in the git-ignored `agents/.name-map.md`; each committed
`agents/critic-*.md` carries only the obscured `First L.` display name plus a pointer to that map.
A fabricated quote or an unsourced lens is the worst failure mode, so this gate turns "every critic
is provenanced" from author discipline into a verifiable property: every `agents/critic-*.md` MUST
carry a source signal — an explicit Sourcing block, a URL, a year citation, OR a reference to the
git-ignored `.name-map.md` where the real attribution/sources live — and the council roster's stated
critic count (`agents/*council*.md`) MUST match the number of `critic-*.md` files on disk, so the
roster can't drift from the tree.

Unlike product-forge, agent-ops does NOT gate library-reference frontmatter: its references are ported,
already-sourced methodology (citing Anthropic, NN/g, papers in prose), not a dated research library.
The distilled-practitioner council is the provenance surface that needs the gate.

It does NOT verify a quote is accurate (only a human / web-fetch can) — but it guarantees no critic
ships without a provenance pointer. Run it in CI alongside validate_plugin.py / reference-lint.py.

Usage:
  check-sourcing.py <plugin-dir>   # exit 0 if every critic is provenanced + count matches, 1 if any gap
  check-sourcing.py selftest
Stdlib only (Python 3.8+).
"""
import os
import re
import sys

# A Sourcing block, a URL, a year, or a pointer to the git-ignored name-map that holds the real source.
SOURCE_SIGNAL = re.compile(r"Sourcing|https?://|(?:19|20)\d\d|\.name-map\.md")
ROSTER_COUNT = re.compile(r"\((\d+)\s+critics?\)")


def check(root):
    root = os.path.abspath(root)
    findings = []
    agdir = os.path.join(root, "agents")
    critic_files = []
    if os.path.isdir(agdir):
        for fn in sorted(os.listdir(agdir)):
            if not (fn.startswith("critic-") and fn.endswith(".md")):
                continue
            critic_files.append(fn)
            text = open(os.path.join(agdir, fn), encoding="utf-8", errors="replace").read()
            if not SOURCE_SIGNAL.search(text):
                findings.append((os.path.join("agents", fn),
                                 "critic carries no source signal (Sourcing block / URL / year)"))
        # roster-count integrity: a council orchestrator's "(N critics)" must match the files on disk
        for fn in sorted(os.listdir(agdir)):
            if fn.endswith(".md") and "council" in fn and not fn.startswith("critic-"):
                m = ROSTER_COUNT.search(open(os.path.join(agdir, fn), encoding="utf-8", errors="replace").read())
                if m and critic_files and int(m.group(1)) != len(critic_files):
                    findings.append((os.path.join("agents", fn),
                                     f"roster says {m.group(1)} critics but {len(critic_files)} critic-*.md files exist"))
    return findings


def _selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        ag = os.path.join(d, "agents")
        os.makedirs(ag)
        open(os.path.join(ag, "critic-sourced.md"), "w").write(
            "---\nname: critic-sourced\n---\nGrounded in <https://example.com> (2020).\n")
        open(os.path.join(ag, "critic-bare.md"), "w").write(
            "---\nname: critic-bare\n---\nNo source signal in this body.\n")
        open(os.path.join(ag, "agentic-council.md"), "w").write("## Roster (9 critics)\n")  # wrong: 2 exist
        rels = {r for r, _ in check(d)}
        for expect in (os.path.join("agents", "critic-bare.md"), os.path.join("agents", "agentic-council.md")):
            if expect not in rels:
                ok = False
                print(f"selftest: failed to flag {expect}", file=sys.stderr)
        if os.path.join("agents", "critic-sourced.md") in rels:
            ok = False
            print("selftest: false-flagged critic-sourced.md", file=sys.stderr)
    print("selftest: PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def main(argv):
    if argv and argv[0] == "selftest":
        return _selftest()
    args = [a for a in argv if not a.startswith("-")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: check-sourcing.py <plugin-dir>", file=sys.stderr)
        return 2
    findings = check(args[0])
    for rel, why in findings:
        print(f"  {rel}: {why}")
    print(f"RESULT: {'PASS' if not findings else 'FAIL'} ({len(findings)} sourcing gap(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
