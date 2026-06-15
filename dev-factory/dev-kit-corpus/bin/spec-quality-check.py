#!/usr/bin/env python3
"""spec-quality-check.py — the REAL verifier the corpus spec adapter binds (rubric.system.spec-quality).

This is the mechanization of the spec-quality rubric's [gate] dimensions. validate.py runs it on a spec
cell's asset and mints the signal from its EXIT STATUS (0 = all gates pass). It runs ONLY the [gate]
dimensions — the [review] dimensions (intent-fidelity, boundary-completeness, …) are a calibrated critic's
job, not this script's. A spec asset is a structured spec (JSON, or JSON front-matter in a `.md`) declaring:

    acceptance_criteria : [ {id, check|rubric_cell} , ... ]   # zero prose-only criteria
    non_goals           : [ "..." , ... ]                     # explicit out-of-scope
    binds_rubric        : "rubric.<scope>.<slug>"             # the rubric this spec scores against
    decomposition?      : { parent:{criteria:[...]}, cells, tickets, edges }  # optional; entailment-checked

Gate dimensions enforced here:
  schema-valid              — parses; carries a heading/title + the structural keys; cell id excludes maturity
  criteria-checkable        — every acceptance criterion is executable or rubric-bound (zero prose-only)
  non-goals-present         — explicit non-goals declared
  rubric-binds              — binds_rubric points at a rubric.* cell
  decomposition-entailment  — when a decomposition is declared, _entailment_check.py passes

Usage:  spec-quality-check.py <asset-path>   |   spec-quality-check.py selftest
Exit 0 = all gates pass; 1 = a gate failed; 2 = bad invocation. Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _entailment_check  # noqa: E402  (promoted library: the decomposition-entailment gate)

_CELL_ID_RE = re.compile(
    r"^(ontology|spec|rubric|policy|capability|methodology|protocol|ledger|pattern)"
    r"\.(call|task|workflow|system|fleet)\.[a-z0-9]+(-[a-z0-9]+)*$"
)
_MATURITY = {"absent", "defined", "instantiated", "validated", "operating", "regenerating", "stale", "deprecated"}


def _resolve_asset(path):
    """A spec asset is a SKILL-format file (.md/.json), OR a folder whose `SKILL.md` is the spec (the rich
    SKILL-format shape — `spec/<slug>/SKILL.md` + references/)."""
    if path and os.path.isdir(path):
        return os.path.join(path, "SKILL.md")
    return path


def _frontmatter(raw):
    """Minimal YAML front-matter parse — the subset a SKILL-format spec uses (`key: value` + folded `>`
    blocks). Returns {} when there is no front-matter (a legacy json-only spec). Stdlib only, no yaml dep."""
    if not raw.lstrip().startswith("---"):
        return {}
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
    if not m:
        return {}
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_][\w-]*\s*:", line):
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip()
            fm[key] = "" if v in (">", "|") else v
        elif key and line.strip() and line[:1].isspace():
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def _load_spec(path):
    """Returns (contract, front-matter). The machine-readable contract is JSON, or the first fenced ```json
    block in a .md / SKILL.md — so a SKILL-format spec EMBEDS its contract in the skill body (one source of
    truth, no parallel artifact). A folder asset resolves to its SKILL.md."""
    raw = open(_resolve_asset(path), encoding="utf-8", errors="replace").read()
    fm = _frontmatter(raw)
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        return json.loads(raw), fm
    m = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        return json.loads(m.group(1)), fm
    raise ValueError("spec asset carries no structured spec (expected JSON or a ```json block) — "
                     "a prose-only spec cannot be mechanically gated")


def _gate_schema_valid(spec):
    if not isinstance(spec, dict):
        return False, "spec is not a JSON object"
    if not (spec.get("title") or spec.get("name") or spec.get("intent")):
        return False, "spec has no title/name/intent (not instantiable)"
    cell = spec.get("cell") or spec.get("id")
    if cell is not None:
        if not _CELL_ID_RE.match(str(cell)):
            return False, f"cell id {cell!r} is malformed (must be {{layer}}.{{scope}}.{{slug}})"
        if str(cell).split(".", 1)[0] != "spec":
            return False, f"cell id {cell!r} is not a spec.* cell (the spec-quality gate validates spec-layer cells only)"
        if str(cell).rsplit(".", 1)[-1] in _MATURITY:
            return False, f"cell id {cell!r} encodes maturity (identity must exclude state)"
    if not isinstance(spec.get("acceptance_criteria"), list):
        return False, "spec has no acceptance_criteria list"
    return True, "schema-valid"


