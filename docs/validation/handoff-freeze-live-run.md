# Handoff freeze live run

Recorded: 2026-10-04. Ticket T-0212 (warn mode), built as one handwritten step. Branch `t0212`, plugin files uncommitted at the time of the run (the hook and `hooks.json` are in this branch's tree).

## What was built

- `run_lifecycle.py` stores the handoff's sha256 at launch (`handoff_sha256` in the attempt record, `SDLC_HANDOFF_SHA256` in the child environment).
- `run.sh` rehashes the handoff before it writes the run line, adds `handoff_sha256` and `stale_input` to it, and prints `run.sh: stale input: <handoff> changed while <role> ran`. The exit code is unchanged.
- `hooks/warn-handoff-edit.sh`, registered under an `Edit|Write|NotebookEdit` matcher: warn mode (default) allows the edit, warns, and appends to `stale-edits.log`; `SDLC_HANDOFF_EDIT_MODE=deny` blocks it.

## Environment

- 2.1.289 (Claude Code), run from a throwaway git project in a temporary folder outside this repository, with the plugin's `adapters/claude/hooks.json` registered through `--settings` (commands rewritten to this branch's plugin path).
- Model from each result's `modelUsage`: `claude-haiku-4-5`, effort low, `--permission-mode acceptEdits`, `--allowedTools Read Edit`.
- The project held `.sdlc/x/handoff.md` and an empty `.sdlc/x/planner-L3.running` beside it (a role is live).

## Live results

| Arm | Command setting | Handoff after | stale-edits.log | Observed |
| --- | --- | --- | --- | --- |
| Warn (default) | none | `new` (edit applied) | one line: `edited while planner-L3 ran` | Edit allowed, logged |
| Deny | `SDLC_HANDOFF_EDIT_MODE=deny` | `old` (unchanged) | one line | Model reported "A hook is blocking the edit ... scope changes belong in a new ticket" |

Evidence: [warn](handoff-freeze-live-run/claude-warn.json), [deny](handoff-freeze-live-run/claude-deny.json). One run per arm. A first attempt in the user's default plan permission mode logged the hook line but could not edit because of plan mode, not the hook; it is not counted.

## Offline checks

- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: warn allows and logs (Edit, Write, NotebookEdit), deny exits 2 (negative control), no `.running` file, another file name, and a missing path pass silently with no log line.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: a stub planner that edits the handoff mid-run gives `stale_input` true and one stderr line; no edit and a sibling-file edit give false; a stub that never reads the handoff but whose file changed is still flagged. Negative controls observed: forcing `stale_input=false` fails the edit case, and a wrong `handoff_sha256` fails the launch-hash case.
- `scripts/check.py` item 18 guards the names, the hook file, its registration, and the doc, each with a negative control.

## Known limits

- The `rerun <level> stale input` action in `steps.py next`, `resume` and `review`, and excluding a stale planner result from `review_action`, `lean_warnings` and `footprint.py`, are not built. The flag is on the run line only. A conductor, or a later ticket, has to act on it.
- No Codex arm. Codex has no hooks. The runner flag works on both backends because `run_lifecycle.py` wraps both, but the selftest used the Claude stub; a real Codex run with a mid-run edit was not made.
- The hook warns on stderr and the log; with exit 0 the model may not see the warning text on every host version. The deny arm shows the model does see a denial.
- The ticket's live criterion "a planner run ends in rerun" is not met, because the rerun action is not built.

## Verification

An independent L3 verifier (Fable, via `run.sh` from a frozen runner checkout, `.sdlc/.0212-handoff-freeze/step-1/verifier-L3.md`) ran every criterion and found one defect: `scripts/check-packaging.py` pinned the PreToolUse route count at 3, and the new matcher made it 4. It was fixed (the pin is now 4 plus a check that the `Edit|Write|NotebookEdit` route names the hook; observed: removing the route makes it fail) and was not re-verified by a second role run, in line with the burn-down rules. All other criteria passed, including both negative controls and the real hook probe. The verifier also noted the record's JSON evidence files hold only result, cost, turns and model, so the live-run table rests on those fields and on the stale-edits.log lines shown above. After merging main in, `bash plugins/sdlc-lite/scripts/check.sh`, `check-packaging.py`, `codex_roles.py generate --check`, `tickets.py check`, `run-selftest.sh` and `hook-selftest.sh` pass.
