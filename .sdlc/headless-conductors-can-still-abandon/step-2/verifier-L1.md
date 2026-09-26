<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep 'hooks/block-background.sh' CLAUDE.md | grep -q Agent`: pass. Evidence: the command exits 0 in the tree. It is RED against HEAD (`git show HEAD:CLAUDE.md | grep ... | grep -q Agent` fails), so the check can fail. The diff shows CLAUDE.md:24 now reads `PreToolUse(Bash, Agent) hook` and adds the Agent rule.
- `! grep 'hooks/block-background.sh' CLAUDE.md | grep -q 'PreToolUse(Bash)'`: pass. Evidence: exits 0 in the tree and is RED against HEAD. The block-publish bullet still reads `PreToolUse(Bash)` but has no `hooks/block-background.sh` string, so it cannot trip this check.
- conductor.md `grep 'block-background' ... | grep -q Agent`: pass. Evidence: exits 0 in the tree, RED against HEAD.
- chain/SKILL.md, same check: pass. Evidence: exits 0 in the tree, RED against HEAD.
- bench/SKILL.md, same check: pass. Evidence: exits 0 in the tree, RED against HEAD.
- fanout/SKILL.md, same check: pass. Evidence: exits 0 in the tree, RED against HEAD.
- .claude/agents/sdlc-lite-author.md, same check: pass. Evidence: exits 0 in the tree, RED against HEAD.
- scripts/bench.sh, same check: pass. Evidence: exits 0 in the tree, RED against HEAD. The diff changes the comment at line 7 to "denies Bash and Agent run_in_background".
- scripts/fanout.py, same check: pass. Evidence: exits 0 in the tree, RED against HEAD. The diff changes the docstring at line 36.
- (guard) no em dash in added lines: pass. Evidence: the full command exits 0 in the tree. The predicate does go red on an added em dash: `printf '+foo — bar\n' | grep '^+' | grep -q '—'` matched, so the negated form was RED.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh >/dev/null 2>&1; echo exit=$?` printed `exit=0`. The output tail shows the order, fanout, run, and hook selftests PASS, plus `ok: shellcheck` and `ok: plugin validate`. So the check.py word requirements (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`) still hold in chain, bench, fanout, and conductor. The builder said it did not see check.sh's own exit code, so I ran it myself.

Other checks:
- `grep -rln block-background` outside .git and .sdlc finds two hits with no "Agent": hooks.json and check.sh:5. hooks.json is config, not a description, and was step 1's scope. check.sh:5 reads "(block-background.sh and block-publish.sh on fixture JSON)" and does not call the hook Bash-only. The handoff's file list does not name either one, so I raised no finding.
- The Do section says to keep all other wording. Reading the diff, each changed line alters only the hook clause and leaves the rest as it was.

## Out of scope changes
None attributable to this step. The step 1 files are also modified in the working tree: `plugins/sdlc-lite/hooks/block-background.sh`, `plugins/sdlc-lite/hooks/hooks.json`, and `plugins/sdlc-lite/scripts/hook-selftest.sh`. `step-1/handoff.md` lines 4 to 13 name them, and `step-1/verifier-L1.md` has verdict pass. The task `handoff.md` diff fills in the Goal, Intent, and Constraints (the planner/clarify stage), not step 2 build work.

## For the next attempt
None
