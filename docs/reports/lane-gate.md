# run.sh lane gate (T-0274)

Branch `lane-gate`, from main at 8d45cb6. Claims below are backed by command output seen in this session.

## What changed

- `scripts/run.sh`: a planner, builder, or plan-reviewer run on a task or step handoff of a ticket (an `id:` line) runs `steps.py lane --check <task dir>`. Lane solo prints the `solo_run.py run --task-dir <dir> --tier <S|M|L> --brief ...` command and exits 5 with no attempt record. `SDLC_LANE_OVERRIDE="<reason>"` proceeds, appends `lane override: <reason>` once to skips.md (not on a dry run), and adds `lane_override` to the runs.jsonl line.
- Not gated: other roles, a handoff with no ticket id, lanes other than solo, a skips.md whose last `lane:` record is not solo, lifecycle children.
- `scripts/steps.py`: `lane --check` prints the lane and writes nothing.
- `scripts/fanout.py`: sets the override for `--lane full` and `--driver` runs.
- `skills/fix/SKILL.md` step 3 records `lane: fix` and the planner and filer skips; `agents/conductor.md` gets one line on exit 5; `docs/references/sdlc-internals.md` describes the gate.
- Two budget-gate fixtures in `run-selftest.sh` moved from size S to size L so they still reach the budget gate.

## Red then green

- Before the gate, the new `run-selftest.sh` case failed: `run selftest: FAIL: lane gate: planner on a size S ticket exited 0, want 5`.
- After the gate, `bash plugins/sdlc-lite/scripts/run-selftest.sh` printed `run selftest: PASS`.
- The verifier reproduced the red with main's run.sh in a temporary worktree (rc=1, same message).

## Verifier

- Round 1 (fable L3): fail on two items. `fanout.py` never set the override for `--driver`, and `/fix` step 3 dead-ended on exit 5. Both fixed in e022c6e, plus no skips.md write on a dry run.
- Round 2, failed criteria only (a first attempt hit the 25 minute limit and was rerun): criteria 5 and 8 pass; criterion 7 fail, because the new `lane: fix` line made `tickets.py close --reason` refuse without `## Skipped` entries for planner and filer. The verifier named the fix (two skip lines in SKILL.md step 3) and observed that shape close with exit 0 in its own throwaway repo.
- The SKILL.md fix was applied after round 2 and not re-run through a third verifier (replan cap). Verdict records: `.sdlc/.0274-lane-gate/verifier-L3-first.md.txt`, `verifier-L3-second.md.txt`.

## Checks run

See the commit message of the closing commit and the final report for the exact check.sh result from a path without "claude".
