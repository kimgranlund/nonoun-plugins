#!/usr/bin/env python3
"""guidelines-ledger — validate the brand-guidelines elicitation choice-ledger (well-formed by construction).

The `/brand-elicit` loop walks the six brand domains; for each it crosses two of the seven exploration
axes into a 2×2, the designer picks a quadrant (A/B/C/D) + comments, and the chosen "design move" is
appended to a **choice-ledger** — the cumulative state the assembler later compiles into corpus docs. This
gate keeps that ledger well-formed by construction (the score-record / assess-record discipline): a malformed
choice is rejected at write time, not discovered at assembly. It also computes coverage, **assembles** the
ledger into corpus docs, and **projects a brand-spec card** for the optional brand-decomposer grading seam.

The six domains + seven axes MIRROR `design-skills:brand-decomposer` (a parallel skill, NOT a dependency —
brand-forge MAKES, brand-decomposer GRADES); they are restated here as stable vocabulary, not imported. The
`card` projection targets brand-decomposer's documented `*.brand.json` shape so it can be GRADED there
(`brand-spec-check.py lint <card>`) when installed — best-effort to that shape, not a hard contract.

Usage:
  guidelines-ledger validate <ledger.json>                                       # exit 1 on any malformed entry
  guidelines-ledger coverage <ledger.json>                                       # per-domain resolved/absent + frontier
  guidelines-ledger coherence <ledger.json> [--domain <d>] [--strict]            # prior commitments + edges + contradictions
  guidelines-ledger assemble <ledger.json> --out <corpus> [--flat] [--apply]     # ledger → corpus docs (dry-run default)
  guidelines-ledger card <ledger.json> [--idea "..."] [-o <out.json>]            # project a brand-spec card (brand-decomposer seam)
  guidelines-ledger template | schema | selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

DOMAINS = ("mark", "voice", "color", "type", "expression", "governance")
AXES = ("functional-expressive", "product-led-human-led", "quiet-loud", "literal-metaphorical",
        "restraint-loudness", "institutional-conversational", "systematic-organic")
QUADRANTS = ("A", "B", "C", "D")
# the brand-decomposer relationship vocabulary, for the optional coherence graph
RELATIONSHIPS = ("supports", "expresses", "constrains", "contradicts", "exemplifies", "prohibits",
                 "specializes", "inherits_from", "applies_to_surface", "derived_from")
MOVE_REQUIRED = ("move", "rationale", "expected_effect")
SEVERITIES = ("must", "should", "may")
# domain → corpus layer the assembler writes it into (the design's domain↦layer map)
LAYER_OF = {"mark": "03-identity", "voice": "05-voice", "color": "04-expression",
            "type": "04-expression", "expression": "04-expression", "governance": "07-guidelines"}
DEFAULT_CORPUS = "brand-corpus"  # the catalog default corpus root (matches /brand-corpus-export, /brand-stack)
DEFAULT_LEDGER = os.path.join(DEFAULT_CORPUS, "00-sources", "guidelines-elicitation.json")


def _validate_entry(e, i, ids):
    p = []

    def bad(msg):
        p.append(f"entries[{i}]: {msg}")

    if not isinstance(e, dict):
        return [f"entries[{i}]: not an object"]
    if not e.get("id"):
        bad("missing `id`")
    if e.get("domain") not in DOMAINS:
        bad(f"`domain` must be one of {DOMAINS}, got {e.get('domain')!r}")
    if not isinstance(e.get("round"), int) or e.get("round", 0) < 1:
        bad("`round` must be an integer ≥ 1")
    axes = e.get("axes")
    if not (isinstance(axes, list) and len(axes) == 2 and len(set(axes)) == 2 and all(a in AXES for a in axes)):
        bad(f"`axes` must be two distinct values from {AXES}, got {axes!r}")
    presented = e.get("presented", list(QUADRANTS))
    if not (isinstance(presented, list) and presented and all(q in QUADRANTS for q in presented)):
        bad(f"`presented` must be a non-empty subset of {QUADRANTS}, got {presented!r}")
        presented = list(QUADRANTS)
    if e.get("chosen") not in presented:
        bad(f"`chosen` ({e.get('chosen')!r}) must be one of the presented quadrants {presented}")
    move = e.get("move")
    if not isinstance(move, dict):
        bad("`move` (the chosen design-move) is required and must be an object")
    else:
        for k in MOVE_REQUIRED:
            if not str(move.get(k, "")).strip():
                bad(f"`move.{k}` is required and non-empty")
        conf = move.get("confidence")
        if conf is not None and not (isinstance(conf, (int, float)) and 0.0 <= conf <= 1.0):
            bad(f"`move.confidence` must be in [0,1], got {conf!r}")
        sev = move.get("severity")
        if sev is not None and sev not in SEVERITIES:
            bad(f"`move.severity` must be one of {SEVERITIES} if present, got {sev!r}")
        ev = move.get("exemplar_evidence", [])
        if ev and not (isinstance(ev, list) and all(isinstance(x, dict) and x.get("brand") for x in ev)):
            bad("`move.exemplar_evidence[]` entries each need at least a `brand`")
    contribs = e.get("contributors")
    if not (isinstance(contribs, list) and contribs):
        bad("`contributors` is required and non-empty (who shaped this choice)")
    else:
        for j, c in enumerate(contribs):
            if not (isinstance(c, dict) and c.get("who") and c.get("role") and c.get("date")):
                bad(f"contributors[{j}] needs `who`, `role`, `date`")
    sup = e.get("supersedes")
    if sup is not None and sup not in ids:
        bad(f"`supersedes` ({sup!r}) does not reference an earlier entry id")
    return p


def validate(ledger):
    """Return a list of problems ([] = valid). Validates the whole choice-ledger."""
    p = []
    if not isinstance(ledger, dict):
        return ["ledger is not a JSON object"]
    for k in ("brand", "created"):
        if not str(ledger.get(k, "")).strip():
            p.append(f"ledger missing `{k}`")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return p + ["`entries` must be a list"]
    seen = set()
    for i, e in enumerate(entries):
        prior_ids = set(seen)  # supersedes may only point at an EARLIER entry
        p += _validate_entry(e, i, prior_ids)
        eid = e.get("id") if isinstance(e, dict) else None
        if eid in seen:
            p.append(f"entries[{i}]: duplicate id {eid!r}")
        if eid:
            seen.add(eid)
    refs_ok = set(DOMAINS) | seen
    for i, edge in enumerate(ledger.get("graph", []) or []):
        if not (isinstance(edge, dict) and edge.get("from") and edge.get("to")
                and edge.get("relationship") in RELATIONSHIPS):
            p.append(f"graph[{i}]: needs `from`, `to`, and a `relationship` in {RELATIONSHIPS}")
            continue
        for end in ("from", "to"):
            if edge[end] not in refs_ok:
                p.append(f"graph[{i}].{end} ({edge[end]!r}) must be a domain or an existing entry id")
    return p


def _template():
    return {
        "brand": "<brand>", "created": "<YYYY-MM-DD>",
        "entries": [{
            "id": "color-r1", "domain": "color", "round": 1,
            "axes": ["functional-expressive", "restraint-loudness"],
            "presented": ["A", "B", "C", "D"], "chosen": "B",
            "comment": "yes, but warmer — terracotta not blue",
            "move": {
                "move": "A signature accent on a near-neutral base — one hot color used sparingly as the brand's 'tell'",
                "rationale": "Lets the foundation's 'quiet confidence' read while still owning one ownable color",
                "expected_effect": "Recognition at a glance without shouting; contrast headroom for accessibility",
                "severity": "should",
                "exemplar_evidence": [{"brand": "Stripe", "what": "accent on white", "why_cited": "restrained-expressive at scale"}],
                "confidence": 0.8},
            "contributors": [{"who": "designer", "role": "chooser", "date": "<YYYY-MM-DD>"},
                             {"who": "brand-guidelines", "role": "proposer", "date": "<YYYY-MM-DD>"}],
            "supersedes": None}],
        "graph": [{"from": "color-r1", "to": "expression", "relationship": "constrains"}],
    }


def live_entries(ledger):
    """Entries not superseded — a revision replaces the entry its `supersedes` names; only live choices assemble."""
    entries = [e for e in ledger.get("entries", []) if isinstance(e, dict)]
    superseded = {e.get("supersedes") for e in entries if e.get("supersedes")}
    return [e for e in entries if e.get("id") not in superseded]


def coverage(ledger):
    """Per-domain coverage over the six domains: live-choice count + state (resolved ≥1 / absent)."""
    live = live_entries(ledger)
    return {d: {"choices": sum(1 for e in live if e.get("domain") == d),
                "state": "resolved" if any(e.get("domain") == d for e in live) else "absent"} for d in DOMAINS}


def coherence(ledger, domain=None):
    """The mechanized half of cross-domain coherence: compute the prior commitments + graph edges that should
    inform framing a domain's 2×2 (or the whole picture), and surface `contradicts` edges to resolve. The
    loop READS this before framing options; resolution stays the model's/designer's judgment (it informs,
    it doesn't railroad). Returns {commitments, edges, contradictions}."""
    live = live_entries(ledger)
    by_id = {e.get("id"): e for e in live}
    edges = ledger.get("graph", []) or []

    def touches(ref):
        if not domain or ref == domain:
            return not domain or ref == domain
        e = by_id.get(ref)
        return bool(e and e.get("domain") == domain)

    commitments = [{"domain": e.get("domain"), "id": e.get("id"), "move": e.get("move", {}).get("move", ""),
                    "axes": e.get("axes", []), "chosen": e.get("chosen")}
                   for e in live if not (domain and e.get("domain") == domain)]
    rel_edges = [g for g in edges if (not domain) or touches(g.get("from")) or touches(g.get("to"))]
    contradictions = [g for g in edges if g.get("relationship") == "contradicts"]
    return {"commitments": commitments, "edges": rel_edges, "contradictions": contradictions}


def _convention(out):
    """Detect the corpus convention at `out` so assembly never creates a mixed corpus (the never-mix rule)."""
    flat = folder = False
    if os.path.isdir(out):
        for name in os.listdir(out):
            if re.match(r"^\d\d-[a-z][a-z0-9-]*--.+\.md$", name):
                flat = True
            elif re.match(r"^\d\d-[a-z][a-z0-9-]*$", name) and os.path.isdir(os.path.join(out, name)):
                folder = True
    return "mixed" if (flat and folder) else "flat" if flat else "folder" if folder else "empty"


def _doc_path(out, domain, flat):
    layer = LAYER_OF[domain]
    return os.path.join(out, f"{layer}--{domain}.md") if flat else os.path.join(out, layer, f"{domain}.md")


def _render_domain_doc(domain, entries, sources_ref):
    """Deterministic ledger → corpus doc: provenance frontmatter + each live choice as a typed rule."""
    seen, contribs = set(), []
    for e in entries:
        for c in e.get("contributors", []):
            k = (c.get("who"), c.get("role"))
            if k not in seen:
                seen.add(k)
                contribs.append(c)
    out = ["---", "contributors:"]
    for c in contribs:
        out.append(f'  - {{who: "{c.get("who")}", role: {c.get("role")}, date: {c.get("date")}}}')
    out += [f"sources: [{sources_ref}]", "---", "",
            f"# {domain.capitalize()}", "",
            f"> Assembled by `/brand-elicit` from {len(entries)} choice(s); each rule traces to a ledger entry.", ""]
    for e in entries:
        m = e.get("move", {})
        out.append(f"## {m.get('move', '(move)')}  ({m.get('severity', 'should')})")
        out.append(f"**Why:** {m.get('rationale', '')}  **Effect:** {m.get('expected_effect', '')}")
        for ev in m.get("exemplar_evidence", []) or []:
            out.append(f"Like: {ev.get('brand', '')} — {ev.get('what', '')} ({ev.get('why_cited', '')}).")
        if e.get("comment"):
            out.append(f"_Designer note:_ {e['comment']}")
        out.append(f"_[{' × '.join(e.get('axes', []))} · chose {e.get('chosen')} · round {e.get('round')} · ledger:{e.get('id')}]_")
        out.append("")
    return "\n".join(out) + "\n"


def _is_elicited(path):
    """True if `path` is a doc THIS assembler produced (safe to overwrite idempotently), not hand-authored."""
    try:
        return "Assembled by `/brand-elicit`" in open(path, encoding="utf-8", errors="replace").read(2000)
    except OSError:
        return False


def assemble(ledger, out, ledger_path, flat=False, apply=False, force=False, log=print):
    """Compile the live choice-ledger into per-domain corpus docs (provenance-traced). Dry-run unless apply.
    NON-DESTRUCTIVE: overwrites only a doc this assembler previously wrote (idempotent re-assembly) or under
    `force`; a hand-authored doc at the canonical name is never clobbered — the elicited version is written to
    a flagged `<name>.elicited.md` sibling instead. Returns [(path, rule_count)], or None if the corpus is mixed."""
    conv = _convention(out)
    if conv == "mixed":
        log(f"assemble: '{out}' is a MIXED corpus (both flat and folder layers) — reconcile with corpus-migrate first")
        return None
    flat_mode = flat or conv == "flat"
    rel = os.path.relpath(ledger_path, out)  # so corpus-provenance can resolve `sources:` back to the ledger
    sources_ref = rel if not rel.startswith("..") else f"00-sources/{os.path.basename(ledger_path)}"
    written = []
    for d in DOMAINS:
        es = [e for e in live_entries(ledger) if e.get("domain") == d]
        if not es:
            continue
        canon = _doc_path(out, d, flat_mode)
        if force or not os.path.exists(canon) or _is_elicited(canon):
            target, redirected = canon, False
        else:  # a hand-authored doc holds the canonical name — don't clobber it
            target, redirected = canon[:-3] + ".elicited.md", True
        if apply:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            open(target, "w", encoding="utf-8").write(_render_domain_doc(d, es, sources_ref))
        note = (f"  (canonical {os.path.relpath(canon, out)} is hand-authored — not overwriting; --force to replace)"
                if redirected else "")
        log(f"  {'wrote' if apply else 'would write'} {os.path.relpath(target, out)} ({len(es)} rule(s)){note}")
        written.append((target, len(es)))
    log(f"assemble: {len(written)} domain doc(s) {'written to' if apply else 'planned for'} {out} "
        f"({'flat' if flat_mode else 'folder'} convention){'' if apply else ' — dry run; pass --apply to write'}")
    return written


def project_card(ledger, idea=None):
    """Project the live ledger into a brand-spec card matching `design-skills:brand-decomposer`'s documented
    `*.brand.json` shape — for the optional grading seam. Each chosen design-move becomes a typed `rule`
    (truth `proposed`: the designer chose it; evidence points back at the ledger entry, so it's traced). The
    brand idea comes from `--idea` (the foundation); concrete tokens/contrast are left empty — the elicitation
    captures directional rules, not hex values, and brand-decomposer will honestly flag that incompleteness."""
    rules = []
    for e in live_entries(ledger):
        m = e.get("move", {})
        conf = m.get("confidence", 0.8)
        rules.append({
            "id": e.get("id"),
            "domain": e.get("domain"),
            "statement": m.get("move", ""),
            "severity": m.get("severity", "should"),
            "evidence": [{"deck_id": "guidelines-elicitation", "slide_id": e.get("id"), "confidence": conf}],
            "confidence": conf,
            "truth": "proposed",
        })
    return {
        "brand": ledger.get("brand", "<brand>"),
        "strategy": {
            "brand_idea": idea or "<from 01-foundation — pass --idea to embed the brand idea for axis-A grading>",
            "meaning_chain": ["idea", "voice", "mark", "color", "type", "expression", "apps"],
        },
        "domains": {d: {} for d in DOMAINS},
        "tokens": [],
        "rules": rules,
        "examples": [],
        "surfaces": [],
        "color_pairs": [],
    }


def selftest():
    fails = []

    def expect(c, m):
        if not c:
            fails.append(m)

    good = _template()
    good["brand"], good["created"] = "Acme", "2026-06-20"
    good["entries"][0]["contributors"][0]["date"] = "2026-06-20"
    good["entries"][0]["contributors"][1]["date"] = "2026-06-20"
    expect(validate(good) == [], f"a well-formed ledger failed: {validate(good)}")

    def broken(mut):
        import copy
        g = copy.deepcopy(good)
        mut(g)
        return validate(g)

    expect(broken(lambda g: g["entries"][0].update(domain="branding")), "bad domain not caught")
    expect(broken(lambda g: g["entries"][0].update(chosen="E")), "chosen outside presented not caught")
    expect(broken(lambda g: g["entries"][0].update(axes=["quiet-loud"])), "single-axis 2×2 not caught")
    expect(broken(lambda g: g["entries"][0].update(axes=["nope", "quiet-loud"])), "unknown axis not caught")
    expect(broken(lambda g: g["entries"][0]["move"].pop("rationale")), "missing move.rationale not caught")
    expect(broken(lambda g: g["entries"][0]["move"].update(confidence=1.5)), "out-of-band confidence not caught")
    expect(broken(lambda g: g["entries"][0].update(contributors=[])), "empty contributors not caught")
    expect(broken(lambda g: g["entries"][0].update(supersedes="ghost")), "dangling supersedes not caught")
    expect(broken(lambda g: g["entries"].append(g["entries"][0])), "duplicate id not caught")
    expect(broken(lambda g: g["graph"][0].update(relationship="vibes")), "bad graph relationship not caught")
    # a legitimate supersession (a later entry revises an earlier one) passes
    rev = _template()["entries"][0]
    rev["id"], rev["supersedes"], rev["round"] = "color-r2", "color-r1", 2
    rev["contributors"][0]["date"] = rev["contributors"][1]["date"] = "2026-06-20"
    g2 = json.loads(json.dumps(good))
    g2["entries"].append(rev)
    expect(validate(g2) == [], f"a legitimate supersession failed: {validate(g2)}")
    expect(coverage(good)["color"]["state"] == "resolved" and coverage(good)["voice"]["state"] == "absent",
           "coverage mis-reported the live domains")
    # supersession is honored by live_entries: the revision wins, count stays 1 for color
    expect(len(live_entries(g2)) == 1 and live_entries(g2)[0]["id"] == "color-r2", "supersession not honored in live_entries")
    # assemble: dry-run plans one domain doc; --apply writes a provenance-carrying corpus doc; mixed is refused
    import shutil
    import tempfile
    d = tempfile.mkdtemp(prefix="guidelines-assemble-selftest-")
    try:
        lp = os.path.join(d, "00-sources", "guidelines-elicitation.json")
        os.makedirs(os.path.dirname(lp))
        json.dump(good, open(lp, "w"))
        plan = assemble(good, d, lp, apply=False, log=lambda *_: None)
        expect(plan is not None and len(plan) == 1 and plan[0][1] == 1, "assemble dry-run did not plan exactly the color doc")
        assemble(good, d, lp, apply=True, log=lambda *_: None)
        doc = os.path.join(d, "04-expression", "color.md")
        txt = open(doc).read() if os.path.isfile(doc) else ""
        expect("contributors:" in txt and "sources: [00-sources/guidelines-elicitation.json]" in txt,
               "assembled doc missing provenance frontmatter")
        expect("(should)" in txt and "signature accent" in txt, "assembled doc missing the typed rule")
        # non-destructive: re-assembling overwrites OUR own elicited doc (idempotent), no sibling spawned
        assemble(good, d, lp, apply=True, log=lambda *_: None)
        expect(not os.path.isfile(os.path.join(d, "04-expression", "color.elicited.md")),
               "re-assembling our own elicited doc wrongly spawned an .elicited sibling")
        # a HAND-AUTHORED canonical doc is never clobbered — the elicited version goes to a flagged sibling
        open(doc, "w", encoding="utf-8").write("# Color\nhand-authored, do not clobber\n")
        assemble(good, d, lp, apply=True, log=lambda *_: None)
        expect("hand-authored" in open(doc).read(), "assemble clobbered a hand-authored doc")
        expect(os.path.isfile(os.path.join(d, "04-expression", "color.elicited.md")),
               "assemble did not write the .elicited sibling beside a hand-authored doc")
        # --force overwrites the hand-authored canonical
        assemble(good, d, lp, apply=True, force=True, log=lambda *_: None)
        expect("Assembled by" in open(doc).read(), "assemble --force did not overwrite the canonical doc")
        open(os.path.join(d, "01-foundation--x.md"), "w").write("x")  # now flat + folder both present
        expect(assemble(good, d, lp, apply=False, log=lambda *_: None) is None, "a mixed corpus was not refused")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # card projection: a brand-spec card for the optional brand-decomposer grading seam
    card = project_card(good, idea="Quiet confidence, made ownable.")
    expect(card["brand"] == "Acme" and card["strategy"]["brand_idea"] == "Quiet confidence, made ownable.",
           "card projection lost brand/idea")
    expect(set(card["domains"]) == set(DOMAINS), "card domains != the six")
    expect(bool(card["rules"]) and all(r["domain"] in DOMAINS and r["severity"] in SEVERITIES and r["evidence"]
                                       and r["truth"] == "proposed" for r in card["rules"]),
           "card rules malformed (domain/severity/evidence/truth)")
    expect(card["rules"][0]["id"] == "color-r1" and "signature accent" in card["rules"][0]["statement"],
           "card rule did not project from the ledger entry")
    # coherence: prior commitments + edges relevant to a domain; contradictions surfaced; dangling refs caught
    coh = coherence(good, "expression")
    expect(any(c["domain"] == "color" for c in coh["commitments"]), "coherence missed the color commitment for expression")
    expect(any(g["from"] == "color-r1" and g["to"] == "expression" for g in coh["edges"]), "coherence missed the constrains edge")
    gc = json.loads(json.dumps(good))
    gc["graph"].append({"from": "color-r1", "to": "voice", "relationship": "contradicts"})
    expect(validate(gc) == [], f"a valid contradicts edge was rejected: {validate(gc)}")
    expect(len(coherence(gc)["contradictions"]) == 1, "coherence did not surface the contradicts edge")
    gd = json.loads(json.dumps(good))
    gd["graph"].append({"from": "ghost-id", "to": "color", "relationship": "supports"})
    expect(any("a domain or an existing entry id" in x for x in validate(gd)), "a dangling graph ref was not caught")

    if fails:
        sys.stderr.write("guidelines-ledger selftest: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("guidelines-ledger selftest: OK (validate: a well-formed ledger + a legitimate supersession pass, "
          "bad domain/quadrant/axes/move/confidence/severity/contributors/supersedes/duplicate-id/graph-edge "
          "each caught; coverage + supersession honored; assemble dry-run + --apply write a provenance-carrying "
          "domain doc and refuse a mixed corpus; card projects a brand-spec card for the brand-decomposer seam; "
          "coherence surfaces commitments + edges + contradictions, dangling graph refs caught)")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.stderr.write(__doc__ or "")
        return 0
    cmd = argv[0]

    def _ledger():
        """The ledger path: the first positional, or the default `./brand-corpus/00-sources/…` ('no folder given')."""
        return argv[1] if len(argv) > 1 and not argv[1].startswith("-") else DEFAULT_LEDGER

    if cmd == "selftest":
        return selftest()
    if cmd == "template":
        print(json.dumps(_template(), indent=2))
        return 0
    if cmd == "schema":
        print(json.dumps({"domains": DOMAINS, "axes": AXES, "quadrants": QUADRANTS,
                          "relationships": RELATIONSHIPS, "move_required": MOVE_REQUIRED}, indent=2))
        return 0
    if cmd == "validate":
        path = _ledger()
        try:
            ledger = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.stderr.write(f"guidelines-ledger: cannot read {path}: {e}\n")
            return 2
        probs = validate(ledger)
        for x in probs:
            sys.stderr.write(f"  - {x}\n")
        print(f"RESULT: {'PASS' if not probs else 'FAIL'} ({len(probs)} problem(s), "
              f"{len(ledger.get('entries', []))} entr(y/ies))")
        return 1 if probs else 0
    if cmd in ("coverage", "assemble"):
        path = _ledger()
        try:
            ledger = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.stderr.write(f"guidelines-ledger: cannot read {path}: {e}\n")
            return 2
        probs = validate(ledger)
        if probs:
            sys.stderr.write(f"guidelines-ledger {cmd}: ledger is invalid — run `validate` first ({len(probs)} problem(s))\n")
            return 1
        if cmd == "coverage":
            cov = coverage(ledger)
            for dom in DOMAINS:
                print(f"  {dom:12} {cov[dom]['state']:9} ({cov[dom]['choices']} choice(s))")
            resolved = [dom for dom in DOMAINS if cov[dom]["state"] == "resolved"]
            frontier = [dom for dom in DOMAINS if cov[dom]["state"] == "absent"]
            print(f"RESULT: {len(resolved)}/{len(DOMAINS)} domains resolved; "
                  f"frontier: {', '.join(frontier) or '(none — all covered)'}")
            return 0
        out = (argv[argv.index("--out") + 1] if "--out" in argv and argv.index("--out") + 1 < len(argv) else DEFAULT_CORPUS)
        res = assemble(ledger, out, path, flat="--flat" in argv, apply="--apply" in argv, force="--force" in argv)
        return 1 if res is None else 0
    if cmd == "card":
        path = _ledger()
        try:
            ledger = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.stderr.write(f"guidelines-ledger: cannot read {path}: {e}\n")
            return 2
        probs = validate(ledger)
        if probs:
            sys.stderr.write(f"guidelines-ledger card: ledger is invalid — run `validate` first ({len(probs)} problem(s))\n")
            return 1
        idea = (argv[argv.index("--idea") + 1] if "--idea" in argv and argv.index("--idea") + 1 < len(argv) else None)
        card = project_card(ledger, idea)
        text = json.dumps(card, indent=2)
        out = (argv[argv.index("-o") + 1] if "-o" in argv and argv.index("-o") + 1 < len(argv) else None)
        if out:
            open(out, "w", encoding="utf-8").write(text + "\n")
            sys.stderr.write(f"guidelines-ledger card → {out} ({len(card['rules'])} rule(s)). Grade it in "
                             f"design-skills:brand-decomposer:  python3 bin/brand-spec-check.py lint {out}\n")
        else:
            print(text)
        return 0
    if cmd == "coherence":
        path = _ledger()
        try:
            ledger = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.stderr.write(f"guidelines-ledger: cannot read {path}: {e}\n")
            return 2
        probs = validate(ledger)
        if probs:
            sys.stderr.write(f"guidelines-ledger coherence: ledger is invalid — run `validate` first ({len(probs)} problem(s))\n")
            return 1
        dom = (argv[argv.index("--domain") + 1] if "--domain" in argv and argv.index("--domain") + 1 < len(argv) else None)
        if dom and dom not in DOMAINS:
            sys.stderr.write(f"guidelines-ledger coherence: --domain must be one of {DOMAINS}\n")
            return 2
        coh = coherence(ledger, dom)
        print(f"Coherence for `{dom}` — frame the 2×2 to cohere with:" if dom else "Coherence (the whole picture):")
        print("  prior commitments:")
        for c in coh["commitments"]:
            print(f"    [{c['domain']}] {c['move']}  ({' × '.join(c['axes'])} · {c['chosen']})")
        if not coh["commitments"]:
            print("    (none yet)")
        print("  edges:")
        for g in coh["edges"]:
            print(f"    {g['from']} --{g['relationship']}--> {g['to']}")
        if not coh["edges"]:
            print("    (none)")
        if coh["contradictions"]:
            print("  ⚠ contradictions (resolve, don't bake):")
            for g in coh["contradictions"]:
                print(f"    {g['from']} --contradicts--> {g['to']}")
        n = len(coh["contradictions"])
        print(f"RESULT: {len(coh['commitments'])} commitment(s), {len(coh['edges'])} edge(s), {n} contradiction(s)")
        return 1 if ("--strict" in argv and n) else 0
    sys.stderr.write(f"guidelines-ledger: unknown command {cmd!r}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
