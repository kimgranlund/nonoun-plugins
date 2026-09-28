<!-- role=verifier level=L1 model=sonnet effort=medium -->
All checks pass. Now filing the verdict.

## Verdict
pass

## Criteria
- `grep -qF 'PreToolUse(Bash, Agent, Monitor)' CLAUDE.md`: pass. Evidence: `grep -qF ... CLAUDE.md && echo PASS1` → PASS1; confirmed red at pre-build HEAD in throwaway worktree (`git worktree add --detach <tmp>/base HEAD`) → FAIL1, so the check bites.
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' CLAUDE.md`: pass. Evidence: grep exits 0; CLAUDE.md:23 states the run.sh Layout description (BASH_DEFAULT_TIMEOUT_MS/BASH_MAX_TIMEOUT_MS to 3600000 unless already higher, stream-json log, result pick), matching the Do.
- `grep -q 'stream-json' CLAUDE.md`: pass. Evidence: CLAUDE.md:23, "It logs the run as `--output-format stream-json --verbose`".
- `grep -q 'task-notification' CLAUDE.md`: pass. Evidence: CLAUDE.md:23, "...else the last one whose origin is not `task-notification`, else the last one..."; confirmed red at pre-build HEAD (FAIL4).
- `grep -q 'Monitor' .claude/agents/sdlc-lite-author.md`: pass. Evidence: file line 37 area names Monitor in the headless-foreground hazard and says run.sh and fanout raise the timeouts (confirmed via file diff and grep); red at pre-build HEAD (FAIL5).
- `grep -q 'stream-json' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: SKILL.md:42, "`.sdlc/**/*.log`: raw role transcript (stream-json: one JSON event per line, stderr mixed in)"; red at pre-build HEAD (FAIL6).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran in the built tree, exit 0, all selftests, shellcheck, and plugin validate PASS; also ran in the pre-build-HEAD throwaway worktree, exit 0 (gate was already green there too, so no inherited-red concern; the guard passing both before and after is consistent with a documentation-only step that fixes any red earlier steps introduced, per the Do).

Other Do items not covered by a grep criterion, checked directly: `plugins/sdlc-lite/agents/conductor.md` now says bench.sh, run.sh, and fanout raise timeouts and every Monitor call is denied (line 23); `plugins/sdlc-lite/skills/chain/SKILL.md` lists Monitor in the block-background denial list (line 9); `plugins/sdlc-lite/skills/fix/SKILL.md` correctly left unchanged since it does not enumerate what block-background denies (verified via grep, no match); `plugins/sdlc-lite/scripts/check.sh` header comment names the Monitor fixtures and run selftest coverage (lines 3-4).

## Out of scope changes
None. `git diff --stat` restricted to the six files the Do names shows exactly the expected edits (CLAUDE.md, .claude/agents/sdlc-lite-author.md, conductor.md, check.sh, chain/SKILL.md, handoff-format/SKILL.md), and the builder's own tool-call log (`step-6/builder-L2.log`) shows no edits outside these files. Other modified files in `git status` (builder.md, verifier.md, block-background.sh, hooks.json, check.py, fanout.py, hook-selftest.sh, run-selftest.sh, run.sh, step-1 through step-5 dirs, planner-L2.md) are uncommitted carryover from this task's earlier steps (1-5), not touched by this step's builder run.

## For the next attempt
None.
