#!/usr/bin/env python3
"""two-plane.py — the deterministic core of the two-plane orchestrator. Self-contained (stdlib only).

The orchestrator reasons on two planes in isolated contexts (see
../../docs/designs/two-plane-orchestrator.md): the OUTSIDE-IN **Charter** (graded by goals-decomposer)
and the INSIDE-OUT **Blueprint** (graded by architecture-decomposer). This tool mechanizes the three
parts of that pipeline that are arithmetic, not judgment — so the agents do only what agents are for:

  extract <charter.json>                  the POLLUTION GUARANTEE: emit the distilled constraints
                                          extract (ranked characteristics + principles + non-goals) the
                                          Blueprint agent receives — NOT the charter's prose/diagnosis,
                                          so the goals' narrative can't anchor the structural reasoning.
  crosscheck <charter.json> <bp.json>     the SEAM GATE: every ranked characteristic is served by a
                                          Blueprint mechanism; flags UNSERVED_GOAL / DANGLING_SERVES /
                                          UNHONORED_PRINCIPLE / STALE.
  staleness <charter.json> <bp.json>      section-level: which Blueprint mechanisms are stale because the
                                          characteristic they serve changed since derivation.
  hash <charter.json>                     the charter hash + per-characteristic hashes (record these in a
                                          Blueprint's charter_ref so staleness is detectable).
  lattice <lattice.json> <ch> <bp> [--update]   the MAINTAINER: propagate charter drift across the cell
                                          graph — stale every cell deriving from the charter (never the
                                          charter cell or the append-only ledger); --update writes it back.
  record <ledger.jsonl> <event-json>      append one event to the append-only ledger (orchestrator-supplied).
  selftest                                green (covered) / red (gap+stale) fixtures.

A *.charter.json (the binding subset; ids derived from name/text when absent):
  {"title","diagnosis",
   "characteristics":[{"id","name","rank","metric","threshold","window"}],
   "principles":[{"id","text"} | "text"], "non_goals":[...], "acceptance":[...]}
A *.blueprint.json:
  {"title","charter_ref":{"hash","chars":{<char-id>:<hash>}},
   "mechanisms":[{"id","name","serves":[<char-id>...],"section"}],
   "honors_principles":[<principle-id>...]}
Python 3.8+.
"""
import hashlib
import json
import re
import sys


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "x"


def _canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _h(o):
    return hashlib.sha256(_canon(o).encode("utf-8")).hexdigest()[:16]


def _char_id(c):
    return c.get("id") or ("char." + _slug(c.get("name", "?")))


def _prin_id(p):
    if isinstance(p, dict):
        return p.get("id") or ("prin." + _slug(p.get("text", "?")))
    return "prin." + _slug(p)


def _char_hash(c):
    """The content that, if changed, stales a mechanism serving this characteristic — its measurable
    substance (not its prose rationale)."""
    return _h({k: c.get(k) for k in ("name", "rank", "metric", "threshold", "window")})


def extract(charter):
    """The distilled constraints extract — what BINDS the structure, nothing that anchors it. The
    Blueprint agent sees only this, never the charter's diagnosis/acceptance prose."""
    if not isinstance(charter, dict):
        raise ValueError("charter must be a JSON object")
    chars = [c for c in (charter.get("characteristics") or []) if isinstance(c, dict)]
    return {
        "_note": "constraints extract — the binding subset of the charter; the Blueprint agent's ONLY view of it",
        "characteristics": [
            {"id": _char_id(c), "name": c.get("name"), "rank": c.get("rank"),
             "metric": c.get("metric"), "threshold": c.get("threshold"), "window": c.get("window")}
            for c in sorted(chars, key=lambda c: c.get("rank", 1e9))
        ],
        "principles": [{"id": _prin_id(p), "text": p.get("text") if isinstance(p, dict) else p}
                       for p in (charter.get("principles") or [])],
        "non_goals": list(charter.get("non_goals") or []),
    }


def charter_hashes(charter):
    chars = [c for c in (charter.get("characteristics") or []) if isinstance(c, dict)]
    per = {_char_id(c): _char_hash(c) for c in chars}
    return {"hash": _h(extract(charter)), "chars": per}


