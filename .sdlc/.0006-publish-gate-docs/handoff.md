---
id: T-0006
title: "Document that block-publish.sh only guards role runs"
type: chore
status: done
size: S
priority: P3
depends: []
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
Nobody assumes the publish hook guards the user's own session.

## Intent
- Do: state in the conductor agent and `skills/file` that `hooks/block-publish.sh` exits 0 unless `SDLC_ROLE` is set (by design), so publishing from the user's own session is gated only by the AskUserQuestion step in /file.
- Non-goals: extending the hook to the user's session.
- Done when: both files say it and check.sh passes.

## Context
- `hooks/block-publish.sh` checks `SDLC_ROLE`, which only `scripts/run.sh` sets.

## Constraints
None.
