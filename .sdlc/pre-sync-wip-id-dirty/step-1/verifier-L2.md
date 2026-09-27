<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- End-to-end mktemp run (AC1): pass. Evidence: ran the exact command from the handoff against the built tree: `EXIT:1`, `REPORT_ROW_OK`, `SUBJECT_OK`, `NOT_ANCESTOR_OK`, `NO_DIRTY_OK`, `T1_PRESENT_OK` all printed. Bites: ran the same command against a copy of `fanout.py` with the new `return` line removed (simulating pre-fix behavior) — got `EXIT:0` instead of 1, so the check discriminates.
- `grep -qF "dirty-sync case:" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: `AC2_OK` printed; `git diff` shows the string at the case-8 comment and `expect(f'dirty-sync case: ...`.
- `grep -qF "dirty-sync control:" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: `AC3_OK` printed; present in the negative-control block of the diff.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, prints `fanout selftest: PASS`: pass. Evidence: ran it in the built tree, got exactly `fanout selftest: PASS`, exit 0. Bites: copied the whole `scripts/` dir to `/tmp/verify-fanout-check2`, removed the new `return 'dirty before sync', f'wip {sha}'` line, reran `selftest` there — got `fanout selftest: FAIL` with 6 `dirty-sync case:` lines red (T-0002 wrongly merged, `dirty.txt` reached `fanout/ds`, ticket status flipped to `done`), matching the pre-fix bug from the ticket. Restored nothing needed since the edit was on a throwaway copy, not the working tree.
- `sed -n "1,/^import /p" ... | grep -qF "dirty before sync"`: pass. Evidence: `AC5_OK` printed; docstring change visible in `git diff` above the `import` line.
- `! grep -qF "Before each sync, a dirty lane tree is WIP-committed first" ...`: pass. Evidence: `AC6_OK` printed; the old sentence is removed per the diff.
- `grep -qF "dirty before sync" .../SKILL.md`: pass. Evidence: `AC7_OK` printed; diff shows the new sentence in `SKILL.md` line 9.
- `! grep -qF "a dirty tree is also WIP-committed before each sync" .../SKILL.md`: pass. Evidence: `AC8_OK` printed; old phrase removed in the diff.
- `grep -qF "dirty before sync" CLAUDE.md`: pass. Evidence: `AC9_OK` printed; diff shows the new phrase in the `scripts/fanout.py` bullet.
- `! grep -qF "and before a sync finds a dirty lane tree" CLAUDE.md`: pass. Evidence: `AC10_OK` printed; old phrase removed in the diff, and only that one sentence in the bullet changed (rest of the very long bullet is byte-identical per diff).
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md`: pass. Evidence: `AC11_OK` printed; file untouched.

## Out of scope changes
`.sdlc/pre-sync-wip-id-dirty/handoff.md` (modified), `.sdlc/pre-sync-wip-id-dirty/planner-L2.md`, `runs.jsonl`, and `step-2/` (untracked) also differ from a clean checkout. Checked: these are all planner-phase artifacts with mtimes 18:34–18:39, while the step-1 builder log (`builder-L3.md`) is timestamped 18:42 — they predate this build step and belong to the `/chain` planning phase that ran before step 1, not to this step's build. Dismissing as pre-existing pipeline state, not a step-1 side effect.

## For the next attempt
None.
