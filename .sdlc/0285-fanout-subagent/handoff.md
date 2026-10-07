---
id: T-0285
title: "Fanout lanes as isolated background sub-agents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0284, T-0281]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Fanout keeps preflight, overlap, locked merge, gates, close, and report as scripts, and the conductor dispatches each lane as a background sub-agent in an isolated worktree.

## Intent
- Do: Fanout lanes as isolated background sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `fanout.py prep` prints, for each ticket, the lane (`steps.py lane`), the dispatch JSON (sub-agent name, model, `isolation: worktree`, brief with the commit instruction `<id>: <title>`), and refuses what `run` refuses today (overlap, uncommitted handoff, `--max-lanes`); dry-run parity cases pass.
  - `fanout.py land <branch>` merges one finished sub-agent branch behind the same locked merge, gates, vacuous-gate refusal, and `close <id>` commit as an external lane does today; a red gate resets the merge (existing behavior, regression case) and the report carries `Lane for <id>` and the tier line.
  - The `--driver` stub path and the existing `fanout.py selftest` cases still pass unchanged; a case with a stub that fails to commit gives outcome `no changes`.
  - Full-chain tickets in a fanout are driven by the parent conductor (roles as sub-agents against the lane branch, `Tree:` line in each brief), documented in `skills/fanout/SKILL.md`; the headless-conductor-per-lane default is removed only in the retire ticket.

## Context
Design section 5. Lane names are `<ticket>-solo`, so the host puts the work on branch `worktree-<name>` under `.claude/worktrees/<name>` (documented; result gives path and branch, observed); `prep` knows the branch before the spawn. `.claude/worktrees/` must be ignored and excluded from watchers (preflight refuses otherwise, as for `.worktrees/`). Register the branch with `external_branch:` or pass it to `land` directly.

## Constraints
No push; main untouched, as today. No em dashes. No push, tag, or publish.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0; its cases 22 to 24 cover prep (lane, dispatch JSON, run/prep refusal parity), land (merge, gates, vacuous gate, red-gate reset, `no changes`, tier M verifier) and a stub that commits nothing.
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- [ ] `python3 scripts/check-packaging.py` exits 0.
- [ ] `git diff --check` exits 0.
- [ ] `grep -q 'fanout.py land' plugins/sdlc-lite/skills/fanout/SKILL.md && grep -q 'Tree: <path>' plugins/sdlc-lite/skills/fanout/SKILL.md` documents the full-chain lane driven by the parent.
- [ ] `git check-ignore -q .claude/worktrees/x` exits 0.
