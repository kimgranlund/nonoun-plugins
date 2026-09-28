## Task goal
Running ticket lanes in parallel needs no hand-written driver.

## Step 3: `/fanout` skill, conductor route, long-run guard, and records
level: L2
### Do
- Create `plugins/sdlc-lite/skills/fanout/SKILL.md` in the launcher-skill shape (frontmatter `name: fanout`, `description` starting "Run ticket lanes in parallel: ...", `argument-hint: <lane>=<ids>... [--base REF] [--integration BRANCH] [--gate CMD]... [--lanes-dir DIR]`, `allowed-tools` limited to `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py:*)`, `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*)`, `Bash(git merge --ff-only:*)`, `Read`). Steps: 1. run `fanout.py run --dry-run` with the arguments and the project's own check or test commands as `--gate`s, show the plan; 2. confirm lanes and gates with AskUserQuestion (recommended first: run as planned); 3. run `fanout.py run` with the same session rule as /chain, stated in the skill's own words: headless (`claude -p`) in the foreground with the Bash `timeout` at 3600000, in an interactive session with `run_in_background: true`, wait for the completion notification, never poll with `sleep`; 4. when notified, print `<lanes-dir>/report.md` and `board.py --lanes --waiting "<line>"` verbatim; 5. AskUserQuestion, recommendation first when every ticket merged: fast-forward main with `git merge --ff-only <integration>` in the main worktree, or leave it; never push, never merge otherwise. Say that lane worktrees stay for inspection and that `fanout.py` commits only inside the lanes dir.
- `plugins/sdlc-lite/agents/conductor.md`: add a route line "Several ready tickets to run in parallel lanes → `/sdlc-lite:fanout`" under `## Route every ask`.
- `plugins/sdlc-lite/scripts/check.py`: add `'skills/fanout/SKILL.md'` to the long-run doc tuple (item 4) and its docstring.
- Root `CLAUDE.md`: add `/fanout` to the "Workflow skills" line and the Commands section (`Fan out lanes: scripts/fanout.py run <lane>=<ids>...`); `.claude/agents/sdlc-lite-author.md`: an invariant to keep `scripts/fanout.py`, the /fanout skill, `board.py --lanes`, the /board skill, and CLAUDE.md in sync, and the long-run hazard now naming four docs (chain, bench, fanout, conductor).
### Acceptance criteria
- `test -f plugins/sdlc-lite/skills/fanout/SKILL.md && grep -q '^argument-hint: ' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q 'skills/fanout/SKILL.md' plugins/sdlc-lite/scripts/check.py`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite/. "$t/" && sed -i.bak 's/run_in_background/RIB/g' "$t/skills/fanout/SKILL.md" && python3 "$t/scripts/check.py" "$t" | grep -q 'skills/fanout/SKILL.md: long-run rule missing words'` (the long-run guard bites on the new skill)
- `grep -q 'fanout' plugins/sdlc-lite/agents/conductor.md && grep -q 'Workflow skills: .*fanout' CLAUDE.md && grep -q 'fanout' .claude/agents/sdlc-lite-author.md`
- Reading `skills/fanout/SKILL.md` shows: the dry run first, an AskUserQuestion before the real run, the interactive versus headless rule, the report and `board.py --lanes` as the status output, the single `git merge --ff-only` of main only after an AskUserQuestion, and no push.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (includes `claude plugin validate` on the new skill).
