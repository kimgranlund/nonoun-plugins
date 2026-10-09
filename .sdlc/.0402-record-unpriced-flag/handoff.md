---
id: T-0402
title: "dispatch.py record flags a sub-agent run it cannot price"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py record` for a sub-agent run it cannot price says so, so an unmetered run is visible at the moment it is recorded and not only in the retro.

## Intent
- Do: in scripts/dispatch.py `record`, when a sub-agent result is recorded with no `--transcript` and no `--tokens` (and the dispatch carries no transcript the script can find), print one stderr line `unpriced: <name> has no cost row; pass --transcript <jsonl>` and write the runs row with an explicit `unpriced: true` field. Do not fail the record. Make `fleet_collect.py` count that field in the same `runs.unmetered` figure it already reports, if it does not already. Document the flag in docs/references/sdlc-internals.md next to the record entry and in the conductor "How you run roles" text.
- Non-goals: pricing anything without a transcript; changing prices; model or effort changes.
- Done when:
  - A dispatch selftest case, observed failing first: `record` with no `--transcript` and no `--tokens` prints the `unpriced:` line and the runs row holds `unpriced: true`; with `--transcript` it prints nothing and the row is priced.
  - dispatch.py selftest, fleet_collect selftest if it exists, check.py and tickets.py check pass.

## Context
Fleet retro 2026-10-09 row 1 (docs/reports/2026-10-09-fleet-retro-00.md): 163 of 453 runs unmetered across five repos; conductors record with zero tokens or never pass --transcript. Outcome metric K-001 (docs/kpi/001-runs-without-cost-row.md).

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and prints `dispatch selftest: PASS`, including the cases "record with no --transcript and no --tokens prints the unpriced line and the row holds unpriced true" and "record with --transcript prints no unpriced line and the row is priced".
- `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest` exits 0 and includes the case counting an `unpriced: true` row in `runs.unmetered`.
- In `dispatch.py` `record`, the unpriced note and `unpriced: true` appear only when no cost could be estimated; the record still exits 0.
- `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/agents/conductor.md` document the flag; `claude_roles.py generate --check` and `codex_roles.py generate --check` pass.
- `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.

## Closed

2026-10-09: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
