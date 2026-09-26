<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: added selftest case 6 (a full stub-driver run in the default lanes dir `.worktrees/fanout`, two lanes, two tickets) and one sentence for it in the module docstring's `selftest` paragraph.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS, exit 0.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (every selftest, shellcheck and plugin validate ok).
- Sabotage probe 1 (stray file written only under `.worktrees/`, and the selftest output must name `fanout-stray.txt`): exit 0.
- Sabotage probe 2 (`<id> <title>` commit subject makes the selftest fail): exit 0.
- `sed -n '/^selftest$/,/^"""/p' ... | grep -q 'default lanes dir'`: exit 0.
- `git diff --quiet HEAD -- tickets.py steps.py board.py`: exit 0.
- Observable check: `git diff HEAD -- fanout.py` has two hunks. One is at line 83, in the docstring. The other is at line 865, inside `selftest()`. No line above the selftest marker changed outside the docstring.

## Notes
- I did not rerun either sabotage probe at HEAD to confirm it is red before this step.
- Case 6 reuses the existing `stub` and `report_rows` helpers.
