## Task goal
The merge-step conflict-marker guard's known gap (a kept conflict-marker line textually identical to a parent line, shown as `+ ` or ` +` in `git diff-tree --cc`, not `++`) is either closed or explicitly documented as an accepted limitation, and check.py's behavior probe has a case that pins whichever outcome is chosen.

Decision rule (unattended, no user present): close the gap if a guard exists that (a) flags this new case, (b) still passes all five existing probe cases, especially the legit lane line case, (c) stays one lint-clean criterion line that parses under `bash -n` and has no `||` between checks, and (d) stays readable. If no such guard exists, keep the current guard, add the probe case asserting the documented miss (so a future change is noticed), and record the limitation in the template's surrounding docs and CLAUDE.md. The planner records which branch it took and why under the plan.

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
