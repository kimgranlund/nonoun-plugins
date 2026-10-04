<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/results.py` (new, executable, stdlib only): holds the `SCHEMA` table, `ROLES`, `validate`, `structure_error`, `key_value` and `schema_lines`, the CLI (`validate`, `schema`, `key`, `selftest`) and a 51-case selftest.
- `plugins/sdlc-lite/scripts/check.sh`: runs `python3 "$root/scripts/results.py" selftest || fail=1` just before the steps.py line, and lists `results.py` in the header comment's selftest list.

## Checks
- `python3 plugins/sdlc-lite/scripts/results.py selftest`: 51 `ok:` lines, `results selftest: PASS`, exit 0.
- schema grep for the `plan-reviewer` line: passed.
- schema grep for the `builder` line: passed.
- `test "$(python3 plugins/sdlc-lite/scripts/results.py key scout)" = Map`: passed.
- validate on a valid builder file with a header: exit 0.
- validate on a headerless file with `--role builder`: exit 1, one stderr line containing `results.py: $f: first line is not a`. Passed.
- validate on an empty file with `--role scout`: exact line `results.py: $f: empty result`. Passed.
- validate on a verifier with Criteria above Verdict: exact line `results.py: $f: ## Criteria comes before ## Verdict`. Passed.
- validate on a plan-reviewer with `maybe`: output contains `is not one of pass|replan|blocked`. Passed.
- selftest grep for `ok: key_value reads the key value of a headerless result`: passed.
- Loop over the tracked `.sdlc` result files (33 files, `.sdlc/.*` excluded): every one validated, exit 0.
- `grep -qF 'scripts/results.py" selftest' plugins/sdlc-lite/scripts/check.sh`: passed.
- (guard) scope check against `SDLC_BASE_SHA=f45649ed7434f69b45414575b449ea20d7125977`: passed. Only `results.py` and `check.sh` changed outside `.sdlc`.
- Usage errors (`key poet`, an unknown subcommand, `validate x --role poet`): each exited 2.
- No em dashes in either file. `git diff --check` was clean.
- shellcheck is not installed here, so it was not run on `check.sh`.
- I did not run the full `bash plugins/sdlc-lite/scripts/check.sh`, because no acceptance criterion names it.

## Notes
- The CLI uses argparse, so a usage error prints argparse's usage text to stderr and exits 2.
- One reason string is not in the settled list: an existing file that cannot be read returns `cannot read: <strerror>` instead of raising. A missing path or a non-file still returns `no such file`.
- In the Python API, passing a role that is not in `SCHEMA` to `validate` or `structure_error` raises `ValueError`. `key_value` returns `None` for an unknown role, or for a role with no allowed set, and never raises.
- Reason 7 quotes the first line stripped but keeps its original case. Matching is done on the lowercased value.
