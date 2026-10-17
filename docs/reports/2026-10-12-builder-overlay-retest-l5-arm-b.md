# Builder overlay retest, L5 arm B (T-0458 addendum)

Adds the cell the first report could not run. Evidence: `2026-10-12-builder-overlay-retest/rt-ndc-step2-L5-B-1/` and the run log line of 15:14Z in [`.sdlc/.0458-builder-overlay-retest/run-log.md`](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0458-builder-overlay-retest/run-log.md). The cap was raised from 20 to 30 USD for this cell (`.sdlc/notes.md`, 2026-10-12).

## Result

| arm | task | level | cost_usd | builder_min | blocked | block tag |
|---|---|---|---|---|---|---|
| A (no overlay) | ndc-step2 | L5 | 8.54 | 22.8 | yes | plan defect |
| B (overlay) | ndc-step2 | L5 | 10.36 | 33.7 | yes | plan defect |

- Both arms blocked on the same defect: the scope guard omits `scripts/bundle.mjs`, which the mandated chart imports require. The overlay did not change whether the builder blocked.
- Arm B cost 21 percent more and took 48 percent longer than arm A. One pair, so it shows no effect, not a cost increase.
- Ticket spend is about 29.7 USD (19.30 before this cell plus 10.36), under the raised 30 USD cap.

## Verdict

Overlay L5: no benefit shown (blocked rate 1 of 1 versus 1 of 1, cost up, n=1). Overlay L1: unchanged from the first report, no run tested blocking. The data does not support dropping either overlay or extending the set: the retest is inconclusive. The maintainer's 2026-10-11 decision to keep the overlays stands; T-0443 stays a separate decision.
