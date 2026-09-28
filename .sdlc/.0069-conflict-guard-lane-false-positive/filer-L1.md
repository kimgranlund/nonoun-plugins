<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0069: Merge-step conflict-marker guard only flags markers the merge added

## PR body
### Summary
The merge-step conflict-marker guard used to fail on any line starting with seven `<` or `>` in any file the merge touched. A lane branch that legitimately added such a line therefore failed a clean merge. The guard now fails only on marker lines the merge itself added, meaning the lines `git diff-tree --cc` marks `++` (new versus both parents). This follows up T-0064.

### Changes
- **`plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`:** in the `merge-step` template, the old `git diff -z ... | xargs -0 sh -c ...` guard is replaced by:
  `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`
  The two blocks stay byte-identical, and no other line in them changed.
- **`plugins/sdlc-lite/scripts/check.py`:** the behavior probe now runs five cases on `sp ace.txt`:

  | Case | Expected |
  |---|---|
  | empty merge | pass |
  | marker added by the merge commit itself | fail |
  | legit lane line (new) | pass |
  | real conflict kept (new) | fail |
  | clean | pass |

  The probe comment and docstring item 6 are updated to match.
- **`CLAUDE.md`:** the merge-step decision now describes the new criterion.
- **`.claude/agents/sdlc-lite-author.md`:** one new hazard line covers the `diff-tree --cc` guard and the five probe cases.

### Verification
- **Step 1, builder L2, verifier L1: pass.**
  - Old-guard negative control: `check.py` run against an archive of `7e51f1b` prints `legit lane line flagged`, so the new case catches the old behavior.
  - Kept-conflict negative control: with the guard replaced by `true "<<<<<<<"`, `check.py` prints `kept conflict markers not flagged`.
  - `check.py` and `check.sh` are green.
  - `steps.py` and `builder.md` are unchanged.
  - The verifier confirmed the two template blocks are byte-identical.
- **Step 2, builder L1, verifier L1 (run on Opus): pass.** Each doc grep went red on the HEAD copy and green on the working tree. The em-dash check bit on a control file. `check.sh` is green.

### Known trade-off (from the plan)
A kept marker line that is textually identical to a parent line and aligns with it shows as `+ ` rather than `++`, so the guard misses it. There is also a behavior change in `steps.py split --only`: it skips only guard spans containing `HEAD^1`, and the new span has none, so it now runs on the pre-merge tree. That run is green unless the pre-merge HEAD is itself a merge commit that kept markers.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: the merge-step conflict-marker guard no longer fails a merge whose lane branch legitimately adds a line starting with seven `<` or `>`. It now flags only marker lines the merge itself introduced (`git diff-tree --cc` `++` lines). check.py probes both the legit-lane-line and kept-conflict cases. (T-0069)

## Follow-ups
- The merge-step conflict-marker guard misses a kept conflict-marker line that is textually identical to a parent line and aligns with it in the combined diff (shown as `+ `, not `++`). Add a probe case and decide whether to close the gap.
