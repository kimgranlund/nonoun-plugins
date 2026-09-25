<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0020: board.py fails its selftest when a ticket status is not classified for visibility

## PR body
### Summary
`board.py` used to hide tickets by checking the literal strings `dropped` and `done`. If `tickets.py` added a new status, nothing would force anyone to decide whether the board shows or hides it. Now every `tickets.ENUMS['status']` value is listed in one of three named sets, and the board selftest fails when those sets and the enum stop matching. Which statuses the board shows is unchanged, and an unknown status still shows.

### Changes
- `plugins/sdlc-lite/scripts/board.py` adds three module-level visibility sets: `ALWAYS_HIDDEN` (`dropped`), `HIDDEN_WITHOUT_STEP_WORK` (`done`) and `ALWAYS_SHOWN` (`proposed`, `ready`, `blocked`). A comment says every new status must go in one of them.
- `belongs_on_board` checks a ticket's status against these sets instead of against literal strings.
- A new helper, `unclassified_statuses(known, sets=None)`, reports three problems:
  - a known status that is in no set
  - a status that is in two sets
  - a set entry that is not a known status
- A new section 6 in the selftest runs three checks:
  - a consistency check against `tickets.ENUMS['status']`
  - a negative control that adds `zz-new-status` and expects a failure
  - a check that a status placed in two sets is caught
- `tickets.py`, `CLAUDE.md` and `skills/board/SKILL.md` are unchanged, because what the board shows is unchanged.

### Verification
The builder ran these checks and the independent verifier (L1) reran them. Verdict: pass.
- `python3 plugins/sdlc-lite/scripts/board.py selftest` printed `board selftest: PASS` and exited 0.
- A grep for `'dropped'` and `'done'` finds them only in the named sets and in selftest fixtures, not in `belongs_on_board`.
- Negative control: `'zz'` was added to `tickets.ENUMS['status']` in memory and the selftest was run. It printed FAIL, named `'zz'` and exited 1. Without `'zz'` it passes.
- The existing selftest expectations are unchanged. `git diff --stat` shows no edit to `tickets.py`.
- `scripts/check.sh`, run from `plugins/sdlc-lite`, exited 0. That run includes the role-level check, the tickets and board selftests, shellcheck and plugin validate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- board.py now lists each ticket status in a named visibility set, and its selftest fails when a status in `tickets.py` is not classified. The board shows and hides the same tickets as before. (T-0020)

## Follow-ups
None
