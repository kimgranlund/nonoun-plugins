## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 17: Selftest suite, corpus regression, check.sh wiring
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add the `corpus` family to `traces/selftest.py`: it prints `skip: corpus: <why>` when `<git toplevel>/.sdlc/.0109-make-the-fixed-count-lint` is absent; otherwise it runs `ingest.run(toplevel, out=<temp dir>)` and the detectors and asserts that every `*.attempt.json` under `<toplevel>/.sdlc/` (walking the dot folders too) is named in some row's `sources`, that every runs.jsonl line that parses as an object maps to exactly one row, and that the findings hold `plan-defect-refusal` with evidence path `.sdlc/.0109-make-the-fixed-count-lint/handoff.md`, `plan-defect-refusal` with evidence path `.sdlc/.0134-mirror-the-extended-planner-rules/step-1/verifier-L1.md`, `replan-loop` with evidence path `.sdlc/.0113-close-rename-breaks-refs/step-2.superseded-1/builder-L2.md`, and `attempt-without-run-row` with the attempt id recorded in `.sdlc/.0162-entry-files-in-step-handoffs/step-6/builder-L2.attempt.json` (status failed, no runs.jsonl row); when `<toplevel>/.worktrees/fanout-night/logs` exists it also asserts `overwritten-gate-log` for `gate-steps-T-0148-1.log`, else prints a `skip:` line for that part. The whole suite (no `-k`) prints one `ok:` line per detector positive and one per negative control from steps 12 to 15 plus the reader, join, store, and findings cases; the whole suite is a guard here because it already passes and must keep passing, so fix any case an earlier step broke. Wire `python3 "$root/scripts/traces.py" selftest || fail=1` into `plugins/sdlc-lite/scripts/check.sh` after the onboard selftest line and name the traces selftest in its header comment.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest | grep -q '^ok: corpus: '`
- `grep -qF 'traces.py' plugins/sdlc-lite/scripts/check.sh`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh)$')"`
