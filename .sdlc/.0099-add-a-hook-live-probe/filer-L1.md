<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0099: Add hook-live-probe selftest case for a non-2 hook exit code

## PR body
### Summary
`hook-live-probe.sh --selftest` had no case where the payload is a JSON boolean `true` but the hook exits with something other than 2. Deleting the `hook_rc != 2` check left the selftest green (found by the step 1 verifier during T-0075). This adds that case, so removing the check now turns the selftest red.

### Changes
All in `plugins/sdlc-lite/scripts/hook-live-probe.sh`, selftest block only:
- The stub claude gains a `nodeny` mode. It runs the registered hook with `SDLC_HEADLESS` and `SDLC_ROLE` unset, so `block-background.sh` exits 0 for a good payload.
- New case (e) runs `probe nodeny "$good"`. It asserts the probe exits 1 and prints `verdict: FAIL: hook exit code 0, not 2`.
- The `STUB_MODE` header comment and the section comment now name case (e).

Cases (a) to (d), live mode and the `hook_rc != 2` check itself are unchanged. The selftest stays offline. CLAUDE.md and the author agent only say "`--selftest` (offline)" and list no cases, so they need no edit.

### Verification
Step 1 built at L2 and passed the L1 verifier:
- `hook-live-probe.sh --selftest` exits 0 and prints `hook live probe selftest: PASS`.
- Mutation check: with the `hook_rc != 2` check deleted from a copy, the selftest exits nonzero.
- With a fresh `TMPDIR`, the run prints no `temp dir left behind` line and leaves the dir empty.
- A diff-scope guard shows every hunk sits above the `# Live mode.` banner (line 128).
- `scripts/check.sh` exits 0, including the probe selftest, shellcheck and plugin validate.

The verifier did not run the mutation against HEAD in a throwaway worktree. It relied on the diff showing case (e) as the only change to the result.

## Changelog entry
- `hook-live-probe.sh --selftest` now includes case (e), where the hook exits with a code other than 2 on a valid payload. The probe must exit 1 with `hook exit code N, not 2`, so removing the `hook_rc != 2` check turns the selftest red.

## Follow-ups
None
