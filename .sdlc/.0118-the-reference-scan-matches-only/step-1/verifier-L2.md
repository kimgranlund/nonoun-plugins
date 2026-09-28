<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Selftest exits 0 and prints `tickets selftest: PASS`: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/tickets.py selftest` and it printed `tickets selftest: PASS`.
- Close refuses a relative reference from another ticket folder and writes nothing: pass. Evidence: I ran the criterion command and it exited 0. The same command against the HEAD `outside_refs` and `rewrite_files` fails, because there the selftest case `a ../ from another ticket folder reference refuses ...` gets rc=0 instead of a refusal.
- Close `--rewrite-refs` rewrites that reference and keeps its form (`see ../.0001-x/filer-L1.md`): pass. Evidence: the criterion command exited 0. The selftest case `--rewrite-refs rewrites a ../ ... in its own form` also passes, and it goes red at the HEAD functions.
- Archive `--dry-run --rewrite-refs` lists the relatively citing file: pass. Evidence: the criterion command exited 0. The selftest case `archive refs: --dry-run --rewrite-refs lists a ../ ...` goes red at the HEAD functions.
- A `./`-relative link from a file in the ticket root is rewritten: pass. Evidence: the criterion command exited 0. The `./ from the ticket root` cases go red at the HEAD functions.
- (guard) Absolute reference refused, then rewritten in absolute form: pass. Evidence: the criterion command exited 0. The absolute selftest cases pass at HEAD too, so this guard holds both before and after. The builder said so, and the selftest cases confirm it.
- (guard) Negative controls do not block and stay untouched: pass. Evidence: the criterion command exited 0.
  - Mutation 1: I dropped the `'/' in tok` requirement in a throwaway copy. The selftest failed on `'see 0003-x and other/0003-x/handoff.md' in .sdlc/index.md is not a reference`.
  - Mutation 2: I made any token whose component matches the slug count. The selftest failed on the `docs/spec.md` negative control, the `.sdlc/index.md` control and the archive control.
  - So the negative controls can go red.
- Red before, green after: pass. Evidence: I made a detached worktree at HEAD (`f1bd56b`) and copied the new `tickets.py` in. I then swapped only the `outside_refs`, `rewrite_files` block back to the HEAD versions. The selftest printed `FAIL, these did not bite:` and listed exactly 12 cases. Those are the `../` and `./` cases (refuse, dry-run and rewrite) for close and for archive. No existing case and no negative control failed there. I removed the worktree and pruned it afterwards.
- Existing `(u) refs` and `archive refs` expectations not edited: pass. Evidence: `git diff HEAD -U0 -- plugins/sdlc-lite/scripts/tickets.py` shows two selftest hunks, `@@ -1649,0 +1706,46 @@` and `@@ -1830,0 +1933,44 @@`. Both are pure additions. All removed lines fall in `outside_refs`, `rewrite_files` and the `cmd_close` docstring.
- Builder claim that `scripts/check.sh` is green: confirmed. I ran `plugins/sdlc-lite/scripts/check.sh` and it ended with `hook selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`. I did not capture its exit code, since the pipe through `tail` hid it.

Steelman of a possible fail reason: the step's Intent said no symlink resolution, but the builder added `os.path.realpath` for absolute tokens. The step's Do and criteria don't forbid it. It only widens absolute-token matching, and the negative controls still pass. I dropped this as a finding.

## Out of scope changes
None. Two paths are dirty besides `tickets.py`:
- `.sdlc/0118-the-reference-scan-matches-only/handoff.md` is the task handoff. I read its diff: it is the Intent, Goal and Constraints text, written before the build, and not the builder's edit.
- `.sdlc/0118-the-reference-scan-matches-only/step-*`, `planner-L2.md` and `runs.jsonl` are untracked pipeline artifacts.

## For the next attempt
None
