<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: `argument-hint` now includes `<lane>@<branch>=<ids>...`. Added a new paragraph on external lanes after the lanes-dir paragraph.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: added one sentence to the "Ids are allocated across worktrees" rule covering the `external_branch: <branch>` registration and the `check` warning.
- `docs/references/sdlc-internals.md`: the `tickets.py` entry now covers the registration line, what `id_floor` counts, and the `check` warning. The `fanout.py` entry's usage now includes `<lane>@<branch>=<id>[,<id>...]`, and the entry describes the external lane path: no worktree, no driver, branch never written, gates only when the merge made a commit, the refusals, and the dry-run and report lines.

## Checks
All six step criteria passed (each grep, and the `--lanes` count test against the base).
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0.
- `python3 scripts/check-packaging.py`: exit 0.
- `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: exit 0.
- Scope guard (`test -z ...`): exit 0.

## Notes
`SDLC_BASE_SHA` was taken from the step's `base-sha` file wherever the environment did not already set it. I took the wording of the refusals and the report line from the existing docstring in `fanout.py`.
