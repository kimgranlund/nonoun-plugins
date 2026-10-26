# Intent and evaluation contract

A useful brief establishes what matters while leaving design choices open. Use prose, tables or the optional scaffold. This is a reasoning aid, not an additional required JSON schema or a mandatory workshop.

## Connect intent and means

Apply [bidirectional reasoning](bidirectional-reasoning.md) at the level relevant to the decision. Describe the outcome sought, the means that could support it, and any consequential mismatch, dependency or tradeoff. Available means may include content, evidence, capabilities, people or external systems. Neither user intent nor organizational intent maps exclusively to one direction. Record only the conclusions useful for evaluating the proposal; a traceability matrix is optional.

## Describe the problem

| Field | Questions to answer |
| --- | --- |
| User intent | What is the person trying to accomplish? What uncertainty or obstacle prevents it? |
| Desired outcome | What should become true for the person and organization? What does a useful completion look like? |
| Context | Who is acting, from which entry point, with what knowledge, frequency, urgency and environment? |
| Object or subject | What is being understood, compared, created, changed or monitored? What is its lifecycle? |
| Content responsibilities | What must be explained, demonstrated, compared, requested, confirmed or preserved? What evidence is available? |
| Primary decision/action | What decision or action moves the person toward the outcome? What legitimate alternative is available? |
| Entry and exit | What brings the person here? Where can success, deferral, rejection and recovery lead? |
| Constraints | Which requirements are supplied or verified? Which apparent constraints are assumptions? |
| Open questions | Which unanswered questions could materially change the approach? Which can be explored through alternatives? |

Separate user intent from the organization's preferred action. A visitor deciding the product is unsuitable can be a successful experience. An administrator declining an unsafe change can be successful completion. Do not turn every surface into a conversion funnel.

Content responsibilities describe meaning, not a prescribed section list. “Demonstrate fit with credible evidence” leaves room for an example, comparison, trial or case narrative. It does not require a testimonial carousel. Never invent customer quotes, performance claims, prices, data or permissions to satisfy a template.

## Define success without inventing evidence

For a KPI candidate, specify as much as the available evidence supports:

- Construct: the outcome the measure approximates and why it is relevant.
- Definition: numerator/denominator for rates, or start/stop events and aggregation for duration/count measures.
- Eligible population and exclusions: user segment, role, new/returning use, bots, staff and abandoned/ineligible attempts where relevant.
- Measurement window: one task, session, cohort or period. Mark unknown rather than inventing it.
- Collection method: usability observation, task assessment, interview, telemetry, operational data or another appropriate source. Mark proposed instrumentation as proposed.
- Baseline and target: supplied values and sources, or unknown. Do not manufacture benchmark percentages.
- Interpretation limits: confounders, data quality, accessibility differences and proxy failure.
- Guardrail: an outcome that must not worsen as the primary measure improves.

A goal is the desired result. A KPI is one possible indicator. Intent is the person's purpose. Do not collapse these into a single “increase engagement” statement. Choose a small set of measures that would discriminate the hypotheses, rather than attaching every candidate KPI to every page.

Example: “qualified next-step rate” could mean eligible visitors who complete the agreed next step divided by eligible exposed visitors during the agreed window. Qualification and eligibility must be defined with the project; clicks alone do not establish fit. Pair the measure with expectation accuracy or poor-fit activation, and consider privacy before proposing tracking.

For early wireframes, use observable questions: can participants find the next step, correctly explain consequences, distinguish alternatives, recover an interrupted task, or recognize missing data? Do not claim production business impact from these checks. Faster completion is not always better for consequential decisions; time-on-page is ambiguous for both reading and confusion.

## Preserve room for alternatives

A/B/C test competing approaches to the same user task. Keep the user goal, required capabilities, content facts and operational constraints consistent. Share tokens and component conventions; choose composition separately for each hypothesis.

Before markup, briefly describe each proposal's organizing principle, primary interaction or decision sequence, and main tradeoff. Each pair should differ on at least two structural dimensions: information architecture, interaction model, disclosure strategy, comparison method, or allocation of screen space. At least one difference must change how the user understands or completes the task. For a narrowly constrained component where two dimensions are not meaningful, state that constraint and identify the consequential alternative rather than inventing unnecessary complexity.

Reordering identical sections, changing columns, or adjusting color, typography and spacing does not by itself constitute another proposal. Do not obtain B/C only by rearranging A's markup. Implement the states and transitions needed to experience the proposed difference; a rationale cannot substitute for behavior.

State when each approach is preferable and what becomes harder. If two proposals have essentially the same explanation, revise one before building. Preserve compatibility with surrounding flows. Safety, truthful content, accessibility and necessary recovery are shared requirements, not optional differentiators.

Before delivery, compare A/B, A/C and B/C against the brief. Identify the actual structural differences and exercise their task paths. Evaluate task fitness separately from contrast: a different proposal that drops capabilities or adds unjustified steps is not a successful alternative.

## Label authority

- **Requirement:** explicit user instruction or verified project/platform constraint. Record the source.
- **Heuristic:** reasoned default with conditions and counterexamples. It can be rejected with an explanation.
- **Example:** one possible realization, not a prescribed pattern.
- **Assumption:** an unverified premise; identify impact and how to resolve it.
- **Evidence:** supplied or researched material supporting a specific claim, with its limits.

Ask only about uncertainty that blocks consequential work. For reversible design choices, proceed with stated assumptions and use proposals to expose the decision. Keep acceptance criteria focused on observable user outcomes and actual constraints, not fidelity to an example layout.
