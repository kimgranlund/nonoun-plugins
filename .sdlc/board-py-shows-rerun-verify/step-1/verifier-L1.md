<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q "ask the user" plugins/sdlc-lite/scripts/board.py`: pass. Evidence: the command printed the G1 marker and exited 0. The string is in the new `step_row` branch and in the docstring.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: pass. Evidence: it printed `board selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: exit 0.
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/steps.py` (guard): pass. Evidence: exit 0, and `git status` does not list steps.py.
- `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0; the tail shows the run, hook, live-probe, shellcheck and plugin validate checks all passing.
- The selftest output contains a passing case for one no-verdict result ("rerun verify") and one for two consecutive ones ("stop" / "ask the user"): pass. Evidence: the selftest printed these lines.
  - `ok: one no-verdict verifier: no verdict · builder L1 · verifier L1, rerun verify`
  - `ok: two no-verdict verifiers: stop · no verdict x2 · builder L1 · verifier L1, ask the user`
  - `ok: fail then rebuild counts only later no-verdicts: stop · no verdict x2 ... ask the user · attempt 2`
- The new cases can go red: pass. I copied the new `board.py` into a throwaway worktree at HEAD and changed `if n >= 2:` to `if n >= 99:`. The selftest then reported FAIL on the two-consecutive case and the x2-after-rebuild case, each showing `rerun verify`. The single no-verdict case stayed ok, which is correct.
- Case (c) has a second half: pass. Evidence: a fixture with one no-verdict after a fail and a rebuild still says `no verdict ... rerun verify`. Adding a second no-verdict after the build gives `stop x2`. So a no-verdict before the newest build is not counted.
- Docs: pass. The `board.py` docstring is updated (diff). `grep -n "no verdict\|no-verdict"` on CLAUDE.md and `skills/board/SKILL.md` matched nothing that describes the board's rendering, so leaving them unchanged is correct. The builder's note says CLAUDE.md's "no verdict" text is in the `steps.py` line, but the grep did not surface it. This does not change the outcome, because the handoff only asks for those docs to change if they mention the rendering.

## Out of scope changes
None. The diff touches only `board.py` and `.sdlc/board-py-shows-rerun-verify/handoff.md`. The handoff.md change fills in the Goal and Constraints placeholders, which is planner bookkeeping and not project code. The rest is untracked `.sdlc` artifacts.

## For the next attempt
None
