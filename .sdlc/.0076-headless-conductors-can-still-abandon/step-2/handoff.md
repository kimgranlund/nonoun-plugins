## Task goal
A headless sdlc-lite session (SDLC_ROLE set, or SDLC_HEADLESS=1) cannot launch a background subagent through the Agent tool and then end its turn, abandoning the work; interactive sessions are unaffected.

## Step 2: Name Agent in every doc that describes block-background.sh
level: L1
### Do
Update each description of the guard so it says the hook covers both Bash and Agent in headless sessions. For Agent, it denies the call unless `run_in_background` is explicitly `false`, because Agent runs in the background by default and a missing field counts as background. Keep all other wording, and keep every word `scripts/check.py` requires (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`) in chain, bench, fanout, and conductor. No em dashes. Files to change:
- Repo-root `CLAUDE.md`, the `hooks/block-background.sh` Layout bullet. Change `PreToolUse(Bash) hook` to `PreToolUse(Bash, Agent) hook` or similar, and add the Agent rule. Leave the `block-publish.sh` bullet as it is.
- `plugins/sdlc-lite/agents/conductor.md`
- `plugins/sdlc-lite/skills/chain/SKILL.md`
- `plugins/sdlc-lite/skills/bench/SKILL.md`
- `plugins/sdlc-lite/skills/fanout/SKILL.md`
- `.claude/agents/sdlc-lite-author.md`, which mirrors CLAUDE.md.
- The comments in `plugins/sdlc-lite/scripts/bench.sh` (line 7) and `plugins/sdlc-lite/scripts/fanout.py` (the driver env docstring near line 36), where they say the hook denies `run_in_background`, so they mention Agent too.
### Acceptance criteria
- `grep 'hooks/block-background.sh' CLAUDE.md | grep -q Agent`
- `! grep 'hooks/block-background.sh' CLAUDE.md | grep -q 'PreToolUse(Bash)'`
- `grep 'block-background' plugins/sdlc-lite/agents/conductor.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/bench/SKILL.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q Agent`
- `grep 'block-background' .claude/agents/sdlc-lite-author.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/scripts/bench.sh | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/scripts/fanout.py | grep -q Agent`
- (guard) `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/skills plugins/sdlc-lite/scripts/bench.sh plugins/sdlc-lite/scripts/fanout.py plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-selftest.sh | grep '^+' | grep -q '—'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0. It is green on the current tree.
