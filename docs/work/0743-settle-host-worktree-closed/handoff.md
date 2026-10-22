---
id: T-0743
title: "Landed host-owned agent worktrees do not hold the integration tree open"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After `settle`, a host-owned Claude Code agent worktree (`.claude/worktrees/agent-*`) whose branch is merged into the integration branch no longer counts as an open lane, so the integration tree closes and the next `fanout.py prep` with the default lanes dir works; settle prints the exact cleanup command for any host worktree it cannot remove.

## Intent
- Do: In `lanes.py` (`lane still open` check, about line 1883) and `fanout.py settle`, treat a host-owned worktree whose branch is an ancestor of the integration branch as closed for the integration-close check, and print the `git worktree remove` line for the maintainer.
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #71 (quoted):

> **Version:** sdlc-lite 0.33.0, Claude Code host, sub-agent lanes (`isolation: worktree`). Seen in ui-kit-neue 2026-10-22.
>
> **What happened**
> After every ticket landed and `fanout.py cover` passed, `fanout.py settle fanout/2026-10-22c --require-covered` fast-forwarded main. It then printed:
> `lane still open: <root>/fanout/integration (lanes still open into fanout/2026-10-22c: agent-a2a38b6fc2697a508, agent-a81580b9b89717d7a, agent-ad7b98c0455f2ee1b)`
>
> The open lanes are the host-owned `.claude/worktrees/agent-*` trees the Agent tool made. `lanes.py sweep --apply` keeps them as `host-owned (Claude Code)`, and `lanes.py list --stale` lists all four as `closable, legacy`. Nothing in the plugin may remove them, so the integration tree never closes. The next `fanout.py prep` with the default lanes dir then refuses:
> `fanout: <root>/fanout/integration exists (an earlier run?); remove it with git worktree remove, or pass another --lanes-dir`
>
> **Expected**
> Once its branch is merged into the integration branch, a host-owned sub-agent worktree does not hold the integration tree open, and settle closes it. Or the plugin documents and supports how the host worktree is released, for example by recording it as landed.
>
> **Workaround used**
> The second wave used `--lanes-dir <root>/fanout-d`. Five agent worktrees and two integration trees are still on disk, waiting for the maintainer.
>
> **Ask**
> Treat a landed host-owned worktree as closed for the integration-close check, or have `land` mark it so. Print the exact cleanup the maintainer must run.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/lanes.py`: in `evaluate` row 4, a lane into the integration branch whose tree exists, is host-owned (`wtroot.host_owned`) and whose branch is an ancestor of the integration branch no longer counts as open. `do_close` prints `host-owned <path> landed in <b>; remove it yourself: git worktree remove <path>` for each such tree and never removes it. `fanout.py settle` prints the close message, so the line reaches the maintainer there unchanged; fanout.py is not edited. Truth table row 4 documents it.
- New selftest case `host landed` (`case_host_landed_integration`): an unmerged agent-y still holds the tree open alone; once only the merged agent-x remains, close removes the integration tree, keeps agent-x and prints its cleanup line.
- Negative control, run before the fix (same case): `FAIL: host landed: host landed: want agent-y alone open, got 1: lanes still open into wave/1: agent-x, agent-y | host landed: want the integration tree closed and '...', got 1: lanes still open into wave/1: agent-x`.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 8f08aaab` exit 0.
