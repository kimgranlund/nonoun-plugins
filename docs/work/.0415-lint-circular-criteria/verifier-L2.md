<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) selftest prints the three `(circ)` lint labels: pass. Evidence: I ran the criterion's command on the built tree and it exited 0 (`red1=0`). The selftest output has `ok:` lines for all three labels (lines 397-399 of the saved output). In a detached worktree at `$SDLC_BASE_SHA`, selftest has 0 `(circ)` lines, so the check goes red before the change.
- #2 (red) selftest prints the two refusal-record labels: pass. Evidence: the criterion's command exited 0 (`red2=0`). Lines 400-401 are `ok: (circ) a lint refusal appends one line to refusals.jsonl in the task dir` and `ok: (circ) the same refusal of the same plan is written once`. The base worktree has no `(circ)` lines, so the check goes red there.
- #3 (guard) `steps.py selftest`: pass. Evidence: rc=0 with 406 `ok:` lines and `steps selftest: PASS`. This includes the builder's two extra cases, a split red-guard/red-first record and a read-only task dir.
- #4 (guard) scope: pass. Evidence: the criterion's command exited 0 (`guard=0`). `git status` shows only `steps.py` modified outside `.sdlc`.
- Runtime check beyond selftest, in a throwaway plan in a tmp dir:
  - A criterion `grep -q pass step-1/verifier-L2.md` in step 1 is refused. The finding line and the hint line `move it to a later step, or declare it held with a trailing [stage: ..., owner: ...] clause` are both printed, rc=1.
  - Exactly one JSON line was written to `refusals.jsonl` with keys `ts`, `tool` (`steps.py lint`), `plan` (`planner-L2.md`), `step` (1) and `text`.
  - A second identical lint run left the file at 1 line.
  - After adding a trailing `[stage: integration; owner: integration]` clause, lint printed `steps lint: ok`, rc=0.
- False-positive sweep: I copied every `.sdlc/*/planner-L*.md` plan into tmp dirs and linted each. Zero were flagged for the new finding.
- Equivalence of the span loop: `command_spans` is defined as `criteria_lines` + `line_spans` (steps.py:620-622). `lint_steps` now iterates the same pairs, so span coverage is unchanged.
- Docstring: the module docstring's split and lint paragraphs are updated (diff hunks at 74-90, 129-165). The diff contains no em or en dashes (grep returned nothing).

## Out of scope changes
None. The only tracked change is `plugins/sdlc-lite/scripts/steps.py`. The untracked `.sdlc/0415-*` files are run records under `.sdlc`, which the scope guard excludes.

## For the next attempt
None. One cosmetic nit that does not fail the step: the diff changed `folded = review_findings(...)` to `folded =review_findings(...)` at steps.py `split`, which is a stray whitespace edit on an unrelated line.
