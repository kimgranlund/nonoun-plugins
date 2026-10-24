---
id: T-0764
title: "prep and record print no sweep lines for other repos"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep` and `dispatch.py record` print no `lanes sweep: unmarked:` lines for scratch dirs that belong to other repos; at most one summary line for this repo.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/lanes.py` and its docs.
- Also (T-0762 verifier note): add the missing control beside the `host removed` lanes.py selftest case: a removed host tree whose branch is NOT an ancestor of the integration branch must still hold the integration tree open (unmerged work is never orphaned); show it fails when the ancestor test in `evaluate` is dropped.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: 26 `lanes sweep: unmarked: /var/folders/.../sdlc-lite/...` lines from other repos on every prep and record.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `lanes.py` selftest case: the sweep run from repo A lists no unmarked dir that belongs to repo B; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `wtroot.mine(path, cwd)` (new) says whether a folder sits under this repo's scratch dir or tmp roots. `lanes.sweep` prints an unmarked folder only when it is this repo's, as one line (`unmarked: <path>`, or `unmarked: <n> folders, first <path>`); `dispatch.sweep_tmp` (the `record` path) skips another repo's unmarked folders. No folder is deleted that was not before.
- lanes.py selftest: `sweep other repo` case plus mutant `SWEEP-MINE` (own-repo test dropped): FAIL line `sweep other repo ('sweep',): want one unmarked line for this repo only, got 0: unmarked: 3 folders, first .../sweepother-tmp/sdlc-lite/other-deadbeef/probe-b`.
- T-0762 verifier note: case `host removed unmerged` plus mutant `HOST-GONE` (ancestor test dropped in `evaluate`): FAIL line `host removed unmerged: want agent-z alone holding the integration tree open, got 0: closed wave-1 (ancestor)`.
- Checks: `gate_lock.py run ... lanes.py selftest` exit 0, `dispatch.py selftest` exit 0, `wtroot.py selftest` ok, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check ec16815a` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: ec16815a0ed8
- Changed: see commits
- Commits: 6c88be3 T-0764: prep and record print no sweep lines for other repos
- Check: 1 A `lanes.py` selftest case: the sweep run from repo A lists no unmarked dir that belongs to repo ...: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py sel...: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:1475 record still prints one... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/wtroot.py:250 sweep, unchanged removes a... -> notes.md
- Follow-up: fix-now: docs/references/sdlc-internals.md:169 still says the sweep lists an... -> notes.md
