---
id: T-0040
title: "A script writes step handoffs from a plan"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
/chain turns a plan into step handoffs with a script, not per-session parsing.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. /chain step 3 says "for each ## Step n block, write step-<n>/handoff.md" (skills/chain), so every conductor writes its own parser; that session needed a second one for a single-step replan. Suggested: `steps.py split <planner.md> [--only N]` writing step-<n>/handoff.md per the handoff-format step template (task goal plus step block), with a selftest. Pairs with the superseded-step-dirs ticket for replans.

## Constraints
What must not change. "None" if none.
