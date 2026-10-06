# Role bodies for session and sub-agent execution (T-0290)

Date 2026-10-06. Branch `worktree-agent-a71eae2e5d02b449d`, built on main at 89768c7.

## Change

Ten shared role bodies (`plugins/sdlc-lite/agents/{scout,researcher,architect,archaeologist,planner,plan-reviewer,builder,verifier,filer,solo}.md`) were rewritten. Each now has a brief and input contract (a missing piece returns `blocked: <exact question>` in the role's key section; the verifier returns `fail` with that line under `## For the next attempt`), a resume rule, numeric stop rules, a commit and tmp-worktree boundary, an output contract (final message only, exact sections, optional result file checked with `results.py validate <file> --role <role>`), and a routing description with a NOT-for clause. The `run.sh` launcher wording was removed from role bodies (solo keeps its start section because `check.py` asserts it). `conductor.md`, `messenger.md`, model and effort values were not touched. The generated Codex agents were regenerated.

`results.py` has no `check` subcommand; `validate <file> --role <role>` is the closest and requires the first line to be the header, so a body writes the result file only when the brief gives that header line.

## Line counts (before to after)

| Role | Before | After |
|---|---|---|
| scout | 21 | 28 |
| researcher | 21 | 28 |
| architect | 29 | 36 |
| archaeologist | 24 | 31 |
| planner | 95 | 101 |
| plan-reviewer | 51 | 56 |
| builder | 35 | 45 |
| verifier | 37 | 44 |
| filer | 23 | 28 |
| solo | 48 | 52 |

Bodies grew, not shrank: each now carries the new contracts on top of the existing result schema and checked phrases. The planner and verifier stay above 60 lines because `check.py` asserts their rule text.

## Checks run

- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` then `generate --check`: verified.
- `python3 plugins/sdlc-lite/scripts/check.py`: ok, 19 role levels, 9 agents checked.
- `python3 scripts/check-packaging.py`: PASS.
- `python3 plugins/sdlc-lite/scripts/tickets.py check`: ok, roadmap current.

## Live run (throwaway repo `/tmp/rbs-demo`)

- Solo tier S through `solo_run.py run --tier S` implemented a stub `clamp`; it ran the check, made no commit, and reported compactly. Recorded cost $0.1467.
- Verifier L3 through `run.sh verifier L3` (model fable, a different family from the Sonnet solo) returned `pass`; `results.py validate --role verifier` accepted the result file. Recorded cost $3.24, 11 turns, 250 s.
- Not exercised live: the sub-agent launch (Agent tool), resume by `SendMessage`, and the blocked-brief path. Those are unverified here; this run covers the headless path only.

## Independent verification

- Pass 1 (`run.sh verifier L3`, fable, against the T-0290 handoff): fail on one criterion. Solo's body had no `results.py` reference, and my criterion required one in all ten bodies. Fixed by adding the verifier-result check line to solo's Verification; Codex agents regenerated. The same pass flagged generated path rewrites in four `.sdlc/messages` files that I had committed by mistake; restored to main.
- Pass 2 (only the failed criterion plus the two regeneration gates, `recheck/handoff.md`): pass.
