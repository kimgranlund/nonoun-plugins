<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `.gitignore`: added `.sdlc/messages/` after `.sdlc/runtime/`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added the Layout line, the ignore-list entry and the bullet below the list.
- `plugins/sdlc-lite/scripts/onboard.py`: added the local mailbox bullet to `ROOT_AGENTS_TEMPLATE` after the roadmap line. `TEMPLATE_VERSION` is still 1.
- `docs/repo-onboarding/design.md`: added the same bullet, byte for byte, after the roadmap line.
- `docs/maintenance/sdlc-internals.md`: added one notice sentence to the `scripts/run.sh` entry, and a new `scripts/messages.py` entry placed before `## Feed`.
- `docs/ticket-stages/design.md`, Message bus section only:
  - Added a status line after the heading.
  - Changed the `re` wording.
  - Named the command on every transition row, with `protocol` and `expires` added to the create row's Stamped cell.
  - Added the exact reply rule and the notice fields.

## Checks
I exported `SDLC_BASE_SHA` from the step's `base-sha` file before running these.
- `git check-ignore -q .sdlc/messages/new/bob/x.md`: PASS
- handoff-format grep criterion: PASS
- onboard.py and design.md line equality, plus `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: PASS
- sdlc-internals `new message(s)` grep and the heading-order awk: PASS
- design.md `messages.py expire`, `T-0177` and no `(ticket id)`: PASS
- (guard) `TEMPLATE_VERSION = 1`: PASS
- (guard) design.md line 3 unchanged from base: PASS
- (guard) no em dash in added lines: PASS
- (guard) scope file list: PASS
- `git diff --check`: clean

## Notes
None
