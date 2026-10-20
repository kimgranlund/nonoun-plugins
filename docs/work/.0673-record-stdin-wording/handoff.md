---
id: T-0673
title: "Skills say record reads the transcript, not the final message on stdin"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0667]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every skill that tells the conductor to run `dispatch.py record` says what `conductor.md` says after T-0667: run `record --agent-id <id>` with the notice figures and nothing on stdin; stdin only when the role's transcript is missing.

## Intent
- Do: reword the `record` sentence in `skills/{build,fix,agent,architect,dig,file,scout,research,verify,bench,fleet-retro,review-traces}/SKILL.md` and `skills/plan/references/steps.md` under `plugins/sdlc-lite/` to match the T-0667 wording in `agents/conductor.md` "How you run roles" step 3.
- Non-goals: any script change.
- Done when: the criteria pass.

## Context
Found by the T-0667 builder: those 13 files still say "with the sub-agent's final message on stdin", which contradicts `conductor.md` after T-0667 (stale guidance makes conductors scrape transcripts by hand, issue #27).

## Constraints
None.

## Acceptance criteria
1. `grep -rln "final message on stdin" plugins/sdlc-lite/skills` prints nothing.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `python3 scripts/check-packaging.py` exits 0.
3. `git diff --check <base sha>` exits 0.

## Outcome
Reworded the `record` sentence in the 13 named files (12 skills and `skills/plan/references/steps.md`) to the T-0667 wording: `record` with the figures from the completion notice, nothing on stdin, stdin only when the role's transcript is missing; dropped `--transcript <sub-agent transcript jsonl>` from those command lines. `check.py` item 41 (T-0334) required `--transcript` in every skill `record` call, which contradicts T-0667, so it now forbids it (negative controls swapped); this is the one script edit, forced by criterion 2. Criteria 1 to 3 pass; role generation is unchanged.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: d3bb0b41ad3a
- Changed: see commits
- Commits: 130724e T-0673: skills say record reads the transcript, nothing on stdin
- Check: 1 `grep -rln "final message on stdin" plugins/sdlc-lite/skills` prints nothing: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `python3 scripts/check-packaging.py` ex...: pass
- Check: 3 `git diff --check <base sha>` exits 0: pass
- Check: 4 Brief check (dropping `--transcript` loses nothing): pass
- Follow-up: note: plugins/sdlc-lite/skills/agent/SKILL.md:36 tells the solo record... -> notes.md
- Follow-up: decide: the handoff's Non-goals "any script change" contradict criterion 2... -> notes.md
