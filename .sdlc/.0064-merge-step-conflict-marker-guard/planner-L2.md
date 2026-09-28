<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make the merge-step conflict-marker guard skip cleanly when the merge touched no files, stay NUL-safe for odd paths, and still fail on a real marker in a touched file, then prove that with a check.py probe that fails if either template copy regresses.

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

## Step 2: Probe the guard's behavior in check.py and update the records
level: L2
### Do
In `plugins/sdlc-lite/scripts/check.py`, after the existing merge-step `steps.py lint` block, add a behavior probe. Take the planner block `pb` that `merge_block` already read from `root`. Extract the criterion line that starts with `- (guard) ` and contains `<<<<<<<`, and take the text between its first and last backtick. Then, in a `tempfile.mkdtemp()` throwaway git repo (removed afterward), do the following:
- Run git with `-c user.name=t -c user.email=t@t` or equivalent env, and use `init -b main`.
- Base commit: `untouched.txt` holds the line `<<<<<<< legit fixture`, and `sp ace.txt` holds `a`.
- Case 1: merge a branch with only an empty commit, using `--no-ff`. The span, run with `bash -c`, must exit 0 (empty path list: no whole-tree scan).
- Case 2: from HEAD^1, a branch appends `>>>>>>> lane` to `sp ace.txt`, and a `--no-ff` merge follows. The span must exit non-zero (marker in a touched file whose name has a space).
- Case 3: reset main to before case 2, then merge a branch that adds a clean `ok file.txt` with `--no-ff`. The span must exit 0.

Each wrong result appends an error whose text contains `conflict-marker guard` and names the case, e.g. `merge-step conflict-marker guard: empty merge flagged`. A missing criterion line is also an error containing `conflict-marker guard`.

Update the module docstring item 6 to say check.py also runs the conflict-marker guard against a throwaway repo. In the repo-root `CLAUDE.md` Decisions bullet "A merge is a standard builder step", change the last sentence so it says `check.py` keeps the two copies identical and lint-clean, runs their conflict-marker guard against a throwaway repo, and keeps them in step with builder.md. Also add "conflict-marker guard" to that sentence. `.claude/agents/sdlc-lite-author.md` stays accurate as written. Do not commit.
### Acceptance criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0 on the tree after the step. The real templates pass all three cases.
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && cp CLAUDE.md "$d/p/CLAUDE.md" && git show 192054c:plugins/sdlc-lite/agents/planner.md > "$d/p/agents/planner.md" && git show 192054c:plugins/sdlc-lite/skills/handoff-format/SKILL.md > "$d/p/skills/handoff-format/SKILL.md" && python3 "$d/p/scripts/check.py" "$d/p" | grep -q "conflict-marker guard"` (negative control: the old whole-tree form is flagged)
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && cp CLAUDE.md "$d/p/CLAUDE.md" && perl -pi -e 's/\|\| ! git grep/|| git grep/' "$d/p/agents/planner.md" "$d/p/skills/handoff-format/SKILL.md" && python3 "$d/p/scripts/check.py" "$d/p" | grep -q "conflict-marker guard"` (negative control: an inverted guard is flagged)
- `grep -q "conflict-marker guard" CLAUDE.md`
- `sed -n 6,14p plugins/sdlc-lite/scripts/check.py | grep -q "conflict-marker guard"`

## Risks
- xargs behavior differs by platform. BSD skips the command on empty input and GNU runs it once with no args. The `test $# -eq 0` branch covers both. I checked on macOS only, under both bash and zsh, with a throwaway-repo probe.
- If `HEAD^1` is missing, `git diff` fails, the pipeline sees an empty list, and the guard passes. The two-parent criterion in the same template still fails in that case, so I did not add `pipefail`.
- The regex still flags a line added on the lane branch that legitimately starts with seven `<` or `>` in a touched file. The goal does not ask to change that.
- The step 2 negative controls pin commit `192054c` for the old template text. They stay valid only while that commit exists, which holds unless history is rewritten.
- The step 2 negative controls copy the plugin plus `CLAUDE.md` into a temp dir. A copy with the current tree passes check.py (verified), so those criteria turn green only when the new probe emits its error.
