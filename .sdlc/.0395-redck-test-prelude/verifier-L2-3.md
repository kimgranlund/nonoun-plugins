## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/redck.py selftest`: pass. Evidence: run on the built tree, rc=0, ends `redck selftest: PASS`, including 4 new T-0395 cases. Bite (the throwaway worktree add was refused by the block-stray-worktree hook because SDLC_TMP_WORKTREES is unset in this session, so I mutated copies of the built scripts under the tmp prefix instead): with split_prelude returning `dirty, {}`, 3 new cases failed ("declared new test, implementation untouched...", "...content changes after recording...", "declared test plus one source edit..."). With the sha256 compare in prelude_changed disabled, the "content changes after recording" case failed. With a blanket `tests/` ignore, the "undeclared new test is retrospective" and "unsafe tests: entry" cases failed. With the implementation paths dropped, the "declared test plus one source edit" case failed. With the unsafe-entry filter in steps.declared_tests removed, the "unsafe tests: entry" case failed. So each Done-when case can go red.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: rc=0, `steps selftest: PASS`, including the new `(k2c) lint refuses a tests: entry` cases for `tests/`, `tests/*.sh`, `/abs/a.sh`, `../a.sh` and `(k2c) exact test files lint ok`. Bite: with the problem filter in declared_tests disabled, the four `(k2c) lint refuses` ok lines did not appear. That mutated copy then crashed later because it ran outside the plugin layout.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: rc=0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`. This is a gate and is green, so no base run was needed.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass. Evidence: rc=0, with only the existing placeholder and flat-layout warnings.
- `grep -q 'tests: <path>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: rc=0 on the built tree (plugins/sdlc-lite/skills/handoff-format/SKILL.md:141). Against the base copy from `git archive a4c96c17` it gave rc=1, so the check bites.
- Behavior (declared dirty test is a hashed prelude, undeclared test or source path is retrospective, a declared test changed after recording makes audit report prelude-changed): pass. Evidence: an independent CLI run of the built `redck.py` in a scratch git repo (a handoff with `- (red) \`test -f impl.txt\`` and `tests: tests/a.sh`):
  - Declared tests/a.sh only: `recorded 1 pre-edit control(s) red`, control `{'phase': 'pre-edit', 'result': 'red', 'dirty': [], 'prelude': {'tests/a.sh': 'd6c667bd...'}}`, which matches `shasum -a 256 tests/a.sh`. After impl.txt was created, audit gave `redck: audit: ok`.
  - Then tests/a.sh was rewritten: audit gave `redck: audit: prelude-changed (declared test changed: tests/a.sh)` and process-deviations.md gained `process deviation: red-checkpoint: prelude-changed: ...`.
  - Declared test plus src.txt: `phase: retrospective, dirty: ['src.txt']`.
  - Undeclared tests/b.sh: `retrospective, dirty: ['tests/b.sh'], prelude: {}`.
  - No tests: line: retrospective.
  - `tests: tests/` (a directory): stderr says `tests: entry tests/ is not an exact repo-relative file path and declares nothing`, and the phase is retrospective.
  - The same declared-test scenario with the base redck.py (git archive of a4c96c17) recorded `retrospective` and audited `retrospective`, which reproduces the bug.

## Out of scope changes
None.
- plugins/sdlc-lite/scripts/steps.py adds declared_tests and a lint finding. The Do asks to "lint it", and redck.py imports declared_tests, so this is in scope.
- .sdlc/0395-redck-test-prelude/handoff.md gained only the `## Acceptance criteria` block (checked with git diff).
- Audit consumers (run.sh:714 and dispatch.py:962) discard the audit output, so the new status name breaks no dependent (checked with grep).
- The em/en dash scan of the added lines found nothing, and `git diff --check` gave rc=0.
- Steelman of a finding I dropped: docs/references/sdlc-internals.md:103 still lists the audit statuses without `prelude-changed` and does not mention the prelude. The builder's rebuttal would be that the handoff's Done-when names only the handoff-format line. That rebuttal holds, so I did not file it as a fail. It remains a stale-doc follow-up.

## For the next attempt
None
