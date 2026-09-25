## Task goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Step 1: Shared ordering helper `order.py`, and run.sh records the result file
level: L3
### Do
- New module `plugins/sdlc-lite/scripts/order.py`. The other scripts import it (`board.py` already does `import tickets` from the same dir), and it also runs as a CLI. One ordering rule, written once:
  - `records(d)`: the lines of `d/runs.jsonl` in file order, with their index. Skip bad JSON lines. A missing file gives `[]`.
  - Rank of a result file (`<role>-L*.md` in `d`):
    1. A record with a `file` field (new, see below) ranks that file directly by its line index.
    2. Records without `file` (the legacy trail) are grouped by (role, level). They pair with that role-level's canonical files that are not already ranked. Canonical means the name matches `^<role>-(L\d)(?:-(\d+))?\.md$`, with no suffix meaning k=1. Pairing runs from the end: the last record goes to the highest k, and so on. This is needed because legacy trails have overwritten or hand-renamed files. In `bench/results/2026-09-24-button-geometry-model/step-2`, two verifier L2 runs left only `verifier-L2.md`, which is the later one.
    3. Anything else is unrecorded. That covers non-canonical legacy names like `verifier-L1.attempt2.md`, extra files, and dirs with no runs.jsonl.
  - Sort key: an unrecorded file sorts as `(0, level number, k, name)`, a recorded one as `(1, rank)`. Unrecorded files always sort before recorded ones.
  - Public API:
    - `ordered(d, role)`: the list from oldest to newest.
    - `newest(d, role)`: a path or None.
    - `counts_after(later, earlier)`: True when both are recorded and `rank(later) >= rank(earlier)`, and also True when either one is unrecorded. This keeps the current "a verifier with no records counts" behavior for fixtures.
  - No `stat()` / mtime anywhere in the module.
  - CLI:
    - `order.py newest <dir> <role>` prints the newest path, or nothing. Exit 0.
    - `order.py selftest`: every fixture file gets the same mtime (`os.utime`). At least one case also sets the mtimes inverse to the true order, so an mtime rule would give the wrong answer. Cases:
      - (a) records with `file`
      - (b) legacy records with no `file`, paired from the end (reproduces button-geometry step-2 so that `verifier-L2.md` is newest)
      - (c) no runs.jsonl: level then k then name
      - (d) `counts_after` true, false, and unrecorded
      - (e) bad JSON lines are skipped
- `plugins/sdlc-lite/scripts/run.sh`: the runs.jsonl `jq -c` line gains `file: "<name>.md"` (`--arg file "$name.md"`). Leave the verifier swap for Step 4.
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/order.py" selftest || fail=1`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: assert that each of the 3 runs.jsonl lines carries `file`, equal to `planner-L3.md`, `planner-L3-2.md`, and `planner-L3-3.md` in order.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/order.py selftest` exits 0.
- `grep -n "mtime\|stat()" plugins/sdlc-lite/scripts/order.py` prints nothing.
- Copy `plugins/sdlc-lite/bench/results/2026-09-24-button-geometry-model/step-2` to a temp dir and run `touch -t 202601010000` on every file in it. Then `order.py newest <tmp> verifier` prints a path ending `verifier-L2.md`, and `order.py newest <tmp> builder` prints one ending `builder-L3.md`.
- Negative control: temporarily change the sort key in the selftest copy (or a scratch copy of order.py) to `st_mtime`. The selftest then fails.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`. `jq -r .file` over its runs.jsonl gives the three names in order. Running it with the `file` field removed from run.sh makes it FAIL.
