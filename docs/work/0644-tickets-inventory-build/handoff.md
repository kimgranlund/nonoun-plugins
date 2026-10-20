---
id: T-0644
title: "tickets.py inventory: build the T-0584 design"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py inventory` reports each open or recently closed ticket's real state: its branch, whether that branch has landed on main or a named integration branch, and its newest verifier verdict.

## Intent
- Do: (1) Factor the `git cherry` patch-identity test out of `lanes.orphans` into a shared `patch_landed(top, into, ref)` helper in `plugins/sdlc-lite/scripts/lanes.py`, and use it in `lanes.landed` between `pr merged` and the file compare (state `patch`). (2) Add read-only `tickets.py inventory [--into <branch>]... [--days N] [--json]` per the design: one row per ticket and branch with id, status, branch or `-`, landed state, newest verifier role-level, verdict, result file. (3) Selftests.
- Non-goals: any write or cleanup action; changing `order.py` ordering (already correct).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Design, output format and reused functions: `docs/work/.0584-tickets-inventory/handoff.md` `## Outcome` (verified 2026-10-19). Reuse `tickets.load`, `tickets.worktree_pairs`, `tickets.branch_tickets`, `tickets.default_branch`, `lanes.discover`, `lanes.landed`, `order.records_dir`, `order.newest`. Verifier note: the design says the verdict is read "as `results.py` parses it"; find the real parser and reuse it. Source: maison's hand-built `collect.py` and `classify.py` (verifier sort order, stale sibling branches, pointer branches, unusual record paths).

## Constraints
`lanes.landed` keeps its existing states and order for ancestor, pr merged and content; `lanes.orphans` output is unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with inventory cases for: a `verifier-L3-2.md` beside `verifier-L3.md` (the `-2` file is newest), a branch cherry-picked onto main (`landed:main(patch)`), a stale sibling branch for the same ticket (its own row, `not landed`), and records under a legacy path.
2. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, and its orphans case still passes using `patch_landed`.
3. `python3 plugins/sdlc-lite/scripts/tickets.py inventory --json` in this repo exits 0 and prints valid JSON (`| python3 -m json.tool >/dev/null`).
4. `git diff --check` exits 0.

## Outcome
Built by solo L2.
- `plugins/sdlc-lite/scripts/lanes.py`: new `patch_landed(top, into, ref)` (the set of ref commits with no patch-equivalent in into, None when `git cherry` fails); `orphans` uses it with unchanged output; `landed(..., patch=False)` checks it between `pr merged` and the file compare and returns `patch` only when a caller passes `patch=True`, so close, sweep and list keep their states and truth table.
- `plugins/sdlc-lite/scripts/tickets.py`: read-only `inventory [--into BRANCH]... [--days N] [--json]`, one row per ticket and branch (its `branch:` line, lane records naming it, local branches holding its id), landed via `lanes.landed(patch=True)`, newest verifier via `order.newest` in `order.records_dir` (the branch's worktree copy when it has one), verdict via `results.key_value`. Usage docstring updated. Selftest cases: `-2` verifier newest, cherry-pick `landed:main(patch)` with a later content change, stale sibling `not landed (b.txt)`, legacy in-folder records, the `--days` window, and a control showing `landed` without the patch test says `not landed`.
- Checks: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/tickets.py inventory --json | python3 -m json.tool >/dev/null` exit 0; `git diff --check` exit 0.
- Note: criterion 1 pins the exact string `landed:main(patch)`; `steps.py verifier-level` prints L2.
