<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -q -- --conductor`: pass. Evidence: exit 0 on the built tree. In a throwaway worktree at `$SDLC_BASE_SHA` the same command exits 1, so the check can go red.
- Negative control (copy with an allow-all `block-role-spawn.sh`, then `! ... --selftest`): pass. Evidence: I ran the command as written and it exited 0. The copy's selftest printed `hook live probe selftest: FAIL: (k) conductor: exit 1, want 0 (verdict: FAIL: conductor deny: hook exit code 0, not 2)`. On the built tree the selftest passes, so the `!` would fail on a probe that ignores the hook exit code. The biting variable is the hook exit code on the deny run.
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: pass. Evidence: `hook live probe selftest: PASS`, exit 0. Cases (k) to (o) are in the diff and cover the four required cases: deny plus allow passes, deny hook exit 0 fails naming the exit code, no `agent_type` fails, and no Agent call fails. I also mutated a throwaway copy by replacing the hook-exit-code check with `elif false`. The selftest then failed with `(m) deny allowed: exit 0, want 1`, so case (m) bites. The guard was green after the step, so no pre-build run was needed.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `hook selftest: PASS`, exit 0.
- Do-section behavior, checked by reading the diff and by the selftest, since no live call is allowed in this step:
  - The mode uses `--plugin-dir <plugin root> --agent sdlc-lite:conductor`. The selftest counts exactly 2 runs with each argument.
  - The capture hook wraps `block-role-spawn.sh` through `--settings`.
  - The deny prompt names `sdlc-lite:scout` and the allow prompt names `general-purpose`, both with `run_in_background` false.
  - The output lines are `conductor deny/allow: agent_type …, subagent_type …, hook exit code …` plus `verdict: PASS` or `verdict: FAIL: <reason>`.
  - The `--out` report holds the date, model, `claude --version`, both payloads, both lines, and the verdict as its last line. The selftest asserts this.
  - The usage line, `--help` and header comment are updated, and the "never passes --plugin-dir" wording is scoped to the Bash and Agent modes.
  - `--agent --conductor` together exits with a usage error, as observed.
  - `git diff --check` is clean.

## Out of scope changes
None from this step. The tree also has uncommitted changes to `hooks.json`, `check.sh`, `hook-selftest.sh`, and the new `block-role-spawn.sh`. The builder's note attributes them to step 1, and this step's diff touches only `hook-live-probe.sh`. `git status` shows no other modified tracked files beyond those and the `.sdlc` records.

## For the next attempt
None
