<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 `check.py | grep -qF 'check.py: argument hints: '`: pass. Evidence: ran it, exit 0; check.py itself exits 1 with 78 `argument hints` FAIL lines (red on today's skills, as the step intends).
- #2 six named findings (agent H-2, build H-2, ticket H-3, report H-4, fleet-retro H-5, board H-6): pass. Evidence: loop over the six prefixes printed no MISSING; each is visible in the check.py output (e.g. `FAIL check.py: argument hints: skills/ticket/SKILL.md: H-3 hint is 361 characters, at most 100`).
- #3 (guard) no FAIL line other than argument hints: pass. Evidence: `! check.py | grep '^FAIL ' | grep -qvF 'check.py: argument hints: '` exit 0. The summary line `FAIL: 19 role levels...` is excluded by the trailing space.
- #4 seven control literals H-1..H-7 in check.py: pass. Evidence: loop printed no MISS. The literals sit at check.py lines near 1604-1634 of the diff.
- #5 (guard) no stub or reference skill flagged: pass. Evidence: `! check.py | grep -qE 'argument hints: skills/(plan-goal|...|level-rubric)/'` exit 0.
- #6 prompts.md section `## Skill arguments and questions`: pass. Evidence: grep exit 0; diff shows the hint grammar, hint rules H-1 to H-7, the Arguments table shape, and seven question rules.
- #7 `argument-hint` in plugins/sdlc-lite/AGENTS.md: pass. Evidence: grep exit 0; the diff adds one bullet under Contracts and routing naming `argument-hint`, the `## Arguments` table, the prompts.md anchor and check.py item 60.
- #8 `| Skill |` row of the README names check.py: pass. Evidence: grep exit 0; diff shows the Check cell now reads `prompt_lint P-2, P-3, P-6; check.py argument hints (H-1 to H-7)`, Enforcement still `enforced`.
- #9 docstring item 60 names H-1..H-7 and its controls, each a module-level mutant of `hints_bad`: pass. Evidence: read the `git diff` of check.py. Item 60 lists every rule and every control. The controls (`_hint_new` calls at module level) cover H-1, six H-2 fixtures, H-3 at 100 (positive) and 101, two H-4, H-5 (plus an `[options]` table positive), two H-6 plus a bad-header case, and H-7. All of them mutate in-memory text.
  Bite check: I copied `plugins/` to `/tmp/v0463b`, because the throwaway worktree add was blocked (SDLC_TMP_WORKTREES unset). I ran ten single-line mutants of `hints_bad` and `hint_parses` against the copy. Each mutant tripped its own control line:
  - `hint_parses` always true: all six H-2 controls red.
  - H-3 off: the H-3 control went red.
  - H-1 off: the H-1 control went red.
  - H-4 body check off and H-4 script check off: each control went red.
  - H-5 off: the H-5 control went red.
  - H-6 table-row check off: red. H-6 heading check off: the "two headings" control went red; the "without heading" control still tripped the other H-6 branch, so that mutant does not isolate it.
  - H-7 off: the H-7 control went red.
  - `[options]` table reading ignored: the positive control went red.
  The unmutated copy prints no control FAIL line.
- #10 (guard) `docs_check.py --root .`: pass. Evidence: `docs_check: 0 errors, 30 warnings`, exit 0.
- #11 (guard) only the four allowed files changed outside .sdlc: pass. Evidence: the `test -z` pipeline exited 0. `git diff --stat` lists check.py, AGENTS.md, README.md and prompts.md plus the .sdlc handoff. `git status` shows no change under plugins/sdlc-lite/skills.

## Out of scope changes
None. `.sdlc/0463-skill-ui-hints/handoff.md` (+3 lines) and the new .sdlc artifacts are task records, excluded by the guard.

## For the next attempt
None.

## Notes
- check.py, the H-2 "a double quote" control uses `new <slug> \"title\"`, which also holds a backslash and a bare word after the first item, so the quote is not the only biting variable. The mutant run still shows the control going red when the parser is broken, so it is a weak but valid control.
- The throwaway-worktree path was unavailable (hook: SDLC_TMP_WORKTREES unset), so the negative-control mutations ran on a copy under /tmp/v0463b; the project tree was not touched.
