# Knowledge and operations documents

Runbooks, test plans, reports, research notes, postmortems, policies, and the glossary: what a team knows and how it operates. [Core rules](core.md) apply to all of them. System prompts and agent instructions have their own card, [prompts.md](prompts.md), which is later and more specific than this one.

| Type | Shape | Machine-checked |
|---|---|---|
| Runbooks / procedures | Full STE, the one place the whole dictionary pays off. DITA task shape: numbered steps, one imperative action each, a warning before its step, the expected result after it. Template: [runbook.tmpl](../../assets/templates/runbook.tmpl). | docs_check S-4 with `doc-type: runbook` |
| Test plans / cases | Gherkin, or typed cases per [test-case.json](../../assets/schemas/test-case.json): id, precondition, action, expected, and the requirement IDs traced. | none |
| Report / analysis | Pyramid Principle: the answer first, then the supporting structure. Plain Language prose. Every number traces to a source or a query. Claims, evidence, and inference marked apart (`[V]` and `[U]`, [core rules](core.md)). | docs_check S-6 with `doc-type: report` |
| Research notes / literature | Structured abstract: background, method, findings, limitations. Claims tagged with their evidence level. Citations as resolvable IDs (DOI or URL). Open questions as an explicit list. | none |
| Postmortem / incident | Blameless template: [postmortem.tmpl](../../assets/templates/postmortem.tmpl). Timeline as timestamped events, then impact, root cause, contributing factors, and action items with owners. | none |
| Policies / guardrails | RFC 2119 keywords with their defined meanings, one rule per statement, EARS for a conditional rule. | docs_check S-5 with `doc-type: policy` |
| Glossary / ontology | One term, one part of speech, one definition, aliases marked unapproved. Every other document type links into it. This repo's: [glossary.md](../../references/glossary.md). | none |

## Rules

1. A runbook step has one action. Put a warning before the step it applies to, never after.
2. A test case traces to at least one requirement ID. A case that traces to nothing tests nothing anyone asked for.
3. A report states its answer in the first paragraph. Dated evidence goes in `docs/reports/`, named `YYYY-MM-DD-slug.md`. A release or a retro writes one; a single ticket does not, and its evidence is the `## Outcome` of its handoff.
4. A postmortem names systems and decisions, not people. Each action item has an owner and a ticket.
5. A glossary term has exactly one definition. A second sense is a second term.
