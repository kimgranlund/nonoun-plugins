<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Make `tickets.py new --numbered` persist `ticket_folders: numbered` in `<root>/config`. A plain `check` then enforces the NNNN-/id rule without a separate step.

## Step 1: Failing selftest first
level: L2
### Do
In the `selftest` in `plugins/sdlc-lite/scripts/tickets.py`, after the "new --numbered" case (around line 594), add these cases:
- **Renamed folder fails plain check.** Run `new --numbered` on a fresh case. Then rename `0003-gamma` to `0009-gamma`, which holds T-0003. Regenerate the roadmap the way the existing rename cases do. Assert that a plain `check` (no flag) returns rc 1 and names the prefix mismatch.
- **Config is written.** After `new --numbered`, assert that `<root>/config` exists and `config_numbered(root)` is True.
- **Existing config is kept.** Start from a config containing `# keep me\nother: x\n` and run `new --numbered`. Assert the original lines survive and the numbered line is added exactly once.
- **No duplicate line.** Run `new --numbered` twice, or run it with the config line already present. Assert that only one `ticket_folders: numbered` line exists.
- **Plain mode writes nothing.** Run `new` with no flag. Assert that no `config` file is created.

Run `python3 tickets.py selftest` and confirm the new cases fail before Step 2 (red first).
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits non-zero, and the failure output names the new cases.
- The negative control (the plain `new` case) is already green.

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

## Risks
- Existing selftest cases may assume `new --numbered` leaves no config file. For example, the "plain mode" negative controls or the `snap` comparisons. Re-run the full selftest to catch these.
- The `close --numbered` follow-ups do not write config by this plan. It is unneeded, since the parent `new` already did, but a repo that only ever ran `close --numbered` stays in plain mode.
