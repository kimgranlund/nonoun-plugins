---
id: T-0061
title: "Add a steps.py next <step dir> helper that reads the newest builder..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0060
---

## Goal
After any builder or verifier run, `/chain` and the conductor get the next escalation action from code (`steps.py next <step dir>`) instead of re-deriving it from prose, so a `plan defect:` tag or a blocked build can no longer be routed to a rebuild by mistake.

## Context
Follow-up from T-0060 (unpassable-plan-criteria/filer-L1.md):

Add a `steps.py next <step dir>` helper that reads the newest builder and verifier results through `order.py` and prints the next action. Today the plan-defect route is followed only by instruction in `/chain` and the conductor. That same channel was ignored in the second T-0060 report.

## Intent
Literal ask: add a `steps.py next <step dir>` helper that reads the newest builder and verifier results through `order.py` and prints the next action.
Deltas:
- Action vocabulary unstated: defaulted: mirror /chain step 4 exactly. One action per call, first stdout line is a keyword, e.g. `build`, `verify`, `rebuild` (first non-plan-defect fail at a level), `bump` (second non-plan-defect fail at the same level, naming the new level), `replan` (builder blocked, or verifier fail whose `## For the next attempt` starts with `plan defect:`), `done` (verifier pass), `stop` (fail at L5). Following lines may give the reason, the level, and the result file(s) read. The planner may refine names but must cover every /chain step 4 branch.
- Level for `build`/`rebuild`/`bump`/`verify`: defaulted: build level from the step handoff's `level:` or the newest builder file name; verifier level derived per the level-rubric (builder L1/L2 -> L1, L3 -> L2, L4/L5 -> L3).
- "Newest" means `order.py` (`newest`/`ordered`/`counts_after`, imported, never mtime); a verifier result counts only if it is newer than the newest builder result.
- Fail counting: defaulted: count non-plan-defect verifier fails after builder runs at the current level; plan-defect fails never count toward a bump.
- Where it is used: defaulted: /chain step 4 (and the conductor agent's escalation line) call `steps.py next` after each builder and verifier run and follow its action; the prose rules stay as the spec.
- Unparseable/missing result or bad dir: defaulted: nonzero exit with a message on stderr, nothing written.
- (gap: exact Status/Verdict line formats of builder/verifier results; default: read them from agents/builder.md and agents/verifier.md.)
Do: add `next` to scripts/steps.py (read-only, writes nothing), extend `steps.py selftest` to prove every action branch and the error case with fixtures, wire /chain step 4 and agents/conductor.md to it, and update the CLAUDE.md Layout `scripts/steps.py` line and the sdlc-lite-author agent if it lists steps.py subcommands.
Non-goals: changing escalation rules themselves; making /chain executable code; touching order.py's rule.
Done when: `python3 plugins/sdlc-lite/scripts/steps.py selftest` passes with a case per action, `plugins/sdlc-lite/scripts/check.sh` has no new failures versus the base commit, and /chain step 4 names `steps.py next`.

## Constraints
- `order.py` stays the single ordering rule; `next` never reads file times.
- `split` and `lint` behavior and their selftest cases are unchanged.
- `next` writes nothing to disk.
