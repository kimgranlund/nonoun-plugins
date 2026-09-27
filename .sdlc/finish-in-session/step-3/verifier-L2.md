<!-- role=verifier level=L2 model=sonnet effort=high -->
No stray worktrees remain. All evidence gathered.

## Verdict
pass

## Criteria
- `grep -q '^## 5\. Loose ends' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the command, rc=0 (line 44 of file).
- `grep -q '^## 6\. File' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the command, rc=0 (line 51).
- `grep -q '^## 7\. Close out' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the command, rc=0 (line 54).
- `grep -q 'fix-now' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the command, rc=0.
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the command, rc=0 (line 48).
- `grep -qF 'decide:' plugins/sdlc-lite/skills/open-questions/SKILL.md`: pass. Evidence: ran the command, rc=0.
- `grep -q 'Loose ends' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: ran the command, rc=0.
- `grep -q 'notes.md' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: ran the command, rc=0.
- `! grep -q 'no one writes them by hand' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: ran the command, rc=0; `git diff` on the file confirms the phrase was replaced with the required text.
- `grep -q 'Loose ends' plugins/sdlc-lite/skills/level-rubric/SKILL.md`: pass. Evidence: ran the command, rc=0; new `### Loose ends step` subsection has no `| L<n> |` table row.
- `grep -qF 'decide:' plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: ran the command, rc=0.
- `grep -q 'Loose ends' CLAUDE.md`: pass. Evidence: ran the command, rc=0; `git diff CLAUDE.md` shows the `/chain` bullet naming the Loose ends step and close-out round.
- Negative-control criterion (copy tree, mutate "Loose ends"→"Loose threads" in chain SKILL.md, run check.py, grep for the failure): pass. Evidence: ran the exact command span, `rc=1` from check.py and `printf "%s\n" "$out" | grep -q "skills/chain/SKILL.md.*Loose ends"` matched ("NC MATCH FOUND").
- `(guard) python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: ran on the built tree, `ok: 18 role levels, 8 agents checked`, rc=0; also ran in a throwaway worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`, HEAD=209ed6a, the pre-build commit since no commit was made) and it was green there too (rc=0), so the guard held before and after, consistent with its "green at HEAD and must stay green" note; worktree removed afterward. The negative control above already proves this same check.py mechanism can go red, so this guard is not vacuous.

## Out of scope changes
`plugins/sdlc-lite/agents/filer.md`, `scripts/tickets.py`, `skills/fanout/SKILL.md`, `skills/file/SKILL.md`, `skills/ticket/SKILL.md`, and part of `plugins/sdlc-lite/scripts/check.py` (the `FINISH_DOCS` scaffold and check 9 docstring entry) are changed but belong to this task's steps 1 and 2, not step 3. Checked: `.sdlc/finish-in-session/step-1/verifier-*.md` and `step-2/verifier-*.md` both show `## Verdict\npass`, and `.sdlc/finish-in-session/planner-L3.md` step 1 and step 2 Do sections name exactly these files, confirming they are earlier completed steps sitting uncommitted in the tree (as the builder's own Notes state), not new work by this step's builder. `.sdlc/finish-in-session/handoff.md`'s `## Intent` section is also filled in but this predates planning (a /clarify-stage edit, not named in any step's Do, and step 3's builder Notes/Changes never mention it). None of these were introduced by this build. Not filing as out-of-scope findings: all read-checked against their source (planner Do sections and verifier verdicts) rather than dismissed on assumption.

## For the next attempt
None.
