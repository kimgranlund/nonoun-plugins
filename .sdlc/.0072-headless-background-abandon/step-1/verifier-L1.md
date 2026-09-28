<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `test -x block-background.sh`: pass. Evidence: the test printed X1.
- Role set with background true exits 2, and stderr has 600000 and foreground: pass. Evidence: rc=2, and the message reads "...run this in the foreground with the Bash timeout at 600000 or more...".
- `SDLC_HEADLESS=1` with background true exits 2: pass. Evidence: rc=2.
- Neither variable set with background true exits 0 (negative control): pass. Evidence: rc=0.
- Role set with background absent exits 0: pass. Evidence: rc=0. A `run_in_background: null` input also exits 0.
- hooks.json registers block-background.sh and the Bash matcher has 2 hooks: pass. Evidence: the `grep` matched and `jq -e` printed `true`. The diff adds the second command in the same quoting style, and block-publish is unchanged.
- `hook-selftest.sh` prints `hook selftest: PASS`: pass. Evidence: it printed the line with rc=0. The script covers all the listed cases and builds the push string at runtime.
- Wired into check.sh: pass. Evidence: check.sh has the added `bash "$root/scripts/hook-selftest.sh" || fail=1` line and the updated header comment. The full check run printed "hook selftest: PASS".
- (guard) block-publish still exits 2 on a push with `SDLC_ROLE=builder`: pass. Evidence: rc=2.
- (guard) shellcheck at warning severity on hooks and scripts: pass. Evidence: sc=0.
- (guard) `check.sh` exits 0: pass. Evidence: the rerun printed `check rc=0`; its tail included "ok: shellcheck" and "ok: plugin validate".
- The selftest can go red: pass. Evidence: in a throwaway copy I changed `== "true"` to `== "nope"` in the hook. The selftest then printed `FAIL: role + background true: exit 0, want 2` and exited 1.

## Out of scope changes
None. The tracked changes are hooks.json and check.sh. The new files are block-background.sh and hook-selftest.sh. The rest is `.sdlc` task artifacts.

## For the next attempt
None
