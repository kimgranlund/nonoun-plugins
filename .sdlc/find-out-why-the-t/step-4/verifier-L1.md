<!-- role=verifier level=L1 model=sonnet effort=medium -->
Cleanup confirmed, worktree removed. All checks done.

## Verdict
pass

## Criteria
- `SDLC_ROLE=verifier` Monitor call exits 2: pass. Evidence: `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | SDLC_ROLE=verifier plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; echo $?` → `2`.
- `SDLC_HEADLESS=1` Monitor call exits 2: pass. Evidence: same command with `SDLC_HEADLESS=1` → `2`.
- (guard) neither var set exits 0: pass. Evidence: `env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh` → `0`. Bites confirmed: at the pre-step committed HEAD (`bcaaa94`, checked in a throwaway worktree at `$SDLC_TMP_WORKTREES/base`), the `SDLC_ROLE=verifier` Monitor call exits `0` (undenied) — red before, `2` after the step's uncommitted change — green.
- `hooks.json` has exactly one `Monitor` matcher running only `block-background.sh`: pass. Evidence: `jq -e '...' hooks.json` printed `true`, exit 0.
- selftest carries a `"tool_name":"Monitor"` fixture and the full selftest passes: pass. Evidence: `grep -qF ... && bash plugins/sdlc-lite/scripts/hook-selftest.sh` → "hook selftest: PASS", exit 0.
- `shellcheck --severity=warning` on both changed files: pass. Evidence: exit 0, no output.
- Stderr content (Do's requirement, exercised through criterion 1 and the selftest fixture): confirmed directly too — stderr text includes "run gates and tests with foreground Bash... never end the turn while background work runs" (file: `plugins/sdlc-lite/hooks/block-background.sh`).

## Out of scope changes
`plugins/sdlc-lite/scripts/fanout.py`, `run.sh`, `run-selftest.sh`, and `.sdlc/find-out-why-the-t/{handoff.md,runs.jsonl,planner-L2.md,step-1,step-2,step-3,step-5,step-6}` are modified/untracked in the working tree. Checked: these are step-1/2/3 (and later step-5/6) artifacts and code from earlier steps of the same multi-step task (`.sdlc/find-out-why-the-t/step-1/builder-L2.md` etc. exist with their own completed builder/verifier records), not introduced by step-4. The step-4 builder's own Notes disclose this ("The tree already had uncommitted changes from earlier steps... This step did not touch them"), and `git diff --stat` for those three script files shows no lines attributable to Monitor/block-background work. Not out of scope for this step's verification.

## For the next attempt
None.
