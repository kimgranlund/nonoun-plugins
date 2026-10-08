## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` passes, including the (r) notes-fix fold and real-defect replan cases: pass. Evidence: the run ends with `steps selftest: PASS` and exits 0. It prints these lines: `ok: (r) a replan review whose findings are all notes-fix passes: review says split, split appends them to the step Notes` (once for a replan review and once for a pass review), `ok: (r) negative: one real defect among notes-fix findings still replans and split refuses`, three `not notes-level and replans` negatives (`- plan: notes-fix: x`, `- step 1: x`, `None`), and `ok: (r) notes-fix reviews never count toward the one-replan cap`. I ran three negative controls on copies of plugins/sdlc-lite placed under the tmp prefix. (1) With the `if v == 'replan' and review_notes(path): return 'pass'` branch removed from review_verdict (steps.py:1815), the selftest FAILs on the replan-fold case and the one-replan-cap case. (2) With the split fold disabled (steps.py:1350 `if folded and folded.get(n):` changed to `if False:`), it FAILs both "all notes-fix passes ... appends them to the step Notes" cases. (3) With review_notes changed to ignore non-notes items (`return notes or None`), it FAILs `(r) negative: one real defect among notes-fix findings still replans and split refuses`. Each check fails when its mechanism is removed.
- plan-reviewer.md defines `notes-fix:` and its verdict rule; chain and handoff-format describe the fold: pass. Evidence: plugins/sdlc-lite/agents/plan-reviewer.md:37 defines a notes-fix, gives its line form, and says "it never forces `replan`; when every finding is a notes-fix the verdict is `pass`, and `steps.py split` appends each to its step's `### Notes`". plan-reviewer.md:53 adds the notes-fix line to the Findings template. plugins/sdlc-lite/skills/chain/SKILL.md:46 says such a review "reads as `pass` (never a replan): `split` appends them to that step's handoff under `### Notes`". plugins/sdlc-lite/skills/handoff-format/SKILL.md:132 says such a review "adds no entry and no replan: `steps.py split` writes those items under `### Notes`".
- check.py, `tickets.py --root .sdlc check`, and both `generate --check` pass: pass. Evidence: `check rc=0`, `tickets rc=0` (warnings only, about closed tickets and the flat layout), `claude_roles.py generate --check` prints "Claude agent definitions verified (22 files)" with rc=0, and `codex_roles.py generate --check` prints "Codex agent definitions verified" with rc=0. I also ran `bash plugins/sdlc-lite/scripts/check.sh`: rc=0, and all suites print PASS/ok, including the run selftest, the hook selftest, shellcheck, and plugin validate.

## Out of scope changes
None. Each file was checked:
- plan-reviewer-L1.md and the two sdlc-plan-reviewer-l1*.toml files are generated outputs. Both `generate --check` runs passed, so they match the generators. Their em dashes were already there: the removed toml lines carry them too, and the non-toml diff has no added em or en dash (`grep -P` rc=1).
- The `.sdlc/0364-replan-loop-small-gaps/handoff.md` diff only appends `## Acceptance criteria`, the criteria this run checks.
- base-sha and the `*.dispatch.json` / `*.attempt.json` files are untracked run bookkeeping.
- `git diff --check 65d5f3db` rc=0.

A note on the dependent trace: `git grep` shows review_verdict's other callers at steps.py:1895, 1934, 1941 and 1953 (review action, replan count, stop rule). The selftest (r) suite covers those paths and it passes. No other script reads plan-reviewer verdicts through review_verdict.

## For the next attempt
None
