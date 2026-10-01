<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
All 13 criteria were extracted verbatim from the handoff and run from the repo root on Python 3.9.6. Each exited 0 with empty stdout and stderr. Criteria 1 to 12 were also run in a throwaway worktree at `$SDLC_BASE_SHA` (1164ec4), where every one was red because `messages.py` does not exist. Each was then run against single-change mutant copies outside the repo to name the conjunct that bites; an unmodified control copy was green on all 12.

- Criterion 1 (`--help` holds the 12 phrases): pass. Evidence: exit 0; base exit 2. Removing any one of 11 phrases from the docstring alone turns it red. `expiry sweep` also comes from the `expire` subparser help, so it goes red only when removed from both. The table printed by `--help` has the four columns and five rows the Do names.
- Criterion 2 (send, read, ack lifecycle with ordered stamps): pass. Evidence: exit 0; base exit 2. Red when `read` skips the `read_time` stamp, when `ack` omits `ack_time`, when the slug is constant, and when `ack` leaves the file in `read/`.
- Criterion 3 (`count`, `list`, `expire` create nothing; counts per receiver): pass. Evidence: exit 0; base exit 1. Red when `count` or `expire` creates the mailbox, when `count` ignores the receiver, and when `list` prints the wrong sender column.
- Criterion 4 (refusals exit 1, no traceback, state unchanged): pass. Evidence: exit 0; base exit 2. Red when a refusal exits 2, when it tracebacks, when a wrong receiver may read, and when a re-read or re-ack returns 0. Ack of an unread message is guarded twice (lines 699 and 704), so it goes red only with both removed.
- Criterion 5 (follow-up gate, reply, expiry outcomes, notice): pass. Evidence: exit 0; base exit 2. Red with the gate off (repeating the builder's control), the reply rule never matching, reply defaulting to follow-up true, the notice lacking `kind`, no notice sent, a plain `expired` outcome, expiry stamping `ack_time`, and expiry skipping `new/`.
- Criterion 6 (an invalid file refuses every subcommand): pass. Evidence: exit 0; base exit 2. Red when `count` skips validation, when `check` tolerates missing keys, and when `list` or `expire` skips invalid files.
- Criterion 7 (caller cannot set stamps; missing flags exit 1): pass. Evidence: exit 0; base exit 1. Red with a `--protocol` or `--send-time` flag added, with argparse `required=True`, and with a parser that reads a second front matter block. The newline-topic and bad `--follow-up` checks exist at two layers, so each goes red only with both removed.
- Criterion 8 (4000-byte cap): pass. Evidence: exit 0; base exit 2. Red at cap 4001 and at cap 3999.
- Criterion 9 (`read` markers, trust line, marker line refused): pass. Evidence: exit 0; base exit 2. Red with the marker check removed, the trust line removed, and the body not printed.
- Criterion 10 (traversal and bad names refused): pass. Evidence: exit 0; base exit 2. Red with any name accepted, any id accepted, and uppercase names accepted.
- Criterion 11 (linked worktree shares the main mailbox): pass. Evidence: exit 0; base exit 2. Red with a cwd-based mailbox and with a toplevel-based mailbox. The `mbox-wt` directory it leaves under `$SDLC_TMP_WORKTREES` was removed afterwards.
- Criterion 12 (file exists, no em dash): pass. Evidence: exit 0; base exit 1. Red with one em dash inserted. A byte scan found 0 non-ASCII bytes.
- Criterion 13 (guard, scope): pass. Evidence: exit 0. With the filter target swapped to another name it exits 1 and lists `plugins/sdlc-lite/scripts/messages.py`, so it can go red. The diff leg is empty and the untracked leg holds only that file.
- Do behavior no criterion pins, the `read` claim race ("A loser gets FileNotFoundError and exits 1 with `already claimed`"): fail. Evidence:
  - Eight concurrent `read` calls on one message, 45 rounds: exactly one winner each round, but 4 of 315 losers printed `messages.py: id <id> is in more than one folder: .../new/bob/<id>.md, .../read/bob/<id>.md` and not `already claimed`. The message was only in `read/`.
  - Cause: `locate` (`messages.py:380-392`) scans `new`, then `read`, then `done` without atomicity. A claim rename between two scans makes it see the file twice.
  - Reproduced deterministically by importing the module and renaming `new` to `read` right after the first `is_regular` hit. `read` then exits 1 with the two-folder message. `reply <id>` under the same interleaving exits 1 and writes no reply, against "It finds the original in any state folder". The control with no interleaving prints `already claimed`.
  - This contradicts the builder's claim that all five losers say `already claimed`, and the docstring line "a loser exits 1 with `already claimed`".
  - Steelman: the builder would answer that no criterion pins the text and that exit 1 with unchanged state holds. That is true for `read`, but the Do and the ticket Intent both name the loser's message, the printed reason reports a two-folder state that never existed, and `reply` is refused outright. The finding stands.

Do behaviors probed beyond the criteria and found as specified (observed runs in throwaway repos):
- Usage errors exit 2, including `--rec` and `--ro` abbreviations.
- 34 bad-value inputs each exit 1 with one stderr line, empty stdout, no traceback, and nothing created.
- Root resolution works for a subdirectory, outside git, `--root`, and a repo whose common dir is not named `.git`, where `git status --porcelain --ignored` stays empty after `count`, `list`, and `expire`.
- A pinned clock gives `-2` then `-3` on an id clash, across receivers.
- `AGENTS.md`, temp files, a FIFO, a symlink, and a directory named like a message are ignored.
- The reply rule rejects a wrong topic, a wrong receiver folder, and a missing `re`.
- The expiry sweep prints done paths then notice paths, does not sweep its own notice, and never writes `--now`.

Two builder choices were examined and dismissed:
- `read` prints no blank line for an empty body. Observed output keeps each marker on its own line, and the Do's wording is ambiguous for an empty body.
- A path elsewhere in the mailbox gets the id-based refusal. Observed exit 1, which matches "else exit 1".

Neighbor checks: `python3 plugins/sdlc-lite/scripts/check.py` and `python3 scripts/check-packaging.py` both exit 0 with the new file present. `git grep messages.py` outside `.sdlc` finds only `docs/ticket-stages/design.md`, so no dependent exists yet.

## Out of scope changes
None. `git status --short` shows only `plugins/sdlc-lite/scripts/messages.py` outside `.sdlc`; the other untracked files are the runner's step artifacts.

## For the next attempt
All 13 acceptance criteria pass; keep them green. One defect remains in `plugins/sdlc-lite/scripts/messages.py`.

`locate` and `locate_one` (lines 380-392) scan the state folders one after another. A message that moves forward during the scan is counted in two folders, and `locate_one` refuses with `id <id> is in more than one folder`. Callers affected: `cmd_read` (line 639), `cmd_reply` (line 605), `cmd_ack` (line 698).

Required behavior:
- A `read` that loses a claim race exits 1 with `already claimed`, every time.
- `reply` finds an original that is mid-move and sends the reply.
- The duplicate-id refusal fires only when the id really sits in two folders. A message only moves forward, so a re-scan or taking the furthest state resolves a transient double sighting.

Reproduce: in a throwaway repo, loop 40 times: `send` one message to `bob`, start 8 background `read <id> --receiver bob` calls, `wait`, and collect stderr. Every one of the 7 losers per round must say `already claimed`; today about 1 in 80 says `in more than one folder`.
