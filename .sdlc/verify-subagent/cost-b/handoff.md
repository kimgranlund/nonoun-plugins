# Verify T-0331 and T-0332 transcript pricing and calibration on the released tree

Independent check of 2 ticket(s) that closed with no verifier verdict. The tree under test is the current worktree: SDLC Lite v0.21.0 (commit 027da15a) plus three doc-only commits (`git diff --stat 027da15a HEAD -- plugins` is empty). There is no builder diff to review, so the dispatch base sha (the 0.21.0 merge commit) is not a scope boundary: judge each criterion on the files as they stand now, and list nothing under "Out of scope changes" unless you saw the tree change.

Each ticket was built by a solo Sonnet low agent (one `role solo` record in its closed folder's `runs.jsonl`). You run on another model family. The source of every criterion is the ticket's own closed folder (`.sdlc/.NNNN-*/handoff.md`, history, read it for context and its Closed note); the criteria below restate its "Done when" lines with the shifted names resolved. Treat the builder's "delivered, checks passed" note as unverified.

Rules for this run:
- Read-only. Fix nothing, create no project file, change no git state. Use a throwaway worktree or a temp fixture under your tmp prefix for any before-the-change or red control.
- A behavior criterion passes only on a run you observed; a selftest line counts when you ran the selftest and saw that case, and a negative control you saw go red (in a throwaway copy, or a fixture of your own) makes it stronger. A criterion you cannot run fails with the reason.
- A later ticket may have changed the same code (the cost chain T-0280, T-0328, T-0331, T-0332 re-fit the estimate in turn). Judge each ticket's stated criterion on the tree as it stands, against that ticket's own band or condition; a table replaced by a better one is not a fail unless the ticket's condition no longer holds.
- Write one verdict for the whole file. Criterion ids carry the ticket (for example `T0279-1`) so the verdict splits per ticket: each id is `pass` or `fail`, and every fail gets a one-line root cause. The top-level Verdict is `fail` if any id fails.
- No em dashes or en dashes in your report.

## Acceptance criteria

T-0331 (conductor and chain skills, fanout land, calibration):
- T0331-1: the conductor agent and chain skill (plugins/sdlc-lite/agents/conductor.md, plugins/sdlc-lite/skills/chain/SKILL.md, and any launcher skill that runs `dispatch.py record`) pass `--transcript` to `dispatch.py record`. Show the lines with `git grep -n -- '--transcript' plugins/sdlc-lite` and name any `record` call in those texts that lacks it.
- T0331-2: the fanout path writes a priced solo row: at `fanout.py land` the lane's solo `runs.jsonl` row gets a priced `cost_usd` (transcript priced). Observe with the fanout selftest case that checks it (find it with `git grep -n 'cost' plugins/sdlc-lite/scripts/fanout.py`), or a fixture of your own; a code read alone does not pass.
- T0331-3: the estimate for the L2 and L3 verifier rows in docs/reports/subagent-mode-live-2026-10-07/ (host-cost.txt) is within 35 percent of host, where the transcript undercounts input and output tokens a calibration factor fitted on those rows is applied (`usage_calibration` in plugins/sdlc-lite/adapters/claude/prices.json), documented, and the fitted band is stated in the report (docs/reports/subagent-mode-live-2026-10-07.md). Compute the ratios from the stored rows with the tree's own code and quote them; check the documented factors equal the ones in prices.json.
- T0331-4 (guard): `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` and `python3 plugins/sdlc-lite/scripts/cost_estimate.py selftest` exit 0.

T-0332 (bug; folder .sdlc/.0332-transcript-usage-last-line, no runs.jsonl, fixed inside the live rerun commit):
- T0332-1: `cost_estimate.transcript_usage` sums the last usage line per message id (the final counts). Observe `cost_estimate.py selftest` case 'transcript_usage sums the last line once per message id' (fixture: message a has output 8, 8, 10; b has 5; expected output sum 15), and prove it bites: in a throwaway copy make `transcript_usage` take the first line per id and see that case go red.
- T0332-2: the calibration in prices.json is refit so a live fable verifier row lands within 35 percent of the host: the final-rerun verifier (docs/reports/subagent-mode-live-2026-10-07/final-host-cost.txt, G-verifier-L3.dispatch.json and its transcript usage, or the stored row) priced by the tree's code is within 35 percent of the host figure. Show the ratio (the live report says 0.74) and say whether you reproduced it from the stored files.
- T0332-3: the failing test landed with the fix: the fixture case in T0332-1 exists in the selftest and the selftest exits 0 on the tree; and `usage_calibration` input and output factors are 225 and 1.27 as the release record states.
- T0332-4 (guard): `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.
