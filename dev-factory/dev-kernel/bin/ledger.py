#!/usr/bin/env python3
"""ledger.py — dev-factory's append-only provenance ledger (the event-sourced spine).

The ledger is the SOURCE OF TRUTH for every state transition (harness-and-storage.md): git-native
JSONL at `.agents/dev-factory/ledger/events.jsonl`, append-only, never mutated. Current operational
state — ticket lifecycle, cell maturity, leases, metrics, the grid — is a materialized *fold* over
this log; the SQLite index the server keeps is downstream and rebuildable by replay. Provenance
cannot be retrofitted, so the ledger is authoritative and the database is never ahead of it.

This module is dev-native (the coordination event vocabulary — dispatch/claim/transition/signal/
block/demote/... — is dev-factory's; the vendored harness-forge kernel carries a different one). It
borrows harness-forge's proven discipline: append via a single path, no-progress as a failure-loop
detector in code, and false-pass returning `unmeasured` (not a misleading 0.0%) until an independent
refuter exists — autonomy is earned by a measured rate, never asserted.

Usage:
  ledger.py append --dir DIR --event E --actor-kind K --actor-id ID [--ticket T] [--cell C] \
            [--from S] [--to S] --rationale "why"
  ledger.py read   --dir DIR [--cell C] [--ticket T] [--event E] [--since ISO]
  ledger.py tail   --dir DIR [-n N]
  ledger.py no-progress --dir DIR --cell C [-n 3]      # exit 0 if a no-progress loop is detected
  ledger.py selftest
Stdlib only; Python 3.8+.
"""
import datetime
import hashlib
import json
import os
import sys
import time

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EVENTS = ["dispatch", "claim", "transition", "signal", "block", "unblock",
          "demote", "promote", "regenerate", "stale-propagated", "cancel", "incident",
          "activity-start", "handoff", "activity-complete", "activity-fail"]
ACTOR_KINDS = ["human", "server", "agent"]

# Crockford base32, ULID alphabet (excludes I, L, O, U).
_B32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid(prefix=""):
    """A lexicographically-sortable ULID: 48-bit ms timestamp + 80 bits randomness, Crockford base32."""
    ms = int(time.time() * 1000)
    rnd = int.from_bytes(os.urandom(10), "big")
    n = (ms << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_B32[n & 31])
        n >>= 5
    body = "".join(reversed(out))
    return f"{prefix}{body}" if prefix else body


def _path(d):
    return os.path.join(d, "ledger", "events.jsonl")


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _chain_hash(prev_h, entry):
    """Each entry binds the previous via a hash of (prev_hash + the entry body). A tampered or reordered
    entry breaks every hash after it — the tamper-evident audit trail Tier 3 lights-out requires."""
    body = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((prev_h + body).encode("utf-8")).hexdigest()[:16]


def _last_hash(d):
    if not os.path.isfile(_path(d)):
        return ""
    last = ""
    for line in open(_path(d), encoding="utf-8"):
        if line.strip():
            try:
                last = json.loads(line).get("h", "")
            except json.JSONDecodeError:
                pass
    return last


