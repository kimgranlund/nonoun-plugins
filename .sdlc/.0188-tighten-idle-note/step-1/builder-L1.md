<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- docs/reports/messages-idle-host-limit-2026-10-01.md: replaced the "both address this limit" sentence with the handoff's text.

## Checks
- Criteria 1 and 2 (grep for the old phrase absent, new phrase present): passed.
- Criterion 3 (guard, no files changed outside the target): passed.

## Notes
- I grepped the file for "wait" and "address". Line 11 and line 15 say a parent waits on the messenger to keep its turn open. They do not claim `wait` wakes an idle host, so I left them unchanged.
