---
id: T-0780
title: "Give the fanout skill room under its size limit"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc-lite/skills/fanout/SKILL.md` sits at least 1,500 characters under the 18,000-character packaging limit, with nothing lost: detail moves into the skill's `references/` files it already links.

## Intent
- Do: move the longest detail paragraphs (sub-agent lanes internals, settle and land detail) into the existing `references/` files (lane-lifecycle, land, main) and leave one linked line each in SKILL.md. Then add the lines T-0760, T-0766 and T-0758 could not fit: `advance` stops on a blocked solo report (T-0760); `steps.py next` prints `lane red` when an inherited red's base is off the into branch (T-0766).
- Non-goals: changing behaviour.
- Done when: the criteria pass.

## Context
T-0760, T-0766 and T-0758 (2026-10-24) each had to drop or shorten a SKILL.md line because the file was within 30 characters of the limit `scripts/check-packaging.py` enforces.

## Acceptance criteria
1. `wc -c < plugins/sdlc-lite/skills/fanout/SKILL.md` prints at most 16500.
2. Every fact removed from SKILL.md is present in a linked `references/` file (list the moves in the Outcome), and SKILL.md names the T-0760 and T-0766 behaviours.
3. `python3 scripts/check-packaging.py` passes, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `git diff --check <base sha>` exits 0.

## Outcome
SKILL.md went from 17,997 to 16,379 characters. Moves (each full text is verbatim in the target, SKILL.md keeps a short linked line):
- Run-from-root paragraph (wip commit, `dirty before sync`, `integration dirty`) to `references/lane-lifecycle.md` "Stops and dirty trees"; SKILL.md keeps a shorter line that also states the T-0772 `bookkeeping: <paths>` commit.
- External lane paragraph to `references/lane-lifecycle.md` "External lanes".
- Step 3 hook sentence (`hooks/block-background.sh` and the SDLC_HEADLESS launcher rule) to `references/lane-lifecycle.md` "Headless runs"; SKILL.md keeps `SDLC_HEADLESS=1`.
- Legacy lane root (`migrate-worktrees.sh`) sentence to `references/lane-lifecycle.md` "Legacy lane roots".
- Sub-agent step 4 `sync` paragraph (generated files, `--regen`, `sync conflict`) to `references/land.md` "Sync a running lane".
- Sub-agent step 5 (full ticket driven by the parent) to `references/land.md` "Full tickets in sub-agent mode".
- PR merge paragraph to `references/main.md` "PR merge"; SKILL.md keeps both invariants' commands because `check.py` item "merge ops" requires them there.
Added lines: T-0760 (`stop: blocked` from `advance`, step 3) and T-0766 (`lane red`, Report), with the rules also written in `references/land.md`; T-0772 in the run-from-root line.
Not added: T-0770 (the fix has not landed; settle still exits 1 then) and T-0765 (the amend retag lives in the chain skill, not fanout).
Checks: `wc -c` 16379; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 8e8a3653` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 8e8a36530db1
- Changed: see commits
- Commits: 091b9d3 T-0780: give the fanout skill room under its size limit
- Check: 1 `wc -c < plugins/sdlc-lite/skills/fanout/SKILL.md` prints at most 16500: pass
- Check: 2 Every removed fact is present in a linked references/ file, and SKILL.md names the T-0760 and T-0...: pass
- Check: 3 `python3 scripts/check-packaging.py` passes, `python3 plugins/sdlc-lite/scripts/check.py` exits 0...: pass
- Follow-up: note: plugins/sdlc-lite/skills/fanout/references/lane-lifecycle.md:9... -> notes.md
- Follow-up: note: plugins/sdlc-lite/skills/fanout/SKILL.md:58 mentions a stop... -> notes.md