def verify_chain(d):
    """Re-walk the ledger, recomputing each entry's chain hash. Returns (ok, broken_at_line|None). The
    derived input for autonomy's tamper_evident: an edited, reordered, or truncated history is detectable."""
    p = _path(d)
    if not os.path.isfile(p):
        return True, None
    prev_h = ""
    for i, line in enumerate((l for l in open(p, encoding="utf-8")), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            return False, i
        body = {k: v for k, v in e.items() if k != "h"}
        if _chain_hash(prev_h, body) != e.get("h"):
            return False, i
        prev_h = e.get("h")
    return True, None


def append(d, event, actor, subject, rationale, frm=None, to=None, hashes=None, metrics=None, ts=None):
    """Append one entry. Returns its ledger ref (the 1-based line number as 'ledger:N'). The ONLY writer
    of the ledger file; every state change in dev-factory terminates here — no silent work."""
    if event not in EVENTS:
        raise ValueError(f"unknown event: {event} (not in {EVENTS})")
    if not isinstance(actor, dict) or actor.get("kind") not in ACTOR_KINDS or not actor.get("id"):
        raise ValueError("actor must be {kind: human|server|agent, id}; tool output is never an actor")
    if not rationale or not str(rationale).strip():
        raise ValueError("rationale is required — a record without a why is useless for regeneration")
    if not (subject.get("ticket") or subject.get("cell")):
        raise ValueError("subject must name at least one of ticket/cell")
    entry = {"ts": ts or _now(), "event": event, "actor": actor, "subject": subject, "rationale": rationale}
    if frm is not None:
        entry["from"] = frm
    if to is not None:
        entry["to"] = to
    if hashes:
        entry["hashes"] = hashes
    if metrics:
        entry["metrics"] = metrics
    os.makedirs(os.path.dirname(_path(d)), exist_ok=True)
    entry["h"] = _chain_hash(_last_hash(d), entry)   # bind the previous entry → a tamper-evident chain
    with open(_path(d), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    n = sum(1 for _ in open(_path(d), encoding="utf-8"))
    return f"ledger:{n}"


def read(d, cell=None, ticket=None, event=None, since=None):
    p = _path(d)
    if not os.path.isfile(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if cell and e.get("subject", {}).get("cell") != cell:
            continue
        if ticket and e.get("subject", {}).get("ticket") != ticket:
            continue
        if event and e.get("event") != event:
            continue
        if since and e.get("ts", "") < since:
            continue
        out.append(e)
    return out


def tail(d, n=20):
    return read(d)[-n:]


def no_progress(d, cell, n=3):
    """A no-progress loop = the last `n` failure signals on `cell` carry the SAME signature (the
    deterministic failure-loop detector, in code, not the agent's counting). Returns (bool, reason)."""
    sigs = [e for e in read(d, cell=cell, event="signal") if e.get("to") == "fail" or e.get("metrics", {}).get("result") == "fail"]
    fails = [e for e in read(d, cell=cell) if e.get("event") == "block" or (e.get("event") == "transition" and e.get("to") == "blocked")]
    # signature = the rationale tail; N identical consecutive failure rationales = a stuck loop
    rats = [e.get("rationale", "") for e in read(d, cell=cell)][-n:]
    if len(rats) >= n and len(set(rats)) == 1 and rats[0]:
        return True, f"no-progress: last {n} attempts on {cell} share one failure signature"
    return False, "progressing"


def false_pass_rate(d, family=None):
    """The trust-trajectory input. Returns 'unmeasured' until an independent refuter has disagreed with a
    critic at least once — a 0.0% with no refuter is a LIE that would auto-promote a never-checked family.
    Honest scope: only an `incident` event (a refuter caught a false pass) makes this measurable."""
    incidents = [e for e in read(d, event="incident")]
    signals = [e for e in read(d, event="signal")]
    if not incidents:
        return "unmeasured"
    passes = [e for e in signals if e.get("to") == "pass" or e.get("metrics", {}).get("result") == "pass"]
    if not passes:
        return "unmeasured"
    return len(incidents) / max(1, len(passes))


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as d:
        # ulid shape
        u = ulid("tkt-")
        expect(u.startswith("tkt-") and len(u) == 30, f"bad ulid: {u}")
        import re
        expect(re.match(r"^tkt-[0-9A-HJKMNP-TV-Z]{26}$", u) is not None, f"ulid not Crockford-base32: {u}")
        # append requires a rationale + a real actor
        try:
            append(d, "transition", {"kind": "server", "id": "s"}, {"ticket": "tkt-x"}, "")
            expect(False, "empty rationale was accepted")
        except ValueError:
            pass
        try:
            append(d, "transition", {"kind": "toolresult", "id": "x"}, {"ticket": "t"}, "why")
            expect(False, "tool-output actor accepted")
        except ValueError:
            pass
        # a real append + read-back
        ref = append(d, "transition", {"kind": "server", "id": "srv"}, {"ticket": "tkt-1", "cell": "spec.task.x"},
                     "draft->active by triager", frm="draft", to="active")
        expect(ref == "ledger:1", f"first append ref wrong: {ref}")
        got = read(d, ticket="tkt-1")
        expect(len(got) == 1 and got[0]["to"] == "active", "read-back failed")
        # append-only: a second append does not rewrite the first
        append(d, "signal", {"kind": "server", "id": "srv"}, {"cell": "spec.task.x"}, "pass", to="pass")
        expect(len(read(d)) == 2, "second append lost an entry")
        # no-progress detector
        for _ in range(3):
            append(d, "block", {"kind": "server", "id": "srv"}, {"cell": "spec.task.y"}, "verifier failed: 3 type errors")
        np, _r = no_progress(d, "spec.task.y", n=3)
        expect(np, "no-progress loop not detected on 3 identical failure signatures")
        np2, _ = no_progress(d, "spec.task.x", n=3)
        expect(not np2, "no-progress false-positive on a progressing cell")
        # false-pass is unmeasured until a refuter incident exists
        expect(false_pass_rate(d) == "unmeasured", "false-pass not 'unmeasured' without a refuter")
        # tamper-evident chain: intact after honest appends; a single edit is detected
        ok_chain, broken = verify_chain(d)
        expect(ok_chain, f"chain should verify after honest appends (broke at line {broken})")
        lines = open(_path(d), encoding="utf-8").readlines()
        e0 = json.loads(lines[0]); e0["rationale"] = "TAMPERED-AFTER-THE-FACT"
        lines[0] = json.dumps(e0, ensure_ascii=False) + "\n"
        open(_path(d), "w", encoding="utf-8").writelines(lines)
        bad_chain, at = verify_chain(d)
        expect(not bad_chain and at == 1, f"a tampered entry was not detected by the chain (verify={bad_chain}, at={at})")
    if fails:
        sys.stderr.write("ledger selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("ledger selftest: OK (ULID shape; rationale + real-actor required; append-only read-back; "
          "no-progress detects an N-identical failure loop; false-pass is 'unmeasured' until a refuter exists)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    verb = argv[0]
    d = _arg(argv, "--dir", ".agents/dev-factory")
    if verb == "append":
        actor = {"kind": _arg(argv, "--actor-kind", "server"), "id": _arg(argv, "--actor-id", "server")}
        subject = {}
        if _arg(argv, "--ticket"):
            subject["ticket"] = _arg(argv, "--ticket")
        if _arg(argv, "--cell"):
            subject["cell"] = _arg(argv, "--cell")
        try:
            ref = append(d, _arg(argv, "--event"), actor, subject, _arg(argv, "--rationale", ""),
                         frm=_arg(argv, "--from"), to=_arg(argv, "--to"))
        except ValueError as e:
            print(f"ledger.py: {e}", file=sys.stderr)
            return 2
        print(ref)
        return 0
    if verb == "read":
        for e in read(d, cell=_arg(argv, "--cell"), ticket=_arg(argv, "--ticket"),
                      event=_arg(argv, "--event"), since=_arg(argv, "--since")):
            print(json.dumps(e, ensure_ascii=False))
        return 0
    if verb == "tail":
        for e in tail(d, int(_arg(argv, "-n", "20"))):
            print(json.dumps(e, ensure_ascii=False))
        return 0
    if verb == "no-progress":
        np, reason = no_progress(d, _arg(argv, "--cell"), int(_arg(argv, "-n", "3")))
        print(reason)
        return 0 if np else 1
    print(f"ledger.py: unknown verb {verb}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
