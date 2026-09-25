---
id: T-0026
title: "tickets.py: check should warn when every ticket folder has an NNNN..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0024
---

## Goal
1. `tickets.py check` (not in numbered mode) prints a warning, without failing, when every ticket folder under the root has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered`, telling the user how to persist the mode.
2. `tickets.py close --numbered` persists `ticket_folders: numbered` to `<root>/config`, as `new --numbered` already does (covers T-0027).
Done when both behaviors have selftest cases that fail without the change, and `plugins/sdlc-lite/scripts/check.sh` passes.

## Context
Follow-up from T-0024 (numbered-mode-not-persisted/filer-L1.md):

tickets.py: `check` should warn when every ticket folder has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered` (e.g. gen-ui-system-svelte-lite, whose numbered folders predate T-0024)

## Constraints
- `check` exit status is unchanged: the new message is a warning, never a failure.
- Plain slugs stay the default; no warning when there are no tickets or any folder lacks the prefix.
- Update the tickets.py usage docstring, the /ticket skill, CLAUDE.md, and `.claude/agents/sdlc-lite-author.md` where they describe numbered mode persistence.

## Triage
2026-09-24, user-approved: keep; also covers T-0027: `close --numbered` must persist `ticket_folders: numbered` like `new --numbered`.
