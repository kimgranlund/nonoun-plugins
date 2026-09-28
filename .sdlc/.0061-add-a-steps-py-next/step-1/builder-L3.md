<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: added the `next <step dir>` subcommand (`next_action`, `cmd_next`, and helpers for sections, Status, Verdict, plan defects and levels), documented it in the module docstring and argparse, and added 19 `next ` selftest checks.

## Checks
- Acceptance criteria 1 to 13 (build L2, verify L1, verify L3, replan on blocked, done, rebuild L2, replan on a plan defect, bump L3, rebuild L3 after a bump, stop at L5, stale verifier gives verify L1, missing-dir error, writes nothing): each command was pulled from the handoff and run with `bash -c`. All passed.
- `test "$(python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c '^ok: next ')" -ge 14`: passed (19 checks).
- (guard) `steps.py selftest | tail -1 | grep -qx 'steps selftest: PASS'`: passed.
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/order.py`: passed.
- (guard) The non-`next` `ok:` lines here match those from a `git worktree add --detach <tmp> HEAD` copy: 22 lines, `diff` shows no difference. The temporary worktree was then removed and pruned.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (shellcheck and plugin validate ok).
- Extra: `grep -c '—' steps.py` found 0 em dashes.

## Notes
- Pairing rule: each verifier is paired with the last builder in `order.ordered` for which `order.counts_after(verifier, builder)` is true. A counted fail is a non-plan-defect `fail` whose paired builder is at the newest builder's level.
- Parsing:
  - Status and Verdict are the first non-blank line under the heading, case-insensitive.
  - `plan defect:` must be at the start of the first non-blank line under `## For the next attempt`, after stripping whitespace. The check is case-sensitive.
  - Only `level: L1` to `level: L5` is accepted from the handoff.
- `read:` lines list only builder and verifier files. The handoff is not listed, even when its level is used.
- Five checks go beyond the handoff's case list: plan-defect fails do not count toward a bump, file times inverse to the run order are ignored, a handoff with no level line is refused, a builder with no done/blocked Status is refused, and a verifier with no pass/fail Verdict is refused.
- Nothing was committed.
