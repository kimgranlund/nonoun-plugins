<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/order.py` (new, executable): the shared ordering rule with `records`, `ordered`, `newest` and `counts_after`, plus the CLI `newest <dir> <role>` and `selftest` (cases a to e, 15 assertions).
- `plugins/sdlc-lite/scripts/run.sh`: the runs.jsonl line now has `file: "<name>.md"` (`--arg file "$name.md"`). The header comment mentions it. The verifier swap is unchanged.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/order.py" selftest || fail=1` and updated the header comment.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: asserts that the 3 runs.jsonl `file` values are `planner-L3.md`, `planner-L3-2.md` and `planner-L3-3.md` in order. A missing field reads as `MISSING`.

## Checks
- `python3 scripts/order.py selftest`: all 15 cases pass, prints `order selftest: PASS`, exit 0.
- `grep -n "mtime\|stat()" scripts/order.py`: prints nothing (grep exit 1).
- Copied `bench/results/2026-09-24-button-geometry-model/step-2` to a temp dir and ran `touch -t 202601010000` on every file:
  - `order.py newest <tmp> verifier` printed `<tmp>/verifier-L2.md`.
  - `order.py newest <tmp> builder` printed `<tmp>/builder-L3.md`.
- Sort-key negative control: in a scratch copy, changed the `ordered` sort key to `os.stat(...).st_mtime`. The selftest failed with exit 1, and 5 checks missed: (a) ×2, (b) highest-k pairing, (c) ordering, (e) newest.
- `bash scripts/run-selftest.sh`: prints `run selftest: PASS`, exit 0.
- `jq -r .file` on the runs.jsonl of a kept copy of the selftest run printed `planner-L3.md`, `planner-L3-2.md`, `planner-L3-3.md`.
- `file`-field negative control: removed ` file: $file,` from run.sh. The run selftest printed `FAIL: runs.jsonl file fields are 'MISSING MISSING MISSING '`, exit 1. run.sh was then restored from a backup and has one `file: $file` again.
- My first try at that control was invalid: its sed left `,,`, so jq failed to parse. I redid it as described above.
- `bash scripts/check.sh`: exit 0. The order selftest, run selftest, shellcheck and plugin validate all pass.

## Notes
- Legacy pairing and unrecorded keys:
  - A `file` record naming a file that isn't in the dir is ignored.
  - A non-canonical name such as `verifier-L1.attempt2.md` sorts as unrecorded, keyed by the `L<n>` in its name, with k=1 and the name as tiebreaker.
- `counts_after` reads the rank of each path from that path's own dir.
- In (e), line indexes still count bad lines: records come back as `[0, 4]`, not `[0, 1]`.
- Stale records for later steps: several docs still say "newest by mtime", and step 4 will make them wrong. This step changed none of them:
  - `board.py`'s docstring
  - `steps.py` split help
  - run.sh's "readers take the newest file"
- `tickets.py` is the only script in `scripts/` without the executable bit. I left it alone.
