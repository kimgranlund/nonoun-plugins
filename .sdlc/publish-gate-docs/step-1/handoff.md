## Task goal
Nobody assumes the publish hook guards the user's own session.

## Step 1: Document the hook's scope in the conductor agent and /file
level: L1

### Do
- In `plugins/sdlc-lite/agents/conductor.md`, near the existing rule "Publishing (commit, push, PR, issue) happens only after the user approves it through AskUserQuestion", add one or two plain sentences: `hooks/block-publish.sh` exits 0 unless `SDLC_ROLE` is set (only `scripts/run.sh` sets it), by design, so it guards role runs only; publishing from the user's own session is gated only by the AskUserQuestion approval step in /file.
- In `plugins/sdlc-lite/skills/file/SKILL.md`, at the approval/publish step, state the same fact: the hook does not guard this session, so the AskUserQuestion approval is the only gate; never publish without it.
- Style: no em dashes, no bold inline labels, plain short sentences. Do not change the hook itself or any other file.
- Run `plugins/sdlc-lite/scripts/check.sh` and report its result (the validate warning about the repo CLAUDE.md is expected).

### Acceptance criteria
- conductor.md states that block-publish.sh exits 0 unless SDLC_ROLE is set, so it does not guard the user's own session.
- skills/file/SKILL.md states the same, and that the AskUserQuestion approval is the only publish gate in the user's session.
- `hooks/block-publish.sh` is unchanged; `git diff --stat` shows only those two files.
- No em dash (U+2014) in the added text.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.
