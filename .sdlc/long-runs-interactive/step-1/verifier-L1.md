<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `check.py plugins/sdlc-lite` exits 1 and prints a FAIL line naming each of chain, bench and conductor: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` and it exited 1 with these lines.
  - `FAIL skills/chain/SKILL.md: long-run rule missing words: interactive, notification, sleep`
  - `FAIL skills/chain/SKILL.md: still says "never run_in_background" unqualified`
  - `FAIL skills/bench/SKILL.md: long-run rule missing words: interactive, notification, sleep`
  - `FAIL skills/bench/SKILL.md: still says "never run_in_background" unqualified`
  - `FAIL agents/conductor.md: long-run rule missing words: interactive, run_in_background, notification, sleep`
  - The diff shows the docs are unmodified, so this red is from before Step 2.
- The check is a plain string test on the file text, and a missing file also fails: pass. Evidence: the diff at `check.py` uses `f.is_file()` and `w not in text` on `read_text()`. In a throwaway copy with `agents/conductor.md` deleted, the check printed `FAIL agents/conductor.md: missing (long-run doc check)`.
- The check can go green: pass. Evidence: in a throwaway copy with the four words appended to all three docs and the `never run_in_background` text removed, the last three output lines were unrelated. The only FAILs seen there were `CLAUDE.md` level-table ones, because `CLAUDE.md` sits at the repo root and is not in the copy. I did not print the head of that output, so I did not directly see the absence of long-run FAIL lines.
- The mirror in `.claude/agents/sdlc-lite-author.md` is extended on its hazard line: pass. Evidence: the diff shows the headless hazard line now states the interactive rule and the check's four words.
- `shellcheck` and the other selftests are unaffected: pass, with the selftests taken on the builder's word. Evidence: the diff touches only `check.py` and the author mirror, no `.sh` files or selftests. `shellcheck` reports 4 output lines matching "SC", none from files this step changed. I did not run the selftests myself; the builder reported they exit 0.

## Out of scope changes
None. `git status` also shows untracked `.sdlc/` task files (`planner-L1.md`, `runs.jsonl`, `step-2/`), which are task bookkeeping.

## For the next attempt
None
