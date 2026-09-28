<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Keep the current `++`-only merge-step conflict-marker guard and document its known miss as an accepted limitation. Two new check.py probe cases pin that choice: a legit lane line in a file both sides changed must pass, and an aligned kept marker must pass as the documented miss.

Decision record (the handoff's unattended decision rule): I took the **document** branch. I tested it in throwaway repos. When `sp ace.txt` holds a `>>>>>>> aligned` line on the base, both sides change the line above it, and the merge conflicts, the result can keep git's `>>>>>>> aligned` marker while `<<<<<<<` and `=======` are stripped. In that case `git diff-tree --cc HEAD` shows the kept marker lines only as `+ ` and ` +`, and the current guard passes (rc 0). A guard that also flags `+ `/` +` (`^(\+\+|\+ | \+)(<<<<<<<|>>>>>>>)( |$)`) catches it and still passes all five existing probe cases. That is only because the existing legit case touches a file only one side changed, which `--cc` omits. The same guard flags a legit lane line (`+ >>>>>>> lane`) in a file both sides changed cleanly. That is exactly the T-0069 false positive (its plan names this case). The two cases produce the same diff marks, so no line-mark guard can tell them apart. The only remaining signal is per-file marker counts across HEAD, both parents, and the merge base. That needs a loop over NUL-separated names, rename handling, and a pre-merge fallback, which fails rule (c) (one lint-clean line) and rule (d) (readable). So rules (a) to (d) cannot all hold, and the limitation gets documented and pinned instead.

## Step 1: Pin the both-sides legit case and the aligned-marker miss in the check.py probe
level: L2
### Do
Edit only `plugins/sdlc-lite/scripts/check.py`, in the behavior probe block (after `# Behavior probe:`, before the `except subprocess.CalledProcessError`). Add two cases after the existing kept-conflict case. Each case starts with `g('reset', '-q', '--hard', pre)`, the same way the existing cases do. Keep every existing case and its error text unchanged.

1. **Both-sides legit lane line** (must pass the guard):
   - From `pre`, run `g('checkout', '-qb', 'both', pre)`.
   - Write `sp ace.txt` = `a\n>>>>>>> lane\n` and commit.
   - Back on main, reset to `pre`. Write `sp ace.txt` = `top\na\n` and commit.
   - Run `g('merge', '-q', '--no-ff', '-m', 'merge both', 'both')`. This merges cleanly and `--cc` shows `+ >>>>>>> lane`.
   - If `span_rc() != 0`, append the error `merge-step conflict-marker guard: both-sides legit lane line flagged`.
2. **Aligned kept marker, documented miss** (the guard must pass, which pins the accepted limitation):
   - From `pre` on main, write `sp ace.txt` = `a\n>>>>>>> aligned\n` and commit. Save that HEAD as `b2`.
   - Run `g('checkout', '-qb', 'aligned', b2)`. Write `lane\n>>>>>>> aligned\n` and commit.
   - Back on main, reset to `b2`. Write `main\n>>>>>>> aligned\n` and commit.
   - Run `gr('merge', '-q', '--no-ff', 'aligned')`. It conflicts, so run it without `check=True`.
   - Rewrite `sp ace.txt` without the lines that start with `<<<<<<<` or `=======`. Keep the kept `>>>>>>> aligned` marker. Then `g('add', '-A')` and commit.
   - The marker text must equal the branch name `aligned`, so git's marker matches the parent line.
   - If `span_rc() != 0`, append the error `merge-step conflict-marker guard: aligned kept marker flagged; the documented limitation changed, update the merge-step docs`.
3. Update the probe comment above the block and module docstring item 6 so they name all seven cases. Add one sentence that the aligned-marker case pins a known miss: a kept marker textually identical to a parent line that aligns with it shows as `+ ` or ` +`, not `++`. Use no em dashes.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite/agents plugins/sdlc-lite/skills plugins/sdlc-lite/scripts CLAUDE.md "$d"/ && python3 -c 'import pathlib,sys; [p.write_text(p.read_text().replace("^\\+\\+(<", "^(\\+\\+|\\+ | \\+)(<")) for p in map(pathlib.Path, sys.argv[1:])]' "$d/agents/planner.md" "$d/skills/handoff-format/SKILL.md" && python3 "$d/scripts/check.py" "$d" | grep -q "aligned kept marker flagged"`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite/agents plugins/sdlc-lite/skills plugins/sdlc-lite/scripts CLAUDE.md "$d"/ && python3 -c 'import pathlib,sys; [p.write_text(p.read_text().replace("^\\+\\+(<", "^(\\+\\+|\\+ | \\+)(<")) for p in map(pathlib.Path, sys.argv[1:])]' "$d/agents/planner.md" "$d/skills/handoff-format/SKILL.md" && python3 "$d/scripts/check.py" "$d" | grep -q "both-sides legit lane line flagged"`
- (guard) `grep -qF 'grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"' plugins/sdlc-lite/agents/planner.md`
- (guard) `! grep -n '—' plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Step 2: Document the accepted limitation next to the template and in the repo docs
level: L1
### Do
Add one sentence (or a short clause) containing the exact phrase `textually identical to a parent line` to each file below. Leave the fenced ```` ```merge-step ```` blocks byte-for-byte unchanged, and use no em dashes.
1. `plugins/sdlc-lite/agents/planner.md`, `## Merge steps`, in prose outside the fenced block (for example after the "Criterion 1 above still applies" paragraph). Say the conflict-marker guard flags only `++` lines of `git diff-tree --cc HEAD`, so a kept marker line textually identical to a parent line that aligns with it (shown as `+ ` or ` +`) passes. This is accepted, because no one-line guard separates it from a legit lane line in a file both sides changed. The builder must still resolve every conflict, and the check.py probe pins the miss.
2. `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, `### Merge step`, in prose after the fenced block. Add the same limitation sentence.
3. Repo-root `CLAUDE.md`, the "A merge is a standard builder step" decision. After the diff-tree clause, add that a kept marker line textually identical to a parent line and aligned with it passes. This is an accepted limitation that the check.py probe pins.
4. `.claude/agents/sdlc-lite-author.md`, the hazard line about the conflict-marker guard. Change the probe case list to the seven cases (empty, marker, legit lane line, both-sides legit lane line, real conflict kept, aligned kept marker as the documented miss, clean). Add that a kept marker textually identical to a parent line passes by design.
### Acceptance criteria
- `grep -q "textually identical to a parent line" plugins/sdlc-lite/agents/planner.md`
- `grep -q "textually identical to a parent line" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -q "textually identical to a parent line" CLAUDE.md`
- `grep -q "textually identical to a parent line" .claude/agents/sdlc-lite-author.md`
- `grep -q "aligned kept marker" .claude/agents/sdlc-lite-author.md`
- (guard) `diff <(git show HEAD:plugins/sdlc-lite/agents/planner.md | awk '/^...merge-step$/,/^...$/') <(awk '/^...merge-step$/,/^...$/' plugins/sdlc-lite/agents/planner.md)`
- (guard) `diff <(git show HEAD:plugins/sdlc-lite/skills/handoff-format/SKILL.md | awk '/^...merge-step$/,/^...$/') <(awk '/^...merge-step$/,/^...$/' plugins/sdlc-lite/skills/handoff-format/SKILL.md)`
- (guard) `! grep -n '—' CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- The aligned-marker case depends on git's merge output (the marker text is `>>>>>>> <branch name>`) and on the pairwise alignment Myers produces. A future git version could align the marker differently and show it as `++`. The new case would then fail with its "documented limitation changed" message. That is the intended signal, but it may look like a regression.
- Step 2's block-unchanged guards compare against `HEAD`. If a conductor wip commit lands after step 2's edits but before verification, they compare against the edited tree and still pass. They only catch block edits that are uncommitted.
- The mutated-guard criteria in step 1 copy `agents`, `skills`, `scripts`, and `CLAUDE.md` into a temp dir. A future check.py check that reads other plugin paths would add unrelated FAIL lines there, but the criteria grep only for the new messages.
