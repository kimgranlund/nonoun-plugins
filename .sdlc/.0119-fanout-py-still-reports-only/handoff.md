---
id: T-0119
title: "fanout.py still reports only driver failed rc=<n> when a lane's..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0115
---

## Goal
When a lane's driver (conductor) exits non-zero and the lane's ticket dir holds a step whose `steps.py next` action is `inherited`, fanout.py reports the inherited-red cause (outcome starting `inherited red: step-<n>: <tests>`, with the driver rc still visible, for example a `(driver rc=<n>)` suffix) instead of only `driver failed rc=<n>`. A non-zero exit with no inherited step keeps `driver failed rc=<n>` exactly.

## Context
Follow-up from T-0115 (fanout-py-treats-a-lane/filer-L1.md):

fanout.py still reports only `driver failed rc=<n>` when a lane's conductor exits non-zero after an inherited-red stop, so the inherited-red cause stays hidden in that case; detect it there too.

## Constraints
- The zero-exit inherited-red path, its outcome text `inherited red: step-<n>: <tests>`, and selftest case 5 stay unchanged.
- An inherited-red stop after a non-zero exit behaves like any stop: no lane commit, merge, or close; the lane tree is WIP-committed as `wip(<id>): <outcome>`; later tickets in the lane are `skipped`.
- The fanout.py docstring (step 2/3), the fanout selftest (a new case with a stub driver that writes an inherited builder result and exits non-zero, plus its negative control), and any doc that describes `driver failed rc=<n>` (CLAUDE.md Layout fanout.py entry, .claude/agents/sdlc-lite-author.md, skills/fanout) are updated in the same change.
- `plugins/sdlc-lite/scripts/check.sh` stays green.
