---
role: builder
level: all
model: all
effort: all
host: claude
task_set: bench step-1 replay, 3 of 5 tasks, overlay vs none
pass_rate: 3/5
cost_usd: 7.94
date: 2026-10-11
evidence: docs/reports/2026-10-11-builder-overlay-ab.md
---
## Method

Replay A/B of the builder L1 and L5 overlays (T-0441, commit 00735e20). Arm A is a shared clone at HEAD with agents/builder-L1.md and builder-L5.md taken from 00735e20^, so the arms differ only by the At this level section. Arm B is HEAD. Each cell replays the archived 2026-09-27 step-1 handoff in a fresh clone of the task repo at its base: dispatch.py prepare builder, a headless claude -p --plugin-dir <arm> --agent sdlc-lite:builder-<level>, record --transcript, one verifier (armB root), then the hidden check. The cap was 10 USD for replay rows. L1 ran 5 pairs (rep 1 all three tasks, rep 2 two tasks). command-modal-footer rep 2 and all L5 pairs were skipped for budget. button-geometry-model and svelte-icon-component were not run (repos absent).

## Result

Verdict: drop. L1 overlay: drop. L5 overlay: unverified. Null at this sample size: no. Spend: 7.94 USD. No builder blocked in either arm (0 of 5 each), so the L1 blocked-rate rule (not below arm A) drops it. First pass was identical per task (subagent-tool-names 2 of 2, figma-stale-skip-report 0 of 2, command-modal-footer 1 of 1, both arms). Builder cost was +3.3 percent. There was no hidden-check regression. Arm B passed 3 of 5 (hidden check, or the verifier for command-modal-footer). The effect is not visible at this sample size; the drop is a property of the zero-block baseline.
