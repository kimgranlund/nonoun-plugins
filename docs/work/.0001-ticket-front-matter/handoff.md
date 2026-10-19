---
id: T-0001
title: "Ticket front matter in handoff.md"
type: feature
status: done
size: L1
priority: P2
depends: []
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
A task's handoff.md can carry optional YAML front matter that makes it a ticket, so a person's decisions (type, status, priority, order) live next to the brief.

## Intent
- Do: document the optional front matter in `skills/handoff-format`: `id` (T-NNNN), `title`, `type` (feature|bug|chore|spike|idea), `status` (proposed|ready|blocked|done|dropped), `size` (S|M|L|XL), `priority` (P1-P3), `depends` [ids], `created`, `from` (origin ticket id). Optionally add id and status columns to `scripts/board.py`.
- Non-goals: front matter status never tracks build progress; that stays derived by board.py.
- Done when: the format is documented, board.py renders a task with and without front matter, and check.sh passes.

## Context
- Reference implementation: `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.sdlc/_templates/{feature,bug,chore,spike,idea}.md` and `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.sdlc/CONTEXT.md`.
- The requester checked that board.py already ignores front matter and renders fine.
- These tickets in `.sdlc/tickets/` already use this format.

## Constraints
Handoffs without front matter must keep working unchanged.
