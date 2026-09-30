<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -E '^5\. ' plugins/sdlc-lite/skills/fix/SKILL.md | grep -q 'Unattended'`: pass. Evidence: exit 0 on the built tree. The `git diff` shows the new text on the `5. ` line.
- `grep -E '^5\. ' plugins/sdlc-lite/skills/fix/SKILL.md | grep -q 'never push'`: pass. Evidence: exit 0 on the built tree.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: on the built tree it printed "ok: 18 role levels, 8 agents checked". Applying the new check.py to the old SKILL.md at the pre-build HEAD (a throwaway worktree) printed "FAIL skills/fix/SKILL.md: step 5 lacks the Unattended rule with "never push"", so the new check goes red on the old text. The check also carries a built-in negative control (`check.py` diff, `fxt.replace('never push','push')`), which also passes on the built tree.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified".

The wording matches `/chain` section 7's Unattended bullet, `chain/SKILL.md` line 62. It covers no AskUserQuestion, no push or pull request, a local commit at most, and a report listing what is waiting. The interactive rule is unchanged, since the diff only appends to the `5. ` line.

## Out of scope changes
The `.sdlc/0162-*` deletions and modifications, plus `.sdlc/0168-unattended-publish/handoff.md`, are outside the step. The builder's notes say it did not touch them. They are task-folder bookkeeping outside `plugins/`, and the step's `git diff` for `plugins/` shows only `check.py` and `fix/SKILL.md`. I dismissed them as harmless on that basis.

## For the next attempt
None
