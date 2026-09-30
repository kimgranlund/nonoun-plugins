<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF "Other plugins' agents are not substitutes" plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: the grep matched. The `git diff` shows the new bullet, word for word, directly after the first "How you run roles" bullet. The Agent-tool spawn bullet now begins "Every other Agent-tool spawn, such as a read-only search helper, states `model`".
- `grep -qF "not substitutes" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: the grep matched. The diff adds `SUBST_PHRASE`, `subst_missing`, the error append, and a negative control that strips the phrase and requires the guard to flag it. The style matches `fix_lint_bad`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: on the built tree it printed `ok: 18 role levels, 8 agents checked`. I also copied the new `check.py` into a throwaway worktree at HEAD, where `conductor.md` still has the old text. There it printed `FAIL agents/conductor.md: run.sh-only rule missing "Other plugins' agents are not substitutes"` and `FAIL: 18 role levels, 8 agents checked`. The check goes red on the old text and green on the new. The `0` after that run is `tail`'s exit code, not `check.py`'s. The FAIL lines are the evidence.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: it printed `Codex agent definitions verified`. `sdlc-conductor-l1.toml` shows as changed in the diff, so it was regenerated.

## Out of scope changes
- `.sdlc/0160-repo-onboarding-skill/handoff.md` and `docs/repo-onboarding/design.md` show as modified. The builder says they were dirty before this step.
- I did not diff them against the base, so I can't independently confirm that. The step touches neither, and the diff of the step's own files shows nothing from them.
- No other changes beyond the three files the step named.

## For the next attempt
None
