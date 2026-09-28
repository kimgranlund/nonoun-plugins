<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0064: Merge-step conflict-marker guard skips empty merges and handles paths with spaces

## PR body
### Summary
The merge-step template has a conflict-marker guard criterion. When `git diff --name-only HEAD^1 HEAD` listed no paths, it ran `git grep` with an empty pathspec and scanned the whole tree. It also broke paths apart at spaces. Now it passes cleanly when the merge touched no files. It reads paths NUL-separated, so a name with a space stays one path. It still fails on a real marker in a touched file. A new check.py probe fails if either template copy goes back to the old form.

### Changes
- `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the same line is replaced in both files, and they stay identical. The fourth merge-step criterion is now:
  `git diff -z --name-only --diff-filter=d HEAD^1 HEAD | xargs -0 sh -c 'test $# -eq 0 || ! git grep -nE "^(<<<<<<<|>>>>>>>)( |$)" -- "$@"' sh`
  It keeps its `(guard)` tag, and the other four criteria are unchanged.
- `plugins/sdlc-lite/scripts/check.py`: new behavior probe. It pulls the guard span out of the planner template and runs it in a throwaway git repo against three cases:
  - an empty `--no-ff` merge with a legitimate `<<<<<<<` line in an untouched file must pass
  - a marker added to the touched file `sp ace.txt` must fail
  - a clean added file must pass

  Docstring item 6 is updated to match.
- `CLAUDE.md`: the "A merge is a standard builder step" Decisions bullet now says check.py runs the conflict-marker guard against a throwaway repo. `.claude/agents/sdlc-lite-author.md` did not need a change.

### Verification
- Step 1 (builder L1, verifier L1 Opus medium): pass.
  - The grep criteria went red at HEAD and green on the working tree.
  - `check.sh` exited 0.
  - Negative control: with only one template copy changed, `check.sh` failed with "block differs".
  - Runtime probe: an empty diff with a legitimate marker in an untouched file exited 0 (the old span exited 1). A marker in `a b.txt` exited 1. A clean touched file and a deleted file both exited 0.
- Step 2 (builder L2, verifier L1 Sonnet medium): pass.
  - `check.sh` exited 0 with no FAIL lines.
  - Negative control: the old templates from 192054c produced `empty merge flagged` and `marker in touched file not flagged`.
  - Negative control: an inverted guard produced `marker in touched file not flagged` and `clean merge flagged`.
  - The CLAUDE.md and docstring greps passed.

Nothing was committed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: the merge-step conflict-marker guard no longer scans the whole tree when a merge touched no files, and handles paths with spaces. `check.py` now runs the guard against a throwaway repo, so a template copy that goes back to the old form fails the check (T-0064).

## Follow-ups
- Merge-step conflict-marker guard still flags a line on the lane branch that legitimately starts with seven `<` or `>` in a touched file; restrict it to markers that git's merge left in the file, or document the false positive.
- Merge-step conflict-marker guard's xargs empty-input branch was checked only on macOS (BSD xargs); run the check.py probe under GNU xargs (Linux) to confirm the `test $# -eq 0` path.
