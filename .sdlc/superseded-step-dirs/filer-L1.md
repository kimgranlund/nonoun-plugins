<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0039: A defined name for superseded step dirs

## PR body
### Summary
When a replan replaces a step, the old step dir now gets a defined name, `step-<n>.superseded-<k>/`. `board.py` and `bench-summary.sh` no longer count these dirs as steps, but their cost is still counted. `/chain` renames the dirs during a replan, and `handoff-format` documents the name. Before this change, a hand-renamed dir such as `step-15-blocked` showed up on the board as a second "15." row and was counted as an extra step.

### Changes
1. **`scripts/board.py`**
   - New helper `live_step_dirs(task)`. It keeps only dirs whose name is exactly `step-<digits>`.
   - `plan_steps` and the `--summary` ⚠ L5 check now use the helper.
   - `cost()` and `has_step_work` still read every `step-*` dir on purpose, and a comment in each says so.
   - The docstring is updated.
   - New selftest case 5e.
2. **`scripts/bench-summary.sh`**
   - The steps, passed and attempts loop skips any dir whose name does not match `^step-[0-9]+$`.
   - The cost line is unchanged, so superseded dirs still count toward cost.
   - The old `ls -t` pick of the newest verifier file is now a glob loop using `-nt`. This fixes shellcheck finding SC2012.
3. **`skills/handoff-format/SKILL.md`**: adds a layout entry for `step-2.superseded-1/` and a rule line: a live step dir is exactly `step-<digits>`.
4. **`skills/chain/SKILL.md`** step 4.2: before writing fresh step handoffs, the conductor moves each replaced `step-<n>/` that already has builder or verifier output to `step-<n>.superseded-<k>/`, using the first free k.
5. **Audit of the remaining `step-*` readers**: no code changes were needed. `statusline.sh` only reads the step number from a running path. Every other hit is either a live-step reader, one of the readers that count every dir on purpose (cost, `has_step_work`), or a fixture or doc.

### Verification
- **Step 1** (verifier pass):
  - `board.py selftest` and `tickets.py selftest` pass. Case 5e checks: two steps, two board rows, no ⚠ L5, cost includes the superseded dir, and `has_step_work` is true when a task has only a superseded dir.
  - Negative control: with the helper removed, the selftest goes red with a `ValueError` on `2.superseded`.
  - A manual board render showed exactly two step rows.
- **Step 2** (verifier pass on the second attempt):
  - A fixture with `step-1` plus `step-1.superseded-1` prints steps=1, passed=1, attempts=1, cost=3. At HEAD it prints steps=2 and attempts=2.
  - shellcheck is clean. The first attempt failed only because of the SC2012 finding, which was already there at HEAD; the second attempt fixed it.
  - The newest-verifier behavior was checked with passing and failing verifier files in both orders.
- **Step 3** (verifier pass): `grep superseded` finds the three expected lines, and the same grep on HEAD finds nothing. `check.sh` exits with rc=0.
- **Step 4** (verifier pass):
  - The verifier classified every grep hit on its own.
  - `check.sh` exits with rc=0.
  - Negative control: with the live-step filter replaced by `True`, `check.sh` exits with rc=1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- A step dir replaced by a replan is now named `step-<n>.superseded-<k>/`. `/chain` renames it during a replan. The board and `bench-summary.sh` no longer count it as a step (no extra rows, totals, % or ⚠ L5), but its cost is still counted. Hand-renamed dirs such as `step-15-blocked` no longer render as steps.

## Follow-ups
None
