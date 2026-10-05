## Task goal
When the SDLC Lite conductor is in force, an Agent-tool spawn of another plugin's builder, verifier, or planner agent is flagged before it runs, with a message pointing at `run.sh`.

## Step 3: Live conductor run, evidence, and docs
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --conductor --out docs/reports/agent-spawn-hook-live-run.md` from the repository root in the foreground. This spends model calls; the handoff's done-condition asks for live evidence. The T-0165 probe (`docs/reports/role-routing-probe.md`) launched the conductor the same way, `claude -p --agent sdlc-lite:conductor --plugin-dir <plugin>`, so the launch form is known to work.
- If the recorded `agent_type` is neither `sdlc-lite:conductor` nor `conductor`, change the match in `hooks/block-role-spawn.sh` and its selftest fixtures to the observed value, then rerun.
- If the conductor model refuses the call, strengthen the probe prompt rather than weakening the checks.
- Add a short note under the report's top heading, never after the verdict line (the verdict must stay the last line of the file), on what it proves: the observed `agent_type` for a plugin session agent launched with `--agent sdlc-lite:conductor`. It does not prove the interactive `.claude/settings.json` agent path, unless you also observe that path and record it there.
- Add the report to the index in `docs/README.md`: one list item in the form of the existing validation entries (dated live run for T-0166), whose link target is `validation/agent-spawn-hook-live-run.md`.

Add a section to `docs/maintenance/claude-hooks.md` after the `block-disk-scan.sh` section and before the closing paragraph. Its heading has exactly the form of the other hook sections there: two hash marks, a space, then the path `hooks/block-role-spawn.sh` wrapped in single backticks. The acceptance criteria match that heading with a dot in place of each backtick, so keep this form. The section covers:
- the event and matcher: PreToolUse, Agent
- conductor detection: `agent_type` of `sdlc-lite:conductor` or `conductor`, or `SDLC_ROLE=conductor`
- the deny rule (SDLC Lite role agents; another plugin's builder, verifier, reviewer, planner, or checker agent) and the allowed helpers (Explore, general-purpose, Plan, a missing subagent_type)
- the fixtures' location in `scripts/hook-selftest.sh` and the `--conductor` probe in `scripts/hook-live-probe.sh`
- the statement that this is a Claude hook only and Codex conductor sessions are not enforced; the word `Codex` must appear inside this section's own body, because the criterion searches only the text between this heading and the next level-two heading
Also extend the closing paragraph's "Bash and Agent modes" to name the conductor mode.

In `plugins/sdlc-lite/agents/conductor.md` line 24 (the bullet beginning "Planner, builder, and verifier work runs only through"), add one sentence: in Claude Code, `hooks/block-role-spawn.sh` denies such spawns, and Codex has no equivalent enforcement. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so the generated `sdlc-conductor-l1.toml` follows.
### Acceptance criteria
- `test -f docs/reports/agent-spawn-hook-live-run.md`
- `test "$(tail -n 1 docs/reports/agent-spawn-hook-live-run.md)" = "verdict: PASS"`
- `grep -qE "^conductor deny: agent_type [^ ]*conductor, .*hook exit code 2$" docs/reports/agent-spawn-hook-live-run.md`
- `grep -qE "^conductor allow: agent_type [^ ]*conductor, .*hook exit code 0$" docs/reports/agent-spawn-hook-live-run.md`
- `grep -qF "validation/agent-spawn-hook-live-run.md" docs/README.md`
- `grep -qE "^## .hooks/block-role-spawn\.sh.$" docs/maintenance/claude-hooks.md` (a dot stands in for each backtick around the path)
- `awk "/^## .hooks\/block-role-spawn\.sh./{f=1;next} /^## /{f=0} f" docs/maintenance/claude-hooks.md | grep -q Codex` (only the new section's body, up to the next level-two heading, is searched)
- `grep -q block-role-spawn.sh plugins/sdlc-lite/agents/conductor.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
