# Progressive Context skill specification

Status: proposed, v0.3. Recorded: 2026-09-27.

This document preserves the skill proposal developed in the ICM and generative-systems discussion. It specifies future behavior; it does not install a skill or claim that the required runtime exists. This specification is self-contained and is colocated with the earlier six-document proposal set.

## Purpose

Progressive Context designs and maintains systems that turn intent into evaluated, reusable capabilities. It applies ICM's scoped navigation and inspectable context to persistent constructs that can be composed, assessed, published, and revised.

The central loop is:

> Discover capabilities → specify a construct → compose → evaluate → qualify for reuse → maintain as dependencies and intentions change.

A construct represents a persistent identity. A revision is an immutable snapshot of its definition and realization. An instance is one running use of a revision with its own inputs and state. Publication qualifies a specific revision for a bounded set of uses; it does not declare a construct universally complete.

## General-purpose architecture

The core model applies to different project and artifact types. Generative UI is the first developed profile, not a restriction on what counts as a construct. Generality is a design intention that still requires validation outside UI projects.

| Layer | Responsibilities | Examples |
| --- | --- | --- |
| Universal core | Identity, intent, revisions, relationships, evidence, lifecycle, and context routing | Proposed capability, assessed revision, published contract |
| Domain profiles | Domain concepts, realization contracts, evaluation methods, and qualification policy | UI elements, research reports, learning modules, operational procedures |
| Environment adapters | Storage, retrieval, editing, execution, rendering, and inspection | Filesystem, browser database, A2UI runtime, document tools |

The UI profile owns `ElementSpec` and its meaning. The A2UI adapter translates supported UI realizations into runtime behavior. Filesystem `AGENTS.md` manifests are one representation of the logical records; other adapters expose equivalent data through APIs. None of these UI or filesystem choices is mandatory for the universal core.

### Profiles and proportional requirements

Each profile declares its construct types, domain definitions, realization formats, required information by maturity, evaluation methods, publication evidence, and the meaning of reuse. Pin the profile revision with assessments; changing qualification policy requires reassessment rather than silently changing the meaning of an old pass.

| Domain | Construct and realization | Example evidence | Meaning of reuse |
| --- | --- | --- | --- |
| Software | Authentication capability implemented in code | Functional and integration checks | Invoke or integrate through a supported interface |
| Research | Evidence synthesis realized as a report and sources | Coverage, accuracy, source review | Interpret or cite findings within their stated limits |
| Education | Learning module containing lessons and exercises | Assessment of learning outcomes | Deliver or adapt the module for supported learners |
| Operations | Onboarding procedure with templates and automation | Completion, exception, and timing observations | Execute the procedure in a supported setting |
| Design | Visual system containing tokens and components | Accessibility, consistency, usability review | Compose new artifacts using its contracts |
| Data | Transformation pipeline implemented in queries or processing steps | Correctness, data quality, reproducibility checks | Run against supported datasets |

Evaluation may use executable checks, human judgment, observed outcomes, or source verification. Profiles must distinguish what each method establishes and must not describe judgment as proof of a stronger claim.

Requirements scale with intended use, consequence, and breadth of distribution. A personal checklist may need little structure; a shared dependency needs more explicit contracts and evidence. Proportionality can reduce required work, but cannot turn missing evidence into a passing result or hide known limitations.

### Flexible lifecycle and endpoints

A construct may start with identity, intent, and unresolved questions. Additional fields become required as it makes stronger claims. The full contract is a destination for qualification, not an intake form that every idea must complete.

The lifecycle expresses evidence-backed maturity, not a mandatory linear workflow. Work may branch into alternatives, return to specification, abandon a candidate, or stop at an accepted deliverable. Publication and subsequent reuse are optional. Record abandonment, withdrawal, and retirement separately from historical maturity and preserve the reasons and prior evidence.

Maintain a new draft while an earlier revision remains accepted or published. Changes to goals create explicit intent revisions. More activity, more files, or a later timestamp never imply higher maturity.

