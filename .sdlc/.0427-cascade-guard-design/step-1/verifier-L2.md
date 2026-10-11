<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) `test -f docs/specs/sdlc-lite/cascade-guard.md`: pass. Evidence: exit 0 on the built tree. `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/c/.sdlc/0427-cascade-guard-design/step-1/red-checkpoint.jsonl` records a pre-edit control for this exact span with `exit:1`, `result:red`, base 4e77062d. There is no `process-deviations.md`.
- #2 Headings and Status line: pass. Evidence: the python check printed `[] True` and exited 0. All 8 H2 names match, and a `Status:` line contains T-0427.
- #3 No en or em dashes: pass. Evidence: the check printed `[]`, exit 0, over the 3 changed files.
- #4 Index entries: pass. Evidence: the grep pair exited 0. README.md has the Cascade guard bullet after the Lane lifecycle bullet. AGENTS.md has `- [cascade-guard.md](cascade-guard.md)` between `bounded-plan-correction.md` and `cost-control.md`.
- #5 (guard) managed-block hash: pass. Evidence: the check printed `True`, exit 0. The marker reads `sha256:b1bbe59b7bf5`, the value the handoff predicted. It bites because a mismatch would print False and exit 1, and the check recomputes the digest from the block text.
- #6 (guard) docs_check emits no D-10 or B-3a warning on cascade-guard.md: pass. Evidence: `docs_check.py` exited 0. Its output holds no `cascade-guard` line, and the summary is `0 errors, 25 warnings (B-2a 10, B-3a 7, D-10 3, D-11 5)`. The guard can go red: the same `^warning B-3a <path>:` line format appears for other files (e.g. `docs/references/sdlc-internals.md`).
- #7 Cascade counter section: pass. Evidence: N is the single integer 6, with the section 3 "Why 6" table. I reran the collector for both repos:
  - Maison: 339 tickets, median 2, p90 11, T-0378 10 runs. The total is now 1896 against the doc's 1895 because one more run landed; the doc's own note says plan time was 1894.
  - agent-ui: 218 runs, 40 folders, median 3, p90 10, matching the doc.
  - My per-step tally from `runs.jsonl` matches the doc: T-0378 steps 1 and 2 are 7 each (4 task rows plus 3 each), T-0362 step 1 is 8 (5+3) and step 2 is 7 (5+2), and T-0379 steps 1 and 2 are 6 each (4+2).
  - The doc quotes the spot in `prepare`, directly after the budget gate and before `lock = None`. I checked `dispatch.py` 622 and 720 to 726 against the quoted block and they match.
  - The two-line stop-and-ask message is verbatim, and exit 6 is stated as free.
  - The override flag is `--cascade-override`, recorded in `skips.md` and on `runs.jsonl`.
  - The doc states which tally N rests on (per-step) and why the 10 and 11 gap is not an error. Observed by reading the doc.
- #8 Template-instance plan review section: pass. Evidence: I ran the doc's proof logic (printing trimmed) on the real maison files.
  - T-0362 `planner-L3-4.md` against T-0378 `planner-L3-2.md` printed `44 lines differ by sha, count or id only; 22 other lines`, exit 1. This is exactly what the doc reports.
  - Against `planner-L3-3.md` it printed `41 ... 40 other lines`, exit 1, also as the doc reports.
  - The self-diff printed `0 ... 0`, exit 0, which matches the doc's control. A negative probe also went red: `sed s/six/seven/` printed `11 other lines`, exit 1.
  - The doc states one reviewer on the diff only, outside the replan cap. It has a "What forces the normal route" list and the skip rule that a pass is not re-verified unless a verified file changed since.
- #9 Verifier, Build tickets, Files and Rejected sections: pass. Evidence by reading the doc:
  - Section 5 describes what `block-role-spawn.sh` enforces and cites `hooks.json` line 19. I confirmed line 19 is the `block-role-spawn.sh` command entry. I confirmed `hook-selftest.sh` from line 25 holds the matching case descriptions.
  - Section 5 also covers Codex, the T-0339 gap, and the rule that closes it.
  - Section 9 lists 4 tickets sized L3, L3, L3 and L2, each with its own negative control.
  - Section 8 lists repo-relative paths.
  - Section 10 gives a reason for every rejected alternative.
  - Section 6 states that T-0428 and T-0429 are kept out and cites their folders. The line numbers `steps.py` 2586 and 2684 and `dispatch.py` 622 and 1215 are accurate.
- #10 Scope: pass. Evidence: the `test -z` command exited 0. The only non-`.sdlc` changes are `cascade-guard.md`, `README.md` and `AGENTS.md` under `docs/specs/sdlc-lite/`.
- #11 (guard) `docs_check: 0 errors`: pass. Evidence: the output reads `docs_check: 0 errors, 25 warnings`.
- #12 (guard) `check.py`: pass. Evidence: exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.

## Out of scope changes
None. `git status` shows only the three allowed `docs/specs/sdlc-lite/` files, plus `.sdlc/` task records and artifacts, which the criterion excludes. I ran the `fleet_collect.py` calls without `--gh` and wrote nothing to the repo. My scratch files are in `/tmp` and are removed.

## For the next attempt
None
