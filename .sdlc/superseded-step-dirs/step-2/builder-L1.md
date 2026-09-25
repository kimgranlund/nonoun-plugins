<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/bench-summary.sh`: the skip for dirs not matching `^step-[0-9]+$` and its comment were already in the working tree. This pass replaced the `ls -t` verifier pick with a glob loop that keeps the newest `verifier-*.md` using `-nt`. The cost line is unchanged.

## Checks
- Fixture run with `SDLC_BENCH_DIR=<tmp>` and `step-1` (passing verifier, builder cost 1.00) plus `step-1.superseded-1` (builder cost 2.00): steps=1, passed=1, attempts=1, cost=3. The cost prints as `3`, not `3.00`, because the script formats it through `jq`.
- `shellcheck plugins/sdlc-lite/scripts/bench-summary.sh`: clean, no findings.

## Notes
Nothing was committed.
