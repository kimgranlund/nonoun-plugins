# Optional workflow stages

Read when a recurring process needs explicit handoffs between kinds of work. A workflow definition is reusable guidance; a task handoff and its run records describe one occurrence. Keep the definition outside the task's run directory and link it from the handoff. Start with an existing project process when one exists. [Small repository change](examples/small-repository-change.md) is an example, not a required layout or sequence.

Use these distinctions when selecting records:

| Concept | Question it answers | Example |
| --- | --- | --- |
| Capability | What can a product, artifact, or process do, and under what contract? | A command's supported input and output |
| Workflow stage | What context must pass between recurring kinds of work? | Frame a change before implementation |
| Performer role | Who or what performs work in a particular run? | An SDLC builder or a human editor |
| Concrete plan step | What bounded change and acceptance criteria apply in this task? | Add a link to a handoff template |

A stage can involve multiple roles or plan steps; a role can participate in different stages. Stage position describes where work sits in a workflow. It says nothing by itself about a capability's maturity or reuse eligibility. Those claims still need the capability contract and applicable evidence in [the evidence guide](evidence.md).

Define only stages whose boundary changes what the next worker needs to read or produce. A useful stage contract has:

- **Inputs:** authoritative links, decisions, and prerequisites to load.
- **Work/process:** the operation and its scope, without copying an entire role procedure.
- **Outputs:** artifact names or links that the next stage can inspect.
- **Exit/evidence:** observable conditions and the records that show them. An exit description is guidance unless an existing tool checks it.
- **Review:** include only when an actual user decision is required before the next stage; identify the decision and its reviewable material.

At a boundary, the task handoff may link the reusable workflow and the relevant stage contract, then name the concrete input revisions, results, unresolved findings, and next operation. Link existing artifacts rather than copying them into the workflow definition. Do not add a stage status field, scheduler, or second next-action rule: use the project's current planner, run, and verification records for execution. If SDLC is present, [its integration guide](sdlc.md) explains the mapping.
