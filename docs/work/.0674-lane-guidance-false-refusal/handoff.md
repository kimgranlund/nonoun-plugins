---
id: T-0674
title: "prepare refuses a guidance path that is missing everywhere, not only in the lane"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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

## Outcome
`lane_guidance` in `plugins/sdlc-lite/scripts/dispatch.py` now appends to `missing` only when the path is held by the main checkout or the lane's `into` branch; a path held nowhere no longer refuses. Docstring and the `guidance` header paragraph updated. New selftest case: a handoff naming `skills/nowhere/SKILL.md` prepares with exit 0 and no refusal line. Checks: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0 (the new case FAILs with the change reverted), `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `git diff --check da4d03e3` exit 0.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: da4d03e38580
- Changed: see commits
- Commits: 1db66ff T-0674: lane guidance check skips paths missing everywhere
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case, and the new c...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 3 `git diff --check <base sha>` exits 0: pass
- Check: 4 Brief extra, live prepare on this lane's handoff: pass
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py:77 the header paragraph now... -> notes.md
