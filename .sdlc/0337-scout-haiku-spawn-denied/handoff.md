---
id: T-0337
title: "dispatch.py prepare scout L1 emits a model the Agent tool rejects and the spawn hook denies (found by ultimate-tokens)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The scout role can be spawned as a sub-agent: `dispatch.py prepare scout L1` prints a model value the Agent tool accepts, and `block-role-spawn.sh` allows exactly that value for the scout row.

## Intent
- Do: Repro from ultimate-tokens 2026-10-07: `adapters/claude/levels.json` gives the scout row model `claude-haiku-4-5`; the Agent tool schema accepts only `sonnet|opus|haiku|fable`, so the printed value is rejected before the hook, and the alias `haiku` is denied by `block-role-spawn.sh`. Make prepare print the alias for rows whose pinned id is not an alias, and make the hook compare family or alias against the row (not the raw id). Record what the alias resolved to in the dispatch record from the transcript model field when readable. Note the known issue in `docs/reports/bench-scout-pin` history: on a Max login the alias `haiku` resolved to Sonnet 5.5, so say in the dispatch record and release note which model actually ran; do not change the scout model or effort default (a user decision). Audit the other 21 rows for the same alias problem (a selftest that runs prepare for every row and checks the printed model against the Agent schema's alias set).
- Non-goals: model or effort changes; the account-switch criterion; T-0288.
- Done when:
  - A selftest runs `dispatch.py prepare` for all 22 rows and every printed model is in the Agent schema alias set and passes the hook for that row (observed), with a negative control for a bad model.
  - One live scout spawn through prepare, Agent and record succeeds (observed, record the transcript model field).
  - check.py, tickets.py check, dispatch and hook selftests pass.

## Context
Reported by the ultimate-tokens conductor, who used `SDLC_BACKEND=claude run.sh scout L1` as the documented fallback. Files: plugins/sdlc-lite/scripts/dispatch.py, plugins/sdlc-lite/hooks/block-role-spawn.sh, plugins/sdlc-lite/adapters/claude/levels.json, scripts/claude_roles.py.

## Constraints
No em or en dashes. No push or publish. Model and effort defaults unchanged.
