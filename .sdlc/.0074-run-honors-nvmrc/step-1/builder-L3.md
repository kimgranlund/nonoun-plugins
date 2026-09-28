<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: resolves `.nvmrc` from the git toplevel after the git preflight and before the `SDLC_DRY_RUN` exit. It never sources or runs nvm. Exact versions match only their own dir. Partial versions match whole components and take the highest installed version by numeric compare. Aliases are not resolved. It prints one `run.sh: .nvmrc ...` stderr line per outcome and runs `export PATH="<bin>:$PATH"` on a match. The header comment now describes this.
- `plugins/sdlc-lite/scripts/run-selftest.sh`:
  - The stub `claude` now records `${PATH%%:*}` in `$tmp/pathhead`.
  - Added `.nvmrc` cases against a fake `NVM_DIR` holding v18.19.1, v20.9.0, v20.11.0 and v200.1.0:
    - exact match, with and without the `v`
    - `20`/`v20` pick v20.11.0 over v20.9.0 and ignore v200.1.0
    - `v20.9` and `v20.11` match; `v20.1` and `v2` do not
    - `18`, and the missing version `v22.1.0`
    - aliases `lts/*` and `node`
    - an nvm dir that does not exist
    - no `.nvmrc`, which must print nothing
    - whitespace around the version is stripped
  - Every case checks the whole stderr line exactly.
  - One real run checks that `claude` sees the matched bin dir first on PATH.
  - The header comment was updated, and the existing cases and the `run selftest: PASS` line are unchanged.

## Checks
- AC1 (`20` picks v20.11.0 and ignores v20.9.0/v200.1.0, dry run): exit 0, printed the `prepended .../v20.11.0/bin to PATH` line.
- AC2 (`  v20.11.0` with surrounding whitespace): exit 0, prepended line printed.
- AC3 (v20.11.0 not installed): exit 0, printed a `not found` line and no `prepended` line.
- AC4 (`lts/*`): exit 0, printed an `alias not resolved` line and no `prepended` line.
- AC5 (guard, no `.nvmrc`): exit 0, no `.nvmrc` text in the output.
- `grep -q NVM_DIR plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, exit 0.
- Negative control: in a `git worktree add --detach <tmp> HEAD` copy with both built files copied in and the `export PATH=` line removed from run.sh, the selftest printed `run selftest: FAIL: .nvmrc real run: claude saw PATH head '<tmp>/bin', want '<tmp>/nvm/versions/node/v20.11.0/bin'` and exited 1. The worktree was removed afterwards.
- Extra mutations in the same worktree, each of which made the selftest FAIL with rc=1:
  - lexical highest-pick (it chose v20.9.0)
  - no minor-component check (`v20.9` got v20.11.0)
  - string-prefix major match (`20` got v200.1.0)
  - alias reported as not found
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0; all selftests PASS, `ok: shellcheck`, `ok: plugin validate`.

## Notes
- A `.nvmrc` that holds only whitespace prints nothing and leaves PATH alone, the same as having no `.nvmrc`. The handoff does not cover this case; I did this rather than print an alias line with an empty version.
- Written for bash 3.2, the macOS `/bin/bash`, with no associative arrays or `mapfile`.
- Plain `shellcheck` (no severity flag) reports one info-level SC2016 in run.sh's skill-loading `sed`, which was there before this change. The warning-severity check is clean.
- Nothing was committed.
