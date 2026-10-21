---
id: T-0687
title: "document merge.lock land queueing and add fanout.py queue"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor knows concurrent `fanout.py land` calls queue on `merge.lock` and can see the land order with one command, so it stops building `pgrep -f 'fanout.py land'` waiters.

## Intent
- Do: (1) in `plugins/sdlc-lite/skills/fanout/SKILL.md:53` and `plugins/sdlc-lite/skills/fanout/references/land.md:11`, replace "Land one branch at a time" with a sentence that concurrent `land` calls are safe and queue on `<lanes-dir>/merge.lock` in arrival order, so start each as its own background call and never poll with `pgrep`; keep every check.py item 24 and item 56 (Merge ops) phrase in those files, including `fanout.py land <branch>`. (2) Add `fanout.py queue [--lanes-dir DIR] [--integration BRANCH]` in `plugins/sdlc-lite/scripts/fanout.py`: `MergeLock.__enter__` (near line 1287) writes `<lanes-dir>/merge.lock.holder` (pid, branch, ticket, start time) and `__exit__` removes it; `queue` prints the holder line and one `waiting` line per other live `fanout.py land` process for that lanes dir (excluding its own pid), or `queue: empty`; add its row to the `## Arguments` table of `plugins/sdlc-lite/skills/fanout/SKILL.md`. (3) A selftest case: with a holder file written by a live process, `queue` prints it as `landing`; with none and no land running it prints `queue: empty`.
- Non-goals: `land --after T-NNNN`; changing lock order or the merge itself.
- Done when: the criteria pass.

## Context
Source: GitHub issue #37, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
The conductor built `while pgrep -f 'fanout.py land'; do sleep 20; done` waiters; each matched its own command line, so 3 background waiters started 22:39Z to 22:43Z sat 14 to 18 minutes until stopped by hand at 22:57Z. 37 queue waits and polls in 0.27.
On main, part of the doc claim is already fixed: `plugins/sdlc-lite/agents/conductor.md:56` says "the merge lock orders the lands", and `skills/fanout/references/land.md:11` says the background call lets "the merge lock order the lands". But the same land.md line and `skills/fanout/SKILL.md:53` still say "Land one branch at a time", which reads as "wait for one before starting the next". `land` takes `MergeLock(ctx['lanes_dir'] / 'merge.lock')` at fanout.py:2510; `MergeLock` (fanout.py:1287) is an fcntl flock, which records no holder, so `queue` needs the holder file.

## Constraints
The lock semantics are unchanged; a stale holder file (dead pid) is reported as `stale holder` and never blocks a land.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the new case, and the case fails with the change reverted.
2. `grep -c "Land one branch at a time" plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/skills/fanout/references/land.md` prints 0 for both files, and `grep -n "merge.lock" plugins/sdlc-lite/skills/fanout/SKILL.md` prints a line.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check 8624f984` exits 0.

## Outcome
Base: `git merge --no-edit main` was already up to date at 9e8e77c6; `git diff --check` ran against that base and against 8624f984.
- `fanout.py`: `MergeLock` takes holder fields and writes `<lanes-dir>/merge.lock.holder` (pid, cmd, branch, ticket, integration, start) on acquire, removes it before release; `land` passes branch, ticket and integration. New `fanout.py queue [--lanes-dir DIR] [--integration BRANCH]` prints `landing: <holder>` (or `stale holder: <holder>` for a dead pid), then one `waiting: pid=<pid> <args>` per other live `fanout.py land` for that lanes dir, oldest first, or `queue: empty`. Usage, docstring and selftest case T-0687 (landing, empty, stale holder, waiting, --integration filter, a stale holder never blocks the lock) added.
- Docs: SKILL.md step 4 and references/land.md replace "Land one branch at a time" with the concurrent-land sentence naming `<lanes-dir>/merge.lock`, `pgrep` and `fanout.py queue`; `queue` row added to the Arguments table.
- Conductor-added item (T-0659 defect on main): SKILL.md was 18,631 characters, over the 18,000 limit. Moved the "Lane lifecycle" paragraph word for word into new `references/lane-lifecycle.md` and the `rolling` roll paragraph into a `## Roll` section of `references/land.md`, each linked from its old place. SKILL.md is now 17,757 characters; every check.py phrase stays.
Checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0 (PASS); with the base fanout.py, `queue` exits 2 (usage) and `MergeLock(..., branch=...)` raises TypeError, so the case fails reverted. `grep -c "Land one branch at a time" ...` 0 and 0; `grep -n "merge.lock" .../SKILL.md` prints lines; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 8624f984` exit 0.
Open: flock wakeup order is not strictly FIFO, so the docs say the lands queue and merge one at a time, and `queue` lists waiters by start time.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (sonnet) · base: 9e8e77c6ac48
- Changed: see commits
- Commits: e456944 T-0687: document merge.lock land queueing and add fanout.py queue
- Check: 1 fanout.py selftest exits 0 with the new case, and the case fails with the change reverted: pass
- Check: 2 "Land one branch at a time" absent from SKILL.md and land.md, and SKILL.md has a merge.lock line: pass
- Check: 3 check.py exits 0: pass
- Check: 4 `git diff --check 8624f984` exits 0: pass
- Check: 5 Conductor note, SKILL.md under 18,000 characters and moved text word for word: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1297 MergeLock: the holder file... -> notes.md
