---
name: design-crit
description: Critique product interfaces, workflows, and wireframes using outside-in decomposition and inside-out validation with four sequenced specialist reviewers. Use for design critique and UX review, not ordinary code review or automatic implementation.
---

# Design critique

The core method is **bidirectional decomposition**: peel the design onion outside in to establish what each layer must accomplish, then work inside out to check whether the parts actually compose into that experience. Ask the right type of question at the right level and in dependency order. The outcome is a coherent design decision, not four competing aesthetic opinions.

## Outside in, then inside out

These are complementary reasoning passes, not competing aesthetic viewpoints. “Outside” means user purpose and domain context, not the outer border of a screen. “Inside” means concrete operations and their effects, not merely implementation code.

| Layer | Outside-in question: purpose → constraints | Inside-out question: evidence → consequence |
| --- | --- | --- |
| Purpose and domain | Whose problem is this, what outcome matters, and what domain rules must hold? | Does the resulting experience complete that job and preserve those rules? |
| Journey and meaningful moments | What decisions must happen, in which order, with what context? | Do local transitions compose into a complete journey without lost context, redundant commits or dead ends? |
| Surfaces and containers | What belongs together, and which familiar regions own identity, work and commitment? | Do controls and content share the right scope, and do navigation/scroll/focus behavior preserve continuity between regions? |
| Controls, state and language | What can the user do here, what changes, and how is that represented? | Does the actual action/result/recovery match its label, state and promised scope? |

Before descending a layer, record its purpose, governing constraints, decisions and unresolved assumptions. Do not choose a component to compensate for an undefined task, simplify copy before knowing the operation, or rearrange a footer before identifying the transaction it commits. Decompose only as deeply as needed to explain the design risk; do not inventory every pixel.

Then trace representative operations back outward. Follow **control → state transition → container transaction → journey consequence → user outcome**, including the most consequential interruption or recovery path. Check composition, not just each part in isolation: individually reasonable controls can collectively produce duplicate commitments, lost drafts, overload or an incomplete job. Internal elegance does not establish usefulness.

Use a lightweight layer map with stable IDs, parent purpose, local responsibility, constraints and evidence/unknowns. Record which layer owns each finding and which layers it affects. When a low-level symptom contradicts a higher-level premise, reopen the nearest responsible layer; do not patch the symptom with more copy or automatically restart the entire review.

The method is complete when the outer intent has a traceable path to concrete behavior and the inner behavior has been traced back to the intended outcome—or the missing evidence is explicitly reported. Static artifacts support a represented walkthrough; they do not establish runtime correctness. For scoped work, include only the relevant layers and their immediate dependencies.

The reviewer names are hypothetical professional lenses, not company affiliations, endorsements, proprietary rubrics, or instructions to imitate a brand's visual style. Their responsibilities below are deliberately distinct.

## Establish the review boundary

Identify the requested artifact/version, target users, domain, primary task and success condition, relevant constraints, and whether the request authorizes critique only or revision. Inspect the artifact itself; do not critique only its description. For visual artifacts, inspect a rendered view as well as relevant source. For interactive claims, exercise the actual behavior when available and authorized.

Use product specifications, existing terminology, observed behavior, and the project's component registry as evidence. Distinguish domain convention, platform convention, local design-system rule, and stylistic preference. Verify consequential external claims against authoritative sources when needed; never cite a reviewer persona as authority. A conventional pattern in one domain is not automatically appropriate in another.

Ask only for missing information that would materially change the critique. Otherwise state a bounded assumption and proceed. Do not create speculative personas, add new workflows, or treat a wireframe's placeholder text as a requirement.

Prepare a compact shared brief:

- Artifact/version and stable screen/panel IDs.
- User, task, domain entities and known constraints.
- Evidence available versus unknown behavior.
- Existing decisions, open questions, and scope of permitted changes.

## Four specialists, in this order

The specialists are lenses applied to the decomposition, not substitutes for its layers. For a full critique, the **outside-in pass** spawns the four sub-agents **sequentially**, not as a simultaneous opinion poll. Use available sub-agent tools, not new user-owned chats. Start each with fresh context when supported and pass the brief, layer map, artifact paths/links, its reference file, and the latest decision handoff. Give it read-only ownership; the parent owns synthesis and edits. Do not override model settings without another applicable instruction.

