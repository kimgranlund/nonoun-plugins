<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
Method: each criterion's command span was run verbatim with `bash -c` on the built tree (`SDLC_BASE_SHA=f45649e`), then in a throwaway worktree at `$SDLC_BASE_SHA`, then against mutants of the built files overlaid on that worktree. "Base" below means the pre-build commit. The worktree and scratch files are removed; `git status` and HEAD are unchanged.

- 1 `steps.py next` on a headerless builder prints `invalid result: …builder-L2.md: `: pass. Evidence: rc 0 on the built tree; full output is `invalid result: <path>/builder-L2.md: first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header`, then `reason: the newest result does not match its results.py schema; stop and ask the user`, then `read: <path>`, exit 0. Red at base (rc 1). Red with the builder check removed from `next_action` (mutant A) and with the special printing disabled in `print_action` (mutant L).
- 2 `steps.py review` on a headerless planner: pass. Evidence: rc 0; output is `invalid result: …planner-L3.md: first line is not a … header`, the reason line, one `read:` line, exit 0. Red at base; red with the planner check removed from `review_action` (mutant B) while 3, 4, 5 stayed green.
- 3 `steps.py split` on a headerless planner exits 1, writes nothing: pass. Evidence: rc 0; stderr `invalid result: …planner-L3.md: …`, exit 1 for a dir target, `--only 1`, and a file target; a sha snapshot of the task dir was identical before and after (`15448b89dcd1`). Red at base; red with the planner check removed from `split()` (mutant C).
- 4 `steps.py review` on a headerless plan-reviewer: pass. Evidence: rc 0; output names `plan-reviewer-L1.md` and lists `read:` for the plan and the review. Red at base; red with the reviewer check removed from `review_action` (mutant D).
- 5 `steps.py split` on a headerless plan-reviewer exits 1, writes nothing: pass. Evidence: rc 0; stderr `invalid result: …plan-reviewer-L1.md: …`, exit 1, snapshot unchanged (`cec4b058122e`). Red at base; red with the reviewer check in `split()` replaced by `pass` (mutant E) while 2, 3, 4 and guard 16 stayed green.
- 6 results selftest prints `ok: negative control: an accept-all results.py lets steps.py next print verify`: pass. Evidence: rc 0; the line is at selftest output line 53. Red at base (no `results.py`). Red when `next_action` uses an inline header check instead of `results.structure_error` (mutant J), so the line proves the refusal routes through `results.py`.
- 7 results selftest prints `ok: steps.py next on a headerless builder result prints invalid result, not verify`: pass. Evidence: rc 0; output line 52, with `ok: steps.py next on a valid builder result prints verify L1` at line 54 and `results selftest: PASS`. Red at base; red under mutants A and L.
- 8 `! grep -qE "REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'" steps.py`: pass. Evidence: rc 0, and the file exists, so the negated grep is not vacuous. Red at base; red when a `REVIEW_VERDICTS` name is put back (mutant M). A runtime import confirms `first_word` and `REVIEW_VERDICTS` are gone and `section` is kept (`steps.py:967`, used by `fanout.py:634-636`).
- 9 builder header with `level=L2` in `traces/selftest.py`: pass. Evidence: rc 0; diff at `traces/selftest.py:340`. Red at base and with the base copy of the file (mutant H).
- 10 verifier header in `traces/selftest.py`: pass. Evidence: rc 0; `_VERIFIER_HEAD` is used only in `_results_next`, and `_verifier_text` stays headerless. Red at base and under mutant H.
- 11 `'invalid result'` in `traces/selftest.py`: pass. Evidence: rc 0; the new `step-nohead` assertion. Red at base and under mutant H. The assertion bites at runtime: mutant A turned `traces.py selftest` red.
- 12 builder header in `fanout.py`: pass. Evidence: rc 0; diff at `fanout.py:1066` and `1149-1152`, filer stubs unchanged. Red at base. With the base (headerless) `fanout.py` beside the built `steps.py` (mutant G), `fanout.py selftest` fails 6 inherited-red cases, so the fixture change is load-bearing.
- 13 (guard) valid builder gives `verify L1`: pass. Evidence: rc 0 on the built tree and at base. Its red form is criterion 1's fixture (header dropped), which prints `invalid result`.
- 14 (guard) header present, no Status gives `rebuild L2`: pass. Evidence: rc 0 on the built tree and at base. Red when `steps.py` calls `results.validate` instead of `structure_error` (mutant F).
- 15 (guard) valid L2 plan splits: pass. Evidence: rc 0 on the built tree and at base. Its red form is criterion 3's fixture.
- 16 (guard) valid plan plus passing review gives `split`, then split writes: pass. Evidence: rc 0 on the built tree and at base. Its red forms are criteria 4 and 5's fixtures.
- 17 (guard) `steps.py selftest`: pass. Evidence: `steps selftest: PASS`, 201 `ok:` lines, identical in name to base's 201 (`diff` empty), so no expectation changed. Red under mutant F (rebuild and reverify cases) and when `hdr()` is a no-op (mutant I).
- 18 (guard) `fanout.py selftest`: pass. Evidence: rc 0 on the built tree and at base. Red under mutant G.
- 19 (guard) `traces.py selftest`: pass. Evidence: rc 0 on the built tree and at base. Red under mutant A, and under mutant H with `steps.next_action agrees: ('done', 'invalid result')`, the failure the handoff predicted.
- 20 (guard) scope: pass. Evidence: rc 0 on the built tree and at base. Red with a stray untracked `scripts/zzz_stray.py` (mutant N).

