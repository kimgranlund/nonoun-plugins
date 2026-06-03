#!/usr/bin/env python3
"""check-foundations-coverage.py — gate the foundations/ ↔ rubrics/ contract.

Every theory doc in references/foundations/ must have exactly one rubric that claims it via the
`foundation` field in references/rubric-manifest.json, and every `foundation` link must resolve.
This turns the foundation↔rubric mapping from an asserted name-correspondence into a checked fact
(the 2026-05-31 audit found governance/plan-anatomy rubrics orphaned from the registry and the
rubric-foundations doc with no standalone rubric).

Checks (any failure → exit 1):
  - ORPHAN FOUNDATION  — a foundations/*.md no rubric's `foundation` field points to.
  - BROKEN LINK        — a `foundation` field that doesn't resolve to a file on disk.
  - DUPLICATE CLAIM    — two rubrics claiming the same foundation (the pairing is 1:1).
  - MISSING RUBRIC FILE — a manifest entry whose `file` isn't on disk.
Informational (not a failure): rubrics with no `foundation` (not every rubric needs a theory doc).

Usage: check-foundations-coverage.py [--json]
Exit 0 = contract holds; 1 = a gap; 2 = bad invocation / unreadable manifest.
"""
from __future__ import annotations
import argparse
import json
import os
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(SKILL_ROOT, "references")
MANIFEST = os.path.join(REFS, "rubric-manifest.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="check-foundations-coverage.py",
                                 description="Gate the foundations/ ↔ rubrics/ coverage contract.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: cannot read {MANIFEST} — {e}", file=sys.stderr)
        return 2

    rubrics = manifest.get("rubrics", [])
    foundations_dir = os.path.join(REFS, "foundations")
    on_disk = {f for f in os.listdir(foundations_dir) if f.endswith(".md")} \
        if os.path.isdir(foundations_dir) else set()

    # foundation file (basename) -> [rubric names that claim it]
    claims: dict[str, list[str]] = {}
    broken_links, missing_files, no_foundation = [], [], []
    for r in rubrics:
        name = r.get("name", "?")
        rf = r.get("file")
        if rf and not os.path.isfile(os.path.join(REFS, rf)):
            missing_files.append((name, rf))
        f = r.get("foundation")
        if not f:
            no_foundation.append(name)
            continue
        if not os.path.isfile(os.path.join(REFS, f)):
            broken_links.append((name, f))
            continue
        claims.setdefault(os.path.basename(f), []).append(name)

    orphan_foundations = sorted(b for b in on_disk if b not in claims)
    duplicate_claims = {f: rs for f, rs in claims.items() if len(rs) > 1}

    errors = bool(orphan_foundations or broken_links or duplicate_claims or missing_files)
    result = {
        "foundations_on_disk": len(on_disk),
        "foundations_covered": len(on_disk) - len(orphan_foundations),
        "orphan_foundations": orphan_foundations,
        "broken_links": broken_links,
        "duplicate_claims": duplicate_claims,
        "missing_rubric_files": missing_files,
        "rubrics_without_foundation": sorted(no_foundation),
        "ok": not errors,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"foundations ↔ rubrics coverage — {result['foundations_covered']}/{len(on_disk)} foundations claimed")
        for f in sorted(on_disk):
            who = claims.get(f)
            print(f"  [{'OK ' if who else 'GAP'}] {f}" + (f"  <- {', '.join(who)}" if who else "  <- (no rubric claims it)"))
        if broken_links:
            print("\n  BROKEN LINKS (foundation field points at a missing file):")
            for n, f in broken_links:
                print(f"    - {n} -> {f}")
        if duplicate_claims:
            print("\n  DUPLICATE CLAIMS (a foundation should be claimed by exactly one rubric):")
            for f, rs in duplicate_claims.items():
                print(f"    - {f} <- {', '.join(rs)}")
        if missing_files:
            print("\n  MISSING RUBRIC FILES:")
            for n, f in missing_files:
                print(f"    - {n} -> {f}")
        if no_foundation:
            print(f"\n  (info) {len(no_foundation)} rubric(s) carry no foundation link "
                  f"— fine if they have no theory doc: {', '.join(sorted(no_foundation))}")
        print(f"\nRESULT: {'PASS — every foundation has exactly one rubric' if not errors else 'FAIL'}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
