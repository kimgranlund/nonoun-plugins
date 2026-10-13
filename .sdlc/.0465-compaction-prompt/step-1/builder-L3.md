<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/scripts/plan_check.py: kind `compaction` (argparse, `run_check`, docstring usage and rule list), `check_compaction(text, entry=None, glossary=None)`, `compaction_counts`, the `lines:` and `pin:` lines in `main`, `GOOD_COMPACTION`, `compaction_selftest`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/scripts/compaction_handoff.py: created; `write`, `clear`, `status`, `selftest`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/scripts/check.sh: runs the new selftest after the `plan_check.py` line; named in the header comment.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/.gitignore: added `CLAUDE.local.md`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/references/compaction.md: created, 90 lines; the first fence is the worked example.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/SKILL.md: argument-hint, description, allowed-tools, `Arguments:` line, section 0 sentence, kind table row, reserved first word; 71 lines, 6599 bytes.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/evals/06-compaction.ask.md: created.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/evals/06-compaction.expected.md: created.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/plan/evals/README.md: case row `06-compaction`; "Five asks" and "of 5" now read six.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: one row `plan compaction` after the "Plan by kind" row.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/plugins/sdlc-lite/scripts/check.py: item 31 docstring text tagged T-0465, `plan_compaction_bad(texts)` and its inline negative controls.

## Checks
All run from the tree root with `SDLC_BASE_SHA=07a5c289eae8ce19db8ed716c2400c10841d9ac2` exported.
- Criterion 1, `plan_check.py compaction --file .../references/compaction.md`: exit 0; prints `lines: 18 of 60`, `pin: 7 of 40`, `ok: compaction plan passes`.
- Criterion 2, `plan_check.py selftest` with the nine-rule loop: exit 0; `plan_check selftest: PASS (293 checks)`.
- Criterion 3, `plan_check.py compaction --text "DROP x"`: exit 1 with `FAIL compaction-order: `.
- Criterion 4, `compaction_handoff.py selftest` with the six case names: exit 0; `PASS (6 cases)`.
- Criterion 5, the `SKILL.md` greps and description length: exit 0.
- Criterion 6, reference at most 90 lines and the 16 phrases: exit 0.
- Criterion 7, entry row, `git check-ignore -q CLAUDE.local.md`, `check.sh` line: exit 0.
- Criterion 8, `check.py` greps and `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.
- Criterion 9, eval files, `prompt_lint.py` (22 files, 0 errors, 0 warnings), `scripts/check-packaging.py` (PASS): exit 0.
- Guard, `SKILL.md` literals and size caps: exit 0, rerun after the last `SKILL.md` edit (71 lines, 6599 bytes).
- Guard, scope diff against `$SDLC_BASE_SHA`: exit 0.
- `git diff --check`: exit 0.
- `codex_roles.py generate --check`: exit 0.
- After the last `SKILL.md` edit, reran `check.py` (exit 0) and `prompt_lint.py` on `SKILL.md` (0 errors).

## Notes
- Observed red, `plan_check.py`: the first `plan_check.py selftest` ran against a stub `check_compaction` that returned no findings. It printed `FAIL:` for 24 compaction cases: every `flags` mutant of all nine rules, the glossary warning, the missing entry file, the `--text "DROP x"` subprocess case and the reference example. The run after the rules landed left only the reference case red (file not yet written), and the run after the reference was PASS.
- Observed red, `compaction_handoff.py`: its selftest passed on first run, so I ran five sed mutants of a temp copy (host guard off, ignore guard always true, body cap 99, stale at 99 hours, span not removed). Each of the six cases failed under at least one mutant.
- `redck.py record` was not run because no criterion is tagged `(red)`. `check.sh` was not run because the handoff assigns it to step 2.
- `SDLC_BASE_SHA` was empty in the shell. The verifier must export `07a5c289eae8ce19db8ed716c2400c10841d9ac2` before the scope guard.
- The Edit tool decoded the `\u2014` escape into the literal character in `plan_check.py`. A byte scan caught it, and the constant is now `chr(0x2014)`. No file this step touched holds the literal, and `compaction-em-dash flags the character U+2014` still passes.
- Two behaviours in `compaction_handoff.py` go beyond the handoff: `write` also exits 2 on an empty body, and `status` prints `stale: written unknown` when the section has no `Written` line.
- `SKILL.md` line 12 now reads "for every kind but compaction", so it agrees with the new section 0 sentence that the plan rules do not apply to this kind. The handoff did not name that edit.
- Rule readings the handoff left open:
  - `compaction-entry-copy` counts the 4 words on the whole line, verb included.
  - `compaction-decision` skips `none` and POINT lines in DECISIONS.
  - A `none` line in the DROP section is flagged by `compaction-verb`, as the rule text says.
- The handoff section is appended with no blank line before the H2, so `clear` restores the earlier bytes exactly. A file whose last line had no newline gains one.
- Not proven here, as the handoff states: that Claude Code reloads `CLAUDE.local.md` after `/compact`.
- Nothing is committed; all work is in the tree.
