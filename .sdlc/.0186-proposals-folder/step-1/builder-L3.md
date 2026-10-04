<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/proposals.py` (new, executable): scan, list, show, accept, reject, promote, and a selftest with 27 cases.
- `plugins/sdlc-lite/scripts/check.sh`: runs `python3 "$root/scripts/proposals.py" selftest || fail=1` after the evals.py line. `proposals.py` is added after `evals.py` in the header comment's list.

## Checks
- `python3 plugins/sdlc-lite/scripts/proposals.py selftest`: all 27 cases `ok:`, `proposals selftest: PASS`, rc 0 (about 5 s).
- Took all 11 acceptance criteria from the handoff verbatim, stripping only the `- ` / `(guard) ` prefix and the backticks, and ran each with `bash -c`. All 11 exited 0, including criterion 1 (the selftest), criterion 2 (all 27 names `ok:`), criteria 3 to 9 (the temp-project probes), criterion 10 (the executable bit and the check.sh line), and criterion 11 (the guard).
- Ran the guard again after check.sh: rc 0. `git status` shows only `check.sh` modified and `proposals.py` untracked outside `.sdlc`.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0. Every selftest passed, including `proposals selftest: PASS`, and `ok: plugin validate`. Two skips: `shellcheck not installed`, and the fanout corpus skip (`.worktrees/fanout-night/logs is absent`).
- `find plugins -name __pycache__`: empty, both before and after check.sh.
- `git diff --check`: clean.
- `git grep -n check.sh -- plugins scripts`: only prose mentions. Nothing pins the content of check.sh.
- Called `clean()` directly on a string containing an em dash; it turned it into `-`. A 200-character quote is cut to 160 characters ending in `...`.

## Notes
- shellcheck is not installed on this host, so the one-line check.sh edit was not shellchecked. It copies the form of the lines next to it.
- In the selftest's case 1, the builder `runs.jsonl` has a non-JSON line and a blank line before the L3 line. This is deliberate: it exercises the skip rules. So the builder-bump evidence is `runs.jsonl:1` and `runs.jsonl:5`, not `:3`. Criterion 4 covers the plain L2, L2, L3 layout and expects `:3`.
- `promote` passes `--root` to tickets.py exactly as given. tickets.py prints the handoff path relative to the cwd when that root is relative, so promote resolves a relative path against the cwd.
- `scan` with two known proposals sharing a `pattern:` line (only possible by hand or with the known-match mutant) updates the one with the lowest id.
- The source file has no em dash: `clean()` uses the `'\u2014'` escape.
- evals.py and tickets.py are unchanged. Nothing was committed.
