<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/handoff-format/run-operations.md: added the `## Run a role from a temporary worktree` section. It covers when to use it, a 5-step numbered recipe, a fenced `sh` block, where results land, how to commit builder edits on a named branch, removal without `--force`, why `SDLC_TMP_WORKTREES` is not reused, and that fanout is out of scope.
- plugins/sdlc-lite/skills/chain/SKILL.md: the sentence linking shared run operations now also names `Run a role from a temporary worktree`.

## Checks
- All seven grep criteria, chained with `&&`: printed ALLOK, so every one passed.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", rc=0. There was no drift, so I did not run generate.
- `git diff --check`: clean.
- Prose criterion: I read the new section myself. It has one paragraph each for results and `runs.jsonl` landing next to the absolute handoff path in the home `.sdlc/<task>/`, for committing on a named branch before removal or losing the edits, and for removal with no `--force` that touches only the recipe's own worktree.

## Notes
My first attempt used a heredoc containing the worktree-add text, and `block-stray-worktree.sh` denied it. No change was applied then. The section was then written with the Edit tool. `fanout.py` is unchanged.
