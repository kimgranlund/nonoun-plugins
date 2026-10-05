<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/reports/messages-idle-host-limit-2026-10-01.md: the evidence section now says the tool calls (`spawn_agent`, `wait_agent`, `followup_task`, `wait_agent`) are quoted from the parent's rollout files in the rollout paragraph of messages-live-run.md. The wrong `messages-live-run/codex-messenger.txt` reference is gone.
- The other six files are unchanged from the first build: messages.py, messenger.md, design.md, codex-role-execution.md, README.md and the generated sdlc-messenger-l1.toml.

## Checks
- Criterion 1 (the `grep -l 'cannot wake an idle host'` count over the 5 files is 5): pass
- `grep -q 'messages-idle-host-limit-2026-10-01.md' docs/README.md`: pass
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass ("Codex agent definitions verified")
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: pass (exit 0)
- Changed-files allowlist guard: pass
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Shellcheck was skipped because it is not installed.
- Checked every path and quoted string the note cites:
  - release-0.20.2.md exists.
  - `run_in_background: false` is in messages-live-run.md.
  - The "spawn it again" parent prompts are at messages-live-run.md lines 47 and 51.
  - `followup_task`, `spawn_agent` and `wait_agent` are in the rollout paragraph at line 156.
- The note has no em dashes (grep count 0).

## Notes
None
