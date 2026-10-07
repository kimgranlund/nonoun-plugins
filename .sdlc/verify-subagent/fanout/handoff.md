# Verify T-0326, T-0327 and T-0329 fanout sub-agent lanes on the released tree

Independent check of 3 ticket(s) that closed with no verifier verdict. The tree under test is the current worktree: SDLC Lite v0.21.0 (commit 027da15a) plus three doc-only commits (`git diff --stat 027da15a HEAD -- plugins` is empty). There is no builder diff to review, so the dispatch base sha (the 0.21.0 merge commit) is not a scope boundary: judge each criterion on the files as they stand now, and list nothing under "Out of scope changes" unless you saw the tree change.

Each ticket was built by a solo Sonnet low agent (one `role solo` record in its closed folder's `runs.jsonl`). You run on another model family. The source of every criterion is the ticket's own closed folder (`.sdlc/.NNNN-*/handoff.md`, history, read it for context and its Closed note); the criteria below restate its "Done when" lines with the shifted names resolved. Treat the builder's "delivered, checks passed" note as unverified.

Rules for this run:
- Read-only. Fix nothing, create no project file, change no git state. Use a throwaway worktree or a temp fixture under your tmp prefix for any before-the-change or red control.
- A behavior criterion passes only on a run you observed; a selftest line counts when you ran the selftest and saw that case, and a negative control you saw go red (in a throwaway copy, or a fixture of your own) makes it stronger. A criterion you cannot run fails with the reason.
- A later ticket may have changed the same code (the cost chain T-0280, T-0328, T-0331, T-0332 re-fit the estimate in turn). Judge each ticket's stated criterion on the tree as it stands, against that ticket's own band or condition; a table replaced by a better one is not a fail unless the ticket's condition no longer holds.
- Write one verdict for the whole file. Criterion ids carry the ticket (for example `T0279-1`) so the verdict splits per ticket: each id is `pass` or `fail`, and every fail gets a one-line root cause. The top-level Verdict is `fail` if any id fails.
- No em dashes or en dashes in your report.

## Acceptance criteria

T-0326 (fanout.py prep and the spawn gate hooks/block-role-spawn.sh):
- T0326-1: `fanout.py prep` lane prompts carry the `Handoff:` line and prep writes each solo lane's dispatch record (`<name>.dispatch.json`, the solo-S|M|L form the gate allows), so both lane spawns pass the spawn gate; and the same prompt without its Handoff line is still refused. Observe on a fixture of your own (a temp git repo with two ready solo-lane tickets; run `fanout.py prep`, then pipe a PreToolUse Agent event for each lane into `bash plugins/sdlc-lite/hooks/block-role-spawn.sh` with `agent_type` `sdlc-lite:conductor`: exit 0 for both; with the Handoff line removed from the prompt: exit 2). The fanout selftest case is 'case 22 prep: both lane prompts pass the spawn gate, one without its Handoff line is refused'; quote it from a run of `python3 plugins/sdlc-lite/scripts/fanout.py selftest`.
- T0326-2 (guard): `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, `fanout.py selftest` and `dispatch.py selftest` exit 0.

T-0327 (fanout.py land):
- T0327-1: `fanout.py land` recognizes a host-named branch `worktree-agent-<agent_id>` as the solo (or full) lane it belongs to, through the dispatch record's `agent_id` and not the branch name, and closes the ticket; an unknown branch is still treated as an external lane. Observe via the selftest cases around the branches `worktree-agent-a1b2c3` (lands and closes a solo lane) and `worktree-agent-zzz` (unknown, external), and reproduce one on your own fixture; show it bites by making the agent_id in the dispatch record not match and seeing the lane fall back to external.
- T0327-2 (guard): the same gates as T0326-2.

T-0329 (fanout verifier prompt Tree):
- T0329-1: the verifier prompt written for a fanout lane names the lane worktree as its `Tree:`, and a selftest shows the prompt for a worktree lane carries the worktree path. Find where fanout builds that prompt (`git grep -n 'Tree:' plugins/sdlc-lite/scripts/fanout.py plugins/sdlc-lite/scripts/dispatch.py`), observe the selftest case, and reproduce on a fixture lane worktree; show it bites by checking the prompt of the same fixture with the pre-fix behavior (a Tree line naming the main tree) is rejected by the selftest, or by a throwaway worktree edit.
- T0329-2 (guard): the same gates as T0326-2.
