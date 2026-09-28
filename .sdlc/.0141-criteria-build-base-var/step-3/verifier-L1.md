<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'git diff --name-only "$SDLC_BASE_SHA"' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: `grep -qF ...` exit 0 in the built tree; ran the same grep in a throwaway worktree at pre-build HEAD (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`) and got exit 1 (no match), so the criterion bites. Worktree removed after.
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: grep exit 0; also read `git diff plugins/sdlc-lite/agents/builder.md` (item 8 now reads `$SDLC_BASE_SHA` and the worktree example uses it), matching the Do.
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: grep exit 0; read `git diff` on verifier.md item 4, which names `$SDLC_BASE_SHA` as the pre-build HEAD with a worktree example.
- `grep -qF 'SDLC_BASE_SHA' CLAUDE.md`: pass. Evidence: grep exit 0; read the diff — the run.sh paragraph, the steps.py paragraph (`split --only`/`swap`), and the plan-defect Decision all now mention `SDLC_BASE_SHA`.
- `grep -qF 'SDLC_BASE_SHA' .claude/agents/sdlc-lite-author.md`: pass. Evidence: grep exit 0; read the diff — the worktree-hazard line now describes `SDLC_BASE_SHA` and `base-sha`.
- Negative-control criterion (`perl` strip + `check.py` flags `agents/planner.md`): pass. Evidence: ran verbatim on the built tree, exit 0 (PASS). Ran the identical command in the pre-build throwaway worktree (where `check.py` has no `SDLC_BASE_SHA` entry and planner.md has no occurrences to strip): output empty, grep exit 1 (FAIL). Confirms the check is real and newly added, not vacuously true.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: `ok: 18 role levels, 8 agents checked`, exit 0, in the built tree. Ran the same command in the pre-build throwaway worktree: also exit 0 with identical output, so this gate was already green before the step and stays green — no regression, correctly a non-blocking gate here.
- No em dashes (Do item, not a separate acceptance line but stated in Do): pass. Evidence: `grep -n '—'` across the six edited files found zero literal em-dash characters (the only "em dash" hits were the word itself inside prose describing the policy, in sdlc-lite-author.md's existing "How you talk" line, unrelated to this step's new text).

## Out of scope changes
`plugins/sdlc-lite/scripts/run.sh`, `plugins/sdlc-lite/scripts/steps.py`, `plugins/sdlc-lite/scripts/run-selftest.sh` are modified in the working tree but not touched by step 3's Do or builder-L2.md's Changes list. Checked: these are step 1 and step 2's own uncommitted work in the same tree (step-1/builder-L3.md and step-2/builder-L2.md both list exactly these files as their Changes, and step-2's builder explicitly notes "the uncommitted changes to run.sh and run-selftest.sh in the tree were there before this step... I did not touch them"). Not out of scope for this step's verification since no commits separate the steps; harmless.

## For the next attempt
None.
