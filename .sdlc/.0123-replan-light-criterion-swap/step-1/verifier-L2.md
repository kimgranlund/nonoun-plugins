<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- 1 (swap applies, sibling `(guard)` line stays): pass. Evidence: ran the handoff command verbatim from the repo root, exit 0. On a HEAD worktree it fails, because `swap` does not exist there.
- 2 (`next` prints `swap L2`): pass. Evidence: verbatim run, exit 0. At HEAD it fails.
- 3 (a replacement that is red now refuses, writes nothing, ends with `plan defect:`): pass. Evidence: verbatim run, exit 0. At HEAD it fails on the `plan defect:` tail check. A temp copy of `steps.py` with the red-span refusal disabled fails the selftest case `swap: (c) new span red now`, so the check can go red.
- 4 (a replacement that drops `(guard)` refuses): pass. Evidence: verbatim run, exit 0. At HEAD it fails.
- 5 (guard: a second swap on the step replans): pass. Evidence: verbatim run, exit 0. It is also green at HEAD, which is expected for a guard. The handoff says so.
- 6 (`selftest | grep -q "^ok: swap: "`): pass. Evidence: verbatim run, exit 0. `selftest | grep -c "^ok: swap: "` prints 18. At HEAD it fails.
- 7 (`selftest | grep -q "^ok: next swap: "`): pass. Evidence: verbatim run, exit 0. `grep -c` prints 5. At HEAD it fails.
- 8 (guard: full `steps.py selftest`): pass. Evidence: exit 0 on the built tree, and it is also green at HEAD as a guard should be.
- 9 (`grep -q "steps.py swap" scripts/steps.py`): pass. Evidence: exit 0. At HEAD it fails.
- 10 (`grep -q "swap old:" agents/verifier.md`): pass. Evidence: exit 0. The new paragraph is in the diff. At HEAD it fails.
- 11 (`grep -q "swap new:" agents/verifier.md`): pass. Evidence: exit 0. At HEAD it fails.
- 12 (`grep -q "swap old:" scripts/check.py`): pass. Evidence: exit 0. The `PLAN_DEFECT_DOCS` entries are in the diff. At HEAD it fails.
- 13 (`check.py` negative control): pass. Evidence: verbatim run, exit 0, and `check.py` prints `agents/verifier.md: plan-defect route missing "swap old:"` on the mutated copy. At HEAD it fails.
- 14 (guard: `check.py plugins/sdlc-lite`): pass. Evidence: exit 0 on the built tree, and also green at HEAD.
- Do items 2 to 6 (`next_action` routing, docstring, selftest cases (a) to (d), verifier rule, `check.py` docstring): pass. Evidence: I read the `steps.py` diff at `next_action`, `swap_pair`, `earlier_swap` and `swap()`. The diff also holds the docstring paragraphs, and the selftest cases cover every listed refusal and the `next` routes (a) to (d). The extra case "swap-routed fail is not counted, then a fail at L2 gives rebuild L2" is present too.
- Builder claim "check.sh rc=0": partly reproduced.
  - What I saw: `check.sh` on the built tree gave rc=1 twice, then rc=0, rc=0, rc=1 on later runs. Every failure was `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0`.
  - Why I don't hold it against the step: the step changes no hook and no `hook-selftest.sh` (`git diff` is empty for both). `hook-selftest.sh` alone passed 20 of 20 on the built tree and 20 of 20 on a HEAD worktree. Exit 141 is SIGPIPE, which points to a timing race, not a regression. The step's acceptance criteria do not include `check.sh`.
  - Every other `check.sh` stage passed (all selftests, shellcheck, plugin validate). A HEAD worktree ran `check.sh` 4 times, all rc=0, so the intermittent hook flake is worth a look separately.

## Out of scope changes
None. Tracked changes are `plugins/sdlc-lite/scripts/steps.py`, `plugins/sdlc-lite/agents/verifier.md` and `plugins/sdlc-lite/scripts/check.py`, and the step calls for all three. The untracked `.sdlc/0123-replan-light-criterion-swap/*` files are task artifacts. `git status --short` shows no other tracked changes.

## For the next attempt
None
