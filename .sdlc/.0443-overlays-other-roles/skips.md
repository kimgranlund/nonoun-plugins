# Skips

## Lane
- lane: full; point: before planning; reasons: size L3 decides before planning (no planner result yet)
- lane: full; point: before planning; reasons: skips.md already records full, and a lane never returns from full

## Gate
- skip: planner, builder, verifier, filer; reason: gate not met. T-0458 report `docs/reports/2026-10-12-builder-overlay-retest.md` line 5 reads `Verdict: drop` (L1 drop, L5 unverified; the L5 arm-b addendum calls the retest inconclusive and says the data does not support extending the set). The ticket's Intent runs only on keep or extend, and its Context says to close as dropped on drop. Unattended, recommended option taken: stop before planning; no filer, since there are no artifacts to file. Close as dropped is left to /fanout.
