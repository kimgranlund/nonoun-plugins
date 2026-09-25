<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Change the merge-step conflict-marker guard so it only fails on marker lines that are new versus both merge parents, meaning lines `git diff-tree --cc` marks `++`. A lane-branch line that starts with seven `<` or `>` should then pass, and check.py's probe should prove both the new pass case and the new fail case.

## Step 1: Restrict the guard to merge-introduced markers and extend the check.py probe
level: L2
### Do
Restricting the guard is sound, so this step does not fall back to documenting the false positive. I tested the design in throwaway repos with a file name containing a space:
- It passes on an empty merge, on a lane line appended cleanly, on a lane line inside a file that both sides changed (shown as `+ ` in the combined diff), and on a non-merge HEAD.
- It fails on a kept real conflict and on a marker the merge commit itself added.
- It exits 128 outside a repo, so the check is not vacuous when git errors.

1. In `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, in the ```` ```merge-step ```` block, replace the span of the fourth criterion. The old span is the one starting `git diff -z --name-only --diff-filter=d HEAD^1 HEAD | xargs -0 ...`. The new line is:
   `- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"``
   - Keep the two blocks byte-identical.
   - Change no other line in either block.
   - The line still starts `- (guard) ` and contains `<<<<<<<`, so check.py's extraction still finds it.
2. In `plugins/sdlc-lite/scripts/check.py`, change the behavior probe (the block after `# Behavior probe:`). Update its comment and the module docstring item 6 if they describe the old behavior. The probe should hold these cases, each on the repo's `sp ace.txt` file where a file is touched:
   - **empty:** unchanged; must pass.
   - **marker:** keep the error text `marker in touched file not flagged`, but the marker must now be added by the merge commit itself: `merge --no-ff --no-commit <branch>`, append `>>>>>>> evil`, `add`, `commit`. Must fail.
   - **legit lane line:** a lane commit appends `>>>>>>> lane` to `sp ace.txt` and merges cleanly. Must pass. Error text: `merge-step conflict-marker guard: legit lane line flagged`.
   - **real conflict kept:** both sides change the same line of `sp ace.txt`, the merge conflicts, then `git add -A` and commit with the markers left in. Must fail. Error text: `merge-step conflict-marker guard: kept conflict markers not flagged`. The conflicting merge exits nonzero, so run it without `check=True`.
   - **clean:** unchanged; must pass.

   Reset main to `pre` between cases, as the probe already does.
### Acceptance criteria
- `grep -q 'git diff-tree --cc HEAD' plugins/sdlc-lite/agents/planner.md`
- `grep -q 'git diff-tree --cc HEAD' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `! grep -q 'xargs -0 sh -c' plugins/sdlc-lite/agents/planner.md`
- Negative control (old guard fails the legit case): `t=$(mktemp -d) && git archive 7e51f1b plugins/sdlc-lite | tar -x -C "$t" && git show 7e51f1b:CLAUDE.md > "$t/CLAUDE.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/plugins/sdlc-lite" | grep -q "legit lane line flagged"`
- Negative control for the kept-conflict case (observable): copy `plugins/sdlc-lite` and the repo `CLAUDE.md` into a temp dir in the same layout as the criterion above. In both merge-step blocks of the copy, replace the conflict-marker guard's span with `true "<<<<<<<"`. Running `python3 plugins/sdlc-lite/scripts/check.py <tmp>/plugins/sdlc-lite` must print a FAIL line containing `kept conflict markers not flagged`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/agents/builder.md`

## Step 2: Update the docs that describe the guard's criterion
level: L1
### Do
1. In the repo-root `CLAUDE.md`, in the "A merge is a standard builder step" decision, replace "no conflict markers in touched files" with wording that says the guard fails only on conflict-marker lines the merge itself added. Those are the lines `git diff-tree --cc` marks as new versus both parents, so a lane line that starts with seven `<` or `>` passes.
2. In `.claude/agents/sdlc-lite-author.md`, under `## Hazards learned`, add one line. It says the merge-step conflict-marker guard reads `git diff-tree --cc HEAD` (`++` lines only), so a lane's own marker-like lines pass. It also says the check.py probe holds the empty, marker, legit lane line, real conflict kept, and clean cases.
3. Use no em dashes.
### Acceptance criteria
- `! grep -q 'no conflict markers in touched files' CLAUDE.md`
- `grep -q 'diff-tree --cc' CLAUDE.md`
- `grep -q 'diff-tree --cc' .claude/agents/sdlc-lite-author.md`
- `! grep -n '—' CLAUDE.md .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- `steps.py split --only N` skips guard spans that contain `HEAD^1`. The new span has none, so it will now run on the pre-merge tree. That is green when HEAD is not a merge. It turns red only if the pre-merge HEAD is itself a merge commit that kept markers, which is arguably correct.
- A kept marker line that is textually identical to a line on either parent and aligns with it in the combined diff shows as `+ ` rather than `++`, so it would be missed. This is accepted as the lane-line trade-off the ticket hints at.
- The step 1 negative control pins commit `7e51f1b` (the current HEAD), so it stays valid even if a conductor commit moves HEAD between steps.
