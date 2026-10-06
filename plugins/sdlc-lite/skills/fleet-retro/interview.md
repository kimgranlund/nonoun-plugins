# Fleet retro interview

The exact message a conductor receives. Send it unchanged.

---

You are being asked for a retro on how the sdlc-lite plugin served this repo.
Rules: measure only, start no new work, and never edit another repo. Counts and
costs come from the collector, not from you; quote its numbers and do not
estimate your own. Mark anything you did not check yourself [U].

## Part 1: environment (answer first, from commands, not memory)

1. The plugin version path in use (the folder holding `scripts/tickets.py`).
2. `claude --version`.
3. The time now (`date`) and a load snapshot (`uptime`).

## Part 2: questions (at most 5, one short answer each)

1. Top stalls: what stopped or slowed work, the cause, and what would have prevented it.
2. Friction ranked by cost, in dollars or minutes.
3. Decisions that were blocked waiting on the user.
4. What the plugin made faster or slower.
5. Anything you could not verify, marked [U].

## Answer format

One row per finding, ranked by cost, at most 7 rows:

| Symptom | Evidence (command or log path) | Mechanism | Cost | [V] or [U] | Prevention |
|---|---|---|---|---|---|

[V] means you ran the evidence yourself. Write the answer to
`.sdlc/fleet-retro-<date>.md` (max 80 lines), with Part 1 on top.
Reply with one line: the path and your top three findings.
