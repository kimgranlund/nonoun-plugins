---
id: T-0815
title: "Direct and hybrid session agents beside the conductor"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: sdlc-lite-author 2026-10-30
branch: lane/T-0815-t0815
worktree: ../sdlc-lite.worktrees/T-0815-t0815
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Two new session agents ship beside `sdlc-lite:conductor`: `sdlc-lite:direct`, where the session does the work live with no tickets or handoffs, and `sdlc-lite:hybrid`, which works live on small asks and sends large ones to ticketed lanes.

## Context
- Design agreed with the user on 2026-10-30 (session reply "sdlc-lite:direct and hybrid modes"): the mode is the choice of Claude Code session agent; scripts, hooks and tickets stay shared. Evidence: plain session $0.82 vs solo plus verifier $2.51 on the same builds, hidden tests 10 of 10 in both (`docs/reports/2026-10-28-speed-experiment.md`).
- The conductor's "only trivial edits" rule is prose (`plugins/sdlc-lite/agents/conductor.md` line 35), not a hook; `hooks/block-role-spawn.sh` gates only `sdlc-lite:conductor` sessions. `hooks/_role.sh` treats session agents as no role, so the guard hooks (`block-publish`, `block-stray-worktree`, `block-disk-scan`, `block-pattern-kill`) still apply to everyone.
- Session agents are excluded from run.sh agreement checks in `plugins/sdlc-lite/scripts/check.py`; Codex mapping lives in `plugins/sdlc-lite/scripts/codex_roles.py` (`conductor` is in the workspace-write set).

## Do
1. `plugins/sdlc-lite/agents/direct.md`: read, edit, run the project's own checks, commit with a one-line message; no tickets, handoffs or planner unless the user asks; plan inline only for a many-file change; before a change to a risky area (auth, stored formats, migrations, public API, `hash_bound:` paths) offer `/verify` once, never force it; keep every publish and push rule of the conductor.
2. `plugins/sdlc-lite/agents/hybrid.md`: classify each ask with the `steps.py lane` sizing. L1 and L2 asks run live as in direct. L3 and up, anything the user wants in the background or overnight, and anything touching `hash_bound:` paths go to a ticket and a lane through `lanes.py open --claim`, `solo_run.py`, `dispatch.py prepare verifier` and `lanes.py finish`, with one verifier, exactly as the conductor does. The session stays interactive while lanes run.
3. Register both as session agents wherever the conductor and messenger are listed (check.py exclusions, Codex mapping and generation, the plugin `AGENTS.md` session-agent bullet, `docs/references/` where the conductor is documented as the session agent).
4. Add a short "Modes" section to `plugins/sdlc-lite/agents/conductor.md` naming the other two and how to switch (the `"agent"` setting, then a new session).

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 with both new agent files present.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exit 0.
- `python3 scripts/check-packaging.py` exits 0.

## Constraints
- No change to conductor behavior. No new hook.
