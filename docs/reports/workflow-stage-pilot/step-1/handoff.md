## Task goal
Pilot optional workflow-stage contracts in Progressive Context using the existing SDLC Lite handoff and step tools, with an inspectable example and observed validation.

## Step 1: Author stage guidance and example
level: L1
### Do
Add optional Progressive Context stage guidance and a reusable three-stage example. Link it from the Progressive Context skill and SDLC integration; the illustrative task handoff uses the stage link. This work uses the example's Make the change stage.
### Acceptance criteria
- The stage contract has all four boundary fields and limits Review to user decisions: `python3 -c 'from pathlib import Path; s=Path("plugins/progressive-context/skills/progressive-context/references/workflow-stages.md").read_text(); assert all("**"+x+":**" in s for x in ("Inputs", "Work/process", "Outputs", "Exit/evidence")); assert "**Review:** include only when an actual user decision is required" in s'`.
- The guidance distinguishes the four concepts and denies maturity from stage position: `python3 -c 'from pathlib import Path; s=Path("plugins/progressive-context/skills/progressive-context/references/workflow-stages.md").read_text(); assert all("| "+x+" |" in s for x in ("Capability", "Workflow stage", "Performer role", "Concrete plan step")); assert "It says nothing by itself about a capability\x27s maturity" in s'`.
- The Progressive Context skill and SDLC integration link the optional workflow, and the example defines all three stage boundaries: `python3 -c 'from pathlib import Path; b=Path("plugins/progressive-context/skills/progressive-context"); assert "references/workflow-stages.md" in (b/"SKILL.md").read_text(); assert "workflow-stages.md" in (b/"references/sdlc-lite.md").read_text(); s=(b/"references/examples/small-repository-change.md").read_text(); assert all("## "+x in s for x in ("Frame the change", "Make the change", "Check and hand off"))'`.
