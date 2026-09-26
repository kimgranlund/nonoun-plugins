---
id: T-0103
title: "run.sh fails a role run whose result lacks its required section"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A role run that ends without its required output is reported as a failed run, never as done.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite, on 0.9.0): a builder L2 on a merge step resolved every conflict, then ended its turn with "Waiting for the background job to notify." (num_turns 9, is_error false). It never committed and never wrote a Status, and its result file was 95 bytes. run.sh still exited 0, so the wrapper treated the run as done.

Proposal: after the run, run.sh checks the saved result for the role's required heading (builder `## Status` with done or blocked; verifier `## Verdict` with pass or fail; the other roles' first required section). A missing heading makes run.sh exit with a distinct code (for example 3) and name the missing section, and `steps.py next` maps that to a rerun, never to done. This is the "Stop hook that checks result format" item in CLAUDE.md's Later list; update that line.

Also open: why the T-0072 background hook didn't stop this run. The likely route is a background mechanism other than Bash `run_in_background` (Agent tool, Monitor), which T-0076 addresses in batch 17. Confirm after T-0076 ships.

## Constraints
The failing test lands before or with the fix, never after.
