#!/usr/bin/env python3
"""corpus-migrate — convert a brand corpus between its two output conventions (the brand-corpus extension point).

`skills/brand-corpus/references/corpus-architecture.md` defines two shapes for the same eight-layer corpus and
calls migration between them MECHANICAL:

  flat (a Claude **project** — no folders):   01-foundation--the-position.md     (NN-layer--name.md)
  folder (a repo / Cowork):                    01-foundation/the-position.md      (NN-layer/name.md)

This is that mechanical migration, made a tool: it detects the current shape, refuses a MIXED corpus (both
conventions present is a corpus defect the architecture says to reconcile first), and renames every layer asset to
the target shape. **Dry-run by default** — it prints the moves and changes nothing until `--apply`. Layer prefixes
and the per-asset name are preserved exactly; only the separator (`--` ⟷ `/`) changes.

Usage:
  corpus-migrate <corpus-dir> --to folder [--apply]   # flat  → folder  (NN-layer--x.md → NN-layer/x.md)
  corpus-migrate <corpus-dir> --to flat   [--apply]   # folder → flat   (NN-layer/x.md → NN-layer--x.md)
  corpus-migrate <corpus-dir>                         # detect + report the corpus's current shape
  corpus-migrate selftest
Exit 0 = clean (or a clean dry-run); 1 = a mixed-corpus defect / nothing to do with --apply; 2 = usage error.
Stdlib only; Python 3.8+.
"""
import os
import re
import sys

# The eight canonical layers (skills/brand-corpus/SKILL.md). Load-order numbering is part of the prefix.
LAYERS = ("00-sources", "01-foundation", "02-positioning", "03-identity", "04-expression",
          "05-voice", "06-product", "07-guidelines", "08-evaluation")
_LAYER_RE = "|".join(re.escape(l) for l in LAYERS)
FLAT_RE = re.compile(rf"^({_LAYER_RE})--(.+)\.md$")        # 01-foundation--the-position.md


def _flat_assets(d):
    """Top-level flat files: [(path, layer, name)]."""
    out = []
    for fn in sorted(os.listdir(d)):
        m = FLAT_RE.match(fn)
        if m and os.path.isfile(os.path.join(d, fn)):
            out.append((os.path.join(d, fn), m.group(1), m.group(2)))
    return out


def _folder_assets(d):
    """Layer-folder files: [(path, layer, name)] for NN-layer/<name>.md."""
    out = []
    for layer in LAYERS:
        ld = os.path.join(d, layer)
        if os.path.isdir(ld):
            for fn in sorted(os.listdir(ld)):
                if fn.endswith(".md") and os.path.isfile(os.path.join(ld, fn)):
                    out.append((os.path.join(ld, fn), layer, fn[:-3]))
    return out


def detect(d):
    """Return ('flat'|'folder'|'mixed'|'empty', flat_assets, folder_assets)."""
    flat, folder = _flat_assets(d), _folder_assets(d)
    if flat and folder:
        return "mixed", flat, folder
    if flat:
        return "flat", flat, folder
    if folder:
        return "folder", flat, folder
    return "empty", flat, folder


def _planned_moves(d, to):
    shape, flat, folder = detect(d)
    if shape == "mixed":
        return None, "mixed", []
    if to == "folder":
        return [(p, os.path.join(d, layer, name + ".md")) for p, layer, name in flat], shape, flat
    return [(p, os.path.join(d, f"{layer}--{name}.md")) for p, layer, name in folder], shape, folder


def migrate(d, to, apply=False, out=print):
    if to not in ("flat", "folder"):
        out(f"corpus-migrate: --to must be 'flat' or 'folder', got {to!r}")
        return 2
    moves, shape, _src = _planned_moves(d, to)
    if shape == "mixed":
        out("corpus-migrate: MIXED corpus — both flat (NN-layer--x.md) and folder (NN-layer/x.md) conventions are "
            "present. That is a corpus defect; reconcile to one shape before migrating. (Run with no --to to list both.)")
        return 1
    if shape == to:
        out(f"corpus-migrate: the corpus is already in {to} shape — nothing to do.")
        return 0
    if not moves:
        out(f"corpus-migrate: no layer assets found to migrate to {to} (looked for the eight NN-layer assets).")
        return 0
    verb = "would move" if not apply else "moved"
    for src, dst in moves:
        out(f"  {verb}  {os.path.relpath(src, d)}  →  {os.path.relpath(dst, d)}")
        if apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.replace(src, dst)
    if apply and to == "flat":
        for layer in LAYERS:                              # tidy now-empty layer dirs after folder→flat
            ld = os.path.join(d, layer)
            if os.path.isdir(ld) and not os.listdir(ld):
                os.rmdir(ld)
    out(f"corpus-migrate: {len(moves)} asset(s) {'migrated to' if apply else 'would migrate to'} {to} shape"
        + ("" if apply else " — re-run with --apply to perform the moves."))
    return 0


