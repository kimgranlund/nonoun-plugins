---
id: T-0152
title: "External agents (Codex) get lane integration and reserved ticket ids"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).

## Intent
Literal ask: Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).
Deltas:
- Mechanism choice (register owner/branch vs reserve id ranges): gap: the ask offers both; default: one registration of the external branch in the ticket root's config (the same file `config_numbered` reads), used by both fanout.py and tickets.py; id ranges only if the architect finds registration cannot prevent collisions.
- What "join fanout" means for an external lane: gap: whether fanout runs its driver on the branch; default: an external lane runs no driver. fanout.py takes a lane whose branch already exists and is owned by the outside agent (for example a `<lane>@<branch>=<ids>` spec form or a flag, architect's pick), and syncs, gates, merges, and closes it like any lane, without creating `<integration>-<lane>` or requiring a hand-made ref.
- Id collision: defaulted: tickets.py `id_floor` today scans only other git worktrees' ticket roots; a registered external branch that is not checked out is invisible to it. `id_floor` must also count ticket ids committed on registered branches (read from git objects, no checkout), so `tickets.py new` never mints an id already used there.
- Evidence repo (gen-ui-system-svelte-lite lane logs) is not in this repo: defaulted: not needed; the mechanics above follow from fanout.py preflight/setup and tickets.py id_floor.
- Codex parity: defaulted: behavior lives in the shared scripts, so both hosts get it; update the fanout skill and the scripts' docstrings, no host-specific work.
Do: add an external-branch lane form to fanout.py (preflight, setup, run, dry-run plan, report, docstring, selftest), add a registration record for external branches read by tickets.py `id_floor` (and its docstring and selftest), and update skills/fanout and any contract text that states how lanes and ids work.
Non-goals: running a driver or headless conductor on an external branch; pushing or fetching remotes; changing numbered-mode folder names; retrofitting existing tickets.
Done when: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` pass with new cases proving (a) a lane on an existing registered external branch merges and closes with no `<integration>-<lane>` branch created and no driver run, with a negative control, and (b) `tickets.py new` mints an id above one committed only on a registered branch not checked out in any worktree, with a negative control showing the collision without registration; and `bash plugins/sdlc-lite/scripts/check.sh` passes.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 9 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
Existing `<lane>=<id>` lanes, their branch naming, refusals, and selftest cases behave as today. Main is never touched. Nothing is pushed or fetched. Unregistered repos keep today's `id_floor` result.
