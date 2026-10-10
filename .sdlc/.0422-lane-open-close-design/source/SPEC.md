# lane-open and lane-close: spec for sdlc-lite

Source: the 2026-10-09 page-css goal in gen-ui-kit. 43 solo lanes plus 8 integration branches ended as about 440 worktrees, 887 branches and 24 GB because nothing closed a lane. Cleanup took one long session. Working scripts exist in ~/.claude/lane/ (env.sh, lane-open.sh, lane-close.sh, lane-wait.sh), tested end to end on 2026-10-10.

## Problem
1. Lanes opened by prep.sh were never removed. Merge was the last step anyone owned.
2. Lanes lived inside the main checkout (main/.git-worktrees), so grep, vitest, tsc and watchers walked into 440 copies, and Node resolution borrowed the parent's node_modules (hiding the missing install).
3. Port choice was by hand and collided (two lanes on 7431).
4. Squash merges leave no ancestor link, so a branch reaper could not tell merged from unmerged (421 false "unmerged" warnings).

## Skill: lane-open
Input: lane name. Does, in order:
1. Refuse a name already used as a worktree or branch.
2. Fetch origin; add worktree at <root>/lanes/<lane> on branch lane/<lane> off origin/main. Lanes live outside every checkout.
3. Assign a free port in 7400-7699 (not in another lane's .lane.json, not listening) and write .lane.json {lane, branch, port, opened}.
4. pnpm install, then bootstrap-worktree.mjs under Node 22 (a sibling lane has no parent node_modules; bootstrap fails on a missing yaml package before install).
5. Print path and port. The solo dispatch (solo_run.py) runs after this.

## Skill: lane-close
Input: lane name, optional --discard. Does, in order:
1. Refuse if the tree has uncommitted changes (ignoring .sdlc/ and .lane.json).
2. Refuse unless the branch is an ancestor of origin/main OR every file it changed equals origin/main's version (catches squash merges, including ones made on a former host). --discard skips both.
3. Copy .sdlc/ to the archive; append "<branch> <sha>" to closed-lanes.txt so any branch can be recreated.
4. Remove the worktree, delete the branch, prune.

## Script: lane-wait
Input: lane, PR number. Enables auto-merge on green, polls the PR, and on MERGED calls lane-close. On CLOSED it leaves the lane open.

## Where it hooks into sdlc-lite
- fanout.py prep/land: call lane-open per lane and lane-close after land.
- steps.py / dispatch.py: a ticket closed with tickets.py close should print a "lane still open" line if its worktree exists.
- fleet-retro / board: list lanes older than 10 days with no open PR as stale.
- Idle-agent prune and lane-close should run together: when a lane closes, queue its solo agent for dispatch.py prune.

## Rules worth enforcing (checks, not prose)
- No lane worktree under any checkout. A check fails if `git worktree list` shows a path under main/ or dev/.
- A branch older than 10 days with no open PR and no unique content is reaped on the next conductor run.
- Ports for probes come only from .lane.json.

## Known gaps
- lane-wait's merge call (`gh pr merge --auto`) is untested; the earlier waiter script was lost and merged as the owner's account on green.
- env.sh pins a Node 22 path found through npx; replace it with a version-manager lookup.
- reap-branches.mjs crashes when a local branch name equals a remote-tracking ref (pr/4297 vs refs/remotes/pr/4297).
