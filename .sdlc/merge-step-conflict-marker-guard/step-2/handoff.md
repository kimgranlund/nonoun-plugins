## Task goal
The merge-step template's conflict-marker guard criterion never scans the whole tree: when `git diff --name-only HEAD^1 HEAD` lists no paths, the check passes (nothing merged, nothing to scan) instead of running `git grep` with no pathspec, and it still fails when a touched file holds a real conflict marker line.

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
