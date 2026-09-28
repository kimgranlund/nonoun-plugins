<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- Docstring holds `wip(<id>): <outcome>`: pass. Evidence: the `python3 -c 'import ast...'` span gives rc=0 on the built tree and rc=1 in a throwaway worktree at HEAD, so the check can go red. The text is at fanout.py:47-50. It replaces "the tree left as is" and names the `wip <sha>` Commit cell and the WIP commit before each sync.
- `grep -qF 'wip(<id>): <outcome>' plugins/sdlc-lite/skills/fanout/SKILL.md`: pass. Evidence: rc=0 built, rc=1 at HEAD. The sentence is at SKILL.md:9 and includes "inspect a stopped lane's `wip(` commit on its lane branch".
- `grep -qF 'wip(<id>)' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: rc=0 built, rc=1 at HEAD. The new line 24 covers both parts: under fanout the commit lands on the lane branch, and a plain /chain commits nothing and never commits on main.
- `grep -qF 'wip(<id>): <outcome>' CLAUDE.md`: pass. Evidence: rc=0 built, rc=1 at HEAD. The fanout.py Layout bullet now names the lane commit on a stop and before a dirty sync, says it is never merged, and says its sha shows in the report.
- `! git diff HEAD -- ... | grep -q '^+.*—'`: pass. Evidence: rc=0 built, and the un-negated grep prints nothing. In the HEAD worktree I appended the fixture line `x — y` to CLAUDE.md, and the criterion gave rc=1, so it bites.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: "fanout selftest: PASS" and rc=0 on the built tree. In the HEAD worktree I planted a miss (`misses.append('planted')`) and it went red: "FAIL, these did not hold: ... planted", exit code 1.
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: a full run on the built tree gave `check.sh rc=0`, ending with "fanout selftest: PASS ... ok: shellcheck, ok: plugin validate". It can go red because it includes the fanout selftest, which went red on the planted miss above.

## Out of scope changes
None. I checked each changed file:
- The code diff in `plugins/sdlc-lite/scripts/fanout.py` (`wip_commit`, `run_ticket`/`run_lane` wiring, selftest case 4) is Step 1's uncommitted work in the same tree. The task handoff's Do calls for it, and the fanout selftest passes with it.
- `.sdlc/0126-chain-stop-leaves-dirty-tree/handoff.md` gains a `## Intent` section. I read the diff: it is task-artifact bookkeeping from /clarify, not project code.
- `.claude/agents/sdlc-lite-author.md` was left alone. `grep -n 'stop\|wip'` finds no restatement of fanout stop behavior (the only hit, line 32, is about pattern kills), so the builder's claim holds.

## For the next attempt
None.
