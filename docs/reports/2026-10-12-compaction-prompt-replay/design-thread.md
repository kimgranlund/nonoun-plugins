# Fixture: design thread

A written fixture, not a recorded session. Date in the session: 2026-10-12.

Turn 1 user: Design the retry policy for the webhook sender. Goal: one ratified design written to `docs/design/webhook-retry.md`.
Turn 2 agent: Three decisions are open: the backoff curve, the attempt cap, and where failed events go.
Turn 3 user: Rule: no new runtime dependency.
Turn 4 user: Rule: write every duration in seconds, never milliseconds.
Turn 5 agent: Backoff options: fixed 30 seconds, or exponential with jitter.
Turn 6 user: Exponential with jitter. The receivers throttle bursts.
Turn 7 agent: Recorded: user 2026-10-12 picks exponential backoff with jitter.
Turn 8 agent: Attempt cap options: 5 or 8.
Turn 9 user: 8 attempts. One day of coverage matters more than queue size.
Turn 10 agent: Recorded: user 2026-10-12 sets the cap at 8 attempts.
Turn 11 agent: I propose a base delay of 10 seconds and a ceiling of 3600 seconds.
Turn 12 user: Not sure about the ceiling yet. Leave it open.
Turn 13 agent: I chose to store failed events in the existing `dead_events` table, since a new queue needs a dependency.
Turn 14 user: An earlier idea was a Redis queue. Forget it, rule one forbids it.
Turn 15 agent: The draft of `docs/design/webhook-retry.md` holds sections 1 and 2. Section 3 (dead events) is not written.
Turn 16 agent: Open question: who replays dead events, an operator command or a cron job?
Turn 17 user: I will answer after I talk to ops. Write section 3 next. Compacting now.

## Probe questions

1. What is the attempt cap? Expected: 8 (turn 9).
2. May the design add a Redis queue? Expected: no, no new runtime dependency (turns 3 and 14).
3. In which unit are durations written? Expected: seconds (turn 4).
4. Where do failed events go? Expected: the existing `dead_events` table (turn 13).
5. What is the next action and what is still open? Expected: write section 3; the delay ceiling and who replays dead events are open (turns 12, 16, 17).
