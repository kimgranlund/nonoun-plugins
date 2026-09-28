<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Add a `steps.py selftest` case for a done L3 build, which must map to `verify L2`, so a mutant that maps L3 to verifier L3 turns the selftest red.

## Step 1: Add the L3 build → verify L2 selftest case
level: L1
### Do
In `plugins/sdlc-lite/scripts/steps.py`, in `selftest()`, add this check right after the `next verify: build L4 done, no verifier -> verify L3` check (near line 997), in the same style:
`check('next verify: build L3 done, no verifier -> verify L2', nxt(step(3, [('builder-L3.md', DONE)]), 'verify L2'))`
Change nothing else. Do not touch `verifier_level` or `next_action`.
### Acceptance criteria
- `grep -q "build L3 done, no verifier -> verify L2" plugins/sdlc-lite/scripts/steps.py` (red now: the case is absent)
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and prints `steps selftest: PASS`
- Mutant check, done in a copy and not on the tree: copy `plugins/sdlc-lite/scripts/steps.py` to a temp dir, edit the copy's `verifier_level` so L3 maps to 3, and run `python3 <copy> selftest`. It exits non-zero and stderr names the `build L3 done` case.
- (guard) `git diff --stat -- plugins/sdlc-lite/scripts/steps.py` shows only added lines, and `git diff --name-only` lists no other file.
- `plugins/sdlc-lite/scripts/check.sh` passes with no new findings versus the base commit.

## Risks
The mutant criterion depends on the builder finding `verifier_level` (line 454) to write the mutant. The `step(3, ...)` helper writes `level: L3` in the handoff, which matches the existing L2 and L4 cases.
