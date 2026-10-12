<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/docs/reports/2026-10-12-builder-overlay-retest.md`: new report, all 8 sections in the order the handoff gives. The three table rows are copied from `run-log.md` and the raw rows from `rows.jsonl`, both by script.

## Checks
- All nine criteria (seven `(red)`, two `(guard)`) were extracted from the handoff and run once. All nine exited 0.
- Criterion 1, the header and verdict lines: exit 0.
- Criterion 2, run-log rows against the report table: 3 rows against 3.
- Criterion 3, the `Spend:` line: 10.04 against 10.04, with the table sum also 10.04.
- Criterion 4, ticket spend: the report states 19.30 and the computed total is 19.30. This is under 20.
- Criterion 5, `## Not run` terms: no terms missing.
- Criterion 6, required terms, em dashes, trailing whitespace and links: all empty.
- Criterion 7, raw rows: 5 against 5.
- Criterion 8, scope guard: `[]`, no stray paths.
- Criterion 9, `python3 plugins/sdlc-lite/scripts/check.py`: ok, 19 role levels, 9 agents, 22 generated definitions.

## Notes
- The `redck.py record` call reported "retrospective: 14 source path(s) already differ from the base". The tree already held earlier work, so the checkpoint is stored as a base control, not a pre-edit red record. The seven `(red)` controls were red at that point because the report did not exist yet.
- I did no model spend and did not run a cell, `dispatch.py`, a preflight or `cell.py`.
- I did not touch `run-log.md`, the evidence folder or any other file.
- I used "Ticket spend: 19.30 USD" from the criterion 4 computation.
- The criterion commands are wrapped in backticks in the handoff. I stripped them before running.
