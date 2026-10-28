---
id: T-0799
title: "verifier scope diff: a small solo ticket is verified from its diff and recorded checks, not a full reread"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A small solo ticket gets a cheaper independent check: the verifier reruns the ticket's command criteria, reads only `git diff <base>..<review sha>`, and checks each red-first claim, instead of rereading the code base. Independence stays: a different model family, its own runs.

## Intent
- Do: in `dispatch.py prepare verifier`, when the handoff is a solo ticket at L1 or L2 and every acceptance criterion is a runnable command (no prose-only criterion), add a `Scope: diff` line to the brief that tells the verifier to (1) run each criterion command, (2) read the diff from Base sha to Review sha and the files it touches, nothing wider, (3) confirm each failing-first claim in the Outcome by reverting the fix in a throwaway worktree for at most one case, and (4) report `escalate: full` instead of a verdict when the diff touches a file outside the handoff's named scope or a criterion cannot run. Any other ticket gets today's brief. Document the scope line in `plugins/sdlc-lite/agents/verifier.md` and regenerate the generated agent definitions.
- Non-goals: dropping the verifier; changing models or efforts (user decisions); changing L3 and above.
- Done when: the acceptance criteria below pass.

## Context
Evidence (2026-10-28 retro and this session): verifier spend is 53% of sdlc-lite ($266.98 of $499.84), 50% of agent-ui ($546.32 of $1094.69), 28% of maison; on L1 and L2 solo tickets the verifier often took as long as the build (T-0796 build about 25 min, verify 21 min; T-0798 about 8 and 10 min). Analysis: the conductor's answer on 2026-10-28 ("make sdlc as fast as a single session"), theory 1 and 3.
The brief is built in `plugins/sdlc-lite/scripts/dispatch.py` (prepare; see `--solo-model` around line 2594 and the brief lines Base sha / Review sha). Verifier contract: `plugins/sdlc-lite/agents/verifier.md`; generation: `scripts/claude_roles.py` and `plugins/sdlc-lite/scripts/codex_roles.py`.

## Acceptance criteria
1. A dispatch selftest case: prepare verifier on an L1 solo handoff whose criteria are all commands prints a brief with `Scope: diff`; an L1 handoff with one prose-only criterion and an L3 handoff do not. With the change reverted the first case fails (state the FAIL line).
2. `plugins/sdlc-lite/agents/verifier.md` describes the `Scope: diff` rules, including `escalate: full`, and generated-agent parity holds (`check.py` exits 0).
3. dispatch selftest through gate_lock exits 0, `python3 scripts/check-packaging.py` exits 0.

## Constraints
The failing test lands before or with the change. Model and effort tables stay unchanged.
