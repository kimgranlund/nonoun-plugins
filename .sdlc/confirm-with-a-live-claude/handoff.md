---
id: T-0075
title: "Confirm with a live claude -p probe that the Bash PreToolUse..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0072
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0072 (headless-background-abandon/filer-L1.md):

Confirm with a live `claude -p` probe that the Bash PreToolUse payload carries `tool_input.run_in_background` as a JSON boolean. `block-background.sh` is proven only against fixtures, so a different field shape would silently disable it.

## Constraints
What must not change. "None" if none.
