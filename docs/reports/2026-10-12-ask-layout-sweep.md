# /ask blocker sweep across ticket layouts (T-0508)

Date: 2026-10-12. Fixes finding F6 of the [Astra review](2026-10-12-sdlc-lite-astra-review.md), which stays unchanged.

## Change

- `tickets.py blockers [--scope PATH]` lists open tickets with status `blocked` or a `## Deferred` heading, read from `layout_paths(root).tickets` (flat, `ticket_root: tickets`, `layout: topics`). Done, dropped and closed `.NNNN-<slug>` tickets never count. The scope filter runs after discovery and never moves the root. A missing ticket dir or scope is an error naming the path, not `none`.
- `skills/ask/SKILL.md` runs that command from the repository root instead of the hard-coded `.sdlc/tickets` grep, and scopes the verdict and gap greps by the supplied task dir while skipping closed folders.
- `scripts/check.py` item 29 pins the new command text.

## Observed inventory (throwaway flat project, commands from the revised skill, no model call)

Fixture: `.sdlc/stuck` (blocked), `.sdlc/later` (proposed, `## Deferred`), `.sdlc/fin` (done, `## Deferred`), no `config`.

| Command | Exit | Output |
|---|---|---|
| baseline `grep -rl '^status: blocked' .sdlc/tickets` | 2 | `No such file or directory` |
| `tickets.py --root .sdlc blockers` | 0 | `later` deferred, `stuck` blocked; `fin` excluded |
| `tickets.py --root .sdlc blockers --scope .sdlc/stuck/` | 0 | `stuck` only |
| `blockers --scope .sdlc/nope` | 1 | `scope does not exist; nothing searched` |
| `blockers` with `ticket_root: tickets` and no `tickets/` | 1 | `ticket dir does not exist` |

`tickets.py selftest` holds the regression cases: the same fixture in flat, ticket-root and topics layouts gives one inventory, a scoped run keeps one ticket, closed tickets are excluded, a missing scope and ticket dir are errors, and the baseline grep exits 2 on the flat fixture. Removing the closed-ticket exclusion makes the selftest fail.

## Not verified

A live `/sdlc-lite:ask` model session on a flat project was not run; the commands the skill prescribes were run directly.
