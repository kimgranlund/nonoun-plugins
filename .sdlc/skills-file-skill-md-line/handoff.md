---
id: T-0078
title: "skills/file/SKILL.md line 18 still says block-publish 'only fires..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0065
---

## Goal
skills/file/SKILL.md step 4 describes when hooks/block-publish.sh fires accurately: run.sh per role run and fanout.py (SDLC_ROLE=conductor) for lane drivers.

## Context
Follow-up from T-0065 (fanout-py-s-default-lane/filer-L1.md):

skills/file/SKILL.md line 18 still says block-publish "only fires when `SDLC_ROLE` is set by `scripts/run.sh`", which is stale now that fanout.py sets `SDLC_ROLE=conductor` for lane drivers (T-0065).

## Constraints
None.

## Done (conductor trivial edit)
One-line change in plugins/sdlc-lite/skills/file/SKILL.md step 4: the clause now reads "since it only fires when `SDLC_ROLE` is set (by `scripts/run.sh` per role run, and by `scripts/fanout.py` as `conductor` for lane drivers)", matching CLAUDE.md and the conductor prompt. No other doc carries the stale phrase (grep of agents, skills, hooks, CLAUDE.md, .claude). `scripts/check.sh` exit 0. No plan, builder, or verifier runs: trivial edit made by the conductor.
