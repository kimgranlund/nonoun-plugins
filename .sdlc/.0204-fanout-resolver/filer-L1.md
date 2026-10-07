<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0204: fanout.py resolves lane tickets through ticket_dir

## PR body
### Summary
`fanout.py` did not support `ticket_root`. With `ticket_root: tickets` set, preflight looked for ticket ids directly under `.sdlc/`, found none, and refused. Regular lanes now resolve every ticket path through `tickets.ticket_dir`. Under `ticket_root: tickets`, a lane merges and closes its ticket under `.sdlc/tickets/`. Flat-layout behavior is unchanged.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Preflight loads tickets with `tickets.load(tickets.ticket_dir(root))`. A `tickets.Fail` from `ticket_dir` becomes a `Refuse`.
  - A new `trel` (the ticket dir relative to the repo top) is added to ctx.
  - These paths now use `trel`: the committed-handoff check, `driver_for`, the `setup` missing-handoff check, `FANOUT_HANDOFF`, `inherited_red`, and the merge copy and clean paths.
  - The dry run prints `ticket folders in each worktree: <dir>` only when `trel` differs from the root, so flat dry-run output is unchanged.
  - The module docstring is updated.
  - A new selftest case, labelled `ticket_root lane`, is added.
- `docs/references/sdlc-internals.md`: the "Regular lanes do not follow `ticket_root` yet ... follow-up" sentences are replaced with a description of the new behavior.
- Deliberately unchanged:
  - `FANOUT_ROOT` still points at the lane root that holds `config`.
  - The `tickets.py --root <rel> close` command is untouched, because tickets.py resolves `ticket_dir` itself.
  - The `git add -A -- <root>` staging in the close commit still covers the tickets folder.
  - External lanes still use `tickets.branch_tickets`, which already resolves `ticket_root` per branch.

### Verification
Step 1 had builder L2 and an independent verifier L1. The verifier's verdict was pass.
- Fixture run: a committed repo with `ticket_root: tickets` and `.sdlc/tickets/x/handoff.md` (T-0001). `fanout.py run` exited 0, `fanout/t:.sdlc/tickets/x/handoff.md` has `status: done`, and the tip subject is `close T-0001`.
- Negative control: the same fixture against `fanout.py` from `git archive $SDLC_BASE_SHA` exited 2 with `T-0001: no ticket under .../repo/.sdlc has this id`. The check is red on the base and green after the change.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS.
- Grep criteria: all hold.
  - The new `ticket_dir` call and the `ticket_root lane` label are present in `fanout.py`.
  - "Regular lanes follow" is present in the doc.
  - The old "Regular lanes do not follow" text is gone.
- The diff touches only `fanout.py` and `sdlc-internals.md` (outside `.sdlc`), and there are no untracked files outside `.sdlc`.
- `git diff --check` is clean.
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. shellcheck is not installed on this host, so that part was skipped.
- `python3 scripts/check-packaging.py`: pass.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass (209 tickets, roadmap current).

Limits: per the burn-down brief there was no live run, so the checks above are selftests and the gates. shellcheck was not exercised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `fanout.py` resolves regular lane ticket paths through `tickets.ticket_dir`, so lanes now work on repos with `ticket_root: tickets`. Flat layouts are unchanged. The dry run adds a `ticket folders in each worktree:` line when the ticket dir differs from the root.

## Follow-ups
- note: T-0203 (this ticket's dependency) is not an ancestor of this branch, and its `t0203` branch rewrites `fanout.py` heavily around `preflight`, `print_plan`, and `merge_gate_close`. Whoever merges the two must keep both the overlap check and the `trel` routing.
- note: The fixture criterion relies on `tickets.py close` succeeding under `ticket_root: tickets` in a fresh repo with no router files. A later change to close's router handling could turn it red for a reason outside `fanout.py`.
