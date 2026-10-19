---
id: T-0562
title: "Role sub-agents that background a Bash call go idle and never wake when it finishes"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role sub-agent cannot stall by backgrounding a Bash call: the call is refused or run in the foreground, so the role never sits idle waiting for a notification that does not reach it.

## Repro
1. Spawn a role sub-agent (solo, builder, or verifier) whose work includes a long check.
2. The agent runs Bash with `run_in_background: true` and then ends its turn "waiting on the notification".

## Expected
The role keeps working until it reports.

## Actual
The role goes idle; the parent must nudge it (T-0553 builder, 21 min idle, 2026-10-14; T-0558 solo, 2026-10-15), even though the brief says "Run every command in the foreground".

## Context
Brief wording did not hold twice, so a structural guard is needed. Candidate: a PreToolUse hook on Bash that, for a role session (`SDLC_ROLE` set or a role `agent_type`), denies `run_in_background: true` with a message to rerun in the foreground (long checks fit within the Bash timeout or go through `gate_lock.py run`). Mirror it in the role contracts' one line. Codex: note only.

## Constraints
The failing hook selftest (role + background denied; main session + background allowed) lands with the fix. Target 0.23.1.

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0; its T-0562 cases deny Bash `run_in_background: true` and Monitor for a role sub-agent (`agent_type` `sdlc-lite:solo-L2`, `builder-L3`, `verifier-L2`, no `SDLC_ROLE`) with stderr naming the role and "foreground", and pass the main session, `sdlc-lite:conductor`, `Explore`, `general-purpose`, and a sub-agent with `run_in_background: false`. Negative control: the same selftest failed (`sub-agent sdlc-lite:solo-L2 + background true: exit 0, want 2`) against the unchanged hook.
2. `agents/solo.md` Loop step 3 carries the foreground rule (never `run_in_background` or Monitor); `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check` is clean.
4. `docs/references/claude-hooks.md` describes the sub-agent role case under `hooks/block-background.sh`, lists `block-background` among `_role.sh` users, and notes Codex has no hook (text rule only).

## Outcome

2026-10-14 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: e12e8b76ca71
- Changed: see commits
- Commits: 9552fd4 T-0562: block-background denies background Bash and Monitor for role sub-agents
- Check: 1 hook-selftest.sh T-0562 cases: pass
- Check: 2 solo.md Loop step 3 foreground rule, generated agents in parity: pass
- Check: 3 check.py and git diff --check: pass
- Check: 4 claude-hooks.md: pass
- Follow-up: note: redck.py deviations printed nothing, and the handoff has no red... -> notes.md
- Follow-up: note: a main session started with claude --agent sdlc-lite:solo-L2 and no... -> notes.md
