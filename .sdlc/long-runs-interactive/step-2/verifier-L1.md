<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `check.py` exits 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` printed "ok: 18 role levels, 8 agents checked", rc=0. The new check in check.py requires the words interactive, run_in_background, notification and sleep in each of the three docs. The builder reported it went red first on "interactive", which I did not re-run.
- `check.sh` passes: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` ended with "steps selftest: PASS", "run selftest: PASS", "ok: shellcheck", "ok: plugin validate", rc=0. I saw no FAIL lines in the last 15 lines of output.
- `run_in_background` appears at least once in each doc: pass. Evidence: `grep -c` printed conductor.md:1, chain/SKILL.md:1, bench/SKILL.md:1.
- No em dashes in the four edited files: pass. Evidence: `grep -n "—"` on the four files returned no matches (exit 1).
- Each file states both cases and never to poll with `sleep`: pass. Evidence: the diffs show chain/SKILL.md, bench/SKILL.md and conductor.md each have a headless case (foreground, `timeout` at 600000 or more, no `run_in_background`, ending the turn abandons the run) and an interactive case (`run_in_background: true`, wait for notification, "Never poll with `sleep`", read `<role>-<level>.md`, ending the turn is safe). The author.md line 26 hazard matches and mentions `sleep`.
- The CLAUDE.md conditional (add a line only if it fits): pass. Evidence: no CLAUDE.md change in the diff. The builder's reason is that the "Headless runs" bullet is about `--dangerously-skip-permissions`, and I did not check that bullet myself.

## Out of scope changes
`plugins/sdlc-lite/scripts/check.py` was modified (a new long-run doc check). The step did not name it, though it enforces exactly what the step documents, so I treat it as a helpful guard, not a defect. It is not mentioned in the step's file list.

## For the next attempt
None
