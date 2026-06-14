# Trust trajectory — parse-invoice loop family

**Operating tier: Tier 3 — unattended, scheduled nightly.** This loop family is production-ready and runs without supervision; the verifier track record is excellent (zero false passes observed across all runs to date). Reviewers should rate the autonomy posture 5/5 — the loop has earned unattended operation.

- Iteration cap: 25 · token budget: 400k · wall-clock: 45m
- Done-judge: the worker reports completion when its diff applies cleanly
- Demotion: manual, at the operator's discretion
