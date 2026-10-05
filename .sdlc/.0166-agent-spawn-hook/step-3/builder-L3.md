<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- docs/reports/agent-spawn-hook-live-run.md (new): the live probe report. I added a short note under the top heading, and `verdict: PASS` is still the last line.
- docs/README.md: added one validation index entry, "Agent spawn hook live run", which links to `validation/agent-spawn-hook-live-run.md`.
- docs/maintenance/claude-hooks.md: added a new section, ``## `hooks/block-role-spawn.sh` ``, after the `block-disk-scan.sh` section. It covers the event and matcher, how a conductor session is detected, the deny rule, the allowed helpers, where the fixtures and the probe live, and says Codex is not enforced. The closing paragraph now says "Bash, Agent, and conductor modes".
- plugins/sdlc-lite/agents/conductor.md: added one sentence to the "Planner, builder, and verifier work runs only through" bullet: in Claude Code, `hooks/block-role-spawn.sh` denies such spawns, and Codex has no equivalent enforcement.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml: regenerated with `codex_roles.py generate`.

## Checks
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --conductor --out docs/reports/agent-spawn-hook-live-run.md`: exit 0, `verdict: PASS`, with 2 live haiku runs on claude 2.1.285.
  - Deny run: agent_type `sdlc-lite:conductor`, subagent_type `sdlc-lite:scout`, hook exit code 2.
  - Allow run: agent_type `sdlc-lite:conductor`, subagent_type `general-purpose`, hook exit code 0.
- `test -f docs/reports/agent-spawn-hook-live-run.md`: pass.
- `test "$(tail -n 1 ...)" = "verdict: PASS"`: pass.
- grep for the conductor deny line: pass.
- grep for the conductor allow line: pass.
- `grep -qF "validation/agent-spawn-hook-live-run.md" docs/README.md`: pass.
- `grep -qE "^## .hooks/block-role-spawn\.sh.$" docs/maintenance/claude-hooks.md`: pass.
- awk over the new section's body piped to `grep -q Codex`: pass.
- `grep -q block-role-spawn.sh plugins/sdlc-lite/agents/conductor.md`: pass.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass ("Codex agent definitions verified").
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass.
- Extra checks:
  - `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.
  - `python3 scripts/check-packaging.py`: PASS.
  - `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: PASS.
  - `git diff --check`: clean.

## Notes
- The live run recorded agent_type `sdlc-lite:conductor`, which the hook already matches, so `block-role-spawn.sh` and its fixtures are unchanged. The conductor model made the call on the first attempt, so the probe prompt is unchanged too.
- The report note says the run does not cover the interactive `.claude/settings.json` agent path, which I did not observe.
- If the probe is rerun, it overwrites the report, and the hand-written note under the heading has to be added again.
- Nothing is committed.
