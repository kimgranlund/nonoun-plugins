#!/usr/bin/env python3
"""corpus-provenance — audit a brand corpus's provenance integrity (the 00-sources trace + attribution).

Mechanizes the two corpus-architecture audit items the 0.4.27 work added (§ Extension point → audit checklist):
  7. Sources retained + traced — every `sources:` reference resolves to a real file in the corpus.
  8. Provenance present       — foundation/positioning artifacts name their `contributors`.

HARD failure (exit 1): a `sources:` entry that resolves to no file in the corpus — a **broken trace**, the
exact defect retention exists to prevent (the evidence an artifact claims to rest on isn't there). ADVISORY
(WARN, exit 0): a `sources:` ref that resolves but lives outside `00-sources`, and a 01–02 artifact with no
`contributors`. The discipline is gated where it's a real defect, advisory where it's a judgment call.

Usage:
  corpus-provenance <corpus>     # audit a brand corpus (exit 1 on a broken source trace)
  corpus-provenance selftest     # the gate proves itself
Stdlib only; Python 3.8+. Detects both conventions — flat (NN-layer--name.md) and folder (NN-layer/name.md) —
and resolves a `sources:` ref across the two (a flat-style ref still resolves in a folder corpus, and back).
"""
import os
import re
import sys

LAYERS = ("00-sources", "01-foundation", "02-positioning", "03-identity", "04-expression",
          "05-voice", "06-product", "07-guidelines", "08-evaluation")
ATTRIB_LAYERS = ("01-foundation", "02-positioning")  # layers where missing attribution is worth a warning
_LAYER_RE = "|".join(re.escape(l) for l in LAYERS)
FLAT_RE = re.compile(rf"^({_LAYER_RE})--(.+)\.md$")


def _docs(root):
    out = []
    for r, _d, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".md"):
                out.append(os.path.relpath(os.path.join(r, f), root).replace(os.sep, "/"))
    return sorted(out)


def _layer_of(rel):
    rel = rel.replace(os.sep, "/")
    m = FLAT_RE.match(rel)
    if m:
        return m.group(1)
    seg = rel.split("/", 1)[0]
    return seg if seg in LAYERS else None


def _frontmatter(full):
    try:
        head = open(full, encoding="utf-8", errors="replace").read(8000)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    return head[3:end] if end != -1 else None


def _provenance(fm):
    """(contributors:list[str], sources:list[str]) from a frontmatter block — the same tolerant parse
    the brand-corpus MCP uses, no yaml dependency."""
    if not fm:
        return [], []
    who = [w.strip() for w in re.findall(r'who:\s*["\']?([^"\',}\n]+)', fm) if w.strip()]
    inline = re.search(r'sources:\s*\[([^\]]*)\]', fm)
    if inline:
        src = [s.strip().strip('"\'') for s in inline.group(1).split(",") if s.strip()]
    else:
        block = re.search(r'sources:\s*\n((?:[ \t]*-[ \t]*.+\n?)+)', fm)
        src = ([re.sub(r'^[ \t]*-[ \t]*', '', ln).strip().strip('"\'')
                for ln in block.group(1).splitlines() if ln.strip()] if block else [])
    return who, [s for s in src if s]


def _resolve_source(root, ref):
    """(exists, is_under_00_sources). Tries the literal ref + the flat⟷folder translation of a 00-sources
    ref, with a traversal/symlink-escape guard (a ref pointing outside the corpus counts as unresolved)."""
    base = os.path.realpath(root)
    ref = ref.lstrip("./").replace("\\", "/")
    cands = {ref}
    m = re.match(r'^00-sources--(.+)$', ref)
    if m:
        cands.add("00-sources/" + m.group(1))
    m = re.match(r'^00-sources/(.+)$', ref)
    if m:
        cands.add("00-sources--" + m.group(1))
    for c in cands:
        full = os.path.realpath(os.path.join(base, c))
        if (full == base or full.startswith(base + os.sep)) and os.path.isfile(full):
            return True, _layer_of(c) == "00-sources"
    return False, False


