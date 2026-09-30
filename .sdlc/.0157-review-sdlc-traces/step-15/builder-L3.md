<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/detectors/cost.py` (new): `detect(rows, aux, thresholds)` returns `(findings, notes)` for five detectors: cost-over-baseline, many-builder-attempts, polling-loop, background-denial and rate-limit.
- `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py`: added `cost_over_baseline_ratio` 2.0, `many_builder_attempts` 3 and `polling_loop_calls` 5, plus a severity for each of the five detectors (rate-limit 1, the others 2).
- `plugins/sdlc-lite/scripts/traces/detectors/__init__.py`: docstring now lists the cost family and its `(findings, notes)` return shape.
- `plugins/sdlc-lite/scripts/traces/ingest.py`: new `run(..., load_series=None)` parameter and `read_load_series(path)`. When a path is given, `aux['load_series']` holds the file's `[iso timestamp, load1]` pairs. Docstring updated.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: 14 `cost:` cases. That is fires and quiet-on-control for each of the five detectors, plus: the None-baseline note, a step whose newest verifier failed, the load-series value read through `ingest.run`, and pattern-matched polling (5 calls fire, 4 do not).

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost`: exit 0, 14 ok, PASS.
- The for-loop criterion over the five detectors (fires and quiet on control): exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost | grep -qF 'no baseline'`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/detectors/cost.py`: exit 0.
- (guard) scope, with `SDLC_BASE_SHA=7334f490936c50dec2d57a6979004a21562c9f28`: exit 0.
- Full `python3 plugins/sdlc-lite/scripts/traces.py selftest`: exit 0, 90 ok, no skips.
- `git diff --check`: exit 0.
- Mutation check, not saved to the tree: I monkeypatched the thresholds to 7 and 4, swapped the background regex, and forced every step to count as passed. The affected fires and quiet cases, the failed-verifier case and the load-series case all failed as expected.
- pyflakes is not installed here, so no lint was run.

## Notes
- The step says the load series is "given to ingest as `--load-series`, stored in aux", but no ingest CLI exists yet; step 16 adds it. I added only the library side (`ingest.run(load_series=PATH)` puts the pairs in `aux['load_series']`). Step 16 only needs to pass the flag through.
- `cost.detect` returns `(findings, notes)`. The other families return a plain list. Step 16's `detect` subcommand needs to unpack the tuple and print the notes.
- Choices the handoff left open:
  - A "step" is one handoff dir. cost-over-baseline looks only at live (non-superseded) step dirs, which matches how the bench baseline is computed. many-builder-attempts counts each dir separately, superseded dirs included.
  - "Passed" means the newest verifier by `order.newest` has verdict pass.
  - The ratio is rounded to 2 decimals and carried only on the first evidence entry, together with `cost_usd` and `baseline`.
  - A baseline of 0 or below is treated like None and gives the `no baseline` note.
  - polling-loop takes the larger of two groups: the most-repeated identical command, or all calls matching the polling regex. `secs` is None when a timestamp does not parse.
