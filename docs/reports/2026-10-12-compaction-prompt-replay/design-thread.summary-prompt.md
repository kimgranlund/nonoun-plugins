Goal: one ratified retry design for the webhook sender in `docs/design/webhook-retry.md`.
Rules: no new runtime dependency. Every duration is in seconds.
Decisions: user 2026-10-12, backoff is exponential with jitter (receivers throttle bursts). User 2026-10-12, the attempt cap is 8 (one day of coverage). Agent 2026-10-12, failed events go to the `dead_events` table (no new dependency).
State: the draft holds sections 1 and 2; section 3 is not written. The proposed base delay is 10 seconds.
Open: the delay ceiling of 3600 seconds is proposed and not decided. Who replays dead events (operator command or cron job) waits on the user asking ops.
Next: write section 3 of `docs/design/webhook-retry.md`.