Do items no criterion covers, checked by observed runs:
- **Verifier route in `next`:** a valid builder plus a headerless verifier prints `invalid result: …verifier-L1.md: …` with `read:` for the builder then the verifier, exit 0. Criteria-before-Verdict, a builder-role header, and an empty file also give `invalid result`. A header with no Verdict, or Verdict `maybe`, gives `reverify L1`. A valid pass gives `done`.
- **`resume`:** prints the step dir line, then the same three-part output, exit 0.
- **Other schema failures:** an empty builder, Notes before Changes, a planner without `## Goal`, a planner with Risks before Assumptions, and a reviewer with Findings before Verdict all give `invalid result`.
- **Kept routes:** Status `maybe` gives `rebuild L2`; a reviewer with no Verdict or `maybe` gives `review L1`; a `replan` review still gets split's old two-line refusal.
- **Stale results are not checked:** an invalid verifier older than the newest build gives `verify L1`; an invalid review older than the plan gives `review L1` and split succeeds.
- **`lint` unchanged:** `steps lint: ok` on a headerless plan.
- **Reader contracts:** base and built `build_status_or_none`, `build_status`, `verdict_or_none`, `verdict`, and `review_verdict` were compared on 6,226 real result files across the checkout and its worktrees, with 0 differences. `build_status` and `verdict` raise `Fail` with the exact old messages.
- **Builder's note on `inherited red:` confirmed:** `inherited red:` with nothing after it and `inherited red:x` now read as None (old: `inherited`). This follows from step 1's `key_value`, which the Do mandates. No real file uses either form.
- **Real results still route:** the built `steps.py` on this task's own run.sh-written results gives `done` for step-1 and step-2, `verify L3` for step-3, and `split` for review. `run.sh:451` is the only header writer and its format matches the schema.
- **Dependents:** `check.py` rc 0; `board.py selftest` and `order.py selftest` PASS. The traces readers go through the `_or_none` functions, covered by the comparison above and the traces selftest.
- **Docs:** the module docstring names the route for split, review, next, and resume (`steps.py:47-49, 103-104, 113-114, 122-124, 132-134, 142-143, 165`). The `/chain`, `/fix`, and internals docs are not updated; plan step 5 owns them (`planner-L3.md:247-271`) and this step's scope guard forbids them.
- **Coverage gap, not a criterion failure:** removing the verifier check from `next_action` (mutant K) left criteria 1, 7, 17, 18, 19 all green. The steps selftest has no `invalid result` case, so the permanent suites cover only the builder route in `next`. The verifier, planner, and plan-reviewer routes are held only by this handoff's criteria 2 to 5 and the runs above. The Do did not ask for those tests, so this is for a later step to decide.

## Out of scope changes
None.
- `check.py`, `check.sh`, `run.sh`, and `run-selftest.sh` are modified in the tree but are step 2's work: their mtimes (13:53 to 13:57) predate this step's `base-sha` file (14:04:44), and `step-2/builder-*.md` lists them. The scope guard allows them.
- `results.py` gained `_steps_cases` and the `shutil` and `subprocess` imports, as the Do asks.
- `.sdlc/0184-role-result-schema/runs.jsonl` is run.sh's own record and is excluded by the scope guard.

## For the next attempt
None
