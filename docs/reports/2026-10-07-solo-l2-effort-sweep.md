# Solo L2 (Sonnet) effort sweep: high versus xhigh (T-0357)

Date: 2026-10-07. Status: experiment record, uncommitted. `adapters/claude/levels.json` was not touched.

## Question

Does solo L2 (Sonnet) at effort high pass everything it passes at xhigh, at lower cost?

## Method

- Eight closed L1 or L2 tickets with runnable Done-when checks: T-0343, T-0344, T-0345, T-0346, T-0347, T-0348, T-0349, T-0350. Each pre-change state is the parent of the ticket's implementation commit (`git archive` extract, `git init`, one commit), so no checkout shared history with the real repo. Parents: f2eb500d (0343, 0344, 0345, 0347, 0348), e0b10b3c (0346), 4290c22c (0349, 0350). T-0340 was dropped because its parent predates the L1 to L3 tier rename (`solo_run.py run --tier L2` did not exist there); T-0345 replaced it.
- Two checkouts per ticket under `/tmp/sweep-t0357/<ticket>/{high,xhigh}`. All tickets were run as tier L2 whatever their own `size:` (six are L1 tickets), because the question is about the solo L2 row.
- Per arm: `solo_run.py run --task-dir ... --tier L2 --brief "<ticket handoff, deliver per Goal and Done when, no commit>"` printed the dispatch JSON; its `prompt` was passed unchanged to the session.
- Effort method: the Agent tool takes no effort parameter, so each arm was launched as `SDLC_ROLE=solo claude -p --plugin-dir <checkout>/plugins/sdlc-lite --agent sdlc-lite:solo --model sonnet --effort high|xhigh --dangerously-skip-permissions --output-format json -- "<dispatch prompt>"` in its checkout. This is the same command `solo_run.py run --exec` builds, with `--effort` varied. No `dispatch.py record` was run; cost and duration come from the session result JSON (`total_cost_usd`, `duration_ms`), so they are metered, not estimated.
- At most 8 sessions ran at once.
- Judging: the Done-when commands were run by me in each checkout after the session ended: `check.py`, `tickets.py --root .sdlc check`, and the ticket's touched selftest (dispatch, solo_run, steps, tickets, hook-selftest; plus fanout and `codex_roles.py generate --check` for 0349 and 0350). I also confirmed each arm changed the target script and added selftest cases. For T-0344 I additionally ran the reference commit's `hook-selftest.sh` (fb4cc400) against each arm's hook: it fails on the pre-change tree (exit 2 on trailing text) and passes on both arms, so that one is a real behavior check. For the other seven the only behavior evidence is the arm's own new selftest cases; the existing selftests all pass on the unchanged baseline too (checked on T-0346), so they alone do not discriminate.

## Results

| Ticket | High pass | xhigh pass | High cost | xhigh cost | High time | xhigh time | Turns (h / x) |
|---|---|---|---|---|---|---|---|
| T-0343 record artifact from transcript | pass | pass | $0.77 | $5.14 | 12.0 min | 36.8 min | 25 / 50 |
| T-0344 spawn hook Handoff line | pass | pass | $0.40 | $0.75 | 3.8 min | 5.7 min | 14 / 22 |
| T-0345 solo_run default worktree | pass | pass | $0.71 | $3.75 | 6.2 min | 17.8 min | 19 / 45 |
| T-0346 solo_run silent JSON failure | pass | pass | $0.36 | $0.71 | 1.2 min | 8.3 min | 10 / 21 |
| T-0347 lint criteria count and dir | pass | pass | $0.62 | $1.61 | 4.2 min | 21.3 min | 19 / 43 |
| T-0348 close --keep-refs | pass | pass | $0.55 | $1.32 | 4.3 min | 10.7 min | 16 / 39 |
| T-0349 record truncated stdin | pass | pass | $0.60 | $1.00 | 11.2 min | 10.2 min | 18 / 25 |
| T-0350 solo live marker cleanup | pass | pass | $0.68 | $1.03 | 7.6 min | 8.1 min | 21 / 29 |
| Total | 8 of 8 | 8 of 8 | $4.69 | $15.32 | 50.5 min | 118.8 min | 142 / 274 |

Per-criterion detail: every arm was green on `check.py`, `tickets.py check`, and the touched selftests (dispatch, solo_run, steps, tickets, hook, and for 0349 and 0350 also fanout and `codex_roles.py generate --check`). Nothing failed in either arm, so there is no per-criterion difference to list.

High matched xhigh on every ticket: yes (8 of 8 pass at both).

High cost 31 percent of xhigh in total ($4.69 versus $15.32), took 43 percent of the wall time. Total sweep spend about $20, far under the $60 stop line.

## Observations

- xhigh made larger changes on the same tickets: T-0344 hook diff 53 lines versus 9 at high, T-0345 `solo_run.py` +209 versus +85, T-0346 +75 versus +23, T-0347 +189 versus +117, T-0348 +137 versus +89. Larger is not shown to be better here; both passed. No review of code quality was done beyond the Done-when checks.
- T-0346 high ran in a lane worktree, not the main checkout. My own test invocation of `solo_run.py run` left a live marker in that checkout, so the real T-0345 behavior (default to a worktree when another solo is live) routed the dispatch there. I judged the worktree's diff and ran the same commands in it. This is a handling artifact of mine, not a high-effort effect; the other 15 arms ran in their checkouts.
- Several tickets asked the agent to first reproduce the report and close with a note if it could not. Every arm reproduced it and changed code.

## Limits

- One run per arm per ticket, no variance estimate, and sessions are non-deterministic. An 8 of 8 tie with n=8 cannot exclude a failure rate of tens of percent at either effort.
- The judge is the Done-when commands plus a diff inspection, mostly the arm's own selftests. Only T-0344 has an independent reference check. A subtle behavior miss in the other seven would not show.
- All eight are small script and hook fixes on one codebase, mostly L1 tickets run under the L2 row. Larger, multi-file, or ambiguous L2 tickets are not represented.
- No independent verifier (the verifier L2 step the solo flow hands off to) was run on either arm.
- Cost is the session total; per-run cost at xhigh here ($0.71 to $5.14) is lower than the fleet average ($3.31 to $5.53), so these tickets are cheaper than typical.
- The sweep used the pre-change plugin from each ticket's parent commit, not the current main plugin.

## Recommendation

Drop solo L2 to high: partly. The evidence supports it for small L1-sized scripted fixes (8 of 8 matched, about 69 percent cheaper, about 57 percent faster) but is thin for real L2 tickets. Suggested next step if the user wants the change: add a second sweep of 6 to 8 larger L2 tickets with an independent reference check per ticket before editing `levels.json` and locking the eval, or switch only after that. `levels.json` was not changed.
