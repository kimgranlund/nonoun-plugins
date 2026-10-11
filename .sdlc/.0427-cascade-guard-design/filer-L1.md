<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0427: Design a cascade guard: per-step agent-run cap and one-reviewer template-instance plan review

## PR body
Summary

T-0427 is design only: nothing is built. It adds the design for stopping a "verify the verifier" cascade, as found in the maison T-0378 and T-0379 runs. The new doc is `docs/specs/sdlc-lite/cascade-guard.md`, with a `Status:` line naming T-0427 (not built, awaiting approval).

The doc decides:
- **Cascade counter.** The count is agent runs per ticket step: the task's runs plus that step's runs. The cap is N = 6. It is checked in `prepare`, right after the budget gate in `dispatch.py`. It prints a two-line stop-and-ask message and exits 6. The override is `--cascade-override`, recorded in `skips.md` and on `runs.jsonl`.
- **Evidence for N.** Maison has 339 tickets (median 2 runs, p90 11). agent-ui has 218 runs over 40 folders (median 3, p90 10). The maison per-step tallies are:
  - T-0378: 7 runs on each of steps 1 and 2, so it trips the cap.
  - T-0362: 8 on step 1 and 7 on step 2, so it trips the cap.
  - T-0379: 6 on each step, so it passes.
- **Template-instance plan review.** A plan counts as a mechanical copy of a passed plan only if a command shows the diff touches shas, counts and ids alone. One reviewer reads the diff only, and this review does not count against the replan cap of one. The doc lists what forces the normal route. A pass is not re-verified unless a verified file changed since.
- **Verifier never spawns a verifier.** The doc records what `block-role-spawn.sh` already enforces, the Codex case, the T-0339 gap, and the rule that closes it.
- **Relation to T-0421 and the replan cap.** The doc states how the guard sits beside bounded plan correction and the cap of one. T-0428 (doctrine wording) and T-0429 (docs-only skip) are kept out.
- **Measures.** The K-004-style measures come from the collector (`runs.by_ticket`).
- **Build split.** Four tickets: L3, L3, L3 and L2, each with a negative control. The doc also gives the files a build changes and a reason for each rejected alternative.

Changes
- New: `docs/specs/sdlc-lite/cascade-guard.md`.
- `docs/specs/sdlc-lite/README.md`: one `Cascade guard` bullet after the `Lane lifecycle` bullet.
- `docs/specs/sdlc-lite/AGENTS.md`: one managed-block entry between `bounded-plan-correction.md` and `cost-control.md`. The managed-block hash is now `sha256:b1bbe59b7bf5`.
- Tooling quirk: `cascade-guard.md` is marked intent-to-add (`git add -N`) in the index. `check.py`'s broken-link check counts only files git tracks, so the new index links read as broken until the file is tracked. Undo with `git reset -q -- docs/specs/sdlc-lite/cascade-guard.md`; the lane merge commits the file either way.

Verification (verifier L2, verdict pass, all 12 criteria)
- The red control `test -f docs/specs/sdlc-lite/cascade-guard.md` was recorded red (exit 1) before the edit, and is green after.
- The 8 required H2 headings and the `Status:` line are present. A dash check over the 3 changed files found no en or em dashes. Both index entries are present, and the managed-block hash recomputes to the expected value.
- `docs_check.py` reports 0 errors and 25 warnings, none in `cascade-guard.md`. `check.py` exits 0 (19 role levels, 9 agents, 22 generated definitions).
- The verifier reran the collector on both repos:
  - agent-ui matched the doc.
  - Maison now shows 1896 runs against the doc's 1895, because one more run landed after the doc was written.
- The verifier ran the doc's mechanical-copy proof on the real maison plan files. It matched the doc's reported numbers: 44 lines differ by sha, count or id only, 22 other lines, exit 1. A self-diff gave 0/0 and exit 0. An edited copy went red.
- Scope check: the only changes outside `.sdlc/` are the three `docs/specs/sdlc-lite/` files.

Limits
- The doc's own proof refuses the T-0378 plan as a template instance. Against T-0362's passed plan it found 22 other differing lines, and the first review's defect (an expected count of 10 merge commits where a correct build makes 11) sits in those lines. Read section 4 before approving.
- The 10 versus 11 run counts (collector `by_ticket` versus maison's own count) are cited and left unreconciled, as the handoff asked.
- Throwaway-worktree tests were not run. The stray-worktree hook blocked creating one because `SDLC_TMP_WORKTREES` was unset.

## Changelog entry
- Added the cascade guard design (T-0427), `docs/specs/sdlc-lite/cascade-guard.md`. It proposes a per-step agent-run cap of 6 that stops and asks, a one-reviewer template-instance plan review proven by a diff command, and a rule that a verifier never spawns a verifier. Design only; not built.

## Follow-ups
- decide: Approve or change cascade-guard.md as written. Section 4's proof refuses the T-0378 plan, so the template-instance lane would not have saved those runs, and the four build tickets (L3, L3, L3, L2) wait on that call.
- decide: Section 11 of cascade-guard.md leaves two questions open: which roles count toward the cap of 6, and whether a verifier's own test run that changes the tree counts as "a verified file changed since".
- fix-now: `conductor.md` line 9 still says the cap is "6 until T-0427 sets it". Once the design is approved, T-0428 updates it to point at the design.
- note: `check.py` counts only git-tracked files in its broken-link check, so a new doc linked from an index needs `git add -N` first. The handoff expected this only for `onboard.py check`.
- note: The first step handoff was refused by the `steps.py lint` check because it cited relative `.sdlc/tickets/...` paths that resolve against this repo. The replan cites every maison file by absolute path under `/Users/kimgranlund/Projects/maison/ui-kit-maison`.
