<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `! grep -qF 'json" | env' plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: ran on built tree, rc=0. In throwaway worktree at pre-build HEAD (`git worktree add --detach $SDLC_TMP_WORKTREES/base HEAD`), same grep gave rc=1 (pattern present, negation fails) — confirms the check bites.
- `(guard) shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: rc=0 on built tree; also rc=0 at pre-build HEAD (gate was already clean, unaffected by this fix, as expected for a gate).
- `(guard) plugins/sdlc-lite/scripts/hook-selftest.sh` (exits 0, prints PASS): pass. Evidence: ran 30 consecutive times on built tree, all `hook selftest: PASS`, rc=0 every time. At pre-build HEAD, ran 10 times and run 10 failed: `hook selftest: FAIL: block-stray-worktree without role: exit 141, want 0` — reproduces the exact SIGPIPE/pipefail race the handoff diagnosed, and the fix eliminates it (checks-that-bite: red observed pre-fix, green observed post-fix).
- `(guard) plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` (exits 0, prints PASS): pass. Evidence: rc=0, `hook live probe selftest: PASS` on built tree; also green at pre-build HEAD (unaffected gate, as the handoff correctly predicted since that script never sets `pipefail` around its own hook-feeding pipe).
- `(guard) git diff --quiet HEAD -- plugins/sdlc-lite/hooks/` (no change under hooks/): pass. Evidence: rc=0 on built tree; `git diff HEAD -- plugins/sdlc-lite/scripts/hook-live-probe.sh` also empty, confirming that file was left untouched as the handoff required.

Additional check beyond the listed criteria: read the actual diff (`git diff HEAD -- plugins/sdlc-lite/scripts/hook-selftest.sh`) — the only change is `run()`'s stdin feed switched from `printf ... | env ...` to `env ... < <(printf ...)`, with the `3>&1 1>/dev/null 2>&3` fd juggling preserved exactly as the Do required, plus an explanatory comment. No fixture's expected exit code or stderr grep was touched (confirmed by reading the surrounding lines, unchanged from the original file structure).

## Out of scope changes
`.sdlc/investigate-the-intermittent-check-sh/handoff.md` (modified), `planner-L1.md` and `runs.jsonl` (new) are pipeline/process artifacts from the clarify and planner stages that produced this handoff, not code the builder touched. Checked `git diff` for the builder's own change: it touches only `plugins/sdlc-lite/scripts/hook-selftest.sh`, matching the step's scope. Dismissing these as harness bookkeeping, not out-of-scope code changes.

## For the next attempt
None.
