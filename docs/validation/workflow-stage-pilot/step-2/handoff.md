## Task goal
Pilot optional workflow-stage contracts in Progressive Context using the existing SDLC Lite handoff and step tools, with an inspectable example and observed validation.

## Step 2: Exercise handoffs and inspect checks
level: L1
### Do
Use this task handoff and the generated step handoffs to trace the example's Frame, Make, and Check boundaries. Record actual outputs and validation in `exercise-run.md` without fabricating role results. This work spans Make the change and Check and hand off.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py lint docs/validation/workflow-stage-pilot/exercise-plan.md` succeeds.
- `python3 scripts/check-packaging.py` succeeds.
- The author-written exercise record identifies observed results, unresolved limitations, and the authoritative next-action tool: `python3 -c 'from pathlib import Path; s=Path("docs/validation/workflow-stage-pilot/exercise-run.md").read_text(); assert all(x in s for x in ("Commands run from the repository root", "No tool reads these stage headings", "steps.py next", "no independent verifier report"))'`.
