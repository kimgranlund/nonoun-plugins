# Verify T-0279 and T-0286 dispatch recovery and supervisor orphans on the released tree

Independent check of 2 ticket(s) that closed with no verifier verdict. The tree under test is the current worktree: SDLC Lite v0.21.0 (commit 027da15a) plus three doc-only commits (`git diff --stat 027da15a HEAD -- plugins` is empty). There is no builder diff to review, so the dispatch base sha (the 0.21.0 merge commit) is not a scope boundary: judge each criterion on the files as they stand now, and list nothing under "Out of scope changes" unless you saw the tree change.

Each ticket was built by a solo Sonnet low agent (one `role solo` record in its closed folder's `runs.jsonl`). You run on another model family. The source of every criterion is the ticket's own closed folder (`.sdlc/.NNNN-*/handoff.md`, history, read it for context and its Closed note); the criteria below restate its "Done when" lines with the shifted names resolved. Treat the builder's "delivered, checks passed" note as unverified.

Rules for this run:
- Read-only. Fix nothing, create no project file, change no git state. Use a throwaway worktree or a temp fixture under your tmp prefix for any before-the-change or red control.
- A behavior criterion passes only on a run you observed; a selftest line counts when you ran the selftest and saw that case, and a negative control you saw go red (in a throwaway copy, or a fixture of your own) makes it stronger. A criterion you cannot run fails with the reason.
- A later ticket may have changed the same code (the cost chain T-0280, T-0328, T-0331, T-0332 re-fit the estimate in turn). Judge each ticket's stated criterion on the tree as it stands, against that ticket's own band or condition; a table replaced by a better one is not a fail unless the ticket's condition no longer holds.
- Write one verdict for the whole file. Criterion ids carry the ticket (for example `T0279-1`) so the verdict splits per ticket: each id is `pass` or `fail`, and every fail gets a one-line root cause. The top-level Verdict is `fail` if any id fails.
- No em dashes or en dashes in your report.

## Acceptance criteria

T-0279 (plugins/sdlc-lite/scripts/dispatch.py: status, resume, recover):
- T0279-1: `dispatch.py status <dir>` prints each attempt as running, completed, failed, or orphaned. Observe on a fixture of your own (temp dir with an attempt record whose `parent_pid` is dead, no result file): it prints `orphaned`; with `parent_pid` alive it prints `running` (negative control). Also run `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` and quote the cases 'status: running attempt with a dead parent prints orphaned' and 'negative control: a live parent prints running'.
- T0279-2: `dispatch.py resume <name>` for an orphan prints in order: a `SendMessage` line carrying the name and the id, then the new-attempt command with a brief addendum naming the transcript path and `git status` as the first step; it never replays an old report. Observe it on your fixture; a running (non-orphan) attempt is refused.
- T0279-3: `dispatch.py recover <dir>` marks orphaned attempts `interrupted` with the same recovery text as `python3 plugins/sdlc-lite/scripts/run_lifecycle.py recover`, and `dispatch.py prepare` calls it for a dead-parent attempt (observe a prepare against a fixture dir holding a dead-parent attempt: the old record becomes interrupted and prepare proceeds).
- T0279-4: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 (observe it).

T-0286 (supervisor.py and board.py):
- T0286-1: `supervisor.py watch --once` writes an `orphans` list into `status.json` from `dispatch.py status --orphans` over the active ticket folders. Observe: a fixture project with one dead-parent attempt lists it, and one whose parent is alive lists none (negative control). The supervisor selftest case is 'orphans: a dead-parent dispatch is listed in status.json and a live one is not'; quote it from a run of `python3 plugins/sdlc-lite/scripts/supervisor.py selftest` (or its case selector if one exists) and say whether you also reproduced it on your own fixture.
- T0286-2: `board.py` renders an orphaned step as `🟡 orphaned · resume`; `python3 plugins/sdlc-lite/scripts/board.py selftest` and `supervisor.py selftest` exit 0 (observe both).
- T0286-3: the supervisor still never claims, moves, or reads a message body: the pre-existing supervisor selftest cases for that pass unchanged (observe them in the same selftest run, and show `git log -p` for supervisor.py does not edit those cases' assertions in T-0286's change).
- T0286-4 (guard): `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.
