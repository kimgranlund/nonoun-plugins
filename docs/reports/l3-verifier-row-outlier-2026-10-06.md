# L3 verifier row: accepted outlier (T-0336)

Dated 2026-10-06. Supersedes nothing; it narrows the claim in `subagent-mode-live-2026-10-07.md` and the T-0328 and T-0331 conditions.

## Finding

The L3 fable verifier of the live run (agent a904ad1cad883ca4b: input 198, output 8288, cache read 332971, cache write 51769) prices at 0.570 of the host figure 2.4762 with the T-0332 refit (about 1.41 USD). That is outside the 0.65 to 1.35 band. Its stored rows do not repair it: `L3-runs.jsonl` holds only a notice count (0.069 of host) and `transcript-summary.txt` holds an all-lines sum (1.438 of host).

## Decision

No refit. A refit that lifts L3 to 0.65 would push the L2 row (0.93 to 1.09) and the G and F rows above the band, because the fitted factors (input x225, output x1.27) already sit at the limit the other rows allow. The L3 row is accepted as an outlier.

## Narrowed claim

The 35 percent band holds for the L2 opus verifier row and for the G, F and R1 fable verifier rows (0.745, 0.830, 0.847). It does not hold for the L3 fable verifier row (0.570). Its cause is not established: the guess that its cache read and write counts differ in kind from the other rows is untested, and its surviving transcript cannot confirm it. `cost_estimate.py selftest` pins the 0.570 figure so a later change to the factors that moves it is noticed.
