---
id: T-0489
title: "fanout.py settle --forward: merge main into a diverged integration branch, regenerate, cover, then fast-forward (T-0488)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0481]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py settle <integration> --forward` merges main into a diverged integration branch under the locks, regenerates the roadmap and router block, union-merges `notes.md`, runs the gate (T-0481 `cover`), and fast-forwards main only when the gate is green. A plain `settle` still refuses a diverged branch.

## Intent
- Do: in `fanout.py` `settle` (about `:2330-2350`), add `--forward`; reuse the merge lock; on a conflict outside the generated files (`.sdlc/AGENTS.md`, `.sdlc/roadmap.md`, `notes.md`, the `check.sh` header comment) stop with exit 2 naming the files and leave main, the branch and the tree unchanged (no `MERGE_HEAD`).
- Non-goals: a second ledger, gate class or cadence (T-0481 owns them); any push; `roll`; release cutting.
- Done when: a `fanout.py selftest` case after case 28: two tickets; a lane lands T-0001 (close regenerates `roadmap.md` and `.sdlc/AGENTS.md` on the integration branch); on main `tickets.py new` files T-0003; `settle fanout/x --forward --gate true` exits 0 with `settled`, main equals the integration tip, `roadmap.md` lists T-0001 done and T-0003 proposed, `tickets.py check` exits 0, one ledger entry has `to` equal to that tip. Observed red first (today exit 2, `not a fast-forward of main`). Negative controls: `README.md` edited on both sides exits 2 naming `README.md` with `git status --porcelain` empty; plain `settle` on the diverged branch exits 2; `--gate false` leaves main unmoved and the forward-merge commit on the integration branch. `fanout.py selftest` and `check.py` exit 0.

## Context
Design: `docs/planning/merge-ops-and-queue.md` (Approach 2, 4, 6; smallest first build). Evidence: generated-file conflicts at 5 of 8 wave merges in waves 40 to 44, each hand-merged by the maintainer. If T-0481 is dropped, take `--gate CMD...` on settle and run the same loop in the integration tree.

## Constraints
Main moves only by `--ff-only`. One writer on `fanout.py` at a time. No model or effort change.

## Plan review
- dispatch.py prepare builder L3 refused step-1: `steps: step-1/handoff.md: cited path does not exist: .sdlc/gate-ledger.jsonl` / `plan defect: replan this step (/chain 3)`. The ledger path names a file inside the selftest fixture repo, not this tree; write it so it is not read as a cited repo path (for example `gate-ledger.jsonl` in the fixture repo, without the `.sdlc/` prefix in backticks), and keep the rest of planner-L2.md unchanged.
