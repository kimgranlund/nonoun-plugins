<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `ensure_numbered_config(root)`. `cmd_new` calls it only when the `--numbered` flag is passed, after the handoff is written and before `write_roadmap`. Updated the module docstring and the `new --numbered` argparse help.
- `CLAUDE.md`: the `scripts/tickets.py` bullet now says a successful `new --numbered` persists the config line.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, exit 0.
- Manual check in a temp root: `new feature a --numbered` exited 0 and wrote `config` containing `ticket_folders: numbered`. After I renamed `0001-a` to `0009-a`, plain `check` exited 1 with a prefix mismatch error.
- Refusal case: `new feature 0007-x --numbered` in an empty temp root exited 1 on the double prefix. The dir was empty afterwards, so no config was written.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. Levels, selftests, shellcheck and plugin validate all ok.

## Notes
- I used `mktemp -d` roots instead of `/tmp/t` because a command containing `rm -rf` was denied by permissions.
- The config is written only when the flag is passed. A `new` that runs in numbered mode because of existing config does not rewrite the file.
- `git diff` also shows the step-1 selftest additions, which were still uncommitted in the worktree.
