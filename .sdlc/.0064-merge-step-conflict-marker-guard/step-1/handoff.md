## Task goal
The merge-step template's conflict-marker guard criterion never scans the whole tree: when `git diff --name-only HEAD^1 HEAD` lists no paths, the check passes (nothing merged, nothing to scan) instead of running `git grep` with no pathspec, and it still fails when a touched file holds a real conflict marker line.

## Step 1: Replace the conflict-marker guard in both merge-step template copies
level: L1
### Do
In `plugins/sdlc-lite/agents/planner.md` (`## Merge steps`, the fenced `merge-step` block) and `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (`### Merge step`, the fenced `merge-step` block), replace the fourth criterion line

`- (guard) ` + the span `! git grep -nE '^(<<<<<<<|>>>>>>>)( |$)' -- $(git diff --name-only HEAD^1 HEAD)`

with exactly this line in both files (byte-identical; check.py compares the blocks):

```
- (guard) `git diff -z --name-only --diff-filter=d HEAD^1 HEAD | xargs -0 sh -c 'test $# -eq 0 || ! git grep -nE "^(<<<<<<<|>>>>>>>)( |$)" -- "$@"' sh`
```

How it works: NUL-separated paths avoid word splitting, and `--diff-filter=d` drops deleted paths. An empty path list never reaches `git grep`: BSD xargs does not run the command, and GNU xargs runs it once with `$# -eq 0`. Either way the criterion exits 0. A marker hit makes the inner `sh` exit 1, so xargs exits 123 and the criterion fails. Leave the other four criteria and every other line of both blocks unchanged. Do not commit.
### Acceptance criteria
- `grep -qF -- '--diff-filter=d HEAD^1 HEAD | xargs -0 sh -c' plugins/sdlc-lite/agents/planner.md`
- `grep -qF -- '--diff-filter=d HEAD^1 HEAD | xargs -0 sh -c' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `! grep -qF -- '-- $(git diff --name-only HEAD^1 HEAD)' plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0. It confirms the two blocks are identical and pass `steps.py lint`, so the new span parses under `bash -n`.
