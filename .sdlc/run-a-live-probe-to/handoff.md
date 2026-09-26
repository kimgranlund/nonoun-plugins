---
id: T-0092
title: "Run a live probe to confirm that the running Claude Code version..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0076
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0076 (headless-conductors-can-still-abandon/filer-L1.md):

Run a live probe to confirm that the running Claude Code version reports the subagent tool as `Agent`, not `Task`, in PreToolUse `tool_name` and matchers, and that `run_in_background: false` is accepted. If either fails, the new block-background.sh Agent guard never fires or blocks every headless Agent call.

## Constraints
What must not change. "None" if none.
