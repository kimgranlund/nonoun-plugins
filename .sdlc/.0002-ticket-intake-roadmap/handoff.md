---
id: T-0002
title: "Ticket intake command and generated roadmap"
type: feature
status: done
size: M
priority: P2
depends: [T-0001]
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
A person can stamp a typed ticket with the next id and see a dependency-ordered roadmap that is generated, never hand-edited.

## Intent
- Do: a `/ticket` skill backed by a script with `new <type> <slug> "title"` (copy the type's template, assign the next id), `roadmap` (generate `.sdlc/roadmap.md` from front matter, ordered by `depends`), and `check` (fail on a bad field, duplicate id, dangling `depends`/`from`, cycle, or stale roadmap). Possibly a board.py mode instead of a separate script.
- Non-goals: replacing /handoff for free-text briefs.
- Done when: new, roadmap and check work on a fixture, each check failure has a negative control seen to fail, and check.sh passes.

## Context
- Reference implementation: `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/scripts/tickets.py` and `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.sdlc/roadmap.md`.
- Today /handoff turns free text into a handoff but assigns no type or id.

## Constraints
None.
