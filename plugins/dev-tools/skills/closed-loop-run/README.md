# closed-loop-run

A universal agent skill for bounded verification, diagnosis, local improvisation, progressive regression, and durable learning.

## Primary pattern

**Explore locally. Verify progressively. Commit at checkpoints. Learn globally.**

The skill separates:

- H0 actions
- H1 bounded repair windows
- H2 failure episodes
- H3 full verification cycles
- H4 cross-run learning, including a series of cycles

This avoids both expensive full-loop reruns after every defect and unbounded recursive autonomous problem solving.

It also covers running a series of cycles against a live, nondeterministic or paid system: fixed comparison sets, alternating targeted and full cycles, regression churn, mechanism metrics, spend caps and provider-error quarantine.

Start with `SKILL.md`. Templates are optional machine-readable scaffolds. References:

- `references/control-model.md`: horizons, control flow, run protocol, checkpoints, concurrency, cost strategy, domain adaptation.
- `references/diagnosis.md`: diagnosis sequence, lost context and uniform errors, taxonomy, cause classes, clustering.
- `references/verification-ladder.md`: the ladder and the inside-out and outside-in checklists.
- `references/records.md`: episode, attempt, learning record and cycle report shapes.
- `references/experiment-series.md` and `references/live-evaluation.md`: running a series of live, paid cycles.

`updates-log/` records every change set to the skill, newest first in `updates-log/CHANGELOG.md`.
