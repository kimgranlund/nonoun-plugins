<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/fix/SKILL.md: step 2 now tells the conductor to add a `### Read first` subsection when the fixed file's nearest `AGENTS.md` is not the root. It follows the planner's rule and sits after `level:` and before `### Do`. The lint target `.sdlc/<slug>/step-1/handoff.md` is unchanged.
- plugins/sdlc-lite/skills/chain/SKILL.md: in section 5 step 3, the `Loose ends` step handoff now includes the same subsection for the files its items change.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: the step template now has `### Read first` and ``- `<path>` `` between `level: L<n>` and `### Do`. A new paragraph after the template says the subsection is optional, gives the nearest-entry rule with the root left out, and says `steps.py lint` refuses a missing path. The `merge-step` block is unchanged.

## Checks
- All 5 acceptance criteria ran from the repo root and each exited 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: ok, 18 role levels, 8 agents checked.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", exit 0.
- `git diff --check`: clean.

## Notes
`git diff --stat` also shows `docs/references/sdlc-internals.md` as changed. That change was already in the tree before this step, and this step did not touch the file.
