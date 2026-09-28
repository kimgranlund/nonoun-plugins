<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -n "close --numbered"` matches in both SKILL.md and CLAUDE.md: pass. Evidence: in the worktree the grep matched `CLAUDE.md:25` and `plugins/sdlc-lite/skills/ticket/SKILL.md:15`, rc=0. In a throwaway worktree at HEAD the same grep gave rc=1 with no matches, so the check can fail.
- The same grep for `warn` matches in both files: pass. Evidence: matches at `SKILL.md:15` ("plain `check` warns, without failing, when every folder has an `NNNN-` prefix but the config lacks the line") and `CLAUDE.md:25` (same wording), rc=0. At HEAD, SKILL.md had no match, so the check could fail there. The CLAUDE.md side of this check can never fail: `CLAUDE.md:11` ("The validate warning...") matches both before and after the change. I confirmed the actual new text by reading line 25 in the grep output, which now contains "warns".
- `grep -n -i "numbered" .claude/agents/sdlc-lite-author.md` matches at least one line: pass. Evidence: it matched line 16, rc=0: "Numbered ticket mode persists via `new` and `close --numbered`, and `check` warns on numbered folders with no config line. Keep tickets.py, the /ticket skill, and CLAUDE.md in sync on this." The line sits inside the Invariants list, directly before `## After every change`. At HEAD the grep gave rc=1.
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh > /tmp/vchk.out 2>&1; echo check_rc=$?` printed `check_rc=0`, which is the script's own exit status and not a pipe's. The output tail read: ok 18 role levels / 8 agents, selftest PASS, tickets selftest PASS, board selftest PASS, ok shellcheck, ok plugin validate.
- No em dashes (from the Do list): pass. Evidence: `grep -n "—"` on all three edited files gave rc=1, no matches.

## Out of scope changes
None for this step. Two other files also have changes in the tree, but step 2 did not call for them: `plugins/sdlc-lite/scripts/tickets.py` (step 1's code change) and `.sdlc/0026-tickets-py-check-should-warn/handoff.md` (task Goal and Constraints filled in during planning). Both come from earlier stages of the same task.

## For the next attempt
None
