# Author-written exercise plan

This plan is for a lightweight, model-free pilot. It is not a planner role result and has no `runs.jsonl` entry. The existing `steps.py lint` and `steps.py split` tools can still inspect and derive concrete step handoffs from it.

## Goal
Exercise a reusable workflow-stage contract through one real documentation and skill change.

## Step 1: Author stage guidance and example
level: L1
### Do
Add optional Progressive Context stage guidance and a reusable three-stage example. Link it from the Progressive Context skill and SDLC integration; the illustrative task handoff uses the stage link. This work uses the example's Make the change stage.
### Acceptance criteria
- The stage contract has all four boundary fields and limits Review to user decisions: `python3 -c 'from pathlib import Path; s=Path("plugins/progressive-context/skills/progressive-context/references/workflow-stages.md").read_text(); assert all("**"+x+":**" in s for x in ("Inputs", "Work/process", "Outputs", "Exit/evidence")); assert "**Review:** include only when an actual user decision is required" in s'`.
- The guidance distinguishes the four concepts and denies maturity from stage position: `python3 -c 'from pathlib import Path; s=Path("plugins/progressive-context/skills/progressive-context/references/workflow-stages.md").read_text(); assert all("| "+x+" |" in s for x in ("Capability", "Workflow stage", "Performer role", "Concrete plan step")); assert "It says nothing by itself about a capability\x27s maturity" in s'`.
- The Progressive Context skill and SDLC integration link the optional workflow, and the example defines all three stage boundaries: `python3 -c 'from pathlib import Path; b=Path("plugins/progressive-context/skills/progressive-context"); assert "references/workflow-stages.md" in (b/"SKILL.md").read_text(); assert "workflow-stages.md" in (b/"references/sdlc-lite.md").read_text(); s=(b/"references/examples/small-repository-change.md").read_text(); assert all("## "+x in s for x in ("Frame the change", "Make the change", "Check and hand off"))'`.

## Step 2: Exercise handoffs and inspect checks
level: L1
### Do
Use this task handoff and the generated step handoffs to trace the example's Frame, Make, and Check boundaries. Record actual outputs and validation in `exercise-run.md` without fabricating role results. This work spans Make the change and Check and hand off.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py lint docs/reports/workflow-stage-pilot/exercise-plan.md` succeeds.
- `python3 scripts/check-packaging.py` succeeds.
- The author-written exercise record identifies observed results, unresolved limitations, and the authoritative next-action tool: `python3 -c 'from pathlib import Path; s=Path("docs/reports/workflow-stage-pilot/exercise-run.md").read_text(); assert all(x in s for x in ("Commands run from the repository root", "No tool reads these stage headings", "steps.py next", "no independent verifier report"))'`.

## Risks
This model-free exercise proves the document handoff and tool compatibility, not execution by a fresh model context or automatic stage enforcement.
