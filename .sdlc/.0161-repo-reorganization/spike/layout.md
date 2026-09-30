# Documentation layout (trial for T-0161)

This is the trial layout for spike T-0161. It is not `docs/layout.md` and nothing reads it except the spike's `reorg_plan.py`.

`generative-constructs/` and `repo-onboarding/` stay topics, not homes: each is one concept with its own `README.md` index and an internal reading order, and no loose document belongs inside either, so giving them a glob would buy nothing and would take them out of the topic rules (N3).

## Homes

- `maintenance/`
- `reference/` takes `codex-role-execution.md`, `plugin-compatibility.md`
- `reports/` takes `claude-handoff.md`, `claude-response.md`

## Frozen paths

- `docs/validation/`
- `docs/readiness-recovery-validation.md`
- `plugins/sdlc-lite/bench/results/`
- `plugins/sdlc-lite/adapters/codex/agents/`
