---
id: T-0308
title: "/sdlc-lite:fleet-retro skill, cross-repo report, verification sample"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0305, T-0306, T-0307]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `/sdlc-lite:fleet-retro` skill that runs collect, detect, interview, synthesis, a sampled verification and filing across a list of repos.

## Intent
- Do: Add plugins/sdlc-lite/skills/fleet-retro/SKILL.md (frontmatter with a routing description and a NOT-for clause; argument `<repo>...`; allowed tools limited to the scripts). Workflow: (1) run fleet_collect.py per repo with --gh; (2) run fleet_detect.py over the fingerprints; (3) send the interview template to each repo's conductor with SendMessage and wait for the one-line replies; (4) synthesize one report at docs/reports/fleet-retro-<date>.md: a cross-repo table ranked by cost, each finding with its evidence pointer and [V] or [U]; (5) a read-only verifier subagent re-checks a 20 percent sample of the [V] claims against their evidence and downgrades any it cannot reproduce; (6) hand confirmed findings to review-traces for filing after the user approves. Add the skill to the packaging and discovery checks, and a one-line mention in docs/maintenance/sdlc-internals.md. Add plugins/sdlc-lite/skills/fleet-retro/rubric.md (the actionability rubric: gates G1 to G5 pass or fail, graded criteria C1 to C5 scored 0 to 2, threshold 7 of 10, plus the outcome check that a closed ticket moved its metric) and make the step 5 verifier apply it to every finding, not only sample [V] claims. Calibrate on the three 2026-10-06 reports and the hook perf finding. Do not make it run unattended: it ends with one AskUserQuestion round for filing.
- Non-goals: Scheduling (a later /plan-loop can do it); building new collectors.
- Done when:
  - `check.py` and `check-packaging.py` pass with the skill present; the discovery route lists it.
  - A live run on agent-ui and maison (read-only) produces a report that includes the 193-run total for agent-ui and flags the plan-review share, and the verifier sample downgrades a planted false [V] claim (observed negative control).
  - The report contains no claim without an evidence pointer.
  - The rubric run on a fixture set (one clearly actionable finding, one stale-version misattribution, one unverified ceiling guess) scores them above, below and below the threshold respectively (observed).
  - `tickets.py check` passes.

## Context
Decided by the user on 2026-10-06 after three repo root-cause reports (maison, agent-ui, gen-ui-kit, each at root-cause-2026-10-06.md in its repo). Design: a thin skill `/sdlc-lite:fleet-retro` on top of the existing `review-traces` skill: a deterministic collector, mechanical detect rules, a 5-question conductor interview, one cross-repo ranked report, a sampled verifier, then filing through review-traces. Existing pieces to reuse: runs.jsonl dedupe by attempt_id (agent-ui's method), scripts/budget.py cost sums, skills/review-traces/SKILL.md, scripts/footprint.py. Build after the 0.20.11 batch ships; target release 0.21.1.

## Constraints
No model call inside collect or detect. Read-only on every repo it inspects. No em dashes. No change to any model or effort value. No push, tag or publish.
