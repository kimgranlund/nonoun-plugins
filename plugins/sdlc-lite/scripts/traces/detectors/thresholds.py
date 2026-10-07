"""Thresholds: the one dict of numbers every detector reads.

THRESHOLDS  flat keys, plus "severity": {finding kind: 1..3}. A detector never hard-codes a
            number; it reads it here through merged(overrides).
merged(overrides)
            THRESHOLDS with overrides applied on top (None or {} gives THRESHOLDS); an overriding
            "severity" dict is merged key by key, so a caller can change one severity alone.
"""

THRESHOLDS = {
    # escalation: replan-loop fires at this many planner rows in one task dir (or any
    # superseded row), and is high severity at this many replans.
    'replan_loop_planners': 2,
    'replan_loop_high_replans': 2,
    # escalation: unchanged-verdict-bump compares two fails this many levels apart.
    'bump_levels': 1,
    # escalation: run.sh exits with this code when a result lacks its required section.
    'exit_code_missing_section': 3,
    # plan: criteria-never-red reruns each acceptance criterion span at base-sha with this
    # timeout in seconds (rerun.run).
    'rerun_timeout_secs': 60,
    # cost: cost-over-baseline fires when a passed step costs at least this multiple of the
    # bench median cost per passed step.
    'cost_over_baseline_ratio': 2.0,
    # cost: many-builder-attempts fires at this many builder rows in one step dir.
    'many_builder_attempts': 3,
    # cost: polling-loop fires at this many identical (or polling-pattern) Bash calls.
    'polling_loop_calls': 5,
    'severity': {
        'replan-loop': 2,
        'replan-loop-high': 3,
        'recurring-finding': 2,
        'unchanged-verdict-bump': 3,
        'plan-defect-refusal': 2,
        'wrong-resume-order': 3,
        'exit-3-result': 2,
        'statusless-builder': 2,
        'no-verdict-verifier': 2,
        'attempt-without-run-row': 2,
        'stale-running-marker': 2,
        'criteria-never-red': 2,
        'contract-dependents': 2,
        'scope-prose': 2,
        'stray-worktree': 2,
        'tracked-runtime-file': 2,
        'integration-reset': 3,
        'reflog-gone': 1,
        'stale-log-lines': 2,
        'stale-log-lines-legacy': 1,
        'overwritten-gate-log': 1,
        'ticket-id-collision': 3,
        'unregistered-external-branch': 2,
        'cost-over-baseline': 2,
        'many-builder-attempts': 2,
        'polling-loop': 2,
        'background-denial': 2,
        'rate-limit': 1,
    },
}


def merged(overrides=None):
    out = dict(THRESHOLDS)
    out['severity'] = dict(THRESHOLDS['severity'])
    for k, v in (overrides or {}).items():
        if k == 'severity' and isinstance(v, dict):
            out['severity'].update(v)
        else:
            out[k] = v
    return out
