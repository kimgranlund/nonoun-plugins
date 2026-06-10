#!/usr/bin/env python3
"""check-hollow.py <transcript> — score a council transcript against the `docs-studio` fixture.

The companion of check.py for the SECOND fixture shape (build-fixture-hollow.py). It asserts the
council surfaced the two planted JUDGMENT defects that the deterministic gates pass clean and that
isolate the panel's two former blind spots:

  - **H** — hollow components (bodies thinner than their descriptions): AP-P6 / PF5.
  - **L** — a dead-but-wired MCP (task-shaped tools, no server loop): AP-P7 / CF5.

Matching is concept-level (LLM panel → catch-RATE, not a deterministic CI gate). Stdlib only.

Usage: check-hollow.py <transcript-file>     (exit 0 = both planted defects caught)
"""
import re
import sys

PLANTED = {
    "H hollow components — bodies thinner than their descriptions (AP-P6/PF5)": [
        r"hollow", r"thinner than", r"thin(?:ner)? .{0,30}(?:body|bodies|content)",
        r"(?:body|bodies) .{0,30}(?:thin|one sentence|single sentence|restate)",
        r"out.?promis", r"promis\w* .{0,40}(?:more than|than (?:it|they) deliver|but deliver)",
        r"one[ -]sentence", r"single[ -]sentence", r"restates? (?:its|the) (?:frontmatter|description)",
        r"no references?\b", r"nothing to disclose", r"adds? routing surface", r"deepen or delete",
        r"vacan(?:t|cy)", r"empt(?:y|iness)", r"\bstub(?:s|bed)?\b", r"skeleton", r"placeholder",
        r"lean by hollow", r"description out-?runs", r"more (?:promise|description) than (?:body|substance)",
        r"zero capability", r"no (?:real )?(?:capability|substance|depth)", r"\bpf5\b", r"\bap-?p6\b",
    ],
    "L dead-but-wired MCP — defines tools but never serves them (AP-P7/CF5)": [
        r"dead.?(?:but.?)?wired", r"dead code", r"dead.?on.?arrival",
        r"never (?:serves|answers|responds|runs|starts)", r"doesn't (?:run|start|serve|respond|answer)",
        r"no (?:json-?rpc|stdin|server|protocol|main) loop", r"no (?:stdin|server) (?:read|loop)",
        r"defines? .{0,30}tools?.{0,30}exits?", r"exits? (?:immediately|at (?:launch|startup))",
        r"non-?functional", r"\bliveness\b", r"smoke test", r"tools/list", r"no __main__",
        r"never (?:speaks?|implements?) .{0,20}protocol", r"wired .{0,20}(?:dead|nothing|never)",
        r"can(?:not|'t) (?:answer|respond|serve)", r"\bcf5\b", r"\bap-?p7\b",
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
    print(f"\ncouncil-calibration (docs-studio): {len(caught)}/{len(PLANTED)} planted defects caught")
    return 0 if not missed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check-hollow.py <transcript-file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
