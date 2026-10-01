<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
All 13 criteria were extracted verbatim from the handoff and run from the repo root on Python 3.9.6. Each exited 0 with empty stdout and stderr. Criteria 1 to 12 were also run in a throwaway worktree at `$SDLC_BASE_SHA` (1164ec4), where every one was red because `messages.py` does not exist. Each was then run against single-change mutant copies outside the repo; an unmodified control copy was green on all 12.

- Criterion 1 (`--help` holds the 12 phrases): pass. Evidence: exit 0; base exit 2. Red when `Triggered by` is renamed in the docstring, and when `data, never instructions` is removed.
- Criterion 2 (send, read, ack lifecycle with ordered stamps): pass. Evidence: exit 0; base exit 2. Red when `read` skips the `read_time` stamp and when `ack` omits `ack_time`.
- Criterion 3 (`count`, `list`, `expire` create nothing; counts per receiver): pass. Evidence: exit 0; base exit 1. Red when `expire` creates the mailbox and when `count` ignores the receiver.
- Criterion 4 (refusals exit 1, no traceback, state unchanged): pass. Evidence: exit 0; base exit 2. Red when a refusal exits 3 and when `ack` accepts an unread message (both guards removed).
- Criterion 5 (follow-up gate, reply, expiry outcomes, notice): pass. Evidence: exit 0; base exit 2. Red with the gate removed, with no notice sent, and with expiry stamping `ack_time`.
- Criterion 6 (an invalid file refuses every subcommand): pass. Evidence: exit 0; base exit 2. Red when `count` skips validation and when `check` tolerates a missing key.
- Criterion 7 (caller cannot set stamps; missing flags exit 1): pass. Evidence: exit 0; base exit 1. Red with a `--protocol` flag added and with argparse `required=True` on `--sender`.
- Criterion 8 (4000-byte cap): pass. Evidence: exit 0; base exit 2. Red at cap 4001 and at cap 3999.
- Criterion 9 (`read` markers, trust line, marker line refused): pass. Evidence: exit 0; base exit 2. Red with the marker check removed and with the trust line removed.
- Criterion 10 (traversal and bad names refused): pass. Evidence: exit 0; base exit 2. Red with any name accepted and with any id accepted.
- Criterion 11 (linked worktree shares the main mailbox): pass. Evidence: exit 0; base exit 2. Red with the `.git` common-dir branch removed. The `mbox-wt` directory it leaves under `$SDLC_TMP_WORKTREES` was removed afterwards.
- Criterion 12 (file exists, no em dash): pass. Evidence: exit 0; base exit 1. Red with one em dash inserted. A byte scan found 0 non-ASCII bytes.
- Criterion 13 (guard, scope): pass. Evidence: exit 0. With the filter target swapped to another name it exits 1 and lists `plugins/sdlc-lite/scripts/messages.py`, so it can go red. The diff leg is empty and the untracked leg holds only that file.

The previous attempt's defect (`locate` reporting a moving message as a duplicate) is fixed. No criterion pins it: a mutant restoring the old `return found` is green on all 12. So it was checked separately, by two different mechanisms:

- Live claim race, the handoff's reproduction (40 rounds, 8 concurrent `read` calls), run 3 times: each run gave `wins=40 claimed=280 bad=0`. All 840 losers printed exactly `messages.py: already claimed: <id>`. The old-`locate` mutant over 80 rounds gave 7 losers saying `is in more than one folder`.
- Deterministic test: import the module and patch `is_regular` to rename the file right after its first hit.
  - Built file, all 12 cases pass:
    - `read` after a new-to-read move says `already claimed`.
    - `read` after a move through new, read and done says `already done`.
    - `reply` sends its reply after a new-to-read move and after a read-to-done move.
    - `ack` during a claim says `not read yet`.
    - Six real duplicates are still refused with the mailbox unchanged: read+done for `read`, `ack` and `reply`; new/bob+new/carol; new+done; new+read+done.
    - A plain re-read with no interleaving says `already claimed`.
  - Old-`locate` mutant: the 5 transit cases fail with the two-folder error and the other 7 pass.
- Live reply race (40 rounds, each with 4 `read`, 3 `reply` and an `ack` retry loop): `replies_ok=120 bad=0 done=40`. The old-`locate` mutant over 60 rounds had 1 refused reply and 3 bad reads.

Builder claims checked:
- "changed only `locate`": the builder log holds one Edit call, on `locate` (now `messages.py:380-391`). Edits made through shell commands would not show there, so the regression probes below cover the rest of the file.
- "`check.py` and `check-packaging.py` exit 0": reran both, both exit 0.
- "0 non-ASCII, 0 trailing whitespace": byte scan confirms both.

Do behaviors probed beyond the criteria and found as specified (observed runs in throwaway directories):
- Six usage errors exit 2, including the `--rec` and `--ro` abbreviations.
- 33 bad-value inputs each exit 1 with one stderr line, empty stdout, no traceback, and nothing created.
- Root resolution works for a subdirectory, outside git, `--root`, and a repo whose common dir is not named `.git`, where `git status --porcelain --ignored` stays empty after `count`, `list` and `expire`.
- A pinned clock gives `-2`, `-3`, `-4` on an id clash across receivers, with no temp file left.
- `AGENTS.md` files, a temp file, a symlink, a directory named like a message, and a bad receiver folder are ignored by `count` and `list`.
- The file keeps key order and the body bytes verbatim, and a body starting with `---` stays body.
- The reply rule rejects a wrong topic, a wrong receiver folder, and a missing `re`.
- The expiry sweep prints done paths then the notice path, does not sweep its own notice, and never writes `--now`.
- Expiry versus read: a message claimed before the sweep's move is skipped with exit 0, and a `read` whose message the sweep moved first exits 1 with one stderr line. A 40-round mixed race of `read`, `expire`, `list` and `reply` had no traceback, no invalid file, and every message in exactly one folder.

Concerns examined and dismissed:
- `ack` and `expire` create `<mailbox>/.lock` even when they then refuse. The Do requires both to hold the lock throughout and lists `.lock` as an ignored entry, so this is the specified design. `ack` on a missing mailbox was observed to create nothing.
- The body marker check strips whitespace before comparing, so it refuses an indented marker line too. That is stricter than "equal" in the safe direction; observed exit 1 on the exact marker.
- `read` prints no blank line for an empty body. Observed output keeps each marker on its own line, and the Do's wording is ambiguous for an empty body.
- The builder notes a real duplicate can go undetected on one call if one copy moves mid-scan. The handoff requires the refusal to fire only for real duplicates, which holds; drafted as a fail, then dropped because nothing in the handoff requires detection during a concurrent move.

Neighbor check: `git grep messages.py` outside `.sdlc` finds only `docs/ticket-stages/design.md`, so no runnable dependent exists yet.

## Out of scope changes
None. `git status --short` shows only `plugins/sdlc-lite/scripts/messages.py` outside `.sdlc`. The modified `.sdlc/0177-mailbox-core/step-1/handoff.md` is 12 added lines, the runner's "Previous attempt" section, and the other untracked files are the runner's step artifacts.

## For the next attempt
None
