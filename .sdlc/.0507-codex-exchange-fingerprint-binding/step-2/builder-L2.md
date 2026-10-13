<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/adapters/codex/instructions.md`: the two `codex_exchange.py` paragraphs and the "Profile handshake" paragraph now describe the `profile_fingerprint` binding, the exit 2 refusal, the `--failed` answer, and the limits of the final-report check.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/docs/references/codex-role-execution.md`: "Report envelope" gains the binding paragraph, the two `runs.jsonl` keys (`profile_fingerprint`, `profile_check`), and the three new tests as the regression. The native transport paragraph points to it.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/adapters/codex/agents/sdlc-*.toml`: all 28 regenerated with `codex_roles.py generate`, none hand-edited.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md`: new report with the five cases, the step 1 baseline failure output, the gates, and criterion 7 as unverified.

## Checks
- Criterion 1, both `grep -qF` on `instructions.md`: exit 0.
- Criterion 2, `grep -qF profile_fingerprint docs/references/codex-role-execution.md`: exit 0.
- Criterion 3, `grep -qF profile_fingerprint plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`: exit 0.
- Criterion 4, `test -f` and `grep -qi unverified` on the report: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0, `Codex agent definitions verified`.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: exit 0, `Ran 6 tests in 18.788s`, `OK`.
- (guard) `python3 scripts/check-packaging.py`: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`. Rerun after the last report edit: PASS.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: exit 0. The report is untracked, so it also got `git diff --no-index --check /dev/null <report>`: no findings.
- (guard) `git diff --quiet "$SDLC_BASE_SHA"` on the astra review report and its folder: exit 0.
- (guard) scope guard, with `SDLC_BASE_SHA` exported in the command: holds. 35 paths differ outside `.sdlc`: the 28 TOMLs, the four step 1 scripts, `instructions.md`, `codex-role-execution.md`, and the report.
- By-hand run of the five cases with a real waiter process and the `codex_exchange.py` CLI in a temp directory (removed afterwards):
  - Missing: exit 2, no response file, request stays `waiting`.
  - Stale: exit 2, request stays `waiting`.
  - Current: exit 0, waiter exit 0, `profile_check: ready`.
  - Changed after dispatch: the live fingerprint is refused with exit 2, then the dispatched binding is accepted with exit 0.
  - `--failed` with no profile line: exit 0, waiter exit 1, `profile_check: not-checked`.

## Notes
- Live Codex behavior is unverified. The ticket's criterion 7 (a fresh callable named-agent Codex run) cannot run on this Claude host without nesting a CLI, and the report says so.
- Carried from step 1: `dispatch.py` is outside this step's scope and its selftest was not run. If its parity cases compare `runs.jsonl` keys against `run.sh`, the land gate may need the two optional keys there. The full `check.sh` was not run, as the handoff leaves it to the land gate.
- The report quotes the live fingerprint `0.22.5+e27be4736593` for `sdlc-scout-l1`, taken after regeneration. Any later edit to `instructions.md` changes it, and the report is dated evidence, not to be rewritten.
- `instructions.md` was read in full at the edited spans after the scripted replacements: the handshake command is one clean code span ending in `--binding <profile_fingerprint>`.
- The handoff has no `(red)` criterion, so no `redck.py record` was run.
- No throwaway worktree was created. Nothing is committed: the work is uncommitted in the tree.
