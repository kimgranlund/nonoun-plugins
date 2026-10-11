---
id: T-0450
title: "Run review-traces on solo first-round verifier non-passes and builder blocked notes; turn findings into agent file changes"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 10
---

## Question
Which concrete wording or rule changes in `plugins/sdlc-lite/agents/*.md` would have prevented the solo first-round verifier non-passes and the builder blocked notes seen since 2026-10-08, and what does each cost to build?

## Goal
A dated report that turns the 34 first-round verifier non-passes on solo tickets and the 173 builder blocked notes into a ranked list of specific agent file changes, each with the evidence rows behind it.

## Intent
- Do: run `/sdlc-lite:review-traces` (its ingest and detect stages make no model call) on ui-kit-maison, agent-ui, ultimate-tokens and sdlc-lite for the window 2026-10-08 to now, then diagnose and verify through its stages. Sample, do not read all: take every first-round non-pass (the verifier result files named `verifier-L<n>.md` whose verdict is not `pass` and whose ticket later passed or closed), classify each root cause into one of: criterion defect (unsatisfiable, vacuous, fixed sha, circular, needs a live run), builder gap (no default for a gap, scope widened, claimed without running), environment (timeout, load, stale base), verifier over-reach, other; and do the same for builder `blocked` notes (plan defect versus environment versus other). Rank causes by count, then by minutes or dollars from the collector. For each top cause name the agent file and rule it would change (`agents/builder.md`, `verifier.md`, `planner.md`, `solo.md`, the overlays), the smallest wording change, and an observable measure (a detect rule or K-005 movement). Compare with what is already shipped (T-0412, T-0413, T-0438, T-0439, overlays T-0441, T-0448 clarify v2) and say what is already covered.
- Non-goals: editing any agent file; filing the proposed changes as tickets without the maintainer's approval; reading every closed ticket; a model or effort change.
- Done when: `docs/reports/<date>-solo-fails-and-blocks.md` exists with the classified counts, the sample size and how it was drawn, the ranked changes with evidence pointers that resolve (the verifier or builder result path for each), what is already covered, and what is unverified; the report passes `docs_check.py`; at most 3 changes are marked "propose a ticket".
- outcome metric: K-005 (docs/kpi/005-solo-first-pass-rate.md, from T-0449), before: 89 of 123 first-pass (72 percent)

## Context
Baseline and method: `docs/reports/2026-10-11-solo-campaign-baseline.md`. Cost per role since 2026-10-08 (collector): verifier 332 runs $220, builder 223 runs $256, planner 80 runs $130, plan-reviewer 41 runs $59, architect 18 runs $47. Builder blocked: maison 29 of 160, ultimate-tokens 8 of 45, agent-ui 2 of 12; of 173 block notes found on disk, 55 name a plan defect. Prior evidence: `docs/reports/2026-10-11-plan-doc-live-run.md`, `docs/reports/2026-10-10-verifier-minutes.md`, `docs/reports/2026-10-11-agent-prompt-lint-baseline.md`. Skill: `plugins/sdlc-lite/skills/review-traces/SKILL.md`. The other repos are read-only for this spike.

## Constraints
Read-only against every repo it inspects. Budget: stop at $10 and report. One independent verifier checks a sample of the report's evidence pointers. Mark unchecked claims [U].

## Plan review
- steps.py split refused planner-L2.md step 1: acceptance criterion compares a count over a changing set with a fixed number: f=$(ls docs/reports/*-solo-fails-and-blocks.md) && test "$(grep -c "propose a ticket" "$f")" -le 3. other lanes change the set: derive the set at run time, or check only this step's own items. plan defect: replan this step (/chain 3)
- dispatch.py prepare builder L3 refused step-1/handoff.md (steps.py lint links): cited path does not exist: .sdlc/0450-review-traces-solo-fails-and-blocks/sample.py; cited path does not exist: .sdlc/tickets/ (a ui-kit-maison path resolved against this repo). plan defect: replan this step (/chain 3). Second plan-defect refusal for this task: stopped unattended per /chain 3. Note: steps.py lint rejects a .sdlc/ path a step is told to create, and a foreign-repo .sdlc/ path.
