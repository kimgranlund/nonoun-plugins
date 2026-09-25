---
id: T-0053
title: "The hooks.PreToolUse command leaves ${CLAUDE_PLUGIN_ROOT} unquoted..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0049
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0049 (newest-by-mtime/filer-L1.md):

The hooks.PreToolUse command leaves `${CLAUDE_PLUGIN_ROOT}` unquoted, which `claude plugin validate` warns about. A plugin path with spaces could break the block-publish hook.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: keep; quote ${CLAUDE_PLUGIN_ROOT} in the hook command so a path with spaces works.