def report(d, out=print):
    shape, flat, folder = detect(d)
    msg = {"flat": f"FLAT (a Claude project) — {len(flat)} layer asset(s) named NN-layer--name.md.",
           "folder": f"FOLDER (a repo / Cowork) — {len(folder)} layer asset(s) under NN-layer/ directories.",
           "mixed": f"MIXED — {len(flat)} flat + {len(folder)} folder asset(s). A corpus defect: reconcile to one shape.",
           "empty": "EMPTY — no NN-layer assets in either convention."}[shape]
    out(f"corpus-migrate: corpus shape is {msg}")
    return 1 if shape == "mixed" else 0


def selftest():
    import tempfile
    fails = []

    def expect(c, m):
        if not c:
            fails.append(m)

    with tempfile.TemporaryDirectory() as d:
        # build a flat corpus, migrate → folder, assert; migrate back → flat, assert
        for fn in ("00-sources--interview.md", "01-foundation--the-position.md", "05-voice--tone.md", "08-evaluation--audit-q1.md", "README.md"):
            open(os.path.join(d, fn), "w").write("x")
        expect(detect(d)[0] == "flat", "a flat corpus was not detected as flat")
        migrate(d, "folder", apply=True, out=lambda *_: None)
        expect(os.path.isfile(os.path.join(d, "00-sources", "interview.md")), "flat→folder did not move 00-sources (retained inputs)")
        expect(os.path.isfile(os.path.join(d, "01-foundation", "the-position.md")), "flat→folder did not move foundation")
        expect(os.path.isfile(os.path.join(d, "05-voice", "tone.md")), "flat→folder did not move voice")
        expect(os.path.isfile(os.path.join(d, "README.md")), "migration disturbed a non-layer file")
        expect(not os.path.isfile(os.path.join(d, "01-foundation--the-position.md")), "flat→folder left the flat file")
        expect(detect(d)[0] == "folder", "post-migration corpus was not detected as folder")
        migrate(d, "flat", apply=True, out=lambda *_: None)
        expect(os.path.isfile(os.path.join(d, "01-foundation--the-position.md")), "folder→flat did not restore foundation")
        expect(not os.path.isdir(os.path.join(d, "01-foundation")), "folder→flat left an empty layer dir")
        expect(detect(d)[0] == "flat", "round-trip did not return to flat")
        # dry-run changes nothing
        before = sorted(os.listdir(d))
        rc = migrate(d, "folder", apply=False, out=lambda *_: None)
        expect(rc == 0 and sorted(os.listdir(d)) == before, "a dry-run mutated the corpus")
        # a mixed corpus is refused
        os.makedirs(os.path.join(d, "02-positioning"))
        open(os.path.join(d, "02-positioning", "territory.md"), "w").write("x")  # now flat + folder both present
        expect(detect(d)[0] == "mixed", "a mixed corpus was not detected")
        expect(migrate(d, "folder", apply=True, out=lambda *_: None) == 1, "a mixed corpus was not refused")

    if fails:
        sys.stderr.write("corpus-migrate selftest: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("corpus-migrate selftest: OK (flat↔folder round-trips losslessly, preserves non-layer files, tidies empty "
          "layer dirs, dry-run is read-only, a mixed corpus is refused as a defect)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv:
        print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
        return 2
    d = argv[0]
    if not os.path.isdir(d):
        print(f"corpus-migrate: not a directory: {d}", file=sys.stderr)
        return 2
    if "--to" in argv:
        to = argv[argv.index("--to") + 1] if argv.index("--to") + 1 < len(argv) else ""
        return migrate(d, to, apply="--apply" in argv)
    return report(d)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
