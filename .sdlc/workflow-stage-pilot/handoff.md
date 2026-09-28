## Goal
Pilot optional workflow-stage contracts in Progressive Context using the existing SDLC Lite handoff and step tools, with an inspectable example and observed validation.

## Context
This task exercises the reusable [small repository change workflow](../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md). The framing stage produced this handoff; the current stage is [Make the change](../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md#make-the-change). [Check and hand off](../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md#check-and-hand-off) uses the actual changed files and checks recorded in `exercise-run.md`.

Inputs at the boundary: the approved small-pilot scope, repository and plugin AGENTS.md instructions, the Progressive Context skill and its SDLC integration, and the SDLC Lite handoff format. Base source revision: `a4404cb` on `main`. An author-written exercise plan is in `exercise-plan.md`; `steps.py split` will generate the concrete step handoffs. No planner, builder, or verifier model role was invoked for this exercise.

## Constraints
Keep the stage definition reusable and separate from this `.sdlc/` run. Do not add runtime routing, a stage status, a universal folder tree, or model-allocation changes. Existing `steps.py next` retains build and verification routing. Do not claim that a documented exit condition was enforced or that completing a stage qualifies a capability for reuse.
