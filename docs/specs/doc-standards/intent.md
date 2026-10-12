# Intent documents

Goals, KPIs, PRDs, specs, and epics: what a project means to achieve and how it knows. [Core rules](core.md) apply to all of them.

| Type | Shape | Machine-checked |
|---|---|---|
| Goals | OKR: one objective and 2 to 4 measurable key results. Each key result names a KPI by ID (`K-NNN`). STE rules for the sentences. | docs_check G-1 to G-5 |
| KPI / metric definitions | Data first: front matter per [kpi.json](../../assets/schemas/kpi.json), the dbt semantic layer and MetricFlow style. Prose only for rationale. One sense per term, from [the glossary](../../references/glossary.md). | docs_check G-1 to G-5, S-1 |
| PRD | Plain Language narrative: problem, users, non-goals. Then the requirements section in EARS or user stories with acceptance criteria. Metrics by KPI ID. | none |
| Spec / requirements (SPEC, SRS) | Every requirement in an EARS template, with a stable ID (`REQ-NNN`) and an acceptance criterion in Gherkin. The INCOSE rules for quality. | docs_check S-2 with `doc-type: requirements` |
| Epic / parent issue | Objective in OKR shape. Child issues listed by ID, in dependency order. No implementation detail; that belongs in the children. | none |

## Rules

1. A goal states a verifiable end state. "Better" or "faster" with no KPI is not a goal.
2. A KPI has a command that produces its value (`measure:`), a unit, a direction, and a target. A threshold nobody can run is not a KPI.
3. Keep the problem and the solution in separate sections of a PRD. A model reads framing in a requirements section as a requirement.
4. One requirement per ID. A requirement with two `shall` clauses is two requirements.
5. An acceptance criterion is checkable by a command, a test, or a yes or no question. Write it in Gherkin:

```gherkin
Scenario: <name>
  Given <precondition>
  When <action>
  Then <observable result>
```

In this repository, goals live in `docs/goals/` and KPIs in `docs/kpi/`; the design is `docs/specs/repo-onboarding/goals-and-kpi.md`.
