<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `! grep -q 'both address this limit' docs/validation/messages-idle-host-limit-2026-10-01.md`: pass. Evidence: on the built tree it printed `c1=0`. In a throwaway worktree at `$SDLC_BASE_SHA` (cee4ba3) it printed `base_c1=1`, so the check bites. The path exists, since `cat -n` printed the file's 19 lines, so the `!` is not hiding a missing-path exit 2.
- `grep -q 'does not address this limit' docs/validation/messages-idle-host-limit-2026-10-01.md`: pass. Evidence: `c2=0` on the built tree and `base_c2=1` at base.
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" ...; git ls-files --others ...; } | grep -vxE ... | { ! grep -q .; }`: pass. Evidence: `c3=0` on the built tree. In the base worktree I added an unrelated untracked file `zz.txt` as a fixture and the guard went red (`base_guard_fixture=1`). `git status --short` lists only the target file as modified; the other changed paths are all under `.sdlc/`, which the guard excludes.
- Do: other sentences in the file. Evidence: read the whole file with `cat -n`. Line 11 is about the parent waiting on the messenger in past live runs. Line 15 is a workaround that keeps the parent active. Neither claims that `wait` wakes an idle host, so the builder was right to leave them alone. `grep -c '—'` returned 0, so the file has no em dashes. `git diff --check` was clean. The new text at line 19 matches the handoff's replacement wording exactly.

## Out of scope changes
None. The diff touches only `docs/validation/messages-idle-host-limit-2026-10-01.md` (`git status --short`). The other new files are run artifacts under `.sdlc/0188-tighten-idle-note/step-1/`.

## For the next attempt
None
