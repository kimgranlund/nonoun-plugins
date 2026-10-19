---
id: T-0451
title: "lanes.py core: open, close, sweep, list, check, port (lane lifecycle A)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One script owns the lane lifecycle: open, close, sweep, list, check and port, with the landed test and truth table of the design.

## Intent
- Do: build ticket A of section 13: new `plugins/sdlc-lite/scripts/lanes.py` (open, close, sweep, list, check, port, selftest; the kinds table, truth table and record fields in its docstring), the `check.sh` selftest line, and an entry in `docs/references/sdlc-internals.md` with the new `.sdlc/config` keys. Add the section 8.1 rule: `lanes.py open` refuses a lane whose ticket is not claimed (`claimed_by:` for local tickets; for GitHub or Linear it prints the claim directive and does not block), and `close` prints `ticket still open` when it closes a merged lane whose ticket is open. Port the removal logic of `~/.claude/lane/sweep.py` (merged means ancestor, or a MERGED PR whose head sha equals the tip, or every changed file equal; archive ref first; keep dirty, locked, recent and unmerged lanes).
- Non-goals: wiring into fanout, solo_run, tickets or dispatch (B, C); the hook message (D); `lanes.py wait` and board columns (later tickets).
- Done when: `(red)` `python3 plugins/sdlc-lite/scripts/lanes.py selftest` fails now (no file); after, it exits 0 with one case per truth-table row and per C1 to C6 control, each mutant observed failing; `check.sh` exits 0.

## Context
Design (approved by the maintainer 2026-10-11, build A to D as a chain): `docs/specs/sdlc-lite/lane-lifecycle.md`, especially section 13 (ticket table), section 7 (the landed test and truth table), section 8 (who calls close) and section 8.1 (every lane has a ticket, tracker-agnostic). Interim lane guidance now in `plugins/sdlc-lite/AGENTS.md` (Lanes). Maintainer tool `~/.claude/lane/sweep.py` is the logic to port. Shared hot files (`check.sh`, `check.py`, `fanout.py`): one writer at a time.

## Constraints
No model or effort change. Never delete unmerged work; archive ref `refs/archive/<date>/<branch>` before any removal. A locked worktree is a running lane. No push, tag or publish. Read-only against any repo it does not own.

## Closed

2026-10-11: warnings acknowledged: step 2 red controls recorded after the edit; both step verifiers passed; one selftest isolation case and one check.sh run flaked under parallel sessions and passed on rerun and in the verifier run; the flake is fixed in T-0452 (selftest limited to its own temp repo)

> - process deviation: red-checkpoint: retrospective: attempt 5cde5f81297b421892c1bb8c26875006, handoff sha256 4b04d1922281. Step 2 had 4 of 4 (red) criteria without a pre-edit red control: the `check.sh` grep for `lanes.py" selftest`, the `sdlc-internals.md` heading grep, the config-key loop, and the `lanes.py --help` grep. The verifier verdict does not clear this. The builder says step 1's untracked `lanes.py` already differed from the base, so redck stored the controls as retrospective. The builder also says all four criteria were red at base before any edit, and the verifier confirmed the base lacked the `check.sh` line.
> - Step 1 recorded 7 pre-edit controls for 8 `(red)` criteria. The missing one is the `--help` strings check, which was red at base anyway because the file did not exist. Step 1's verifier found no `process-deviations.md` for step 1.
> - Step 1 criterion 8 (selftest leaves worktrees and refs unchanged) failed on the builder's first run, because another session wrote refs inside the run window. A rerun passed, and so did the verifier's run.
> - Step 2's guard (`check.sh`) exited 1 on the builder's first run, and the output was not captured. A second run exited 0 with no edits in between. The builder suspects load but did not confirm it.
> - Step 2's verifier reran `check.sh` and saw no failure lines in the tail, but did not capture the exit code, so that pass rests on the output tail.
> - Both steps have a verifier verdict of pass.
