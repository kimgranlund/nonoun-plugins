## Task goal
Make `tickets.py new --numbered` persist `ticket_folders: numbered` in `<root>/config`. A plain `check` then enforces the NNNN-/id rule without a separate step. Constraint: the failing test lands before or with the fix, never after.

## Step 2: Persist the config in `new --numbered`
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, add a helper `ensure_numbered_config(root)`.
- If `config_numbered(root)` is already True, do nothing.
- Otherwise append `ticket_folders: numbered\n` to `<root>/config`. Create the file if it is missing. If the existing file lacks a trailing newline, add one first.

Call it in `cmd_new` after the folder and handoff are written, only when the `--numbered` flag was passed. Do this before `write_roadmap`, and only after success. A refused `new` must leave no config behind.

Update the docstrings and usage text at lines 5-9 and the `--numbered` help at line 831. Update the CLAUDE.md `scripts/tickets.py` bullet so that `--numbered` on `new` is described as persisting the config line.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0.
- Manual check in a temp root: `tickets.py --root /tmp/t new feature a --numbered` creates `/tmp/t/config` containing `ticket_folders: numbered`. After renaming the folder to a wrong prefix, `tickets.py --root /tmp/t check` exits 1.
- Refusal case: `new --numbered 0007-x` (double prefix) exits non-zero and writes no config.
- `plugins/sdlc-lite/scripts/check.sh` passes, including shellcheck and the plugin validate step.

