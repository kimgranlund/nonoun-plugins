<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1 (resume prints `done` for step-1 and step-2 batch-listed, step-3 per-step passed): pass. Evidence: I extracted the spans from the handoff and ran each one with `bash` from the repo root. rc=0. The same span in a detached worktree at `$SDLC_BASE_SHA` gives rc=1, so it can go red.
- Criterion 2 (a newer `-2` builder in step-2 is not listed, so `$t/step-2 verify L1`): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 3 (step-2 unlisted gives verify): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 4 (an L4 build gives `verify L3`): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 5 (a `Merge ` title gives verify): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 6 (a `gates green` title gives verify): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 7 (the last step gives verify): pass. Evidence: rc=0 on the built tree, rc=1 at base.
- Criterion 8 (a superseded sibling gives verify): pass. Evidence: rc=0 on the built tree, rc=1 at base. I also disabled the superseded check in a temp copy of `steps.py`. `selftest` then failed on "next batch: a step with a superseded sibling -> verify", so that check bites.
- Criterion 9 (`steps.py selftest` prints `ok: next batch:`): pass. Evidence: rc=0. `selftest | grep -c "ok: next batch"` prints 16, and the run ends `steps selftest: PASS`. The criterion fails at base (rc=1).
- Criterion 10 (`## Verified` appears in `steps.py`, the handoff-format `SKILL.md` and `sdlc-internals.md`): pass. Evidence: rc=0 on the built tree, rc=1 at base. I read the diff. The docstring, the new SKILL section (placed before `## Free-text arguments`) and the `sdlc-internals.md` clause all name `## Verified` and list the exclusions and the newest-listing rule.
- (guard) scope: pass. Evidence: rc=0. The un-negated form lists exactly `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/scripts/steps.py` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, so it is not vacuous.
- Focused checks: pass. Evidence: `order.py selftest` and `results.py selftest` both print PASS. `check.py` prints "ok: 19 role levels, 9 agents checked". `check-packaging.py` prints PASS. `git diff --check` is clean.
- Builder claims (one function plus one call site, 16 selftest cases): pass. Evidence: I read `git diff` of `steps.py`. `batch_verified` is the only copy of the rule, and `next_action` has one call, inside the `v is None or not counts_after` branch. A step-dir verifier counting after the build still decides first.

Steelman pass: I considered failing on the cosmetic `why ='no verifier result'` spacing and on a step with no `## Step` line counting as an empty title. The builder would answer that the handoff specifies neither, and the second is documented in its Notes. Both findings are dropped.

## Out of scope changes
None. The untracked `.sdlc/0196-batch-state/step-1/*` files are run artifacts, and the guard excludes `.sdlc`.

## For the next attempt
None
