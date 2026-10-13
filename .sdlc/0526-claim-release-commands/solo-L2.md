# Solo report: T-0526 claim and release commands

## Files changed
- plugins/sdlc-lite/scripts/tickets.py: `claim <id> --by <agent> [--handover --reason TEXT]` and `release <id>`; claim lint warnings in `check` (trailing comment, out of place, older than `claim_days:` with no running attempt); fix hints on the claimed/paused problems and the `new` refusal; router Claim procedure; docstring and usage; selftest cases.
- plugins/sdlc-lite/skills/ticket/SKILL.md: argument hint, arguments table, claim rule.
- .sdlc/AGENTS.md: regenerated router block.
- .sdlc/0526-claim-release-commands/handoff.md: ## Acceptance criteria added.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0
- `git diff --check` exit 0
- Mutation controls: five mutants (lint off, running exemption off, claim line misplaced, roadmap write skipped, comment check off) each fail named selftest cases.
- board.py selftest PASS, check-packaging exit 0, docs_check 0 errors.

verify: needed
