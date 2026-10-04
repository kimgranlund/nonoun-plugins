<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: preflight now loads tickets from `tickets.ticket_dir(root)`. A `tickets.Fail` from that call becomes a Refuse. `trel` was added to ctx, and the committed-handoff check, the driver, the setup missing check, FANOUT_HANDOFF, inherited_red, and the merge copy/clean paths all use it. The dry run prints `ticket folders in each worktree:` only when that dir differs from the root. The docstring was updated, and a selftest case labelled `ticket_root lane` was added.
- docs/maintenance/sdlc-internals.md: the fanout paragraph now says "Regular lanes follow `ticket_root`..." in place of the old follow-up sentences.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- The fixture criterion with the current fanout.py: exit 0
- Negative control, the same fixture against fanout.py from `git archive $SDLC_BASE_SHA`: exit 2, stderr `T-0001: no ticket under .../repo/.sdlc has this id`
- The four grep criteria: all hold
- The diff-scope and untracked-files criteria: both empty, so both pass
- `git diff --check $SDLC_BASE_SHA -- <both files>`: clean
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (shellcheck is not installed, so that part was skipped)
- `python3 scripts/check-packaging.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0

## Notes
These stay unchanged, as the handoff says: `FANOUT_ROOT`, the `tickets.py --root rel close` command, and the `git add -A -- relp` staging in the close commit. Flat-layout dry-run output does not change, because the new line only prints when the ticket dir differs from the root. No commit was made.
