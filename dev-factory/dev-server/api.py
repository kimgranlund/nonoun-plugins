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
    tid = _led.ulid("epic-" if type == "epic" else "iss-" if type in ("issue", "prompt", "instruction") else "tkt-")
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


# ─────────────────────────── operator input / guidance (the 5s steering channel) ───────────────────────────
# An operator streams steering messages in; a 5-second poll folds new ones into an active guidance buffer the
# loop reads. SECURITY: the intake + buffer live under run/, which _gates.VERIFIER protects (`.agents/dev-factory/
# run/*`) — so a gate-wired WORKER cannot forge guidance; only the un-gated single-writer server writes here.

GUIDANCE_CAP = 20   # the active buffer keeps the last N items; the intake jsonl keeps the full audit trail


def _run_dir(d):
    p = os.path.join(d, "run")
    os.makedirs(p, exist_ok=True)
    return p


def _input_path(d):
    return os.path.join(_run_dir(d), "input.jsonl")


def _guidance_path(d):
    return os.path.join(_run_dir(d), "guidance.json")


def enqueue_input(d, text, kind="steer", source="operator"):
    """Append an operator steering message to the append-only intake (run/input.jsonl). Returns the record,
    or None for empty text. Worker-write-denied by the run/ gate; the server/operator path writes it."""
    text = (text or "").strip()
    if not text:
        return None
    rec = {"ts": _now(), "text": text, "kind": kind, "source": source}
    with open(_input_path(d), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def _read_input_lines(d):
    p = _input_path(d)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def read_guidance(d):
    """The active guidance buffer — the derived view the loop + UI read: {updated, cursor, items[]}."""
    p = _guidance_path(d)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return {"updated": None, "cursor": 0, "items": []}


def drain_input(d):
    """Fold any NEW intake lines (past the cursor) into the active buffer, capped to the last GUIDANCE_CAP.
    Idempotent + incremental — returns the newly-folded records (possibly empty). This is the code the 5s
    poll runs: deterministic, no model. Atomic write so a crashed drain never corrupts the buffer."""
    lines = _read_input_lines(d)
    buf = read_guidance(d)
    cursor = buf.get("cursor", 0)
    new = lines[cursor:]
    if not new:
        return []
    items = (buf.get("items") or []) + new
    buf = {"updated": _now(), "cursor": len(lines), "items": items[-GUIDANCE_CAP:]}
    tmp = _guidance_path(d) + ".tmp"
    json.dump(buf, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, _guidance_path(d))
    return new


def recent_guidance(d, n=5):
    """The last n guidance texts, latest last — what a NEWLY dispatched worker's prompt folds in. (A running
    one-shot `claude -p` worker cannot receive mid-flight input; guidance steers the next dispatch + the loop.)"""
    items = read_guidance(d).get("items") or []
    return [it.get("text", "") for it in items[-n:] if it.get("text")]


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


def ready_tickets(d):
    """Active tickets that are actually DISPATCHABLE right now — unclaimed, with every dependency cell
    validated. The board hides this: an 'Active' card may be ready to dispatch, or blocked on an unmet dep."""
    grid = {c["id"]: c["maturity"] for c in lattice_grid(d)}
    out = []
    for t in list_tickets(d, state="active"):
        if t.get("claim"):
            continue
        deps = (t.get("dependencies") or {}).get("cells") or []
        if all(grid.get(c) == "validated" for c in deps):
            out.append(t)
    return out


def factory_state(d, heartbeat_enabled=False, paused=False, family=None):
    """A single 'is the factory working, and what is it doing' headline — what the SSE 'live' dot does NOT
    answer (that only means the socket is connected). Derived from real state (running workers, the heartbeat
    posture, the ready queue) so the UI can say IDLE / RUNNING / ARMED / PAUSED instead of leaving an operator
    to infer it from a green dot. Pure: the transport passes the live HEARTBEAT_ENABLED / PAUSED flags in."""
    running = agents_running(d)
    ready = ready_tickets(d)
    active = list_tickets(d, state="active")
    if paused:
        state = "paused"
    elif running:
        state = "running"        # workers actively on cells
    elif not heartbeat_enabled:
        state = "idle"           # Crawl — dispatch is human-driven; nothing auto-runs
    elif ready:
        state = "armed"          # heartbeat on, dispatchable work waiting — one tick from running
    elif active:
        state = "blocked"        # heartbeat on, active tickets exist but NONE dep-ready — waiting on deps
    else:
        state = "drained"        # heartbeat on, no active tickets at all — the queue is empty / build done
    return {"state": state, "running_agents": len(running), "ready_to_dispatch": len(ready),
            "active_tickets": len(active), "ready_cells": [t.get("target_cell") for t in ready][:8],
            "heartbeat_enabled": bool(heartbeat_enabled), "paused": bool(paused)}


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
        # factory_state (UI-3): the work-state headline distinct from the SSE socket. After the done ticket
        # above there are 0 active tickets, so the states are deterministic.
        expect(factory_state(d, heartbeat_enabled=False)["state"] == "idle",
               "factory_state with heartbeat off must be 'idle' (Crawl, human-driven)")
        expect(factory_state(d, heartbeat_enabled=True)["state"] == "drained",
               "factory_state with heartbeat on + no active tickets must be 'drained' (queue empty)")
        expect(factory_state(d, paused=True, heartbeat_enabled=True)["state"] == "paused", "paused not reported")
        expect("active_tickets" in factory_state(d, False) and "ready_to_dispatch" in factory_state(d, False),
               "factory_state must surface the active + ready counts the UI renders")

        # the 5s operator-input / guidance channel: enqueue -> drain -> buffer -> recent (latest-last)
        expect(recent_guidance(d) == [], "guidance must start empty")
        enqueue_input(d, "focus the drag-drop first", source="operator")
        enqueue_input(d, "use a standard 52-card deck")
        drained = drain_input(d)
        expect(len(drained) == 2, f"drain must fold the 2 new inputs, got {len(drained)}")
        expect(drain_input(d) == [], "drain must be idempotent — no new inputs folds nothing")
        expect(recent_guidance(d, n=5)[-1] == "use a standard 52-card deck", "recent_guidance must be latest-last")
        expect(os.path.exists(os.path.join(d, "run", "input.jsonl")),
               "input intake must live under run/ (the gate-protected perimeter — workers cannot forge guidance)")

        # Feature B: a PROMPT ticket is untriaged intake — created with no cell (iss- id) and PARKED (denied active)
        p = create_ticket(d, "prompt", "build a solitaire game", body="drag-drop, scoring, leaderboards")
        expect(p["id"].startswith("iss-") and p.get("target_cell") is None, "a prompt ticket must be untriaged intake")
        ok, _pt, pmsg = transition_ticket(d, p["id"], "active", srv)
        expect(not ok and "untriaged" in pmsg, f"an untriaged prompt ticket must be denied active: {pmsg}")
    if fails:
        sys.stderr.write("api selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("api selftest: OK (create draft -> materialize; an illegal transition is refused with a reason; "
          "the legal path drives a cell to validated through the validation-path morphism; the index reflects "
          "ticket=done, cell=validated, and the full ledger — all server-mediated, single-writer; the 5s "
          "operator-input channel folds intake -> guidance (idempotent, run/-protected); a prompt intake ticket "
          "parks untriaged)")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    verb = argv[0]
    d = argv[argv.index("--dir") + 1] if "--dir" in argv else os.environ.get("DEV_FACTORY_DIR", ".agents/dev-factory")
    if verb == "enqueue-input":
        text = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else ""
        rec = enqueue_input(d, text, source="cli")
        drain_input(d)
        print(json.dumps(rec)) if rec else sys.stderr.write("enqueue-input: empty text\n")
        return 0 if rec else 1
    if verb == "guidance":
        print(json.dumps(read_guidance(d), indent=2))
        return 0
    sys.stderr.write("api.py is the operations library. verbs: selftest | "
                     "enqueue-input <text> [--dir D] | guidance [--dir D]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
