#!/usr/bin/env python3
"""audit-history.py — producer/validator/liveness-checker for repo-ops's audit-history ledger.

repo-ops's Verify-Target criterion 4 ("audit ledger updated — entry appended to .brain/audit-history/")
and Promise-4 liveness ("a trip-wire-fired record within the dial's freshness window") are asserted in
prose with no enforcing mechanism on their own. This script is the missing harness — the trip-wire that
makes "self-healing" a checked property (a fresh, schema-valid ledger record) rather than a claim.

  validate <file>          — validate one audit-history record against the v1 schema
                             (references/audit-patterns/audit-history-ledger.md). Privacy warnings
                             (secret-shaped finding messages) are surfaced but do not fail.
  liveness --base <repo>    — is there an audit record within the Promise-4 freshness window?
                             LIVE / STALE TRIP-WIRE / MISSING TRIP-WIRE. Window from --strictness
                             (lax=90d normal=30d strict=8d, per guidance/reliability-dial.md) or
                             --window-days. --as-of YYYY-MM-DD makes "now" deterministic for tests.
  index --base <repo>       — regenerate .brain/audit-history/README.md (newest-first trend table).

Exit 0 = valid / live / indexed; 1 = invalid or stale/missing; 2 = bad invocation.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

SEVERITIES = {"critical", "high", "medium", "low"}
STRICTNESS = {"lax", "normal", "strict"}
LIVENESS_WINDOW_DAYS = {"lax": 90, "normal": 30, "strict": 8}  # Promise-4 row of the dial resolver
_ISO = "%Y-%m-%dT%H:%M:%SZ"

# Finding-message privacy hazards (warn, never store secrets/PII in the ledger).
_SECRET = re.compile(r"https?://[^\s)]+/[^\s)]+|sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}"
                     r"|\b(api[_-]?key|secret|password|token)\b\s*[:=]", re.I)

_TOP = {"audit_id": str, "repo": str, "commit": str, "strictness": str, "skill_version": str,
        "promises_evaluated": list, "findings": list,
        "fixes_proposed": int, "fixes_applied": int, "fixes_vetoed": int, "trip_wires": dict}
_FIND = {"id": str, "promise": int, "severity": str, "category": str, "file": str, "message": str}


def _is(v, t):
    return isinstance(v, t) and not (t is int and isinstance(v, bool))


def validate_record(obj) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Empty errors == valid."""
    errs, warns = [], []
    if not isinstance(obj, dict):
        return ["record is not a JSON object"], warns

    for f, t in _TOP.items():
        if f not in obj:
            errs.append(f"missing required field '{f}'")
        elif not _is(obj[f], t):
            errs.append(f"field '{f}' must be {t.__name__}, got {type(obj[f]).__name__}")

    if isinstance(obj.get("audit_id"), str):
        try:
            datetime.strptime(obj["audit_id"], _ISO)
        except ValueError:
            errs.append(f"audit_id '{obj['audit_id']}' is not ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    if isinstance(obj.get("strictness"), str) and obj["strictness"] not in STRICTNESS:
        errs.append(f"strictness '{obj['strictness']}' not in {sorted(STRICTNESS)}")
    if isinstance(obj.get("promises_evaluated"), list):
        bad = [p for p in obj["promises_evaluated"] if not (_is(p, int) and 1 <= p <= 5)]
        if bad:
            errs.append(f"promises_evaluated has out-of-range entries {bad} (must be ints 1..5)")

    for i, fnd in enumerate(obj.get("findings", []) if isinstance(obj.get("findings"), list) else []):
        if not isinstance(fnd, dict):
            errs.append(f"findings[{i}] is not an object")
            continue
        for f, t in _FIND.items():
            if f not in fnd:
                errs.append(f"findings[{i}] missing '{f}'")
            elif not _is(fnd[f], t):
                errs.append(f"findings[{i}].{f} must be {t.__name__}")
        if isinstance(fnd.get("severity"), str) and fnd["severity"] not in SEVERITIES:
            errs.append(f"findings[{i}].severity '{fnd['severity']}' not in {sorted(SEVERITIES)}")
        if _is(fnd.get("promise"), int) and not 1 <= fnd["promise"] <= 5:
            errs.append(f"findings[{i}].promise {fnd['promise']} out of range (1..5)")
        if isinstance(fnd.get("message"), str) and _SECRET.search(fnd["message"]):
            warns.append(f"findings[{i}].message looks secret/PII-shaped — store categories, not content")
    return errs, warns


def _records(base):
    """Yield (date, path, obj) for each parseable audit-history JSON, newest first."""
    out = []
    for p in glob.glob(os.path.join(base, ".brain", "audit-history", "*.json")):
        try:
            o = json.load(open(p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        stamp = o.get("audit_id") or os.path.basename(p)[:10]
        out.append((stamp[:10], p, o))
    return sorted(out, reverse=True)


def cmd_validate(args) -> int:
    try:
        obj = json.load(open(args.file, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"INVALID: cannot read/parse {args.file} — {e}", file=sys.stderr)
        return 1
    errs, warns = validate_record(obj)
    for w in warns:
        print(f"  [warn] {w}", file=sys.stderr)
    if errs:
        print("INVALID:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    n = len(obj.get("findings", []))
    print(f"VALID: {obj['audit_id']} — {n} finding(s), strictness={obj['strictness']}")
    return 0


def cmd_liveness(args) -> int:
    window = args.window_days if args.window_days is not None else LIVENESS_WINDOW_DAYS[args.strictness]
    recs = _records(args.base)
    if not recs:
        print(f"MISSING TRIP-WIRE: no audit-history record under {args.base}/.brain/audit-history/ "
              f"— presence without liveness is clean-by-luck, not self-healing.", file=sys.stderr)
        return 1
    now = datetime.strptime(args.as_of, "%Y-%m-%d") if args.as_of else datetime.now(timezone.utc).replace(tzinfo=None)
    newest_date, newest_path, _ = recs[0]
    age = (now - datetime.strptime(newest_date, "%Y-%m-%d")).days
    if age <= window:
        print(f"LIVE: most recent audit {newest_date} ({age}d ago) within the {args.strictness} "
              f"window ({window}d) — {os.path.relpath(newest_path, args.base)}")
        return 0
    print(f"STALE TRIP-WIRE: most recent audit {newest_date} ({age}d ago) exceeds the {args.strictness} "
          f"window ({window}d) — the self-healing promise is unproven (clean-by-luck, not self-healing).",
          file=sys.stderr)
    return 1


def cmd_index(args) -> int:
    recs = _records(args.base)
    if not recs:
        print(f"no audit-history under {args.base}/.brain/audit-history/", file=sys.stderr)
        return 1
    rows = []
    for date, path, o in recs:
        n = len(o.get("findings", []))
        crit = sum(1 for f in o.get("findings", []) if isinstance(f, dict) and f.get("severity") == "critical")
        rows.append(f"| [{date}]({os.path.basename(path)}) | {o.get('strictness', '?')} | {n} | {crit} | {o.get('fixes_applied', 0)} |")
    out = ["# Audit history", "", "| Date | Strictness | Findings | Critical | Fixes applied |",
           "|---|---|---|---|---|"] + rows + [""]
    readme = os.path.join(args.base, ".brain", "audit-history", "README.md")
    open(readme, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"INDEXED {len(rows)} audit(s) -> {readme}")
    return 0


def cmd_selftest(args) -> int:
    """Prove the validator accepts a good record and rejects malformed ones (CI regression guard)."""
    good = {"audit_id": "2026-05-11T13:42:00Z", "repo": "r", "commit": "c", "strictness": "normal",
            "skill_version": "1.15.0", "promises_evaluated": [1, 2, 3, 4, 5],
            "findings": [{"id": "X", "promise": 1, "severity": "critical", "category": "redundancy",
                          "file": "CLAUDE.md", "message": "divergent content"}],
            "fixes_proposed": 1, "fixes_applied": 1, "fixes_vetoed": 0, "trip_wires": {"lychee": "pass"}}
    bads = [
        {**good, "strictness": "paranoid"},                                        # bad strictness
        {**good, "promises_evaluated": [1, 7]},                                     # out-of-range promise
        {k: v for k, v in good.items() if k != "commit"},                          # missing top field
        {**good, "findings": [{**good["findings"][0], "severity": "catastrophic"}]},  # bad severity
    ]
    failures = []
    if validate_record(good)[0]:
        failures.append("rejected a valid record")
    for i, b in enumerate(bads):
        if not validate_record(b)[0]:
            failures.append(f"accepted malformed case #{i}")
    # the privacy warning must fire (warn, not error) on a secret-shaped message
    leak = {**good, "findings": [{**good["findings"][0], "message": "link to https://x.io/secret/k.pdf"}]}
    errs, warns = validate_record(leak)
    if errs or not warns:
        failures.append("privacy warning did not fire as a non-fatal warning")
    if failures:
        print("SELFTEST FAIL: " + "; ".join(failures), file=sys.stderr)
        return 1
    print(f"SELFTEST OK: accepts the valid record, rejects {len(bads)} malformed cases, warns on secret-shaped messages")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="audit-history.py", description="Validate / liveness-check / index repo-ops's audit-history ledger.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("selftest", help="prove the validator accepts good / rejects bad (CI guard)")
    st.set_defaults(fn=cmd_selftest)
    v = sub.add_parser("validate", help="validate one audit-history record against the v1 schema")
    v.add_argument("file")
    v.set_defaults(fn=cmd_validate)
    l = sub.add_parser("liveness", help="is the most recent audit within the Promise-4 freshness window?")
    l.add_argument("--base", required=True, help="repo root (ledger lives in <base>/.brain/audit-history/)")
    l.add_argument("--strictness", choices=sorted(STRICTNESS), default="normal")
    l.add_argument("--window-days", type=int, default=None, help="override the dial window")
    l.add_argument("--as-of", default=None, help="treat this YYYY-MM-DD as 'now' (deterministic tests)")
    l.set_defaults(fn=cmd_liveness)
    i = sub.add_parser("index", help="regenerate the human README trend table")
    i.add_argument("--base", required=True)
    i.set_defaults(fn=cmd_index)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
