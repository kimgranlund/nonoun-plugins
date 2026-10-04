## Task goal
T-0212 handoff freeze, WARN mode (user decision): record a handoff's hash at role launch, flag the run line `stale_input` when it changed while the role ran, and add a Claude-only hook that warns and logs (deny switch) when a running role's handoff.md is edited.

## Step 1: stale_input flag, run line fields, warn-handoff-edit hook
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/maintenance/claude-hooks.md` (section `hooks/warn-handoff-edit.sh`)
### Do
Built directly (no builder role) against the base commit in `base-sha`: `run_lifecycle.py` (handoff_sha256 in the attempt record, SDLC_HANDOFF_SHA256 in the child env), `run.sh` (rehash before the jq append, `handoff_sha256` and `stale_input` on the run line, stderr `run.sh: stale input: <handoff> changed while <role> ran`, exit code unchanged), new `hooks/warn-handoff-edit.sh` registered under `Edit|Write|NotebookEdit` in `adapters/claude/hooks.json`, selftests in `run-selftest.sh` and `hook-selftest.sh`, `check.py` item 18, `docs/maintenance/claude-hooks.md`, and `docs/validation/handoff-freeze-live-run.md`.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints `hook selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- (red) Negative control, run it yourself in a throwaway copy of the repository, never in this tree: change `stale_input=true` in `plugins/sdlc-lite/scripts/run.sh` to `stale_input=false`; `run-selftest.sh` must then fail with a `stale input:` line. Change the hook's deny `exit 2` to `exit 0`; `hook-selftest.sh` must then fail.
- Run a real hook probe: feed `hooks/warn-handoff-edit.sh` JSON `{"tool_name":"Edit","tool_input":{"file_path":"<tmp>/handoff.md"}}` with a `planner-L3.running` file beside it: exit 0, stderr names planner-L3, and `stale-edits.log` gains one line; with `SDLC_HANDOFF_EDIT_MODE=deny` exit 2; with no `.running` file, exit 0 and no log.
- Check the claims in `docs/validation/handoff-freeze-live-run.md` against the tree and the two JSON evidence files; the record states its own limits (no `rerun` action in steps.py, no Codex arm). Report any statement that is wrong or unsupported.
- Scope: `git diff --name-only <base-sha>` touches only the files named under Do (plus the ticket and step folders under `.sdlc/0212-*`); it does not touch `steps.py`, `footprint.py`, `board.py`, `budget.py`, any model or effort table, or `plugins/sdlc-lite/agents/`.
- Report whether `rerun <level> stale input` exists anywhere in `steps.py`; it is expected NOT to (a stated, recorded limit) and must not be counted as a failure unless the record claims otherwise.
