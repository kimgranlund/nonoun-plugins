---
id: T-0544
title: "Lean records E: Layout rule and tidy (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0543]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Layout rule and tidy: part E of SDLC Lite 0.23.0 lean work records (wave 4).

## Intent
- Do: build part E of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for E, Interfaces and Risks). Files: `tickets.py` (top-level allow-list `check` warning, `tidy [--apply]`, router `Folder layout` and `Ticket lifecycle` sections, `claim --by <word>` from T-0534), `skills/fleet-retro/{SKILL.md,interview.md}`, `skills/{grill,review-traces,bench}/SKILL.md` (write in the records dir), `onboard.py` "Work records" block :382-391
- Non-goals: the other parts (A to F) of the same design.
- Done when: `tickets.py selftest` exits 0 with: `check` warns on a stray top-level file and stays silent for an allowed name (negative control); `tidy` without `--apply` changes nothing; `tidy --apply` moves the stray file into `archive/` and refuses while a `*.running` marker exists; `claim --by astra` is accepted

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0; its T-0544 cases cover the `check` warning on a stray top-level file with an allowed name and a `top_level_allow:` glob silent (negative control), `tidy` without `--apply` leaving the tree identical, `tidy --apply` moving the stray into `archive/`, refusing while a `*.running` marker exists and when the destination exists, and `claim --by astra` accepted.
2. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 (the regenerated `.sdlc/AGENTS.md` router with the Folder layout and Ticket lifecycle sections is current).
3. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with the updated Work records block.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `python3 scripts/check-packaging.py` exits 0.
5. The grill, review-traces, bench and fleet-retro skills write their work files in the records dir that `order.py records-dir` prints and the fleet-retro interview answer goes by `messages.py send`: `git grep -n -F -e ".sdlc/fleet-retro-<date>.md" -e "<review task>/cluster" -e "<slug>/design.md" -- plugins/sdlc-lite/skills` exits 1.

## Outcome

2026-10-14 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: `plugins/sdlc-lite/scripts/tickets.py` `selftest` takes about 4 minutes. Each negative-control run through the full suite was slow; the T-0544 cases are not slow themselves. | note: `tickets.py --root .sdlc check` on this repo now prints 43 loose-entry warnings (`fix-protocol-controls`, `fleet-retro-*` and others). They are warnings only (rc=0) and are what `tidy` is for. Running `tidy --apply` on this repo is a separate decision. | note: I did not break the `claim --by astra` path in the throwaway copy. The case is pass-only evidence, because claim already accepted any word before this change; only the help text and router changed.) · verifier: verifier-L2 (sonnet) · base: ab94588622d9
- Changed: see commits
- Commits: 1a64696 T-0544: Lean records E: Layout rule and tidy (0.23.0)
- Check: 1 `tickets.py selftest` exits 0 and its T-0544 cases cover the layout rule: pass
- Check: 2 `tickets.py --root .sdlc check` exits 0: pass
- Check: 3 `onboard.py selftest` exits 0: pass
- Check: 4 `check.py` and `check-packaging.py` exit 0: pass
- Check: 5 The skills write their work files in the records dir and the interview answer goes by `messages.p...: pass
