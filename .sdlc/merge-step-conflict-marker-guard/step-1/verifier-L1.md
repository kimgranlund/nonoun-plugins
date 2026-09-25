<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF -- '--diff-filter=d HEAD^1 HEAD | xargs -0 sh -c' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: the working tree gives `c1=0`. The same command in a throwaway worktree at HEAD gives `h1=1`, so the check can go red.
- `grep -qF -- '--diff-filter=d HEAD^1 HEAD | xargs -0 sh -c' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: the working tree gives `c2=0`. The HEAD worktree gives `h2=1`.
- `! grep -qF -- '-- $(git diff --name-only HEAD^1 HEAD)' planner.md SKILL.md`: pass. Evidence: the working tree gives `c3=0`. The HEAD worktree gives `h3=1`, because the old span is still in both files there. Both paths exist, so the negation is not vacuous.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: the working tree gives `c4=0`, with the output ending in `ok: shellcheck` and `ok: plugin validate`.
  - Negative control: I copied only the new planner.md into a HEAD worktree. check.sh printed `FAIL merge-step block differs between agents/planner.md and skills/handoff-format/SKILL.md` and returned `check_one_copy_exit=1`.
  - Copying both files into that worktree turned it green again (`check(both)=0`).
  - The part that can go red is the check that both blocks are identical.
- The span actually runs (task goal, runtime). I extracted it from planner.md and ran it in a temp repo:
  - Empty diff with a legitimate `<<<<<<< ` line in an untouched file: the new span returns `new_empty_exit=0`. The old span on the same repo returns `old_empty_exit=1`, because it scanned the whole tree and matched `old.txt:1`.
  - Marker in a touched file named `a b.txt` (the name has a space): it prints `a b.txt:1:<<<<<<< HEAD` and returns `marker_exit=1`.
  - Clean touched file: `clean_exit=0`.
  - Deleted file: `deleted_exit=0`.

## Out of scope changes
None. `git diff` shows the one replaced line in each of the two template files. The changed `.sdlc/merge-step-conflict-marker-guard/handoff.md` and the untracked `.sdlc` artifacts come from planning and orchestration, not from the builder.

## For the next attempt
None
