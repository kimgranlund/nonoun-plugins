---
id: T-0448
title: "Modernize clarify (our port of find-intent): plan-ready intent, runnable done-when, cost-aware asks"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:clarify` turns a fuzzy ask into a plan-ready intent in one pass: a handoff or plan-doc front block that `steps.py lint` and `plan_check.py` accept without a rewrite, with questions asked only when the answer changes the lane, level, cost or an irreversible step.

## Intent
- Do: modernize `plugins/sdlc-lite/skills/clarify/SKILL.md` (our 48-line port of the older upstream `find-intent` skill; read the upstream copy at `github.com/kimgranlund/claude-plugins` commit 5f9819b86b4dc77934fd36226025cec2e2a88d81, path `harness/skills/find-intent`, as prior art only, vendor nothing) with these changes, each small: (1) the output is the agent-task schema from the doc standards (goal, context pointers, constraints, definition of done, out of scope, verification command) and the plan-doc Outcome block when the work is multi-step; (2) every Done when is a runnable command or the literal `unverifiable: <why>`, and a criterion that reads its own step's verifier result, names a fixed sha or needs a live run a verifier cannot do is refused or moved to `[owner: maintainer]` (the three defects the T-0438 and plan-doc runs hit); (3) a size and lane estimate (`level` L1 to L4, `steps.py lane`) with a one-line cost and reversibility note, so asks are limited to forks that change the lane, the level, the cost, or an irreversible action; (4) tracker awareness per lane-lifecycle section 8.1: claim or create the ticket first in the repo's tracker (local, GitHub, Linear) before any lane; (5) a pass-through for follow-ups that point at session state ("any updates", "do that") so no extraction runs; (6) a low-tier path of three steps (extract, default, write) for Sonnet low and Haiku, matching the per-tier overlay design; (7) the unattended gap and default format kept as is, and a re-run on a changed ask rather than a patch.
- Add a deterministic lint of the clarify output block (goal present, non-goals present, Done when runnable or `unverifiable`, level present) in `plan_check.py` or `steps.py lint`, with a positive case and an observed-red negative control per rule, and 6 to 8 eval cases built from asks in this repo's history (a bare goal, a wrong-unit ask like "build an agent" for a deterministic check, a conflicting ask, an already-scoped ask that must pass through, a follow-up that must pass through, an unattended gap).
- Non-goals: changing `grill`, `ask` or `open-questions`; a model or effort change; porting the upstream references or evals wholesale.
- Done when: `python3 plugins/sdlc-lite/scripts/check.py`, `check-packaging.py` and `bash plugins/sdlc-lite/scripts/check.sh` exit 0; the new lint rules each have an observed-red negative control in the relevant selftest; the eval cases exist under the skill folder and a replay of them through `clarify` yields output the lint accepts for 5 of the 6 non-pass-through cases and one-line pass-through for the 2 pass-through cases (report the replay, mark it unverified if not run); the skill stays self-contained.

## Context
Current skill: `plugins/sdlc-lite/skills/clarify/SKILL.md`. Related: `skills/plan-goal`, `skills/plan-doc` and its format reference, `skills/ask`, `docs/specs/sdlc-lite/lane-lifecycle.md` section 8.1, T-0447 (document standards; the agent-task schema lives in its `work-items.md` card; if T-0447 has not landed, define the block in the skill and let T-0447 reconcile), the per-tier overlay design `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md`. Observed defects of unclear intent in this repo: `docs/reports/2026-10-11-plan-doc-live-run.md` (stale plan, no rule for already-built, unsatisfiable rehearsal criterion in T-0438).

## Constraints
No model or effort change. Hard invariants stay: one question round at most, recommendation first, never drip questions. Skill folder self-contained (`check.py` item 42).
