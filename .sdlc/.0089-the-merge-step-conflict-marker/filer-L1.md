<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0089: Document and pin the merge-step conflict-marker guard's aligned-marker miss

## PR body
### Summary
This keeps the `++`-only merge-step conflict-marker guard and documents its known gap as an accepted limitation. Two new check.py probe cases pin that choice.

The gap: after a conflicted merge, a kept conflict-marker line can be textually identical to a parent line and aligned with it. `git diff-tree --cc` then shows it as `+ ` or ` +` instead of `++`, so the guard passes it.

The planner tested this in throwaway repos. Widening the guard to `^(\+\+|\+ | \+)(<<<<<<<|>>>>>>>)( |$)` catches the aligned kept marker. It also flags a legit lane line in a file both sides changed cleanly (`+ >>>>>>> lane`), which is the T-0069 false positive. The two cases produce the same diff marks. Telling them apart would take per-file marker counts across HEAD, both parents, and the merge base, and that fails the ticket's "one lint-clean line" and "readable" rules. So the planner took the ticket's document branch.

### Changes
- `plugins/sdlc-lite/scripts/check.py`: two behavior probe cases added after the kept-conflict case:
  - A both-sides legit lane line, which must pass the guard.
  - An aligned kept marker, which must pass the guard as the documented miss. If it ever fails, the error says the documented limitation changed.
  - The probe comment and docstring item 6 now name all seven cases.
  - Existing cases and their error text are unchanged.
- `plugins/sdlc-lite/agents/planner.md` (`## Merge steps`) and `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (`### Merge step`): a limitation paragraph, placed outside the fenced `merge-step` blocks. The blocks are byte-for-byte unchanged.
- `CLAUDE.md`: the merge-step decision now names the accepted limitation.
- `.claude/agents/sdlc-lite-author.md`: the hazard line lists the seven probe cases and says an aligned kept marker passes by design.

### Verification
- Step 1 (builder L2, verifier L1): pass.
  - `check.py` and `check.sh` exit 0.
  - In a temp copy with the widened guard, check.py reports both `aligned kept marker flagged` and `both-sides legit lane line flagged`. So both new cases go red when the guard changes and stay green on the real tree.
  - The guard text in planner.md is unchanged, and check.py has no em dashes.
- Step 2 (builder L1, verifier L1 on Opus): pass.
  - Each of the four docs contains "textually identical to a parent line". Each grep exits 0 in the tree and 1 at HEAD.
  - The merge-step block diffs against HEAD are empty, with a negative control.
  - None of the four files has an em dash.
  - `check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- The merge-step conflict-marker guard still misses one case: a kept marker line textually identical to a parent line and aligned with it. This is now documented as an accepted limitation. check.py adds two probe cases, one for this miss and one for a legit lane line in a file both sides changed, so any change to the guard's behavior is caught. (T-0089)

## Follow-ups
None
