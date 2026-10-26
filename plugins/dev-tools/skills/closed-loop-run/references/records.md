# Records Reference

The shapes behind SKILL.md sections 4, 5 and 16. Scaffolds with empty values are in `templates/`; keep the two in step when a field changes.

## Episode contract

Create one episode per failure or tightly coupled failure cluster. An episode MUST declare:

```yaml
episode:
  id: E-001
  objective: "Specific local outcome to achieve"
  observed: "Evidence-backed deviation"
  expected: "Expected behavior or result"
  scope:
    allowed: ["bounded areas the episode may change"]
    forbidden: ["areas it must not change"]
  invariants:
    - "conditions that must remain true"
  verification:
    direct: "cheapest discriminating check"
    local: "affected unit/subsystem check"
  budget:
    attempts: 4
    wall_time: null
    cost: null
    change_radius: "local"
    architecture_changes: false
  stop:
    no_progress_after: 2
    confidence_floor: null
```

Adjust budgets to the task. If wall time or monetary cost cannot be measured, use attempts plus scope and verification limits.

## Attempt record

For each attempt, record at minimum:

```yaml
attempt:
  n: 1
  hypothesis: H1
  action: "what changed or was tested"
  expected_signal: "what result would support/refute the hypothesis"
  observed_signal: "what actually happened"
  outcome_delta: "better | worse | unchanged | unknown"
  information_delta: "higher | lower | unchanged uncertainty"
  decision: "continue | resolve | revert | escalate | stop"
```

Do not require numeric confidence unless the domain supports it. Ordinal confidence is acceptable.

## Learning record

For every materially resolved or escalated episode, create a compact durable record:

```yaml
learning_record:
  episode: E-001
  summary: "short description"
  expected: "intended result"
  observed: "actual evidence"
  root_cause:
    category: "Contract"
    cause: "specific causal mechanism"
    confidence: "high"
  inside_out: "structural finding or n/a"
  outside_in: "outcome finding or n/a"
  attempts:
    count: 3
    useful: [1, 2]
    discarded: [3]
  resolution: "what changed"
  verification: ["V0", "V1", "V3", "V4", "V5"]
  prevention:
    regression: "new/updated check"
    hardening: "contract/knowledge/process change or none"
  residual_risk: "remaining uncertainty"
```

Store only durable lessons. Do not pollute shared knowledge with transient debugging history that has no future retrieval value.

## H3 cycle report

The final report SHOULD contain:

```yaml
cycle_report:
  cycle_id: CLR-001
  intent: "what this run was meant to establish"
  baseline: "checkpoint/version/state"
  verification_summary:
    passed: 0
    failed: 0
    skipped: 0
  episodes:
    resolved: []
    improved: []
    blocked: []
    escalated: []
    exhausted: []
  regressions: []
  new_findings: []
  root_cause_patterns: []
  changes:
    implementation: []
    tests: []
    contracts: []
    knowledge: []
    architecture_process: []
  confidence: "high | medium | low"
  residual_risk: []
  next_cycle:
    required: true
    reasons: []
    recommended_scope: []
```

The report is the handoff boundary between H3 cycles. A new cycle starts from this report rather than from hidden reasoning or an ever-growing recursive context.

### Series fields

A cycle that belongs to a series ([experiment-series.md](experiment-series.md)) adds a `series` block, so the next cycle can compare against it without rereading raw evidence:

```yaml
cycle_report:
  series:
    comparison_set: "id of the fixed case set, settings and sample count"
    kind: "full | targeted"
    compared_to: "cycle id of the last identical run of this set"
    transitions:
      fail_to_pass: []
      pass_to_fail: []
      fail_to_fail_same_cause: []
      fail_to_fail_new_cause: []
    mechanism_metrics:
      - fix: "change id"
        metric: "what shows the mechanism working"
        value: "this cycle"
        previous: "last identical cycle"
        verdict: "fixed live | partly | not exercised | regressed"
    quarantined_provider_errors:
      - kind: "rate limit | usage limit | overload | auth | timeout | runner crash"
        count: 0
        affected_runs: []
        action: "rerun clean | dropped from set | none"
    spend:
      estimate: null
      actual: null
      cap: null
      stop: "done | cap | crash"
    replays_frozen: []
    tooling_gaps: []
```

`pass_to_fail` is the regression list, and in a series report the top-level `regressions` field points at it rather than holding a second copy; a non-empty list is reported even when the pass rate rose. A fix with no exercised mechanism metric is "not exercised", never "fixed".

## Output behavior

During a run:

- keep raw evidence near the episode that produced it;
- keep the active context focused on current hypotheses and decisive evidence;
- summarize discarded experiments rather than carrying all raw reasoning forward;
- preserve provenance from finding → hypothesis → experiment → result → resolution;
- distinguish known facts, supported inference, and unresolved uncertainty;
- make stopping and escalation visible decisions, not silent failures.

At completion, return the H3 cycle report plus any durable learning records and artifacts required by the caller.
