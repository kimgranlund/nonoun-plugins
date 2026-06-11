#!/usr/bin/env python3
"""check.py <transcript> — score a brand-council transcript against the fixture's planted defects.

Given the critique the brand council produced over fixtures/weak-brand-strategy.md, assert it
surfaced each PLANTED defect — the `rubric-brand-strategy` anti-patterns plus the bullshit filter.
Concept-level matching (tolerant of phrasing); reports a catch-rate, not a CI gate, because the
council is an LLM panel.

Usage: check.py <transcript-file>     (exit 0 = every planted defect caught)
Stdlib only.
"""
import re
import sys

PLANTED = {
    "D1 borrowed cultural root (no real provenance)": [
        r"borrowed", r"competitor", r"moodboard", r"other brands", r"\blandscape\b", r"no .{0,14}root",
        r"lifted", r"provenance", r"desk research", r"receipts", r"not .{0,10}earned",
    ],
    "D2 category-restatement position (not exclusive)": [
        r"category restatement", r"restates the category", r"any (?:rival|competitor|brand)", r"could sign",
        r"not exclusive", r"undifferentiated", r"premium choice", r"sign their name", r"no (?:real |ownable )?position",
        r"(?:put|place)s? (?:their|its) name",
    ],
    "D4 no enemy / no tension": [
        r"no enemy", r"nothing to (?:oppose|stand against)", r"frictionless", r"for everyone", r"no tension",
        r"stands? for nothing", r"refuses nothing", r"excludes? no", r"stand against",
    ],
    "D5 persona instead of transformation": [
        r"persona", r"demographic", r"\bsarah\b", r"not a transformation", r"becom(?:e|es|ing)",
        r"before.{0,8}after", r"who they are.{0,20}not",
    ],
    "D6 values without trade-offs": [
        r"trade.?off", r"sacrifice", r"costs? nothing", r"values .{0,20}(?:wish|decoration)", r"give up",
        r"tautolog", r"can(?:not|'t) disagree",
    ],
    "bullshit filter: archetype / VMV doing strategy's job": [
        r"archetype", r"\bexplorer\b", r"horoscope", r"vision/mission/values", r"\bvmv\b",
        r"mission statement", r"boilerplate", r"vision and mission",
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
    print(f"\nbrand council-calibration: {len(caught)}/{len(PLANTED)} planted defects caught")
    return 0 if not missed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check.py <transcript-file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