| Stage / task name | Specialist | Primary responsibility | Reference |
| --- | --- | --- | --- |
| 1 / `crit_domain` | Linear Principal UX Designer lens | Domain-driven task model and established workflow conventions | [Domain review](references/01-domain.md) |
| 2 / `crit_experience` | Figma Principal UX Designer lens | Experience density, grouping, sequence, and continuity | [Experience review](references/02-experience.md) |
| 3 / `crit_familiarity` | Apple Principal UX Designer lens | Familiar interaction patterns, containers, and action placement | [Familiarity review](references/03-familiarity.md) |
| 4 / `crit_clarity` | Braun Principal Product Designer lens | Controlled language and honest, consistent control grammar | [Clarity review](references/04-clarity.md) |

Read each reference before dispatching that stage. Each assignment must include:

> Review this artifact using the attached stage rubric and the current decomposition layer. Inspect the actual artifact. State the question your layer must answer before descending. Treat the handoff as decisions to test, not unquestionable conclusions. Stay within your specialty; flag upstream contradictions instead of silently redesigning upstream work. Return the shared finding format, stage exit judgment, and what the inside-out pass must verify about your decisions. Do not edit artifacts, spawn additional agents, send external messages, or claim unobserved runtime verification.

After each result, the parent resolves necessary findings into the handoff before starting the next stage. Update the artifact only when revisions are authorized; otherwise pass explicit proposed changes keyed to artifact IDs so downstream reviewers know what is unresolved. Do not present a proposed repair as an already verified screen.

Keep the handoff cumulative: artifact/version, accepted decisions with evidence, unresolved upstream issues and their dependent scope, assumptions, proposed-but-unapplied changes, and the next stage's permitted questions. Preserve earlier unresolved items until explicitly resolved or excluded with a reason; a new reviewer result must not silently erase them. Carry only relevant findings, not whole review transcripts.

An upstream issue that invalidates later work stops dependent review. Resolve it from available evidence, or ask the user the specific domain/intent question needed. Independent observations may continue, but do not polish downstream details on an unresolved foundation. Routine local choices do not require approval.

For a scoped follow-up, run only affected stages plus relevant downstream checks; state what is omitted and why. A copy-only review need not restart domain discovery if the task model is unchanged. Honor an explicitly requested reviewer subset/order, but report material prerequisites rather than inventing conclusions. If delegation is unavailable, disclose that the parent is applying the lenses sequentially; do not claim independent reviews occurred.

## Reverse integration pass

After the outside-in reviews, the parent performs **one inside-out pass** using the artifact and accumulated evidence: Braun's operations/language → Apple's container and interaction scope → Figma's sequence/continuity → Linear's domain outcome. This is not a second round of general opinions and does not require four new agents. Reuse a relevant specialist only when a discovered contradiction needs independent resolution; give it the specific broken trace, not the whole task again.

For each selected trace, record the initiating action, observed or represented transition, transaction owner, next moment, eventual outcome and any broken dependency. Verify the primary flow plus relevant failure/cancellation/uncertainty, rather than an exhaustive state matrix. For example: a “Retry” label may be locally clear, but tracing its effect outward can reveal that an uncertain send risks duplicating the user's external action. Repair the execution/recovery model before polishing the button.

If this pass changes an upstream decision, recheck only its affected downstream dependents and trace the repaired path outward once. Apply the bounded re-review rule below. Report any unresolved contradiction; do not claim the onion is coherent because every specialist individually approved a layer.

## Common rubric and finding format

Rate each stage criterion **supported**, **needs revision**, **unknown**, or **not applicable**. Ratings need evidence; do not calculate an aggregate quality score. A static mockup can support represented hierarchy and copy, not certify keyboard behavior, accessibility, cancellation, or persistence.

Return at most five high-impact findings per stage; fewer or none is valid. Each finding includes:

