#!/usr/bin/env python3
"""coverage_check.py — cross-plane coverage gate for a two-plane decomposition.

Routes the deterministic half of decompose to code: given a manifest of
OUTSIDE-IN nodes, INSIDE-OUT actions, and the hosts mapping that crosses them, it
reports the defect quadrant mechanically instead of by eyeballing.

Scope (what this does NOT check): it verifies the two PLANES cross-check — every
action has a node, every leaf has an action (node <-> action). It does NOT verify
real-world completeness. A need that was never written as an action (e.g. a ratified
ADR Decision nobody turned into a node/action) has nothing to leave UNHOSTED, so the
manifest passes clean while the need ships nothing. Catch that upstream with the
ADR-Decision -> action completeness review (references/best-practices.md), a judgement
step, not this gate.

Gates (verdict [gate], exit 1):
  UNHOSTED        an action mapped to no node — a need with nowhere to live
  DANGLING        a hosts entry referencing an unknown action or node
  DUP-ID          a node id or action id used twice
  EDGE-DANGLING   an edges entry referencing an unknown node
  EDGE-CYCLE      the dependency edges form a cycle — no valid build order
  NO-ACCEPT       (plan manifests only) a leaf with no `accept` predicate —
                  a plan unit without a checkable criterion is a wish
Advisories (verdict [advisory], exit 1 only under --strict):
  UNJUSTIFIED-LEAF a leaf node hosting no action and carrying no `justify`
  EDGE-UNJUSTIFIED an edge with no `why` — an edge is a serialization cost; justify it

Usage:
    python coverage_check.py <manifest.json> [--strict]
    python coverage_check.py selftest
Exit 0 = coverage clean.  Exit 1 = at least one gate (or advisory under --strict).
`selftest` proves every code above bites (one mutated fixture per code) and that the
suppressors (justify / why / accept) actually suppress (the negative control).
"""
import json
import sys
from pathlib import Path


def run_checks(m):
    """The one checking engine (the CLI and the selftest both drive THIS).

    Takes a parsed manifest dict; returns (stats, failures, warnings) where
    failures/warnings are lists of (CODE, detail) tuples."""
    nodes = {n["id"]: n for n in m.get("nodes", [])}
    actions = {a["id"]: a for a in m.get("actions", [])}
    hosts = m.get("hosts", [])
    edges = m.get("edges", [])
    plan = bool(m.get("plan"))

    failures, warnings = [], []

    # DUP-ID — ids must be unique within their plane
    if len(nodes) != len(m.get("nodes", [])):
        failures.append(("DUP-ID", "duplicate node id"))
    if len(actions) != len(m.get("actions", [])):
        failures.append(("DUP-ID", "duplicate action id"))

    # DANGLING — every hosts edge must reference real ids
    hosted_actions, hosted_nodes = set(), set()
    for h in hosts:
        a, n = h.get("action"), h.get("node")
        if a not in actions:
            failures.append(("DANGLING", f"hosts.action '{a}' is not a declared action"))
        else:
            hosted_actions.add(a)
        if n not in nodes:
            failures.append(("DANGLING", f"hosts.node '{n}' is not a declared node"))
        else:
            hosted_nodes.add(n)

    # UNHOSTED — every action needs a surface
    for aid, a in actions.items():
        if aid not in hosted_actions:
            failures.append(("UNHOSTED", f"action '{a.get('label', aid)}' ({aid}) maps to no node"))

    # UNJUSTIFIED-LEAF — a leaf that hosts nothing and declares no reason to exist
    for nid, n in nodes.items():
        if n.get("leaf") and nid not in hosted_nodes and not n.get("justify"):
            warnings.append(("UNJUSTIFIED-LEAF", f"leaf '{n.get('label', nid)}' ({nid}) hosts no action and has no justify"))

    # EDGE-DANGLING / EDGE-UNJUSTIFIED — edges reference real nodes and earn their place
    adj = {}
    for e in edges:
        f, t = e.get("from"), e.get("to")
        for end, val in (("from", f), ("to", t)):
            if val not in nodes:
                failures.append(("EDGE-DANGLING", f"edges.{end} '{val}' is not a declared node"))
        if f in nodes and t in nodes:
            adj.setdefault(f, set()).add(t)
        if not (e.get("why") or "").strip():
            warnings.append(("EDGE-UNJUSTIFIED", f"edge {f}->{t} carries no `why`"))

    # EDGE-CYCLE — the constraints must admit a build order
    color = {}
    def visit(u):
        color[u] = 1
        for v in adj.get(u, ()):
            c = color.get(v, 0)
            if c == 1 or (c == 0 and visit(v)):
                return True
        color[u] = 2
        return False

    for u in list(adj):
        if color.get(u, 0) == 0 and visit(u):
            failures.append(("EDGE-CYCLE", "dependency edges form a cycle — no valid build order"))
            break

    # NO-ACCEPT — a plan manifest's leaves each carry a checkable acceptance predicate
    if plan:
        for nid, n in nodes.items():
            if n.get("leaf") and not (n.get("accept") or "").strip():
                failures.append(("NO-ACCEPT", f"leaf '{n.get('label', nid)}' ({nid}) has no `accept` predicate"))

    stats = {"nodes": len(nodes), "actions": len(actions), "hosts": len(hosts),
             "edges": len(edges), "plan": plan}
    return stats, failures, warnings


# --- selftest fixtures -----------------------------------------------------------
# One PASSING base, one mutation per emitted code, one negative control proving the
# suppressors (justify / why / accept) suppress. Every fixture is driven through the
# SAME run_checks() the CLI uses.

