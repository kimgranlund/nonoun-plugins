<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: `verdict_or_none` now returns `'inherited'` when the first line under `## Verdict` starts with `inherited red:` (any case). `next_action` returns `inherited` for a newest verifier that counts after the build. The docstring `next` rules gain the new line. Five selftest cases added.
- `plugins/sdlc-lite/scripts/board.py`: in `step_row`, an inherited verifier renders `🔴 inherited red · builder <L> · verifier <L>, ask the user<tries>`. The no-verdict loop counts `inherited red:` as a verdict. Docstring updated and one selftest case added.
- `plugins/sdlc-lite/scripts/run.sh`: the verifier's allowed value is now `pass|fail|inherited red: .+`, and the header comment on line 19 is updated.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: added `want_rc 0 verifier L1 $'## Verdict\ninherited red: test_a'` and `want_rc 3 verifier L1 $'## Verdict\ninherited red'`.

## Checks
All commands were run from the worktree root. Each criterion was run verbatim under `bash -c`.
- c1 (`steps.py next`, inherited verifier gives `inherited`): PASS
- c2 guard (fail verifier gives `rebuild L2`): PASS
- c3 guard (bare `inherited red` gives `reverify L1`): PASS
- c4 (board `step_row` inherited verifier gives 🔴 `inherited red...`): PASS
- c5 guard (board fail verifier gives 🔴 `fail...`): PASS
- c6 `grep -q 'Verdict\\ninherited red: ' plugins/sdlc-lite/scripts/steps.py`: PASS
- c7 same grep on `board.py`: PASS
- c8 `grep -q "want_rc 0 verifier L1 .*inherited red: " ...run-selftest.sh`: PASS
- c9 `grep -q "want_rc 3 verifier L1 .*inherited red'$" ...run-selftest.sh`: PASS
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS (rc 0)
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS (rc 0)
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: PASS (rc 0)
- `plugins/sdlc-lite/scripts/check.sh` (extra, repo-wide): rc 0, including shellcheck and plugin validate

## Notes
- The inherited check in `next_action` comes after the no-verdict branch and before `pass`, plan defect, and fail counting. The counting loop only counts `== 'fail'`, so an inherited verdict is never a fail. The no-verdict run loop stops at any non-None verdict, so an inherited verdict ends that run.
- The `.sdlc/verifier-fail-on-a-gate/` files were already modified or untracked before this step, and I did not touch them. Nothing was committed.
