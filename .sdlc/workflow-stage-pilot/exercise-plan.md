# Author-written exercise plan

This plan is for a lightweight, model-free pilot. It is not a planner role result and has no `runs.jsonl` entry. The existing `steps.py lint` and `steps.py split` tools can still inspect and derive concrete step handoffs from it.

## Goal
Exercise a reusable workflow-stage contract through one real documentation and skill change.

## Step 1: Author stage guidance and example
level: L1
### Do
Add optional Progressive Context stage guidance and a reusable three-stage example. Link it from the skill and SDLC integration, and allow an optional reference in SDLC Lite task handoffs. This work uses the example's Make the change stage.
### Acceptance criteria
- The stage definition names inputs, work/process, outputs, and exit/evidence, with review only for an actual user decision.
- Guidance distinguishes capability, workflow stage, performer role, and concrete plan step; stage position does not establish capability maturity.
- The skill and handoff guidance link the example without requiring new runtime state or a fixed task folder layout.

## Step 2: Exercise handoffs and inspect checks
level: L1
### Do
Use this task handoff and the generated step handoffs to trace the example's Frame, Make, and Check boundaries. Record actual outputs and validation in `exercise-run.md` without fabricating role results. This work spans Make the change and Check and hand off.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/workflow-stage-pilot/exercise-plan.md` succeeds.
- `python3 scripts/check-packaging.py` succeeds.
- The exercise record identifies observed results, unresolved limitations, and the authoritative next-action tool.

## Risks
This model-free exercise proves the document handoff and tool compatibility, not execution by a fresh model context or automatic stage enforcement.
