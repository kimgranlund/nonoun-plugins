# Verification of the sub-agent mode tickets, 0.21.0 (T-0333)

12 tickets closed on the solo lane with no verifier verdict. Each has a verdict file here (`<ticket>.md`).

Result: 9 pass, 3 fail (T-0280, T-0328, T-0331). Each fail has a filed ticket: T-0334, T-0335, T-0336.

| Ticket | Verdict | Verifier batch | Failed criteria | Filed |
|---|---|---|---|---|
| T-0275 | pass | probes |  |  |
| T-0279 | pass | dispatch-supervisor |  |  |
| T-0280 | fail | cost-a | T0280-2 | T-0335 |
| T-0284 | pass | solo-record |  |  |
| T-0286 | pass | dispatch-supervisor |  |  |
| T-0326 | pass | fanout |  |  |
| T-0327 | pass | fanout |  |  |
| T-0328 | fail | cost-a | T0328-1 | T-0336 |
| T-0329 | pass | fanout |  |  |
| T-0330 | pass | solo-record |  |  |
| T-0331 | fail | cost-b | T0331-1, T0331-3 | T-0334 and T-0336 |
| T-0332 | pass | cost-b |  |  |

## How it ran

- Mode: sub-agents through `dispatch.py` (the new mode under test): `dispatch.py prepare verifier L3 <handoff>` for six batches, the Agent tool with exactly the printed JSON (six `sdlc-lite:verifier-L3` spawns in one block, foreground), then `dispatch.py record --transcript` per batch (all six exit 0, result validated). `run.sh` was not used.
- Model: verifier L3 is fable xhigh; every transcript message reads `claude-fable-5-1`. Every builder was solo sonnet low (`runs.jsonl` of each closed folder, except T-0332, which was fixed inside the live rerun commit and has none), so the family differs.
- Batches (criteria and result under `.sdlc/verify-subagent/<batch>/`): `probes` (T-0275), `dispatch-supervisor` (T-0279, T-0286), `cost-a` (T-0280, T-0328), `cost-b` (T-0331, T-0332), `solo-record` (T-0284, T-0330), `fanout` (T-0326, T-0327, T-0329). Each verdict file carries its ticket's criteria lines verbatim; the batch result is the full text.
- Estimated verifier cost, from `runs.jsonl` (`cost_estimated: true`): about 36.6 USD across the six runs, 4.8 to 7.7 each.
- T-0333's own verifier (L3, same mode, records in `.sdlc/0333-verify-subagent-tickets/`): the first run failed A6 because `check.py`'s link check reads `git ls-files` and the three new ticket folders were untracked while `roadmap.md` linked them; after they were staged (no content change) the second run passed. About 6.3 USD estimated for the two runs.
- Tree under test: v0.21.0 plus three doc-only commits (`git diff --stat 027da15a HEAD -- plugins` is empty). Nothing was fixed.

## Fails and their tickets

- T-0280, criterion T0280-2: cost_basis label for transcript pricing is `usage fields x rates`, the criterion pins `transcript usage x price`, and a docstring is stale. Ticket T-0335.
- T-0328 (T0328-1) and T-0331 (T0331-3): the L3 verifier row prices at 0.570 of host after the T-0332 refit, outside the 35 percent band both tickets state; the live report and the release record already concede it. Ticket T-0336.
- T-0331 (T0331-1): twelve launcher skills spell `dispatch.py record` without `--transcript`. Ticket T-0334.

## Observations (no criterion failed, no ticket filed)

- `dispatch.py resume <name> --root <absolute path with a .worktrees component>` finds nothing (dispatch.py:338 skips such paths); see `T-0279.md`.
- The stray-worktree hook denied the verifiers a throwaway worktree (`SDLC_TMP_WORKTREES` unset in the sub-agent session), so they used `git archive` and file copies under the tmp prefix instead. The verifier role text tells verifiers to use a throwaway worktree, so the two disagree in this mode.
- The verifier tool-call budget (about 40) was met or exceeded by five of six batches (28 to 48 calls); none ran out of criteria.
- `check.py` reads tracked files for its link check, so a ticket filed through `tickets.py new` shows as a broken roadmap link until it is staged or committed (see the T-0333 verifier run above).
- T-0275 rows quoted from a hook.log that no longer holds those lines are recorded evidence only; see `T-0275.md`.
