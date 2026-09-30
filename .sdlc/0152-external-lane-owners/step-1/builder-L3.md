<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `EXTERNAL_RE`, `external_branches(root)`, `branch_tickets(root, branch)` and the helper `unknown_branches(root, names)`. `id_floor` now also counts ticket ids on registered branches. `cmd_check` prints a warning for each registered name that is not a local branch. The docstring's usage block gained a `config` entry, and the `check` entry and the "Ids across git worktrees" paragraph were updated. The selftest gained cases (i) to (iv) inside the existing worktree block.

## Checks
- AC1 (`external_branches` returns `["codex/x", "ext"]` and `config_numbered` still holds): rc=0
- AC2 (registered branch holds T-0002, `new` mints T-0003): rc=0
- AC3 (branch holds `0002-b`, `.0003-c`, `_templates`, `plain`; `new` mints T-0004): rc=0
- AC4 (`check` prints `warning: external_branch nosuch is not a local branch`): rc=0
- AC5 (`"external_branch: <branch>"` in `tickets.__doc__`): rc=0
- AC6 guard (no registration, `new` mints T-0002 as before): rc=0
- AC7 guard `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, rc=0
- AC8 guard (scope diff against `$SDLC_BASE_SHA` touches only tickets.py): rc=0
- `git diff --check`: clean
- `python3 plugins/sdlc-lite/scripts/check.py`: ok, rc=0
- Negative controls: I applied 6 mutations to a scratch copy of the plugin under `mktemp -d`, removed afterwards; the unmutated copy passes. Each mutation made the selftest fail (rc=1) on the matching new case:
  - `id_floor` skips branches: new and close cases fail, the id comes out as T-0002.
  - The folder-name filter is removed: `_templates` gets counted.
  - The front-matter filter is removed: `plain` gets counted.
  - Name dedupe is removed.
  - The check warning is removed.
  - The warning also fires outside git.

## Notes
- `branch_tickets` runs `ls-tree` and `cat-file` from the git toplevel (`-C <top>`) and reads the anchor from the nearest existing directory. This means `<branch>:<rel>` paths resolve from the repo root even when the ticket root does not exist in the checkout. Selftest (ii) covers that case: `.sdlc` is absent on `main`.
- Beyond the spec, `branch_tickets` returns `[]` for an empty name or one starting with `-`, so a config value cannot be passed to git as an option. It also skips a folder name containing a newline, which would break the `cat-file --batch` input.
- Selftest (iii) checks the close follow-up on a copy of the repo taken before `new z`. That way the follow-up id T-0003 depends on the branch's T-0002 and not on a local ticket. Two further unregistered copies act as negative controls: `new` and the close follow-up both mint the colliding T-0002.
- The usage block describes the config lines as a `config` entry in the command list, even though `config` is not a subcommand.
