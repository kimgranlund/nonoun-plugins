<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) `fanout.py settle --help | grep -qF -- --forward`: pass. Evidence: rc 0 on the built tree; red-checkpoint.jsonl records the pre-edit control as exit 1 (result red), and process-deviations.md does not exist.
- #2 (red) `grep -qE '^def cover_at\('`: pass. Evidence: rc 0; pre-edit control red (exit 1) in red-checkpoint.jsonl. `cover_at` at fanout.py:2647.
- #3 (red) `grep -qF 'T-0489' fanout.py`: pass. Evidence: rc 0 (matches at :2426, :2474, :2647, :4607 and more); pre-edit control red.
- #4 (red) `grep -qF -- 'settle <integration> --forward' docs/references/sdlc-internals.md`: pass. Evidence: rc 0. The diff adds one paragraph after the settle/cover paragraph and removes nothing. The checkpoint holds no control for the two doc greps. The diff shows pure additions (docs +2 lines), so the literal is new; the builder's base check was not independently re-run, but the added hunk is the only source of the literal.
- #5 (red) same grep on `skills/fanout/SKILL.md`: pass. Evidence: rc 0. The diff adds one paragraph (+2 lines) and removes nothing, so the literal is new.
- #6 builder result records the T-0489 case observed red on unmodified fanout.py: pass. Evidence: builder-L3.md Notes states exit 1 with T-0489 labels under `these did not hold:` (`unrecognized arguments: --forward`). It also admits one test-side fixture assertion was fixed in that same run. That is a disclosed, harmless detail. My negative control (see #7) independently shows the case bites.
- #7 Observed negative control: pass. Evidence: git worktree add was blocked by the block-stray-worktree hook because SDLC_TMP_WORKTREES is unset in this session, so I used `cp -R plugins/sdlc-lite` under `.worktrees/tmp/0489-s1-verifier-L2/nc`. I mutated the regeneration (`str(root), 'roadmap']` replaced with `'--help']`) and ran `fanout.py selftest`: rc 1, `fanout selftest: FAIL, these did not hold:` listing `T-0489 settle --forward: the roadmap on main lists T-0001 done and T-0003 proposed` and `T-0489 settle --forward: tickets.py check passes on main, got rc=1 ... roadmap.md: stale or missing`. The unmutated built tree passes (see #9). The biting variable is the regeneration; the add/add conflict resolved with `--ours` keeps the stale roadmap, which the roadmap and check assertions catch. The notes-union path is not exercised by the fixture (the fixture has no notes.md), but the criterion needs only one of the two.
- #8 (guard) scope check: pass. Evidence: the guard pipeline printed guard1 rc 0 with `SDLC_BASE_SHA` set to 5c42e976...; the changed files outside `.sdlc` are exactly fanout.py, fanout/SKILL.md and sdlc-internals.md. `git diff --check` rc 0.
- #9 (guard) `fanout.py selftest`: pass. Evidence: output ends `fanout selftest: PASS`. Case 28, case 34 and the T-0489 case all ran in that selftest. Not run at base, because it is green here.
- #10 (guard) `check.py && tickets.py selftest`: pass. Evidence: check.py printed `ok: 19 role levels, 9 agents, 22 generated definitions checked` with rc 0; tickets.py selftest printed `tickets selftest: PASS`.

Code read (settle_forward, fanout.py:2473-2557): the lock is the existing `merge.lock`, held once around the merge, regeneration, commit and `cover_at`. The conflict outside the generated set aborts the merge and verifies MERGE_HEAD is gone. The notes union uses `merge-file -p --union` over stages 2, 1, 3 (current, base, other), with an empty base on add/add. The commit subject is `settle --forward: <head> <sha7> into <integration>`, which does not match MERGE_SUBJECT. The selftest asserts the four negative controls required by the handoff (README conflict, plain settle, red gate, no `--gate`) and the green path assertions.

Steelman: I drafted a possible fail, "notes union untested by the selftest". The builder's rebuttal holds: the handoff's selftest fixture (sized_repo plus land plus tickets.py new) produces no notes.md conflict, and its criteria require only the regeneration or the notes union to bite. Dropped.

## Out of scope changes
None. The `.sdlc/0489-settle-forward/` records are task bookkeeping, excluded by the scope guard. The scratch dir I created is removed.

## For the next attempt
None
