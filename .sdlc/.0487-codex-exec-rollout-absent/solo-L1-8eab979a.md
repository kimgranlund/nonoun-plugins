<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
🟢 T-0487 is fixed. The red test failed before the fix and passes after it, and no other test broke.

The cause is that `codex_exec.py` runs `codex exec --ephemeral`, so a rollout file is never written. The recorder looked for one anyway and printed `rollout absent`. A Codex log with a thread id and no rollout file now records `{"status": "exec ephemeral: no rollout written"}`. A log with no thread id, or an invalid one, still records `rollout absent`.

Files changed, all under `plugins/sdlc-lite/scripts/`:
- `traces/sources/context.py`: the new status and a docstring update.
- `run.sh`: the new status added to the header comment.
- `traces/selftest.py`: the codex-absent case and the ingest case now expect the new status. Both failed before the fix.
- `run-selftest.sh`: the loaded-context control now expects the new status.

Checks:
- `python3 traces.py selftest`: 0 failures. Before the fix it failed on the two updated cases.
- `bash run-selftest.sh`: PASS.
- `bash -n run.sh`: OK.
- `git diff --check`: clean.

Nothing is committed, as the brief said. This is level L1, so no verifier ran. The existing evidence file `docs/reports/codex-live-evidence/chain-step-1-runs.jsonl` still shows `rollout absent`. I left it as it is because it is a dated record of past runs.
