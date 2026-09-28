<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `! grep -qF 'worktree add <tmp>' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: prints c1 PASS on the built tree and c1 FAIL in a detached worktree at HEAD 219fb23, so the check can go red. The file exists, so the negation is not vacuous. The diff replaces all four occurrences (rules 3, 8, 11 and the merge-step block).
- `! grep -qF 'worktree add <tmp>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: c2 PASS on the tree, c2 FAIL at HEAD.
- `grep -qF 'git worktree add --detach <tmp> HEAD^1' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: c3 PASS on the tree, c3 FAIL at HEAD.
- `grep -qF 'git worktree add --detach <tmp> HEAD^1' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: c4 PASS on the tree, c4 FAIL at HEAD. The two merge-step blocks, extracted with sed and compared with `cmp`, are identical, and `python3 plugins/sdlc-lite/scripts/check.py` exits 0 (`ok: 18 role levels, 8 agents checked`).
- `for f in CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md; do grep -q 'without .--detach' "$f" || exit 1; done`: pass. Evidence: c5 PASS on the tree, c5 FAIL at HEAD. The diff adds "any add without `--detach`" to builder.md rule 5, verifier.md rule 3 and the sdlc-lite-author.md hazard line. In the CLAUDE.md bullet it adds "without `--detach`/`-d` (because git can otherwise create a branch, a remote-only name becomes a tracking branch, or check one out)".
- `grep -qF 'git worktree add --detach "$SDLC_TMP_WORKTREES/<name>"' plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: c6 PASS on the tree, c6 FAIL at HEAD. The diff changes only the header comment line.
- The Do says no em dashes: `git diff | grep '^+' | grep -c '—'` gives 0.

## Out of scope changes
`git status` also shows changes to `plugins/sdlc-lite/hooks/block-stray-worktree.sh`, `plugins/sdlc-lite/scripts/hook-selftest.sh` and `.sdlc/0130-git-worktree-add-path-name/handoff.md`, plus untracked task artifacts. This step's Do does not list those three files. They belong to step 1 (the hook change and its fixtures) and the task handoff, and the builder says they were already present. The hook change is live in this session: it denied my first command, which contained a `bash -c` word, as unparseable. So it predates this step's edits and does not come from this step. No other files changed. None beyond those.

## For the next attempt
None
