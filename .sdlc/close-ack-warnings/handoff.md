---
id: T-0057
title: "close --ack-warnings to record why stale filer warnings no longer apply, instead of --force"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A resolved filer warning can be acknowledged with a reason instead of a blanket --force.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

A stale warning ("nothing committed yet", later committed) makes close refuse, so --force is the only way through. Suggested: `close --ack-warnings "<why>"` records why each warning no longer applies.

## Constraints
What must not change. "None" if none.
