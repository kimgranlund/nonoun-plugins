<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Fixture run with the new fanout.py: pass. I ran the handoff's command with `F` set to the built `plugins/sdlc-lite/scripts/fanout.py`. It exited 0, the integration handoff has `status: done`, and the tip subject is `close T-0001`.
- Negative control: pass. I extracted `plugins/sdlc-lite/scripts` from `git archive $SDLC_BASE_SHA` into a temp dir and ran the same fixture against its `fanout.py`. It exited 2, and its output contains `no ticket under` (grep count 1), so the check goes red on the base.
- `grep -qF "tickets.load(tickets.ticket_dir(root))" plugins/sdlc-lite/scripts/fanout.py`: pass. Exit 0.
- `grep -qF "ticket_root lane" plugins/sdlc-lite/scripts/fanout.py`: pass. Exit 0.
- `grep -qF "Regular lanes follow" docs/maintenance/sdlc-internals.md`: pass. Exit 0.
- `! grep -qF "Regular lanes do not follow" docs/maintenance/sdlc-internals.md`: pass. Exit 0.
- Diff scope limited to `fanout.py` and `sdlc-internals.md`: pass. Exit 0.
- No untracked files outside `.sdlc`: pass. Exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Exit 0, printing `fanout selftest: PASS`.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/fanout.py docs/maintenance/sdlc-internals.md`: pass. Exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Exit 0. It skipped shellcheck because it is not installed, and plugin validate was ok.
- (guard) `python3 scripts/check-packaging.py`: pass. Exit 0, printing `PASS`.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass. Exit 0, `ok: 209 tickets, roadmap current`.

I also read the diff against the Do list and it matches.
- The `tickets.Fail` handler is in place.
- `trel` is in ctx.
- `driver_for`, the `setup` missing check, `FANOUT_HANDOFF`, `inherited_red`, and the copy and clean paths use `trel`.
- The `git add -A -- relp` at line 759 still uses `rel`.
- `FANOUT_ROOT` still uses `rel`.
- The close command still uses `rel`.
- `print_plan` adds its line only when `trel != rel`.

## Out of scope changes
None. The only changed tracked files are `plugins/sdlc-lite/scripts/fanout.py` and `docs/maintenance/sdlc-internals.md`. The untracked files are all under `.sdlc/0204-fanout-resolver/step-1/`, which the untracked-files check excludes.

## For the next attempt
None
