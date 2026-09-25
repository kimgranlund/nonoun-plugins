---
id: T-0072
title: "Headless sessions background role runs and end the turn, abandoning the work"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A headless session (claude -p: bench, dogfood, fanout lanes, every role run) can never background a role run or a gate and then end its turn.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
2026-09-25: in the T-0061..T-0064 dogfood batch, two headless conductors (T-0063, T-0061) started builder L2 / planner L2 with run_in_background, printed "Nothing to do until it reports", and exited after ~1 minute; the runs were abandoned (planner-L2.log with no .md). The peer (gen-ui-system-svelte-lite T-0044 step 5) saw a headless verifier L2 do the same with a test gate, and /chain recorded it as fail 1. The docs already say headless means foreground; prose is not holding. Proposed mechanism: the PreToolUse(Bash) hook denies `run_in_background: true` whenever SDLC_ROLE is set (every role run is headless) or SDLC_HEADLESS=1 (set by bench.sh, fanout.py's lane driver, and documented for dogfood launchers), with a message saying to run in the foreground with timeout 600000. Negative control: the hook allows it with neither set.

## Constraints
The failing test lands before or with the fix, never after.
