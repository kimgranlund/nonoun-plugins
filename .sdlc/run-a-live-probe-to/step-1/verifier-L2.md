<!-- role=verifier level=L2 model=sonnet effort=high -->
All the required elements from the Do section are present and self-tested within the selftest suite itself (lines 176-214 verify the exact report format, PostToolUse handling, etc.), which the selftest guard already confirmed PASS. This corroborates the acceptance criteria results rather than substituting for them.

Everything checks out. Let me finalize the verdict.

## Verdict
pass

## Criteria
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -qF -- '--agent'`: pass. Evidence: ran the exact command, rc=0. Also ran on base worktree (HEAD, db8d3f4) via `git worktree add --detach`, rc=1 there, confirming the check bites (red before, green after).
- Selftest bites on an Agent-blind hook (sed `NoAgent` swap): pass. Evidence: ran the exact criterion command, `rc=1` from the selftest (`hook live probe selftest: FAIL: ... agent deny: hook exit code 0, not 2`), so `test "$rc" -ne 0` exits 0. Confirmed the sed pattern actually matches text in `plugins/sdlc-lite/hooks/block-background.sh:11` (`if [[ "$tool" == "Agent" ]]; then`), so the substitution is not a no-op. Also ran the same command against the base worktree, where it evaluates false (exit 1, since the base script has no Agent selftest path at all) — confirms the check discriminates base vs built tree.
- Selftest bites on a hook that denies `false` (sed `nope` swap): pass. Evidence: ran the exact criterion command, selftest failed with `agent allow: hook exit code 2, not 0`, `test "$rc" -ne 0` exits 0. Confirmed the sed pattern matches `plugins/sdlc-lite/hooks/block-background.sh:13` (`if [[ "$abg" != "false" ]]; then`).
- `grep -qF '"tool_name":"Task"' plugins/sdlc-lite/scripts/hook-live-probe.sh`: pass. Evidence: ran the command, rc=0; rc=1 on the base worktree (red before, green after).
- `grep -qF 'hook-live-probe.sh --agent' CLAUDE.md`: pass. Evidence: ran the command, rc=0; rc=1 on the base worktree.
- `grep -qF 'hook-live-probe.sh --agent' .claude/agents/sdlc-lite-author.md`: pass. Evidence: ran the command, rc=0; rc=1 on the base worktree.
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: pass. Evidence: ran it on the built tree, output `hook live probe selftest: PASS`, rc=0 (took 5:23 under current host load, consistent with builder's note about load).
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-live-probe.sh`: pass. Evidence: ran it, rc=0, no output.
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/hooks.json plugins/sdlc-lite/hooks/block-background.sh`: pass. Evidence: ran it, rc=0 (both hook files unchanged versus HEAD).

## Out of scope changes
`.sdlc/run-a-live-probe-to/handoff.md` (task-level handoff, distinct from the step-1 handoff this build targets) is modified in the diff, filling in Goal/Context/Constraints. Checked: its mtime (07:52) predates the planner run (planner-L2.md, 08:16) and this step's builder run (builder-L3.md, 08:33), and the diff content is template-filling (Goal/Context/Constraints), consistent with an earlier `/clarify` pass, not this build step. The builder's own note ("was already modified before this step. I did not touch it.") matches this timeline. Dismissing as pre-existing, not caused by this step.

Untracked `.sdlc/run-a-live-probe-to/planner-L2.md`, `runs.jsonl`, `step-2/`, `step-3/`: checked mtimes, all from 08:16-08:17, before this step's builder ran (08:33) and containing only their own `handoff.md` files with no builder/verifier output inside — normal `steps.py split` artifacts from the planning phase, not touched by this build. Dismissing as out of this step's scope but not a defect.

## For the next attempt
None.
