#!/usr/bin/env python3
"""lifecycle.py — the ticket lifecycle state machine + the typed morphism to the lattice.

This is the deterministic half of the central reconciliation (TDD §4, §7). A ticket is a coordination
Activity whose whole purpose is to drive ONE cell maturity transition. Two machines, one link:

    ticket: draft -> active -> claimed -> in-progress -> in-review -> done   (+ blocked/paused/cancelled)
    cell:   the 8-state maturity machine (the VENDORED harness-forge kernel)

    THE LINK:  ticket `done`  <=>  the target cell advanced to `target_transition.to`,
               and that advance was minted by the validation path (a critic-written signal the
               worker could not forge) — the SAME gate-signal. The board cannot disagree with the
               lattice, by construction.

Single-writer discipline (REQ-CORPUS-003): every transition here is applied by ONE authority (the
server, or a human via the API) and terminates in a ledger event. Workers never call this to
self-claim — the dispatcher assigns `claimed`, designing the claim race out (§7.2).

Computation routes to code: the gates below are deterministic predicates over the lattice + the
ticket, never inference. The model's judgment lives INSIDE a dispatched unit (authoring the asset,
calibrating the rubric), never in deciding whether a transition is legal.

Usage:
  lifecycle.py transition --dir DIR --ticket FILE --to STATE [--actor-kind K --actor-id ID] \
               [--verifier 'cmd args']   # --verifier required for in-review->done (the morphism)
  lifecycle.py gate-ticket-ready --dir DIR --ticket FILE
  lifecycle.py gate-dispatch     --dir DIR --ticket FILE [--slots-free N] [--tier T]
  lifecycle.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import shlex
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import lattice as _lat      # noqa: E402  vendored kernel (transition_ok/load/find/save/cid)
import validate as _val     # noqa: E402  vendored validation path (mints the signal from a verifier's exit)
import ledger as _led       # noqa: E402  native append-only provenance

# Ticket lifecycle: from_state -> {to_state: gate}. `None` = a human/operator transition with no
# readiness predicate (cancel/pause/resume); a string names the gate function that must pass.
LIFECYCLE = {
    "draft":       {"active": "gate_ticket_ready", "cancelled": None},
    "active":      {"claimed": "gate_dispatch", "blocked": None, "paused": None, "cancelled": None},
    "claimed":     {"in-progress": None, "blocked": None, "paused": None, "cancelled": None, "active": None},
    "in-progress": {"in-review": None, "blocked": None, "paused": None, "cancelled": None, "active": None},
    "in-review":   {"done": "gate_signal", "in-progress": None, "blocked": None, "cancelled": None},
    "blocked":     {"active": "gate_ticket_ready", "cancelled": None},
    "paused":      {"active": None, "cancelled": None},
    "done":        {},
    "cancelled":   {},
}

# The maturity that REQUIRES a critic signal to reach — the trust line. Reaching `validated` (a cell that
# will be reused/trusted) is gated by a signal the worker cannot forge — whether the FIRST validation
# (instantiated -> validated) or a RE-validation after a revision (regenerating -> validated). Every other
# advance is the worker authoring (absent->defined, defined->instantiated), starting a revision
# (validated->regenerating), or promoting to use (validated->operating) — applied by the server, making no
# validation claim. The trust boundary holds exactly at the line that matters: a worker can author and
# revise, but cannot declare its own work validated.
SIGNAL_BEARING = {"validated"}


def _ticket_path(d, tid):
    return os.path.join(d, "coordination", "tickets", f"{tid}.json")


def load_ticket(path):
    return json.load(open(path, encoding="utf-8"))


def save_ticket(d, ticket):
    p = _ticket_path(d, ticket["id"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(ticket, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, p)
    return p


# ─────────────────────────── the transition gates (deterministic predicates) ───────────────────────────

def gate_ticket_ready(d, ticket, lat):
    """draft|blocked -> active. The ticket must be well-formed AND bound to a real, legal, validated target."""
    if ticket.get("type") == "issue" and not ticket.get("target_cell"):
        return False, "issue is untriaged: no target_cell (triage it into a feature/task first)"
    tc = ticket.get("target_cell")
    if not tc:
        return False, "no target_cell"
    cell = _lat.find(lat, tc)
    if cell is None:
        return False, f"target_cell {tc} does not exist in the lattice"
    tt = ticket.get("target_transition")
    if not tt or "from" not in tt or "to" not in tt:
        return False, "no target_transition {from,to}"
    if not _lat.transition_ok(tt["from"], tt["to"]):
        return False, f"illegal maturity transition {tt['from']} -> {tt['to']}"
    acc = ticket.get("acceptance", {})
    rc = acc.get("rubric_cell")
    if not rc:
        return False, "acceptance not bound to a rubric_cell (doneness must be a validated rubric, not prose)"
    rcell = _lat.find(lat, rc)
    if rcell is None:
        return False, f"acceptance rubric_cell {rc} does not exist"
    if rcell.get("maturity") != "validated":
        return False, f"acceptance rubric {rc} is not validated (it is {rcell.get('maturity')}) — scoring against vibes"
    b = ticket.get("budget") or {}
    if not (b.get("iterations") and b.get("tokens")):
        return False, "budget missing iterations/tokens (a prose budget is advisory under pressure)"
    if "dependencies" not in ticket:
        return False, "dependencies not declared (use {} to assert none)"
    return True, "ready"


def gate_dispatch(d, ticket, lat, slots_free=1, tier=3, done_tickets=frozenset()):
    """active -> claimed (server dispatcher, single-writer). All readiness, budget, concurrency, and
    autonomy-tier conditions must hold before a worker is launched."""
    deps = ticket.get("dependencies", {})
    for cid in deps.get("cells_ready", []):
        c = _lat.find(lat, cid)
        if c is None or c.get("maturity") != "validated":
            return False, f"dependency cell {cid} not validated (partial-order not satisfied)"
    for t in deps.get("tickets", []):
        if t not in done_tickets:
            return False, f"dependency ticket {t} not done"
    if slots_free < 1:
        return False, "no concurrency slot free (REQ-LOOP-004)"
    # autonomy tier: tier 0 dispatches NOTHING unattended; higher tiers permit it (§14.2). The caller
    # passes the family's ledger-measured tier; lifecycle only enforces the predicate.
    if tier < 1:
        return False, "autonomy tier 0 (attended): no unattended dispatch permitted for this family"
    cell = _lat.find(lat, ticket.get("target_cell"))
    if cell is not None and cell.get("blocked"):
        return False, f"target_cell {ticket['target_cell']} is blocked (stop-gate) — dropped from dispatch"
    return True, "dispatchable"


def _signal_present(d, lat, ticket):
    """gate-signal at in-review->done: the target cell carries a signal_ref AND has reached the ticket's
    to_maturity. A signal can ONLY have been written by the validation path (gate-signal denies worker
    writes to signals/), so its presence is proof a critic — not the worker — validated the work."""
    tc = ticket.get("target_cell")
    cell = _lat.find(lat, tc)
    if cell is None:
        return False, f"target_cell {tc} vanished"
    to = ticket.get("target_transition", {}).get("to")
    if cell.get("maturity") != to:
        return False, f"target_cell {tc} is {cell.get('maturity')}, not the ticket's to-maturity {to}"
    if not cell.get("signal_refs"):
        return False, f"target_cell {tc} has no signal — done would be 'validated by assertion'"
    return True, "signal present; cell advanced"


def _author_advance(d, lat, ticket, actor):
    """Apply an authoring maturity bump (absent->defined, defined->instantiated) at done — the worker
    wrote the asset, the SERVER records the advance (single-writer). No critic signal: an authoring cell
    makes no validation claim. Returns (ok, reason)."""
    tc = ticket["target_cell"]
    cell = _lat.find(lat, tc)
    if cell is None:
        return False, f"target_cell {tc} missing"
    to_mat = ticket["target_transition"]["to"]
    if not _lat.transition_ok(cell["maturity"], to_mat):
        return False, f"illegal maturity advance {cell['maturity']} -> {to_mat}"
    if to_mat in ("defined", "instantiated") and not cell.get("asset_ref"):
        return False, f"no asset_ref on {tc} — the worker authored nothing to advance"
    frm = cell["maturity"]
    cell["maturity"] = to_mat
    _lat.save(d, lat)
    _led.append(d, "transition", actor, {"ticket": ticket["id"], "cell": tc},
                f"authoring advance {tc}: {frm} -> {to_mat}", frm=frm, to=to_mat)
    return True, f"authored {tc} -> {to_mat}"


# ─────────────────────────────────────── the transition driver ───────────────────────────────────────

def transition(d, ticket, to_state, actor, verifier=None, reason=None):
    """Apply one lifecycle transition. Returns (ok, ticket, msg). The done transition runs the validation
    path (the morphism); every transition appends a ledger event (no silent state change)."""
    frm = ticket["state"]
    if to_state not in LIFECYCLE.get(frm, {}):
        return False, ticket, f"illegal lifecycle transition {frm} -> {to_state}"
    lat = _lat.load(d)
    gate = LIFECYCLE[frm][to_state]

    # readiness gates
    if gate == "gate_ticket_ready":
        ok, why = gate_ticket_ready(d, ticket, lat)
        if not ok:
            return False, ticket, f"gate-ticket-ready denied: {why}"
    elif gate == "gate_dispatch":
        ok, why = gate_dispatch(d, ticket, lat)
        if not ok:
            return False, ticket, f"gate-dispatch denied: {why}"

    # THE MORPHISM: in-review -> done. A signal-bearing advance runs the validation path and requires
    # the critic's signal; an authoring advance is applied by the server with no critic signal.
    if to_state == "done":
        tc = ticket["target_cell"]
        to_mat = ticket.get("target_transition", {}).get("to")
        if to_mat in SIGNAL_BEARING:
            if verifier:
                harness = ticket.get("acceptance", {}).get("rubric_cell", "rubric").split(".")[-1] or "verifier"
                cmd = shlex.split(verifier) if isinstance(verifier, str) else list(verifier)
                vok, sig, vmsg = _val.run_validation(d, tc, harness, cmd)
                lat = _lat.load(d)  # reload — validate.py advanced the cell + wrote the signal
                if not vok:
                    # critic failed: ticket returns to in-progress (feedback, attempts++), never done.
                    ticket["state"] = "in-review"
                    _led.append(d, "signal", actor, {"ticket": ticket["id"], "cell": tc},
                                f"validation FAILED: {vmsg}", to="fail")
                    return False, ticket, f"gate-signal denied: verifier failed — {vmsg}"
                cell = _lat.find(lat, tc)
                ticket.setdefault("signal_refs", [])
                ticket["signal_refs"] = list(cell.get("signal_refs", []))
                _led.append(d, "signal", {"kind": "agent", "id": "cell-validator"}, {"ticket": ticket["id"], "cell": tc},
                            f"critic validated {tc}: {vmsg}", to="pass",
                            hashes={"validated_against": [{"cell_id": k, "hash": v} for k, v in cell.get("validated_against", {}).items()]})
                # the maturity advance is itself a ledgered transition (provenance for the grid + staleness)
                _led.append(d, "transition", actor, {"ticket": ticket["id"], "cell": tc},
                            f"cell {tc} advanced to {to_mat} (critic-validated)",
                            frm=ticket.get("target_transition", {}).get("from"), to=to_mat)
            # assert the morphism: a signal exists + the cell reached to_mat (whether we ran the verifier or a prior critic did)
            sok, swhy = _signal_present(d, lat, ticket)
            if not sok:
                return False, ticket, f"gate-signal denied: {swhy}"
        else:
            # authoring advance (absent->defined, defined->instantiated): the worker wrote the asset; the
            # SERVER applies the maturity bump (a worker cannot write lattice.json — gate-verifier). No signal.
            aok, awhy = _author_advance(d, lat, ticket, actor)
            if not aok:
                return False, ticket, f"authoring done denied: {awhy}"

    # commit the ticket transition + ledger it
    ticket["state"] = to_state
    ref = _led.append(d, "transition", actor, {"ticket": ticket["id"], "cell": ticket.get("target_cell")},
                      reason or f"{frm} -> {to_state}", frm=frm, to=to_state)
    ticket.setdefault("provenance", {}).setdefault("ledger_refs", []).append(ref)
    if to_state == "done":
        tt = ticket.get("target_transition", {})
        return True, ticket, f"DONE — ticket {ticket['id']} closed; cell {ticket['target_cell']} advanced {tt.get('from')} -> {tt.get('to')} through gate-signal"
    return True, ticket, f"{frm} -> {to_state}"


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        # a lattice: a validated rubric (the verifier) + an instantiated spec cell to advance
        lat = {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "first-slice", "maturity": "validated",
             "signal_refs": ["signals/rubric.task.first-slice/x.json"], "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "first-slice", "maturity": "instantiated",
             "asset_ref": "spec/first-slice.md", "depends_on": [], "signal_refs": []},
        ]}
        _lat.save(d, lat)
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "first-slice.md"), "w").write("# first slice\n")

        tid = _led.ulid("tkt-")
        ticket = {
            "id": tid, "type": "feature", "title": "validate the first slice", "body": "drive it to validated",
            "state": "draft",
            "target_cell": "spec.task.first-slice",
            "target_transition": {"from": "instantiated", "to": "validated"},
            "acceptance": {"rubric_cell": "rubric.task.first-slice"},
            "budget": {"iterations": 3, "tokens": 100000},
            "dependencies": {},
            "provenance": {"created_by": "human", "ledger_refs": []},
            "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:00+00:00"},
        }
        srv = {"kind": "server", "id": "srv"}

        # 1. draft -> active passes the ready gate
        ok, ticket, msg = transition(d, ticket, "active", srv)
        expect(ok, f"draft->active denied: {msg}")

        # 2. a malformed ticket (unvalidated rubric) is denied by gate-ticket-ready
        bad = dict(ticket); bad = json.loads(json.dumps(ticket)); bad["state"] = "draft"
        badlat = _lat.load(d)
        for c in badlat["cells"]:
            if _lat.cid(c) == "rubric.task.first-slice":
                c["maturity"] = "defined"  # not validated
        _lat.save(d, badlat)
        bok, _bt, bmsg = transition(d, bad, "active", srv)
        expect(not bok and "not validated" in bmsg, f"unvalidated-rubric ticket was NOT denied: {bmsg}")
        # restore the validated rubric
        gl = _lat.load(d)
        for c in gl["cells"]:
            if _lat.cid(c) == "rubric.task.first-slice":
                c["maturity"] = "validated"
        _lat.save(d, gl)

        # 3. active -> claimed -> in-progress -> in-review
        for to in ["claimed", "in-progress", "in-review"]:
            ok, ticket, msg = transition(d, ticket, to, srv)
            expect(ok, f"{to} denied: {msg}")

        # 4. THE MORPHISM (fail path): in-review -> done with a FAILING verifier does NOT close + does NOT advance
        ok, ticket, msg = transition(d, ticket, "done", srv, verifier="python3 -c 'import sys; sys.exit(1)'")
        expect(not ok, f"done was allowed on a failing verifier: {msg}")
        expect(_lat.find(_lat.load(d), "spec.task.first-slice")["maturity"] == "instantiated",
               "cell advanced despite a failing verifier (reward-hack!)")
        expect(ticket["state"] == "in-review", "ticket left in-review on a failed validation")

        # 5. THE MORPHISM (pass path): a PASSING verifier mints the signal, advances the cell, closes the ticket
        ok, ticket, msg = transition(d, ticket, "done", srv, verifier="python3 -c 'import sys; sys.exit(0)'")
        expect(ok, f"done denied on a passing verifier: {msg}")
        cell = _lat.find(_lat.load(d), "spec.task.first-slice")
        expect(cell["maturity"] == "validated", f"cell did not reach validated: {cell['maturity']}")
        expect(cell.get("signal_refs"), "no signal_ref on the validated cell — the morphism's currency is missing")
        expect(ticket["state"] == "done", "ticket not closed after a passing validation")
        # the signal on the cell is the SAME one the ticket carries (one gate, both transitions)
        expect(ticket.get("signal_refs") == cell.get("signal_refs"), "ticket and cell signals diverged (board != lattice)")

    if fails:
        sys.stderr.write("lifecycle selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("lifecycle selftest: OK (draft->active gated on a VALIDATED rubric; the claim race is server-set; "
          "in-review->done runs the validation path — a failing verifier neither closes the ticket nor advances "
          "the cell, a passing one mints the critic's signal and advances both through the SAME gate-signal; "
          "the ticket's signal IS the cell's — the board cannot disagree with the lattice)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    verb = argv[0]
    d = _arg(argv, "--dir", ".agents/dev-factory")
    tpath = _arg(argv, "--ticket")
    if verb in ("gate-ticket-ready", "gate-dispatch"):
        ticket = load_ticket(tpath)
        lat = _lat.load(d)
        if verb == "gate-ticket-ready":
            ok, why = gate_ticket_ready(d, ticket, lat)
        else:
            ok, why = gate_dispatch(d, ticket, lat, int(_arg(argv, "--slots-free", "1")), int(_arg(argv, "--tier", "3")))
        print(why)
        return 0 if ok else 1
    if verb == "transition":
        ticket = load_ticket(tpath)
        actor = {"kind": _arg(argv, "--actor-kind", "server"), "id": _arg(argv, "--actor-id", "server")}
        ok, ticket, msg = transition(d, ticket, _arg(argv, "--to"), actor,
                                     verifier=_arg(argv, "--verifier"), reason=_arg(argv, "--reason"))
        save_ticket(d, ticket)
        print(msg)
        return 0 if ok else 1
    print(f"lifecycle.py: unknown verb {verb}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
