---
id: T-0325
title: "Make every skill self-contained: ship its resources, drop repo-relative path assumptions"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0324]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every skill under plugins/ runs from its own folder plus `${CLAUDE_PLUGIN_ROOT}` scripts, with no reliance on a repo-relative path (docs/, plugins/, ../../) or a specific consumer file layout stated in the skill text.

## Intent
- Do: Audit all 37 skills. Highest reference counts first: handoff-format (24), ticket (17), fleet-retro (16), plan-goal (11), ask (8), file (5), sdlc-lite (3), onboard (3). For each reference, either move the needed file into the skill's own folder (a `resources/` folder is the convention set by T-0324), make the script resolve the consumer path, or state the path as a thing the script discovers. Add a `check.py` guard that fails when a SKILL.md links a path that leaves its skill folder or starts with `docs/`, `plugins/` or `../`, with an observed negative control. Both the Claude and Codex layouts must still resolve (`codex_roles.py generate --check`, `check-packaging.py`).
- Non-goals: changing what a skill does, role bodies, models or efforts.
- Done when:
  - The new guard passes on all skills and fails on a planted outside link (observed).
  - `check.py`, `check-packaging.py`, `codex_roles.py generate --check` and `tickets.py check` pass.
  - Skills outside this repo's checkout still find their files: run one converted skill from a throwaway project dir (observed).

## Context
User direction on 2026-10-06: skills should be as self-contained as possible and not rely on specific local files being in a certain place. The invariant is recorded in plugins/sdlc-lite/AGENTS.md. Do after T-0324, which creates the first resources folder.

## Constraints
No em or en dashes. No push or publish. Skill behavior unchanged.
