<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1 (ticket under `tickets/` and root task both render, `--task 0001-a`): pass. Evidence: I ran the command on a fresh temp tree. The board printed `| T-0001 | 0001-a | ready | ...` and `| side | ...`, and the `--task 0001-a` output contained `0001-a`.
- Criterion 2 (`--summary` = `0001-a 0% (0/1)`): pass. Evidence: I ran the command and the `test` exited 0.
- Criterion 3 (the selftest bites when `ticket_dir` is stubbed): pass. Evidence: I copied `scripts/*.py` into two temp dirs. In the unmodified copy `board.py selftest` exited 0. In the copy with `ticket_dir` stubbed to `return root` it exited 1. This also confirms the selftest needs no `skills/` folder.
- (guard) No config line, so `tickets/0001-a` is not listed: pass. Evidence: `grep -cF 0001-a` on the board output gave 0.
- (guard) `ticket_root: work` (unsupported), so the root task is still listed: pass. Evidence: `grep -cF '| T-0001 | 0001-a |'` gave 1.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`: pass. Evidence: it printed `board selftest: PASS`.
  - The guard checks cleared the pre-build gate rule. Each was run on the built tree and passed, and none went red, so no base-SHA comparison was needed.
  - The negative controls are real. The no-config and `ticket_root: work` cases each assert on the board output, and the selftest case 9 negative controls match those guards.
- (guard) Diff scope limited to `tickets.py` and `board.py`: pass. Evidence: the changed and untracked files outside `.sdlc` were only `plugins/sdlc-lite/scripts/board.py`.

## Out of scope changes
None. The diff touches only `board.py`. `git diff --check` is clean. The `.sdlc` artifacts are excluded by the scope guard.

## For the next attempt
None
