#!/usr/bin/env python3
"""autonomy.py — the trust trajectory: earned, measured, mechanically-revocable autonomy (TDD §14.2).

The keystone safety property. A loop family runs unattended ONLY at the tier its LEDGER-MEASURED track
record has earned — never the tier the artifact claims. The tier is COMPUTED from the ledger here (the
heartbeat's `tier_allows` reads it), and demotion is MECHANICAL: a reward-hack incident or a false-pass
spike drops the family's earned tier with no human in the demotion path (REQ-SAFE-004). Humans investigate
*after* via the incident-responder; the demotion already happened, by virtue of the ledger record that
`tier_for` re-derives from.

The honest-scope invariant (anti-reward-hacking): a false-pass RATE is `unmeasured` until an INDEPENDENT
refuter has re-validated at least one passing cell. A never-refuted family therefore CANNOT reach Tier 2
— you cannot claim "< 5% false-pass" you never measured. A 0.0% with no refuter is the lie that would
auto-promote a never-checked family to lights-out; this refuses it.

  Tier 0 Attended            default for a new family; nothing unattended
  Tier 1 Gated               a validated verifier exists; dispatch, but a human reviews at in-review
  Tier 2 Unattended-in-budget  measured false-pass < 5%, zero open incidents, a budget armed
  Tier 3 Scheduled/lights-out   Tier 2 sustained across a window, hermetic sandbox + tamper-evident audit

Usage:
  autonomy.py tier        --dir DIR [--family F]
  autonomy.py refuter     --dir DIR --cell C [--family F] [--disagree]   # record an independent re-check
  autonomy.py incident    --dir DIR --cell C --reason R [--family F]     # record a caught false pass -> demote
  autonomy.py selftest
Stdlib only; Python 3.8+.
"""
import datetime
import json
import os
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import lattice as _lat      # noqa: E402
import ledger as _led       # noqa: E402

FALSE_PASS_CEILING = 0.05           # Tier 2 needs a measured rate below this
INCIDENT_COOLDOWN_S = 7 * 24 * 3600  # an incident caps the tier until this much clean time passes
SUSTAINED_REFUTERS = 5              # Tier 3 needs this many clean independent re-checks across the window

TIER_POLICY = {
    0: {"name": "attended", "unattended": False, "precondition": "default for a new family"},
    1: {"name": "gated", "unattended": False, "precondition": "a validated verifier exists; human reviews at in-review"},
    2: {"name": "unattended-in-budget", "unattended": True,
        "precondition": "measured false-pass < 5%, zero open incidents, a budget armed"},
    3: {"name": "scheduled", "unattended": True,
        "precondition": "Tier 2 sustained across a window; hermetic sandbox + tamper-evident audit"},
}


def _now():
    return datetime.datetime.now().astimezone()


def _family_match(e, family):
    if family is None:
        return True
    return (e.get("metrics") or {}).get("family") == family


def _has_validated_verifier(d, family=None):
    """A family is at least Tier 1 only once it has a validated rubric (a verifier) to score against."""
    for c in _lat.load(d).get("cells", []):
        if c.get("layer") == "rubric" and c.get("maturity") == "validated":
            return True
    return False


def refuter_checks(d, family=None):
    """Independent re-validations recorded (the denominator of the false-pass rate). Delegates to the
    canonical ledger computation — one source of truth."""
    return _led.refuter_checks(d, family)


def incidents(d, family=None, since=None):
    out = [e for e in _led.read(d, event="incident") if _family_match(e, family)]
    if since:
        out = [e for e in out if e.get("ts", "") >= since]
    return out


def false_pass(d, family=None):
    """incidents / independent-refuter-checks; `unmeasured` until at least one refuter has re-checked — a
    rate you never measured is not a rate you can trust. Delegates to the SINGLE canonical implementation in
    `ledger.false_pass_rate` (the function the autonomy policy docs cite), so the documented formula and the
    consumed formula can never fork again."""
    return _led.false_pass_rate(d, family)


def open_incidents(d, family=None, now=None):
    """Incidents still inside their cooldown — these mechanically cap the tier."""
    now = now or _now()
    cutoff = (now - datetime.timedelta(seconds=INCIDENT_COOLDOWN_S)).isoformat(timespec="seconds")
    return incidents(d, family, since=cutoff)


