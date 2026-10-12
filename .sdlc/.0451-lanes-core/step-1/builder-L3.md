<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/h/plugins/sdlc-lite/scripts/lanes.py: new file, 1831 lines. It has `open`, `close`, `sweep` (dry run by default, `--apply` acts), `list`, `check`, `port`, `archive list`, `archive restore` and `selftest`. The docstring holds the kinds table, truth table, close steps, record fields and config keys. The API is `open_lane`, `close_lane`, `sweep`, `list_lanes`, `still_open`, `landed`, `config`.

## Checks
- `redck.py record <handoff>`, run before the first edit: rc 0, 7 pre-edit controls recorded red.
- c1, last selftest line is `ok: lanes.py selftest`: rc 0.
- c2, `ok: row <n>:` for rows 1 to 12, pr merged, recent, in use and locked: rc 0.
- c3, the C1, C2, C3, C4, C5, C6, C9, C10, C13, claim, still_open and case pr ref lines: rc 0.
- c4, `ok: mutant <M>:` for all nine markers: rc 0. Each mutant was observed failing its case with the named tell.
- c5, `--help` contains each subcommand word: rc 0.
- c6, `--help` contains the seven required strings: rc 0.
- c7, `list --all --json` on this checkout parses as JSON: rc 0.
- c8, worktree list and refs unchanged around the selftest. First run: rc 1. The reflogs show another session writing `main`, `fanout/wave36`, `fanout/wave36-j` and `fanout/wave36-k` and adding the fanout36 worktrees at 01:13:24 to 01:13:42 UTC, inside that run's window. A diagnostic rerun gave selftest rc 0 and an empty diff of worktree list plus refs before and after.
- c9, scope: nothing changed outside `.sdlc` except `lanes.py`: rc 0.
- `git diff --check`: clean.
- One selftest run takes about 72 s on this host, so the five selftest-based criteria take about 6 minutes.

## Notes
- c8 compares the worktree list and `refs/heads`, which every lane in this repo shares. Another lane's commits or worktree adds during the run fail it even though the selftest touches only its temp directory. If it is red, rerun it once and check the `git reflog` timestamps before calling it a failure.
- `red-checkpoint.jsonl` holds 7 records for 8 `(red)` criteria. The one with no pre-edit record is criterion 6, the `--help` check for `"closed <lane> (ancestor)" ... "refs/archive/"`. It was red at base anyway, because the file did not exist. I did not run `record` again.
- One write goes beyond the close steps as listed. After `git update-ref -d refs/heads/<b> <sha>`, close also runs `git config --remove-section branch.<b>`, as `git branch -D` would. Without it, `update-ref -d` leaves the branch description behind, and a reopened name inherits a stale one.
- On this checkout, `list --all --json` shows `h`, `i`, `j`, `k` and both integration trees as `closable, legacy`. That is correct by the spec: `fanout35/` holds `merge.lock` and `logs/`, so these are legacy fanout lanes, and with no commits past main each one is an ancestor of main. The command makes one read-only `gh pr list` call per lane, with a 30 s timeout, and never fetches.
- Not touched, because criterion 9 allows only `lanes.py`: the `check.sh` selftest line and the `docs/references/sdlc-internals.md` entry that the ticket body mentions. Those belong to a later step.
- Choices the handoff left open:
  - `--kind` defaults to `fanout`.
  - The record's `lane` is the tree leaf (`<ticket>-<slug>`). `close` accepts the leaf, the branch or the path.
  - `close` of a locked lane prints `locked: <reason>` and exits 1.
  - A dirty lane with `--discard` goes to row 12.
  - The archive tag is written with `git mktag`, falling back to `git hash-object -t tag -w`. Nothing is created under `refs/tags`.
- The REALPATH control: git records the real path of a worktree, so the selftest opens a lane under `../outside`, then moves that directory into the checkout and leaves a symlink in its place. The real path is then under the checkout while git's stored path is not. The real check fails the case and the mutant passes it.
