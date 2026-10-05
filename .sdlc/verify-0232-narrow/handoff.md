# Verify T-0232, narrow: the two findings of the first L3 pass

## Goal
Independently re-check only what the first verifier failed, on branch reorg-inventory (T-0232). The first pass (.sdlc/verify-0232/verifier-L3.md) passed criteria 1 to 4 and 6 and failed criterion 5; do not re-run check.sh or the script's selftest.

## Acceptance criteria
1. docs/validation/reorg-inventory-live-run.md: the sentence about the misplaced rows now matches the misplaced section of docs/validation/reorg-inventory-live-run/maison-inventory.txt (six README.md under src/components, two SKILL.md, the spec gen-ui-recipes.md and examples/application-patterns/component.md); no other sentence in the record contradicts a committed file under docs/validation/reorg-inventory-live-run/.
2. The plan-session sentence is backed: every number and name in it (success, 34 turns, total_cost_usd 2.5008968, 364376 ms, the two models in modelUsage with their costs, the one denied Bash call in permission_denials, the 122 lines of maison-plan.md) matches plan-session-full.json and the plan file, and the sentence makes no claim the files do not show. The flags in the claude command line are described as the command as run, not as recorded values.
3. All files under docs/validation/reorg-inventory-live-run/ are committed and not ignored (git ls-tree and git check-ignore), git diff --check main...HEAD is clean, and no em dash appears in the changed text files.

## Out of scope
The script, its selftest, the guard, and every gate: the first pass confirmed them and nothing under plugins/ has changed since.
