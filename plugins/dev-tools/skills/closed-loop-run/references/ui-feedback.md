# Close a UI feedback loop

Use when user feedback reveals a visual, composition or interaction defect, especially after an earlier repair or passing check. This specializes the parent skill's diagnosis, evaluator integrity and progressive verification; it does not require a fresh generation, design-crit team or new test framework.

For a read-only retrospective, complete the diagnosis and propose checks without editing artifacts or executing mutations. Report assessment completed separately from artifact repair unverified; the repair steps below apply only when authorized.

## Frame the discrepancy

Translate the feedback into an observable relationship before editing: which control acts on which objects, its scope, where that relationship is communicated, and the expected outcome. Use the screenshot as evidence of a visible state, not proof of DOM semantics or hidden behavior. Ask only if competing interpretations would produce materially different repairs; continue independent inspection while waiting.

For a structural change, revisit the affected region as a whole. A control retained from the old layout may still function but belong in a different location or hierarchy. Check control-to-target ownership, group boundaries, primary versus secondary actions, and visual/semantic association. Do not infer good composition from valid primitive geometry or component counts.

Record acceptance before choosing the repair: a visible/semantic relationship, an interaction outcome, and the relevant narrow/keyboard state. Distinguish user-required placement from a proposed design choice. Do not turn one example into a rule that all interfaces must copy.

## Diagnose both the artifact and the missed detection

Inspect current authored composition, rendered geometry/semantics, relevant component APIs and canonical recipe/specimen. Compare at least the plausible boundaries; do not expand into a full audit:

| Outcome | Evidence needed before choosing it | Smallest fix owner |
|---|---|---|
| Existing pattern not found or confused with a neighboring pattern | Inspect naming, intent/avoidWhen, aliases and competing routes; show the missing/ambiguous edge or contradiction | Existing registry/recipe selection guidance |
| Existing pattern implemented incorrectly | Required relationship/API is supported, but authored composition deviates; record whether governing guidance was delivered | App integration and outcome regression; do not add a duplicate component |
| Existing pattern lacks a needed feature | Name the exact unsupported state, operation or relationship after inspecting its public contract and implementation; distinguish absent API from a bug in promised behavior | Extend the existing owner compatibly, or repair its bug |
| No suitable pattern exists | Scoped search and closest alternatives cannot satisfy the required contract without recreating a reusable capability | Propose the smallest new pattern/API with acceptance and ownership; author only when authorized |
| Intentional application-specific composition | Existing primitives cover the needs; novelty is domain data, orchestration or brand layout without established reusable demand | Keep local; track recurrence rather than prematurely promote |
| Evaluation missed the defect | Previous checks pass the rejected arrangement or encode the implementation as the oracle | Existing outcome check and review procedure |
| Uncertain intent, incomplete evidence or environment failure | Conflicting requirements, unread authority, missing runtime evidence or unavailable tooling prevent distinguishing causes | Clarify or obtain the missing evidence; do not label an unsearched capability absent |

More than one outcome may apply: an app integration error and a verifier blind spot often coexist. Record discovery, capability, implementation and evaluation findings separately. A pattern name match is not evidence of feature completeness; a failed lookup is not proof that a new pattern is needed. Use the primitive contract/resolver only when the supported composition itself violates its promised geometry or behavior.

For a retrospective, distinguish authority available at the time from current documentation. Current support can justify a repair but cannot prove that an earlier author received that guidance.

Before concluding that no suitable pattern exists, name the required behavioral contract, the canonical search scope, and the closest plausible alternatives inspected with their concrete limitations. Unread plausible alternatives or unresolved naming conflicts keep the conclusion provisional; no fixed number of failed searches proves absence.

Explain the mechanism with source and rendered evidence. Mark contributing hypotheses separately; a document improvement does not prove the old wording caused the decision. If the user catches a defect after a claimed pass, explicitly identify what the previous checks did and did not establish. Avoid blaming context routing merely because an agent produced the artifact.

## Bounded repair and discriminating verification

Use the parent episode contract, scaled to the task: one coupled defect, a small attempt limit, explicit editable owners, preserved outcomes and a stop on repeated no-progress. Repair the earliest demonstrated cause within authorization. Propose broader alternatives with their tradeoffs instead of silently redesigning neighboring flows.

Strengthen the existing check so the original rejected arrangement fails. Prefer the preserved pre-fix artifact; otherwise use a reversible, clearly labeled mutation of the current result that recreates the relevant defect. Explain what the mutation does not reproduce. Prove failure, restore the intended arrangement, and prove success. A passing screenshot/column count alone is not a discriminating test of control placement or scope.

Separate the outcome oracle from the chosen implementation contract. A baseline failing because it lacks a newly chosen component or selector proves structural difference, not the original relationship failure. Use the same observable relationship on both versions where possible; otherwise retain independent evidence of the original failure and label the structural check’s narrower scope. A supported alternate composition should not fail the outcome oracle merely for using different hosts.

Check the relationship outside-in on the final rendered artifact, then inside-out against supported API/geometry. For changed interactive groups, exercise scope, mixed/empty states where applicable, keyboard activation and focus visibility; verify narrow layouts without shrinking controls. Wait for readiness and settled appearance before captures. Rebuild affected output after edits and bind final evidence to final source. Reuse unaffected evidence rather than repeatedly running broad suites.

## Close and learn

Keep three conclusions separate: artifact corrected, regression discriminates, future agent behavior unverified. If only the symptom improves, use IMPROVED rather than RESOLVED. Preserve original and repaired evidence and the rationale for changed acceptance; never rewrite a historical success into proof of the newly added criterion.

Match each causal and completion claim to its actual evidence. Record whether support comes from runtime observation, source inspection or inference; a before/after pass supports the tested mechanism, not an exclusive explanation or a historical routing cause. For preservation claims, compare relevant values and stable IDs rather than only existence/counts. A compound test name or early failure does not prove every clause or later scenario ran; report viewport, setup and assertions actually reached. Qualify unsupported clauses or queue a focused check instead of upgrading them from adjacent evidence.

Retain concrete UI/API rules in the repository's canonical recipe or component owner. Retain the general diagnosis-and-detection lesson here. Entry skills and kickoff routes should link to owners rather than duplicate checklists. No new skill, runner or generation trial is needed when existing owners can carry the correction.

The report should name the symptom, confirmed cause and any hypothesis, proposed/implemented fix by layer, negative-control result, final outcome checks, and remaining limits. Stop after the bounded repair and learning record; recurrence reduction requires later observed use.
