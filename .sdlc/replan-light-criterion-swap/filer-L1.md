<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0123: Apply a verifier's replacement criterion with `steps.py swap`, and harden planner criteria against stale checks

## PR body
### Summary
Plan defects were the top stop cause in the gen-ui overnight lanes: 8 in total. The verifier's `plan defect:` note usually proposes a replacement criterion, but every such note forced a planner L3 replan. This PR lets a verifier-proposed swap be applied to the step handoff and rebuilt at the same level when the swap is provably safe. It also adds two planner rules so criteria stay stable across main syncs and guards can go red.

### Changes
- `steps.py swap <step dir> [--timeout SECONDS]` is a new subcommand.
  - The verifier's `## For the next attempt` note must hold exactly one `swap old:` line with one code span and exactly one `swap new:` line.
  - Preconditions: the newest verifier result counts after the newest builder, its verdict is `fail`, it carries the `plan defect:` tag, and the step has no earlier swap.
  - The old span must appear on exactly one criterion line.
  - The new text must keep the line's `(guard)` tag, hold a command span, skip no `HEAD^1` or `<placeholder>` span, and lint clean.
  - Each new span is run under `bash -c` from the git toplevel and refused if it is red, times out, or changes the work tree.
  - Every refusal writes nothing, exits 1, and ends with a `plan defect: steps swap refused: <why>; replan this step (/chain 4.2)` line.
  - An already-applied swap prints `swap: already applied` and exits 0.
- `steps.py next` prints `swap L<level>` for a plan-defect fail with a valid first pair. Every other plan defect still goes to `replan`. A swap-routed fail is not counted toward a bump.
- `verifier.md` states the swap format. A builder never proposes a swap.
- `/chain` (step 4 and a new item 8) and the conductor route `swap` to `steps.py swap`, then rebuild at the printed level with no `## Previous attempt`. They record a `swap applied:` line under `## Plan review`. A refused or second swap takes the planner L3 replan.
- `handoff-format` and `level-rubric` skills, `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` are updated so the records match.
- `planner.md` gains rules 11 and 12. Rule 11: see each `(guard)` red first (un-negated, or on a fixture) so it can go red. Rule 12: check files other lanes also change by membership or structure, not by an exact line.
- `check.py` guards the new phrases (`swap old:`, `swap new:`, `steps.py swap`, `can go red`, `membership or structure`) across the docs.

### How each was verified
All three steps have a `pass` verdict from an independent verifier.
- Step 1 (verifier L2): all 14 criteria were run verbatim. The new-behavior criteria fail on a HEAD worktree, so they can go red. A copy of `steps.py` with the red-span refusal disabled fails the selftest case `swap: (c) new span red now`. The builder added 23 selftest cases (18 `ok: swap: `, 5 `ok: next swap: `). It also ran a mutation test with the `(guard)` tag check and the swap tree-change check disabled, and the selftest went red.
- Step 2 (verifier L2): the nine greps pass in the tree and fail at HEAD where checked. A probe that strips `steps.py swap` from the chain skill makes `check.py` print `plan-defect route missing "steps.py swap"`. The verifier read the chain section 4 diff. `check.py plugins/sdlc-lite` exits 0.
- Step 3 (verifier L1): the greps pass. A negative control replacing "can go red" with `xx` makes `check.py` print `plan-defect route missing "can go red"`. Rules are numbered 1 to 12 with no gaps, and only added lines appear in the `planner.md` diff. `check.py` and `check.sh` exit 0.
- Step 1 caveat: the step 1 verifier saw `check.sh` intermittently fail with `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0`. This step changes no hook. `hook-selftest.sh` alone passed 20 of 20, and `check.sh` at HEAD passed 4 of 4 runs (see the first follow-up).

## Changelog entry
- Added `steps.py swap`: when a verifier fails a step with a `plan defect:` note holding one `swap old:`/`swap new:` pair, the criterion is swapped in the step handoff and the step rebuilds at the same level, with no planner L3 replan. The swap is refused, and the step replans, if the new criterion is red, changes the work tree, drops its `(guard)` tag, or is a second swap on the step. `steps.py next` prints `swap`, and `/chain` and the conductor route it.
- Planner rules 11 and 12: a `(guard)` must be seen red first so it can go red, and files that other lanes change are checked by membership or structure, not an exact line.

## Follow-ups
- Investigate the intermittent `check.sh` failure `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0` (SIGPIPE, likely a timing race). It appeared on the built tree in the step 1 verification, and `hook-selftest.sh` alone passed 20 of 20.
- Mirror the extended planner rules (a guard seen red first, membership or structure checks) into `.claude/agents/sdlc-lite-author.md`. The step 3 builder did not, and the file lists the plan-defect route the maintainer must keep in sync.
