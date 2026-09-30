## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 6: Fanout reader
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/fanout.py`: `read(lanes_dir)` returns lanes-dir facts in both layouts (`scripts/fanout.py` documents them; the pre-T-0155 layout has no run-id prefixes, `gate-<lane>-<id>-<k>.log` names, and no fanout.log): `report` (the `| Lane | Ticket | Outcome | Commit |` rows of `report.md`, the `- Run:` id or None, the gate commands, the integration worktree path, the external lane branches), `fanout_log` entries (path, line number, run_id, lane, ticket, event) from `logs/fanout.log` when present, `driver_logs` (lane, ticket, path, line count, the run ids seen), and `gate_logs` (lane, ticket, k, attempt n or None for the legacy name, path, run ids seen, rc when a fanout.log or report line records `rc=<n>` for that gate). A line's run id is its `[fanout-<12 hex>] ` prefix, None without one. Register the `fanout` cases: a legacy fixture (no prefixes, `gate-alpha-T-0001-1.log`, no fanout.log, report.md without a Run line, outcome `red: ... rc=1`) and a prefixed fixture (`fanout.log`, `gate-alpha-T-0001-1-a1.log` and `-a2.log`, a `- Run:` line) both yield lane outcomes, gate attempts with rc, and per-line run ids (None for legacy, the id for prefixed).
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout | grep -q '^ok: fanout: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/fanout.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
