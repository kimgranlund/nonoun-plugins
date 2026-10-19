---
id: T-0513
title: "A (parity) criterion for styling tickets: screenshot pair with named properties (T-0501 B4)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `(parity)` criterion makes a styling approval checkable: a capture command writes a real screenshot, the verifier compares it with a named mockup on at most five named properties.

## Intent
- Do: the form ``- (parity) `<capture command>` writes `<real.png>`; against `<mock.png>`: <property>, <property>`` (at most five properties, never "matches"); `steps.py lint` refuses a `(parity)` line with fewer than two image paths or no property list; one line in `agents/verifier.md` (run the capture as an observed run, Read both images, record pass or fail per property, unnamed differences are notes); document the form in `skills/handoff-format/SKILL.md`. A styling ticket writes `verifier: L3` when the owner wants it.
- Non-goals: image diff tooling; any change to levels.
- Done when: a `steps.py selftest` lint case for each refusal (red first) and one accepted form; `check.py` item for the verifier line observed red; `generate --check` for both hosts and `check.py` exit 0.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. Evidence: agent-ui QuestionCard shipped far from the approved mockup because the verifier checked behavior only.

## Constraints
No new prohibition in `verifier.md`. One writer on `verifier.md` (after B2).

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, and its `(parity)` cases hold: a one-image-path line and a no-property-list line are refused with the plan defect, a full form lints clean (the two refusals were red before `parity_findings` existed).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0, including the `verifier parity` item that flags a verifier file missing either phrase of the `(parity)` line in `plugins/sdlc-lite/agents/verifier.md` (seen red with one phrase removed from `verifier-L1.md`).
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0
- `grep -q 'a `(parity)` criterion passes per named property' plugins/sdlc-lite/agents/verifier.md` exits 0, and `grep -q 'steps.py lint` refuses a `(parity)` line' plugins/sdlc-lite/skills/handoff-format/SKILL.md` exits 0

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: The hook block-stray-worktree.sh blocked creating a throwaway worktree because SDLC_TMP_WORKTREES was unset ("role 'solo'"). Base and negative-control runs used a `git archive 07a5c289` extract and a file copy under /tmp/v0513.xyFG instead. Permission to remove that directory afterwards was denied, so it remains outside the repo. | plugins/sdlc-lite/scripts/steps.py:1707: lint does not enforce the "at most five properties" or the never-"matches" part of the form. Only the documentation and the verifier line carry them. The Intent asks lint to refuse only the missing-paths and missing-property-list cases, so this is no criterion gap.
