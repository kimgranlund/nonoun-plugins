---
id: T-0601
title: "dispatch.py prune queues names that match no live agent"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0601-t0601
worktree: ../sdlc-lite.worktrees/T-0601-t0601
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every name `dispatch.py prune` lists is the live agent's spawn name, so `TaskStop task_id=<name>` stops it. Finished solos and verifiers get queued, and stale entries from earlier sessions don't pile up.

## Repro
2026-10-15, after `lanes.py finish` landed six lanes in this repo:
- `dispatch.py prune` listed `T-0565-solo`, `T-0596-solo` and the rest, but the live agents are named `0565-solo-L2` and so on (the dispatch `name`). `TaskStop task_id=T-0565-solo` failed with `No task found`.
- The queue also holds 18 entries from 2026-10-09 to 2026-10-14 sessions (`verify-0-22-2-recheck-verifier-L2`, `0440-architect-L1`, ...), which no TaskStop in this session can reach.
- The session had 49 finished teammates idle; none of the `prune: <name>` lines that `record` printed for verifiers appeared in the list.

## Expected
The queue uses the dispatch JSON's `name`. Entries carry the session id they were spawned in, and `prune` lists only the current session's, offering `prune --forget-stale` for the rest.

## Context
`dispatch.py` prune queue (`.sdlc/runtime/prune.json`, around line 1254). `fanout.py land` and `lanes.py finish` queue merged solos (conductor.md "Prune").

## Constraints
Never stop an agent whose attempt is still running.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0. Its new cases cover:
   - a solo landed through finish or fanout is queued under its dispatch `name`;
   - entries from another session are not listed, and `--forget-stale` removes them.

   The cases failed before the fix.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: dispatch.py:1255-1262 `prune_root` redirects the queue to the main checkout when called from a linked worktree. That goes beyond the Expected text but is covered by a selftest case and is consistent with queue entries having to survive lane removal. | note: entries with no `session` field are treated as stale whenever CLAUDE_CODE_SESSION_ID is set (dispatch.py `prune_lines`, `prune_forget_stale`). This matches the 18 old entries in the repro. | note: my cleanup of the empty directory /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0601-verifier-L2 and the scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0601-verifier-L2 was denied by the permission system. The throwaway worktree itself was removed with `git worktree remove`.) · verifier: verifier-L2 (sonnet) · base: 5498cf017198
- Changed: see commits
- Commits: 3b71bcb T-0601: dispatch.py prune queues names that match no live agent; 13999cd T-0601: record lane T-0601-t0601
- Check: 1 `dispatch.py selftest` exits 0 with new cases for a solo queued under its dispatch name and for o...: pass
- Check: 2 `git diff --check` exits 0: pass
