# Solo campaign baseline, 2026-10-08 to 2026-10-11

Recorded: 2026-10-11. Window: tickets whose `runs.jsonl` holds a `solo` role row dated 2026-10-08 or later, in ui-kit-maison, agent-ui, ultimate-tokens and sdlc-lite (gen-ui-kit had none). Method: a one-off script over each repo's `.sdlc` folders (hidden closed `.NNNN-*` folders included, worktree copies excluded), not a committed tool and not independently checked. T-0449 builds the committed version and must reproduce these counts.

| Count | Value |
|---|---|
| Solo tickets / solo runs | 166 / 192 |
| Closed / open | 122 / 44 (open includes in-flight and a folder-layout artifact) |
| Tickets with an independent verifier | 123 (43 had none: docs-only skip and L1 default) |
| First verifier round pass | 89 of 123 (72 percent) |
| Ended in a pass | 107 of 123 (87 percent) |
| More than one verifier round | 32 |
| Closed without a final pass | 12 (inherited, deferred or superseded verdicts) |

By repo (first pass, ended in pass, verified): sdlc-lite 50 and 54 of 60; ui-kit-maison 30 and 42 of 49; ultimate-tokens 7 and 9 of 9; agent-ui 2 and 2 of 5.

Cost: priced only in sdlc-lite, 83 solo runs, 75 metered, $222.93, about $3 a run and about 20 minutes. ui-kit-maison 1 of 78 priced, ultimate-tokens 0 of 20, agent-ui 2 of 11 (K-001).

Not shown: whether a pass met the ticket's intent; rework after close; solo against the chain on cost per closed ticket. Verifier files are ordered by round number (`verifier-L2.md`, `-2`, `-3`); a first draft ordered them by name and misread rounds.

Reproduced by the committed script (T-0449): `python3 plugins/sdlc-lite/scripts/solo_stats.py stats <the four repos> --since 2026-10-08 --until 2026-10-11T20:00:00Z` prints 166 tickets, 192 runs, 122 closed, 44 open, 123 verified, 89 first-pass, 107 ended in pass, 32 multi-round and 12 closed without a final pass, and by repo the first-pass, ended-in-pass and verified counts above. Two rules the first draft left implicit: closed means a hidden `.NNNN-*` folder (25 of the 44 open tickets are agent-ui, ultimate-tokens and ui-kit-maison folders that keep their closed tickets visible with a handoff status of done or dropped), and two verifier files of different levels (`verifier-L2.md`, then `verifier-L3.md`) are two rounds. The `--until` instant is not in the tally; it is the instant that reproduces its run counts (83 sdlc-lite, 78 ui-kit-maison). Priced runs in that window: 79 of 192, $225.67.
