<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/fix/SKILL.md: in step 2, the lint command now targets `.sdlc/<slug>/step-1/handoff.md` instead of `.sdlc/<slug>`.
- plugins/sdlc-lite/scripts/check.py: added the `fix_lint_bad` contract check. It fails when a `steps.py lint` target in skills/fix/SKILL.md is missing or does not end in `/step-1/handoff.md`. It also has a built-in negative control, like the checks next to it.

## Checks
- `grep -qE 'steps\.py lint \.sdlc/.slug./step-1/handoff\.md' plugins/sdlc-lite/skills/fix/SKILL.md`: pass.
- `grep -q 'step-1/handoff.md' plugins/sdlc-lite/scripts/check.py`: pass.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0, "ok: 18 role levels, 8 agents checked".
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 0, "Codex agent definitions verified". No regeneration was needed.
- Negative control: copied the plugin to `$SDLC_TMP_WORKTREES/negfix` and restored the HEAD (old) fix/SKILL.md there. `check.py <copy>` gave rc 1 with "FAIL skills/fix/SKILL.md: steps.py lint target is not .sdlc/<slug>/step-1/handoff.md". The copy was then removed.

## Notes
None
