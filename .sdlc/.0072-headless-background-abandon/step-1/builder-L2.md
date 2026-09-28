<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-background.sh`: new executable hook. When `SDLC_ROLE` is set or `SDLC_HEADLESS=1`, it denies `run_in_background: true` with exit 2 and the specified stderr message.
- `plugins/sdlc-lite/hooks/hooks.json`: registered `block-background.sh` as a second command hook under the existing Bash PreToolUse matcher. The `block-publish.sh` entry is unchanged.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: new selftest with the 6 block-background cases plus the block-publish push and `ls` cases. Each case runs under `env -u SDLC_ROLE -u SDLC_HEADLESS`.
- `plugins/sdlc-lite/scripts/check.sh`: wired in `hook-selftest.sh` after `run-selftest.sh` and updated the header comment.

## Checks
- `test -x .../block-background.sh`: pass
- SDLC_ROLE=builder with background true: exit 2, and stderr contains 600000 and foreground: pass
- SDLC_HEADLESS=1 with background true: exit 2: pass
- Neither variable set with background true: exit 0: pass
- SDLC_ROLE=verifier with background absent: exit 0: pass
- hooks.json grep plus jq check that the Bash matcher has 2 hooks: pass (`true`)
- `bash .../hook-selftest.sh | grep -q 'hook selftest: PASS'`: pass
- `grep -q hook-selftest.sh .../check.sh`: pass
- (guard) block-publish push with SDLC_ROLE set exits 2: pass
- (guard) `shellcheck --severity=warning` on hooks and scripts: the first run failed on SC2069 in my new selftest. I fixed the stderr capture (`3>&1 1>/dev/null 2>&3`) and the rerun passed (exit 0).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: the first run exited 1 on that same shellcheck warning. The rerun after the fix exited 0.

## Notes
None
