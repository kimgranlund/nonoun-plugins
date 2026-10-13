# Plan eval cases

Six asks, one per kind, each with the kind the skill should resolve, the lint its result must pass, and the questions it should ask. The first five are the replay of the merge design (`.sdlc/.0462-plan-skills-merge-design/architect-L1.md`, Replay plan) and of the T-0467 handoff; the sixth comes from the T-0465 handoff.

- `<case>.ask.md`: the ask near-verbatim, then one `Source:` line naming where it came from.
- `<case>.expected.md`: line 1 `Kind: <kind>`, line 2 `Lint: ` and the backticked lint command of that kind, line 3 `Questions: ` and the count expected.

| Case | What it tests |
|---|---|
| 01-goal | no kind token and no `handoff.md`: the kind comes from the ask or one question; the block passes the goal lint |
| 02-fanout | two named tickets become one two-line fanout command with a `lanes:` line in the dry run |
| 03-doc | "so a smaller model can run it" resolves to a plan doc with the `control:` line in the dry run |
| 04-steps | an argument that names a `handoff.md` resolves to `steps` with no question |
| 05-campaign | "migrate every page" resolves to a campaign with a census and a partition |
| 06-compaction | the first token `compaction` selects the compaction kind with no question; the block passes the compaction lint and the return ends with `Run: /compact <paste>` |

## Ticket placeholders

The design's replay named T-0455, T-0456, T-0459 and T-0381. They are closed or dropped now, so the asks carry `<T-A>`, `<T-B>` and `<ticket folder>`. Fill them at run time with ready tickets from `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check` and the roadmap, and write the ids used into the replay record.

## Replay

1. Run `/sdlc-lite:plan` on each `.ask.md`, in a throwaway worktree, and save what it returns.
2. Compare the kind it resolved with line 1 of the `.expected.md`.
3. Run the command on line 2 over the returned block or file. Count a case as passing when the first return passes the lint with no fix round.
4. Count the `AskUserQuestion` questions asked and compare with line 3.
5. Record the two counts (cases passing the lint on first return, of 6; questions asked, summed) in a dated report. Mark the replay unverified when it was not an independent model run.

The question counts on line 3 are expectations from the skill text, not measurements: no replay has run yet.