def _budget_armed(d):
    return os.path.isfile(os.path.join(d, "run", "heartbeat.json")) or os.path.isfile(os.path.join(d, "run", "budget.json"))


def tier_for(d, family=None, now=None, hermetic=False, tamper_evident=None):
    """The EARNED tier — computed from the ledger, never asserted. The heartbeat reads this as
    `tier_allows`. Returns an int 0..3. `tamper_evident` defaults to DERIVED from the ledger hash-chain
    (ledger.verify_chain) — a real audit-integrity check, not a flag; `hermetic` stays an operator-declared
    deploy property (true network/process isolation isn't introspectable from here)."""
    now = now or _now()
    if tamper_evident is None:
        tamper_evident = _led.verify_chain(d)[0]      # the audit trail's hash-chain is intact
    tier = 0
    if _has_validated_verifier(d, family):
        tier = 1
    fp = false_pass(d, family)
    if tier >= 1 and fp != "unmeasured" and fp < FALSE_PASS_CEILING and _budget_armed(d):
        tier = 2
    if tier >= 2 and hermetic and tamper_evident and len(refuter_checks(d, family)) >= SUSTAINED_REFUTERS:
        tier = 3
    # MECHANICAL DEMOTION: any open incident caps the family at Tier 1 (no unattended dispatch), no human
    # in the path — the cap is a pure function of the ledgered incident.
    if open_incidents(d, family, now):
        tier = min(tier, 1)
    return tier


def tier_allows(d, ticket=None, family=None, now=None):
    """The spec §8.1 `tier_allows(t)` predicate the heartbeat's ready-filter uses: does the family's EARNED
    tier permit an unattended dispatch at all? Tier 0 permits nothing; Tier >=1 permits dispatch (Tier 1
    dispatches but stops at in-review for human review, Tier 2+ drives to done). The boolean form of
    `tier_for`; the heartbeat reads the int from `tier_for` to decide auto-validate vs in-review."""
    return tier_for(d, family=family, now=now) >= 1


def record_refuter_check(d, cell, agreed, family=None, now=None, rationale=None):
    """An INDEPENDENT refuter re-validated `cell`. Agreement makes the false-pass rate measurable; a
    disagreement is a caught false pass → an incident (mechanical demotion)."""
    now = now or _now()
    _led.append(d, "signal", {"kind": "agent", "id": "refuter"}, {"cell": cell},
                rationale or f"independent refuter re-check of {cell}: {'agreed' if agreed else 'DISAGREED'}",
                to="pass" if agreed else "fail", ts=now.isoformat(timespec="seconds"),
                metrics={"refuter": True, "agreed": bool(agreed), "family": family})
    if not agreed:
        return record_incident(d, cell, f"refuter disagreed with the critic on {cell} — a false pass", family, now)
    return tier_for(d, family, now)


def record_incident(d, cell, reason, family=None, now=None):
    """A reward-hack / false-pass incident. Logs it AND flags the family's verifier cells `stale` (they
    must be re-validated before trust resumes). The demotion is the ledger record + the stale flag; the
    next tier_for re-derives the lower tier. No human approves it."""
    now = now or _now()
    _led.append(d, "incident", {"kind": "server", "id": "exploit-scan"}, {"cell": cell},
                f"INCIDENT: {reason}", ts=now.isoformat(timespec="seconds"), metrics={"family": family})
    # stale the verifier cells — a verifier implicated in a false pass cannot be trusted until re-validated
    lat = _lat.load(d)
    staled = []
    for c in lat.get("cells", []):
        if c.get("layer") == "rubric" and c.get("maturity") == "validated":
            c["maturity"] = "stale"
            staled.append(_lat.cid(c))
    if staled:
        _lat.save(d, lat)
        _led.append(d, "demote", {"kind": "server", "id": "autonomy"}, {"cell": cell},
                    f"mechanical demotion: verifier(s) {staled} flagged stale after the incident",
                    ts=now.isoformat(timespec="seconds"), metrics={"family": family})
    return tier_for(d, family, now)


