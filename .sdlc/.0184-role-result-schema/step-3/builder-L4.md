<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: imports `results`. Deleted `first_word` and `REVIEW_VERDICTS`. `build_status_or_none`, `verdict_or_none`, and `review_verdict` now return `results.key_value(path, role)`. `build_status` and `verdict` raise `Fail` with the same messages as before.
- `plugins/sdlc-lite/scripts/steps.py`: new `invalid result` route:
  - `next_action` checks the newest builder, then the newest verifier that counts after it, with `results.structure_error`.
  - `review_action` checks the newest plan and the newest plan-reviewer that counts after it.
  - `split()` raises `Fail('invalid result: <path>: <reason>')` for a bad plan or plan-reviewer result. Both checks run before `rejected_by_review`, `read_goal`, and any write.
  - `cmd_next`, `cmd_resume`, and `cmd_review` share one new printer, `print_action`. For `invalid result` it prints the result line, then the fixed reason line, then the `read:` lines, and exits 0.
  - Module docstring updated for split, review, next, and resume.
- `plugins/sdlc-lite/scripts/steps.py` selftest: added the `hdr(name, text)` helper and used it in `task()`, `step()`, both `r_task()` helpers, and every direct write of a planner, builder, verifier, or plan-reviewer fixture (cases c, g, i, j, o, r, and swap). `guard_plan()` and `r_plan()` gained a `## Goal` line. No expectation changed.
- `plugins/sdlc-lite/scripts/fanout.py`: the selftest stub builder and verifier `printf`s now write a header line first. The filer stubs are unchanged.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: the `_builder_text` header now has `level=L2`. `_results_next` writes each verifier with a header (`_verifier_text` stays headerless). It also asserts that a builder result with no header gives `'invalid result'`.
- `plugins/sdlc-lite/scripts/results.py`: added `_steps_cases`, which runs `steps.py next` as a subprocess:
  - a headerless builder result gives `invalid result`;
  - a valid one gives `verify L1`;
  - negative control: copies of steps.py and order.py beside an accept-all results.py print `verify L1`.

  New imports: `shutil` and `subprocess`.

## Checks
- All 20 acceptance criteria, taken verbatim from the handoff and run with `bash -c`, `SDLC_BASE_SHA=f45649e…` (12 step criteria plus 8 guards): all exit 0, run twice (before and after the final docstring tidy).
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- `python3 plugins/sdlc-lite/scripts/traces.py selftest`: PASS
- `python3 plugins/sdlc-lite/scripts/results.py selftest`: PASS, including the 3 new `ok:` lines
- I wrapped `steps.main` and reran `steps.selftest()` to catch existing cases passing only by accident. None of its next, review, or split calls printed `invalid result` (0 hits, rc 0).
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0. `board.py selftest` and `order.py selftest`: PASS.
- `git diff --check` on steps.py, fanout.py, and traces/selftest.py: clean.
- Manual run on a temp fixture: next, resume, review, and split each print the `invalid result: <path>: <reason>` form; split exits 1 and writes nothing.

## Notes
- One behavior change comes from step 1's schema, not from this step. An `inherited red:` value now has to match `inherited red: .+` exactly. The old prefix check also accepted a bare `inherited red:` or `inherited red:x` with no space; both now read as statusless or no verdict. No existing fixture used those forms.
- Docs that describe the next and review actions (`docs/maintenance/sdlc-internals.md`, the `/chain` skill) were not touched, because they are outside this step's scope guard. Step 5 owns them.
- `lint`, `board.py`, `traces/sources/results.py`, and the other traces readers were left unchanged, as the handoff says.
- No commit was made. The changes to check.py, check.sh, run.sh, and run-selftest.sh in the tree come from step 2, not this step.
