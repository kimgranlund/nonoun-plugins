#!/usr/bin/env python3
"""api.py — the server's operations layer: the single-writer, gate-checked, ledgered write path.

This is the logic behind the REST surface (§9.3) — kept stdlib + testable so the whole coordination
path is CI-verifiable without FastAPI. app.py is a thin transport that calls straight into these
functions; the heartbeat (§8) calls `transition_ticket` exactly as a human drag does. Every mutation
here is server-mediated: it goes through the kernel's gates (gate-ticket-ready / gate-dispatch /
gate-signal via lifecycle.py), appends the ledger, writes the file-of-record, and re-materializes the
index — in that order (the DB is never ahead of the ledger). A UI drag is a transition *request*; an
illegal one is refused with a reason, never silently applied.

Stdlib only; Python 3.8+.
"""
import datetime
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import store as _store  # noqa: E402
sys.path.insert(0, _store._KERNEL_BIN)
import lattice as _lat       # noqa: E402
import lifecycle as _lc      # noqa: E402
import ledger as _led        # noqa: E402
import autonomy as _auto     # noqa: E402


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_lattice(d):
    """The vendored scaffold lays the layer dirs but not lattice.json; the server initializes an empty
    canonical lattice on first write so load/rebuild never hit a missing file. dev-factory stamps its OWN
    producer — the migration anchor must read `dev-factory`, not the vendored kernel's `harness-forge`
    default (the I-? provenance fix); `save()` also stamps the writing `kernel_version`. Both persist across
    every later load-modify-save."""
    if not os.path.exists(os.path.join(d, "lattice.json")):
        _lat.save(d, {"cells": [], "produced_by": "dev-factory"})


def init_instance(d):
    """Initialize a dev-factory instance: scaffold the substrate tree + the empty lattice + the
    coordination dirs. Idempotent. The server calls this on boot against the configured instance dir. On an
    EXISTING instance it runs the kernel-version handshake (`kernel_compat`) and warns on a skew — the
    run-time half of the vendoring contract (a re-vendored kernel meeting an older instance's state)."""
    _lat.scaffold(d)
    existed = os.path.exists(os.path.join(d, "lattice.json"))
    _ensure_lattice(d)
    if existed:
        ok, msg = _lat.kernel_compat(_lat.load(d))
        if not ok:
            sys.stderr.write(f"[dev-factory] kernel-version skew on boot: {msg}\n")
    for sub in ("tickets", "roadmap", "issues"):
        os.makedirs(os.path.join(d, "coordination", sub), exist_ok=True)
    return d


# ─────────────────────────────────────── tickets ───────────────────────────────────────

def create_ticket(d, type, title, body="", target_cell=None, target_transition=None,
                  acceptance=None, budget=None, dependencies=None, priority=None, created_by="human"):
    """Create a draft ticket (file-of-record + materialize). The first ledger event is the draft->active
    transition; creation itself is the initial state, not a transition.

    Shape contract (DF-5): `target_transition` is a `{"from","to"}` dict naming ONE legal maturity step
    (`defined→instantiated`, then `instantiated→validated` — multi-step like `defined→validated` is rejected
    by the lifecycle machine), validated here at the source. `acceptance` is `{"rubric_cell": …}`. Transitions
    elsewhere take an `actor` of shape `{"kind","id"}` (a bare string raises in `ledger.append`)."""
    tid = _led.ulid("epic-" if type == "epic" else "iss-" if type == "issue" else "tkt-")
    ticket = {
        "id": tid, "type": type, "title": title, "body": body, "state": "draft",
        "budget": budget or {"iterations": 5, "tokens": 200000},
        "dependencies": dependencies if dependencies is not None else {},
        "provenance": {"created_by": created_by, "ledger_refs": []},
        "timestamps": {"created": _now(), "updated": _now()},
    }
    if target_cell:
        ticket["target_cell"] = target_cell
    if target_transition is not None:
        # Validate at the source (DF-1/DF-5): a `target_transition` must be a `{"from","to"}` dict naming one
        # legal maturity step. Rejecting a bare string here means a malformed ticket never reaches disk — far
        # better than the string surviving to crash every later store.rebuild (incl. server boot).
        if not (isinstance(target_transition, dict) and target_transition.get("from") and target_transition.get("to")):
            raise ValueError(f"target_transition must be a {{'from','to'}} dict (one legal maturity step, "
                             f"e.g. {{'from':'defined','to':'instantiated'}}), got {target_transition!r}")
        ticket["target_transition"] = target_transition
    if acceptance:
        ticket["acceptance"] = acceptance
    if priority:
        ticket["priority"] = priority
    _ensure_lattice(d)
    _lc.save_ticket(d, ticket)
    _store.rebuild(d)
    return ticket


