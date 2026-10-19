---
id: T-0129
title: "Worktrees created from inside a script or program a role runs..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0107
---

## Goal
When a role run leaves behind a git worktree or branch it created outside the Bash tool text the block-stray-worktree hook sees (from a python script, make target, or other program), run.sh reports it at run end, so the conductor and user learn about the stray instead of finding it later.

## Intent
Literal ask: add run-end detection or reporting for stray worktrees and branches created from inside a script or program a role runs.
Deltas:
- report vs remove: defaulted: report only (stderr line naming each stray worktree path and branch, plus a field on the run's runs.jsonl line); never remove or delete anything outside this run's own $SDLC_TMP_WORKTREES prefix, which cleanup already owns.
- baseline: defaulted: snapshot `git worktree list --porcelain` and local branches (`refs/heads`) before the role starts, compare after the role ends and after the existing tmp-prefix cleanup; only worktrees and branches that appeared during the run count.
- concurrency: defaulted: concurrent fanout lanes or other role runs can add worktrees and branches during a run (see the run.sh header); the report says "appeared during this run" and does not claim this role made them, and it never fails the run (exit code unchanged). (gap: no way to attribute a new worktree to this role with certainty; default: report all that appeared, excluding this run's own prefix.)
- dry run: defaulted: SDLC_DRY_RUN=1 takes no snapshot and prints nothing new.
Do: in scripts/run.sh, snapshot worktrees and local branches before the role runs; at exit (after cleanup_worktrees) list worktrees not under this run's prefix and branches that were not present before, print one stderr line each (`run.sh: stray worktree appeared during this run: <path> [<branch>]`, `run.sh: stray branch appeared during this run: <branch>`), and record them in the runs.jsonl line when that line is written after the role; cover it in the run selftest (a stub role that creates a worktree and a branch through a script is reported; a run that creates none prints nothing; a worktree under the prefix is not reported); update CLAUDE.md, the sdlc-lite-author agent, and any doc describing run.sh's exit behavior (and the block-stray-worktree hook docs, noting the run-end report covers what the hook cannot see).
Non-goals: deleting or moving stray worktrees or branches; changing block-stray-worktree.sh; changing fanout.py's own worktrees.
Done when: the run selftest proves a script-created worktree and branch are reported at run end and a clean run reports nothing, and scripts/check.sh passes.

## Context
Follow-up from T-0107 (role-throwaway-worktrees-created-outside/filer-L1.md):

Worktrees created from inside a script or program a role runs (python, make) bypass the new block-stray-worktree hook, which only sees Bash tool text; add run-end detection or reporting for stray worktrees and branches.

## Constraints
run.sh's exit code, required-section check, and tmp-prefix cleanup are unchanged. The report never removes anything. scripts/check.sh stays green.

## Plan review
- step 3 split --only 3: guard `bash plugins/sdlc-lite/scripts/check.sh` timed out at the 300s default with every selftest PASS (host load); reran with `--guard-timeout 1200`, green in 218s. Not a plan defect, no replan.
- step 1 builder run: the builder edited scripts/run.sh while that run.sh was executing, so bash failed at line 214 (`rest: unbound variable`) after the role finished and builder-L3.md was not saved; the conductor recovered it from builder-L3.log with run.sh's own jq save logic.