def status(d, family=None, now=None):
    now = now or _now()
    t = tier_for(d, family, now)
    return {"tier": t, "name": TIER_POLICY[t]["name"], "unattended": TIER_POLICY[t]["unattended"],
            "false_pass": false_pass(d, family), "refuter_checks": len(refuter_checks(d, family)),
            "open_incidents": len(open_incidents(d, family, now)), "budget_armed": _budget_armed(d)}


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": []})
        n0 = _now()

        # a brand-new family: Tier 0 (no verifier)
        expect(tier_for(d, now=n0) == 0, "new family should be Tier 0 (attended)")

        # add a validated verifier → Tier 1 (gated); NOT Tier 2 (false-pass unmeasured)
        lat = _lat.load(d)
        lat["cells"].append({"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated", "depends_on": [], "signal_refs": ["x"]})
        _lat.save(d, lat)
        expect(tier_for(d, now=n0) == 1, "a validated verifier should yield Tier 1")
        expect(false_pass(d) == "unmeasured", "false-pass must be 'unmeasured' before any refuter check")

        # arm a budget + an independent refuter that AGREES → false-pass measured low → Tier 2
        os.makedirs(os.path.join(d, "run"), exist_ok=True)
        json.dump({"start_ts": n0.isoformat(timespec="seconds")}, open(os.path.join(d, "run", "heartbeat.json"), "w"))
        record_refuter_check(d, "spec.task.s", agreed=True, now=n0)
        expect(false_pass(d) == 0.0, f"one agreeing refuter check → 0.0 false-pass; got {false_pass(d)}")
        expect(tier_for(d, now=n0) == 2, f"measured-clean family + budget should reach Tier 2; got {tier_for(d, now=n0)}")

        # an UNMEASURED family with a budget still cannot reach Tier 2 (honest scope)
        with tempfile.TemporaryDirectory() as r2:
            d2 = os.path.join(r2, ".agents/dev-factory")
            _lat.scaffold(d2)
            _lat.save(d2, {"cells": [{"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated", "depends_on": [], "signal_refs": ["x"]}]})
            os.makedirs(os.path.join(d2, "run"), exist_ok=True)
            json.dump({"start_ts": n0.isoformat(timespec="seconds")}, open(os.path.join(d2, "run", "heartbeat.json"), "w"))
            expect(tier_for(d2, now=n0) == 1, "an unmeasured family must NOT reach Tier 2 even with a budget — honest scope")

        # MECHANICAL DEMOTION: a refuter that DISAGREES (a caught false pass) drops the tier with no human
        t_before = tier_for(d, now=n0)
        new_tier = record_refuter_check(d, "spec.task.s", agreed=False, now=n0)
        expect(t_before == 2 and new_tier <= 1, f"a caught false pass must demote Tier 2 -> <=1; got {t_before}->{new_tier}")
        expect(tier_for(d, now=n0) <= 1, "the demotion must persist (re-derived from the ledger, not a human's call)")
        # the verifier was flagged stale (must be re-validated before trust resumes)
        rub = next(c for c in _lat.load(d)["cells"] if c["layer"] == "rubric")
        expect(rub["maturity"] == "stale", "the implicated verifier was not flagged stale by the incident")
        # the demotion is in the ledger (auditable), the incident too
        expect(any(e["event"] == "incident" for e in _led.read(d)), "no incident ledgered")
        expect(any(e["event"] == "demote" for e in _led.read(d)), "no mechanical demotion ledgered")

        # after the cooldown passes (no new incidents), the cap lifts (but the staled verifier keeps Tier at <=1 anyway)
        later = n0 + datetime.timedelta(seconds=INCIDENT_COOLDOWN_S + 60)
        expect(not open_incidents(d, now=later), "incident should be out of cooldown later")
    if fails:
        sys.stderr.write("autonomy selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("autonomy selftest: OK (new family=Tier 0; a validated verifier=Tier 1; false-pass is 'unmeasured' "
          "until an independent refuter checks, so an unmeasured family CANNOT reach Tier 2 even with a budget; "
          "a measured-clean family reaches Tier 2; a caught false pass MECHANICALLY demotes it to <=1 AND stales "
          "the verifier, re-derived from the ledger with no human in the demotion path)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    d = _arg(argv, "--dir", ".agents/dev-factory")
    fam = _arg(argv, "--family")
    if argv[0] == "tier":
        print(json.dumps(status(d, fam)))
        return 0
    if argv[0] == "refuter":
        print(record_refuter_check(d, _arg(argv, "--cell"), agreed="--disagree" not in argv, family=fam))
        return 0
    if argv[0] == "incident":
        print(record_incident(d, _arg(argv, "--cell"), _arg(argv, "--reason", "unspecified"), family=fam))
        return 0
    print(f"autonomy.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
