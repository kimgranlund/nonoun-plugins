<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: added the `next verify: build L3 done, no verifier -> verify L2` check in `selftest()`, right after the L4 case (2 added lines).

## Checks
- `grep -q "build L3 done, no verifier -> verify L2" plugins/sdlc-lite/scripts/steps.py`: found.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0, printed `steps selftest: PASS`.
- Mutant check: I copied the whole `scripts/` dir to a temp dir and changed `verifier_level` so L3 maps to 3. `selftest` exited 1 and stderr listed `next verify: build L3 done, no verifier -> verify L2`.
- `git diff --stat -- plugins/sdlc-lite/scripts/steps.py`: 2 insertions and no deletions.
- `plugins/sdlc-lite/scripts/check.sh`: I only read the last 5 lines, which showed run selftest, hook selftest, hook live probe selftest, shellcheck, and plugin validate all passing. I did not compare it against the base commit.

## Notes
- The mutant check needs the whole `scripts/` dir because `steps.py` imports the sibling module `order`. Copying `steps.py` alone fails with `ModuleNotFoundError`.
- The guard's second clause does not hold literally. `git diff --name-only` also lists `.sdlc/0081-add-a-steps-py-selftest/handoff.md`, which was already modified before my edit, and I did not touch it. The `steps.py` diff itself is additions only.
