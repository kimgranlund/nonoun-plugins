## Task goal
The merge-step conflict-marker guard's known gap (a kept conflict-marker line textually identical to a parent line, shown as `+ ` or ` +` in `git diff-tree --cc`, not `++`) is either closed or explicitly documented as an accepted limitation, and check.py's behavior probe has a case that pins whichever outcome is chosen.

Decision rule (unattended, no user present): close the gap if a guard exists that (a) flags this new case, (b) still passes all five existing probe cases, especially the legit lane line case, (c) stays one lint-clean criterion line that parses under `bash -n` and has no `||` between checks, and (d) stays readable. If no such guard exists, keep the current guard, add the probe case asserting the documented miss (so a future change is noticed), and record the limitation in the template's surrounding docs and CLAUDE.md. The planner records which branch it took and why under the plan.

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
