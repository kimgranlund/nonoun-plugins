# Task-led review

Start with representative tasks and observed friction, not an aggregate maturity
score. Use the smallest relevant slice of the corpus. Trace one successful route,
one failure and one boundary case when evidence permits. If only files are
available, call the route proposed and runtime behavior unknown.

For each relevant responsibility record one state:
- Supported: cited structural or observed evidence supports this specific claim.
- Gap: an applicable requirement is contradicted by evidence.
- Unknown: evidence is insufficient; name the smallest missing record.
- Not applicable: explain why the task does not need this responsibility.

Do not sum these into maturity, quality or efficiency. Separate structural checks
from demonstrated retrieval performance. More metadata is not necessarily better.

| Responsibility | Question | Evidence to seek |
|---|---|---|
| Entry and navigation (T0-T1) | Can this task reach the right starting point? | Actual invocation, local entry, next-hop links |
| Scope (T2) | Are applicable constraints found before action? | Scope declaration, precedence, delivery sequence |
| Description and discovery (T3-T4) | Is identification cheap and unambiguous? | Stable IDs, relevant summaries, query results; a simple index may suffice |
| Depth and intent (T5-T6) | Does expansion address a missing requirement? | Intent, selected route, depth reason and irrelevant reads |
| Procedure (T7) | Can the task finish and know when to stop? | Required context, stop conditions, acceptance checks |
| Assembly (T8) | What actually reached the model? | Returned bytes versus explicit request assembly |
| Working set (T9) | Is temporary state kept out of durable truth? | Task artifacts and reviewed promotion process |
| Integrity (T10) | Are targets reachable and current? | Link/hash checks; independent semantic review |
| Governance (T11) | Can disagreement and change be resolved? | Authority scope, source owner, supersession, migration |

Follow the [working procedure](../SKILL.md#working-procedure), using the
[practical evaluation criteria](evaluation.md#practical-evaluation-criteria) for
affected boundaries. Check both missing context and unnecessary machinery: repeated
rules, parallel inventories, alternate parsers/resolvers and tests that reproduce
the implementation’s assumptions. Prefer a shared cause and bounded repair over
another local exception.

Use [gap analysis](../templates/gap-analysis.md). Never infer a missing capability
solely because a particular filename or tier-specific artifact is absent.
