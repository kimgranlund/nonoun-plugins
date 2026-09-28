<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Rewrite planner rule 1 so the planner runs all of a step's criterion probes in one Bash call that prints each criterion's label, exit code, and at most the first 5 lines of output, then show with one live planner L2 run that turns fall below 11.5.

## Step 1: Batch the criterion probes in planner rule 1
level: L2
### Do
Edit rule 1 in `plugins/sdlc-lite/agents/planner.md` (the numbered item under `## Criteria that can pass`). Add the literal phrase `one Bash call` and say that the planner runs all of one step's criterion probes in one Bash call. That call prints, for each criterion, its label, its exit code, and at most the first 5 lines of its output (use the words `exit code` and `first 5 lines`). Keep every existing sentence of rule 1 word for word: the read-only probing, red now and red for the right reason, the `(guard)` green now, and the `steps.py split --only N` side-effect sentence. Do not touch rule 11 or any other rule.

In `plugins/sdlc-lite/scripts/check.py`, add the entry `'one Bash call': ('agents/planner.md',),` to the `PLAN_DEFECT_DOCS` dict so the phrase is guarded.

Stale-context repair: in the repo-root `CLAUDE.md` Decisions bullet that says "The planner runs each criterion once before writing it", add that it runs one step's probes in one Bash call per step. Make the same edit in `.claude/agents/sdlc-lite-author.md` only if it states the same rule; it does not today.

Change no model, effort, run.sh level table, or other agent file.
### Acceptance criteria
- `grep -qF 'one Bash call' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'first 5 lines' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'exit code' plugins/sdlc-lite/agents/planner.md`
- `grep -qF "'one Bash call': ('agents/planner.md'" plugins/sdlc-lite/scripts/check.py`
- `grep -qF 'one Bash call' CLAUDE.md`
- (guard) `grep -qF 'with read-only commands only; never run one that changes the tree or git state' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'must be red now, and red for the right reason' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'tagged `(guard)` and must be green now' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF '11. A `(guard)` is a check that can go red.' plugins/sdlc-lite/agents/planner.md`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/skills/level-rubric plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/agents/filer.md`

## Step 2: Gates green and live planner measurement
level: L2
### Do
Run `plugins/sdlc-lite/scripts/check.sh` from the repo toplevel and fix any red that step 1 introduced.

Then take one live measurement outside the repo:
1. `mkdir -p /tmp/t0132-probe`, then copy `.sdlc/.0017-board-order-by-id/handoff.md` (a small size-S ticket) to `/tmp/t0132-probe/handoff.md`. Copy only that file, no plan or step artifacts.
2. From the worktree toplevel, run `plugins/sdlc-lite/scripts/run.sh planner L2 /tmp/t0132-probe/handoff.md` in the foreground. run.sh loads this worktree's plugin through `--plugin-dir`, so the run uses the new rule 1. This writes `planner-L2.md` and a `runs.jsonl` line into `/tmp/t0132-probe/`.
3. Record that run's `turns` and `cost_usd` from `/tmp/t0132-probe/runs.jsonl` in the builder result's Notes, for the filer.

Nothing from `/tmp/t0132-probe` goes into the repo, and nothing is committed. Change no model or effort.
### Acceptance criteria
- `test -s /tmp/t0132-probe/planner-L2.md`
- `jq -se 'map(select(.role=="planner" and .level=="L2")) | length > 0 and (last.turns < 11.5)' /tmp/t0132-probe/runs.jsonl`
- The builder result's Notes state the measured run's turns and cost_usd, and they match the last planner L2 line of `/tmp/t0132-probe/runs.jsonl`.
- (guard) `test -z "$(git ls-files --others --exclude-standard -- .sdlc | grep t0132)"`
- (guard) `plugins/sdlc-lite/scripts/check.sh`

## Risks
- One live run is a sample of one. Turns vary from run to run, so a run at 12 or more could fail step 2 even though the rule works. If that happens, rerun once before treating it as a real fail.
- The live run spends model calls: roughly $0.5 to $0.8 at planner L2.
- It needs `/tmp` to survive until the verifier runs.
- A builder running `run.sh` inside its own role run nests `SDLC_ROLE`. The hooks still allow a foreground Bash call, so this should work, but it has not been tried.
