---
id: T-0053
title: "The hooks.PreToolUse command leaves ${CLAUDE_PLUGIN_ROOT} unquoted..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0049
---

## Goal
The block-publish PreToolUse hook runs, and blocks, when the plugin path contains spaces; `claude plugin validate` reports no unquoted-placeholder warning.

## Context
Follow-up from T-0049 (newest-by-mtime/filer-L1.md):

The hooks.PreToolUse command leaves `${CLAUDE_PLUGIN_ROOT}` unquoted, which `claude plugin validate` warns about. A plugin path with spaces could break the block-publish hook.

## Constraints
The hook script and its matcher stay as they are; only the command string in `plugins/sdlc-lite/hooks/hooks.json` changes.

## Triage
2026-09-24, user-approved: keep; quote ${CLAUDE_PLUGIN_ROOT} in the hook command so a path with spaces works.

## Closed

2026-09-24: Shipped in 0.6.0; verified live: builder push blocked with the plugin at a path containing a space.
