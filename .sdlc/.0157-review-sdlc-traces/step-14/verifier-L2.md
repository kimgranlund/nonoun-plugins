<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene`: pass. Evidence: I ran it and it exited rc=0. Output listed 18 `ok: hygiene:` lines and ended with `traces selftest: PASS`.
- The `for d in ...` loop over the 7 detectors: pass. Evidence: I ran the loop body as separate greps and printed `MISS` on any failure. It printed no `MISS` line and reached `loop done`. Both `ok: hygiene: <d> fires` and `ok: hygiene: <d> quiet on control` appear for all 7 detectors.
- `test -f plugins/sdlc-lite/scripts/traces/detectors/hygiene.py`: pass. Evidence: I ran it and it printed `exists`. The file is 330 lines and defines `detect(rows, aux, thresholds)`.
- (guard) scope: pass. Evidence: the guard command exited 0 (`scope=0`). `git diff --name-only $SDLC_BASE_SHA -- . ':(exclude).sdlc'` lists only `.gitignore` (adds `__pycache__/`). The untracked files are all under `plugins/sdlc-lite/scripts/traces.py` and `plugins/sdlc-lite/scripts/traces/`.
- Checks can go red (checks-that-bite): pass. Evidence: I copied the scripts tree to `$SDLC_TMP_WORKTREES/mut` and stubbed each of the 7 detector functions in turn to `return []`. Each mutation made `selftest -k hygiene` exit rc=1, so every detector's case bites. I removed the copy afterwards.
- Behavior against the Do: pass. Evidence: `hygiene.py` implements all 7 detectors plus `reflog-gone`, with the cause hints and severities specified, for example `reflog-gone` at severity 1 and the legacy gate log at severity 1. The extra selftest cases are green:
  - The clean control fires nothing.
  - `reflog-gone` replaces `integration-reset` when the worktree is gone.
  - `integration-reset` needs both a reset and a lost-edit signal.
  - Mixed run ids give severity 2 at the first line of the second id.
- Wider regression: pass. Evidence: I ran the full `traces.py selftest`. It printed `traces selftest: PASS`. `git diff --check` returned 0. `git worktree list` shows no leftover fixture worktrees.

The builder's claims (7 detectors, 18 cases, all-family selftest PASS, mutation check, no leftover worktrees) were checked against my own runs above.

Steelman pass on the one weak point I considered filing: the hygiene control edits the step 6 prefixed fixture. Filing rebuttal: the handoff says the prefixed fixture "fires none", but its `beta-T-0002.log` mixes run ids. The builder handles this by rewriting it to a single id in the control and adding a separate case where the unchanged fixture fires severity 2. Both the control and the mixed-id case are green in my run, so the finding is dropped.

## Out of scope changes
None. `.gitignore` gained `__pycache__/`, which the scope guard allows. The step 6 fixtures moved into writers in `selftest.py`, which is inside the allowed `traces/` path. The step 6 assertions are unchanged, and the full selftest passes.

## For the next attempt
None
