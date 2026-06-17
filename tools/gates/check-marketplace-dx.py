#!/usr/bin/env python3
"""check-marketplace-dx.py — gate the marketplace ENTRY quality (the browse/install DX surface).

`validate_plugin.py marketplace` checks an entry's `name` + `source` (legality, collisions). This gates
the layer above: the **discoverability quality** of the card a user browses — the mechanizable subset of
marketplace-DX (`references/marketplace-dx.md`). The *judgment* subset (first-five-minutes, "stays
enabled", namespace etiquette) is owned by the critics/dimensions named there; this checks only what is
form, not taste:

  - **Scannable card** — `description` present; FAIL if ≥ CARD_FAIL chars (an essay nobody reads in a
    browse list), WARN if ≥ CARD_WARN (the catalog's good cards sit ~275–400).
  - **Category present** — `category` non-empty (FAIL); WARN if outside the recognized set.
  - **Tag hygiene** — `tags` present (FAIL if none); WARN if > TAG_MAX (tag-spam) or a tag isn't kebab-case.

Usage:
  check-marketplace-dx.py marketplace [<repo-root>]   # default: cwd
  check-marketplace-dx.py selftest
Exit 0 = clean (warnings allowed); 1 = a FAIL finding; 2 = usage error. Stdlib only, Python 3.8+.
"""
import json
import os
import re
import sys

CARD_FAIL = 800        # ≥ this many chars in a marketplace card description is unscannable — FAIL
CARD_WARN = 500        # ≥ this is getting long — WARN (the catalog's good cards are ~275–400)
TAG_MAX = 12           # > this many tags is noise, not signal — WARN
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# A recognized category vocabulary (generous); an entry outside it WARNs, it doesn't fail.
KNOWN_CATEGORIES = {
    "design", "developer-tools", "product", "productivity", "data", "devops",
    "security", "ai", "writing", "research", "education", "testing", "fun",
}


def check_entries(plugins):
    """Return (fails, warns) — lists of strings — for a marketplace `plugins` list."""
    fails, warns = [], []
    for entry in plugins:
        if not isinstance(entry, dict):
            fails.append("an entry is not an object")
            continue
        name = entry.get("name") or "<unnamed>"
        desc = entry.get("description")
        if not isinstance(desc, str) or not desc.strip():
            fails.append(f"{name}: missing marketplace-card `description`")
        else:
            n = len(desc)
            if n >= CARD_FAIL:
                fails.append(f"{name}: card description is {n} chars (≥ {CARD_FAIL}) — unscannable in a "
                             f"browse list; cut to a 1–2 sentence pitch (the full scope lives in the README)")
            elif n >= CARD_WARN:
                warns.append(f"{name}: card description is {n} chars (≥ {CARD_WARN}) — getting long for a card")
        cat = entry.get("category")
        if not isinstance(cat, str) or not cat.strip():
            fails.append(f"{name}: missing `category` (the first discovery axis)")
        elif cat not in KNOWN_CATEGORIES:
            warns.append(f"{name}: category {cat!r} is outside the recognized set ({sorted(KNOWN_CATEGORIES)})")
        tags = entry.get("tags")
        if not isinstance(tags, list) or not tags:
            fails.append(f"{name}: missing `tags` (the second discovery axis)")
        else:
            if len(tags) > TAG_MAX:
                warns.append(f"{name}: {len(tags)} tags (> {TAG_MAX}) — tag-spam dilutes discovery; "
                             f"keep the load-bearing few")
            bad = [t for t in tags if not (isinstance(t, str) and KEBAB.match(t))]
            if bad:
                warns.append(f"{name}: non-kebab tag(s) {bad}")
    return fails, warns


def run(root):
    path = os.path.join(root, ".claude-plugin", "marketplace.json")
    try:
        market = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"RESULT: ERROR — cannot read {path}: {e}", file=sys.stderr)
        return 2
    fails, warns = check_entries(market.get("plugins", []))
    for w in warns:
        print(f"  warn:  {w}")
    for f in fails:
        print(f"  FAIL:  {f}", file=sys.stderr)
    n = len(market.get("plugins", []))
    if fails:
        print(f"RESULT: FAIL ({len(fails)} finding(s), {len(warns)} warning(s)) over {n} entr(y/ies)", file=sys.stderr)
        return 1
    print(f"RESULT: PASS ({len(warns)} warning(s)) — marketplace-DX over {n} entr(y/ies)")
    return 0


def selftest():
    fails_out = []

    def expect(cond, msg):
        if not cond:
            fails_out.append(msg)

    clean = {"name": "good-plugin", "category": "developer-tools", "tags": ["a", "b", "c"],
             "description": "A tight, scannable one-line pitch for the browse card."}
    f, w = check_entries([clean])
    expect(f == [] and w == [], f"clean entry flagged: fails={f} warns={w}")

    # over-long card → FAIL
    f, _ = check_entries([{**clean, "description": "x" * CARD_FAIL}])
    expect(any("unscannable" in x for x in f), "missed an over-long card description")
    # long-ish card → WARN (not fail)
    f, w = check_entries([{**clean, "description": "x" * CARD_WARN}])
    expect(f == [] and any("getting long" in x for x in w), "missed the long-card WARN / wrongly failed")
    # missing category → FAIL; odd category → WARN
    f, _ = check_entries([{**clean, "category": ""}])
    expect(any("category" in x for x in f), "missed missing category")
    _, w = check_entries([{**clean, "category": "wat"}])
    expect(any("recognized set" in x for x in w), "missed an off-vocabulary category WARN")
    # missing tags → FAIL; tag-spam → WARN; non-kebab → WARN
    f, _ = check_entries([{**clean, "tags": []}])
    expect(any("tags" in x for x in f), "missed missing tags")
    _, w = check_entries([{**clean, "tags": ["t%d" % i for i in range(TAG_MAX + 1)]}])
    expect(any("tag-spam" in x for x in w), "missed tag-spam WARN")
    _, w = check_entries([{**clean, "tags": ["Bad_Tag"]}])
    expect(any("non-kebab" in x for x in w), "missed non-kebab tag WARN")

    if fails_out:
        sys.stderr.write("check-marketplace-dx selftest: FAIL\n")
        for m in fails_out:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("check-marketplace-dx selftest: OK (clean entry passes; catches over-long/long card, "
          "missing/odd category, missing/spammy/non-kebab tags)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if argv and argv[0] == "marketplace":
        return run(argv[1] if len(argv) > 1 else ".")
    print("usage: check-marketplace-dx.py marketplace [<repo-root>] | selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
