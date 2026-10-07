<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criteria 1 to 5 (the five `ok: (lane) ...` labels: before planning, lean for F/E/A, L4 negative, `## Plan review` negative, every `review_required` reason): pass. Evidence: I ran each criterion command verbatim through `bash -c`, and all returned rc 0. `steps.py selftest` prints `steps selftest: PASS` with 215 `ok:` lines, and all 9 `(lane)` labels are present at lines 207-215. At `$SDLC_BASE_SHA` in a throwaway worktree, the first of these criteria returned rc 1, because `steps.py lane` was an invalid choice there.
- Criterion 6 (the four labels: full after planning, skips.md, sticky, missing dir): pass. Evidence: the criterion's `for` loop returned rc 0, and the four labels appear as `ok:` in the selftest output. I also mutated a temp copy (`LANE_MAX_STEPS=3` plus `steps.py` removed from `LANE_CONTRACTS`). The full-after-planning case went red with `FAIL, these did not hold: (lane) full after planning ...`, so the check bites.
- Criterion 7 (size M handoff gives `lean`, with the exact skips.md line): pass. Evidence: the command returned rc 0. A separate run on an XL handoff printed `full`, `reason: size XL decides before planning (no planner result yet)` and `read: <path>/handoff.md`. It created skips.md as `# Skips`, a blank line, `## Lane`, and the record.
- Criterion 8 (no front matter gives `full` with the no-size reason, with no traceback): pass. Evidence: the command returned rc 0, covering stdout and the exact skips.md line.
- Criterion 9 (docstring has a `\n  lane ` entry mentioning `skips.md`, and `lane_action` source holds `review_required(`): pass. Evidence: the command returned rc 0. The base `steps.py` has no `lane` subcommand at all, so this check is red there.
- Criterion 10 (`docs/references/sdlc-internals.md` names `skips.md` and `review_required`): pass. Evidence: the command returned rc 0, and the base grep for `skips.md` returned rc 1. The diff shows the `lane <task dir>` clause right after the `review` clause. It names `fix`/`lean`/`full`, the `reason:` and `read:` lines, `review_required()`, the size-only rule before planning, the after-planning conditions, the sticky `full`, and the `- lane:` line under `## Lane`. It also names `LANE_CONTRACTS` and the exit-1 cases.
- (guard) `results.py selftest`: pass. Evidence: rc 0 in the run of all 13 criteria. The lazy `import tickets` sits inside `lane_action` (steps.py in the diff), with a comment saying why.
- (guard) no em dash in `steps.py` or `sdlc-internals.md`: pass. Evidence: rc 0.
- (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: rc 0. `git status --short` shows only those two files modified, plus untracked files under `.sdlc/`, which the guard excludes.
- Spec behaviors I probed directly beyond the criteria:
  - `lane /nonexist` gives rc 1, empty stdout, and one stderr line `steps lane: no such directory: /nonexist`.
  - Passing a file path instead of a dir gives the same one-line error.
  - An existing `## Lane` section with a record, a blank line, `## Skipped`, and `- x` with no final newline gets the new record right after the old one. `od -c` shows the blank line, `## Skipped`, and `- x` kept, with only a trailing `\n` added.
  - A sticky skips.md gives `full` with the sticky reason, and `read:` lines for both `handoff.md` and `skips.md`.
  - `lane -h` and the top-level `-h` list `lane` and name `skips.md` in its help text.
  - `python3 plugins/sdlc-lite/scripts/check.py` prints `ok: 19 role levels, 9 agents checked`, so the `SCHEMA_COPY` regex is not tripped. A grep of `steps.py` for `REVIEW_VERDICTS`, `startswith('inherited red:')`, and the `first_word(path, 'Status'|'Verdict')` calls found none.
  - `git diff --check` is clean.

## Out of scope changes
None. The tracked diff is only `plugins/sdlc-lite/scripts/steps.py` and `docs/references/sdlc-internals.md`. The untracked files under `.sdlc/0197-lane/step-2/` are run artifacts. `handoff-format/SKILL.md` is untouched, as the handoff required. I removed my throwaway worktree. I did not run `lane` on the real `.sdlc/0197-lane` dir.

## For the next attempt
None
