# Experience reasoning lenses

Use a shared core with locally selected lenses. SaaS is a product context, native is a delivery environment, and dashboard is a surface. A native SaaS application can combine analytical, editing and agent-supervision work. Avoid multiplying project categories or imposing a website story on every task.

The [registry](patterns/registry.json) exposes this guidance as `experienceReasoning`. These are revisitable prompts, not mandatory questionnaires or a prescribed design algorithm. Read only what changes the current decision. Reconcile user progress and system capabilities through [bidirectional reasoning](bidirectional-reasoning.md).

## Shared core

- **Progress and context:** What progress does the person need to make, and under what operating conditions?
- **Credible support:** What can the system support, with what constraints, evidence and authority?
- **Responsibilities:** What information, decisions and actions connect desired progress to available means?
- **Structure:** How should those responsibilities become flows, surfaces and components?
- **Emphasis:** What deserves prominence, detail, density or progressive disclosure?
- **Continuity:** How will people navigate, interrupt, resume, recover and understand the result?
- **Evaluation:** What observations would demonstrate useful outcomes, and what guardrails prevent misleading success?

## Select lenses locally

### Narrative and readiness

A person needs to understand relevance, assess evidence and choose a next step. Organize around story and increasing readiness.

- What must be understood or trusted before progression?
- Where does a change in representation advance meaning or renew attention?
- What commitment is justified at this point?

Candidate measures: Comprehension, Qualified progression, Expectation accuracy. Guardrails: Poor-fit progression, Unsupported claims, Pressure without new grounds for action. Read [Narrative and readiness](narrative-reasoning.md).

### Native context and continuity

Device capabilities and interruptible sessions materially shape a task, on mobile or desktop. Organize around contextual journeys and continuity.

- What should happen quickly, and what requires sustained attention?
- How do permissions, input modality, offline use and device capabilities change the task?
- What survives interruption, switching devices or returning later?

Candidate measures: Correct task completion, Successful re-entry, Recovery effort, Permission understanding. Guardrails: Lost work, Unexpected permission consequences, Inaccessible input paths. Read [Native context and continuity](profiles/mobile.md).

### Product work and SaaS lifecycle

People create, manage, collaborate on or administer persistent objects. Organize around work, objects and lifecycle.

- Which objects, relationships and states organize the work?
- How do roles, dependencies, concurrency and repeat use affect completion?
- What establishes readiness, supports orientation and separates personal preferences from workspace policy?

Candidate measures: Valid completion, Repeat-use efficiency, Rework, Successful handoffs. Guardrails: Wrong-scope changes, Permission errors, Coordination failures, Speed at the expense of quality. Read [Product work and SaaS lifecycle](profiles/product.md).

### Analysis and intervention

People interpret signals, investigate causes and decide whether to act. Organize around questions, signals and decisions.

- Which question or exception deserves attention?
- What baseline, denominator, time range or comparison gives a signal meaning?
- How can someone move from overview to evidence, investigation and action?

Candidate measures: Interpretation accuracy, Detection time, Decision quality, Action follow-through. Guardrails: False alarms, Missed signals, Stale or misleading comparisons. Read [Analysis and intervention](profiles/dashboard.md).

### Delegation and supervision

Agents propose or execute work while people supply objectives, direction, choices or authority. Organize around delegation with inspectable boundaries.

- What may be delegated, under which scope, budget and stop conditions?
- When should a person direct, choose, approve or intervene?
- What evidence, uncertainty, changes and results make supervision meaningful?

Candidate measures: Successful outcomes, Appropriate intervention, Correction effort, Authority compliance. Guardrails: Unauthorized actions, Missed escalation, Automation surprise, Uncalibrated confidence. Read [Delegation and supervision](profiles/agentic.md).

## Units of responsibility

A unit may establish access, readiness or orientation; prioritize work; edit an object; answer an analytical question; authorize a proposed action; or set durable behavior. Choose boundaries around a coherent responsibility, not a fixed screen size or a universal list of application sections.

- What responsibility does this unit fulfill within the experience?
- What information, evidence and actions are required?
- Which representation fits their relationship and consequences?
- What prominence, density, depth and interaction does the task justify?
- Which entry, working, completion, interruption and recovery states matter?
- How does this unit connect to adjacent work and preserve continuity?
- What observable result would indicate successful resolution?

Scale has independent dimensions: space, emphasis, information density, effort, disclosure depth and interaction demand. Preserve full-width section wrappers; choose internal divisions and text measure intentionally. Repeated tasks generally need stable object and action placement. Vary representation where responsibility changes, rather than rotating templates for novelty.

## Time, state and coherent alternatives

For consequential flows, establish enough context to review the proposal: entry and prerequisites, current object/state, available actions and authority, resulting state, persistence, completion, and relevant interruption or recovery. Include loading, empty, failure, conflict or stale-data conditions when they change the design. Do not generate every theoretical state.

A/B/C may compare workflow hypotheses: a guided sequence, a contextual workspace and a task queue can offer different ways to achieve the same outcome. Keep facts, scope and permissions comparable. State how each changes effort, visibility, dependency handling and recovery. Cosmetic screen rearrangements do not resolve those questions.

Use stable state-specific page IDs in the existing manifest, with transitions and compatibility explained in the companion brief. Group tightly coupled decisions into coherent alternatives. Where mixed choices could create an impossible journey, either choose a boundary that avoids such mixing or implement explicit validation before promising it. The current shell does not enforce flow compatibility or simulate application state machines.

## Capture useful review evidence

Show the relevant role, state, task and prototype boundary in concise intent/context text. Invite feedback about missing support, incorrect transitions, uncertain consequences and recovery as well as preferences. Existing element, page and decision notes preserve that feedback without a compulsory taxonomy or new schema fields.

A design selection is not an operational approval. Distinguish what reviewers can inspect in a static artifact from behavior that needs a functional prototype: permissions, persistence, concurrency, offline behavior, authentic device affordances and agent execution. Record concise conclusions, not private reasoning transcripts.

Define selected measures by population, task, observation window and collection method. Keep unknown baselines unknown. Preference, click counts and time spent are insufficient evidence of task success or business impact by themselves.
