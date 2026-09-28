<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- Extracted planner block with `<n>`→1 has `## Step 1: Merge ` and passes `steps.py lint`: pass. Evidence: ran the criterion command verbatim, output `steps lint: ok`, `exit=0`. Extracted file holds 5 criterion command spans (lines shown in output). Negative controls: same command in a throwaway worktree at HEAD (`f336568`) exits 1 (no block exists); a copy with one span broken (`-eq 3 ((`) makes lint print the bash syntax error and `plan defect: replan this step (/chain 3)`, exit 1.
- Planner block contains every required substring: pass. Evidence: criterion command verbatim, `exit=0`, nothing printed as missing. Negative control at HEAD: `exit=1` (empty block fails `test -n`).
- handoff-format block non-empty and byte-identical to planner block: pass. Evidence: criterion command verbatim, `diff` printed nothing, `exit=0`. Negative controls: at HEAD `exit=1`; perturbing one byte (`HEAD^1`→`HEAD^2`) in the planner copy makes `diff` exit 1.
- `grep -n 'git merge --no-ff' plugins/sdlc-lite/agents/builder.md` prints at least one line: pass. Evidence: printed lines 10 and 11, `exit=0`. Negative control at HEAD: no output, `exit=1`.
- builder.md shows the three rules: pass. Evidence: `plugins/sdlc-lite/agents/builder.md:10` "Commits happen only on a merge step: a step whose title starts with `Merge ` and whose Do runs `git merge --no-ff <branch>`"; `:11` merge, resolve, create the merge commit, never `git merge --abort` after resolving, no other commit, blocked on uncommitted tracked changes; `:12` "On every other step, never commit."; `:13` "Never push, open a PR, or publish, on any step. The publish hook blocks these regardless."
- (guard) hooks, run.sh, steps.py, verifier.md unchanged: pass. Evidence: `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/agents/verifier.md` → `exit=0`; `git status --short` lists only builder.md, planner.md, handoff-format/SKILL.md and `.sdlc/` files as modified. This guard bites by construction (it is the same predicate that reports the three edited files as changed).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: run twice; tail shows `order selftest: PASS`, `run selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`; `check.sh exit=0`.

Structure checks from Do: `## Merge steps` is at planner.md:21, after `## Criteria that can pass` (:13) and before `Final message` (:40). `### Merge step` is at SKILL.md:113, under `## Step handoff` (:93), before `## Free-text arguments` (:132). Block line lengths `13 27 11 6 196 23 59 46 50 91 149 3`: only the closing fence is 3 characters. HEAD is still `f336568`, so nothing was committed.

## Out of scope changes
`.sdlc/0059-merge-step-template/handoff.md` (Intent section filled in) is modified in the tree, but its mtime (08:25:27) predates the planner run (08:29) and the builder run (08:31), and the builder log never references it, so it came from the session's /clarify, not this step. No other files outside the step's three named files changed.

## For the next attempt
None
