---
id: T-0306
title: "fleet_detect.py: waste and stall detect rules"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0305]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Mechanical rules that flag waste and stalls in a collector fingerprint, each with the evidence field that triggered it.

## Intent
- Do: Add plugins/sdlc-lite/scripts/fleet_detect.py with `detect <fingerprint.json>... ` printing findings as JSON lines (rule id, repo, evidence path, measured value, threshold), plus `selftest`. Rules at minimum: planner results per ticket over 5; plan-review plus planning share of spend over 40 percent; size M ticket with more than 20 criteria; any hook process over 50 percent CPU for over 20 seconds; Chromium over 30 processes or 6 GB; interrupted or limit-marker attempts over 3; a session whose plugin version is older than the installed one; a CI workflow with more than 25 push runs in 7 days duplicating its pull_request runs.
- Non-goals: Fixing any finding; model judgment.
- Done when:
  - Each rule has a fixture that triggers it and one that does not (a positive and a negative per rule, observed).
  - Running detect on the fingerprints of the three repos reproduces these known findings: agent-ui plan-review share over 40 percent, maison a size M ticket over 20 criteria is not required, maison and gen-ui-kit Chromium over the threshold.
  - Thresholds live in one table at the top of the file and are documented.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06 after three repo root-cause reports (maison, agent-ui, gen-ui-kit, each at root-cause-2026-10-06.md in its repo). Design: a thin skill `/sdlc-lite:fleet-retro` on top of the existing `review-traces` skill: a deterministic collector, mechanical detect rules, a 5-question conductor interview, one cross-repo ranked report, a sampled verifier, then filing through review-traces. Existing pieces to reuse: runs.jsonl dedupe by attempt_id (agent-ui's method), scripts/budget.py cost sums, skills/review-traces/SKILL.md, scripts/footprint.py. Build after the 0.20.11 batch ships; target release 0.21.1.

## Constraints
No model call inside collect or detect. Read-only on every repo it inspects. No em dashes. No change to any model or effort value. No push, tag or publish.