def get_ticket(d, tid):
    p = _lc._ticket_path(d, tid)
    return _lc.load_ticket(p) if os.path.isfile(p) else None


def list_tickets(d, state=None):
    return _store.query_tickets(d, state=state)


def edit_ticket(d, tid, fields):
    """Free field edits are legal only in `draft` (state changes go through transition)."""
    t = get_ticket(d, tid)
    if t is None:
        return None, "no such ticket"
    if t["state"] != "draft":
        return None, f"ticket is {t['state']}; only draft tickets accept free edits (use /transition)"
    for k in ("title", "body", "target_cell", "target_transition", "acceptance", "budget", "dependencies", "priority"):
        if k in fields:
            t[k] = fields[k]
    t["timestamps"]["updated"] = _now()
    _lc.save_ticket(d, t)
    _store.rebuild(d)
    return t, "edited"


def transition_ticket(d, tid, to_state, actor, verifier=None, reason=None):
    """THE single-writer transition path. Applies the kernel gate + (for done) the validation-path
    morphism, ledgers, writes the file, re-materializes. Returns (ok, ticket, msg)."""
    t = get_ticket(d, tid)
    if t is None:
        return False, None, f"no such ticket: {tid}"
    ok, t, msg = _lc.transition(d, t, to_state, actor, verifier=verifier, reason=reason)
    t["timestamps"]["updated"] = _now()
    _lc.save_ticket(d, t)        # file-of-record (already ledgered inside transition)
    _store.rebuild(d)            # re-materialize the index (Crawl-scale: full rebuild; Walk: incremental)
    return ok, t, msg


def cancel_ticket(d, tid, actor, reason="cancelled by human"):
    return transition_ticket(d, tid, "cancelled", actor, reason=reason)


# ─────────────────────────────────────── lattice + ledger (reads + seeding) ───────────────────────────────────────

def seed_cell(d, layer, scope, slug, maturity="absent", asset_ref=None, depends_on=None,
              budget=None, signal_refs=None):
    """Add (or update) a cell in the lattice — the lattice-architect's write, applied by the server. The
    vendored kernel owns the canonical lattice.json; this is the thin write wrapper."""
    _ensure_lattice(d)
    lat = _lat.load(d)
    cid = f"{layer}.{scope}.{slug}"
    existing = _lat.find(lat, cid)
    cell = existing if existing else {"layer": layer, "scope": scope, "slug": slug}
    cell["maturity"] = maturity
    cell.setdefault("blocked", False)
    cell["depends_on"] = depends_on or cell.get("depends_on", [])
    cell.setdefault("signal_refs", signal_refs or [])
    if asset_ref:
        cell["asset_ref"] = asset_ref
    if budget:
        cell["budget"] = budget
    if not existing:
        lat.setdefault("cells", []).append(cell)
    _lat.save(d, lat)
    _store.rebuild(d)
    return cell


def lattice_grid(d):
    return _store.grid(d)


def ledger_query(d, cell=None, since=None, n=100):
    """Always returns the source-of-truth ledger-entry shape (event/from/to/subject/actor/rationale),
    consistent across filters. The flat materialized shape is store.ledger_tail (for the UI fast path)."""
    return _led.read(d, cell=cell, since=since)[-n:]


