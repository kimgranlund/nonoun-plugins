# Role records

Detail for the handoff-format skill's `## Layout` section: what a role run writes in the records dir.

`prepare` also writes `<role>-<level>.attempt.json` and `<role>-<level>.dispatch.json` (the brief and paths the spawn gate matches), and `record` writes the header line, validates the result, and appends the `runs.jsonl` line with `transport: subagent`. A rerun of the same role and level writes `<role>-<level>-<k>.md` (k = 2, 3, ...); the first result is never overwritten, and the newest is decided by `scripts/order.py`: latest runs.jsonl record (both writers record `file`), else level then rerun index then name; never mtime. runs.jsonl keeps the history.
