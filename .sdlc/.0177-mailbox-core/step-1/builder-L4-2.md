<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py` (still untracked): changed only `locate`. It still scans `new`, `read`, `done` in that order. Before returning, it checks each earlier sighting again, after the last sighting was seen:
  - A message only moves forward and keeps its receiver, so a file still at an earlier sighting is a real second file and stays in the result.
  - A file gone from an earlier sighting was the same message moving, so it is dropped.
  - `locate_one` and its duplicate refusal are unchanged, so the refusal now fires only for a real duplicate. The docstring on `locate` explains the rule.

## Checks
- Repro before the fix: 40 rounds of `send` plus 8 concurrent `read` calls. Exit 1: 5 of 280 losers printed `id <id> is in more than one folder` (new/ and read/).
- The same 40-round race after the fix, run 3 times: every run exited 0 with `wins=40 claimed=280 bad=0`. Every loser printed exactly `messages.py: already claimed: <id>`.
- Live reply race: 40 rounds, each with 4 concurrent `read`, one `ack` retry loop and 3 concurrent `reply`. Exit 0: all 120 replies succeeded and 40 messages reached done.
- Deterministic in-process test: imports the module and patches `is_regular` to rename the file right after its first hit. All 11 cases pass:
  - Transit cases:
    - `read` after a new-to-read move: `already claimed`.
    - `read` after a move through new, read and done: `already done`.
    - `reply` after a new-to-read move: succeeds.
    - `reply` after a read-to-done move: succeeds.
    - `ack` during a claim: `not read yet`.
  - Real duplicates still refused, with the mailbox unchanged:
    - read/+done/ for `read`, `ack` and `reply`.
    - new/bob+new/carol for `reply`.
    - new/+done/ for `read`.
- Negative control: the same test against a copy that keeps the old `return found`. Exit 1: all 5 transit cases fail with the two-folder error, and the 6 duplicate cases still pass.
- All 13 acceptance criteria, extracted verbatim from the handoff and run from the repo root with `bash`: each exited 0 with no output. Criterion 11 used the role's `SDLC_TMP_WORKTREES`. I removed `mbox-wt` afterwards, and the prefix directory is empty.
- `git diff --check`: exit 0. The file has 0 non-ASCII lines (so no em dash) and 0 lines with trailing whitespace.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0. `python3 scripts/check-packaging.py`: exit 0.

## Notes
- If a real duplicate exists and one copy moves during the scan, the duplicate can go undetected on that one call. The fix rules out false refusals; catching every duplicate during concurrent moves is best effort.
- `cmd_reply` keeps its 3-try retry, which now covers the case where the original moves between `locate` and `load`. A message moves at most twice.
- My scratch directory with the race scripts and the deterministic test is still at `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.1ESE7deBSm` because the request to remove it was denied. It is outside the repo.
