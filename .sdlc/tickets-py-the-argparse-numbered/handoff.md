---
id: T-0034
title: "tickets.py: the argparse --numbered help text for close does not..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0026
---

## Goal
`tickets.py close --help` says that `--numbered` persists `ticket_folders: numbered` to `<root>/config` on success, matching `new --numbered`'s help and the module docstring.

## Context
Follow-up from T-0026 (tickets-py-check-should-warn/filer-L1.md):

tickets.py: the argparse `--numbered` help text for `close` does not mention that it persists `ticket_folders: numbered` to `<root>/config`

## Constraints
Help text only; no behavior change.

## Triage
2026-09-24, user-approved: keep, P3; one-line help text fix.

## Done (conductor trivial edit, 2026-09-24)
Routed as a trivial one-line edit per the conductor rules, so no plan, build, or verify role ran.
- Change: `plugins/sdlc-lite/scripts/tickets.py`, the `close` subparser's `--numbered` help now reads "name each follow-up folder NNNN-<slug> after its own new id and, on success, persist `ticket_folders: numbered` in <root>/config (also on via that config)". The "on success" matches `close()`'s docstring and the selftest case (j) that a refused close writes no config.
- Checks: `python3 scripts/tickets.py close -h` shows the new text; `scripts/check.sh` passes (level tables, selftest, tickets selftest, board selftest, shellcheck, plugin validate).
