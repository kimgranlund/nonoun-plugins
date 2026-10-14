# Fleet retro interview

The exact message a conductor receives. Send it unchanged except `<retro root>` and `<date>`, which the retro fills in.

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

[V] means you ran the evidence yourself. Row rules:

- One mark per row: `[V]` or `[U]`. A row with a checked and an unchecked part is `[U]`; name the unchecked part in Mechanism. Any other mark (an emoji, "unverified") or none is written `[U]`.
- One finding per row. A bullet listing several symptoms is several rows. A note that names no symptom, cost, or gain is not a row. A proposed change goes in the Prevention cell of the finding it fixes; one with no finding behind it is left out.
- Fill every cell; write `none` where there is nothing to say (no fix exists, the cause is outside the plugin, a decision waits on the user).
- Something that got faster is a row: Symptom is what got faster, Cost the measured saving or `unmeasured`, Prevention `keep`.

Send the answer (max 80 lines, Part 1 on top) as one mailbox message, the
answer on stdin, and write no file in this repo:
`python3 <plugin>/scripts/messages.py --root <retro root> send --receiver fleet-retro --sender <this repo's folder name> --topic "fleet-retro <date>" --follow-up false -`
(`<plugin>` is the Part 1 plugin path). Reply with one line: the path `send` prints
and your top three findings.
