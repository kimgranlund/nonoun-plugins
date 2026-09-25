## Task goal
Merging two lanes is a standard builder step with criteria it can meet.

## Step 2: Guard the template in check.py
level: L2
### Do
Add a check to `plugins/sdlc-lite/scripts/check.py`, next to the plan-defect route checks, and add a line for it to the module docstring. The check does five things:
1. It extracts the fenced `merge-step` block from `agents/planner.md` and from `skills/handoff-format/SKILL.md`. Each block runs from the fence line that is three backticks plus `merge-step` to the next line that is exactly three backticks.
2. It fails if either block is missing or empty, or if the two blocks differ.
3. It replaces `<n>` with `1`, writes the planner block to `planner-L2.md` in a temp dir, and runs `python3 <root>/scripts/steps.py lint` on that file. It fails on a nonzero exit, and the error message includes the lint's stderr.
4. It fails if `agents/builder.md` lacks `git merge --no-ff`.
5. It removes the temp dir.

Every failure goes into `errors` with the same `FAIL` output format the file already uses.
### Acceptance criteria
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/merge-base --is-ancestor/merge-base/' "$d/a/p/skills/handoff-format/SKILL.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0. The two blocks now differ, so check.py fails.
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/wc -w\)/wc -w/' "$d/a/p/agents/planner.md" "$d/a/p/skills/handoff-format/SKILL.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0. The blocks are still identical but no longer parse, so the lint fails.
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/git merge --no-ff/git merge/g' "$d/a/p/agents/builder.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0 on the real tree.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. (guard)