1. Stable ID, owning layer, affected parent/dependent layers, and exact screen/state/element.
2. Observed evidence and confidence (confirmed observation or hypothesis).
3. User consequence and the criterion violated.
4. Classification: **necessary**, **recommended**, or **preference**.
5. Smallest concrete revision and its tradeoff: name the interface element, what moves, merges, disappears, or changes behavior, and how that serves the task. Distinguish interface changes from documentation-only clarifications.
6. Verification question or acceptance scenario.

Also return decisions worth preserving, unknowns that affect the conclusion, and a stage exit: **ready**, **ready with explicit assumptions**, or **upstream issue to resolve**. Necessary means required for the stated task, integrity, or demonstrated usability—not the reviewer's taste.

## Synthesize without voting

Merge duplicate findings by causal issue. Preserve dissent where evidence is incomplete. Resolve conflicts by explicit user goals and domain truth, then observed usability/evidence, familiar conventions, local consistency, and finally stylistic preference. Do not average incompatible workflows or automatically obey the last reviewer.

Maintain a short decision record: competing recommendations → chosen behavior → reason/evidence → tradeoff → affected states → validation. Later stages may reopen earlier decisions only with a concrete contradiction or new evidence. For example, replace ambiguous “Retry” with the actual recovery operation; do not merely rename a potentially duplicate external send.

Use no more than one downstream re-review per materially changed stage by default. If uncertainty remains, report it and propose the smallest user test; avoid endless critique loops. Do not spawn a fresh set of personas to manufacture consensus.

## Verify recommendation-to-interface translation

For revisions, accepted recommendations must translate into meaningful changes to the interface, not just annotations describing better behavior. Map each accepted finding to an affected screen/state and a concrete change in grouping, hierarchy, action placement, control treatment, visible language, or interaction. If a recommendation concerns ownership or task structure, make that relationship legible in the interface itself; an explanatory footer or README is not a substitute.

Require a rendered before/after comparison of the affected interfaces before calling a revision complete. Use matched screen/state IDs, comparable scale and viewport, and the same task/content where possible. Show the actual interfaces side by side or as aligned paired frames; a prose change log alone is insufficient. For interaction changes, compare the relevant transition/state sequence. Label necessary differences so a changed dataset, zoom level or scenario cannot masquerade as a design improvement.

Accompany the comparison with a compact change record:

| Finding / screen | Before → after | What moved, merged, disappeared or changed | Why it helps the user | Evidence / remaining limits |
| --- | --- | --- | --- | --- |

Inspect the comparison with designer annotations set aside: does the interface now express the recommendation, and does its action still lead to the intended outcome? If the main interface is essentially unchanged, do not report a structural redesign. Repair the missing translation within scope, or explicitly classify the result as a contract/documentation clarification and retain the interface work as unresolved. Documentation-only changes do not close an accepted interface finding. Removed controls must either be unnecessary or remain discoverable in their new location; hiding required work is not simplification.

Meaningful does not mean large or novel. A small visible copy or state change can resolve a real issue. Preserve sound designs, explain deliberate non-changes, and do not move controls merely to manufacture a dramatic comparison. Critique-only work specifies the proposed interface delta without claiming it was applied; behavior that a static artifact cannot establish remains unverified.

## Deliver or revise

- Critique-only: report prioritized findings, conflict resolutions, preserved decisions and next actions. Do not edit the product.
- Revision requested: preserve prior artifacts, use a new version in the established project location, and implement the accepted decisions in the requested format. Do not replace an SVG request with an interactive application. Use applicable authoring skills only when their scope fits.
- Keep alternate states visibly separate from the main screen. Distinguish designer annotations from product copy.
- Reinspect the revised artifact. Check the changed flows/states and relevant visual boundaries. Report exactly what was verified and what remains proposed or untested.
- For revised artifacts, show what changed and why with artifact links, the required rendered before/after comparison, and its compact change record. Include the key outside-in decisions and inside-out traces/broken dependencies, proportionate to scope. Do not bury unresolved behavioral decisions in documentation while the visible interface contradicts them.
- Record peer updates only when requested or required by project workflow; writing a ledger does not authorize sending messages.

No fixed brand aesthetics, universal step-count target, mandatory wizard, or automatic header/footer on every container is implied by this skill.
