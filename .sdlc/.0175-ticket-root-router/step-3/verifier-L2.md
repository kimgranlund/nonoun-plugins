<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criteria 1-15 (behavior: router written by new, close, roadmap and check; counts, ticket and claimed lines; both layouts; Procedures identical; block and import preserved; each check cause; malformed refusal; router line): pass. Evidence: I extracted all 21 criteria from handoff lines 103-123 and ran each with `bash -c` from the repo root. All exited 0. At the base sha in a throwaway worktree, criteria 1-18 exited non-zero, so the checks can go red. Criteria 19-21, the guards, were green there, as expected for guards.
- Criterion 16 (defect injected into `router_problems`): pass. Evidence: exit 0. The clean copy's selftest passed, and the copy with `return []` inserted after `def router_problems(root, ts):` failed. The injected defect is `router_problems` returning [] unconditionally, and the selftest fails on it.
- Criterion 17 (defect injected into `write_router`): pass. Evidence: exit 0. The injection makes `write_router` return early once `AGENTS.md` exists, and the selftest failed on it. The `assert s.count(k) == 1` in the criterion confirms the injection target exists, so the edit was real.
- Criterion 18 (docstring has AGENTS.md, CLAUDE.md, claimed_by, router:): pass. Evidence: exit 0. The diff shows docstring text for the router files, `claimed_by` and the `router:` line.
- Criteria 19-21 (guards: selftest, render byte-equal to base, only `tickets.py` changed): pass. Evidence: exit 0 on the built tree. I also ran `tickets.py selftest` directly and it printed `tickets selftest: PASS`.
- Extra manual check of the preflight, with a malformed block in `AGENTS.md`: `new`, `close --dry-run`, `close` and `roadmap` each exited 1 with `AGENTS.md: router block malformed: start marker at line 1 has no end marker after it; fix its markers by hand, then rerun; nothing written`. `ls` showed no new folder, and `check` also failed on the malformed block. The message matches the handoff format.
- Extra manual check of the empty case: `check` on a root with no tickets and no `AGENTS.md` printed `ok: 0 tickets, roadmap current` with rc=0.
- The builder's claim that only the docstring changed among existing lines holds: `git diff | grep '^-[^-]'` shows one deleted line, the `check` docstring line, which was rewritten.

## Out of scope changes
None. `git diff --stat` shows only `plugins/sdlc-lite/scripts/tickets.py` changed, and guard 21 passed. The untracked files under `.sdlc/0175-ticket-root-router/step-3/` are run artifacts.

## For the next attempt
None
