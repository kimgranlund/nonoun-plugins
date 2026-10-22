---
id: T-0698
title: "Lane roles run heavy test suites through gate_lock run"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Builders, solo agents and verifiers working in a lane admit their heavy test suites through the gate lock, so lanes from every conductor on one machine share one admission limit.

## Intent
- Do: add one Rules line to `plugins/sdlc-lite/agents/builder.md`, `solo.md` and `verifier.md`: run a full test suite or browser test (npm test, node --test, vitest, playwright, jest, a repo gate) as `python3 <plugin-root>/scripts/gate_lock.py run --need compute_units=N --nice -- <cmd>`; a single test file or a selftest of one script runs directly. Regenerate with `claude_roles.py generate` and `codex_roles.py generate`. Name the rule in `docs/references/sdlc-internals.md` where the gate lock is described.
- Non-goals: a hook that enforces it; translating worker counts (separate ticket).
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "Lane agents run tests directly. Builders, solo agents and verifiers run `npm test`, `node --test`, `vitest` and `playwright` in lane trees without going through `gate_lock.py run`. Each lane's test run is admitted with no limit."

## Acceptance criteria
1. `git grep -n "gate_lock.py run" plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/solo.md plugins/sdlc-lite/agents/verifier.md` prints one line per file.
2. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.

## Outcome
- The existing machine-wide queue sentence in `plugins/sdlc-lite/agents/builder.md`, `solo.md` and `verifier.md` now reads: a full test suite or browser test (npm test, node --test, vitest, playwright, jest, a repo gate) and the full `check.sh` run as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_lock.py run --need compute_units=N --nice -- <cmd>`, N the workers the suite starts (1 to 6); a single test file or a selftest of one script runs directly. The path is unquoted so the literal `gate_lock.py run` of criterion 1 matches (the old quoted form printed nothing).
- `docs/references/sdlc-internals.md` names the rule in the `gate_lock.py` section. Generated Claude and Codex agents regenerated.
- Checks: criterion 1 prints one line per file; both `generate --check` exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check a8680df4` exit 0.
