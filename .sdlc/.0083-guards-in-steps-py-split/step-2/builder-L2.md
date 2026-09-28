<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- CLAUDE.md: the steps.py Layout bullet, the Systems code-gates line, and the Decisions plan-defect bullet now describe the guard that changed the work tree.
- .claude/agents/sdlc-lite-author.md: the Plan-defect route bullet now includes a guard that changed the work tree.
- plugins/sdlc-lite/skills/chain/SKILL.md: the section 3 and 4.2 text on `--only N` now covers a red guard or a guard that changed the work tree.
- plugins/sdlc-lite/agents/planner.md: rule 1 gains one sentence saying guards must be side-effect free. The merge-step block is untouched.
- plugins/sdlc-lite/scripts/check.py: added the `'changed the work tree'` entry to `PLAN_DEFECT_DOCS`.

## Checks
- The four `grep -q "changed the work tree"` doc checks: all found the phrase.
- `grep -q "'changed the work tree'" plugins/sdlc-lite/scripts/check.py`: found.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n1 | grep -qx 'steps selftest: PASS'`: pass.
- `test -z "$(git status --porcelain --untracked-files=all -- plugins/sdlc-lite/skills/handoff-format)"`: pass.

## Notes
None
