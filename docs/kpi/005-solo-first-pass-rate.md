---
id: K-005
title: Share of verified solo tickets that pass the independent verifier on the first round
status: active
owner: maintainer
created: 2026-10-11
unit: percent
direction: up
target: ">= 85"
baseline: {value: 72, date: 2026-10-11, source: docs/reports/2026-10-11-solo-campaign-baseline.md, verified: true}
measure: python3 plugins/sdlc/scripts/solo_stats.py stats <repo> [<repo> ...] --since <date> [--until <date>]
read: first_pass / verified * 100 (the "first round pass" line); also "ended in a pass" and "multi-round" beside it
cadence: per retro
goals: [G-003]
---
## Definition
Of the solo tickets in the window that have an independent verifier (a `verifier-L<n>[-<round>].md` result file in the ticket folder), the share whose first verifier file reads `## Verdict` pass. A solo ticket is a ticket folder whose `runs.jsonl` holds a `solo` role row inside the window. Rounds are ordered by round number, then verifier level, never by file name. Tickets with no verifier (docs-only skip, the L1 default) are outside the denominator and are counted as "without a verifier".

## Reading it
- The command reads only each repo's main checkout `.sdlc`, hidden closed `.NNNN-*` folders included and worktree copies left out. Closed is a hidden folder; a repo that keeps closed tickets visible reports them as open (`open_done` counts those with a handoff status done or dropped).
- Baseline, 2026-10-11, `--since 2026-10-08 --until 2026-10-11T20:00:00Z` over ui-kit-maison, agent-ui, ultimate-tokens and sdlc-lite: 166 solo tickets (192 runs), 122 closed, 123 verified, 89 first-pass (72 percent), 107 ended in a pass (87 percent), 32 multi-round, 12 closed without a final pass. The run matches the hand tally in the baseline report. The `--until` instant is reconstructed so the run counts match (83 sdlc-lite and 78 ui-kit-maison solo runs); the tally's own clock was not recorded. Records written later, and tickets closed or verifier files added after the tally, move the counts, so a later run with the same window may differ.
- Not shown: whether a pass met the ticket's intent, rework after close, and solo against the chain.
- Cost is in the same output and stays a floor: only priced runs carry a cost (K-001). The baseline window priced 79 of 192 runs, $225.67, about $2.86 and 21 minutes a priced run; the unmetered 113 are counted and never estimated.

## History
- 2026-10-11: created with the baseline and `solo_stats.py` (T-0449).
