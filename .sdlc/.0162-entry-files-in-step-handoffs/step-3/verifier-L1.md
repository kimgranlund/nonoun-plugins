<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF '### Read first' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: exit 0. The diff adds the subsection to fix step 2 and keeps the lint target `.sdlc/<slug>/step-1/handoff.md`.
- `grep -qF '### Read first' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: exit 0. The diff adds it to section 5 step 3, after `level:` and before `### Do`.
- `grep -qF '### Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: exit 0.
- `grep -A2 -x 'level: L.n.' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qxF '### Read first'`: pass. Evidence: exit 0. The template now has `level: L<n>` followed directly by `### Read first`. The check can go red: at HEAD the handoff-format file has 0 occurrences of "Read first", so `grep` fails there. I did not run the pipeline at HEAD.
- `grep -F 'Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qi optional`: pass. Evidence: exit 0. The new paragraph reads "`### Read first` is optional…". It gives the nearest-entry rule with the root left out and says `steps.py lint` refuses a missing path. The `merge-step` block is unchanged in the diff.

I also ran `python3 plugins/sdlc-lite/scripts/check.py`. It printed "ok: 18 role levels, 8 agents checked".

## Out of scope changes
`docs/references/sdlc-internals.md` is modified in the tree, but this step did not call for it. The change adds the `### Read first` lint description to the `steps.py` entry. `git log` shows the file was last committed in a97ed40, before HEAD. I could not tie it to a specific earlier step. It matches the task goal and does not affect this step's criteria, so I am not counting it against the step.

## For the next attempt
None
