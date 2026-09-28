---
id: T-0099
title: "Add a hook-live-probe.sh selftest case where the hook exits with a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0075
---

## Goal
`plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` gains a case where the payload is a JSON boolean true but the hook exits with a code other than 2 (for example 0 or 1); the probe must exit 1 with a reason naming the hook exit code. Removing the `hook_rc != 2` check (line ~223) must turn the selftest red.

## Context
Follow-up from T-0075 (confirm-with-a-live-claude/filer-L1.md):

Add a hook-live-probe.sh selftest case where the hook exits with a code other than 2; the step 1 verifier found that removing the rc==2 check leaves the selftest green.

## Constraints
Existing selftest cases (a) to (d) and live-mode behavior stay unchanged. The selftest stays offline (stub claude, no model call). `scripts/check.sh` stays green. Update CLAUDE.md, `.claude/agents/sdlc-lite-author.md`, or other docs only if they enumerate the selftest cases.
