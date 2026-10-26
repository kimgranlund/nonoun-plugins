# Stage 3 — Apple-inspired familiarity and container review

## Own

Recognition over relearning: familiar navigation, container composition, action locations, platform interaction expectations, and responsive/focus continuity. Use conventions appropriate to the actual platform and domain; do not transplant Apple styling or platform rules into every product.

## Ask after the sequence is settled

- What familiar pattern does this moment resemble? Does it behave as that appearance promises?
- Are users learning a new pattern unnecessarily? If novel, what benefit justifies the learning cost and what familiar behavior anchors it?
- Can users predict where identity, content, content operations and final commitment will appear?
- Are navigation, selection, editing and execution represented distinctly?
- Does the narrow or keyboard experience preserve the same mental model?

## Container rubric

| Region | Scope and expected responsibility |
| --- | --- |
| Header | Container identity/context, Back, close/collapse and scoped status. |
| Optional toolbar | Operations on the displayed body: search, filters, sorting, view selection, selection actions. |
| Body | Reading, comparison, selection or editing content; local errors and actions stay beside their subject. |
| Optional footer | Complete the container's task: Save/Cancel, Apply/Cancel, decisions, or conversation composer. |

Start/end placements follow reading direction and platform conventions, not fixed left/right coordinates. Identify each action's scope before placing it. New record belongs to list operations; editing a record belongs to its detail; committing a draft belongs to its transaction. Do not duplicate primary commits in several slots without a demonstrated need.

Use optional regions only when meaningful. Header/body/footer is a composition vocabulary, not mandatory empty furniture or a demand for new components. Reuse the project's supported container/part APIs and geometry. Keep alternate-state specimens outside the represented interface.

## Evaluate

- **Familiarity:** appearance and operation match a recognizable pattern or justify a bounded departure.
- **Slot consistency:** identity, operations and commitment occupy predictable, scope-correct regions.
- **Navigation consistency:** Back, close, cancel, selection and editing have stable meanings.
- **Access and adaptation:** describe expected keyboard/focus behavior, reading order, narrow layout and scroll ownership; mark untested behavior unknown.

For bounded panes/dialogs, declare one scroll owner and explicit sticky behavior. Preserve focus visibility and usable body space; page sections normally flow. Do not force sticky chrome or a footer onto all contexts.

## Exit

Return a region → responsibility → component/pattern map, with any justified novelty and the recognition cost it introduces. Do not polish wording except to identify ambiguous semantics for stage 4.

For inside-out validation, identify which transaction and navigation scope each local action belongs to. Check that control behavior composes with container commitment, focus, scroll and return paths; a familiar-looking footer is wrong if it saves a different scope from the body it appears to own.
