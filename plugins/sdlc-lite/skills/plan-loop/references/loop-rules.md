# Loop rules

Labels: from the host (the `/loop` skill and tool descriptions in Claude Code), observed here, or unverified. Codex's `/loop` behavior is unverified.

| Rule | Detail | Label |
|---|---|---|
| Interval token | A leading `^\d+[smhd]$` token, or a trailing `every N unit` clause. Anything else, including `20mins:`, is dynamic mode with the whole text as the prompt | from the host; the `20mins:` mistake was made in this repo's thread |
| Cron mapping | `Nm` with N up to 59 becomes `*/N * * * *`; N at least 60 becomes hours and must divide 24; `Nh` up to 23 becomes `0 */N * * *`; `Nd` becomes `0 0 */N * *`; seconds round up to a minute. An interval that does not divide its unit rounds to a clean one | from the host |
| Avoid `:00` and `:30` | Approximate requests should land off the half hour | from the host |
| Lifetime | Recurring jobs expire after 7 days and fire only while the session is idle | from the host |
| Dynamic mode | No interval: run now, then re-arm with a heartbeat of 1200 to 1800 seconds unless an event wakes it; the runtime clamps delays to 60 to 3600 seconds | from the host |
| Events over polling | A monitor streams events and wakes the loop; it expires after at most 30 minutes | from the host |
| Prompt shape | Self-contained, idempotent, reads state from files or commands, reports progress since the last run, ends on a stop condition | observed: the status loop in this repo's thread restated progress each fire |
| Cost | Each fire is a model turn: choose the longest interval that fits the need | inferred |
| No status loops | A fixed-interval prompt that watches running work (status, board, progress, waiting on, land, dispatch) fails `status-polls-running-work`: a background role's completion notification already wakes the session. For a plan doc use the driver turn in [run-plan](../../run-plan/SKILL.md) | observed: maison's 10-minute check reported "nothing moved" dozens of times |

Example: `/loop 20m check the deploy health and report what changed since the last run; stop when the notes file says done` (`notes.md` in `.sdlc/`, `.sdlc/notes/notes.md` with `layout: topics`, `docs/work/NOTES.md` with `work_root: docs/work`)
