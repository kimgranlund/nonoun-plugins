<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/results.py selftest`: pass. Evidence: I ran it and it printed `results selftest: PASS` with rc=0. I broke copies of `results.py` in `$SDLC_TMP_WORKTREES` to see it go red. With the order check disabled it printed three MISS lines, for Criteria before Verdict, Checks before Changes, and Notes before Changes. With `key_value` made header-dependent it missed the headerless case. With the inherited regex loosened it missed both bare `inherited red` rejections. The copies were deleted afterwards.
- schema line for `plan-reviewer` (`grep -qxF`): pass. Evidence: I ran the command and it exited 0 (c2=0). The full `schema` output matches the handoff table line for line.
- schema line for `builder` (`grep -qxF`): pass. Evidence: exit 0 (c3=0).
- `key scout` equals `Map`: pass. Evidence: exit 0 (c4=0).
- validate of a valid builder file with a header: pass. Evidence: exit 0 (c5=0).
- validate of a headerless file with `--role builder` gives rc 1, one stderr line, and `first line is not a`: pass. Evidence: exit 0 (c6=0).
- validate of an empty file with `--role scout` gives the exact line `results.py: $f: empty result`: pass. Evidence: exit 0 (c7=0).
- validate of a verifier with Criteria before Verdict gives the exact line `## Criteria comes before ## Verdict`: pass. Evidence: exit 0 (c8=0).
- validate of a plan-reviewer with `maybe` contains `is not one of pass|replan|blocked`: pass. Evidence: exit 0 (c9=0).
- selftest includes the line `ok: key_value reads the key value of a headerless result`: pass. Evidence: exit 0 (c10=0). Mutation 2 above shows this case can go red.
- Every tracked `.sdlc` result file validates: pass. Evidence: the loop covered 33 files and none failed (c11 n=33).
- `grep -qF 'scripts/results.py" selftest' check.sh`: pass. Evidence: exit 0 (c12=0). The diff shows `python3 "$root/scripts/results.py" selftest || fail=1` placed before the steps.py line, and `results.py` added to the header comment list.
- (guard) only `results.py` and `check.sh` changed outside `.sdlc`: pass. Evidence: exit 0 (c13=0). The guard can fail when a third file appears, because it filters on `git diff --name-only` plus untracked files.

Beyond the listed criteria I also checked these:
- **Usage errors:** `key poet` and an unknown subcommand both exit with rc 2.
- **File modes and dashes:** `results.py` is mode `-rwxr-xr-x`, and there are no em dashes in either changed file.
- **Wider scan:** a scan of `.sdlc` in this worktree and in the main checkout returned only the closed history file `.0163-codex-default-models-rejected/step-1/builder-L3.md`. The handoff already names it as the known failure.
- **Order reason:** a builder with Status, Notes, Changes, Checks gives `## Notes comes before ## Changes`, which matches the handoff's A/B rule.

## Out of scope changes
None. `git diff $SDLC_BASE_SHA` outside `.sdlc` touches only `check.sh`, and `results.py` is the one new file. The `.sdlc/` changes are run artifacts and are excluded from the guard.

One builder addition is not in the handoff's reason list: an unreadable file returns `cannot read: <strerror>`. I read the code (`_check`, the `OSError` branch). It is an unspecified edge case that does not touch any settled reason, so I did not count it as a defect.

I did not run the full `check.sh`. No criterion names it, and the selftest it adds ran green on its own.

## For the next attempt
None
