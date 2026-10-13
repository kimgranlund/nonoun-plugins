Goal: tickets T-0101, T-0102 and T-0103 are closed on `wave/7`.
Rules: at most 2 lanes run at once. No ticket closes on a verifier fail.
Decisions: agent 2026-10-12, T-0102 gets one replan (the criterion was wrong). User 2026-10-12, T-0102 pauses and the user is told when the replan fails. User 2026-10-12, T-0103 merges after T-0102 (both edit `config/limits.yaml`).
State: T-0101 is merged into `wave/7` and the gate `make test` is green. The T-0102 replan is building in lane b. T-0103 is verified in lane c and held.
Open: the budget of T-0102 is at $4 of $5; the raise at $5 is the user's decision.
Next: check the T-0102 replan build in lane b, then verify it.
