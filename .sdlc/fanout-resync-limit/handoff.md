---
id: T-0127
title: "fanout: make the resync retry limit configurable"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Busy repos can raise the lane resync limit.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

With many lanes touching shared registries (AGENTS.md indexes, generated files), 2 resync tries is too low; the peer raised it to 8 locally. Add `--resync-tries N` (default 2) or a config key.

## Constraints
What must not change. "None" if none.

## Open question (conductor, 2026-09-26)
Blocked on a user decision. `scripts/fanout.py` has no resync retry to make configurable: in this tree, in the 0.11.1 plugin cache, and in the marketplace copy, `run_ticket` syncs the lane once and a `sync conflict`, `merge conflict`, or red gate stops the lane with no retry. The peer's "2 tries, raised to 8" was local to their setup. Delivering this means designing a new retry loop first. Decide:
- What a try retries: on `merge conflict` into integration, resync the lane from integration and re-merge; or also rerun the driver on the resynced lane; or only the pre-ticket sync.
- Default: 1 (today's behavior, no retry) or 2 (the peer's baseline).
- Surface: `--resync-tries N` flag, a `<root>/config` key, or both.
