<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 The design names every file a build changes, each new check with a negative control, and the ordered build tickets; docs_check.py and check.py pass; no dashes: pass. Evidence:
  - Files per build: section 17.9 (`git diff docs/specs/sdlc-lite/lane-lifecycle.md`) gives a "Files changed" cell for A, A2, B, E, F and G. B, C, D, H and I point back to section 13, and that table (read at lines in `## 13`) names each file: `scripts/tickets.py`, `scripts/dispatch.py`, `hooks/block-stray-worktree.sh`, `scripts/hook-selftest.sh`, `docs/references/claude-hooks.md`, `scripts/board.py`, `scripts/fleet_collect.py`, `scripts/fleet_detect.py`, `skills/fanout/SKILL.md`, `scripts/check.sh` and the rest. I matched every caller in the 17.6 table to a ticket that changes its file: fanout.py run, prep, land and step 5 go to B (fanout.py and skills/fanout); tickets.py close and dispatch.py prune go to C; the board goes to E; `plugins/sdlc-lite/AGENTS.md` and the C14 grep in check.sh go to G. I found no caller without a ticket.
  - Checks with negative controls: 17.7 lists C1 and C4 (amended) and the new C9 to C14. Each has a "Negative control" cell with a mutant that must fail, and 17.9 assigns each check to a ticket (A: C9, C10, C13; A2: C11, C12; G: C14).
  - Ordered tickets with sizes: 17.9 says "Order: A, A2; D at any time; then B, C, E, F, G; H and I after A", and each row has a size from L1 to L3.
  - Intent items 1 to 8 map to 17.1 to 17.7 and 17.9. The Context item (gh pr merge needs `--squash`/`--merge`/`--rebase`, PR 425, opt-in per PR) is recorded in 17.8 and in the amended sections 9, 11 and 12.
  - `python3 plugins/sdlc-lite/scripts/docs_check.py` gives rc=0 and "0 errors, 25 warnings". At base `$SDLC_BASE_SHA`, run in a throwaway worktree, it reports 24 warnings. The one new warning is a soft limit, not an error: `warning D-11 docs/specs/sdlc-lite/lane-lifecycle.md: document has 451 lines, over the 400-line soft limit`.
  - Proof the docs check can fail: in the base worktree I planted a doc folder outside the allowed homes, and the result was `error D-1 docs/zzz-nohome/` with rc=1.
  - `python3 plugins/sdlc-lite/scripts/check.py` gives rc=0 and "ok: 19 role levels, 9 agents, 22 generated definitions checked".
  - No dashes: a Python count of U+2013 and U+2014 is 0 in each of the three changed files. `grep -nP '[\x{2013}\x{2014}]'` over them gives rc=1, and the same grep on a planted em dash matched (rc=0), so the check works. `git diff --check` gives rc=0.
  - I checked the prose's [T] claims in a throwaway repo with git 2.54.0, and all of them hold:
    - With `lane/x` present, `git branch lane` fails with "'refs/heads/lane/x' exists".
    - The branch description is gone after the branch is deleted (`config --get` rc=1).
    - `git config --worktree lane.port` exits 0 with the extension off and writes the shared config, which then reads 7401.
    - `git branch foo refs/archive/<date>/foo` with an annotated tag behind it peels to a commit.
    - `<branch>.<sha7>` passes `check-ref-format`.

## Out of scope changes
None. `docs/README.md` and `docs/specs/sdlc-lite/README.md` each change one index line to mention section 17. I read the diff: both are index entries for the changed spec, which docs_check's index conventions expect. The untracked `.sdlc/0424-*` files are run records. The solo run reports `stray_worktrees: []` and `stray_branches: []` in runs.jsonl, and `git status` shows no worktree or branch removed.

## For the next attempt
None. One optional point: the spec is now 451 lines and adds a new D-11 soft-limit warning. It is a warning, not an error, and no criterion covers it.
