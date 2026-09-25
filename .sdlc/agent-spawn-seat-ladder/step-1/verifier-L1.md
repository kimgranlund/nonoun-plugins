<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Section heading `## Agent-tool spawns` exists in level-rubric: pass. Evidence: `grep -q '^## Agent-tool spawns' skills/level-rubric/SKILL.md` succeeded. The diff shows the heading as a newly added line, so the check was red before the change.
- Section names haiku, sonnet, opus, fork, effort, 7.13 and 1.82: pass. Evidence: a `grep -q` for each term against the text from the heading to the end of the file printed "ok" for all seven. `grep -c haiku` printed 1. All seven terms sit in lines the diff adds, so they were absent from the section before.
- Conductor has the Agent-tool spawn line and a level-rubric pointer: pass. Evidence: both greps succeeded on `agents/conductor.md`. The diff adds one bullet directly after the levels bullet: "Every Agent-tool spawn outside run.sh states `model` per the "Agent-tool spawns" section of the level-rubric skill."
- No em dashes in either file (guard): pass. Evidence: `! grep -q '—'` on both files printed "noem ok".
- `scripts/check.sh` passes (guard): pass. Evidence: I ran it from `plugins/sdlc-lite`. The order, fanout, run and hook selftests printed PASS, and the output ended with "ok: shellcheck" and "ok: plugin validate". I only read the last 15 lines, so I did not see the earlier selftests or any CLAUDE.md warning. Nothing in the tail showed a failure.
- `git diff --name-only` lists only the allowed files and no `scripts/` file: pass. Evidence: it lists `plugins/sdlc-lite/agents/conductor.md`, `plugins/sdlc-lite/skills/level-rubric/SKILL.md` and `.sdlc/agent-spawn-seat-ladder/handoff.md`. No `scripts/` file appears. The handoff is a ticket-tree artifact and is discussed below.

The section is prose and bullets with no table, and it covers every point the handoff lists.

## Out of scope changes
`.sdlc/agent-spawn-seat-ladder/handoff.md` is modified. It is a task-tracking artifact, not a plugin file, and the handoff's criterion only forbids `scripts/` files. Untracked `planner-L1.md` and `runs.jsonl` also sit in the task directory. No plugin file outside the two named ones changed.

## For the next attempt
None
