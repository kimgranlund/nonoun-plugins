<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) selftest prints `ok: T-0473: base kept, A1 work committed: ...stores at_sha`: pass. Evidence: the grep -qxF span exits 0 on the built tree. A copy of the base-sha 4694d0cd scripts (git archive, in a temp dir) prints 0 T-0473 lines, so the check is red before the build.
- #2 (red) `...A1 original on an ancestor base is preserved`: pass. Evidence: grep exits 0 on the built tree; red on the base copy. A mutant with `same_lineage` reduced to equality fails this title and the T4 title.
- #3 (red) `...own pre-edit green defers to an earlier same-lineage pre-edit red: preserved`: pass. Evidence: grep exits 0 on the built tree; red on the base copy. A mutant that returns `green-baseline` before the earlier-red lookup fails exactly this title, so the check bites on the deferral rule.
- #4 (red) `...work committed after the base with no earlier red is green-baseline (control)`: pass. Evidence: grep exits 0 on the built tree; red on the base copy.
- #5 `...a control whose base is not an ancestor of HEAD is not bound (control)`: pass. Evidence: grep exits 0. A mutant with `same_lineage` always True fails exactly this title, so the control bites on the lineage rule.
- #6 (red) docstring has `at_sha` and `ancestor of HEAD`, and the sdlc-internals redck section has `at_sha`: pass. Evidence: the command exits 0 on the built tree. The same Python check on the base copy exits 1.
- #7 The builder report quotes a pre-fix selftest FAIL run whose misses include the T1, T2, T4 and T5 titles: pass. Evidence: builder-L3.md "Checks" lists exactly those four titles. Corroborated by the base copy (it has no T-0473 lines) and by the `equal` and `nodefer` mutant runs, which show the cases go red when the rules are absent. The builder did not record the red run live, so I did not re-observe the original FAIL listing; the corroboration is by mutants.
- #8 (guard) `redck.py selftest`: pass. Evidence: exit 0, "redck selftest: PASS", 29 ok lines. The only existing check whose title changed is the old line-394 one, which T2 replaces; the other existing checks keep their ok verdict.
- #9 (guard) `check.py`: pass. Evidence: exit 0, "ok: 19 role levels, 9 agents, 22 generated definitions checked".
- #10 (guard) `git diff --check $SDLC_BASE_SHA` on the two files: pass. Evidence: exit 0, no output.
- #11 (guard) scope guard: pass. Evidence: exit 0. Only redck.py and sdlc-internals.md differ outside `.sdlc`.
- #12 (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0 with SDLC_BASE_SHA set to 4694d0cd; the tail shows run, hook, shellcheck and plugin validate all ok.

Inherited-gate check not needed: no gate failed.

Process deviation: `process-deviations.md` is absent in the step dir, so there is no red-checkpoint deviation to account for.

## Out of scope changes
None. `git diff` touches only `plugins/sdlc-lite/scripts/redck.py` and `docs/references/sdlc-internals.md`. The untracked files are `.sdlc` task records. The stale builder wording in `agents/builder.md:28` was left alone, as the handoff directs.

Limitation: the tool-hook refused `git worktree add` (SDLC_TMP_WORKTREES unset), so the base comparisons used `git archive 4694d0cd` into a mktemp dir, not a git worktree. This does not affect the verdicts.

## For the next attempt
None
