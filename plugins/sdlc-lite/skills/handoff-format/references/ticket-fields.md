# Ticket front matter fields

Detail for the handoff-format skill's `## Ticket front matter` section.

## Closing in numbered mode

In numbered mode, `close` renames the folder `NNNN-<slug>` to `.NNNN-<slug>`; tools still treat it as a closed ticket. Before the rename, `close` refuses, writing nothing, when files outside the folder cite `<root>/NNNN-<slug>` (found with `git grep`), naming each; `--rewrite-refs` rewrites them to the dot path with the rename, and `--force` closes and leaves them.

## Field rules

A `file:` depends entry is repo-relative and met once the path exists; it never orders tickets. A `cap:` entry is met once a `done` ticket provides it, and orders the ticket after every provider. `check` fails a malformed entry or an unprovided `cap:`.

A `successor:` names the one ticket that took this one over: it superseded it, delivered it, verified it in an integration ticket, or fixed it in another repository (`<repo>:T-NNNN`). While this ticket is open and a local successor is `done`, `check` prints the ready-to-run `close <folder> --reason "..."` line; a successor in another repository is shown, never resolved. `check` fails a malformed value or a local id no ticket has.

Front matter is purely additive: a handoff with no front matter keeps working unchanged, and no runner requires or parses it. `board.py` reads `id`/`status` from front matter for display only (via `tickets.py`'s parser, so a task without front matter or an unreadable handoff.md just gets empty cells); it still never requires, validates, or writes front matter. `/ticket new` stamps these fields, `/ticket check` validates them, and `scripts/tickets.py` remains the sole parser and writer of front matter semantics. `tickets.py close` sets `status: done` and stamps `from: <id>` on each follow-up idea ticket it creates. `board.py` also uses ticket status to decide which tasks it lists at all: a `dropped` ticket, or a `done` ticket with no recorded step work, is left off the board entirely.

`size` is the ticket level, on the same L1 to L5 scale as the role levels: L1 and L2 go to the `solo` lane by default, L3 and above to the chain (`steps.py lane` decides). A ticket written by an older plugin version may still carry the one-letter size names; `tickets.py` reads each as its level and stores the level whenever it writes the front matter, and `tickets.py migrate-size --apply` rewrites them all at once.

`status` here is a person's decision (proposed, ready to build, claimed by someone working on it, paused with a reason, blocked, done, dropped), not build progress. `claimed` requires `claimed_by:` and `paused` requires `paused_reason:`; `area:` must name one of the `areas: a, b, c` names in `.sdlc/config`. It never tracks how far a task got through the roles; that stays derived by `/board` from `.sdlc/` run state. The two are independent: a ticket can sit at `status: ready` while `/board` shows no runs yet, or `status: blocked` while a step has already built.

## Origin

Origin: this convention comes from the `.sdlc/_templates/` and `CONTEXT.md` of the gen-ui-system-svelte-lite project. The ticket templates this plugin ships are in `skills/ticket/templates/`.
