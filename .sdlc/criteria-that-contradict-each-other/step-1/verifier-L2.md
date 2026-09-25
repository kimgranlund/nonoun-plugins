<!-- role=verifier level=L2 model=fable effort=medium -->
All criteria observed green, negative controls red where they should be; writing the verdict.

## Verdict
pass

## Criteria
- AC1 red guard refuses with `plan defect:` last line naming the span, no `step-1`: pass. Evidence: the criterion command exited 0; stderr was `steps: .../planner-L1.md step 1: (guard) criterion is red now (exit 1): test -e /nonexistent-sdlc-guard-x` then `plan defect: step 1 red guard: test -e /nonexistent-sdlc-guard-x; replan this step (/chain 3)`. Red at HEAD in a throwaway worktree: `NC AC1 rc=1` (HEAD wrote `step-1/handoff.md` instead of refusing).
- AC2 `sleep 30` with `--guard-timeout 1` refuses, `plan defect:` last line holds `sleep 30`, no `step-1`: pass. Evidence: exit 0; stderr `... criterion is red now (timed out after 1s): sleep 30` then `plan defect: step 1 red guard: sleep 30; ...`. At HEAD: `NC AC2 rc=1` (unknown option). Extra: `sleep 30 | cat` also refused in 1.23s wall, so the process-group kill reaches the pipeline grandchild.
- AC3 `split --help` mentions `--guard-timeout`: pass. Evidence: `AC3 rc=0`; at HEAD `NC AC3 rc=1`.
- AC4 at least 6 `ok: (n) ` selftest lines: pass. Evidence: `grep -c` printed `7`, `AC4 rc=0`; at HEAD `NC AC4 rc=1` (zero `(n)` cases).
- AC5 docstring holds `red guard`, `guard-timeout`, `HEAD^1`, `placeholder`: pass. Evidence: `AC5 rc=0`; at HEAD `NC AC5 rc=1`. steps.py:17-25.
- (guard) full `split` and `lint` execute nothing (marker absent, red guard does not refuse): pass. Evidence: `AC6 rc=0`. Biting variable is the `if only:` gate at steps.py:318; in a throwaway copy with that one line changed to `if True:` the criterion went red (`NC AC6 rc=1`, `ran` marker present, red guard refused) and `selftest rc=1`.
- (guard) `--only` with a green guard plus a `HEAD^1` guard and a `<placeholder>` guard writes the handoff: pass. Evidence: `AC7 rc=0`. Biting variable is `guard_skipped` (steps.py:220-221); with it returning `False` in a throwaway copy the criterion went red (`NC AC7 rc=1`, both spans reported red: `Could not access 'HEAD^1'`, `bash: tmp: No such file`) and `selftest rc=1`.
- (guard) `steps.py selftest`: pass. Evidence: `steps selftest: PASS`, `AC8 rc=0`.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0 from the repo root: pass. Evidence: `AC9 rc=0`; tail shows `order selftest: PASS`, `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.

Additional Do-list checks: guard cwd is the git toplevel for a task dir inside the repo (guard `test "$(pwd)" = "$(git rev-parse --show-toplevel)"` ran green from `.sdlc/zz-verif-*`, removed afterwards); red-guard stderr shows the indented output tail (`  boom`) between the per-guard line and the `plan defect:` line; `PLAN_DEFECT` constant unchanged at steps.py:71 and still used by the lint refusal at :149; `guard_spans` reuses `criteria_lines` and the shared `line_spans` (steps.py:185-213).

## Out of scope changes
None by the builder. `git status` also shows `.sdlc/criteria-that-contradict-each-other/handoff.md` modified (Goal, Constraints, Clarify gaps filled in) and untracked `planner-L2.md`, `runs.jsonl`, `step-2/handoff.md`; their mtimes (12:17, 12:21) predate the builder run (12:24) and they are the clarify and planner outputs of this task, not step 1 work. Only `plugins/sdlc-lite/scripts/steps.py` was edited, as the step required.

## For the next attempt
None
