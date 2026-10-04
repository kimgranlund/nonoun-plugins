<!-- role=plan-reviewer level=L1 model=fable effort=high -->
## Verdict
replan

## Findings
- step 4: acceptance criteria: the `(guard) bash plugins/sdlc-lite/scripts/check.sh` criterion runs at split time under `steps.py split --only`'s default 300 s guard timeout, and on this host it takes longer than that, so the split refuses with `plan defect` before any builder starts; the plan names the remedy (`--guard-timeout`) only under `## Risks`, and no step Do or chain instruction tells the conductor to pass it. A full split is not available because `step-1/` and `step-2/` hold role output (`steps.py:885-889`), so `--only 3 4` (or `--only 4`) and therefore the step 4 guards are unavoidable. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` exited 0 in 417 s (`uptime` load averages 12.16 17.22 19.73); planner-L3-2.md:284 measured 253 s and planner-L3-2.md:293 flags the 300 s default; `plugins/sdlc-lite/scripts/steps.py:28` (`--guard-timeout SECONDS (default 300)`), `steps.py:496-500` (timeout kills the span, rc None), `steps.py:519-522` (a timed-out guard is red and `Fail(... plan defect ...)`); `grep -rn 'guard-timeout' plugins/sdlc-lite/skills plugins/sdlc-lite/agents` printed nothing; `plugins/sdlc-lite/skills/chain/SKILL.md:40` routes a `--only` refusal to a replan.

## Missing decisions
None
