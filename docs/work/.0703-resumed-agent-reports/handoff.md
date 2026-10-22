---
id: T-0703
title: "A resumed sub-agent reports back to the conductor"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A sub-agent resumed after a host restart tells the conductor when it finishes, and `dispatch.py status` flags a finished report the conductor has not recorded.

## Intent
- Do: in `plugins/sdlc-lite/scripts/dispatch.py`, the `resume` ladder's resume message tells the agent to `SendMessage` "main" with its pointer line when done. `status` prints `report-unrecorded` for an attempt whose report file is newer than its attempt record and that has no recorded result. Name both in `plugins/sdlc-lite/agents/conductor.md` where it covers recovery; regenerate the agents.
- Non-goals: changing how the host delivers idle notices.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "After a host restart, a sub-agent resumed with `SendMessage` (by agent id, since names no longer resolved) finished and wrote its report, but no idle or completion notice reached the conductor. Five lanes sat idle for 15 to 35 minutes until a manual check."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: `resume` output holds the SendMessage instruction; `status` prints `report-unrecorded` for a report newer than its unrecorded attempt and nothing extra once recorded. Each case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.

## Outcome
- `dispatch.py` `resume` ladder message now asks the agent to `SendMessage` 'main' with its `<role>-<level> <status> <path>` pointer line (`RESUME_MESSAGE`); `status` adds `report-unrecorded` to any attempt other than completed or failed whose report file is newer than its attempt record (the older `report-written-unrecorded` flag is unchanged).
- Named both in `agents/conductor.md` (recovery paragraph) and `docs/references/sdlc-internals.md`; regenerated `sdlc-conductor-l1.toml`.
- Checks: `dispatch.py selftest` PASS; with the change reverted the 3 positive new cases fail (the 2 negative controls pass by design); `claude_roles.py generate --check` 0; `codex_roles.py generate --check` 0; `check.py` 0; `check-packaging.py` 0; `git diff --check 91ad9980` 0.

## Outcome

2026-10-21 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 91ad99809f64
- Changed: see commits
- Commits: d1c4ab8 T-0703: A resumed sub-agent reports back to the conductor
- Check: 1 `dispatch.py selftest` exits 0 with new cases (resume holds the SendMessage instruction; status p...: pass
- Check: 2 `claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0: pass
- Check: 3 `check.py` exits 0 and `git diff --check <base sha>` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py:971-974 answers the... -> notes.md
- Follow-up: note: plugins/sdlc-lite/agents/conductor.md:43 names both the... -> notes.md
