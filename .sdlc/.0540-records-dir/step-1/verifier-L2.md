<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 records-dir new, dotted and step folders: pass. Evidence: extracted verbatim from the handoff and run under bash with `SDLC_TMP_WORKTREES` set to the tmp prefix: exit 0. At the base sha (`git archive 27a0cc9c plugins/sdlc-lite/scripts` copy) the same span exits 1 (`order.py` raises IndexError on the unknown `records-dir` argument), so it bites.
- #2 legacy markers and runtime precedence: pass. Evidence: exit 0 on the built tree, exit 1 at base. Bites on the `records-dir` subcommand and on the legacy/runtime branch order.
- #3 `skips.md` is not a legacy marker: pass. Evidence: exit 0 on the built tree, exit 1 at base.
- #4 `records.sh` `records_dir` and `records_dir_make`: pass. Evidence: exit 0 on the built tree. At base it exits 1 with "records.sh: No such file or directory". The span checks the returned paths, the created dir and `.gitignore` containing `*`.
- #5 `newest` finds a result in runtime: pass. Evidence: exit 0 on the built tree, exit 1 at base (empty output).
- #6 `task-dir` reverse map: pass. Evidence: exit 0 on the built tree, exit 1 at base (IndexError).
- #7 `records_dir(create=True)` makes the dir and `.gitignore`: pass. Evidence: exit 0 on the built tree. At base it fails with `AttributeError: module 'order' has no attribute 'records_dir'`.
- #8 `steps.py lane` sees a runtime plan, `skips.md` written in the task folder: pass. Evidence: line 60 of the handoff extracted and run in a fresh git fixture, exit 0 on the built tree (no `steps.py` edit). At base, exit 1 (the plan in runtime is not found), so it bites.
- #9 selftest prints `ok: (g) records_dir`: pass. Evidence: `order.py selftest` exit 0 prints nine `ok: (g) ...` lines (seven `records_dir`, two `task_dir`). The base selftest has none, so the grep exits 1 there.
- #10 `shellcheck --severity=warning plugins/sdlc-lite/scripts/records.sh`: pass. Evidence: exit 0, no output.
- #11 (guard) only `order.py` and `records.sh` change outside `.sdlc`: pass. Evidence: the guard pipeline exits 0. `git diff --name-only 27a0cc9c -- . ":(exclude).sdlc"` lists only `plugins/sdlc-lite/scripts/order.py`, and the untracked list only `plugins/sdlc-lite/scripts/records.sh`.

Builder claims checked against the tree and not taken from the summary:
- "Bash and Python agree": walked six fixtures (new folder, a task whose `step-1` holds only `handoff.md`, that step dir, a task with a legacy `step-1/builder-L2.md`, the legacy step dir, a dotted step dir). `order.py records-dir` and the sourced `records_dir` printed identical paths in every case. A trailing-slash relative input gave the same runtime path in both.
- "Existing consumers unbroken": `steps.py selftest`, `results.py selftest`, `board.py selftest` and `dispatch.py selftest` all PASS on the built tree. `order.py bogus` now prints the Usage block instead of raising IndexError. `fanout.py selftest` and `tickets.py selftest` produced no output, so they are not a usable check. I killed both hung runs, which were mine.
- Red-first order: `red-checkpoint.jsonl` holds control records at `base_sha` 27a0cc9c. There is no `process-deviations.md`.

## Out of scope changes
None. Besides the two allowed files, the tree changes only `.sdlc/` records (ticket and step records, run logs and dispatch files), which the guard excludes.

## For the next attempt
None.

## Notes
- plugins/sdlc-lite/scripts/order.py:_legacy and plugins/sdlc-lite/scripts/records.sh:_records_legacy: the Do's rule 4 says a `step-<n>` dir is a legacy marker. The build counts it only when that step dir itself holds `runs.jsonl`, `*.attempt.json` or a role result. A task whose only content is `step-1/handoff.md` therefore goes to runtime here but would record in place under the literal rule. No criterion tests it, and Python and bash agree with each other. Steps 2 and 3 should know the narrower reading when they switch callers.
- The criterion-extraction regex I used first missed some criteria. I ran those (#8 to #11) by hand, so every criterion was observed.
