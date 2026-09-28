## Task goal
Pilot optional workflow-stage contracts in Progressive Context using the existing SDLC Lite handoff and step tools, with an inspectable example and observed validation.

## Step 2: Exercise handoffs and inspect checks
level: L1
### Do
Use this task handoff and the generated step handoffs to trace the example's Frame, Make, and Check boundaries. Record actual outputs and validation in `exercise-run.md` without fabricating role results. This work spans Make the change and Check and hand off.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/workflow-stage-pilot/exercise-plan.md` succeeds.
- `python3 scripts/check-packaging.py` succeeds.
- The exercise record identifies observed results, unresolved limitations, and the authoritative next-action tool.
