<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) every S rule has a `_cases()` entry: pass. Evidence: the command exits 0 on the built tree. Against the base docs_check.py (extracted with `git archive ad35eaaa ...scripts`) the same check raises `AssertionError: ['S-1', 'S-7']`, so it bites. process-deviations.md records a retrospective red-checkpoint for both (red) criteria; I ran the base-side control myself, which is the failing-first proof.
- #2 (red) `standards` group gives exactly one S-5 error for a lowercase `must`: pass. Evidence: exit 0 on the built tree. At base it raises `AssertionError: []`, so it bites.
- #3 (guard) `docs_check.py selftest`: pass. Evidence: exit 0, prints "docs_check selftest: PASS" with positive ok and negative ok for every gate. The new `_cases()` entries (diff lines for S-1 to S-7) feed the `drops S-<n>` controls.
- #4 (guard) `docs_check.py --root .`: pass. Evidence: exit 0, "0 errors, 24 warnings (B-2a 10, B-3a 7, D-10 3, D-11 4)". No S finding on this tree.
- #5 (guard) scope guard with `SDLC_BASE_SHA=ad35eaaa...`: pass. Evidence: the `test -z "$(...)"` command exits 0. The variable was empty in the shell, so I exported the brief's base sha first.
- Extra, not a numbered criterion: `check.py plugins/sdlc-lite` exits 0 ("ok: 19 role levels, 9 agents, 22 generated definitions checked"), so the `DOCS_CHECK_NEEDS` pins are intact. The diff adds no em or en dash (grep exit 1).
- Spec behavior probes (builder claims checked by my own runs on temp fixtures):
  - S-1 fires with "front matter lacks baseline" when kpi.json requires `id, baseline`.
  - S-2 fires on an ID line with no `Acceptance:`, and stays silent on `- R-1:` followed by `Acceptance:`.
  - S-4 fires on a runbook whose only numbered line is inside a fence.
  - S-5 fires on `May` and stays silent on `may` inside a code span and on `MUST`.
  - S-7 fires on "Check - so Enforcement must be advisory" and on a broken assets link. A valid registry gives no S-7 finding.
  - Builder's "red was retrospective" claim confirmed by process-deviations.md.

## Out of scope changes
None from this step. The dirty paths outside docs_check.py (AGENTS.md, check.py, check.sh, prompt_lint.py, architect files) belong to step 1 and are inside the scope guard's allow-list.

## For the next attempt
None. Two notes, neither fails a criterion:
- `standards_rules` skips files directly under `docs/` (`'/' not in rel`). A `doc-type:` file at `docs/x.md` is not checked. I probed this with a top-level policy containing `must` and got no S-5. The handoff says "a docs Markdown file". Step 3 homes are in subfolders, so there is no impact now.
- A hook blocked `git worktree add` because `SDLC_TMP_WORKTREES` was unset in this session. I took the base-side controls from `git archive` into a temp dir instead. No worktree was created.
