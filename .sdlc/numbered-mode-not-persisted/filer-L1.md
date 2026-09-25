<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0024: new --numbered persists ticket_folders: numbered so plain check enforces the prefix

## PR body
### Summary
`tickets.py new --numbered` named the folder `NNNN-<slug>` but did not write `<root>/config`. A plain `check` therefore stayed in plain mode. A folder renamed to `0009-bar` that still held T-0002 passed with exit 0. After this change, a successful `new --numbered` adds `ticket_folders: numbered` to `<root>/config`. A later plain `check` then enforces the NNNN-/id rule with no separate step.

### Changes
- **Step 1: failing selftest first.** Added five config-persistence cases to `selftest` in `plugins/sdlc-lite/scripts/tickets.py`:
  - config is written
  - a renamed `0009-gamma` fails a plain `check`
  - existing config lines are kept
  - no duplicate numbered line
  - a plain `new` writes no config
- **Step 2: the fix.** Added `ensure_numbered_config(root)`. It does nothing if the config already turns numbered mode on. Otherwise it appends the line, creating the file if needed. `cmd_new` calls it only when `--numbered` was passed, after the handoff is written and before `write_roadmap`. A refused `new` writes no config. Updated the module docstring, the `--numbered` help, and the `scripts/tickets.py` bullet in CLAUDE.md.

### Verification
- **Step 1 (verifier L1: pass).** `selftest` exited 1 and named the four new red cases. The rename case failed with `rc=0 ''`, which shows its assertion can go red. The negative control `plain new writes no config` was green.
- **Step 2 (verifier L1: pass).**
  - `selftest` exited 0.
  - Manual check in a mktemp root: `new feature a --numbered` wrote `config` with `ticket_folders: numbered`. After `mv 0001-a 9999-a`, plain `check` exited 1 with `folder prefix 9999- does not match id 'T-0001'`.
  - At HEAD, in a throwaway worktree, the same `new --numbered` left no config, so this check does fail without the fix.
  - Refusal case `new feature 0007-x --numbered` exited 1 and left the root empty.
  - `scripts/check.sh` exited 0, including shellcheck and plugin validate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `tickets.py new --numbered` now writes `ticket_folders: numbered` to `<root>/config`, so a later plain `check` enforces the folder prefix/id match (T-0024).

## Follow-ups
- tickets.py: `check` should warn when every ticket folder has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered` (e.g. gen-ui-system-svelte-lite, whose numbered folders predate T-0024)
- tickets.py: `close --numbered` does not persist `ticket_folders: numbered`, so a repo that only ever ran `close --numbered` stays in plain check mode