def roadmap(d):
    import glob
    out = []
    for f in glob.glob(os.path.join(d, "coordination", "roadmap", "*.json")):
        try:
            out.append(json.load(open(f, encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


# ─────────────────────────── activities + the agent monitor (the lens) ───────────────────────────

def list_activities(d, status=None):
    return _store.activities(d, status=status)


def agents_running(d):
    """The agent monitor: the live running slice of the activity lens (queued/running/handed-off)."""
    return _store.activities(d, running_only=True)


# ─────────────────────────── roadmap + issues (the coordination corpus) ───────────────────────────

def create_epic(d, title, body="", target_cell=None, tickets=None, created_by="human"):
    """An epic: a dependency-ordered container of tickets, one file under coordination/roadmap/."""
    eid = _led.ulid("epic-")
    epic = {"id": eid, "title": title, "body": body, "tickets": tickets or [], "status": "draft",
            "provenance": {"created_by": created_by, "ledger_refs": []},
            "timestamps": {"created": _now(), "updated": _now()}}
    if target_cell:
        epic["target_cell"] = target_cell
    p = os.path.join(d, "coordination", "roadmap", f"{eid}.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(epic, open(p, "w", encoding="utf-8"), indent=2)
    _store.rebuild(d)
    return epic


def create_issue(d, title, body="", created_by="human"):
    """An untriaged observation — a ticket of type `issue` with no target cell until triaged."""
    return create_ticket(d, "issue", title, body, created_by=created_by)


def list_issues(d):
    return [t for t in _store.query_tickets(d) if t.get("type") == "issue"]


def triage_issue(d, iss_id, new_type, target_cell, target_transition, acceptance,
                 budget=None, dependencies=None, priority=None):
    """The ticket-triager's write: turn an untriaged issue into a well-formed ticket bound to a cell +
    transition + a validated rubric. Server-applied; the result can then pass gate-ticket-ready."""
    t = get_ticket(d, iss_id)
    if t is None or t.get("type") != "issue":
        return None, "not an untriaged issue"
    t.update({"type": new_type, "target_cell": target_cell, "target_transition": target_transition, "acceptance": acceptance})
    if budget:
        t["budget"] = budget
    if dependencies is not None:
        t["dependencies"] = dependencies
    if priority:
        t["priority"] = priority
    t["timestamps"]["updated"] = _now()
    _lc.save_ticket(d, t)
    _led.append(d, "transition", {"kind": "agent", "id": "ticket-triager"}, {"ticket": iss_id, "cell": target_cell},
                f"issue {iss_id} triaged into a {new_type} bound to {target_cell}")
    _store.rebuild(d)
    return t, "triaged"


# ─────────────────────────── governance + reports ───────────────────────────

def demote(d, family, cell, reason, actor=None):
    """The human governance demote (/api/control/demote): records an incident. The demotion itself is
    MECHANICAL — autonomy re-derives the lower tier from the ledgered incident; this just records it."""
    return _auto.record_incident(d, cell, reason, family=family)


def status(d, family=None):
    """The /harness-status-equivalent: maturity histogram, frontier, autonomy tier, gate-fire counts."""
    grid = lattice_grid(d)
    from collections import Counter
    mat = Counter(c["maturity"] for c in grid)
    return {"autonomy": _auto.status(d, family),
            "maturity": dict(mat),
            "cells": len(grid),
            "tickets": {s: len(list_tickets(d, state=s)) for s in ("active", "claimed", "in-progress", "in-review", "done", "blocked")},
            "running_agents": len(agents_running(d))}


def report(d, name, **kw):
    import reports as _reports
    return _reports.report(d, name, **kw)


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        init_instance(d)
        srv = {"kind": "server", "id": "dev-server"}
        # seed: a validated rubric + an instantiated spec cell
        seed_cell(d, "rubric", "task", "x", maturity="validated", signal_refs=["signals/rubric.task.x/seed.json"])
        seed_cell(d, "spec", "task", "x", maturity="instantiated", asset_ref="spec/x.md")
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "x.md"), "w").write("# x\n")

        # create a draft ticket through the API
        t = create_ticket(d, "feature", "advance x", target_cell="spec.task.x",
                           target_transition={"from": "instantiated", "to": "validated"},
                           acceptance={"rubric_cell": "rubric.task.x"}, budget={"iterations": 2, "tokens": 1000})
        expect(t["state"] == "draft", "created ticket not draft")
        expect(get_ticket(d, t["id"])["id"] == t["id"], "get_ticket failed")
        expect(len(list_tickets(d, state="draft")) == 1, "draft not materialized")

        # an illegal transition is refused with a reason
        ok, _t, msg = transition_ticket(d, t["id"], "done", srv)
        expect(not ok, "illegal draft->done allowed")

        # drive it legally through the API; done runs the validation path
        for to in ["active", "claimed", "in-progress", "in-review"]:
            ok, _t, msg = transition_ticket(d, t["id"], to, srv)
            expect(ok, f"{to} via API denied: {msg}")
        ok, ticket, msg = transition_ticket(d, t["id"], "done", srv, verifier="python3 -c 'import sys;sys.exit(0)'")
        expect(ok and ticket["state"] == "done", f"done via API failed: {msg}")

        # the index reflects it: ticket done, cell validated, ledger has the run
        expect(len(list_tickets(d, state="done")) == 1, "done ticket not in index")
        g = {c["id"]: c for c in lattice_grid(d)}
        expect(g["spec.task.x"]["maturity"] == "validated", "cell not validated in the grid")
        expect(g["spec.task.x"]["signal_count"] >= 1, "no signal counted on the cell")
        expect(any(e["event"] == "transition" and e.get("to") == "done" for e in ledger_query(d)), "done not in ledger")
    if fails:
        sys.stderr.write("api selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("api selftest: OK (create draft -> materialize; an illegal transition is refused with a reason; "
          "the legal path drives a cell to validated through the validation-path morphism; the index reflects "
          "ticket=done, cell=validated, and the full ledger — all server-mediated, single-writer)")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    sys.stderr.write("api.py is the operations library (use selftest, or import it / run app.py)\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
