## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 11: Findings writer, stable ids, and clusters
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/findings.py`: `make(detector, family, severity, layer, cause_file, cause_rule, evidence, summary)` returns a finding dict with `id` = the first 12 hex of sha256 over the detector name plus the sorted evidence keys and values, `detector`, `family`, `severity` (3 high, 2 medium, 1 low), `layer` (one of sdlc-lite, project, host, task-text, unknown), `cause_hint` {file (a plugin-relative path or None), rule}, `evidence` (a list of {path, line} or {attempt_id} entries, each allowed extra keys), `summary`; `write(out, findings, now)` merges into `<out>/findings.jsonl`: an id already present keeps its `first_seen` and gets `last_seen` = now, a new id gets both = now, an id absent from this run is kept with `stale` True; `clusters(out, max_n)` groups the non-stale findings by `cause_hint.file`, ranks clusters by highest severity then finding count, caps the list at `max_n`, writes `<out>/clusters.json`, and returns the list. Register the `findings` cases: writing the same three synthetic findings twice keeps every id and changes only `last_seen`; a finding missing from the second run is marked stale; `clusters(out, 2)` on findings over three cause files returns the two highest-severity clusters.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings | grep -q '^ok: findings: '`
- `test -f plugins/sdlc-lite/scripts/traces/findings.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
