#!/usr/bin/env python3
"""execplan.py — assemble a unit's typed ExecutionPlan from the kit's dispatch policy (TDD §8.2, execution-strategy.md).

The compass picks WHICH cell to advance; this picks HOW the unit runs — its orchestration shape, loop
strategy, context plan, effort ladder, and delegation. Per the routing law that is DETERMINISTIC: a
`DispatchPolicy` (kit-supplied) maps unit characteristics to a plan by first-matching rule; the model's
judgment lives INSIDE the assembled plan, never in choosing it ("selection is policy, not vibes"). The
dispatcher consumes the plan; without this, every unit ran as a generic single-pass worker regardless of
what the policy declared.

  unit = {ticket_type, target_layer, target_scope, risk_band, autonomy_tier}
  plan = first rule whose `match` is satisfied (omitted match keys are wildcards) → rule.plan, else default

Usage:
  execplan.py assemble --policy FILE --ticket FILE [--dir DIR] [--tier N]
  execplan.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import lattice as _lat  # noqa: E402


def risk_band(risk):
    """Map a 0-1 risk estimate to the policy's match band."""
    if risk is None:
        return "moderate"
    return "low" if risk < 0.34 else "moderate" if risk < 0.67 else "high"


def _matches(match, unit):
    """A rule matches when EVERY present key admits the unit's value; omitted keys are wildcards."""
    for key, allowed in (match or {}).items():
        val = unit.get(key)
        if val is None:
            return False
        if val not in allowed:
            return False
    return True


def assemble(policy, unit):
    """First-matching rule wins; `default` applies when none match. Pure function — no I/O, no inference."""
    for rule in policy.get("rules", []):
        if _matches(rule.get("match"), unit):
            return rule["plan"], "rule"
    return policy.get("default"), "default"


def unit_from(ticket, cell, tier):
    return {
        "ticket_type": ticket.get("type"),
        "target_layer": cell.get("layer") if cell else None,
        "target_scope": cell.get("scope") if cell else None,
        "risk_band": risk_band((ticket.get("priority") or {}).get("risk")),
        "autonomy_tier": tier,
    }


def load_policy(path):
    pol = json.load(open(path, encoding="utf-8"))
    if "default" not in pol:
        raise ValueError(f"dispatch policy {path} has no `default` ExecutionPlan")
    return pol


def plan_for(policy, ticket, cell, tier):
    """The full assembly the dispatcher calls. Returns (plan, source)."""
    return assemble(policy, unit_from(ticket, cell, tier))


def selftest():
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    team = {"orchestration_shape": "orchestrator-workers", "loop_strategy": "auto-research",
            "context_plan": {"retrieval": "spec-rubric-patterns"}, "effort": {"model_tier": "large", "reasoning_effort": "high", "max_iterations": 8},
            "delegation": {"mode": "team", "max_depth": 2}}
    mid = {"orchestration_shape": "evaluator-optimizer", "loop_strategy": "auto-research",
           "context_plan": {"retrieval": "spec-rubric-patterns"}, "effort": {"model_tier": "mid", "reasoning_effort": "moderate", "max_iterations": 5},
           "delegation": {"mode": "none", "max_depth": 1}}
    default = {"orchestration_shape": "single-pass", "loop_strategy": "single",
               "context_plan": {"retrieval": "minimal"}, "effort": {"model_tier": "small", "reasoning_effort": "low", "max_iterations": 2},
               "delegation": {"mode": "none", "max_depth": 0}}
    policy = {"family": "corpus", "rules": [
        {"match": {"target_layer": ["spec", "rubric"], "risk_band": ["high"]}, "plan": team},
        {"match": {"target_layer": ["spec", "rubric", "pattern"]}, "plan": mid},
    ], "default": default}

    # risk banding
    expect(risk_band(0.1) == "low" and risk_band(0.5) == "moderate" and risk_band(0.9) == "high", "risk banding wrong")

    # a high-risk spec unit → the TEAM rule (first match), maximal decomposition
    plan, src = assemble(policy, {"ticket_type": "feature", "target_layer": "spec", "target_scope": "system", "risk_band": "high", "autonomy_tier": 2})
    expect(src == "rule" and plan["delegation"]["mode"] == "team", f"high-risk spec did not get the team plan: {plan['orchestration_shape']}")

    # a moderate-risk spec unit → the SECOND rule (mid), not the team rule (first-match, but risk_band excludes it)
    plan, src = assemble(policy, {"ticket_type": "task", "target_layer": "spec", "target_scope": "task", "risk_band": "moderate", "autonomy_tier": 1})
    expect(plan["effort"]["model_tier"] == "mid", "moderate-risk spec did not fall to the mid rule")

    # an unmatched layer (ledger) → the DEFAULT (single-pass), an irreducible unit collapses
    plan, src = assemble(policy, {"ticket_type": "chore", "target_layer": "ledger", "target_scope": "call", "risk_band": "low", "autonomy_tier": 0})
    expect(src == "default" and plan["orchestration_shape"] == "single-pass", "unmatched unit did not collapse to default")

    # first-match-wins is order-sensitive (the team rule precedes the mid rule)
    plan, _ = assemble(policy, {"ticket_type": "feature", "target_layer": "rubric", "target_scope": "system", "risk_band": "high", "autonomy_tier": 3})
    expect(plan["delegation"]["mode"] == "team", "first-match-wins violated")

    # unit_from derives the band from the ticket priority
    u = unit_from({"type": "feature", "priority": {"risk": 0.9}}, {"layer": "spec", "scope": "system"}, 2)
    expect(u["risk_band"] == "high" and u["target_layer"] == "spec", "unit_from derived the wrong unit")
    if fails:
        sys.stderr.write("execplan selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("execplan selftest: OK (risk banding; first-matching rule wins; a high-risk definitional unit assembles a "
          "team/orchestrator plan, a moderate one a mid evaluator-optimizer, an irreducible/unmatched unit collapses "
          "to the single-pass default — selection is deterministic policy, never inference)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    if argv[0] == "assemble":
        policy = load_policy(_arg(argv, "--policy"))
        ticket = json.load(open(_arg(argv, "--ticket"), encoding="utf-8"))
        d = _arg(argv, "--dir", ".agents/dev-factory")
        cell = _lat.find(_lat.load(d), ticket.get("target_cell")) if os.path.exists(os.path.join(d, "lattice.json")) else None
        plan, src = plan_for(policy, ticket, cell, int(_arg(argv, "--tier", "1")))
        print(json.dumps({"source": src, "plan": plan}, indent=2))
        return 0
    print(f"execplan.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
