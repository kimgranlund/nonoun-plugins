## Task goal
A Claude Code conductor can start the `solo` agent for a size S or M ticket, and every routing text agrees that solo is the default lane. Read `.sdlc/0217-solo-start-path/handoff.md` (Goal, Intent, Context, Constraints) first: it is the ticket.

## Step 1: Give the conductor a start path for solo and make the routing texts agree
level: L3

### Read first
- plugins/sdlc-lite/agents/solo.md
- plugins/sdlc-lite/agents/conductor.md (T-0199's rules are already in this branch: keep them, do not duplicate)
- plugins/sdlc-lite/hooks/block-role-spawn.sh
- plugins/sdlc-lite/skills/fix/SKILL.md
- plugins/sdlc-lite/scripts/check.py (the numbered items: add item 19 to the docstring and the code; existing item numbers repeat from merges, leave them)

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests or doc edits outside this step. Report blocked instead of looping. Keep one authoritative location per fact.
1. Start path, the smaller option: block-role-spawn.sh only gates the Agent tool, so a conductor starts solo as a headless session from Bash with `claude -p --plugin-dir ${CLAUDE_PLUGIN_ROOT} --agent sdlc-lite:solo --model <model> --effort <effort> "<typed brief>"` run in the foreground at the project root, with the tier model and effort from the table in solo.md (S Sonnet low, M Sonnet xhigh, L Opus xhigh). Put that one command and one sentence on how a conductor uses it (and that the hook denies the Agent-tool spawn of any `sdlc-lite:` agent, so this is the path) in agents/solo.md, nowhere else. If the publish and other role hooks key off `SDLC_ROLE`, set the right value in that command so the session is guarded like a role (read the hooks to see; change no hook unless a hook would otherwise leave the solo session unguarded, and then keep the change minimal with a positive case and a negative control that a scout spawn is still denied). Add a Codex note in solo.md: the conductor starts `sdlc-solo-l1`, `sdlc-solo-l2`, or `sdlc-solo-l3` through the existing Codex path.
2. Routing texts agree that size S and M go to `solo` by default and that `/fix` is used only when the user asks for it or the lane script prints `fix`: conductor.md (reconcile with T-0199's lane line, do not duplicate), skills/fix/SKILL.md (its description and opening), plugins/sdlc-lite/AGENTS.md (the lane rule line), and .claude/agents/sdlc-lite-author.md (the objective line).
3. check.py: add item 19 that guards the agreement with a negative control: agents/solo.md holds the `--agent sdlc-lite:solo` start command, and the four routing texts mention `solo`; the phrase removed from any one must be flagged.

### Acceptance criteria
- `grep -q -- "--agent sdlc-lite:solo" plugins/sdlc-lite/agents/solo.md`
- `grep -q "solo" plugins/sdlc-lite/agents/conductor.md && grep -q "solo" plugins/sdlc-lite/skills/fix/SKILL.md && grep -q "solo" plugins/sdlc-lite/AGENTS.md && grep -q "solo" .claude/agents/sdlc-lite-author.md`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs .claude`
