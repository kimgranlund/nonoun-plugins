---
id: T-0674
title: "prepare refuses a guidance path that is missing everywhere, not only in the lane"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0655]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` refuses a lane dispatch only when a named guidance path is present in the main checkout or the lane's `into` branch and missing from the lane, which is real lane drift. A path that exists nowhere at that spelling (for example a plugin-relative `skills/handoff-format/SKILL.md` in a handoff) no longer blocks the dispatch.

## Intent
- Do: in `lane_guidance` (`plugins/sdlc-lite/scripts/dispatch.py`, the loop near line 620), append to `missing` only when `where` is set; keep the "present on" message. Update the docstring near line 75 to match. Add a selftest case: a handoff naming a guidance path absent from the lane, the main checkout and the into branch prepares normally (exit 0, no refusal line).
- Non-goals: resolving plugin-relative paths.
- Done when: the criteria pass.

## Context
Found live 2026-10-20: right after T-0655 landed, `dispatch.py prepare verifier L2` for T-0661 exited 5 with `guidance missing in lane: skills/handoff-format/SKILL.md` and no "present on" part. The handoff names the file plugin-relative; it exists at `plugins/sdlc-lite/skills/handoff-format/SKILL.md` in both trees. Every lane handoff that cites a plugin-relative skill path is blocked until this lands. The existing case at dispatch.py:2462 (present on main, missing in lane, exit 5) must keep passing.

## Constraints
The T-0655 refusal for real drift is unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case, and the new case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check <base sha>` exits 0.