def crosscheck(charter, blueprint):
    """Return (fails, warns) for the seam between a charter and a blueprint."""
    fails, warns = [], []

    def F(k, m):
        fails.append((k, m))

    def W(k, m):
        warns.append((k, m))

    if not isinstance(charter, dict) or not isinstance(blueprint, dict):
        F("WELL_FORMED", "charter and blueprint must both be JSON objects")
        return fails, warns

    chars = [c for c in (charter.get("characteristics") or []) if isinstance(c, dict)]
    char_ids = {_char_id(c): c for c in chars}
    mechs = [m for m in (blueprint.get("mechanisms") or []) if isinstance(m, dict)]
    served = set()
    for m in mechs:
        for sid in m.get("serves") or []:
            served.add(sid)
            if sid not in char_ids:
                W("DANGLING_SERVES", "mechanism '%s' serves '%s', which is not a charter characteristic"
                  % (m.get("id") or m.get("name", "?"), sid))

    # COVERAGE: every ranked characteristic must have a structural mechanism; a high-rank gap is critical
    for cid, c in char_ids.items():
        if cid not in served:
            rank = c.get("rank")
            sev = F if (isinstance(rank, int) and rank <= 2) else W
            sev("UNSERVED_GOAL", "UNSERVED_GOAL — characteristic '%s' (rank %s) has no Blueprint "
                "mechanism serving it; the architecture doesn't address a goal it's held to"
                % (c.get("name", cid), rank))

    # PRINCIPLES: each charter principle should be acknowledged (the council judges *actual* adherence)
    honored = set(blueprint.get("honors_principles") or [])
    for p in charter.get("principles") or []:
        pid = _prin_id(p)
        if pid not in honored:
            W("UNHONORED_PRINCIPLE", "UNHONORED_PRINCIPLE — principle '%s' is not in the Blueprint's "
              "honors_principles (does the structure respect it?)"
              % (p.get("text") if isinstance(p, dict) else p))

    # STALENESS: the blueprint was derived against a charter hash; if it drifted, the blueprint is stale
    ref = (blueprint.get("charter_ref") or {}).get("hash")
    cur = charter_hashes(charter)["hash"]
    if ref and ref != cur:
        F("STALE", "STALE — Blueprint was derived against charter hash %s but the charter is now %s; "
          "regenerate before trusting the cross-check" % (ref, cur))
    elif not ref:
        W("NO_CHARTER_REF", "Blueprint has no charter_ref.hash — staleness can't be detected; record "
          "`two-plane.py hash` output at derivation")
    return fails, warns


def staleness(charter, blueprint):
    """Section-level: which mechanisms are stale because the characteristic they serve changed."""
    cur = charter_hashes(charter)["chars"]
    ref = (blueprint.get("charter_ref") or {}).get("chars") or {}
    stale = []
    for m in blueprint.get("mechanisms") or []:
        if not isinstance(m, dict):
            continue
        for sid in m.get("serves") or []:
            if sid in cur and sid in ref and cur[sid] != ref[sid]:
                stale.append((m.get("id") or m.get("name", "?"), sid))
    return stale


# --- the maintainer: lattice staleness propagation + the append-only ledger --------------------
def _cell_name(c):
    return "%s.%s.%s" % (c.get("layer"), c.get("scope"), c.get("slug"))


def _dependents(lattice, root):
    """Every cell that transitively depends_on `root`."""
    deps = {_cell_name(c): set(c.get("depends_on") or []) for c in lattice.get("cells", [])}
    out, frontier = set(), [root]
    while frontier:
        x = frontier.pop()
        for n, d in deps.items():
            if x in d and n not in out:
                out.add(n)
                frontier.append(n)
    return out


def lattice_state(lattice, charter, blueprint):
    """The deterministic maintainer: a charter drift stales every cell that derives from the charter
    (the blueprint, the cross-check, transitively) — never the charter cell itself, never the ledger
    (append-only). Returns one row per cell with the recommended maturity."""
    cur = charter_hashes(charter)["hash"]
    ref = (blueprint.get("charter_ref") or {}).get("hash")
    drifted = bool(ref) and ref != cur
    downstream = _dependents(lattice, "spec.workflow.charter") if drifted else set()
    rows = []
    for c in lattice.get("cells", []):
        name = _cell_name(c)
        rec, reason = c.get("maturity"), ""
        if name in downstream and c.get("layer") != "ledger":
            rec, reason = "stale", "charter drifted (%s → %s); %s derives from it" % (ref, cur, name)
        rows.append({"cell": name, "current": c.get("maturity"), "recommended": rec, "reason": reason})
    return rows


