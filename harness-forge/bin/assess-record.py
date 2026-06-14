#!/usr/bin/env python3
"""assess-record.py — emit + validate a durable /harness-assess PROPOSAL record (I-15).

`/harness-assess` surveys an existing project and RECOMMENDS how to seed the lattice — which weak/absent
layer is the frontier, the smallest scope that yields signal, a real verifier command, whether to wire.
Without a durable artifact that recommendation evaporates into the chat (self-red-team, Charity M.): you
can't later diff "what assess PROPOSED" against "what got SEEDED". This writes the recommendation to
`.agents/harness/assess/<slug>.json` — validated, so every record is well-formed by construction rather
than the model hand-writing JSON (the parallel to plugins-factory's `scores/` D8 audit trail, I-15).

HONEST SCOPE — this is a PROPOSAL, never live lattice state:
  * It records the MODEL's judgment (the recommendation), not earned verifier signal.
  * It lives under `.agents/harness/assess/`, DELIBERATELY OUTSIDE gate-signal's protected perimeter
    (signals/ rubric/ ledger/ run/ lattice.json …) — a proposal is freely (re-)writable; a re-assess
    overwrites its own proposal. A `gate-signal` selftest negative-case locks that non-protection in.
  * The kernel never reads `assess/` — `lattice.py` computes state from `lattice.json`, full stop. A
    proposal sitting beside it changes nothing the engine/compass/loop does.
  * `record_type`/`status` are const-VALIDATED, so a record that fails to announce itself as a PROPOSAL
    is refused. It is committed (NOT run/-ignored) so the proposal-vs-seed diff survives.

A record:
  {
    "record_type": "harness-assess-proposal", "status": "PROPOSAL", "_note": "...",
    "project": "<name>", "root": "/abs/path", "intent": "develop-this" | "operate-on-this",
    "survey": { "stack": {...}, "layers": {layer: {"strength": "strong|incidental|none", "evidence": [...]}},
                "survey_caveat": "..." },
    "recommendation": {
      "first_slice": "<the first thin job + checkable acceptance>",
      "frontier_layer": "policy", "scope": "task",
      "mature_layers": ["ontology", "rubric", "capability"],
      "verifier_command": "npm test", "frontier_order": ["policy", "methodology"],
      "wire": true, "seed_command": "/harness-seed \"...\""
    },
    "proposed_at": "2026-06-14T10:30:00-07:00", "proposed_by": "harness-forge /harness-assess"
  }

Usage:
  assess-record.py write <project> --root <dir> --slice "<first slice>" --frontier <layer> --scope <scope>
                   --verifier "<cmd>" [--intent develop-this] [--mature l1,l2] [--frontier-order l1,l2]
                   [--wire] [--seed-command "..."] [--survey-json <path|->] [--by "..."] [--at <iso>] [--dir <dir>]
  assess-record.py validate <file.json>     # validate an existing proposal against the shape
  assess-record.py selftest                 # round-trip a valid proposal + reject the malformed shapes

Exit 0 = written / valid; 1 = invalid; 2 = usage error. Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import lattice as _lat  # noqa: E402 — sibling kernel module: the canonical LAYERS/SCOPES enums (single source, no drift)

LAYERS = set(_lat.LAYERS)
SCOPES = set(_lat.SCOPES)
STRENGTHS = {"strong", "incidental", "none"}          # survey.py's I-14 signal-strength vocab (NOT a PRESENT/ABSENT verdict)
INTENTS = {"develop-this", "operate-on-this"}         # /harness-assess step 3: develop THIS project vs build a capability that OPERATES ON it
RECORD_TYPE = "harness-assess-proposal"
STATUS = "PROPOSAL"
_NOTE = ("PROPOSAL — not live lattice state. A read-only record of what /harness-assess recommended; the lattice is "
         "seeded by /harness-seed and lives in lattice.json. Diff this against the seed to see what changed.")
_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def _now():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")   # the harness timestamp convention


def _slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return s or "project"


def validate(rec):
    """Return a list of error strings; empty == valid. Const-checks the PROPOSAL markers + enum-checks every
    layer/scope/strength/intent against the kernel's vocab — a malformed proposal is REFUSED, never written."""
    errs = []
    if not isinstance(rec, dict):
        return ["record is not a JSON object"]
    if rec.get("record_type") != RECORD_TYPE:
        errs.append(f"`record_type` must be the constant {RECORD_TYPE!r}")
    if rec.get("status") != STATUS:
        errs.append(f"`status` must be the constant {STATUS!r} (this is a proposal, not live lattice state)")
    if not isinstance(rec.get("project"), str) or not rec.get("project", "").strip():
        errs.append("`project` must be a non-empty string")
    if not isinstance(rec.get("root"), str) or not rec.get("root", "").strip():
        errs.append("`root` must be a non-empty string (the surveyed project path)")
    if rec.get("intent") not in INTENTS:
        errs.append(f"`intent` must be one of {sorted(INTENTS)}")
    surv = rec.get("survey")
    if not isinstance(surv, dict):
        errs.append("`survey` must be an object")
    else:
        layers = surv.get("layers")
        if not isinstance(layers, dict) or set(layers) != LAYERS:
            errs.append(f"`survey.layers` must cover exactly the nine layers {sorted(LAYERS)}")
        else:
            for lyr, cell in layers.items():
                if not isinstance(cell, dict) or cell.get("strength") not in STRENGTHS:
                    errs.append(f"survey.layers[{lyr!r}].strength must be one of {sorted(STRENGTHS)}")
                elif not isinstance(cell.get("evidence"), list):
                    errs.append(f"survey.layers[{lyr!r}].evidence must be a list")
    rc = rec.get("recommendation")
    if not isinstance(rc, dict):
        errs.append("`recommendation` must be an object")
    else:
        if not isinstance(rc.get("first_slice"), str) or not rc.get("first_slice", "").strip():
            errs.append("recommendation.first_slice must be a non-empty string")
        if rc.get("frontier_layer") not in LAYERS:
            errs.append(f"recommendation.frontier_layer must be one of {sorted(LAYERS)}")
        if rc.get("scope") not in SCOPES:
            errs.append(f"recommendation.scope must be one of {sorted(SCOPES)}")
        if not isinstance(rc.get("verifier_command"), str) or not rc.get("verifier_command", "").strip():
            errs.append("recommendation.verifier_command must be a non-empty string (a REAL exit-coded command)")
        ml = rc.get("mature_layers")
        if not isinstance(ml, list) or any(m not in LAYERS for m in ml):
            errs.append(f"recommendation.mature_layers must be a list ⊆ {sorted(LAYERS)}")
        fo = rc.get("frontier_order")
        if not isinstance(fo, list) or any(m not in LAYERS for m in fo):
            errs.append(f"recommendation.frontier_order must be a list ⊆ {sorted(LAYERS)}")
        if not isinstance(rc.get("wire"), bool):
            errs.append("recommendation.wire must be a boolean")
    if not isinstance(rec.get("proposed_at"), str) or not _TS_RE.match(rec.get("proposed_at", "")):
        errs.append("`proposed_at` must be an ISO-8601 timestamp")
    if not isinstance(rec.get("proposed_by"), str) or not rec.get("proposed_by", "").strip():
        errs.append("`proposed_by` must be a non-empty string")
    return errs


