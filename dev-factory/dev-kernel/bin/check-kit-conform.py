#!/usr/bin/env python3
"""check-kit-conform.py — the kernel/kit boundary, enforced (TDD §5).

A kit binds the kernel's contracts to one family; it never forks them. This gate is the boundary's
falsification test made mechanical: a conformant kit (a) is a well-formed `Kit` (kit.schema.json), (b)
ships only species-correct `Adapter`s (adapter.schema.json — a VALIDATION adapter MUST carry a target +
verifier; a DISPATCH adapter MUST carry a runtime + the safety guarantees, which the JSON Schema leaves
optional, so this gate is where the species contract actually bites), and (c) requires ZERO kernel edits
— it must not ship any file that shadows a dev-kernel bin or schema. A kit that needs the kernel changed,
or that re-implements it, has leaked the boundary, and this fails.

Usage:
  check-kit-conform.py kit <kit-dir>      # exit 1 if the kit violates the contract
  check-kit-conform.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# files a kit must NEVER ship — shipping one means it forked/shadowed the kernel rather than binding it.
KERNEL_BINS = {"lattice.py", "validate.py", "lifecycle.py", "compass.py", "ledger.py", "autonomy.py",
               "gate-signal", "gate-verifier", "gate-ledger", "gate-naming"}
KERNEL_SCHEMAS = {"cell.schema.json", "ticket.schema.json", "ledger-entry.schema.json", "activity.schema.json",
                  "dispatch-policy.schema.json", "naming.schema.json", "lattice.schema.json"}
_SLUG_OK = lambda s: isinstance(s, str) and s and all(c.islower() or c.isdigit() or c == "-" for c in s)
_LAYERS = {"ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"}
_RUNTIMES = {"claude-agent-sdk", "headless-claude-code", "mock"}


def validate_adapter(a, idx):
    errs = []
    where = f"adapter[{idx}]"
    kind = a.get("kind")
    if kind not in ("validation", "dispatch"):
        return [f"{where}: kind must be validation|dispatch (got {kind!r})"]
    if not _SLUG_OK(a.get("name")):
        errs.append(f"{where}: name must be a kebab slug")
    if kind == "validation":
        # species contract: a validation adapter binds a (layer[, scope]) to a verifier command
        t = a.get("target")
        if not isinstance(t, dict) or t.get("layer") not in _LAYERS:
            errs.append(f"{where} (validation): `target.layer` must be a layer enum")
        v = a.get("verifier")
        if not isinstance(v, list) or not v:
            errs.append(f"{where} (validation): `verifier` must be a non-empty argv list (the command validate.py runs)")
        for forbidden in ("runtime", "invocation", "guarantees"):
            if forbidden in a:
                errs.append(f"{where} (validation): must not carry dispatch-only field `{forbidden}`")
    else:  # dispatch
        if a.get("runtime") not in _RUNTIMES:
            errs.append(f"{where} (dispatch): `runtime` must be one of {sorted(_RUNTIMES)}")
        g = a.get("guarantees")
        if not isinstance(g, dict):
            errs.append(f"{where} (dispatch): `guarantees` is required (the §9.2 runtime guarantees)")
        else:
            # the SAFETY guarantees are non-negotiable: a worker must run hermetic with gates active
            if g.get("hermetic_worktree") is not True:
                errs.append(f"{where} (dispatch): guarantees.hermetic_worktree must be true")
            if g.get("gates_active") is not True:
                errs.append(f"{where} (dispatch): guarantees.gates_active must be true (the immutable boundary inside the worktree)")
            if g.get("event_stream") is not True:
                errs.append(f"{where} (dispatch): guarantees.event_stream must be true (events teed into the ledger)")
        for forbidden in ("target", "verifier"):
            if forbidden in a:
                errs.append(f"{where} (dispatch): must not carry validation-only field `{forbidden}`")
    return errs


def validate_dispatch_policy(path):
    if not os.path.isfile(path):
        return [f"dispatch_policy: file not found ({path})"]
    try:
        dp = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"dispatch_policy: invalid JSON ({e})"]
    errs = []
    if not dp.get("family"):
        errs.append("dispatch_policy: missing `family`")
    if "default" not in dp:
        errs.append("dispatch_policy: missing `default` ExecutionPlan")
    for i, rule in enumerate(dp.get("rules", [])):
        if "match" not in rule or "plan" not in rule:
            errs.append(f"dispatch_policy.rules[{i}]: needs both `match` and `plan`")
    for label, plan in [("default", dp.get("default"))] + [(f"rules[{i}].plan", r.get("plan")) for i, r in enumerate(dp.get("rules", []))]:
        if isinstance(plan, dict):
            for req in ("orchestration_shape", "loop_strategy", "context_plan", "effort", "delegation"):
                if req not in plan:
                    errs.append(f"dispatch_policy.{label}: ExecutionPlan missing `{req}`")
    return errs


def validate_kit(kit_dir):
    errs = []
    manifest = os.path.join(kit_dir, "kit.json")
    if not os.path.isfile(manifest):
        return False, [f"no kit.json at {kit_dir} (the Kit manifest binding the kernel contracts)"]
    try:
        kit = json.load(open(manifest, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"kit.json: invalid JSON ({e})"]

    name = kit.get("name", "")
    if not (name.startswith("dev-kit-") and _SLUG_OK(name)):
        errs.append(f"kit.name must be dev-kit-<family> (got {name!r})")
    if not kit.get("family"):
        errs.append("kit.family is required")
    if not kit.get("kernel_compat"):
        errs.append("kit.kernel_compat is required (the dev-kernel version range this kit binds)")
    rm = kit.get("rubric_manifest")
    if not isinstance(rm, list) or not rm:
        errs.append("kit.rubric_manifest must be a non-empty list (which validated rubric gates which layer)")
    else:
        for i, m in enumerate(rm):
            if not isinstance(m, dict) or m.get("layer") not in _LAYERS or not m.get("rubric_cell"):
                errs.append(f"kit.rubric_manifest[{i}]: needs a layer enum + a rubric_cell")
    adapters = kit.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        errs.append("kit.adapters must be a non-empty list (at least one validation adapter)")
    else:
        for i, a in enumerate(adapters):
            errs += validate_adapter(a, i)
        if not any(a.get("kind") == "validation" for a in adapters):
            errs.append("kit.adapters: a family needs at least one VALIDATION adapter (else 'validated' means nothing)")
    if not kit.get("dispatch_policy"):
        errs.append("kit.dispatch_policy is required (the deterministic unit->execution-plan map)")
    else:
        errs += validate_dispatch_policy(os.path.join(kit_dir, kit["dispatch_policy"]))

    # THE BOUNDARY: a conformant kit ships ZERO kernel files (it binds the contracts, never forks them)
    for root, _dirs, files in os.walk(kit_dir):
        for f in files:
            if f in KERNEL_BINS:
                errs.append(f"BOUNDARY VIOLATION: kit ships a kernel bin `{f}` ({os.path.relpath(os.path.join(root, f), kit_dir)}) — a kit binds the kernel, never forks it")
            if f in KERNEL_SCHEMAS:
                errs.append(f"BOUNDARY VIOLATION: kit ships a kernel schema `{f}` — bind it by $id, do not copy it")
    return (not errs), errs


def _write_conformant_kit(kit_dir):
    os.makedirs(kit_dir, exist_ok=True)
    plan = {"orchestration_shape": "evaluator-optimizer", "loop_strategy": "auto-research",
            "context_plan": {"retrieval": "spec-rubric-patterns"}, "effort": {"model_tier": "mid", "reasoning_effort": "moderate"},
            "delegation": {"mode": "none", "max_depth": 1}}
    json.dump({"family": "demo", "rules": [], "default": plan},
              open(os.path.join(kit_dir, "dispatch-policy.json"), "w"))
    json.dump({
        "name": "dev-kit-demo", "family": "demo", "kernel_compat": ">=0.1.0,<0.2.0",
        "rubric_manifest": [{"layer": "spec", "rubric_cell": "rubric.task.demo"}],
        "adapters": [
            {"kind": "validation", "name": "spec-check", "target": {"layer": "spec"}, "verifier": ["python3", "-c", "import sys;sys.exit(0)"]},
            {"kind": "dispatch", "name": "mock", "runtime": "mock",
             "guarantees": {"hermetic_worktree": True, "gates_active": True, "event_stream": True, "stop_on": ["signal", "budget"]}},
        ],
        "dispatch_policy": "dispatch-policy.json",
    }, open(os.path.join(kit_dir, "kit.json"), "w"))


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        good = os.path.join(root, "dev-kit-demo")
        _write_conformant_kit(good)
        ok, errs = validate_kit(good)
        expect(ok, f"a conformant kit was rejected: {errs}")

        # a validation adapter missing its verifier → FAIL (the species contract bites here)
        bad1 = os.path.join(root, "bad1")
        _write_conformant_kit(bad1)
        k = json.load(open(os.path.join(bad1, "kit.json")))
        del k["adapters"][0]["verifier"]
        json.dump(k, open(os.path.join(bad1, "kit.json"), "w"))
        ok, errs = validate_kit(bad1)
        expect(not ok and any("verifier" in e for e in errs), "a validation adapter without a verifier was accepted")

        # a dispatch adapter with gates_active=false → FAIL (the safety guarantee is non-negotiable)
        bad2 = os.path.join(root, "bad2")
        _write_conformant_kit(bad2)
        k = json.load(open(os.path.join(bad2, "kit.json")))
        k["adapters"][1]["guarantees"]["gates_active"] = False
        json.dump(k, open(os.path.join(bad2, "kit.json"), "w"))
        ok, errs = validate_kit(bad2)
        expect(not ok and any("gates_active" in e for e in errs), "a dispatch adapter with gates_active=false was accepted")

        # a kit that ships a kernel bin → BOUNDARY VIOLATION
        bad3 = os.path.join(root, "bad3")
        _write_conformant_kit(bad3)
        os.makedirs(os.path.join(bad3, "bin"), exist_ok=True)
        open(os.path.join(bad3, "bin", "lattice.py"), "w").write("# forked kernel\n")
        ok, errs = validate_kit(bad3)
        expect(not ok and any("BOUNDARY VIOLATION" in e for e in errs), "a kit shadowing a kernel bin was accepted")
    if fails:
        sys.stderr.write("check-kit-conform selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("check-kit-conform selftest: OK (a conformant kit passes; a validation adapter without a verifier, a "
          "dispatch adapter without gates_active, and a kit shadowing a kernel bin all FAIL — the species contract "
          "and the zero-kernel-edits boundary are enforced, not just documented)")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    if argv[0] == "kit":
        ok, errs = validate_kit(argv[1])
        if ok:
            print(f"kit-conform: OK — {argv[1]} binds the kernel contracts (no kernel edits, species-correct adapters)")
            return 0
        sys.stderr.write(f"kit-conform: FAIL — {argv[1]}\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        return 1
    print(f"check-kit-conform.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
