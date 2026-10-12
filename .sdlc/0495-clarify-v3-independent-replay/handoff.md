---
id: T-0495
title: "Independent replay of the clarify v3 skill on the ten eval cases (T-0461 follow-up)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The ten eval cases for `/clarify` v3 are replayed by someone other than the skill's builder, so the report states a verified result.

## Intent
- Do: replay each of `plugins/sdlc-lite/skills/clarify/evals/*.ask.md` against the current `plugins/sdlc-lite/skills/clarify/SKILL.md` using the method of `docs/reports/2026-10-11-clarify-v2-replay.md`: a fresh-context sub-agent per case (Sonnet), each given only the skill text and the ask; the replaying agent does not write the replay prompts differently per case and does not judge its own work. Run `python3 plugins/sdlc-lite/scripts/plan_check.py clarify` on every produced handoff block. Report per case: the output class (handoff block, `already scoped:`, `follow-up:`, `stopped:`), the lint line, and whether it matches the expected class in the case file. Write the result to `docs/reports/2026-10-12-clarify-v3-independent-replay.md` and say in its first lines which agent ran the replay and that the builder of the skill did not judge it.
- Non-goals: any change to the skill, the evals or the lint; judging level estimates (cases 02, 04, 05 and 06 differ from expected levels, noted in T-0461, left for a later retro).
- Done when: the report lists all ten cases with class, lint line and match; the verifier (a different agent from the replayer) reruns two of the ten cases and agrees; `git diff --check` is clean.

## Context
Origin: T-0461 filer follow-up `fix-now`: "Rerun the 10-case replay with an independent model run (the spawning builder judged the first one); the current result is unverified." First replay: `docs/reports/2026-10-12-clarify-v3-replay.md` (7 of 7 non-pass-through accepted, 3 of 3 pass-through, unverified). The plan merge chain builds on `/clarify`.

## Constraints
Docs and one report only; no plugin file edits. State only what a command shows.