Composable, portable, and reusable are separate scoped claims. Composability concerns compatible interfaces and assumptions; portability concerns supported environments and dependencies; reusability concerns successful use through a declared contract. A profile specifies evidence for each claim it makes.

### General publication rule

Publication requires evidence that an independent consumer can use the construct through its declared contract within the claimed scope. The profile defines the consumer, the use, the independence conditions, and the evidence threshold. Independence means the assessment does not depend on undocumented knowledge from the original creation process; it does not universally require an AI agent.

The UI profile operationalizes this with a fresh agent instantiating the unchanged realization on a second supported input scenario. A research profile may instead require an independent reader to trace and interpret findings correctly. Adaptation is recorded as a derived revision or construct and assessed for its own purpose.

## Relationship to ICM Architect

Jake Van Clief's current ICM Architect supports multiple workspace forms, recursive composition, explicit stage contracts, and cold-start navigation checks. Its system-map reference also distinguishes implemented, obsolete, and aspirational material, with verification status and change-impact guidance. These capabilities are upstream strengths, not new contributions of this proposal.

Sources reviewed in the session:

- [ICM Architect skill](https://github.com/RinDig/icm-architect/blob/main/SKILL.md).
- [System-map reference](https://github.com/RinDig/icm-architect/blob/main/references/system-map.md).
- [ICM paper by Van Clief and McDermott](https://arxiv.org/html/2603.16021v2).

These links follow moving branches. Before implementing a derivative, record the exact upstream revision and preserve applicable attribution and licensing. This proposal is an attributed extension for construct lifecycles, initially applied to A2UI reuse, not an assertion of general superiority.

## UI profile foundation: folder-native element ontology

Use the existing [Folder-Native Gen UI Ontology](../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md) as the element-contract foundation. Extend it with lifecycle semantics rather than introduce a competing component registry. This direction was agreed in the discussion; the extension remains a specification, not implemented behavior.

`ElementSpec` owns the UI element's props, behavioral states, slots, invariants, composition edges, and renderer claims. The lifecycle model owns maturity, revision identity, evidence applicability, and qualification for reuse. Progressive Context guides work across both contracts. Constructs that are not UI elements need their own realization contract and must not be forced into `ElementSpec`.

Preserve the ontology's machine-readable front matter and explanatory body, shared generation of schema and catalog, distinction between owned parts and shared composition, validated examples, story references, prop parity, structured errors, and bounded repair. Assess the corresponding code before calling any specified check implemented.

### Stage-dependent requirements

| Stage | Required information | Eligibility |
| --- | --- | --- |
| Proposed | Identity, intent, unresolved assumptions | Planning discovery only |
| Specified | Domain references, proposed interface, criteria | Planning and implementation work |
| Realized | Candidate implementation, dependencies, applicable element-contract checks | Preview and evaluation if runtime validation passes |
| Accepted | Applicable evidence for the declared purpose | Use within the accepted scope |
| Published | Public reuse contract, portability boundaries, independent reuse evidence | Default reusable-capability catalog |

An intent-only stub must not fail merely because it lacks an implementation or stories. It must also never masquerade as an instantiable renderer component. The proposed build classifies maturity before applying stage-specific requirements; full realization requirements still apply when an element claims implementation. An invalid realized node cannot evade checks by silently downgrading itself to a stub.

Generate a planning view that exposes unrealized capabilities and gaps, and a usable-capability view that exposes qualified revisions. The validator vocabulary for a run must agree with its allowed capabilities. Explicit preview runs may select realized candidates; ordinary published-component generation must not select them by accident.

### Manifest ownership and projections

Component `AGENTS.md` files are the filesystem entry points for authored contracts and references to realization and evidence. Large evidence bodies remain in their authoritative records. A browser representation preserves the same logical fields and reference semantics without requiring files.

Authored fields include identity, intent, contract, criteria references, dependency references, and declared applicability. Computed fields include assessment results, evidence freshness, and publication eligibility. If computed values appear in a manifest, generate or verify them against their sources; hand-editing them cannot qualify a component. Publication decisions remain separate recorded events naming an eligible revision.

The combined inputs support three projections: a discovery catalog, a validator schema, and a qualification view. Each projection records its source revisions. Shared generation detects defined classes of drift; it does not prove runtime behavior or eliminate all drift.

### Separate behavioral state, maturity, and version

The element's behavioral `states`, such as idle/loading/error, remain separate from lifecycle maturity. The element's compatibility `version` remains separate from an exact construct revision. Evidence identifies the exact revision and evaluation environment even when an implementation change does not require a compatibility-version bump.

### Integration rules to resolve during implementation

- Retrieval must include required cross-subtree contract dependencies, or reject their use explicitly. A strict subtree filter cannot silently omit a slot's external accepted element.
- Context-loading behavior belongs to the agent protocol or harness. Folder presence alone does not prove disclosure.
- Schema and prop-parity checks establish bounded structural claims. Rendering, actions, domain correctness, task completion, and independent reuse require their own evidence.
- Portability claims name supported targets and conditions and require actual renderer coverage. Target-agnostic instance syntax alone does not establish portability.
- Reconcile the ontology document's enforced-check claims with its deferred plan items against code. Report each as implemented, proposed, or unverified before migration.

## Activation and limits

Activate for requests to architect a construct system, adopt an existing project into it, compose from reusable capabilities, assess publication readiness, or analyze the effects of a changed contract or dependency.

Do not activate solely because a folder contains Markdown. For a one-off answer or a small task adequately served by a saved prompt, recommend the smaller structure. Ordinary UI implementation should use the project's existing UI authoring contracts; this skill adds lifecycle and context organization where the task requires them.

## Modes and outputs

| Mode | Typical request | Required output |
| --- | --- | --- |
| Architect | Design a generative system | Minimal construct model, context routes, lifecycle rules, and adapter decisions |
| Adopt | Organize an existing project | Source-backed inventory, ownership mappings, unresolved gaps, and proposed migration |
| Compose | Build from existing capabilities | Intent, pinned dependencies, realization, and evaluation criteria for a new revision |
| Qualify | Assess readiness for use or publication | Revision-specific findings, evidence applicability, and eligibility assessment |
| Maintain | Assess a changed requirement or dependency | Impact analysis, stale-evidence findings, and required reevaluation |

Adoption must preserve existing authoritative sources and working entry points. It should add references rather than duplicate specifications. Moves require a reference-impact review and must respect the user's existing authorization and the host's permission policy.

## Core procedure

1. Identify the requested outcome, current operation, domain profile, and supported execution environment. If no profile fits, define the smallest needed profile explicitly rather than impose UI assumptions.
2. Inspect existing sources and contracts; distinguish observations from assumptions.
3. Resolve the domain terms required to understand the outcome and evaluate it.
4. Discover candidate capabilities through summaries, then load selected contracts.
5. Select compatible revisions or identify a missing capability.
6. Create or revise the smallest sufficient construct.
7. Evaluate the exact realization against explicit criteria.
8. Record findings, evidence applicability, and the justified next state.

Questions are necessary when missing information changes meaning or scope. Routine structural choices can be made explicitly as proposed defaults. Never require every possible document before allowing exploratory work.

## Minimum construct contract

The full construct contract exposes identity, type, summary, intent, domain references, public interface, realization references, evaluation criteria, dependency relationships, and limitations. Stage-dependent profile requirements determine which fields must be present. An initial proposal can contain only identity, intent, and unresolved questions; absent contracts, criteria, and realizations remain explicitly unresolved rather than invented.

Evidence is stored separately and references the assessed revision, criteria version, dependency versions, method, environment, observations, and result. Status is derived from these records and transition decisions; editing a status field cannot establish eligibility.

Relationships distinguish live dependency, containment, and historical derivation. Runtime instances cannot silently mutate published definitions. New criteria or revised intentions must be recorded as changes in expectations rather than represented as improved performance under the old expectations.

## Progressive disclosure

| Operation | Initial resources | Deeper resources |
| --- | --- | --- |
| Discover | Purpose, capabilities, status, limitations | Manifest and public contract |
| Use | Contract, applicability, examples | Selected realization and dependencies |
| Modify | Intent, relevant semantics, target revision | Implementation and decisions |
| Evaluate | Criteria, target, methods, fixture references | Observations and relevant implementation |
| Diagnose | Findings and effective environment | Provenance and affected dependencies |

Material limitations must be visible during selection. Resource references must resolve exactly. Required constraints cannot be dropped silently to fit a context budget.

The filesystem adapter establishes explicit navigation rules. The web adapter retrieves records through APIs. Neither treats the existence of an instruction file as evidence that an agent has read it. The harness records loaded resource references and assembles fresh context at operation boundaries.

## Skill and harness responsibilities

| Skill guidance | Harness enforcement |
| --- | --- |
| Interpret intent and identify ambiguity | Resolve exact resource revisions |
| Select relevant contracts | Load mandatory context and log loaded references |
| Propose criteria and interpret findings | Execute checks and retain observations |
| Explain publication eligibility | Enforce transition guards |
| Propose revisions | Preserve history and reject stale-head writes |

A skill file alone cannot guarantee immutability, freshness, resource loading, or publication integrity. In a filesystem-only deployment without supporting checks, report these properties as procedural or unverified. Do not claim enforced behavior where only instructions exist.

## Proposed skill package

The following is a future package layout, not a list of existing repository paths.

<!-- doc-paths: off proposed package layout, not implemented files -->

```text
progressive-context/
  SKILL.md
  references/
    construct-model.md
    context-routing.md
    lifecycle-and-evidence.md
    adoption-and-impact.md
    qualification.md
  profiles/
    ui.md
  adapters/
    filesystem.md
    web-js.md
    a2ui.md
  templates/
    construct.md
    public-contract.md
    criterion.md
    assessment.md
  checks/
    references
    required-fields
    evidence-targets
    publication-eligibility
```

<!-- doc-paths: on -->

The entry skill contains triggers, mode selection, invariants, and reference routes. Load only the relevant mode, profile, and adapter. The initial package supplies the UI profile; add other profiles when actual projects need them rather than scaffold speculative domains. Templates are optional starting points, and check implementation details remain to be selected. Shared concepts have one authoritative definition rather than copies in every mode.

## A2UI adapter requirements

Distinguish implemented renderer components from reusable compositions. A generated composition may enter the construct library after qualification; naming a new component does not implement renderer support.

A reusable composition declares its input schema, bindings, supported actions, outputs, required catalog/runtime versions, dependency revisions, and loading/error behavior. Instantiation assigns isolated component IDs and state scopes and resolves registered handlers. Validate the exact representation against the selected adapter before rendering.

Evaluation covers schema validity, actual rendering, data and action integration, domain correctness, task completion, and reuse. A schema pass is not evidence for the other dimensions. Pin and inspect the project's actual A2UI dialect before implementing the adapter; no compatibility with a particular external runtime is assumed here.

## Qualification rules

Acceptance means a revision satisfies its stated purpose under documented conditions. Publication adds a promise that another consumer can use the revision through its public contract.

Publication requires all of the following:

- Explicit purpose, assumptions, interface, scope, and limitations.
- Resolvable realization and pinned dependencies.
- Applicable passing evidence for every required criterion, with no unresolved blocking findings.
- Independent-consumer evidence meeting the selected profile's publication policy. For the UI profile, this is a second supported input scenario in a fresh agent context, without editing the reused realization.
- Recorded profile, evaluator, and relevant environment versions and a reproducible use or inspection entry point.
- An authorized publication decision under the host's configured policy.

Changed realization, criteria, semantics, or dependencies trigger reassessment. Prior evidence remains historical evidence about its original target. Initially rerun the complete relevant suite rather than inventing selective freshness rules. A failing observation within the published scope suspends default reuse eligibility pending triage.

## UI profile worked example and acceptance tests

Compose an overdue-invoice workspace from an invoice table, customer summary, and local follow-up action panel. Define overdue status explicitly and use synthetic fixtures. Follow-up creates a local draft; it does not send a message.

The skill and harness together must demonstrate:

1. A fresh context can discover the workspace and find its public contract without reading the whole library.
2. The workspace shows exactly the eligible invoices and correct selected-customer details.
3. Local actions create the expected state, independently of displayed success text.
4. Evaluation names the exact artifact and criterion revisions.
5. Changing a dependency prevents stale evidence from qualifying the new candidate.
6. A second instance uses different supported data without shared-state errors.
7. A fresh agent instantiates the unchanged candidate using public resources alone.
8. A later grouping-by-customer adaptation becomes a separately evaluated revision or construct.

Negative controls must include a missing dependency, stale evidence, an unsupported renderer component, and an attempt to publish with a required unknown result. The system must report these accurately and reject ineligible publication.

## Claimed advantage and its test

Potential advantages are portability across storage environments, precise qualification, explicit evidence invalidation, and dependable A2UI composition. These are proposed benefits. Jake's simpler file-based approach may remain preferable for small, sequential, human-reviewed workflows with little reuse.

Compare ordinary artifact storage, ICM-inspired stage-scoped organization, and the construct model on equivalent creation-and-reuse tasks. Hold model, task requirements, components, and evaluation methods constant. Measure outcome success, correction effort, token use, setup cost, and maintenance cost. Require a fresh-context reuse task and report failed trials as well as successful ones.

An advantage is established only if improved reuse and quality justify the added curation and infrastructure. More metadata, more files, or a richer skill description are not success measures.

To validate general-purpose behavior, additionally exercise at least one non-UI profile. Confirm that an intent-only proposal is valid, an accepted deliverable can end without publication, non-executable evidence can support appropriately bounded claims, and independent use can be assessed without requiring an A2UI runtime or a fresh AI agent. These are future checks; the UI prototype alone does not establish cross-domain effectiveness.

## Implementation decisions still open

- Public plugin name decided: **Progressive Context**, package `progressive-context`.
- Exact domain-profile schema, composition rules when more than one profile applies, and the first non-UI validation project.
- Exact lifecycle field schema and its integration with the existing element ontology, including stage-aware validation and derived qualification views.
- Exact runtime/catalog adapter and executable check interfaces.
- Publication authority and acceptable evidence for different consequence levels.
- Thresholds and experiment size for a credible efficiency comparison.

Resolve these against the existing project before scaffolding a skill. This document authorizes no implementation by itself; it records the agreed direction for subsequent work.

## Agreed packaging direction

Ship as a sibling plugin to SDLC Lite in this repository. Keep installation independent: the capability plugin owns durable contracts, intent, context navigation, composition, and reuse assessments; SDLC Lite owns tickets, plans, execution attempts, verification, and work closure. Existing UI-authoring plugins continue to own UI implementation.

Integrate through references rather than duplicated records. Tickets identify affected capabilities and claims; assessments cite applicable verification records. The integration is optional, so non-development projects can use the capability plugin alone and ordinary development can continue using SDLC Lite alone.

The first release should contain one routed skill, a minimal capability contract, assessments that reference existing evidence, a filesystem adapter, optional SDLC integration guidance, and a UI profile referencing the existing ontology. Defer a general lifecycle engine, custom revision infrastructure, and browser adapters until a deployment needs them. Validate one existing component and ticket through contract, plan, verification, and assessment before expanding the architecture.


## Initial implementation boundary (2026-09-27)

The peer plugin now exists at `plugins/progressive-context`, with one shared authoring skill and contract, evidence, and integration references. It implements the minimal file-based authoring workflow; larger runtime requirements above remain proposals. The name is Progressive Context. No superiority over ICM Architect has been experimentally established.

Initial simplification: keep one capability contract, a linked assessment only after evaluation, and an optional release pointer. Derive lifecycle descriptions from these facts. Reuse existing Git revisions and SDLC artifacts. Do not require a registry, stage engine, custom revision service, or a complete domain ontology for an intent stub.
