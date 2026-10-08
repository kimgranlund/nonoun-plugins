# Verify T-0369, T-0371, T-0375, T-0376, T-0377, T-0378, T-0379, T-0380 on main

## Goal
Independently verify eight closed solo tickets on main at HEAD (builders were solo sonnet; you are a different family). Lane verifiers passed or the lanes fixed small gaps before merge (T-0376 and T-0378 had a lane verifier fail that the lane fixed; T-0378's two failing greps now match the selftest output). Confirm the final tree.

## Intent
- Do: for each ticket read its closed folder (.sdlc/.NNNN-*/handoff.md) and check each Done-when criterion with an observed command in a throwaway git archive copy of HEAD (git-initialised, under your tmp prefix; no worktrees), with a red control where a criterion is a guard. Codex host behavior cannot be run here, so judge no-model tests and mark live Codex claims unverified. T-0369, T-0376 and T-0378 also touch the dispatch and spawn path: confirm hook-selftest.sh, dispatch selftest and a throwaway prepare, record and prune cycle still work end to end with the new name format.
- Non-goals: editing anything.
- Done when: a pass or fail per ticket with the command and output per criterion.

## Context
T-0369 Done-when (.sdlc/.0369-messenger-spawn-persistent/handoff.md):
  - A hook-selftest case: a conductor spawning `sdlc-lite:messenger` passes, another role from a conductor still denies (observed failing first).
  - A parent-visible assertion: after a claim, the parent transcript contains a message from the poller within N seconds; a poller that only writes assistant text fails the test (observed failing first). Also a startup ping reaches the named parent address.
  - A messages.py or messenger selftest simulates two messages 13 seconds apart reaching the parent in one turn (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

T-0371 Done-when (.sdlc/.0371-guards-single-session/handoff.md):
  - Selftests: an attempt carrying the caller pid does not block the next prepare; an unrelated stray worktree or branch no longer warns in record while the role's own stray still does (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

T-0375 Done-when (.sdlc/.0375-lane-ledger/handoff.md):
  - A selftest with fixture lanes (one stale, one verified, one codex-owned) prints each column correctly (observed failing first).
  - `board.py --lanes` output without lanes is unchanged.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

T-0376 Done-when (.sdlc/.0376-lane-base-from-merge-base/handoff.md):
  - A selftest: a lane forked from a commit older than main HEAD records its fork point as the base; the scope-guard diff lists only the lane's files (observed failing first).
  - Interaction with T-0366 checked: prepare verifier and step-N/base-sha print the same sha for the same lane.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

T-0377 Done-when (.sdlc/.0377-split-only-tree/handoff.md):
  - A selftest: a handoff in a lane worktree whose main checkout lacks the file the guard greps reports ok when run with --only, and fails without the fix (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

T-0378 Done-when (.sdlc/0378-red-checkpoint-builder/handoff.md):
  - Tests cover: no tagged criteria, valid pre-edit controls, missing evidence, post-edit retrospective controls, and resumed work with evidence from an earlier attempt (observed failing first).
  - A run that completes without the checkpoint writes a process-deviation line that the verifier handoff and the filer read.
  - check.py, tickets.py check, the affected selftests, codex-selftest and both generate --check pass.

T-0379 Done-when (.sdlc/.0379-replan-prior-report-links/handoff.md):
  - Fixture tests (observed failing first): steps 3 and 4 reusing WIP and a step 9 fix citing its previous verifier all reference the correct superseded directories before runner input hashing; an absent path is refused; path reuse (a later new builder-L3.md must not satisfy a link meant for the previous build) is caught.
  - check.py, tickets.py check, steps and dispatch selftests, both generate --check pass.

T-0380 Done-when (.sdlc/.0380-messenger-lifecycle/handoff.md):
  - Selftests cover criteria 1, 3, 4 and 6 (observed failing first); 2, 5 and 7 are procedure text in agents/messenger.md and the mailbox AGENTS.md with a check.py phrase guard.
  - check.py, tickets.py check, messages.py selftest, both generate --check pass.

## Constraints
Read-only. No em or en dashes.
