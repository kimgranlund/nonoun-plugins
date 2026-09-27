<!-- role=planner level=L3 model=fable effort=xhigh -->
Fixture worktree removed, tree back to its pre-probe state. Every criterion has now been run once (red-now ones red for the right reason, guards green now and red on a fixture), and the draft plan lints clean. Writing the plan.

## Goal
Rewrite planner rule 1 so the planner runs all of a step's criterion probes in one Bash call that prints each criterion's label, exit code, and at most the first 5 lines of output, then show with one live planner L2 run that turns fall below 11.5.

## Step 1: Batch the criterion probes in planner rule 1
level: L2
### Do
Edit rule 1 in `plugins/sdlc-lite/agents/planner.md` (item 1 under `## Criteria that can pass`). Keep every existing sentence of rule 1 word for word (the read-only probing sentence, the red-now-for-the-right-reason sentence, the `(guard)` green-now sentence, and the `steps.py split --only N` side-effect sentence). After the first sentence, add that the planner runs all of one step's probes in one Bash call, one `bash -c` per criterion so a red one never stops the rest, and that the call prints, for each criterion, its label, its exit code, and at most the first 5 lines of its output. Use the literal phrases `one Bash call`, `exit code`, and `first 5 lines`. The rule may add that rule 11's un-negated guard runs go into the same call; do not edit rule 11 or any other rule, and do not change the Merge steps section or the final-message format.

In `plugins/sdlc-lite/scripts/check.py`, add the entry `'one Bash call': ('agents/planner.md',),` to the `PLAN_DEFECT_DOCS` dict (next to `'gates green'`), so the phrase is guarded. Proven on a copy: with the entry present and the phrase absent, check.py fails with `plan-defect route missing "one Bash call"`.

Stale-context repair: in the repo-root `CLAUDE.md` Decisions bullet that says "The planner runs each criterion once before writing it (red now for new behavior, green now for a `(guard)`)", extend that sentence so it says the planner runs all of a step's probes in one Bash call that prints each criterion's label, exit code, and at most its first 5 output lines (the phrase `one Bash call` must appear). `.claude/agents/sdlc-lite-author.md` does not state rule 1 today, so leave it alone.

Change no model, effort, run.sh level table, or other agent file. Only these three files change in this step.
### Acceptance criteria
- `grep -qF 'one Bash call' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'first 5 lines' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'exit code' plugins/sdlc-lite/agents/planner.md`
- `grep -qF "'one Bash call': ('agents/planner.md'" plugins/sdlc-lite/scripts/check.py`
- `grep -qF 'one Bash call' CLAUDE.md`
- (guard) `grep -qF 'with read-only commands only; never run one that changes the tree or git state' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'must be red now, and red for the right reason' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qE 'is tagged .\(guard\). and must be green now' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'so a guard must be side-effect free' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qE '^11\. A .\(guard\). is a check that can go red\.' plugins/sdlc-lite/agents/planner.md`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/skills/level-rubric plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/agents/filer.md`

## Step 2: Gates green and live planner measurement
level: L2
### Do
Run `plugins/sdlc-lite/scripts/check.sh` from the worktree toplevel and fix any red that step 1 introduced (the check.py entry and the planner.md phrase must agree). It takes about two minutes here. A `hook selftest: FAIL: block-pattern-kill without role: exit 141` line is the known intermittent SIGPIPE flake tracked as T-0133, not a step 1 defect: rerun check.sh once and record both outcomes in Notes.

Then take one live measurement outside the repo:
1. `mkdir -p /tmp/t0132-probe`, then copy `.sdlc/the-steps-py-lint-accepts/handoff.md` (T-0137, an open ticket whose handoff is 865 bytes and whose change is one lint tweak in `steps.py`, so its criteria are red today) to `/tmp/t0132-probe/handoff.md`. Copy only that file, no plan or step artifacts.
2. From the worktree toplevel, run `plugins/sdlc-lite/scripts/run.sh planner L2 /tmp/t0132-probe/handoff.md` as a foreground Bash call with the Bash `timeout` at 900000 or more. run.sh loads this worktree's plugin through `--plugin-dir`, so the run uses the new rule 1, and it writes `planner-L2.md`, `planner-L2.log`, and a `runs.jsonl` line into `/tmp/t0132-probe/` only. Nested `claude -p` runs work here (fanout lanes launch role runs from a headless conductor the same way).
3. Record that run's `turns` and `cost_usd` from the last planner L2 line of `/tmp/t0132-probe/runs.jsonl` in the builder result's `## Notes`, for the filer, and count its Bash tool calls (`jq -R -c 'fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' /tmp/t0132-probe/planner-L2.log | sort | uniq -c`) so the filer can compare with the 8 Bash calls of this ticket's own planner-L2 run.

Nothing from `/tmp/t0132-probe` goes into the repo, and nothing is committed. Leave `/tmp/t0132-probe` in place for the verifier. Change no model or effort.
### Acceptance criteria
- `test -s /tmp/t0132-probe/planner-L2.md`
- `jq -se 'map(select(.role=="planner" and .level=="L2")) | length > 0 and (last.turns < 11.5)' /tmp/t0132-probe/runs.jsonl`
- The builder result's Notes state the measured run's turns and cost_usd, and they match the last planner L2 line of `/tmp/t0132-probe/runs.jsonl`.
- (guard) `! git ls-files --cached --others --exclude-standard | grep -q t0132-probe`
- (guard) `plugins/sdlc-lite/scripts/check.sh`

## Risks
- One live run is a sample of one. Turns vary from run to run: this ticket's own planner L2 run, on the old rule, took 9 turns (8 Bash calls) against the 11.5 average, so a pass does not prove the rule change and a run at 12 or more does not disprove it. If it fails, rerun once (run.sh writes `planner-L2-2.md` and appends a line; the criterion reads the last line) before treating it as a real fail, and let the filer note the variance.
- The live run spends model calls: roughly $0.5 to $0.8 at planner L2.
- `/tmp/t0132-probe` must survive until the verifier runs; a reboot between build and verify empties it.
- `check.sh` took 1:59 wall clock on this host with the tree idle. `steps.py split --only 2` runs it as a guard under the default 300 s guard timeout, so a host under fanout load could time it out and refuse the step as a plan defect; rerun the split when the host is quieter. The T-0133 SIGPIPE flake (`exit 141` in the hook selftest) can also turn the guard red once at split or verify time.
- A builder running `run.sh` inside its own role run nests `SDLC_ROLE`; run.sh overrides it to `planner` and unsets `SDLC_BASE_SHA`, and the hooks allow a foreground Bash call, but this exact nesting (builder → planner) has not been tried in this repo.
