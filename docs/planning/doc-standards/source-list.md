---
status: proposed
owner: maintainer
---
# Document standards: source list

Status: proposal, the maintainer's own list of the standard to use for each document type. It is the input of T-0447. `docs/specs/doc-standards/` is built from it; this file stays as the dated source.

- Goals: OKR structure (objective + 2 to 4 measurable key results) for shape; STE rules (not the dictionary) for the sentences. A goal an LLM can act on needs a verifiable end state, so each KR should reference a KPI by ID.
- KPI / metric definitions: Structured metric schema (name, quantity, unit, numerator/denominator, filters, window, source, target), stored as data, dbt semantic layer / MetricFlow style. Vocabulary: a project glossary with one sense per term. Prose only for rationale.
- Spec / requirements (SPEC, SRS): EARS sentence templates for every requirement, INCOSE rule set for quality, each requirement with a stable ID and an acceptance criterion in Gherkin. This is the most LLM-friendly standard available because every statement has a known grammar.
- PRD: Plain Language (ISO 24495) for the narrative (problem, users, non-goals), EARS or user-story-with-acceptance-criteria for the requirements section, metrics referenced by KPI ID. Keep problem and solution in separate sections so the model does not treat framing as requirements.
- HLD / architecture: C4 model for diagrams and component vocabulary, ADRs (Nygard format: context, decision, consequences) for each decision. Diagrams as code (Mermaid, Structurizr DSL) so the harness can read them.
- LLD: Interface contracts first: OpenAPI/AsyncAPI, JSON Schema, Protobuf, or typed signatures. Prose follows the DITA "reference" topic shape (purpose, inputs, outputs, errors, examples). Invariants and preconditions as explicit statements using EARS or Design-by-Contract phrasing.
- API docs: OpenAPI as source of truth; Microsoft or Google developer style guide for descriptions; one runnable example per endpoint.
- Runbooks / procedures: Full STE compliance here. Numbered steps, one action each, imperative, warnings before the step, expected result after. DITA "task" topic shape. This is the one place the whole dictionary pays off.
- Agent task / ticket / work order: A fixed schema (goal, context pointers, constraints, definition of done, out of scope, verification command). Definition of done in Gherkin or as an executable check. This is the highest-leverage document in an agent workflow and the one most often written as loose prose.
- System prompts / agent instructions: Plain Language rules, imperative mood, one rule per line, no hedging modals, explicit priority order for conflicting rules. Terminology from the glossary. Test-driven: each rule should have an eval case.
- Test plans / cases: Gherkin, or a typed test schema (id, precondition, action, expected, trace-to-requirement ID).
- Report / analysis: Pyramid Principle (answer first, then supporting structure), Plain Language for prose, every number traceable to a source or query. Claims, evidence, and inference marked separately so a model can weight them.
- Research notes / literature: Structured abstract (background, method, findings, limitations), claims tagged with evidence level, citations as resolvable IDs (DOI/URL). Open questions as an explicit list, not buried in text.
- Postmortem / incident: Blameless postmortem template (timeline, impact, root cause, contributing factors, action items with owners). Timeline as structured events with timestamps.
- Decision records: ADR. One decision per file, immutable once accepted, superseded rather than edited.
- Changelog / release notes: Keep a Changelog format with Conventional Commits categories; semantic versioning.
- Glossary / ontology: One term, one part of speech, one definition, with aliases marked as unapproved. This is STE's dictionary idea scoped to the domain, and every other document type above should link into it.
- Policies / guardrails: RFC 2119 keywords (MUST/SHOULD/MAY) with their defined meanings, one rule per statement, EARS for conditional rules.
- Bug report: Fixed template: environment, steps to reproduce (full STE, numbered, one action each), expected result, actual result, evidence (logs, screenshot, failing test), severity and impact on a defined scale. The reproduction steps are the only part a model must execute literally, so they get the strictest treatment. A bug without a repro should be labeled as such rather than filed as a bug.
- Feature request / enhancement: Problem statement in Plain Language, then a user story with acceptance criteria in Gherkin, linked to the PRD requirement ID if one exists. No proposed solution in the request body; put it in a comment or an ADR. A harness that gets "the user wants X done via Y" will build Y.
- Task / chore ticket: The agent-task schema from before: goal, context pointers, constraints, definition of done, out of scope, verification command. Definition of done must be checkable by a command or a test, not by judgment.
- Epic / parent issue: Objective in OKR shape, child issues listed with their IDs and the dependency order. The epic carries intent; it should not carry implementation detail that belongs in children.
- Issue titles: Conventional Commits-style prefix (bug:, feat:, chore:, spike:) plus a scope and an imperative summary under 72 characters. Titles are what a harness sees in a list, so they need to be searchable and typed.
- Spike / investigation: Question to answer, time box, what decision it feeds, and the required deliverable (usually an ADR or a short report). Closes with the finding, not with "done."
- PR title and body: Conventional Commits title. Body with a fixed structure: what changed, why (link to the issue), how to verify (commands and expected output), risks and rollback, and a checklist the author filled in. The "why" links rather than repeats. If the PR implements a requirement, cite its ID so traceability survives.
- Commit messages: Conventional Commits. Subject in the imperative, body explaining why, footer with issue references and breaking-change markers. Machine-parseable, which is the point.
- PR review comments: Conventional Comments (suggestion:, issue:, nitpick:, question:, with blocking/non-blocking decorations). The label tells the recipient what action the comment demands, which pays off most with an agent reviewer or reviewee.
- Issue / PR labels: A closed, documented vocabulary, one axis per label family (type, priority, status, area). Treat it as part of the glossary.
- Definition of done / acceptance checklist: Gherkin or a yes/no checklist where every item is verifiable. Keep it in the issue template so it exists before work starts.
- Release / milestone: Keep a Changelog aggregated from Conventional Commits, scoped to a version, with the issues closed listed by ID.
