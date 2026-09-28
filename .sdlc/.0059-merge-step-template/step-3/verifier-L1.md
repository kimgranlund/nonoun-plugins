<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -n 'merge-step' CLAUDE.md .claude/agents/sdlc-lite-author.md` prints at least one line for each of the two files: pass. Evidence: the grep exits 0 and prints `CLAUDE.md:11` (the Commands line), `CLAUDE.md:84` (the new Decisions bullet) and `.claude/agents/sdlc-lite-author.md:14` (the new Invariants bullet). The check can fail: at HEAD, `git show HEAD:<file> | grep -c merge-step` gives `0` for both files.
- `grep -n 'git merge --no-ff' CLAUDE.md` prints at least one line: pass. Evidence: the grep exits 0 and prints `84:- **A merge is a standard builder step.** ... the builder runs \`git merge --no-ff <branch>\` and makes the merge commit ...`. The check can fail: `git show HEAD:CLAUDE.md | grep -c 'git merge --no-ff'` gives `0`.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (guard): pass. Evidence: `check rc=0`, and the output ends with `order selftest: PASS`, `run selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. As a guard it only has to be green now. I did not break it this step to watch it go red. The new check.py merge-step section (check.py diff, lines 95-120) adds FAIL paths for a missing block, blocks that differ, a lint failure, and builder.md missing `git merge --no-ff`.
- The Do content matches the handoff: pass. Evidence: CLAUDE.md:84 covers all four points: the template locations; the builder runs `--no-ff` and it is the only step kind that commits; push and publishing stay blocked and the verifier never changes git state; the five criteria; and what check.py guards. CLAUDE.md:11 names the guard on the check.sh line. sdlc-lite-author.md:14 has the Invariants bullet as specified.

## Out of scope changes
None. The step touched only `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`. The other modified files come from steps 1-2 of this task or from the conductor, which owns `.sdlc/0059-merge-step-template/`:
- `agents/builder.md`
- `agents/planner.md`
- `scripts/check.py`
- `skills/handoff-format/SKILL.md`
- `.sdlc/0059-merge-step-template/handoff.md`

## For the next attempt
None
