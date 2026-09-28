<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: `inherited_red()` now reads `## Verdict` from `read[1]` when `len(read) == 2` (the verifier reported the inherited red). When the builder reported it, it still reads `## Status` from `read[0]`. I updated the function docstring, the module docstring's step-3 text, and the selftest docstring to match. I also added selftest case 5c: builder Status `done` plus a newer verifier Verdict `inherited red: test_v` must give the outcome `inherited red: step-1: test_v`.

## Checks
- Criterion 1 (verifier-inherited `test_verifier`): the grep matched, exit 0.
- Guard (builder-inherited `test_builder`): the grep matched, exit 0.
- Guard `cd plugins/sdlc-lite && scripts/check.sh`: exit 0. All selftests PASS (fanout included), plus ok for shellcheck and plugin validate.

## Notes
Nothing was committed. The fanout selftest prints nothing when it passes, so the log has no line for case 5c. It ran inside check.sh, which exited 0.
