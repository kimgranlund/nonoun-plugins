<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0204: fanout.py resolves lane tickets through ticket_dir

## PR body
### Summary
`fanout.py` did not support `ticket_root`. With `ticket_root: tickets` set, preflight looked for ticket ids directly under `.sdlc/`, found none, and refused. Regular lanes now resolve every ticket path through `tickets.ticket_dir`. Under `ticket_root: tickets`, a lane merges and closes its ticket under `.sdlc/tickets/`. The planned-scope overlap check, added by T-0203, reads step handoffs from the same ticket root. Flat-layout behavior is unchanged.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Preflight loads tickets with `tickets.load(tickets.ticket_dir(root))`. A `tickets.Fail` from `ticket_dir` becomes a `Refuse`.
  - A new `trel` (the ticket dir relative to the repo top) is added to ctx. These paths now use it: the committed-handoff check, `driver_for`, the `setup` missing-handoff check, `FANOUT_HANDOFF`, `inherited_red`, and the merge copy and clean paths.
  - `planned_scope` builds the ticket folder path from `tickets.ticket_dir(...) / slug`. Step 2 added this after the branch verifier found the overlap check still read `.sdlc/<slug>`.
  - The dry run prints `ticket folders in each worktree: <dir>` only when `trel` differs from the root, so flat dry-run output is unchanged.
  - The module docstring is updated.
  - The new `ticket_root lane` selftest case covers a merge-and-close, and also two lanes (T-0002, T-0003) with a shared planned step-1 scope under `.sdlc/tickets/`.
- `docs/maintenance/sdlc-internals.md`: the "Regular lanes do not follow `ticket_root` yet" sentences are replaced. The new text says regular lanes follow `ticket_root`, and that the dry run's planned-scope overlap check reads step handoffs from that dir.
- Deliberately unchanged:
  - `FANOUT_ROOT` still points at the lane root that holds `config`.
  - The `tickets.py --root <rel> close` command is untouched, because tickets.py resolves `ticket_dir` itself.
  - The `git add -A -- <root>` staging in the close commit.
  - External lanes still use `tickets.branch_tickets`, which already resolves `ticket_root` per branch.

### Verification
Both steps were built and then independently verified. Step 1 had builder L2 and verifier L1, and the verdict was pass. Step 2 had builder L3 and verifier L2, and the verdict was pass.
- Step 1 fixture: a committed repo with `ticket_root: tickets` and `.sdlc/tickets/x/handoff.md` (T-0001). `fanout.py run` exited 0, the integration handoff has `status: done`, and the tip subject is `close T-0001`.
- Step 1 negative control: the same fixture against `fanout.py` from `git archive $SDLC_BASE_SHA` exited 2 with `no ticket under .../.sdlc has this id`. It is red on the base and green after the change.
- Step 2 negative control: the old routing line `tdir = pathlib.Path(root) / slug` was put back and nothing else changed. The selftest then failed only on `ticket_root lane: planned scopes under .sdlc/tickets print the a/b shared.txt pair line`, with output `not planned, checked at merge time`. The verifier reproduced this in a throwaway worktree.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS in both steps.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass (step 2).
- `bash plugins/sdlc-lite/scripts/check.sh`: pass in both steps. shellcheck is not installed on this host, so that leg did not run.
- `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass in both steps.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass in step 1 (209 tickets, roadmap current).
- `git diff --check`: clean in both steps.
- Diff scope: only `fanout.py` and `sdlc-internals.md` changed outside `.sdlc`, and there are no untracked files outside `.sdlc`.

Limits: per the burn-down brief there was no live run. The evidence is selftests and the gates. shellcheck was not exercised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `fanout.py` resolves regular lane ticket paths, including the planned-scope overlap check, through `tickets.ticket_dir`, so lanes now work on repos with `ticket_root: tickets`. Flat layouts are unchanged. The dry run adds a `ticket folders in each worktree:` line when the ticket dir differs from the root.

## Follow-ups
- note: The `ticket_root` lane selftest fixture relies on `tickets.py close` succeeding in a fresh repo with no router files, so a later change to close's router handling could turn it red for a reason outside `fanout.py`.
- note: shellcheck is not installed on the build host, so the shell lint leg of `check.sh` was never exercised for this change.
