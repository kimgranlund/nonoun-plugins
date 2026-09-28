---
id: T-0159
title: "Lifecycle and codex selftests time out under host load"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
check.sh stays green on a loaded host when the code is correct.

## Repro
Run `bash plugins/sdlc-lite/scripts/check.sh` at load average ~45 (2026-09-28, 1305s run).

## Expected
lifecycle-selftest.py and codex-selftest.py pass, as they do standalone (both rc 0 right after).

## Actual
- lifecycle: test_sigkill_recovers_claude_but_codex_native_refuses hits a fixed `timeout=20` on the retry run; test_both_hosts_cancel_lock_retry_and_routing asserts `scout-L1.running` exists before the child has written it (race).
- codex: test_native_exchange_preserves_runner_artifacts finds no `scout-L1.request.json` (same race shape).

## Context
Replace fixed short timeouts and immediate existence asserts with polling for the condition up to a generous deadline (for example 120s), failing with the observed state. Negative control: the tests must still fail against the pre-c78e9b5 run_lifecycle.py.

## Constraints
No change to runtime behavior; tests only.
