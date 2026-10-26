# Capability briefs

Apply only capabilities relevant to the task. They cross project categories and do not imply additional required pages. Each section offers intent, content responsibilities, KPI candidates, guardrails and open design questions. Define measurement details through the [intent contract](intent-contract.md).

Contents: [Commerce](#commerce-and-transactions), [Search](#search-and-discovery), [Support](#service-and-support), [Operations](#operational-and-administrative-systems), [Collaboration](#collaboration-and-community), [Learning](#learning-and-guidance), [AI](#ai-assisted-experiences), [Lifecycle](#lifecycle-and-re-entry).

## Commerce and transactions

**Intent:** Evaluate an exchange, understand the commitment, complete it accurately, and manage its consequences. Includes purchases, subscriptions, bookings, renewals and refunds.

**Content responsibilities:** Establish suitability, availability, total cost, entitlements, prerequisites, timing and relevant policies. Explain what is committed at each step, who receives confirmation and how to change or recover. Distinguish pending from completed transactions and provide enough reference information to resolve problems.

**KPI candidates:** Eligible transaction completion, correct plan/item selection, payment recovery, successful changes or cancellations. Define whether completion means intent, authorization, settlement or fulfilment.

**Guardrails:** Unexpected charges, unsuitable purchases, duplicate orders, involuntary renewal, support demand and obstructed cancellation. Abandonment can indicate informed non-fit.

**Decision space:** Guided evaluation versus direct purchase; progressive details versus one reviewable summary; account-first versus appropriately deferred identity. Explore what risk or uncertainty each approach resolves rather than assuming fewer fields always wins.

**Conditions:** Unavailable inventory, changed price, failed payment, interrupted checkout, pending confirmation, partial fulfilment, renewal and reversal. Real payment or legal-policy behavior needs verified requirements and implementation beyond the static shell.

## Search and discovery

**Intent:** Find, compare and recognize a relevant object or answer, whether the person knows its name or only a need.

**Content responsibilities:** Supply understandable result labels, useful distinguishing attributes, scope, filters, ordering rationale and context for no/partial matches. Preserve query and comparison context through detail views. Explain personalization or generated answers when that affects trust.

**KPI candidates:** Relevant-result success, answer success, time to useful result, successful refinement and zero-result recovery. Define “useful” by the task; a click can be a mistaken result.

**Guardrails:** Missed relevant results, false confidence, bias toward popular items, excessive refinement and exposure of restricted content.

**Decision space:** Query-first, faceted exploration, guided narrowing or relationship-based browsing. Combine paths when audiences enter with different knowledge. A conversational entry needs a reason beyond novelty and a route to inspect its evidence.

**Conditions:** Ambiguous queries, misspellings, no matches, too many matches, unavailable results, permission filtering, stale indexes and multilingual content.

## Service and support

**Intent:** Resolve a problem, understand progress and reach an appropriate human or system when self-service is insufficient.

**Content responsibilities:** Identify the issue without requiring internal vocabulary, explain actionable steps and consequences, retain relevant context across escalation, and clarify ownership and expected next contact. Do not make unsupported resolution-time promises.

**KPI candidates:** Verified resolution, repeat contact for the same issue, successful escalation, effort and satisfaction. Define a resolution window and avoid counting disappearance as success.

**Guardrails:** Incorrect advice, forced self-service, hidden contact routes, repeated explanation, unresolved silence and sensitive-data overcollection.

**Decision space:** Symptom-led triage, knowledge retrieval or case-first support. Compare how each handles uncertainty, urgency and continuity rather than treating contact deflection as the universal goal.

**Conditions:** Unknown issue, failed suggested fix, outage, duplicate case, escalation, asynchronous reply and reopened problem.

## Operational and administrative systems

**Intent:** Process work accurately, govern access and configuration, and handle exceptions with clear scope and accountability.

**Content responsibilities:** Show queue priorities, eligibility, assignment, affected objects, permission boundaries and consequences. Make inherited settings and bulk-selection scope explicit. Provide verification, recovery and audit context proportional to the action.

**KPI candidates:** Correct completion, throughput by eligible work type, exception age, rework, correction effort and recovery time. Account for case complexity before interpreting speed.

**Guardrails:** Unintended access, wrong-scope changes, unsafe bulk actions, lost work, unreviewed exceptions and unfair individual productivity comparisons.

**Decision space:** Queue-first processing, object-first administration or guided consequential changes. Compare efficiency for experienced operators with comprehension for infrequent administrators. Do not solve every uncertainty by inserting a confirmation dialog.

**Conditions:** Mixed eligibility, partial bulk success, concurrent change, locked records, insufficient permissions, expired approval, rollback and audit review.

## Collaboration and community

**Intent:** Coordinate work or contributions, form shared understanding, and sustain useful participation with appropriate boundaries.

**Content responsibilities:** Establish audience, ownership, visibility, attribution, next responsibility and notification scope. Separate comments, decisions and durable outcomes. For communities, explain contribution expectations, reporting and moderation outcomes without exposing restricted details.

**KPI candidates:** Successful handoffs, resolved work, response to actionable requests, contribution usefulness and conflict resolution. Define quality through the community or task; raw message volume is not collaboration success.

**Guardrails:** Notification overload, harassment, visibility mistakes, unresolved responsibility, duplicated work and suppression of legitimate contributions.

**Decision space:** Object-centered discussion, task-centered handoffs or conversation-centered coordination. Compare persistence, discoverability and how decisions become authoritative. A feed may surface activity while making responsibility difficult to locate.

**Conditions:** Concurrent edits, stale comments, external guests, role changes, muted notifications, reported content, disputed decisions and departed owners.

## Learning and guidance

**Intent:** Develop understanding and the ability to perform a task independently, with support matched to existing knowledge.

**Content responsibilities:** Establish prerequisites, learning outcome, meaningful sequence and practice opportunities. Explain errors and provide feedback that supports correction. Allow relevant skipping or revisiting without implying that exposure proves mastery.

**KPI candidates:** Demonstrated task competence, knowledge retention, successful transfer to a new case, time to competence and assistance required. Define how competence is assessed.

**Guardrails:** Superficial completion, inappropriate difficulty, inaccessible instruction, dependence on hints and misleading progress claims.

**Decision space:** Guided progression, task-embedded coaching or reference-led self-direction. Compare support for novices and returning users. Avoid mandatory tours whose steps do not correspond to a useful first task.

**Conditions:** Prior expertise, prerequisite gaps, incorrect attempts, interrupted learning, forgetting, alternative formats and assessment recovery.

## AI-assisted experiences

**Intent:** Delegate useful work while retaining appropriate understanding, control and ability to inspect or correct uncertain results.

**Content responsibilities:** Explain the task scope, inputs, context available, expected output, relevant limitations and what actions require explicit approval. Distinguish generated suggestions, retrieved evidence and executed changes. Show sources or provenance when they help assess the result; do not fabricate precision or imply certainty through confident styling.

**KPI candidates:** Useful-result acceptance after review, task completion quality, correction effort, recovery success and appropriate reliance. Define acceptance criteria beyond clicking Accept; account for hidden downstream errors.

**Guardrails:** Unnoticed mistakes, unsupported claims, unintended execution, sensitive-context exposure, overreliance and excessive review burden.

**Decision space:** Inline assistance, a dedicated conversational workspace, or bounded delegation with review checkpoints. Choose according to task ambiguity, reversibility and evidence needs. Conversation is not mandatory for AI, and autonomy should not expand merely because the UI supports it.

**Conditions:** Missing context, uncertain/contradictory results, partial execution, interruption, cancellation, refusal, stale sources, retry and version comparison. Prototype simulated responses must be clearly identified. Actual model behavior and tool authorization require separate implementation and evaluation.

For synthetic examples of bounded delegation, see [the agent-first scenario suite](demo-suite.md#agent-first-examples): research judgment, operational recovery and creative direction. These explore different relationships between intent, evidence, authority and outcomes. Use only the mechanisms that clarify the human's next decision; a conversation transcript or confidence badge is not inherently useful.

## Lifecycle and re-entry

**Intent:** Start with understanding, reach useful value, return with continuity, adapt to changed needs, and leave or reverse a commitment without unnecessary obstruction.

**Content responsibilities:** Explain first-use prerequisites, preserve meaningful progress, show relevant changes since last use, and make identity/account transitions understandable. Communicate upgrade implications and data consequences of downgrading, cancellation or deletion with verified facts.

**KPI candidates:** Meaningful activation, successful resumption, retained useful outcomes, recovery of interrupted work and successful plan/account changes. Define cohorts and elapsed windows; mere return visits are not retained value.

**Guardrails:** Repetitive onboarding, coerced upgrades, abandoned work, surprise loss, inaccessible exit and manipulative urgency.

**Decision space:** Immediate useful task, staged setup or guided orientation; contextual re-entry versus a universal home; self-service transitions versus justified assisted changes. Consider how prerequisites and task frequency alter the tradeoffs.

**Conditions:** Returning after a long absence, changed entitlement, expired session, invitation, account switching, trial expiry, reactivation and departure.
