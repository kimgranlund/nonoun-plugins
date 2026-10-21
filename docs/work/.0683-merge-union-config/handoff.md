---
id: T-0683
title: "merge_union config: land union-merges listed paths behind one light gate"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A repo can name append-only shared files (fixtures, scenario lists) in `.sdlc/config` with `merge_union: <glob>...`, and `fanout.py land` union-merges a conflict in those paths the way it already does for notes.md, checks the result with one light gate before the merge commit, and says `union-merged` in its report instead of stopping on `merge conflict`.

## Intent
- Do: (1) add `merge_union_globs(root)` in `plugins/sdlc-lite/scripts/tickets.py` beside `hash_bound_globs` (near line 727, a new `MERGE_UNION_RE` beside `HASH_BOUND_RE` at line 425), plus an optional `merge_union_gate: <cmd>` line, and document both keys in the config docstring near tickets.py:269 and in `plugins/sdlc-lite/skills/fanout/references/land.md`. (2) In `merge_generated` (`plugins/sdlc-lite/scripts/fanout.py`, near line 1606), take a conflicted path matching a `merge_union` glob through the same three-stage `git merge-file -p --union` as notes.md (fanout.py:1637 to 1645) and return the union-merged paths; in `merge_gate_close` (near line 1670) run `merge_union_gate` in the integration tree after the union and before the `Merge <branch>: <id>` commit (fanout.py:1705), resetting and returning `union gate red: <cmd>` on a non-zero exit, force the full gate class for that land, and add `union-merged: <paths>` to the land output. (3) Selftest cases in `fanout.py selftest`: two lanes appending different lines to one `merge_union` file land as `merged` with both lines present and `union-merged` printed; the same file with no `merge_union` line still stops as `merge conflict`; a `merge_union_gate` that exits 1 leaves HEAD at the pre-merge commit.
- Non-goals: language-aware merges; changing how notes.md or the generated roadmap and router files merge; `fanout.py sync`.
- Done when: the criteria pass.

## Context
Source: GitHub issue #38, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
Parallel lanes append blocks to the same fixture or scenario file, and land stops on `merge conflict`: 15 conflicted lands across 13 tickets in 0.27 and 3 more in 0.28.1. Hand "keep both" resolution then broke syntax (`fixtures/react/sections/shared-geometry.tsx: error TS1005: '}' expected`; a JSX unclosed tag), with no check before the commit.
On main: `merge_generated` (fanout.py:1606) already unions notes.md (`git merge-file -p --union` at fanout.py:1642) and returns `('conflict', paths)` for any other conflicted path outside the generated files and the `theirs` pathspecs (fanout.py:1626 to 1628). `merge_gate_close` commits the merge (fanout.py:1705) and only then runs the `--gate` set, resetting to `before` on red (fanout.py:1743), so a broken union is already reset by a failing full gate; the new `merge_union_gate` gives a cheaper, earlier and named failure, and forcing the full class stops a `light_scope` land from skipping the real gates. Config keys follow the `hash_bound:` reader pattern (tickets.py:425, 727).

## Constraints
A repo with no `merge_union:` line lands exactly as today. A conflict in a path outside the generated files and the `merge_union` globs still stops as `merge conflict`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the three new cases, and the union case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a `merge_union_globs` case (config lines read in order, comments ignored, a missing config yields []).
3. `grep -n "merge_union" plugins/sdlc-lite/skills/fanout/references/land.md` prints at least one line.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check 8624f984` exits 0.

## Outcome
Base: merged main into the lane first (`git merge --no-edit main` fast-forwarded the lane to 4efd51f7); `git diff --check` is green against both 4efd51f7 and 8624f984.
- `plugins/sdlc-lite/scripts/tickets.py`: `MERGE_UNION_RE`, `MERGE_UNION_GATE_RE`, `merge_union_globs(root)` and `merge_union_gate(root)` (first uncommented line), both keys in the config docstring, and a selftest case (order kept, duplicates once, comments ignored, missing config gives [] and None).
- `plugins/sdlc-lite/scripts/fanout.py`: `merge_generated` takes `union` globs and an `unioned` out-list and union-merges a matching conflicted path through the notes.md three-stage `git merge-file -p --union`; `merge_gate_close` passes the repo's globs, prints `union-merged: <paths>`, forces the full gate class for that land, and runs `merge_union_gate` before the merge commit, resetting to the pre-merge commit as `union gate red: <cmd>` on a non-zero exit. Other callers (settle, sync, lanes.py) are unchanged. Three selftest cases: union lands merged with both lines; no `merge_union` line still stops as `merge conflict`; a gate exiting 1 leaves fanout/g at `close T-0001`.
- `plugins/sdlc-lite/skills/fanout/references/land.md`: documents both keys.
Checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0; with the land's union globs replaced by `()` it exits 1 on exactly the T-0683 union and union gate cases. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0. `grep -n "merge_union" plugins/sdlc-lite/skills/fanout/references/land.md` exit 0. `python3 plugins/sdlc-lite/scripts/check.py` exit 0. `git diff --check 8624f984` exit 0.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 9dc347f22c55
- Changed: see commits
- Commits: d66619d T-0683: merge_union config: land union-merges listed paths behind one light gate
- Check: 1 fanout selftest exits 0 with the three new cases, union case fails with the change reverted: pass
- Check: 2 tickets selftest exits 0 with a merge_union_globs case: pass
- Check: 3 land.md mentions merge_union: pass
- Check: 4 check.py exits 0: pass
- Check: 5 git diff --check 8624f984 exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1719: the force-full-gate-class... -> notes.md
