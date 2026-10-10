# Verifier minutes and the delta verifier decision (T-0417)

Window: 2026-10-06 to 2026-10-10 (since the 2026-10-06 fleet retro, the start of the last full retro window). Measurement only; no code changed, nothing filed.

## Commands run

```
python3 plugins/sdlc-lite/scripts/fleet_collect.py collect ~/Projects/nonoun/ultimate-tokens --since 2026-10-06
python3 plugins/sdlc-lite/scripts/fleet_collect.py collect ~/Projects/maison/ui-kit-maison --since 2026-10-06
python3 plugins/sdlc-lite/scripts/fleet_collect.py collect ~/Projects/nonoun/agent-ui --since 2026-10-06
```

Verifier count, median and max come from `attempts.by_role.verifier` of each collection. Re-verifies come from the same completed `*.attempt.json` records (role `verifier`, started in the window, deduplicated by attempt_id, worktrees included, read through `fleet_collect.scan_sdlc`): in one handoff directory, the second and later verifier attempts by `started_at`. Minutes are `finished_at` minus `started_at`. The verifier count and total reproduce the collector's `by_role.verifier` exactly (39, 210, 30).

## ultimate-tokens

| Measure | Value |
|---|---|
| Verifier attempts | 39 |
| Median minutes | 9.0 |
| Max minutes | 50.6 |
| Total verifier minutes | 522.0 |
| Re-verifies (second and later in one handoff dir) | 2 |
| Re-verify minutes | 13.4 |
| Share of verifier minutes | 2.6 percent |

## agent-ui

| Measure | Value |
|---|---|
| Verifier attempts | 30 |
| Median minutes | 4.7 |
| Max minutes | 15.3 |
| Total verifier minutes | 179.0 |
| Re-verifies (second and later in one handoff dir) | 4 |
| Re-verify minutes | 38.9 |
| Share of verifier minutes | 21.7 percent |

## ui-kit-maison (control, does not decide the verdict)

The spec names maison as the control: its rounds came from unmet prerequisites, not fixes.

| Measure | Value |
|---|---|
| Verifier attempts | 210 |
| Median minutes | 12.1 |
| Max minutes | 109.9 |
| Total verifier minutes | 3369.8 |
| Re-verifies (second and later in one handoff dir) | 42 |
| Re-verify minutes | 509.9 |
| Share of verifier minutes | 15.1 percent |

## Reading

The threshold is 25 percent of verifier minutes in ultimate-tokens or agent-ui. ultimate-tokens is at 2.6 percent and agent-ui at 21.7 percent, both under it. agent-ui is the nearer one, but on 4 re-verifies and 38.9 minutes over a 30-attempt sample; it does not clear the bar. Maison sits at 15.1 percent and is reported only as the control.

Verdict: do not build a delta verifier
