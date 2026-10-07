<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `git check-ignore -q .sdlc/messages/new/bob/x.md`: pass. Evidence: exit 0 on the built tree. `.gitignore` at the base sha has 0 lines matching "messages", so the check goes red before the change.
- handoff-format SKILL.md exact ignore line plus a Layout line mentioning `scripts/messages.py`: pass. Evidence: both greps exit 0. The diff adds the Layout line after `.sdlc/runtime/`, the fenced-list line, and the bullet below the list.
- onboard.py and design.md "local mailbox" lines are identical and contain `.sdlc/messages/`, and `onboard.py selftest` is green: pass. Evidence: the command exited 0 and the selftest tail shows the gate lines "positive ok, negative ok". The diff shows the same bullet in `ROOT_AGENTS_TEMPLATE` and in `design.md` right after the roadmap line.
- sdlc-internals.md has "new message(s)" and the entry order run.sh, then messages.py, then Feed: pass. Evidence: exit 0. The diff shows the notice sentence appended to the run.sh entry and the new messages.py entry above `## Feed`.
- `docs/specs/ticket-stages/design.md` has `messages.py expire` and `T-0177`, and no longer has "(ticket id)": pass. Evidence: exit 0.
- (guard) `TEMPLATE_VERSION = 1`: pass. Evidence: grep exit 0.
- (guard) line 3 of `docs/specs/ticket-stages/design.md` unchanged from the base: pass. Evidence: exit 0.
- (guard) no em dash in added lines: pass. Evidence: the guard exit 0, and a separate `git diff -U0 | grep -c "^+.*—"` printed 0.
- (guard) no changed files outside the allowed list: pass. Evidence: the guard printed an empty list and exited 0. `git status` shows only the six scoped files plus `.sdlc` artifacts.
- Doc claims against the code: pass. Evidence: the `expires` stamp matches `messages.py:550`. The notice text matches `run.sh:241`. The `expire` rows match the transition table in `messages.py:133-134`.

## Out of scope changes
None. The changed files are `.gitignore`, `SKILL.md`, `onboard.py`, `docs/specs/repo-onboarding/design.md`, `sdlc-internals.md`, and `docs/specs/ticket-stages/design.md`. All six are named in the Do. The diff shows no edits to the other entries in `sdlc-internals.md` and none to the other docs the handoff said to leave alone. Steelman: I drafted a fail on the long run.sh entry diff, which looks large. The rebuttal holds: the diff is one appended sentence on a single-paragraph line, so it was dropped.

## For the next attempt
None
