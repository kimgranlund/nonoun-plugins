---
id: T-0557
title: "check.sh runs selftests in parallel and offers a fast tier"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
branch: lane/T-0557-w72-0557
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`check.sh` finishes much faster: selftests run in parallel, and a fast tier covers the common gate in a few minutes.

## Intent
- Do: run independent selftests concurrently (bounded by cores and the T-0556 slot when present), keeping output per selftest and the first failure's name; add `check.sh --fast` for the structural and quick selftests, used by builders (T-0551) and the CI workflow (T-0554); full `check.sh` stays the land gate.
- Non-goals: dropping any selftest from the full run.
- Done when: full `check.sh` wall time drops measurably on an idle machine (record before and after); `--fast` runs in under 5 minutes; a planted failing selftest still fails both tiers (negative control).

## Context
2026-10-14: `check.sh` took 18 min idle and 47 min under load, and runs in every builder, verifier, and gate.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.
