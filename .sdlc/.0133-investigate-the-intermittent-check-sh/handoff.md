---
id: T-0133
title: "Investigate the intermittent check.sh failure hook selftest: FAIL..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0123
---

## Goal
`plugins/sdlc-lite/scripts/hook-selftest.sh` never fails from a race between feeding a hook its JSON and the hook exiting early: every hook fixture reports the hook's own exit code, so the selftest is deterministic.

Diagnosis (conductor, from reading the code): hook-selftest.sh runs under `set -uo pipefail`, and its `run()` helper feeds the payload with `printf '%s' "$json" | env ... "$hook"`. Every hook exits 0 before reading stdin when its role gate does not match (`[[ -n "${SDLC_ROLE:-}" ]] || exit 0`; block-repo-format.sh when the role is not builder), and block-pattern-kill.sh never reads stdin on its early-exit paths. When the hook exits before printf writes, printf gets SIGPIPE (exit 141), and pipefail makes the pipeline status 141 instead of the hook's 0. Confirm this (for example by making the race likely, such as a hook fixture that exits at once while the feeder sleeps briefly), then fix the harness so a hook that ignores stdin cannot change the reported exit code.

## Context
Follow-up from T-0123 (replan-light-criterion-swap/filer-L1.md):

Investigate the intermittent `check.sh` failure `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0` (SIGPIPE, likely a timing race). It appeared on the built tree in the step 1 verification, and `hook-selftest.sh` alone passed 20 of 20.

## Constraints
- Do not change hook behavior in `plugins/sdlc-lite/hooks/`: in production Claude Code writes the payload, and exiting without reading stdin is valid there. Fix the test harness.
- Every existing fixture keeps its expected exit code and stderr checks.
- `plugins/sdlc-lite/scripts/check.sh` stays green. If `hook-live-probe.sh --selftest` or any other selftest pipes a payload into a hook the same way, fix it the same way.
- Keep the scripts shellcheck-clean.
