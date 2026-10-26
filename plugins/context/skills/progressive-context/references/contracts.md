# Capability contract

Use an existing README or spec when it already owns this information. A new capability can start with only identity, intent, and unknowns. Extend it as facts become available.

```markdown
# Invoice review
ID: billing/invoice-review

## Intent
Help an operator identify overdue invoices and choose a supported next action.

## Terms and boundaries
Overdue means unpaid after the due date in the account timezone.
Sending reminders is outside this capability's current scope.

## Contract
Inputs: invoices and account timezone.
Outputs: filtered list and selected invoice ID.
Dependencies: invoice schema v2; selection callback.
Constraints: read-only; no network mutation.

## Acceptance criteria
- Boundary dates use the account timezone.
- An empty result explains why no rows appear.
- Selecting a row emits that row's ID.

## Implementation and evidence
Implementation: [view](./src/review.ts).
Assessment: none yet; this is an intent-only draft.

## Open questions
How should disputed invoices appear?
```

The example paths are illustrative; create links only to actual files. Stable IDs should survive moves; the path is a locator, not identity. Keep one authoritative location for each fact. Use relative links within a repository, stable record IDs in a web harness, and explicit version constraints across package boundaries.

An AGENTS.md entry might say: “For invoice review changes, read `contract.md`; for date evaluation read `checks/date-cases.md`.” It should not repeat the full contract, task history, or all evaluation results.

A domain profile is a small optional vocabulary and criterion guide, not a second core ontology. UI might need interaction and accessibility terms; research needs claims, sources, and uncertainty; a process needs roles, inputs, and exit conditions. Start from the project's own language.
