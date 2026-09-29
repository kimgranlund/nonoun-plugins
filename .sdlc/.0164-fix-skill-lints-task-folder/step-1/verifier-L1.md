<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qE 'steps\.py lint \.sdlc/.slug./step-1/handoff\.md' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: the grep exited 0. The diff shows `fix/SKILL.md` step 2 now has `steps.py lint .sdlc/<slug>/step-1/handoff.md`.
- `grep -q 'step-1/handoff.md' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: the grep exited 0. The new `fix_lint_bad` guard in `check.py` contains that string.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: it printed `ok: 18 role levels, 8 agents checked` and exited 0.
  - The check can go red. I copied the new `check.py` into a throwaway worktree at HEAD, where `fix/SKILL.md` still has the old text. It printed `FAIL skills/fix/SKILL.md: steps.py lint target is not .sdlc/<slug>/step-1/handoff.md`. The exit code printed empty because of my `PIPESTATUS` use in zsh, but the FAIL line shows the check fired.
  - The check also has a built-in negative control: it strips `/step-1/handoff.md` from the text and requires the guard to flag it.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: it printed `Codex agent definitions verified` and exited 0.
- Behavior extra: `steps.py lint .sdlc/0164-fix-skill-lints-task-folder/step-1/handoff.md` printed `steps lint: ok` and exited 0. This is the documented command form run on a real handwritten step handoff.

Steelman: I drafted a fail that the regex `steps\.py lint (\S+?)` needs a closing backtick. The builder would answer that the SKILL text puts the command in backticks and the guard requires at least one match. The negative control shows it flags the old text, so I dropped the finding.

## Out of scope changes
None. `git diff --stat` shows only `check.py` (+8) and `fix/SKILL.md` (1 line). The other change is the untracked `.sdlc/0164-fix-skill-lints-task-folder/step-1/` task folder.

## For the next attempt
None
