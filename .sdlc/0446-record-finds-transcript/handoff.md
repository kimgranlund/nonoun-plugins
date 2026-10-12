---
id: T-0446
title: "dispatch.py record finds the sub-agent transcript without a flag"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py record` prices a sub-agent run with no `--transcript` flag by finding its transcript from the agent id, so runs stop landing unmetered.

## Intent
- Do: when `--agent-id` is given and `--transcript` is not, find the sub-agent transcript (the host keeps it under the Claude projects folder as `subagents/agent-<agent id>.jsonl`) and price it as `--transcript` does; when none is found, keep today's `unpriced:` line and exit code. A selftest case with a fixture transcript (priced row written) and a negative control (no transcript found, `unpriced:` still printed). Update `agents/conductor.md` and `skills/handoff-format/run-operations.md` only where they say the flag is required.
- Non-goals: changing how cost is computed; Codex transcripts.
- Done when: the selftest passes with an observed red before the change; `check.sh` exits 0; the next retro's K-001 unmetered share for this repo is below its 9 of 17.
- outcome metric: K-001 (docs/kpi/001-runs-without-cost-row.md), before: 9 of 17 unmetered in sdlc-lite, 106 of 130 in ui-kit-maison

## Context
Evidence: `docs/reports/2026-10-11-fleet-retro-12.md` row 3 and row 2; sdlc-lite.json `runs.unmetered` = 9. Code: `plugins/sdlc-lite/scripts/dispatch.py` (record, transcript pricing near the `--transcript` handling, `unpriced:` line).

## Constraints
Never read a transcript outside the agent's own file; do not guess between several matches: take none and print `unpriced:`. No model or effort change.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and its output holds `ok: record with --agent-id and no --transcript finds the sub-agent transcript` (priced row, resolved_model, no `unpriced:` line).
- Negative controls in the same selftest pass: an `--agent-id` with no transcript prints `unpriced: <name> has no cost row; pass --transcript <jsonl>` with exit 0 and `unpriced: true` in the row; two matching transcripts and a path-shaped id (`../x`) both take none and stay unpriced.
- Before the change the new find case fails (observed red).
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `agents/conductor.md` no longer says `--transcript` is required for a priced record, and `codex_roles.py generate --check` passes.
