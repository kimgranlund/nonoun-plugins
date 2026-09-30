<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qx '## Assumptions' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: it exited 0 on the built tree. The same string appears 0 times at base sha 606059b, so the check can go red.
- `grep -qF 'unresolved:' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: it exited 0 on the built tree, and the string appears 0 times at base.
- `grep -qF 'plan review:' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: it exited 0 on the built tree, and the string appears 0 times at base. The diff shows the string in rule 9, in the format `plan review: <verdict>: <finding>`.
- `grep -qF 'Depends on:' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: it exited 0 on the built tree, and the string appears 0 times at base. It appears in the `### Do` line of the format.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: it printed `ok: 18 role levels, 8 agents checked`, with rc=0. This is a gate. I did not run it at base because it is green now.
- (guard) the scope-guard pipeline over `git diff --name-only`, untracked files and `grep -vxE`: pass. Evidence: it exited 0 on the built tree, and the working-tree diff touches only `planner.md` (`git status`). I did not seek a red state for this guard.
- Do requirements, checked in the diff:
  - The `## Assumptions` section sits between the last step block and `## Risks`.
  - Its format is `- <assumption>: verified by <how>` plus `- unresolved: <decision>: <what settles it>`.
  - It says `steps.py split` ignores the section and `steps.py review` stops on an `unresolved:` item.
  - The `### Do` line names targets, settled interface decisions with evidence, `Depends on:` and focused checks, and states that no decision is left to the builder.
  - Rule 9 has the `plan review:` clause, which says to fix the named steps and keep the rest.
  - Removed lines: only the old `### Do` line and the old rule 9 line changed. Rule 9 was extended with its text kept.
  - `check.py` passing confirms the required phrases survive.

## Out of scope changes
None. `git status` shows only `plugins/sdlc-lite/agents/planner.md` modified. The other entries are untracked artifacts under `.sdlc/`.

## For the next attempt
None
