---
id: T-0073
title: "A verifier result with no verdict is counted as a fail and burns a retry"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A verifier output with no pass/fail verdict is reported as an error (no verdict), reruns the verifier, and never counts as a build fail.

## Repro
1. In a step dir, write `builder-L2.md` with `## Status\ndone` and `verifier-L1.md` whose body is only `Nothing to do until the test gate reports.` (no `## Verdict`).
2. `python3 plugins/sdlc-lite/scripts/steps.py next <step dir>`
3. `python3 plugins/sdlc-lite/scripts/board.py --task <slug>`

## Expected
`steps next` names a distinct no-verdict action that reruns the verifier at the same level (for example `reverify L1`, reason naming the no-verdict file), and a no-verdict result is never counted as a fail when counting fails toward rebuild/bump. The board shows it as needing attention (no verdict), not as a red fail. /chain, the conductor, and the docs that describe `steps next` actions follow.

## Actual
`steps next` exits 1 with `steps next: ... has no verifier verdict (pass/fail) under ## Verdict` (so /chain stops, and an older peer on 0.7.0 counted it as fail 1); a no-verdict result earlier in the history also makes the fail count raise. board.py renders any non-pass Verdict as `🔴 fail`.

## Context
From peer setup-sdlc-lite-generative-ui (T-0044 step 5, 0.7.0): verifier L2 returned only "Nothing to do until the test gate reports." and /chain recorded it as fail 1, burning a retry and moving toward a level bump. Ask: run.sh or /chain treats a verifier result without a verdict line as `no verdict`.

## Constraints
Known sites (conductor pre-read): `plugins/sdlc-lite/scripts/steps.py` (`next_action`, `verdict`, the `next` docstring, selftest `next_refused('next error: a verifier with no pass/fail Verdict', ...)`), `plugins/sdlc-lite/scripts/board.py` (around line 110), `plugins/sdlc-lite/skills/chain/SKILL.md` step 4, `plugins/sdlc-lite/agents/conductor.md`, repo `CLAUDE.md` steps.py bullet, `.claude/agents/sdlc-lite-author.md`. Repeated no-verdict results must not loop forever: bound the reruns (for example a second consecutive no-verdict at the same build -> stop). `plugins/sdlc-lite/scripts/check.sh` stays green.
The failing test lands before or with the fix, never after.
