---
id: T-0089
title: "The merge-step conflict-marker guard misses a kept conflict-marker..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0069
---

## Goal
The merge-step conflict-marker guard's known gap (a kept conflict-marker line textually identical to a parent line, shown as `+ ` or ` +` in `git diff-tree --cc`, not `++`) is either closed or explicitly documented as an accepted limitation, and check.py's behavior probe has a case that pins whichever outcome is chosen.

Decision rule (unattended, no user present): close the gap if a guard exists that (a) flags this new case, (b) still passes all five existing probe cases, especially the legit lane line case, (c) stays one lint-clean criterion line that parses under `bash -n` and has no `||` between checks, and (d) stays readable. If no such guard exists, keep the current guard, add the probe case asserting the documented miss (so a future change is noticed), and record the limitation in the template's surrounding docs and CLAUDE.md. The planner records which branch it took and why under the plan.

## Context
Follow-up from T-0069 (conflict-guard-lane-false-positive/filer-L1.md):

The merge-step conflict-marker guard misses a kept conflict-marker line that is textually identical to a parent line and aligns with it in the combined diff (shown as `+ `, not `++`). Add a probe case and decide whether to close the gap.

## Constraints
- The two `merge-step` template copies (`plugins/sdlc-lite/agents/planner.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md`) stay byte-identical; check.py enforces it.
- The existing five probe cases in `plugins/sdlc-lite/scripts/check.py` keep their expected outcomes.
- `steps.py split --only` skips only guard spans containing `HEAD^1`; a new guard must be green on a pre-merge tree unless the prior HEAD kept markers.
- CLAUDE.md and `.claude/agents/sdlc-lite-author.md` describe the criterion; update both if it changes.
- `plugins/sdlc-lite/scripts/check.sh` stays green. No em dashes.
- Never commit, push, or publish.
