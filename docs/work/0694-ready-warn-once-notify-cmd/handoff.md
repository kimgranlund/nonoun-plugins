---
id: T-0694
title: "lanes.py ready warns once per session and runs --notify-cmd on pin"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A worker in a two-session setup sees the "no conductor mailbox" warning from `lanes.py ready` once per session, not on every ready, and can name a command that tells the conductor instead.

## Intent
- Do: in `ready` (`plugins/sdlc-lite/scripts/lanes.py`, the warning near line 1616), print the full warning only the first time per session; later readies print `not sent: no <receiver> mailbox (warned once)`. Key the session on `CLAUDE_CODE_SESSION_ID` when set (the plugin already reads it), else the parent pid, with a marker file under the git common dir.
- Do: add `lanes.py ready --notify-cmd <cmd>` (parser near line 1904): after the ref is pinned, run `<cmd>` through the shell in the main checkout with `SDLC_READY_TICKET`, `SDLC_READY_SHA` and `SDLC_READY_PATH` set; print `notified: <cmd> rc=<n>`; a non-zero rc is a warning, the ready still exits 0. With `--notify-cmd` the mailbox warning is not printed. Document both in the docstring and in the Hosts bullet of `plugins/sdlc-lite/AGENTS.md` (Lanes section, line 43).
- Do: a `lanes.py selftest` case: two readies with no mailbox in one session print the full warning once; a ready with `--notify-cmd 'echo $SDLC_READY_TICKET > <file>'` writes the ticket id.
- Non-goals: registering a Claude cross-session address as a mailbox receiver (`messages.py`).
- Done when: the criteria pass.

## Context
Source: GitHub issue #39, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- 17 of 17 pinned readies in the peer session printed the warning, each followed by a manual SendMessage to the conductor.
- The warning is still on main: `lanes.py:1616` (`warning: not sent to {receiver}: no {receiver} mailbox is registered`, T-0610), returned with exit 0. `ready` takes only `target` and `--ticket` today (lanes.py:1904).

## Constraints
The ready ref, unlock and exit codes are unchanged; a registered mailbox still gets the message.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with the new case, and the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/lanes.py ready --help` lists `--notify-cmd`.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.

## Outcome
- `lanes.py ready` prints the no-mailbox warning in full once per session (key `CLAUDE_CODE_SESSION_ID`, else parent pid; marker under `<git common dir>/sdlc/ready-warned/`), then `not sent: no <receiver> mailbox (warned once)`.
- `ready --notify-cmd <cmd>` runs after the pin in the main checkout with `SDLC_READY_TICKET`, `SDLC_READY_SHA`, `SDLC_READY_PATH`; prints `notified: <cmd> rc=<n>`; a non-zero rc is a warning, exit stays 0; the mailbox warning is not printed.
- Selftest case `ready once` added; it fails with the once-marker or the notify call removed (observed with mutated copies).
- Docs: lanes.py docstring and the Hosts bullet in `plugins/sdlc-lite/AGENTS.md`.
- Checks: `lanes.py selftest` exit 0, `lanes.py ready --help` lists `--notify-cmd`, `check.py` exit 0, `git diff --check 65579ba8` exit 0.
