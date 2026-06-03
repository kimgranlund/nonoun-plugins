#!/usr/bin/env python3
"""check-sourcing.py — the provenance gate for product-forge.

product-forge's whole value proposition is GROUNDED authority, and its council renders named —
often living — practitioners. A fabricated quote or an unsourced claim is the worst failure mode.
This gate turns "everything is sourced" from author discipline into a verifiable property:

  - every library reference (under skills/{methodology,research,patterns,genres}/references/) MUST
    carry YAML frontmatter with `date`, `coverage`, and `primary_sources`;
  - every council critic (agents/critic-*.md) MUST carry a source signal — an explicit Sourcing
    block, a URL, or a year citation.

It does NOT verify a quote is accurate (only a human/web-fetch can) — but it guarantees nothing
ships unsourced. Run it in CI alongside validate_plugin.py / reference-lint.py.

Usage:
  check-sourcing.py <plugin-dir>   # exit 0 if all sourced, 1 if any gap, 2 on bad invocation
  check-sourcing.py selftest
Stdlib only (Python 3.8+).
"""
import os
import re
import sys

LIBRARY_SKILLS = ("product-methodology", "product-research", "product-patterns", "product-genres")
REQUIRED_FM = ("date", "coverage", "primary_sources")
SOURCE_SIGNAL = re.compile(r"Sourcing|https?://|(?:19|20)\d\d")  # a Sourcing block, a URL, or a year


def _frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def check(root):
    root = os.path.abspath(root)
    findings = []
    for skill in LIBRARY_SKILLS:
        refdir = os.path.join(root, "skills", skill, "references")
        for dp, _dirs, files in os.walk(refdir):
            for fn in sorted(files):
                if not fn.endswith(".md"):
                    continue
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, root)
                fm = _frontmatter(open(fp, encoding="utf-8", errors="replace").read())
                if fm is None:
                    findings.append((rel, "no YAML frontmatter (need date + coverage + primary_sources)"))
                    continue
                missing = [k for k in REQUIRED_FM if not re.search(rf"(?m)^{k}\s*:", fm)]
                if missing:
                    findings.append((rel, "missing frontmatter: " + ", ".join(missing)))
    agdir = os.path.join(root, "agents")
    if os.path.isdir(agdir):
        for fn in sorted(os.listdir(agdir)):
            if not (fn.startswith("critic-") and fn.endswith(".md")):
                continue
            text = open(os.path.join(agdir, fn), encoding="utf-8", errors="replace").read()
            if not SOURCE_SIGNAL.search(text):
                findings.append((os.path.join("agents", fn),
                                 "critic carries no source signal (Sourcing block / URL / year)"))
    return findings


def _selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        fl = os.path.join(d, "skills", "product-patterns", "references", "flows")
        os.makedirs(fl)
        open(os.path.join(fl, "good.md"), "w").write(
            "---\ndate: 2026-06-03\ncoverage: foundational\nprimary_sources:\n  - NN/g\n---\n# ok\n")
        open(os.path.join(fl, "bad.md"), "w").write("# no frontmatter here\n")
        ag = os.path.join(d, "agents")
        os.makedirs(ag)
        open(os.path.join(ag, "critic-sourced.md"), "w").write(
            "---\nname: critic-sourced\n---\nGrounded in <https://example.com> (2020).\n")
        open(os.path.join(ag, "critic-bare.md"), "w").write(
            "---\nname: critic-bare\n---\nNo source signal in this body.\n")
        rels = {r for r, _ in check(d)}
        for expect_flag in ("skills/product-patterns/references/flows/bad.md",
                            os.path.join("agents", "critic-bare.md")):
            if expect_flag not in rels:
                ok = False
                print(f"selftest: failed to flag {expect_flag}", file=sys.stderr)
        for expect_clean in ("skills/product-patterns/references/flows/good.md",
                            os.path.join("agents", "critic-sourced.md")):
            if expect_clean in rels:
                ok = False
                print(f"selftest: false-flagged {expect_clean}", file=sys.stderr)
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
