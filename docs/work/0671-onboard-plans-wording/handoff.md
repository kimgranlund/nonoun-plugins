---
id: T-0671
title: "onboard entry text agrees with the docs table on where plans go"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The onboard-managed AGENTS.md block and the docs table agree on where plans go, and the work root's `AGENTS.md` is a link plus the current stage counts, so work records are explained in one place.

## Intent
- Do: (1) In `ROOT_AGENTS_TEMPLATE` (`plugins/sdlc-lite/scripts/onboard.py:416`), change "holds SDLC Lite tickets and plans" to "holds SDLC Lite tickets and their task plans" and add that plan docs under review go to `docs/planning/`. (2) `WORK_ROOT_TEMPLATE` (`plugins/sdlc-lite/scripts/tickets.py:2745`) renders one stage-count line (for example `Stages: proposed 27, ready 0, claimed 0, paused 0.`) under the existing link to the router, from the same counts as the router's `## Stages`. (3) Selftest cases for both; regenerate this repo's work-root entry with `tickets.py --root .sdlc roadmap`.
- Non-goals: listing tickets in `docs/work/AGENTS.md` (the router keeps the list); moving any plan doc.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #31, ui-kit-neue audit 2026-10-20.
In the audited repo `AGENTS.md:50` said the work root holds "tickets and plans" while `docs/AGENTS.md:8` routes plans under review to `planning/`; `docs/work/AGENTS.md` was only a pointer to `.sdlc/AGENTS.md`.
Confirmed here: the block line is `onboard.py:416` (`` `.sdlc/` holds SDLC Lite tickets and plans; ``; `render_templates` swaps in the real tickets path at `onboard.py:644`). The docs table row is `onboard.py:443` (`work/` never holds "Designs and plans under review -> `planning/`"). The pointer half is already done: T-0625 made the work-root entry a short link to the router (`WORK_ROOT_TEMPLATE`, `tickets.py:2745` to `:2750`; selftest at `tickets.py:6476` to `:6481`), and this repo's `docs/work/AGENTS.md` shows it. The stage counts are rendered for the router under `## Stages` (`tickets.py:2694`); reuse that computation. This repo's root `AGENTS.md` has no onboard block, so only consumer repos see change (1) after `onboard.py setup`.

## Constraints
The router's `## Stages` list is unchanged. Both blocks keep their managed-block stamps valid.

## Acceptance criteria
1. `grep -n 'tickets and plans' plugins/sdlc-lite/scripts/onboard.py` finds nothing, and `grep -n 'tickets and their task plans' plugins/sdlc-lite/scripts/onboard.py` finds the block line, which also names `planning/`.
2. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a case: after `new`, the work-root `AGENTS.md` block holds the router link and a stage-count line whose numbers match the router's `## Stages`. The case fails with the change reverted.
4. After `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`, `grep -n 'proposed' docs/work/AGENTS.md` prints the stage-count line, and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
5. `git diff --check` exits 0.

## Outcome

2026-10-20 · lane: solo · verdict: built, unverified · verifier: none · base: c743325e
- Changed: `ROOT_AGENTS_TEMPLATE` says "tickets and their task plans (plan docs under review go to `docs/planning/`)"; `WORK_ROOT_TEMPLATE` renders `Stages: proposed N, ready N, ...` via `stage_count_line`; selftest cases in `onboard.py` and `tickets.py` (the tickets case fails with the replacement removed); `docs/work/AGENTS.md` regenerated.
- Checks: `onboard.py selftest` exit 0, `tickets.py selftest` exit 0, `tickets.py --root .sdlc roadmap` and `check` exit 0, `git diff --check` exit 0. `check.py` shows 3 FAIL lines (fanout `--force`/`--forward` hints) that also fail on main; not touched here.
