## Task goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Step 4: run.sh verifier swap and bench-summary.sh use order.py
level: L2
### Do
- `plugins/sdlc-lite/scripts/run.sh`: replace `ls -t "$dir"/builder-L*.md | head -1` with `python3 "$plugin_root/scripts/order.py" newest "$dir" builder`. Keep `|| true` and an empty result meaning no build.
- `plugins/sdlc-lite/scripts/bench-summary.sh`: replace the `-nt` loop with `v=$(python3 "$root/scripts/order.py" newest "$s" verifier)`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: add a dry-run case (`SDLC_DRY_RUN=1`) in the throwaway repo, with a step dir holding:
  - `builder-L5.md` (header `model=fable`)
  - `builder-L1.md` (header `model=sonnet`)
  - equal mtimes
  - a runs.jsonl recording L1 first and L5 last

  Then `run.sh verifier L2` must print `--model opus` and `--effort medium`: Fable swapped to Opus, the effort left as is. Add the mirror case, where the records show L1 last, so verifier L1 (Sonnet) swaps to `--model opus --effort medium`, and verifier L2 stays `fable`.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`. Reverting the swap line to `ls -t` makes it FAIL.
- Copy `bench/results/2026-09-24-button-geometry-model` into `<tmp>/results/`, `touch` every file to one time, and run `plugins/sdlc-lite/scripts/bench-summary.sh --bench-dir <tmp>`. It reports `3` steps and `3` passed.
- `grep -nE "ls -t|-nt " plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/bench-summary.sh` prints nothing.
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/*.sh` is clean.
