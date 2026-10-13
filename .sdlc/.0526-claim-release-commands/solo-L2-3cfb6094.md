<!-- role=solo level=L2 model=opus effort=medium -->
## Output
🟢 T-0526 is done. The new `claim` and `release` commands and the claim warnings in `check` work, and the independent verifier passed the ticket. Nothing is committed; fanout.py commits this lane.

**Files changed**
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `claim <id> --by <agent> [--handover --reason TEXT]` sets `status: claimed`, writes the `claimed_by:` line directly after `created:`, and regenerates the roadmap.
  - `--handover` swaps in the new holder and adds one dated line to the end of the ticket body.
  - `release <id>` removes the claim, sets `status: ready`, and regenerates the roadmap.
  - `check` now warns, without failing, on three things: a comment after the claim line, a claim line that isn't right after `created:`, and a claim older than `claim_days:` (default 7) when the ticket folder has no running attempt.
  - When a ticket problem makes `new` refuse, the message now names that ticket and a one-line fix.
  - Also updated: the "Claim a ticket" router steps, the help text, and 12 new selftest cases.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: documents the new commands and warnings.
- `.sdlc/AGENTS.md`: regenerated from the new router text.
- The ticket's `handoff.md`: added the missing `## Acceptance criteria`.

**Checks**
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0
- `git diff --check` exit 0
- I broke the new code on purpose in five ways (each warning, the running-attempt exemption, where the claim line goes, the roadmap rewrite). The selftest failed every time and passed again once I restored the file.
- Also run: `board.py selftest` passed, `check-packaging` exit 0, `docs_check` 0 errors, no em dashes in the added lines.
- The solo report `solo-L2.md` passes `results.py solo-report`.

**Verifier**
- Level L2 (Sonnet, high effort): pass on all 5 criteria, with no out-of-scope changes. It tried seven ways of breaking the code on its own, and each failed the selftest.
- It could not create a throwaway git worktree (blocked because `SDLC_TMP_WORKTREES` is unset), so it ran those tests on a copy of the scripts in a temp folder.
- The result `verifier-L2.md` validates, and the run is recorded with `dispatch.py record`.

**Open**
- The reason maison's `new` refused on a claimed ticket was never reproduced, so this fix is tested against a stand-in ticket, not maison's own case.

verify: needed (done: the L2 verifier ran in this session and passed)
