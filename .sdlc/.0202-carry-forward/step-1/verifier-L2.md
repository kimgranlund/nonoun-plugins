<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (the four producer contracts end with `## Carry forward` and hold "at most 15 lines"): pass. Evidence: the criterion's loop exited 0. `git diff` shows the section appended last, after one blank line, in scout, researcher, architect and archaeologist, with the exact body text.
- AC2 (planner and builder reader text present, no heading line): pass. Evidence: the criterion exited 0. `git diff` shows the planner paragraph after "Read the code you plan against..." and the builder sentence at the end of the first paragraph, both matching the handoff text verbatim.
- AC3 (`results.py schema --role` ends with `|Carry forward` for the four roles): pass. Evidence: the loop exited 0. At base, `schema --role scout` printed `scout Map - Map|Entry points|Not found`, so this was red before.
- AC4 (selftest prints both new `ok:` lines): pass. Evidence: the criterion exited 0 and the full run ended `results selftest: PASS`. Mutation check: with 'Carry forward' dropped from the scout schema in a copy of results.py, the selftest printed `MISS: schema prints - for a role with no allowed set` and `MISS: a scout result with ## Carry forward before ## Map fails`. (The same run also logged an unrelated `steps.py` missing-file MISS and a traceback, because the copy sat outside the scripts directory.) So the cases can go red.
- AC5 (an out-of-order fixture fails validate with the message): pass. Evidence: the criterion exited 0. On the built tree, validate printed `## Carry forward comes before ## Map` and returned rc 1. On the base tree it returned rc 0 with no message, so it was red before.
- AC6 (guard: the committed producer results validate): pass. Evidence: seven files matched and the loop exited 0, with no validate error output. My first attempt ran under zsh, where `$fs` is not word-split, and failed with a quirk of my own shell. Rerun under `bash -c`, the exact command exited 0.
- AC7 (heading removed from scout.md is flagged by check.py): pass. Evidence: the criterion exited 0 on a plugin copy.
- AC8 (reader phrase removed from builder.md is flagged): pass. Evidence: the criterion exited 0 on a plugin copy.
- AC9 (guard: `check.py`): pass. Evidence: prints `ok: 19 role levels, 9 agents checked`, exit 0. Extra bite check: removing "at most 15 lines" from researcher.md in a copy printed `FAIL agents/researcher.md: carry-forward text missing "at most 15 lines"`. The guard code, `CARRY_FORWARD` with its negative control, matches the handoff pairs and error strings.
- AC10 (regenerated TOMLs hold the new text): pass. Evidence: the criterion exited 0. `codex_roles.py generate --check` printed `Codex agent definitions verified`, exit 0.
- AC11 (guard: changed files stay in the allowed set): pass. Evidence: the criterion exited 0. `git status` shows only the allowed agents, scripts and TOMLs, plus `.sdlc` artifacts.
- AC12 (guard: no em dashes): pass. Evidence: the criterion exited 0.
- Focused checks: `codex-selftest.py` ran 22 tests, OK, exit 0. `git diff --check` was clean.

## Out of scope changes
None. The changed files are the six agent files, `results.py`, `check.py`, and 14 generated TOMLs. The 14 are scout-l1, researcher-l1 to l3, architect-l1, archaeologist-l1, planner-l1 to l3 and builder-l1 to l5, all via the codex_roles generate step. Cleared by the AC11 guard and `git status`.

## For the next attempt
None. One note, not a defect: check.py's existing Lean lane comment says "(docstring item 13)" while the docstring numbers that item 14. The builder left it alone, as the handoff did not ask for a change.
