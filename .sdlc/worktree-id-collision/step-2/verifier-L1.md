<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -n "worktree"` shows a hit describing id allocation in each of the three files: pass. Evidence: I ran `grep -n "worktree" CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md .claude/agents/sdlc-lite-author.md`. Three hits describe id allocation:
  - `CLAUDE.md:25`: "`new` and `close` follow-ups take the next id above the max across the same-relative ticket root in every `git worktree list` tree (local root only outside git); `check` fails on two tickets sharing an id and names both folders, which also catches branches not checked out in any worktree after merge"
  - `plugins/sdlc-lite/skills/ticket/SKILL.md:16`: "Ids are allocated across worktrees: ..."
  - `.claude/agents/sdlc-lite-author.md:16`: "Keep cross-worktree id allocation (max id across every `git worktree list` tree, `check` failing on duplicate ids) in sync across tickets.py, the /ticket skill, and CLAUDE.md."

  Can this check fail? Yes. At HEAD, `git show HEAD:plugins/sdlc-lite/skills/ticket/SKILL.md | grep worktree` returns nothing. At HEAD, the only `worktree` hits in CLAUDE.md are lines 23 and 81 (statusline, headless runs), and in the author agent lines 22, 28 and 30. None of them is about id allocation, so the criterion was red before this step.
- The diff adds no em dashes: pass. Evidence: `grep -c "—"` on the three files gives 0, 0, 0 in the working tree. `git show HEAD:<f> | grep -c '—'` gives 0, 0, 0 at HEAD. `git diff -- <3 files> | grep '^+' | grep -c '—'` gives 0.
- `plugins/sdlc-lite/scripts/check.sh` exits 0, with only the expected warning: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh > /tmp/vchk2.out 2>&1; echo rc=$?` printed `check.sh rc=0`. The builder had not confirmed this exit code, so I captured it directly. `grep -iE 'warn|fail|error'` on the output found no lines at all, so no unexpected warning was printed and the expected CLAUDE.md validate warning did not appear either. The output ends with "ok: shellcheck" and "ok: plugin validate".
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0: pass. Evidence: it printed "ok: 60 tickets, roadmap current" with `tickets rc=0`.

## Out of scope changes
None from this step. `plugins/sdlc-lite/scripts/tickets.py` is also modified in the tree, but that is step 1's code change. `.sdlc/worktree-id-collision/handoff.md` is modified too, by the conductor's Clarified section. The step-2 builder touched only CLAUDE.md, the ticket SKILL.md, and the author agent, and all three edits are what the step asked for.

## For the next attempt
None
