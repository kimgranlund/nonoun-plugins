<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added five config-persistence cases to `selftest`, placed right after the `new --numbered` case. No change to production code.

## Checks
- `python3 tickets.py selftest` (run from `plugins/sdlc-lite/scripts`): rc=1, red as intended. The four cases below fail and are named in the output:
  - `new --numbered writes config with the numbered line`
  - `after new --numbered, plain check fails a renamed 0009-gamma` (rc=0)
  - `new --numbered keeps existing config lines and adds the numbered line once`
  - `new --numbered (twice) leaves one ticket_folders: numbered line`
- Negative control `plain new writes no config`: green. No other existing case fails.

## Notes
- The no-duplicate check has two variants. The `line present` variant already passes, because the config starts with exactly one numbered line and nothing adds to it yet. It is a guard for Step 2, not a red case. The `twice` variant is the red one.
- Lines are counted with `CONFIG_RE.fullmatch`, so a commented `# ticket_folders: numbered` line does not count toward the total.
- The rename case asserts this exact error text: `0009-gamma: folder prefix 0009- does not match id 'T-0003'`.
