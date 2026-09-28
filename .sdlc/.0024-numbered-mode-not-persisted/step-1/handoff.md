## Task goal
Make `tickets.py new --numbered` persist `ticket_folders: numbered` in `<root>/config`. A plain `check` then enforces the NNNN-/id rule without a separate step. Constraint: the failing test lands before or with the fix, never after.

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

