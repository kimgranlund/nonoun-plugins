#!/usr/bin/env python3
"""score-record.py — emit + validate a durable plugin score record (the D8 audit trail, I-13).

The judge half (`plugin-evaluate` → `score`/`promote`) produces a 9-dimension scorecard and a verdict.
Without a durable artifact that judgment evaporates into the chat transcript (self-red-team, Charity M.
Critical): no regression diff, no record that a plugin was ever certified, `empirical_applications: 0`.
This writes the scorecard to `scores/<plugin>.json` in the exact structure `rubric-manifest.json`'s
`adoption_contract` specifies — validated, so every emitted record is well-formed rather than the model
hand-writing JSON (the hopeful-instruction failure mode the council exists to catch).

A record:
  {
    "plugin": "<name>",
    "rubrics_adopted": ["plugins-holistic/v0.1.0"],
    "scores": { "plugins-holistic/v0.1.0": { "P1-plugin-fitness": 3, ..., "P9-security-trust": 2 } },
    "verdict": "APPROVED" | "CONDITIONAL" | "BLOCKED",   (optional)
    "review": "reviews/<file>.md",                        (optional — the prose record this summarizes)
    "last_scored": "YYYY-MM-DD",
    "scored_by": "<who>"
  }

Durable location: in-repo the audit trail is `plugins-factory/scores/`; for an INSTALLED run, write under
`${CLAUDE_PLUGIN_DATA}` (survives a plugin version bump) or the target repo — never the version-keyed
cache root (self-red-team, Charity M. m5). `--dir` selects the destination.

Usage:
  score-record.py write <plugin> --scores P1=3,P2=3,...,P9=2 [--rubric plugins-holistic/v0.1.0]
                  [--verdict CONDITIONAL] [--review reviews/x.md] [--by plugins-factory]
                  [--date YYYY-MM-DD] [--dir <scores-dir>]
  score-record.py validate <file.json>      # validate an existing record against the schema
  score-record.py selftest                  # round-trip a valid record + reject the malformed shapes

Exit 0 = written / valid; 1 = invalid; 2 = usage error. Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

# Per-rubric dimension vocabularies — shorthand (P1 / D1) → the canonical key the adoption_contract uses.
# Keyed by rubric FAMILY (the part before /vX.Y.Z) so a record's dimensions are validated against the rubric
# it actually adopts: a holistic record carries P1..P9, a carve-quality record carries D1..D7. A record that
# scores a holistic plugin with a carve dimension (or vice versa) is then rejected by construction.
DIM_SETS = {
    "plugins-holistic": {
        "P1": "P1-plugin-fitness", "P2": "P2-component-fit", "P3": "P3-boundary-cohesion",
        "P4": "P4-dependency-legality", "P5": "P5-manifest-packaging", "P6": "P6-context-economy",
        "P7": "P7-routing-discoverability", "P8": "P8-evolution-maintenance", "P9": "P9-security-trust",
    },
    "carve-quality": {
        "D1": "D1-graph-fidelity", "D2": "D2-cuts-at-joints", "D3": "D3-shared-infra-legality",
        "D4": "D4-dependency-graph-integrity", "D5": "D5-node-accounting",
        "D6": "D6-granularity-calibration", "D7": "D7-buildable-proposal",
    },
}
DIMS = DIM_SETS["plugins-holistic"]   # back-compat: the default rubric's shorthand map
CANON = set(DIMS.values())            # back-compat alias (the holistic canon)


def _family(rid):
    """The rubric family — the part before '/vX.Y.Z' — used to pick the dimension vocabulary."""
    return rid.split("/", 1)[0]


def _canon_for(rid):
    """The set of canonical dimension keys legal for rubric `rid`, or None if its family is unknown."""
    dims = DIM_SETS.get(_family(rid))
    return set(dims.values()) if dims else None
VERDICTS = {"APPROVED", "CONDITIONAL", "BLOCKED", "ship", "fix-then-ship", "rebuild"}
_RUBRIC_RE = re.compile(r"^[a-z0-9-]+/v\d+\.\d+\.\d+$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(os.path.dirname(HERE), "scores")  # plugins-factory/scores/


def validate(rec):
    """Return a list of error strings; empty list == valid."""
    errs = []
    if not isinstance(rec, dict):
        return ["record is not a JSON object"]
    if not isinstance(rec.get("plugin"), str) or not rec.get("plugin", "").strip():
        errs.append("`plugin` must be a non-empty string")
    adopted = rec.get("rubrics_adopted")
    if not isinstance(adopted, list) or not adopted:
        errs.append("`rubrics_adopted` must be a non-empty list")
        adopted = adopted if isinstance(adopted, list) else []
    for r in adopted:
        if not isinstance(r, str) or not _RUBRIC_RE.match(r):
            errs.append(f"rubric id {r!r} must look like 'name/vX.Y.Z'")
    scores = rec.get("scores")
    if not isinstance(scores, dict) or not scores:
        errs.append("`scores` must be a non-empty object keyed by rubric id")
        scores = scores if isinstance(scores, dict) else {}
    for rid, dims in scores.items():
        if rid not in adopted:
            errs.append(f"scores reference rubric {rid!r} not in rubrics_adopted")
        canon = _canon_for(rid)
        if canon is None:
            errs.append(f"scores reference rubric {rid!r} of an unknown family (known: {sorted(DIM_SETS)})")
        if not isinstance(dims, dict) or not dims:
            errs.append(f"scores[{rid!r}] must be a non-empty object of dimension→1..5")
            continue
        for dkey, val in dims.items():
            if canon is not None and dkey not in canon:
                errs.append(f"scores[{rid!r}] has unknown dimension key {dkey!r} (expected one of {sorted(canon)})")
            if not isinstance(val, int) or isinstance(val, bool) or not (1 <= val <= 5):
                errs.append(f"scores[{rid!r}][{dkey!r}] = {val!r} must be an int 1..5")
    if "verdict" in rec and rec["verdict"] not in VERDICTS:
        errs.append(f"verdict {rec['verdict']!r} must be one of {sorted(VERDICTS)}")
    if not isinstance(rec.get("last_scored"), str) or not _DATE_RE.match(rec.get("last_scored", "")):
        errs.append("`last_scored` must be an ISO date 'YYYY-MM-DD'")
    if not isinstance(rec.get("scored_by"), str) or not rec.get("scored_by", "").strip():
        errs.append("`scored_by` must be a non-empty string")
    if "review" in rec and (not isinstance(rec["review"], str) or not rec["review"].strip()):
        errs.append("`review`, if present, must be a non-empty string path")
    return errs


def _parse_scores(spec, rubric):
    """'P1=3,P2=3,...' → {rubric: {canonical-dim: int}}. Raises ValueError on a bad token."""
    out = {}
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if "=" not in tok:
            raise ValueError(f"score token {tok!r} must be K=V (e.g. P1=3 or P6-context-economy=3)")
        k, v = tok.split("=", 1)
        k = k.strip()
        key = DIM_SETS.get(_family(rubric), DIMS).get(k.upper(), k)  # P1/D1 shorthand or a full canonical key
        try:
            out[key] = int(v.strip())
        except ValueError:
            raise ValueError(f"score for {k!r} must be an integer, got {v!r}")
    return {rubric: out}


def _flag(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def cmd_write(argv):
    pos = [a for a in argv if not a.startswith("--")]
    # pos[0] == 'write', pos[1] == plugin; flag VALUES are also non-'--' but consumed by _flag, so derive plugin as the
    # first non-'--' token that is not a flag value.
    flag_vals = set()
    for fn in ("--scores", "--rubric", "--verdict", "--review", "--by", "--date", "--dir"):
        if fn in argv and argv.index(fn) + 1 < len(argv):
            flag_vals.add(id(argv[argv.index(fn) + 1]))
    names = [a for a in argv[1:] if not a.startswith("--") and id(a) not in flag_vals]
    if not names:
        print("usage: score-record.py write <plugin> --scores P1=3,...", file=sys.stderr)
        return 2
    plugin = names[0]
    rubric = _flag(argv, "--rubric", "plugins-holistic/v0.1.0")
    scores_spec = _flag(argv, "--scores")
    if not scores_spec:
        print("write requires --scores P1=3,P2=3,...,P9=2", file=sys.stderr)
        return 2
    try:
        scores = _parse_scores(scores_spec, rubric)
    except ValueError as e:
        print(f"RESULT: INVALID — {e}", file=sys.stderr)
        return 1
    date = _flag(argv, "--date")
    if not date:
        import datetime
        date = datetime.date.today().isoformat()
    rec = {
        "plugin": plugin,
        "rubrics_adopted": [rubric],
        "scores": scores,
        "last_scored": date,
        "scored_by": _flag(argv, "--by", "plugins-factory"),
    }
    if _flag(argv, "--verdict"):
        rec["verdict"] = _flag(argv, "--verdict")
    if _flag(argv, "--review"):
        rec["review"] = _flag(argv, "--review")
    errs = validate(rec)
    if errs:
        print("RESULT: INVALID — record failed validation:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    outdir = _flag(argv, "--dir", DEFAULT_DIR)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{plugin}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print(f"RESULT: WROTE {path} (verdict={rec.get('verdict', 'n/a')}, {len(scores[rubric])} dims)")
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
    print(f"RESULT: VALID — {path} ({rec['plugin']}, verdict={rec.get('verdict', 'n/a')})")
    return 0


def cmd_selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    good = {
        "plugin": "demo", "rubrics_adopted": ["plugins-holistic/v0.1.0"],
        "scores": {"plugins-holistic/v0.1.0": {v: 3 for v in CANON}},
        "verdict": "CONDITIONAL", "review": "reviews/x.md",
        "last_scored": "2026-06-13", "scored_by": "plugins-factory",
    }
    expect(validate(good) == [], f"valid record rejected: {validate(good)}")
    # each malformed shape must be caught
    expect(validate({**good, "plugin": ""}) != [], "empty plugin not caught")
    expect(validate({**good, "scores": {"plugins-holistic/v0.1.0": {"P1-plugin-fitness": 9}}}) != [], "out-of-range score not caught")
    expect(validate({**good, "scores": {"plugins-holistic/v0.1.0": {"bogus-dim": 3}}}) != [], "unknown dimension not caught")
    expect(validate({**good, "scores": {"other/v1.0.0": {"P1-plugin-fitness": 3}}}) != [], "score for un-adopted rubric not caught")
    expect(validate({**good, "verdict": "MAYBE"}) != [], "bogus verdict not caught")
    expect(validate({**good, "last_scored": "June 13"}) != [], "non-ISO date not caught")
    expect(validate({**good, "rubrics_adopted": ["plugins-holistic"]}) != [], "rubric without version not caught")
    expect(validate({**good, "scores": {"plugins-holistic/v0.1.0": {"P1-plugin-fitness": True}}}) != [], "bool-as-score not caught")
    # shorthand parse
    parsed = _parse_scores("P1=3,P9=2", "plugins-holistic/v0.1.0")
    expect(parsed["plugins-holistic/v0.1.0"] == {"P1-plugin-fitness": 3, "P9-security-trust": 2}, f"shorthand parse wrong: {parsed}")
    # carve-quality (a second rubric family): a valid D1..D7 record validates, dimensions are rubric-aware
    carve = {
        "plugin": "demo-carve", "rubrics_adopted": ["carve-quality/v0.1.0"],
        "scores": {"carve-quality/v0.1.0": {v: 3 for v in DIM_SETS["carve-quality"].values()}},
        "verdict": "BLOCKED", "review": "reviews/x-carve.md",
        "last_scored": "2026-06-16", "scored_by": "plugins-factory",
    }
    expect(validate(carve) == [], f"valid carve record rejected: {validate(carve)}")
    # cross-rubric mismatch is caught BOTH ways (a holistic dim under carve-quality, a carve dim under holistic)
    expect(validate({**carve, "scores": {"carve-quality/v0.1.0": {"P1-plugin-fitness": 3}}}) != [], "holistic dim under carve-quality not caught")
    expect(validate({**good, "scores": {"plugins-holistic/v0.1.0": {"D1-graph-fidelity": 3}}}) != [], "carve dim under holistic not caught")
    # an unknown rubric family is caught
    expect(validate({**carve, "rubrics_adopted": ["mystery/v0.1.0"], "scores": {"mystery/v0.1.0": {"D1-graph-fidelity": 3}}}) != [], "unknown rubric family not caught")
    # carve shorthand parse (D1 → canonical)
    parsed_c = _parse_scores("D1=5,D6=2", "carve-quality/v0.1.0")
    expect(parsed_c["carve-quality/v0.1.0"] == {"D1-graph-fidelity": 5, "D6-granularity-calibration": 2}, f"carve shorthand parse wrong: {parsed_c}")
    # round-trip through write → validate (suppress their stdout reports — selftest output stays clean)
    with tempfile.TemporaryDirectory() as tmp:
        _stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            rc = cmd_write(["write", "demo", "--scores", ",".join(f"{p}=3" for p in DIMS), "--verdict", "APPROVED", "--date", "2026-06-13", "--dir", tmp])
            written = os.path.join(tmp, "demo.json")
            valid_rc = cmd_validate(written) if os.path.isfile(written) else 1
        finally:
            sys.stdout.close()
            sys.stdout = _stdout
        expect(rc == 0, "write of a valid record did not succeed")
        expect(os.path.isfile(written), "write did not create the file")
        expect(valid_rc == 0, "round-tripped record failed validate")
        back = json.load(open(written))
        expect(len(back["scores"]["plugins-holistic/v0.1.0"]) == 9, "round-trip lost dimensions")

    if fails:
        sys.stderr.write("score-record selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("score-record selftest: OK (validates the adoption_contract shape; rejects empty/out-of-range/"
          "unknown-dim/un-adopted-rubric/bad-verdict/bad-date/unversioned-rubric/bool-score; write→validate round-trips)")
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
