<!-- role=verifier level=L2 model=fable effort=medium -->
All evidence is in. Writing the verdict.

## Verdict
pass

## Criteria
- `build L2` with no builder result: pass. Evidence: `/tmp/crit.sh` c1 → `c1 PASS` in the working tree; `c1 FAIL rc=1` in the `git worktree add --detach /tmp/sdlc-nc-verify HEAD` copy (no `next` subcommand at HEAD).
- `verify L1` after a done L2 build: pass. Evidence: c2 PASS here, FAIL at HEAD.
- `verify L3` after a done L4 build: pass. Evidence: c3 PASS here, FAIL at HEAD.
- `replan` on a blocked builder: pass. Evidence: c4 PASS here, FAIL at HEAD.
- `done` on a pass verdict: pass. Evidence: c5 PASS here, FAIL at HEAD.
- `rebuild L2` on one counted fail: pass. Evidence: c6 PASS here, FAIL at HEAD.
- `replan` on a plan-defect fail: pass. Evidence: c7 PASS here, FAIL at HEAD.
- `bump L3` on two counted fails at L2: pass. Evidence: c8 PASS here, FAIL at HEAD.
- `rebuild L3` after a bump: pass. Evidence: c9 PASS here, FAIL at HEAD. Full stdout observed: `rebuild L3` / `reason: first counted fail at build L3` / `read: .../builder-L3.md` / `read: .../verifier-L2.md`, rc=0.
- `stop` on two counted fails at L5: pass. Evidence: c10 PASS here, FAIL at HEAD.
- `verify L1` with a stale verifier older than the rebuild: pass. Evidence: c11 PASS here, FAIL at HEAD.
- Error on a dir with no handoff.md and no results (rc 1, empty stdout, `steps next: ` on stderr): pass. Evidence: c12 PASS here, FAIL at HEAD. Extra probe of every error kind (missing dir, no handoff, no `level:` line, bad Status, bad Verdict): each `rc=1 stdout=[] unchanged=y stderr_lines=1`, stderr starting `steps next: `.
- Writes nothing (snapshot equal): pass. Evidence: c13 PASS here, FAIL rc=2 at HEAD. Mutant C (a copy of steps.py made to write `.touched`) turned the selftest's `next writes nothing` and all four `next error:` checks red.
- `selftest | grep -c '^ok: next '` ≥ 14: pass. Evidence: 19 lines, listed with `nl` (build, verify L2, verify L4, replan blocked, replan plan-defect, done, rebuild, bump, rebuild after bump, plan-defect not counted, stop, stale verifier, file times ignored, five error kinds, writes nothing). c14 PASS here, FAIL at HEAD.
- (guard) `selftest | tail -1` is `steps selftest: PASS`: pass. Evidence: c15 PASS here and at HEAD. Bites: mutant B (`is_plan_defect` branch disabled) → `steps selftest: FAIL ... next replan: a fail whose next-attempt note starts "plan defect:" replans`; mutant D (L4 verifier mapping broken) → FAIL on `next verify: build L4 done, no verifier -> verify L3`.
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/order.py`: pass. Evidence: c16 PASS; `git diff --stat` lists only `plugins/sdlc-lite/scripts/steps.py`.
- (guard) split and lint `ok:` lines identical here and at HEAD: pass. Evidence: `/tmp/now.txt` and `/tmp/head.txt` both 22 lines, `diff` printed `IDENTICAL`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `check rc=0`, tail `run selftest: PASS / hook selftest: PASS / ok: shellcheck / ok: plugin validate`.
- Docstring and argparse document `next`: pass. Evidence: steps.py:5 `next <step dir> | selftest}`; `steps.py --help` shows `{split,lint,next,selftest}` and the `next` help line; `steps.py next --help` → `usage: steps.py next [-h] step_dir`.

## Out of scope changes
None. `git status`: only `plugins/sdlc-lite/scripts/steps.py` modified; the untracked `.sdlc/add-a-steps-py-next/` entries are the task's own artifacts. Throwaway worktree removed and pruned; `git worktree list` shows only main and tickets-15.

## For the next attempt
None. One observation for the record, not a failure: mutant A (L3 → verifier L3 instead of L2) left the selftest green because the handoff's case list has no L3 → L2 verify case; the real behavior is correct (observed `verify L2` for a done L3 build). Step 2 or a follow-up could add that one case.
