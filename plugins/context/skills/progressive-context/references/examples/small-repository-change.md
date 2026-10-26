# Small repository change: illustrative workflow

Use when a recurring, bounded repository change needs a clean-context handoff from framing through checking. The stages identify context boundaries, not required directories, role assignments, or an automated sequence. For a one-off edit whose context already fits in one handoff, skip this definition.

## Frame the change

- **Inputs:** request, repository instructions, existing contracts, and relevant implementation.
- **Work/process:** determine the requested outcome, scope, constraints, and checks that would demonstrate it. Record unknowns without inventing answers.
- **Outputs:** one task handoff with a goal, context links, constraints, and the next operation. A project planner may turn that handoff into concrete steps.
- **Exit/evidence:** the handoff names the sources and decisions a fresh worker needs; unresolved questions are explicit. Inspect the saved handoff.

## Make the change

- **Inputs:** task handoff, applicable contract and source revision, and the current plan-step handoff when the project uses steps.
- **Work/process:** make the bounded change and record its actual checks and limitations. Follow the project's existing execution rules.
- **Outputs:** changed artifact and the project's implementation report or equivalent work record.
- **Exit/evidence:** inspect the artifact diff and implementation report against the task's criteria. A self-report alone does not establish acceptance.

## Check and hand off

- **Inputs:** task criteria, changed artifact revision, implementation report, and relevant environment.
- **Work/process:** verify the named behavior and boundaries independently where the project requires it. Record failures and what remains untested.
- **Outputs:** verification or assessment record linked to the checked revision, plus the next task action in the project's existing workflow.
- **Exit/evidence:** each claim cites an observed check or is marked unassessed. A passing task check qualifies only the named change; capability reuse needs its own assessment and independent consumer exercise.

For SDLC Lite, the task handoff and `step-<n>/handoff.md` are the concrete inputs; builder and verifier result files are run outputs. `steps.py next` remains the next-action authority. The stage headings here do not assign roles, advance the board, or enforce exit conditions.
