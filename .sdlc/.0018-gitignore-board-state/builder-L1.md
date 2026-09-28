<!-- role=builder level=L1 model=sonnet effort=low -->
Pre-existing change from ticket creation, not made by me. This matches acceptance criteria "lists only the skill file and this ticket folder."

## Status
done

## Changes
plugins/sdlc-lite/skills/handoff-format/SKILL.md: added a fenced .gitignore block with one-line explanations for `.sdlc/.board-state.json`, `.sdlc/**/*.running`, `.sdlc/**/*.log`.

## Checks
- Scratch repo `git check-ignore` test with the new block: `.sdlc/.board-state.json`, `.sdlc/t/builder-L1.running`, `.sdlc/t/builder-L1.log` ignored; `.sdlc/t/builder-L1.md`, `.sdlc/t/runs.jsonl`, `.sdlc/t/handoff.md` not ignored. Passed.
- `plugins/sdlc-lite/scripts/check.sh`: passed (exit 0, all sub-checks ok/PASS).
- `git diff --stat`: lists only `plugins/sdlc-lite/skills/handoff-format/SKILL.md` and `.sdlc/0018-gitignore-board-state/handoff.md` (the ticket folder, pre-existing from ticket creation, not touched by me).

## Notes
None
