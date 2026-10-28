---
id: T-0804
title: "lanes.py open --claim leaves the claim uncommitted in a repo that lands locally while main tracks an upstream"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
In a repository that lands lanes into main locally (`lanes.py finish` settles and closes on main) while main tracks an upstream, `lanes.py open --claim` commits the claim, so opening a lane is one command, as T-0800 intended.

## Repro
1. This repository: main tracks `origin/main`, lanes land locally, `.sdlc/config` has no landing setting.
2. `python3 plugins/sdlc-lite/scripts/lanes.py open t0803 --ticket T-0803 --kind solo --claim --by sdlc-lite-author`.

## Expected
`claim T-0803` is committed on main and the lane starts from it.

## Actual
2026-10-28: `not recorded: main tracks origin/main, so open writes no branch: or worktree: line in main`; the claim stayed as uncommitted edits to the ticket, `.sdlc/AGENTS.md` and the roadmap on main; the lane's copy still read `status: proposed`. The conductor committed `claim T-0803` by hand (14e302cf).

## Context
`plugins/sdlc-lite/scripts/lanes.py` open (`--claim`, around line 1502 to 1523) skips the commit when main tracks an upstream (T-0609: a PR repo lands through the upstream). T-0800 added `--claim`. A repo whose `finish` settles into main locally needs the commit; decide how open knows (a `.sdlc/config` line, or the same signal `finish`/`settle` already uses), keeping the T-0609 PR-repo behavior.

## Acceptance criteria
1. A lanes selftest case: in a repo that lands locally with main tracking an upstream, `open --claim` commits `claim <ids>` and the lane shows the ticket claimed; with the fix reverted it fails (state the FAIL line).
2. The T-0609 case (a PR repo) still writes no commit, and the docs that describe `--claim` say which repos commit.
3. lanes selftest through gate_lock exits 0, `check.py` exits 0.

## Constraints
The failing test lands before or with the fix.
