## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 6: docs describe the three fixes; gates green
level: L2
### Do
Update every record that describes these routes in the same change:
- `CLAUDE.md`:
  - The block-background line becomes `PreToolUse(Bash, Agent, Monitor)` and says Monitor is denied headless.
  - The run.sh Layout line says run.sh sets `BASH_DEFAULT_TIMEOUT_MS`/`BASH_MAX_TIMEOUT_MS` to 3600000 unless already higher, logs `stream-json`, and saves the last result holding the required heading, else the last one without a `task-notification` origin.
  - The Commands check.sh line names the new fixtures.
- `.claude/agents/sdlc-lite-author.md`: the headless-foreground hazard names Monitor and the run.sh timeouts.
- `plugins/sdlc-lite/agents/conductor.md`: where it says bench.sh raises the Bash timeouts, say run.sh and fanout do too.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the `.log` is a stream-json role transcript.
- `plugins/sdlc-lite/scripts/check.sh`: header comment.
- The chain and fix skills, if they list what block-background denies.

Then run every gate below and fix any red that earlier steps introduced.
### Acceptance criteria
- `grep -qF 'PreToolUse(Bash, Agent, Monitor)' CLAUDE.md`
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' CLAUDE.md`
- `grep -q 'stream-json' CLAUDE.md`
- `grep -q 'task-notification' CLAUDE.md`
- `grep -q 'Monitor' .claude/agents/sdlc-lite-author.md`
- `grep -q 'stream-json' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