def record(ledger_path, event):
    """Append one event to the append-only ledger (JSONL). The orchestrator supplies the event (incl.
    its own timestamp) — the bin never mutates a prior line."""
    if not isinstance(event, dict):
        raise ValueError("a ledger event must be a JSON object")
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(_canon(event) + "\n")
    return event


# --- fixtures ----------------------------------------------------------------------------------
_CHARTER = {
    "title": "Checkout", "diagnosis": "abandonment tracks p99 under load; one failure collapses the flow",
    "characteristics": [
        {"name": "scalability", "rank": 1, "metric": "p99", "threshold": "<300ms", "window": "10x"},
        {"name": "resilience", "rank": 2, "metric": "success rate", "threshold": ">95%", "window": "outage"},
        {"name": "evolvability", "rank": 3, "metric": "modules touched", "threshold": "<=1", "window": "per change"},
    ],
    "principles": [{"id": "prin.no-sync", "text": "no synchronous calls on the hot path"}],
    "non_goals": ["not multi-region in v1"],
}
_BP_GREEN = {
    "title": "Checkout arch", "charter_ref": charter_hashes(_CHARTER),
    "mechanisms": [
        {"id": "mech.asg", "name": "auto-scaling group + read replicas", "serves": ["char.scalability"], "section": "compute"},
        {"id": "mech.bulkhead", "name": "circuit breaker + queue fallback", "serves": ["char.resilience"], "section": "resilience"},
        {"id": "mech.pricing-module", "name": "pricing as an isolated module", "serves": ["char.evolvability"], "section": "modules"},
    ],
    "honors_principles": ["prin.no-sync"],
}
# RED — leaves rank-1 scalability unserved, a dangling serve, an unhonored principle, and a stale hash.
_BP_RED = {
    "title": "Checkout arch (draft)", "charter_ref": {"hash": "deadbeefdeadbeef", "chars": {}},
    "mechanisms": [
        {"id": "mech.bulkhead", "name": "circuit breaker", "serves": ["char.resilience"], "section": "resilience"},
        {"id": "mech.ghost", "name": "a thing", "serves": ["char.nonexistent"], "section": "x"},
    ],
    "honors_principles": [],
}


_LATTICE = {"cells": [
    {"layer": "spec", "scope": "workflow", "slug": "charter", "maturity": "validated", "depends_on": []},
    {"layer": "capability", "scope": "workflow", "slug": "blueprint", "maturity": "validated",
     "depends_on": ["spec.workflow.charter"]},
    {"layer": "rubric", "scope": "workflow", "slug": "cross-check", "maturity": "validated",
     "depends_on": ["capability.workflow.blueprint"]},
    {"layer": "ledger", "scope": "workflow", "slug": "events", "maturity": "operating",
     "depends_on": ["spec.workflow.charter"]},
]}


