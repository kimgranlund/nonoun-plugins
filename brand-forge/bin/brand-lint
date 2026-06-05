#!/usr/bin/env python3
"""brand-lint — structural brand-smell checker (the mechanizable slice of the Foundation Canon's "bullshit filter").

SCOPE (be honest): this checks only PATTERN-MATCHABLE STRUCTURAL smells —
archetype language, the vision/mission/values template, fictional personas, brand-DNA/essence
word-clouds, and values stated without trade-offs. It does NOT judge cultural authority or
"is this on brand" — that is irreducible judgment and lives in the brand-methodology skill +
the council. A clean brand-lint says "no structural tells," never "this brand is good."

Usage:
  brand-lint <file.md>...     # lint files; exit 1 if any smell found, else 0
  brand-lint -                # lint stdin
  brand-lint --hook           # PostToolUse hook mode: read event JSON on stdin, lint the
                              #   written .md/.txt file, print advisory findings, ALWAYS exit 0
Stdlib only (Python 3.8+).
"""
import json
import re
import sys

SMELLS = [
    ("ARCHETYPE",
     re.compile(r"\b(brand\s+archetypes?|(?:the\s+)?(hero|sage|outlaw|magician|innocent|explorer|ruler|creator|caregiver|everyman|jester|lover)\s+archetype|(?:12|twelve)\s+archetypes)\b", re.I),
     "the Foundation Canon rejects archetypes — they substitute a borrowed taxonomy for specific cultural research"),
    ("VMV-TEMPLATE",
     re.compile(r"\b(vision,?\s+mission,?\s+(?:and\s+)?values|mission\s+statement|our\s+mission\s+is\s+to|our\s+vision\s+is\b|core\s+values\s*:)", re.I),
     "the vision/mission/values template is a corporate default, not a brand foundation — name the cultural conviction instead"),
    ("PERSONA",
     re.compile(r"\b((buyer|user|customer|audience)\s+personas?\b|meet\s+[A-Z][a-z]+,?\s+(?:a\s+)?\d{2}[\s-]?year[\s-]?old)", re.I),
     "demographic personas are market research, not cultural research — they describe what customers do, not what the world means"),
    ("BRAND-DNA",
     re.compile(r"\bbrand\s+(dna|essence)\b", re.I),
     "brand DNA / essence word-clouds assert distinctiveness without earning it through cultural depth"),
]

EMPTY_VALUES = {
    "integrity", "excellence", "innovation", "passion", "quality", "respect",
    "teamwork", "authenticity", "trust", "collaboration", "accountability", "transparency",
}
# Contrastive constructions only — a real value names what it gives up. Bare " not "/" before "
# were dropped: any incidental negation must not defuse a genuine empty-values list.
TRADEOFF_MARKERS = (" over ", " instead of ", "we choose", "even when", "at the expense",
                    "rather than", " never ", " refuse", " sacrifice", " trade ")


def lint_text(text):
    findings = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for name, rx, why in SMELLS:
            m = rx.search(line)
            if m:
                snippet = line.strip()[:90]
                findings.append((name, i, snippet, why))
    # doc-level: a VALUES LIST stated without trade-offs. Localized to a single block (not scattered
    # across unrelated prose) AND only when the block reads like a values list — so ordinary use of
    # "quality"/"excellence"/"innovation" in unrelated sentences doesn't trip it (Scott W. N1).
    for blk in re.split(r"\n\s*\n", text):
        blow = blk.lower()
        present = {v for v in EMPTY_VALUES if re.search(r"\b" + re.escape(v) + r"\b", blow)}
        looks_like_values = ("value" in blow) or bool(re.search(r"(?m)^\s*[-*•\d]", blk))
        if len(present) >= 3 and looks_like_values and not any(mk in blow for mk in TRADEOFF_MARKERS):
            findings.append(("VALUES-WITHOUT-TRADEOFFS", 0,
                             "values: " + ", ".join(sorted(present)[:6]),
                             "values that exclude nothing are not values — a real value names what the brand gives up for it"))
            break
    return findings


def _render(path, findings):
    out = [f"brand-lint: {len(findings)} structural smell(s) in {path}"]
    for name, ln, snip, why in findings:
        loc = f"line {ln}" if ln else "document"
        out.append(f"  [{name}] {loc}: {snip}")
        out.append(f"      → {why}")
    return "\n".join(out)


def _hook():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    ti = event.get("tool_input", {}) or {}
    path = ti.get("file_path", "") or ""
    if not path.lower().endswith((".md", ".txt", ".mdx")):
        return 0  # only brand artifacts (prose); stay quiet otherwise
    text = ti.get("content")
    if text is None:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            return 0
    findings = lint_text(text)
    if findings:
        print("⚠ brand-lint (advisory — structural smells only, not a cultural verdict):")
        print(_render(path, findings))
    return 0  # advisory: never block a write


def main(argv):
    if "--hook" in argv:
        return _hook()
    args = [a for a in argv if not a.startswith("-")]
    if not args or argv == ["-"]:
        text = sys.stdin.read()
        findings = lint_text(text)
        print(_render("<stdin>", findings) if findings else "brand-lint: clean (no structural smells)")
        return 1 if findings else 0
    any_found = False
    for path in args:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as e:
            print(f"brand-lint: cannot read {path}: {e}", file=sys.stderr)
            continue
        findings = lint_text(text)
        if findings:
            any_found = True
            print(_render(path, findings))
        else:
            print(f"brand-lint: clean — {path}")
    return 1 if any_found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
