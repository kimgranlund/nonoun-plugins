## Task goal
The sdlc-lite-author invariant on line 19 of `.claude/agents/sdlc-lite-author.md` covers the builder no-Status `rebuild`/`stop` route and the run.sh exit 3 rule, matching CLAUDE.md (ticket T-0106, `.sdlc/extend-claude-agents-sdlc-lite/handoff.md`).

## Step 1: Independent check of the conductor's trivial edit
level: L1

Context: the conductor made this one-line doc edit itself (uncommitted, in the work tree; see `git diff -- .claude/agents/sdlc-lite-author.md`). No builder ran. Check the edit against the code and docs it describes; do not edit anything and do not change git state.

### Do
Line 19 of `.claude/agents/sdlc-lite-author.md` (the "No-verdict route" invariant) additionally states: a builder result with no done/blocked Status maps to `rebuild` at its level in `steps.py next`, is never a fail or a bump, and two in a row map to `stop`; `run.sh` exits 3 when a result lacks its role's required section, keeping the result file and `runs.jsonl` line, and that exit goes through `steps.py next`, never to done; and the sync list names run.sh.

### Acceptance criteria
- `sed -n 19p .claude/agents/sdlc-lite-author.md | grep -q 'rebuild'` and the same line mentions `stop`, `exits 3`, and `run.sh`.
- Every claim on line 19 matches the behavior in `plugins/sdlc-lite/scripts/steps.py` (`next`), `plugins/sdlc-lite/scripts/run.sh` (required-section check), `plugins/sdlc-lite/skills/chain/SKILL.md`, `plugins/sdlc-lite/agents/conductor.md`, and `CLAUDE.md`; none contradicts them.
- `git diff --stat -- .claude/agents/sdlc-lite-author.md` shows only that file with one line changed, and no other invariant line changed.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
