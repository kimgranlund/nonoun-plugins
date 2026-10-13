Goal: ship CSV export for the invoices page by running `docs/plans/export-csv.md` to completion.
Rules: no push without asking the user first. Every commit stays under 200 changed lines.
Decisions: user 2026-10-12, the delimiter is a comma (US Excel readers). Agent 2026-10-12, dates are UTC ISO 8601 (the API returns UTC). User 2026-10-12, the streaming writer is out of scope (files are small).
State: branch `feat/export-csv`, 2 dirty files. Steps 1 to 3 are verified, step 4 is built and not verified, step 5 is not started. The steps and criteria are in `docs/plans/export-csv.md`.
Open: whether the export includes voided invoices waits on the user asking finance.
Next: verify step 4 (`export/view.py`).
