<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0166: Deny conductor Agent-tool spawns of role agents with a PreToolUse hook

## PR body
### Summary
When the session runs as the SDLC Lite conductor, a new Claude Code `PreToolUse(Agent)` hook denies an Agent-tool spawn of an SDLC Lite role agent. It also denies another plugin's builder, verifier, reviewer, planner, or checker agent. The deny message points at `run.sh`. Non-conductor sessions and read-only helpers such as `Explore` and `general-purpose` are not blocked. The rule is Claude Code only; Codex has no equivalent enforcement, and the docs and `conductor.md` say so.

The handoff allowed "warns or denies". The plan chose deny (exit 2).

### Changes
- New `plugins/sdlc-lite/hooks/block-role-spawn.sh`, registered in `adapters/claude/hooks.json` under the existing `Agent` matcher, after `block-background.sh`.
  - A session counts as the conductor when `agent_type` is `sdlc-lite:conductor` or `conductor`, or when `SDLC_ROLE=conductor`.
  - It denies `sdlc-lite:*`, and plugin-qualified names with a `builder`, `verifier`, `reviewer`, `planner`, or `checker` token.
- `scripts/hook-selftest.sh`: 12 fixtures (6 deny, 6 allow), including a session with no `agent_type`. `scripts/check.sh`: header comment lists the new hook.
- `scripts/hook-live-probe.sh`: new `--conductor` mode. It runs two real `claude --agent sdlc-lite:conductor` sessions (one deny, one allow) and writes a report. Selftest cases (k) to (o) cover it.
- New `docs/validation/agent-spawn-hook-live-run.md`, the recorded live run, linked from `docs/README.md`.
- `docs/maintenance/claude-hooks.md`: new `hooks/block-role-spawn.sh` section, with the Codex statement.
- `plugins/sdlc-lite/agents/conductor.md`: one sentence naming the hook and the Codex gap. The generated `adapters/codex/agents/sdlc-conductor-l1.toml` is regenerated to match.

### How each was verified
All four steps passed their independent verifiers.
- Step 1 (hook, registration, fixtures): the verifier ran the conductor and `sdlc-lite:builder` case (exit 2, stderr contains `run.sh`). It also ran the `Explore` and no-`agent_type` cases (exit 0). It confirmed the registration with `jq`. Negative control: a stub hook that always exits 0 makes the selftest fail.
- Step 2 (`--conductor` probe): `--help` lists the mode. Negative control: with an allow-all hook the probe selftest fails at (k). The verifier also mutated the exit-code check, and case (m) failed. `hook-live-probe.sh --selftest` and `hook-selftest.sh` pass.
- Step 3 (live run and docs): a live run on claude 2.1.285 with a haiku model.
  - Deny run: `agent_type sdlc-lite:conductor`, `subagent_type sdlc-lite:scout`, hook exit code 2.
  - Allow run: `agent_type sdlc-lite:conductor`, `subagent_type general-purpose`, hook exit code 0.
  - The last line of the report is `verdict: PASS`. The verifier confirmed the transcript exists. The docs greps pass, and `codex_roles.py generate --check` passes.
- Step 4 (gates): the verifier ran `bash plugins/sdlc-lite/scripts/check.sh` (every gate "positive ok, negative ok"), `python3 scripts/check-packaging.py`, and `git diff --check` against the base. All exited 0.
- `shellcheck` is not installed on the host, so it was not run.

The live run covers `--agent sdlc-lite:conductor`. It does not cover an interactive session that declares the conductor in `.claude/settings.json`.

## Changelog entry
- Added a Claude Code `PreToolUse(Agent)` hook, `block-role-spawn.sh`. In a conductor session it denies spawning SDLC Lite role agents, or another plugin's builder, verifier, reviewer, planner, or checker agent, through the Agent tool, and points at `run.sh`. Codex is not covered. Added a `--conductor` mode to `hook-live-probe.sh` and a recorded live run.

## Follow-ups
- decide: The interactive `.claude/settings.json` conductor path was never observed; only `--agent sdlc-lite:conductor` was live-tested, so it is unknown whether `agent_type` is set there and the hook fires.
- note: `git diff --check` skips untracked files, so `block-role-spawn.sh` and the live-run report were not whitespace-checked; run it once they are added.
- note: Rerunning `hook-live-probe.sh --conductor --out` overwrites the live-run report and drops its hand-written note under the heading.
