<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'exits 3' CLAUDE.md`: pass. Evidence: returns 0 in the tree. In a throwaway worktree at HEAD it returns 1, so the check can go red. The matching text is the new run.sh Layout bullet: "it exits 3 and names the section when missing; the result file and `runs.jsonl` line are kept". That text matches the code: `git diff plugins/sdlc-lite/scripts/run.sh` shows `exit 3` and the header "3 result lacks its section".
- `grep -q 'exits 3' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: returns 0 in the tree and 1 at HEAD. The matching text is in step 4: "`run.sh` exits 3 when the result lacks its required section; the result file still exists, so run `steps.py next` as usual."
- `grep -q 'exit 3' plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: returns 0 in the tree and 1 at HEAD. The diff adds one line under "How you run roles": "A `run.sh` exit 3 means the role ended without its required section; it goes through `steps.py next`, never to done."
- `! grep -q 'a Stop hook that checks result format' CLAUDE.md`: pass. Evidence: returns 0 in the tree and 1 at HEAD, where the phrase was present. `test -f CLAUDE.md` returns 0, so the file exists and the negated grep really read it.
- `grep -q 'Bash write guard for read-only roles' CLAUDE.md`: pass. Evidence: returns 0 in the tree and 0 at HEAD. This is a preservation check, so being green at HEAD is expected. It goes red only if the item is deleted. The diff of the Later line removes only "a Stop hook that checks result format;" and keeps the other three items.
- `grep -q 'no done/blocked' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: returns 0 in the tree and 1 at HEAD. The new rule 6 reads: "A builder result with no done/blocked `## Status`: `steps.py next` prints `rebuild` at the same level. It is never a fail and never a bump, and a second in a row → stop and ask the user." It matches the code. The steps.py diff adds `build_status_or_none`, which maps this case to `rebuild L<level>` and, when two statusless builder results come in a row, to `stop`. Selftest cases cover both: "next rebuild: a builder with no done/blocked Status -> rebuild L2" and "next stop: two consecutive builders with no Status -> stop".
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it in the tree and it exited 0. The tail shows `order selftest: PASS`, `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`. Every "fail" line in the output is an `ok:` test name.
- Do item for the CLAUDE.md `steps.py next` description: pass. Evidence: the diff removes "or builder result" from the exit-1 cases. It adds: "a builder result with no done/blocked Status is not an error: it maps to `rebuild` at its level, and two in a row map to `stop`".
- Do item for `.claude/agents/sdlc-lite-author.md` (conditional): accepted as left unchanged. Evidence: `grep -n 'run.sh'` on that file hits only lines 12 and 13 (headless launch and level tables), so it says nothing about run.sh exit codes. Line 19 does describe one `steps.py next` rule, the verifier no-verdict route.
  - Draft fail: the builder skipped the sync line.
  - Steelman: the handoff says to add the line "only if it already describes run.sh exit codes or the `next` rules". The file has no exit-code text, and line 19 covers only the verifier route. No criterion checks this file.
  - Result: dropped as a fail. A follow-up could extend line 19 to cover the builder no-Status route, which would keep it in sync with CLAUDE.md.

## Out of scope changes
None. `git status` also shows `plugins/sdlc-lite/scripts/run.sh`, `run-selftest.sh` and `steps.py` as modified. Grepping `step-1/handoff.md` and `step-2/handoff.md` shows those files belong to steps 1 and 2. Both steps' `verifier-L1.md` files report `## Verdict pass`. The untracked `.sdlc/run-result-format-check/` files are this task's run artifacts.

## For the next attempt
None
