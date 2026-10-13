# Fixture: lane wave

A written fixture, not a recorded session. Date in the session: 2026-10-12.

Turn 1 user: Run wave 7: tickets T-0101, T-0102 and T-0103 in parallel lanes, merged into `wave/7`. Goal: all three closed on `wave/7`.
Turn 2 agent: The dry run shows lanes a, b and c with no overlap.
Turn 3 user: Rule: at most 2 lanes at once, this machine is loaded.
Turn 4 user: Rule: never close a ticket on a verifier fail.
Turn 5 agent: Lanes a (T-0101) and b (T-0102) are open. Lane c waits.
Turn 6 agent: Lane a finished: T-0101 verified, pass.
Turn 7 agent: Lane a merged into `wave/7`. The gate `make test` is green.
Turn 8 agent: Lane c (T-0103) is open.
Turn 9 agent: Lane b: the T-0102 verifier failed, `test_retry_backoff` is red.
Turn 10 agent: I chose one replan for T-0102, not a manual fix, since the criterion was wrong.
Turn 11 user: Agreed. If the replan fails too, pause T-0102 and tell me.
Turn 12 agent: Recorded: user 2026-10-12 caps T-0102 at one replan, then pause.
Turn 13 agent: Lane c: T-0103 touches `config/limits.yaml`, which T-0102 also edits.
Turn 14 user: Merge T-0103 after T-0102, not before. I decide that order.
Turn 15 agent: Recorded: user 2026-10-12 orders the merge T-0102 then T-0103.
Turn 16 agent: T-0102 replan is building. T-0103 is built and verified, pass, and is held.
Turn 17 agent: Open: the budget for T-0102 is at $4 of $5.
Turn 18 user: I will decide on a budget raise when it reaches $5. Compacting now.

## Probe questions

1. How many lanes may run at once? Expected: at most 2 (turn 3).
2. T-0103 is verified. May it merge now? Expected: no, after T-0102 (turn 14).
3. The T-0102 replan fails. What happens? Expected: pause T-0102 and tell the user (turn 11).
4. May T-0102 be closed on a verifier fail if the fix looks small? Expected: no (turn 4).
5. What is the next action and what is still open? Expected: wait for the T-0102 replan build; the budget raise is the user's decision at $5 (turns 16 to 18).