def _flag(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def _list(spec):
    return [t.strip() for t in (spec or "").split(",") if t.strip()]


def _harness_dir():
    return os.environ.get("HARNESS_DIR") or ".agents/harness"


_FLAGS = ("--root", "--slice", "--frontier", "--scope", "--verifier", "--intent",
          "--mature", "--frontier-order", "--seed-command", "--survey-json", "--by", "--at", "--dir")


def cmd_write(argv):
    # derive the project name as the first non-flag token that isn't a flag VALUE (mirrors score-record.py)
    flag_vals = set()
    for fn in _FLAGS:
        if fn in argv and argv.index(fn) + 1 < len(argv):
            flag_vals.add(id(argv[argv.index(fn) + 1]))
    names = [a for a in argv[1:] if not a.startswith("--") and id(a) not in flag_vals]
    if not names:
        print("usage: assess-record.py write <project> --root <dir> --slice ... --frontier <layer> --scope <scope> --verifier <cmd>", file=sys.stderr)
        return 2
    project = names[0]
    root = _flag(argv, "--root", ".")
    # the survey half: a passed-in blob (--survey-json path|-) or run survey(root) now
    sj = _flag(argv, "--survey-json")
    try:
        if sj:
            blob = sys.stdin.read() if sj == "-" else open(sj, encoding="utf-8").read()
            surv = json.loads(blob)
        else:
            import survey as _survey
            surv = _survey.survey(root)
    except (OSError, ValueError) as e:
        print(f"RESULT: INVALID — could not obtain survey: {e}", file=sys.stderr)
        return 1
    slice_txt = _flag(argv, "--slice", "")
    rec = {
        "record_type": RECORD_TYPE,
        "status": STATUS,
        "_note": _NOTE,
        "project": project,
        "root": os.path.abspath(root),
        "intent": _flag(argv, "--intent", "develop-this"),
        "survey": {
            "stack": surv.get("stack", {}),
            "layers": surv.get("layers", {}),                 # already the {strength, evidence} shape post-I-14
            "survey_caveat": surv.get("_caveat", ""),
        },
        "recommendation": {
            "first_slice": slice_txt,
            "frontier_layer": _flag(argv, "--frontier", ""),
            "scope": _flag(argv, "--scope", ""),
            "mature_layers": _list(_flag(argv, "--mature")),
            "verifier_command": _flag(argv, "--verifier", ""),
            "frontier_order": _list(_flag(argv, "--frontier-order")),
            "wire": "--wire" in argv,
            "seed_command": _flag(argv, "--seed-command", f'/harness-seed "{project} — {slice_txt or "<first slice>"}"'),
        },
        "proposed_at": _flag(argv, "--at") or _now(),
        "proposed_by": _flag(argv, "--by", "harness-forge /harness-assess"),
    }
    errs = validate(rec)
    if errs:
        print("RESULT: INVALID — record failed validation:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    outdir = _flag(argv, "--dir") or os.path.join(_harness_dir(), "assess")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{_slug(project)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    r = rec["recommendation"]
    print(f"RESULT: WROTE {path} (PROPOSAL — frontier={r['frontier_layer']}.{r['scope']}, wire={r['wire']})")
    return 0


def cmd_validate(path):
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"RESULT: INVALID — cannot read {path}: {e}", file=sys.stderr)
        return 1
    errs = validate(rec)
    if errs:
        print(f"RESULT: INVALID — {path}:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    r = rec["recommendation"]
    print(f"RESULT: VALID — {path} ({rec['project']}: PROPOSAL frontier={r['frontier_layer']}.{r['scope']}, wire={r['wire']})")
    return 0


def cmd_selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    good = {
        "record_type": RECORD_TYPE, "status": STATUS, "_note": _NOTE,
        "project": "demo", "root": "/abs/demo", "intent": "develop-this",
        "survey": {
            "stack": {"languages": {"Python": 5}, "manifests": ["pyproject.toml"]},
            "layers": {l: {"strength": "none", "evidence": []} for l in LAYERS},
            "survey_caveat": "heuristic",
        },
        "recommendation": {
            "first_slice": "parse one invoice → typed record",
            "frontier_layer": "spec", "scope": "task",
            "mature_layers": ["ontology", "capability"],
            "verifier_command": "pytest tests/ -q",
            "frontier_order": ["spec", "rubric"],
            "wire": True, "seed_command": '/harness-seed "demo — parse"',
        },
        "proposed_at": "2026-06-14T10:30:00-07:00", "proposed_by": "harness-forge /harness-assess",
    }
    expect(validate(good) == [], f"valid proposal rejected: {validate(good)}")
    # each malformed shape must be caught (well-formed by construction)
    expect(validate({**good, "record_type": "scorecard"}) != [], "wrong record_type not caught")
    expect(validate({**good, "status": "LIVE"}) != [], "non-PROPOSAL status not caught (must announce itself)")
    expect(validate({**good, "project": ""}) != [], "empty project not caught")
    expect(validate({**good, "intent": "whatever"}) != [], "bad intent not caught")
    bad_layers = {**good, "survey": {**good["survey"], "layers": {"ontology": {"strength": "strong", "evidence": []}}}}
    expect(validate(bad_layers) != [], "incomplete nine-layer survey not caught")
    bad_strength = {**good, "survey": {**good["survey"],
                    "layers": {**{l: {"strength": "none", "evidence": []} for l in LAYERS},
                               "spec": {"strength": "PRESENT", "evidence": []}}}}
    expect(validate(bad_strength) != [], "a verdict-word strength (the old PRESENT) not caught")
    expect(validate({**good, "recommendation": {**good["recommendation"], "frontier_layer": "bogus"}}) != [], "frontier_layer outside the nine not caught")
    expect(validate({**good, "recommendation": {**good["recommendation"], "scope": "galaxy"}}) != [], "scope outside the five not caught")
    expect(validate({**good, "recommendation": {**good["recommendation"], "mature_layers": ["ontology", "nope"]}}) != [], "mature_layers with a non-layer not caught")
    expect(validate({**good, "recommendation": {**good["recommendation"], "wire": "yes"}}) != [], "non-bool wire not caught")
    expect(validate({**good, "recommendation": {**good["recommendation"], "verifier_command": ""}}) != [], "empty verifier_command not caught")
    expect(validate({**good, "proposed_at": "June 14"}) != [], "non-ISO proposed_at not caught")
    # round-trip through write → validate (suppress stdout — selftest output stays clean)
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "README.md"), "w").write("# demo")     # a tiny project to survey
        _stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            rc = cmd_write(["write", "Demo Project", "--root", tmp, "--slice", "first thin slice",
                            "--frontier", "policy", "--scope", "task", "--verifier", "pytest -q",
                            "--mature", "ontology,capability", "--frontier-order", "policy,methodology",
                            "--wire", "--at", "2026-06-14T10:30:00-07:00", "--dir", os.path.join(tmp, "assess")])
            written = os.path.join(tmp, "assess", "demo-project.json")
            valid_rc = cmd_validate(written) if os.path.isfile(written) else 1
        finally:
            sys.stdout.close()
            sys.stdout = _stdout
        expect(rc == 0, "write of a valid proposal did not succeed")
        expect(os.path.isfile(written), "write did not create the slugged file")
        expect(valid_rc == 0, "round-tripped proposal failed validate")
        back = json.load(open(written))
        expect(back["status"] == "PROPOSAL" and back["record_type"] == RECORD_TYPE, "round-trip lost the PROPOSAL markers")
        expect(set(back["survey"]["layers"]) == LAYERS, "round-trip lost the nine-layer survey")
        expect(back["recommendation"]["wire"] is True, "round-trip lost the wire bool")

    if fails:
        sys.stderr.write("assess-record selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("assess-record selftest: OK (validates the PROPOSAL shape; const-checks record_type/status so a record must "
          "announce itself as a proposal; enum-checks intent/strength/frontier/scope/mature against the kernel vocab; "
          "rejects an incomplete nine-layer survey + a verdict-word strength + a non-bool wire; write→validate round-trips)")
    return 0


def main(argv):
    if len(argv) == 1 and argv[0] == "selftest":
        return cmd_selftest()
    if argv and argv[0] == "write":
        return cmd_write(argv)
    if len(argv) == 2 and argv[0] == "validate":
        return cmd_validate(argv[1])
    print(__doc__.split("Usage:")[1].split("Exit 0")[0].strip() if "Usage:" in __doc__ else "usage error", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
