<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: the verifier swap now finds the newest build with `python3 "$plugin_root/scripts/order.py" newest "$dir" builder 2>/dev/null || true`. An empty result still means no build.
- `plugins/sdlc-lite/scripts/bench-summary.sh`: replaced the `-nt` loop with `v=$(python3 "$root/scripts/order.py" newest "$s" verifier)`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: added a dry-run swap case in `.sdlc/t/step-1`. It uses `builder-L5.md` (fable) and `builder-L1.md` (sonnet) with the same mtime, and runs.jsonl in both orders. The asserts:
  - L5 last: verifier L2 prints `--model opus --effort medium`.
  - L1 last: verifier L1 prints `--model opus --effort medium`.
  - L1 last: verifier L2 prints `--model fable --effort medium`.

## Checks
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`.
- Negative control: I put the swap line back to `ls -t ... | head -1` and the selftest failed: `FAIL: L5 newest: verifier L2 should swap fable ... got: ... --model fable --effort medium`. I then restored the change and it printed PASS again.
- I copied `bench/results/2026-09-24-button-geometry-model` to `<tmp>/results/` and set every file to the same time with `touch -t`. `bench-summary.sh --bench-dir <tmp>` reported steps `3` and passed `3`.
- `grep -nE "ls -t|-nt " run.sh bench-summary.sh` printed nothing (exit 1).
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/*.sh`: clean (exit 0).

## Notes
- In run.sh I added `2>/dev/null` before `|| true` on the order.py call, the same way the old `ls` line hid its errors.
- `order.py` crashes with an IndexError when run with no args while printing its usage (`__doc__` split). This was already the case and is outside this step.
- In dry-run mode, run.sh leaves its skill `mktemp` file behind because it exits before the trap is set. This is also existing behavior; I did not change it.