def _gate_criteria_checkable(spec):
    crits = spec.get("acceptance_criteria") or []
    if not crits:
        return False, "no acceptance criteria (a spec with nothing to check cannot converge)"
    prose_only = []
    for c in crits:
        if isinstance(c, str):
            prose_only.append(c[:48])
            continue
        cid = c.get("id", "<unnamed>")
        executable = bool(c.get("check") or c.get("verifier") or c.get("executable"))
        rubric_bound = bool(c.get("rubric_cell") or c.get("rubric"))
        if not (executable or rubric_bound):
            prose_only.append(cid)
    if prose_only:
        return False, f"prose-only acceptance criteria (neither executable nor rubric-bound): {prose_only}"
    return True, f"all {len(crits)} acceptance criteria are executable or rubric-bound"


def _gate_non_goals_present(spec):
    ng = spec.get("non_goals")
    if not isinstance(ng, list) or not ng:
        return False, "no explicit non_goals declared (unbounded scope)"
    return True, f"{len(ng)} non-goals declared"


def _gate_rubric_binds(spec):
    rc = spec.get("binds_rubric") or spec.get("rubric_cell")
    if not rc:
        return False, "spec binds no rubric (binds_rubric missing) — it would score against vibes"
    if str(rc).split(".", 1)[0] != "rubric":
        return False, f"binds_rubric {rc!r} is not a rubric.* cell"
    return True, f"binds rubric {rc}"


def _gate_decomposition_entailment(spec):
    dec = spec.get("decomposition")
    if not dec:
        return True, "no decomposition declared (entailment gate not applicable)"
    parent = dec.get("parent") or {"criteria": [c.get("id") for c in spec.get("acceptance_criteria", [])
                                                 if isinstance(c, dict)]}
    proof = _entailment_check.check(parent, dec)
    if not proof["entailed"]:
        return False, "decomposition does not entail the parent: " + "; ".join(proof["gaps"])
    return True, (f"decomposition entails the parent "
                  f"({proof['criteria_covered']}/{proof['criteria_total']} criteria covered, "
                  f"{proof['tickets']} tickets)")


def _gate_skill_shape(spec, fm):
    """When a spec is authored in SKILL form (front-matter present), the skill surface and the machine
    contract must AGREE: `name` present, `description` present (the intent surface), and the contract `cell`'s
    slug == `name`. A legacy json-only spec (no front-matter) passes vacuously — valid but minimal; the
    spec-authoring guidance rubric is what pushes new specs to the full skill shape."""
    if not fm:
        return True, "json-only spec (no skill wrapper) — valid but minimal"
    if not fm.get("name"):
        return False, "SKILL-format spec front-matter has no `name`"
    if not fm.get("description"):
        return False, "SKILL-format spec front-matter has no `description` (the intent surface)"
    cell = spec.get("cell") or spec.get("id")
    if cell:
        slug = str(cell).rsplit(".", 1)[-1]
        if slug != fm["name"]:
            return False, f"skill `name` ({fm['name']!r}) disagrees with the contract cell slug ({slug!r})"
    return True, f"skill-shape: name={fm['name']!r}, intent surface present"


GATES = [
    ("schema-valid", _gate_schema_valid),
    ("criteria-checkable", _gate_criteria_checkable),
    ("rubric-binds", _gate_rubric_binds),
    ("non-goals-present", _gate_non_goals_present),
    ("decomposition-entailment", _gate_decomposition_entailment),
]


def check(path):
    """Run every [gate] dimension mechanically. Returns (ok, message)."""
    asset = _resolve_asset(path)
    if not asset or not os.path.isfile(asset):
        return False, f"no asset at {path!r}"
    try:
        spec, fm = _load_spec(path)
    except (json.JSONDecodeError, ValueError) as e:
        return False, f"schema-valid FAILED: {e}"
    failures = []
    passes = []
    for name, fn in GATES:
        ok, msg = fn(spec)
        (passes if ok else failures).append(f"{name}: {msg}")
    ok, msg = _gate_skill_shape(spec, fm)            # the skill surface ↔ contract agreement
    (passes if ok else failures).append(f"skill-shape: {msg}")
    if failures:
        return False, "GATE FAILURES — " + " | ".join(failures)
    return True, "all spec-quality gates pass — " + " | ".join(passes)


def selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    good = {
        "title": "User auth capability",
        "cell": "spec.system.user-auth",
        "acceptance_criteria": [
            {"id": "login-works", "check": "POST /login returns 200 for valid creds"},
            {"id": "rejects-bad", "rubric_cell": "rubric.system.test-suite"},
        ],
        "non_goals": ["password reset", "SSO"],
        "binds_rubric": "rubric.system.spec-quality",
        "decomposition": {
            "parent": {"criteria": ["login-works", "rejects-bad"]},
            "cells": [{"id": "spec.task.login"}, {"id": "spec.task.reject"}],
            "tickets": [
                {"target_cell": "spec.task.login", "acceptance": {"rubric_cell": "rubric.task.login"}, "covers": ["login-works"]},
                {"target_cell": "spec.task.reject", "acceptance": {"rubric_cell": "rubric.task.reject"}, "covers": ["rejects-bad"]},
            ],
            "edges": [],
        },
    }
    with tempfile.TemporaryDirectory() as d:
        gpath = os.path.join(d, "good.json")
        json.dump(good, open(gpath, "w"))
        ok, msg = check(gpath)
        expect(ok, f"rejected a sound spec: {msg}")

        # prose-only criterion -> criteria-checkable fails
        prose = json.loads(json.dumps(good))
        prose["acceptance_criteria"] = [{"id": "fast", "note": "it should feel fast"}]
        prose.pop("decomposition")  # avoid the entailment gate masking the criteria gate
        ppath = os.path.join(d, "prose.json")
        json.dump(prose, open(ppath, "w"))
        ok, msg = check(ppath)
        expect(not ok and "criteria-checkable" in msg, f"accepted a prose-only criterion: {msg}")

        # no non_goals -> non-goals-present fails
        nong = json.loads(json.dumps(good))
        nong.pop("non_goals")
        npath = os.path.join(d, "nong.json")
        json.dump(nong, open(npath, "w"))
        ok, msg = check(npath)
        expect(not ok and "non-goals-present" in msg, f"accepted a spec with no non-goals: {msg}")

        # no rubric binding -> rubric-binds fails
        norub = json.loads(json.dumps(good))
        norub.pop("binds_rubric")
        rpath = os.path.join(d, "norub.json")
        json.dump(norub, open(rpath, "w"))
        ok, msg = check(rpath)
        expect(not ok and "rubric-binds" in msg, f"accepted a spec binding no rubric: {msg}")

        # unsound decomposition (uncovered criterion) -> decomposition-entailment fails
        unsound = json.loads(json.dumps(good))
        unsound["decomposition"]["tickets"] = unsound["decomposition"]["tickets"][:1]
        upath = os.path.join(d, "unsound.json")
        json.dump(unsound, open(upath, "w"))
        ok, msg = check(upath)
        expect(not ok and "decomposition-entailment" in msg, f"accepted an unsound decomposition: {msg}")

        # prose-only .md spec (no structured block) -> schema-valid fails
        mdpath = os.path.join(d, "prose.md")
        open(mdpath, "w").write("# A prose spec\n\nWords, but no machine-checkable structure.\n")
        ok, msg = check(mdpath)
        expect(not ok and "schema-valid" in msg, f"accepted a prose-only .md spec: {msg}")

        # missing asset -> fail
        expect(not check(os.path.join(d, "missing.json"))[0], "accepted a missing asset")

        # a SKILL-format spec (front-matter + brief + the embedded contract block) -> passes (incl. skill-shape)
        contract = json.dumps({k: good[k] for k in good if k != "decomposition"}, indent=2)
        skill_md = ("---\n"
                    "name: user-auth\n"
                    "description: >\n"
                    "  Username/password auth: a valid login succeeds, a bad one is rejected. Scope: the\n"
                    "  credential check; NOT password reset or SSO.\n"
                    "---\n\n"
                    "# user-auth — a credential check\n\n"
                    "**Intent.** A user with valid credentials can authenticate; invalid ones are rejected.\n\n"
                    "**Non-goals.** Password reset, SSO.\n\n"
                    "```json\n" + contract + "\n```\n")
        smpath = os.path.join(d, "user-auth.md")
        open(smpath, "w").write(skill_md)
        ok, msg = check(smpath)
        expect(ok and "skill-shape" in msg, f"rejected a sound SKILL-format spec: {msg}")

        # the FOLDER shape: spec/<slug>/SKILL.md
        folder = os.path.join(d, "user-auth")
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "SKILL.md"), "w").write(skill_md)
        ok, msg = check(folder)
        expect(ok, f"rejected a sound folder-shape SKILL spec: {msg}")

        # skill `name` disagreeing with the contract cell slug -> skill-shape fails
        bad_shape = skill_md.replace("name: user-auth", "name: auth-user")
        bpath = os.path.join(d, "bad-shape.md")
        open(bpath, "w").write(bad_shape)
        ok, msg = check(bpath)
        expect(not ok and "skill-shape" in msg, f"accepted a name/cell-slug disagreement: {msg}")

    if fails:
        sys.stderr.write("spec-quality-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("spec-quality-check selftest: OK (a sound structured spec passes; a prose-only criterion, missing "
          "non-goals, no rubric binding, an unsound decomposition, and a prose-only .md each FAIL the right gate)")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write("usage: spec-quality-check.py <asset-path> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    ok, msg = check(argv[0])
    print(msg, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
