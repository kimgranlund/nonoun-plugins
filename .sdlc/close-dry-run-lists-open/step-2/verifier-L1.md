<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/file/SKILL.md`: pass. Evidence: in the tree, rc=0. In a throwaway worktree at HEAD, rc=1, so the check can go red. The diff adds the text to step 1.1 and to step 1.2's likely-duplicate comparison ("including the `(worktree <name>)` ones").
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/ticket/SKILL.md`: pass. Evidence: in the tree, rc=0. At HEAD, rc=1. The diff puts it in item 4's `--dry-run` sentence.
- `grep -qF '(worktree <name>)' CLAUDE.md`: pass. Evidence: in the tree, rc=0. At HEAD, rc=1. The diff puts it in the `scripts/tickets.py` Layout bullet's `close --dry-run` clause.
- `grep -qF '(worktree <name>)' .claude/agents/sdlc-lite-author.md`: pass. Evidence: in the tree, rc=0. At HEAD, rc=1. The diff puts it in the line 17 sync sentence: "the dry run's `open T-NNNN` listing (which includes other worktrees' open tickets as `(worktree <name>)`)".
- (guard) `grep -qF 'open T-NNNN' plugins/sdlc-lite/skills/file/SKILL.md`: pass. Evidence: rc=0. The diff keeps both the existing `open T-NNNN` and `likely duplicate of T-NNNN` strings.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran `check.sh > /tmp/chk-v2.out 2>&1; echo rc=$?` and got rc=0. The output ends with fanout, run, and hook selftest PASS, shellcheck ok, and plugin validate ok. This check.sh run captures the exit code directly, which the builder's own run did not.
- No em dashes added (`! git diff HEAD -- ... | grep '^+' | grep -q '—'`): pass. Evidence: rc=0. Positive control: `printf '+x — y\n' | grep '^+' | grep -q '—'` returns rc=0 (a hit), so the negated check would go red if an added line had an em dash.
- The docs match the code's output: pass. Evidence: the tickets.py diff builds lines as `f'open {i} {m.get("title", "")} [{x}] (worktree {wdir.name})'`. Its selftest expects `'open T-0004 Gamma [gamma] (worktree wtdr)'` after the local `'open T-0003 Delta [delta]'`. That matches "after the local lines", and the local-copy-decides rule matches the handoff scope.

## Out of scope changes
- `plugins/sdlc-lite/scripts/tickets.py`: this is step 1's code change, not part of this step. Checked: `step-1/verifier-L1.md` has verdict pass, and the diff is the worktree-listing code plus its selftest. Dismissed for this step.
- `.sdlc/close-dry-run-lists-open/handoff.md`: task-level goal and scope that the clarify step filled in (diff read: Goal, Scope, and Constraints sections only). Not project code. Dismissed.
- Untracked `.sdlc/close-dry-run-lists-open/{planner-L2.md,runs.jsonl,step-1/,step-2/}`: pipeline artifacts. Dismissed.

None of this step's doc edits touched other files: `git diff --stat` shows only the four named docs changed on this step's side.

## For the next attempt
None
