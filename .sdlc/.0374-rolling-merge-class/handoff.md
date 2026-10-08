---
id: T-0374
title: "Lanes get a computed merge class (rolling or integration) and a land command for rolling lanes"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0375]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane has a computed merge class, and a rolling lane that is independently verified can land on main at once.

## Intent
- Do: Compute a merge class per lane in the plugin: `rolling` (independently verified, touches no hash-bound or generated path, base is an ancestor of main) can fast-forward to main immediately; `integration` (touches hash-bound or generated files) waits for the next regeneration. Add a `fanout.py land`-style path for rolling lanes with the verifier verdict as the gate. The set of hash-bound paths comes from the repo's declared list in .sdlc/config, not from a guess. Design first: write the rule and the config shape in docs/references/sdlc-internals.md before code; the user decided on 2026-10-08: a repo declares its hash-bound and generated paths as one glob list in .sdlc/config (read by the plugin); no per-ticket declaration. Do not stop to ask about that.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - Selftests: a verified lane touching no declared path and based on an ancestor of main is classed rolling and lands; one touching a declared path is integration and does not; an unverified one never lands; a stale base is not rolling (observed failing first).
  - The class and the land gate are documented in one place.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Lanes accumulate faster than integrations land because the only merge path is the per-round integration solo (maison R2: 15 verified lanes waited on one combined integration). Source: feedback from the maison conductor, 2026-10-08 (about 30 lanes across Claude and Codex, 3 bases, 2 peer repos); its specifics are in the maison repo's .sdlc/notes.md and handoffs. Maison ran plugin 0.21.2; check each claim against 0.21.3 and main before building.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
verifier: L3

- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and its case 27 holds: a lane with a committed `pass` verifier result, a recorded base main contains, and no path a `hash_bound:` line in `.sdlc/config` declares is classed `rolling`, and `fanout.py roll` lands it (exit 0, main fast-forwarded to the merge and `close <id>`, the ticket `done` on main, the main checkout clean); a lane touching a declared path is `integration (hash-bound <path>)`, one with no verifier result `integration (unverified)`, and one whose recorded base main lacks `integration (stale base <sha7>)`, each exit 1 with main unchanged and the ticket still `ready`; a fast-forward git refuses (a local file in the way) is `main not advanced` with main and the file untouched; a lane cut before main moved still rolls; with the `hash_bound` line removed the hash-bound lane rolls (negative control: the class comes from the config).
- [ ] Red first, reproducible from the base commit: `git show HEAD:plugins/sdlc-lite/scripts/fanout.py` has no `roll` verb (`main` accepts only run, prep and land, so case 27 cannot pass there), and `git show HEAD:plugins/sdlc-lite/scripts/board.py` returns a hardcoded `'n/a'` Merge cell in `lane_ledger`, so the new ledger expectations cannot pass there.
- [ ] `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0, and `board.py --lanes` shows Merge `rolling` for a verified lane on main's head, `integration (stale base <sha7>)`, `integration (unverified)`, and `integration (hash-bound gen/x.json)` for a lane with an untracked declared file; `grep -rn "until T-0374" plugins docs` prints nothing.
- [ ] The class rule, the `hash_bound:` config shape, and the roll gate are defined in one place, the "Merge class and `roll`" paragraph under `scripts/fanout.py` in `docs/references/sdlc-internals.md`; `steps.merge_class` is the one implementation of the rule and both `board.py` and `fanout.py` call it; `tickets.hash_bound_globs` is the one reader of the list.
- [ ] Main moves only by fast-forward: `roll` merges, gates, and closes in `<lanes-dir>/rolling`, then runs `git merge --ff-only` where main is checked out or `git update-ref` against main's old sha, and never commits on or resets the main checkout.
- [ ] `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/tickets.py check`, `python3 plugins/sdlc-lite/scripts/steps.py selftest`, `python3 plugins/sdlc-lite/scripts/tickets.py selftest`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exit 0; `git diff --check` is clean and the diff adds no em or en dash.

## Closed

2026-10-08: delivered by the solo agent (level L3); one independent batched verifier passed before the merge
