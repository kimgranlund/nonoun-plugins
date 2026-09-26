<!-- role=verifier level=L1 model=sonnet effort=medium -->
All criteria verified with evidence. The 8 non-guard greps pass green in the built tree and confirmed red at pre-build HEAD (throwaway worktree), so they bite. The guard `bash plugins/sdlc-lite/scripts/check.sh` exits 0 with all selftests, shellcheck, and plugin validate passing. Diff scope matches the Do exactly; files outside builder.md/check.sh/CLAUDE.md/sdlc-lite-author.md are step 1's own prior output, not introduced by this step.

## Verdict
pass

## Criteria
- `grep -qF block-repo-format.sh plugins/sdlc-lite/agents/builder.md`: pass. Evidence: command exits 0; red-control run in throwaway worktree at pre-build HEAD (`$SDLC_TMP_WORKTREES/base`) showed FAIL, confirming the check bites.
- `grep -qF 'files this step changed' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: command exits 0 (phrase pre-existed and is kept per builder.md diff, rule 6 line unchanged in that span).
- `grep -qF block-repo-format.sh plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: command exits 0; `git diff plugins/sdlc-lite/scripts/check.sh` shows the header comment now lists `block-repo-format.sh`.
- ``grep -qF '`hooks/block-repo-format.sh`: PreToolUse(Bash)' CLAUDE.md``: pass. Evidence: command exits 0; red at pre-build HEAD (FAIL in throwaway worktree), confirming bite.
- `grep -F 'Check everything' CLAUDE.md | grep -qF block-repo-format.sh`: pass. Evidence: command exits 0; `git diff CLAUDE.md` shows the Check-everything line's hook-selftest list now includes `block-repo-format.sh`.
- `grep -F 'must exit 0' .claude/agents/sdlc-lite-author.md | grep -qF block-repo-format.sh`: pass. Evidence: command exits 0; red at pre-build HEAD (FAIL in throwaway worktree), confirming bite.
- `grep -F 'Hazards' -A 40 .claude/agents/sdlc-lite-author.md | grep -qF block-repo-format.sh`: pass. Evidence: command exits 0; red at pre-build HEAD (FAIL in throwaway worktree); `git diff` shows a new Hazards line naming the hook.
- `! grep -qF '—' plugins/sdlc-lite/hooks/block-repo-format.sh`: pass. Evidence: command exits 0 (no em dash found); negative control confirmed grep detects a planted em dash in a scratch file, so the predicate can go red.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran in the built tree, exit 0, full log ends with "ok: shellcheck" and "ok: plugin validate", all selftests (steps, order, fanout, run, hook, hook live probe) report PASS.

## Out of scope changes
`plugins/sdlc-lite/hooks/hooks.json`, `plugins/sdlc-lite/scripts/hook-selftest.sh`, `plugins/sdlc-lite/hooks/block-repo-format.sh` (new file), and `.sdlc/formatter-rule-is-prompt-only/handoff.md` are modified/untracked but belong to step 1: `.sdlc/formatter-rule-is-prompt-only/step-1/builder-L3.md` and `verifier-L2.md` exist and record that step 1 already produced these files; step 2's Do only lists edits to builder.md, check.sh, CLAUDE.md, and sdlc-lite-author.md, and the diffs of those four files match the Do's items exactly with no extraneous edits.

## For the next attempt
None.