def _base():
    """A clean two-plane manifest: every action hosted, every leaf load-bearing or
    justified, one justified edge."""
    return {
        "domain": "selftest",
        "nodes": [
            {"id": "n1", "label": "submit bar", "leaf": True},
            {"id": "n2", "label": "schema", "leaf": True},
            {"id": "n3", "label": "spacer", "leaf": True, "justify": "spacing"},
        ],
        "actions": [
            {"id": "a1", "label": "submit the form"},
            {"id": "a2", "label": "pin the schema"},
        ],
        "hosts": [
            {"action": "a1", "node": "n1"},
            {"action": "a2", "node": "n2"},
        ],
        "edges": [
            {"from": "n2", "to": "n1", "why": "n1 renders the schema n2 pins"},
        ],
    }


def selftest():
    failed = []

    def expect(name, manifest, want_fail_codes, want_warn_codes):
        _, failures, warnings = run_checks(manifest)
        got_f = sorted({c for c, _ in failures})
        got_w = sorted({c for c, _ in warnings})
        if got_f != sorted(want_fail_codes) or got_w != sorted(want_warn_codes):
            failed.append(f"{name}: gates {got_f} (want {sorted(want_fail_codes)}) · "
                          f"advisories {got_w} (want {sorted(want_warn_codes)})")

    # 1) the passing base — zero findings on both tiers
    expect("pass-base", _base(), [], [])

    # 2) UNHOSTED — drop a1's hosts row (its former host n1, now an action-free
    #    plain leaf, correctly goes advisory in the same run)
    m = _base(); m["hosts"] = [h for h in m["hosts"] if h["action"] != "a1"]
    expect("unhosted", m, ["UNHOSTED"], ["UNJUSTIFIED-LEAF"])

    # 3) DANGLING — host references a ghost action AND a ghost node.
    #    The ghost action also leaves nothing extra unhosted; the ghost row's node
    #    slot no longer marks n1 hosted, so n1 (a plain leaf) goes advisory too.
    m = _base(); m["hosts"][0] = {"action": "ghost", "node": "nowhere"}
    expect("dangling", m, ["DANGLING", "UNHOSTED"], ["UNJUSTIFIED-LEAF"])

    # 4) DUP-ID — the same node id twice
    m = _base(); m["nodes"].append({"id": "n1", "label": "submit bar again", "leaf": True})
    expect("dup-id", m, ["DUP-ID"], [])

    # 5) EDGE-DANGLING — an edge to an undeclared node
    m = _base(); m["edges"].append({"from": "n1", "to": "ghost", "why": "points at nothing"})
    expect("edge-dangling", m, ["EDGE-DANGLING"], [])

    # 6) EDGE-CYCLE — n1 -> n2 -> n1
    m = _base(); m["edges"].append({"from": "n1", "to": "n2", "why": "the return edge"})
    expect("edge-cycle", m, ["EDGE-CYCLE"], [])

    # 7) NO-ACCEPT — plan manifest, leaves carry no accept
    m = _base(); m["plan"] = True
    expect("no-accept", m, ["NO-ACCEPT"], [])

    # 8) UNJUSTIFIED-LEAF (advisory tier) — strip the spacer's justify
    m = _base(); del m["nodes"][2]["justify"]
    expect("unjustified-leaf", m, [], ["UNJUSTIFIED-LEAF"])

    # 9) EDGE-UNJUSTIFIED (advisory tier) — strip the edge's why
    m = _base(); del m["edges"][0]["why"]
    expect("edge-unjustified", m, [], ["EDGE-UNJUSTIFIED"])

    # 10) negative control — the suppressors must SUPPRESS: a justified action-free
    #     leaf, a why-carrying edge, and accept-carrying plan leaves produce ZERO
    #     findings (valid inputs are not flagged, even at the advisory tier).
    m = _base(); m["plan"] = True
    for n in m["nodes"]:
        if n.get("leaf"):
            n["accept"] = "checkable predicate exits 0"
    expect("negative-control", m, [], [])

    # tier semantics — gates exit 1 always; advisories exit 1 only under --strict
    _, f, w = run_checks(_base())
    if _exit_code(f, w, strict=False) != 0 or _exit_code(f, w, strict=True) != 0:
        failed.append("tier: clean base must exit 0 with and without --strict")
    m = _base(); del m["edges"][0]["why"]
    _, f, w = run_checks(m)
    if _exit_code(f, w, strict=False) != 0 or _exit_code(f, w, strict=True) != 1:
        failed.append("tier: advisory must exit 0 plain, 1 under --strict")
    m = _base(); m["hosts"] = []
    _, f, w = run_checks(m)
    if _exit_code(f, w, strict=False) != 1:
        failed.append("tier: a gate must exit 1")

    for line in failed:
        print(f"[gate] SELFTEST — {line}")
    print("selftest:", "PASS" if not failed else f"FAIL ({len(failed)})")
    return 0 if not failed else 1


def _exit_code(failures, warnings, strict):
    return 1 if failures or (strict and warnings) else 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    strict = "--strict" in argv
    if args == ["selftest"]:
        return selftest()
    if len(args) != 1:
        print("usage: coverage_check.py <manifest.json> [--strict]  |  coverage_check.py selftest")
        return 2
    try:
        m = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[ERROR] cannot read manifest: {e}")
        return 2

    stats, failures, warnings = run_checks(m)

    print(f"== coverage: {stats['nodes']} nodes · {stats['actions']} actions · {stats['hosts']} hosts · {stats['edges']} edges{' · plan' if stats['plan'] else ''} ==")
    for code, detail in failures:
        print(f"[gate] {code} — {detail}")
    for code, detail in warnings:
        print(f"[advisory] {code} — {detail}")
    if not failures and not warnings:
        print("[OK] coverage clean — both planes cross-check")

    return _exit_code(failures, warnings, strict)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
