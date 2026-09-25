<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0071: tickets.py close no longer counts the ticket being closed as a duplicate of its own follow-ups

## PR body
### Summary
`tickets.py close` checked each filer follow-up for duplicates against every ticket, including the one being closed. A follow-up whose title or slug base matched the parent was marked `duplicate of <own id>` and skipped. Closing T-0064 hit this: the close filed 0 follow-ups, and T-0069 and T-0070 had to be stamped by hand. Now the ticket being closed is left out of the duplicate check, so only other tickets can make a follow-up a duplicate.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`, `cmd_close`: the `known` list used for duplicate matching now skips the ticket being closed. It matches that ticket by id (`pid`) or by folder (`slug`).
- `plugins/sdlc-lite/scripts/tickets.py`: the module usage text and the `cmd_close` docstring now say "any other ticket" instead of "an existing ticket".
- `plugins/sdlc-lite/scripts/tickets.py`, `selftest()`: new case `(s2)`. The fixture is a ticket `alpha` with the follow-ups `- Alpha one` and `- Alpha one.`. The case expects three things:
  - The dry run marks neither follow-up as a duplicate.
  - The real close files two tickets, `alpha-one` and `alpha-one-2`.
  - `check` returns 0 afterwards.

  The fixture bullets differ from the plan's examples, which would not have failed before the fix. The verifier accepted this because the plan said "for example".

### Verification
- Test first: the builder wrote `(s2)` before the fix. Selftest failed on both `(s2)` checks: the dry run showed `duplicate of T-0001 (alpha)` and the close filed 0 tickets. After the fix, selftest passed.
- Independent check (verifier L1, pass): in a throwaway worktree the verifier applied the diff, reverted only the `known` filter, and saw `(s2)` fail. With the fix in the real tree, `tickets.py selftest` printed `PASS`.
- `grep -c "(s2)"` on `tickets.py` prints 3.
- `scripts/check.sh` exited 0 (hook selftest, shellcheck, and plugin validate all ok). The builder also ran it on a HEAD worktree and got identical output. The verifier did not run the base comparison because the run was fully green.
- The diff touches only `plugins/sdlc-lite/scripts/tickets.py`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `tickets.py close` no longer marks a follow-up as a duplicate of the ticket being closed, so follow-ups whose title or slug starts like the parent's slug are filed again (T-0071).

## Follow-ups
None
