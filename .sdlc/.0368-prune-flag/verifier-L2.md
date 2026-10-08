## Verdict
fail

## Criteria
- (guard) dispatch.py selftest, `prune flag` cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` gives rc=0, `dispatch selftest: PASS`. It shows `ok: prune flag: prepare sets prune True for` scout, researcher, architect, archaeologist, planner, plan-reviewer, verifier and filer, `... False for builder`, `--no-prune turns a one-shot role off`, `--prune turns a builder on`, and `--prune with --no-prune is a usage error`. Can it go red: in a copy of the built plugin under /tmp I dropped `filer` from PRUNE_ROLES (dispatch.py:125) and the selftest went rc=1 FAIL.
- (guard) dispatch.py selftest, `prune record` and `prune` cases: pass. Evidence: the same run passes these cases: verifier queued with name/agent_id/role/level/recorded_at; builder not queued; a failed record (exit 1) not queued; a pending follow-up not queued; Follow-ups None queued; a `prune: false` dispatch not queued; another open attempt not queued; one `TaskStop task_id=<name>` line per entry; `--done` and `--add` edit the queue; an empty queue prints `prune: nothing queued`. The planner is queued because the list case requires exactly 3 entries. Mutations in the /tmp copy, each run alone: removing the attempt_open check, removing the follow_up_pending check, removing the `queue_prune` call in `record`, or ignoring `d['prune']` each turned the selftest rc=1 with the matching named FAIL lines. The wiring through `record` is covered, not only the helpers.
- (guard) fanout.py selftest: pass. Evidence: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` gives rc=0, `fanout selftest: PASS`. In the /tmp copy, changing `if kind == 'solo' and outcome == 'merged'` (fanout.py:1833) to `if kind == 'solo'` gave rc=1 with `case 23 land prune (T-0368): a land that did not merge queues nothing (negative control), got ['T-0001-solo', 'T-0003-solo', 'T-0004-solo']`.
- (guard) fleet_status.py selftest: pass. Evidence: rc=0 with `ok: pruning: an agent queued 45 minutes is under Stale or stuck with the prune command` and `ok: pruning: an agent queued 5 minutes is not listed (negative control)`. In the /tmp copy, PRUNE_STALE_S=60 min made the 45-minute case FAIL, and PRUNE_STALE_S=1 min made the 5-minute case FAIL.
- (guard) check.py, hook-selftest.sh, codex_roles.py and claude_roles.py generate --check: pass. Evidence: `check.py` rc=0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`. `hook-selftest.sh` rc=0, `hook selftest: PASS`. `codex_roles.py generate --check` rc=0, `Codex agent definitions verified`. `claude_roles.py generate --check` rc=0, `Claude agent definitions verified (22 files)`. `git diff --check` rc=0.
- (guard) conductor.md step 4 and the launcher skills' dispatch step carry the `dispatch.py prune` line: fail. Evidence: plugins/sdlc-lite/agents/conductor.md:36 has step 4 "Prune." (pass for conductor.md). `git grep -l "dispatch.py record"` across skills, counting `dispatch.py prune` per file, shows the line in agent, architect, bench, build, chain, dig, file, fix, fleet-retro, level-rubric, plan, research, scout and verify. It is missing from two skills that docs/references/sdlc-internals.md:146 ("## Launcher skills") lists as launchers and that dispatch one-shot roles:
  - plugins/sdlc-lite/skills/review-traces/SKILL.md:12. This is the same three-step "To dispatch a role ... `dispatch.py record` ..." text that the other ten skills got the prune line on, and the skill dispatches archaeologist, scout, verifier and planner (lines 44, 67, 102). Zero `dispatch.py prune` matches.
  - plugins/sdlc-lite/skills/fanout/SKILL.md:27, step 3: "run the verifier command prep printed ... spawn its JSON, run `dispatch.py record`". The verifier gets `prune: true`, but nothing tells the fanout parent to run `dispatch.py prune`. Zero matches in the file.
  - Steelman: the builder could say both skills defer to conductor.md "How you run roles", which now has step 4. That does not hold, because the other launcher skills also defer to conductor.md and still carry the line, and the criterion asks for the line in the skills. handoff-format and the Codex sdlc-lite adapter only mention `record`. They do not dispatch, so they are not counted.
- Live probe (spawn through prepare and record, `prune`, the printed TaskStop, agent leaves ListAgents): fail. Evidence: this is runtime behavior and I did not observe it. No probe record exists in /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout-f17/prune/.sdlc/0368-prune-flag (only base-sha, handoff.md and this verifier's dispatch and attempt files). The criterion line itself says the probe "was not completed by solo" and leaves it to the parent. A verifier cannot keep a background agent alive across turns to make the TaskStop call. An agent `probe-scout-L1` was listed at my start and was gone from ListAgents later. That suggests the parent ran a probe, but there is no recorded prepare/record/prune/TaskStop output to verify.

## Out of scope changes
None. Each changed file outside dispatch.py, fanout.py and fleet_status.py was checked:
- The six adapters/codex/agents/*.toml files are generated output. `codex_roles.py generate --check` passes, and their only en/em dash lines appear identically on both the - and + side of the diff.
- solo_run.py:122 `prune=False` is what Do (1) says for solo.
- fleet-status.schema.json adds the `pruning` key that fleet_status's schema selftest requires.
- docs/references/sdlc-internals.md is the contract reference for the new behavior.
- handoff.md gained the `## Acceptance criteria` the solo wrote.

## For the next attempt
1. Add the one-line prune step (after `record`, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prune` and make each `TaskStop task_id=<name>` it lists, then `--done`) to two places:
   - plugins/sdlc-lite/skills/review-traces/SKILL.md:12, matching the wording used in scout/plan/verify.
   - plugins/sdlc-lite/skills/fanout/SKILL.md:27, step 3, after its `dispatch.py record` for the lane verifier.
   Then rerun `codex_roles.py generate` / `--check` and `check.py`.
2. The live probe criterion needs the parent's observed run recorded in /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout-f17/prune/.sdlc/0368-prune-flag, for example a probe note with:
   - the `record` output line `prune: <name>`
   - the `dispatch.py prune` line `TaskStop task_id=<name>`
   - the TaskStop reply
   - a ListAgents listing without the agent

   Without that note the criterion cannot pass. As written it is a statement that the probe was not done, not a check.
