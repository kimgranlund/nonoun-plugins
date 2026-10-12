<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest prints `ok: clarify: <rule> ` for all six rules: pass. Evidence: ran the criterion command, exit 0. `plan_check.py selftest` exit 0, "PASS (209 checks)", 27 `ok: clarify:` lines, no FAIL lines. The builder's pre-edit red control for this span is in step-1/red-checkpoint.jsonl (exit 1, red, phase pre-edit). Negative control: in a throwaway copy of the scripts under the tmp prefix I disabled the `CLARIFY_LIVE` branch of `clarify_defect`. The selftest then printed `FAIL: clarify: clarify-done-defect mutant "an item needs a live rehearsal"...` and `FAIL: clarify: clarify-done-defect the same rehearsal item without [owner: maintainer] is flagged`, so the mutant bites; the copy has been removed. The unrelated plan: failures in that copy come from running outside the plugin tree and do not appear in the real tree. The criterion's trailing space in the grep separates `clarify-done ` from `clarify-done-defect`.
- #2 `clarify --text x` exits 1 with `FAIL clarify-goal`: pass. Evidence: ran the command. rc=1; output `FAIL clarify-goal`, `clarify-non-goals`, `clarify-level`, `clarify-done`. The argparse choice and `run_check` entry are in the diff.
- #3 eight ask files non-empty and eight expected files pass `clarify --file`: pass. Evidence: ran the loop. It printed no MISSING or BAD line and printed `ok: clarify plan passes` 8 times. I read 04 (holds a `(gap: ...; default: ...)` delta), 05 (holds the Outcome, Measured by, Rubric and Negative control lines) and 06 (rehearsal item is `[owner: maintainer]`). The ask files each carry a `Source:` line. The README documents the replay steps.
- #4 07 and 08 expected files are one line each with the right prefix: pass. Evidence: ran the command, exit 0. The files read `already scoped: ...` and `follow-up: ...`.
- #5 (guard) scope diff against the base sha: pass. Evidence: ran the command, exit 0. `git status` shows tracked changes only in `plugins/sdlc-lite/scripts/plan_check.py`; the only untracked product path is `plugins/sdlc-lite/skills/clarify/evals/` (README plus 16 case files).

Dependents: `python3 plugins/sdlc-lite/scripts/check.py` exit 0 ("19 role levels, 9 agents, 22 generated definitions checked"), which covers items 42, 43 and 49. `git diff --check` exit 0. The `plan` kind code is untouched in the diff (additions only, plus the `expect()` label tweak, the docstring and the argparse choices).

## Out of scope changes
None. The diff touches plan_check.py and the new evals folder. The `.sdlc` records are role artifacts.

## For the next attempt
None