def audit(root, out=print):
    hard, warn = [], []
    for rel in _docs(root):
        who, srcs = _provenance(_frontmatter(os.path.join(root, rel)))
        layer = _layer_of(rel)
        for ref in srcs:
            exists, under = _resolve_source(root, ref)
            if not exists:
                hard.append(f"{rel}: sources → '{ref}' resolves to no file in the corpus (broken trace)")
            elif not under:
                warn.append(f"{rel}: sources → '{ref}' resolves but is not under 00-sources")
        if layer in ATTRIB_LAYERS and not who:
            warn.append(f"{rel}: no `contributors` — {layer} artifacts should name who shaped them")
    for h in hard:
        out(f"  FAIL  {h}")
    for w in warn:
        out(f"  WARN  {w}")
    if hard:
        out(f"RESULT: FAIL ({len(hard)} broken source trace(s), {len(warn)} advisory warning(s))")
        return 1
    out(f"RESULT: PASS (0 broken source traces, {len(warn)} advisory warning(s))")
    return 0


def selftest():
    import shutil
    import tempfile
    fails = []

    def expect(c, m):
        if not c:
            fails.append(m)

    d = tempfile.mkdtemp(prefix="corpus-provenance-selftest-")
    try:
        os.makedirs(os.path.join(d, "00-sources"))
        os.makedirs(os.path.join(d, "01-foundation"))
        open(os.path.join(d, "00-sources", "interview.md"), "w").write("# Interview\n")
        # clean: a real source + contributors → passes with no findings
        open(os.path.join(d, "01-foundation", "position.md"), "w").write(
            '---\ncontributors:\n  - {who: "Muse", role: aspiration, date: 2026-06-20}\n'
            'sources: [00-sources/interview.md]\n---\n# Position\n')
        expect(audit(d, out=lambda *_: None) == 0, "a clean corpus did not pass")
        # dangling source ref → HARD fail (exit 1)
        broken = os.path.join(d, "01-foundation", "broken.md")
        open(broken, "w").write('---\nsources: [00-sources/missing.md]\n---\n# Broken\n')
        expect(audit(d, out=lambda *_: None) == 1, "a dangling source ref was not failed")
        os.remove(broken)
        # missing attribution on a 01 doc → advisory WARN, still exit 0
        noattr = os.path.join(d, "01-foundation", "noattr.md")
        open(noattr, "w").write("# no frontmatter at all\n")
        warns = []
        expect(audit(d, out=lambda m: warns.append(m)) == 0, "a missing-attribution warning wrongly failed the audit")
        expect(any("no `contributors`" in w for w in warns), "missing attribution was not warned")
        os.remove(noattr)
        # cross-convention: a flat-style source ref resolves to the folder file
        open(os.path.join(d, "01-foundation", "xconv.md"), "w").write(
            '---\ncontributors:\n  - {who: "X", role: author, date: 2026-06-20}\n'
            'sources: [00-sources--interview.md]\n---\n# X\n')
        expect(audit(d, out=lambda *_: None) == 0, "a cross-convention (flat-style) source ref did not resolve")
        # a source ref outside 00-sources → advisory WARN (not a hard fail)
        open(os.path.join(d, "01-foundation", "wronglayer.md"), "w").write(
            '---\ncontributors:\n  - {who: "Y", role: author, date: 2026-06-20}\n'
            'sources: [01-foundation/position.md]\n---\n# Y\n')
        w2 = []
        expect(audit(d, out=lambda m: w2.append(m)) == 0, "an out-of-layer source ref wrongly hard-failed")
        expect(any("not under 00-sources" in w for w in w2), "an out-of-layer source ref was not warned")
        # a traversal source ref is treated as unresolved (HARD), never followed outside the corpus
        open(os.path.join(d, "01-foundation", "evil.md"), "w").write(
            '---\nsources: [../../etc/passwd]\n---\n# Evil\n')
        expect(audit(d, out=lambda *_: None) == 1, "a traversal source ref was not treated as a broken trace")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if fails:
        sys.stderr.write("corpus-provenance selftest: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("corpus-provenance selftest: OK (clean passes; a dangling source ref FAILs; missing attribution + "
          "out-of-layer refs WARN but pass; flat⟷folder refs resolve; a traversal ref is a broken trace)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stderr.write(__doc__ or "")
        return 0
    root = argv[0]
    if not os.path.isdir(root):
        sys.stderr.write(f"corpus-provenance: '{root}' is not a directory\n")
        return 2
    return audit(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
