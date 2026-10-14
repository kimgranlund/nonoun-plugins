---
id: T-0556
title: "Plugin-level machine-wide slot limit for heavy commands across repos"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Heavy commands (browser tests, full suites, builds) from every repo on the machine share one plugin-provided slot limit, so parallel lanes across repos cannot overload the machine.

## Intent
- Do: `scripts/slot.sh` (or `slot.py`) wraps a command in a machine-wide counting lock under the user's cache dir (`~/Library/Caches/sdlc-lite/slots` on macOS, `$XDG_CACHE_HOME/sdlc-lite/slots` elsewhere): `slot.sh run [--slots N] -- <cmd>`, default N from `heavy_slots:` in `.sdlc/config` or 2, released on exit or crash (pid-checked).
- Do: document it in the conductor contract and `/fanout` so lanes route heavy checks through it; a repo's existing `gate_lock` or `browser-slot.sh` can delegate to it.
- Non-goals: replacing a repo's own test runner; scheduling across machines.
- Done when: selftest runs 3 commands with N=2 and observes at most 2 concurrent, and a crashed holder's slot is reclaimed (negative control: without the wrapper, 3 run at once); `check.sh` passes.

## Context
2026-10-14: load average 54 on 20 cores; gen-ui-kit (`gate_lock`) and maison (`.sdlc/browser-slot.sh`) each built their own limiter; `adia/ui-kit` had none and drove a second spike.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.