def selftest():
    errs = []
    gf, gw = crosscheck(_CHARTER, _BP_GREEN)
    if gf:
        errs.append("GREEN blueprint produced FAILs: %s" % gf)
    rf, rw = crosscheck(_CHARTER, _BP_RED)
    rk = {k for k, _ in rf}
    rwk = {k for k, _ in rw}
    if "UNSERVED_GOAL" not in rk:
        errs.append("RED: rank-1 unserved goal not a FAIL (fails=%s)" % sorted(rk))
    if "STALE" not in rk:
        errs.append("RED: stale charter_ref not caught")
    if "DANGLING_SERVES" not in rwk:
        errs.append("RED: dangling serves not warned")
    if "UNHONORED_PRINCIPLE" not in rwk:
        errs.append("RED: unhonored principle not warned")
    # the extract must NOT leak the diagnosis/acceptance (the pollution guarantee)
    ex = extract(_CHARTER)
    if "diagnosis" in ex or "acceptance" in ex or "title" in ex:
        errs.append("extract leaked anchoring prose (diagnosis/acceptance/title): %s" % list(ex))
    if [c["name"] for c in ex["characteristics"]] != ["scalability", "resilience", "evolvability"]:
        errs.append("extract didn't rank-order the characteristics")
    # section-level staleness: change scalability's threshold → only its mechanism is stale
    moved = json.loads(json.dumps(_CHARTER))
    moved["characteristics"][0]["threshold"] = "<200ms"
    st = staleness(moved, _BP_GREEN)
    if not any(sid == "char.scalability" for _m, sid in st):
        errs.append("section-level staleness missed the changed scalability mechanism (%s)" % st)
    if any(sid == "char.resilience" for _m, sid in st):
        errs.append("section-level staleness over-flagged an unchanged characteristic")
    # maintainer: a fresh blueprint (charter_ref matches) stales nothing
    fresh = {r["cell"]: r["recommended"] for r in lattice_state(_LATTICE, _CHARTER, _BP_GREEN)}
    if any(v == "stale" for v in fresh.values()):
        errs.append("lattice: fresh blueprint wrongly staled a cell: %s" % fresh)
    # a drifted charter stales the blueprint + cross-check, but NOT the charter cell or the ledger
    ds = {r["cell"]: r["recommended"] for r in lattice_state(_LATTICE, moved, _BP_GREEN)}
    if ds.get("capability.workflow.blueprint") != "stale" or ds.get("rubric.workflow.cross-check") != "stale":
        errs.append("lattice: drifted charter didn't stale the downstream cells: %s" % ds)
    if ds.get("spec.workflow.charter") == "stale" or ds.get("ledger.workflow.events") == "stale":
        errs.append("lattice: wrongly staled the charter cell or the append-only ledger")
    # malformed inputs must not raise
    for bad in ([], None, "x"):
        try:
            crosscheck(bad, _BP_GREEN)
            extract(_CHARTER)
        except ValueError:
            pass
        except Exception as exc:  # noqa: BLE001
            errs.append("crash on %r (%s)" % (bad, exc))
    return errs


def _report(fails, warns, as_json):
    if as_json:
        find = [{"kind": k, "severity": "fail", "message": m} for k, m in fails]
        find += [{"kind": k, "severity": "advisory", "message": m} for k, m in warns]
        print(json.dumps({"tool": "two-plane", "ok": not fails,
                          "summary": "%d fail, %d advisory" % (len(fails), len(warns)),
                          "findings": find}, indent=2))
        return 1 if fails else 0
    for _k, w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("two-plane: cross-check FAIL (%d)\n" % len(fails))
        for _k, f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("two-plane: OK — every ranked characteristic is served, principles acknowledged, not stale")
    return 0


def _load(p):
    return json.load(open(p, encoding="utf-8"))


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("two-plane: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("two-plane: OK — green covered, red caught (gap/stale/dangling); extract isolates; "
              "section-level staleness verified")
        return 0
    try:
        if argv[0] == "extract":
            print(json.dumps(extract(_load(argv[1])), indent=2, ensure_ascii=False))
            return 0
        if argv[0] == "hash":
            print(json.dumps(charter_hashes(_load(argv[1])), indent=2))
            return 0
        if argv[0] == "crosscheck":
            f, w = crosscheck(_load(argv[1]), _load(argv[2]))
            return _report(f, w, as_json)
        if argv[0] == "staleness":
            st = staleness(_load(argv[1]), _load(argv[2]))
            print(json.dumps([{"mechanism": m, "stale_for": sid} for m, sid in st], indent=2))
            return 0 if not st else 1
        if argv[0] == "lattice":
            rows = lattice_state(_load(argv[1]), _load(argv[2]), _load(argv[3]))
            print(json.dumps(rows, indent=2))
            drift = [r for r in rows if r["recommended"] != r["current"]]
            if drift and "--update" in sys.argv:
                latt = _load(argv[1])
                rec = {r["cell"]: r["recommended"] for r in rows}
                for c in latt.get("cells", []):
                    c["maturity"] = rec.get(_cell_name(c), c.get("maturity"))
                json.dump(latt, open(argv[1], "w", encoding="utf-8"), indent=2)
                sys.stderr.write("two-plane: updated %d cell(s) in %s\n" % (len(drift), argv[1]))
            return 1 if drift else 0
        if argv[0] == "record":
            ev = json.loads(argv[2]) if argv[2].lstrip().startswith("{") else _load(argv[2])
            record(argv[1], ev)
            sys.stderr.write("two-plane: appended 1 event to %s\n" % argv[1])
            return 0
    except (OSError, IndexError, json.JSONDecodeError, ValueError) as e:
        sys.stderr.write("two-plane: %s\n" % e)
        return 2
    sys.stderr.write("usage: two-plane.py extract|hash <charter> | crosscheck|staleness <charter> "
                     "<blueprint> | selftest [--json]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
