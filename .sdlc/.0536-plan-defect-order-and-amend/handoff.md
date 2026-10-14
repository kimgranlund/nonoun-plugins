---
id: T-0536
title: "Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0543]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect.

## Intent
- Do: find where a criterion that can only pass after a later step can be caught cheaply: a planner self-check, a plan-reviewer instruction to run each step's criteria against the tree state that step will see, or a `steps.py lint` rule for criteria naming files or tests a later step owns. Choose from evidence, state the rejected options.
- Do: a narrow route to amend one criterion of one unbuilt step after a builder reports a plan defect, mirroring `steps.py swap` for the verifier case: bounded to one criterion, recorded, and counted against the one-replan cap.
- Non-goals: removing the full replan route.
- Done when: `steps.py selftest` covers the amend route (positive, and a refusal when the step is already built) and the chosen order check has a positive case and an observed negative control.
- Full chain reason: changes next-action decisions in `steps.py`, a behavioral invariant.

## Context
maison T-0546 observations 35, 36: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.

## Outcome

2026-10-14 · lane: full L3 · verdict: closed by reason (delivered by the full chain lane; no filer by default (lean records); gate: full) · verifier: verifier-L2 (sonnet) · base: ab94588622d9
- Changed: see commits
- Commits: 88c83cb T-0536: Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect (maison T-0546)
- Check: step-1#1 (red) selftest plus the four `(order)` ok lines: pass
- Check: step-1#2 (red) planner sentence: pass
- Check: step-1#3 (red) "a later step creates" in `docs/references/sdlc-internals.md` and `steps.py`: pass
- Check: step-1#4 lint of `.sdlc/.0520-ui-designer-agent/planner-L3-2.md`: pass
- Check: step-1#5 (guard) `claude_roles.py generate --check`: pass
- Check: step-1#6 (guard) `codex_roles.py generate --check`: pass
- Check: step-1#7 (guard) scope allow-list: pass
- Check: step-2#1 (red) selftest plus the five pinned `ok:` lines: pass
- Check: step-2#2 (red) `amend <step dir>` in steps.py: pass
- Check: step-2#3 (red) `'steps.py amend'` in check.py: pass
- Check: step-2#4 (red) "note always replans" absent from chain/SKILL.md: pass
- Check: step-2#5 (red) `steps.py amend` in AGENTS.md and sdlc-internals.md, `amend old:` in builder.md: pass
- Check: step-2#6 (guard) `check.py`: pass
- Check: step-2#7 (guard) `claude_roles.py generate --check`: pass
- Check: step-2#8 (guard) `codex_roles.py generate --check`: pass
- Check: step-2#9 (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: pass
- Check: step-2#10 (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass
- Check: step-2#11 (guard) scope allow-list: pass
- Deviation: step-2: process deviation: red-checkpoint: retrospective: attempt 1d8286be8e964f6da4791f7e5d7f6baa, handoff sha256 3efda7789ed8, 4 of 4 (red) criteria without a pre-edit red control: `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && ...`; `grep -qF "'steps.py amend'" plugins/sdlc-lite/scripts/check.py`; `! grep -qF "note always replans" plugins/sdlc-lite/skills/chain/SKI...`; `grep -qF "steps.py amend" plugins/sdlc-lite/AGENTS.md && grep -qF "...`
