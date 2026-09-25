<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -rn -i "by mtime"` returns only task-display-order text: pass. Evidence: I ran the exact command. It returned only `plugins/sdlc-lite/scripts/board.py:253,256` (the `sort_tasks` docstring) and `:453,482,487` (the selftest), exit 0. I also confirmed the check can fail: `git grep -n -i "by mtime" HEAD -- <same paths>` at HEAD also matched `handoff-format/SKILL.md:27` ("the newest file by mtime is the current one"), `steps.py:5,259,275,331` and `tickets.py:938,942`. The board SKILL has no "by mtime" text, and `git diff --stat` shows it unchanged.
- `grep -n "order.py"` finds a match in each of the three files: pass. Evidence: `.claude/agents/sdlc-lite-author.md:17` (the new invariant: newest-file decisions go through `scripts/order.py`, never mtime), `CLAUDE.md:26` (the Layout bullet: the rule, runs.jsonl lines carry `file`, check.sh runs its selftest) and `plugins/sdlc-lite/skills/handoff-format/SKILL.md:27`. I also confirmed this check can fail: the same `git grep` at HEAD exits 1 with no matches. SKILL.md:16 now lists `file` among the runs.jsonl fields (git diff).
- `check.sh` exits 0, and the only validate warning is the expected one: pass. Evidence: I captured the exit code directly with `plugins/sdlc-lite/scripts/check.sh > /tmp/vchk.out 2>&1; echo $?`, which printed `check rc=0`. The run ended with "order selftest: PASS", "run selftest: PASS", "ok: shellcheck" and "ok: plugin validate". The builder's reported rc belonged to `tail`, so I did not use it. check.sh sends validate's output to /dev/null (check.sh:20), so I ran `claude plugin validate plugins/sdlc-lite` separately. It gives one warning, about the unquoted `${CLAUDE_PLUGIN_ROOT}` in `hooks.PreToolUse`, not the CLAUDE.md warning the handoff expected. Validating the same path in a throwaway worktree at HEAD gives the identical single warning, and `hooks/` is unchanged. So this step adds no warning. The handoff's "expected one about CLAUDE.md" wording is stale: this validator no longer emits that warning.

## Out of scope changes
- This step made one comment-only rewording each in `plugins/sdlc-lite/scripts/tickets.py` and `plugins/sdlc-lite/scripts/steps.py` ("never by mtime" became "never by file time"). The handoff did not list these files. The builder disclosed the edits, and without them criterion 1 fails. Everything else in the working tree comes from earlier steps of this task (run.sh, order.py, board.py, check.sh, and so on) and falls outside this step's review.

## For the next attempt
None
