---
id: T-0005
title: "Verifier L1 uses the same model family as builder L1"
type: spike
status: done
size: L1
priority: P3
depends: []
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
Decide whether a Sonnet build should get a non-Sonnet verifier, or state in the rubric why it doesn't.

## Intent
- Do: the user decides between (a) extending run.sh's model swap to Sonnet builds, or (b) keeping Sonnet-verifies-Sonnet and stating the exception in `skills/level-rubric`. Benchmark data (first-try verifier accuracy at L1) can inform it.
- Non-goals: changing any model or effort without the user's explicit decision.
- Done when: the decision is recorded in CLAUDE.md and the rubric, and run.sh matches it.

## Context
- Builder L1 is Sonnet low and verifier L1 is Sonnet medium: fresh context and a separate seat, same model family.
- run.sh swaps a Fable verifier to Opus when the build ran on Fable. The user chose "Fable never verifies Fable" deliberately and narrowed an earlier broader swap on 2026-09-24, so this is a question for the user, not a defect.

## Constraints
Model and effort choices are the user's.

## Decision
2026-09-24, user: swap. A verifier never runs on the build's model family; after a Sonnet build a Sonnet verifier becomes Opus medium (Fable builds already got Opus). Implemented in scripts/run.sh; stated in skills/level-rubric and CLAUDE.md.
