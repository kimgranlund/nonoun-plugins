# Assessment and reuse

A compact Markdown assessment is enough. Record:

- Subject ID and exact implementation revision or content digest.
- Contract/criteria revision and dependency versions that affect the claims.
- Relevant environment, evaluator, and time.
- Each criterion, check actually run, observed result, and evidence link.
- Failures, missing checks, limitations, and the accepted use scope.

A base commit alone does not identify a dirty working tree. Commit the checked material when appropriate, or capture a content digest/snapshot including relevant untracked files and changes. Never mark evidence current if the material cannot be identified. Link existing verification or evaluation records when they contain the needed facts; add only missing qualification information.

Use “not assessed” for missing evidence, “failed” for a demonstrated violation, and “stale” when relevant checked inputs changed. Changes invalidate affected claims, not every unrelated claim in the project. A proposed test is not an assessment. Schema validation establishes structural validity only.

For a new or changed checker, demonstrate acceptance of a known-valid case and rejection of an intentional defect for the expected reason before using its verdict to qualify a capability. Confirm the defect reaches the material exercised. Reuse that qualification for an unchanged checker within its tested scope. If the checker was wrong, retain the original verdict and link a corrected assessment of affected results; do not report reanalysis as an implementation improvement.

Trace change impact through existing contract and dependency links. For example, a changed shared date parser affects an invoice view's boundary-date claim and dependent consumers of that behavior; rerun those checks. Unchanged row-selection evidence can remain current if its inputs and behavior do not depend on the parser. Record uncertain impact as needing assessment rather than assuming independence; no separate dependency registry is required.

Useful lifecycle views:

| Available facts | Description |
|---|---|
| Goal only | Intended |
| Contract and criteria | Specified |
| Implementation exists | Implemented, not necessarily accepted |
| Current evidence satisfies named criteria | Accepted for that scope |
| Bounded public contract and independent reuse demonstrated | Qualified for the tested reuse scope |

These are descriptive views, not mandatory stored states or a strictly linear process.

Before claiming reuse, exercise the public interface from a separate consumer context with only the advertised dependencies and context. Record what it needed, what failed, and what remains platform-specific. Portable is always qualified: across which hosts, environments, versions, and uses?

A release pointer is optional. If used, point to an immutable revision plus the applicable assessment; avoid copying mutable “passed” flags into a catalog. One-off deliverables can be complete without being released.
