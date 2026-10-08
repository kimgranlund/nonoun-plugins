<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `steps.py selftest 2>&1 | tail -1 | grep -q 'steps selftest: PASS'`: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/steps.py selftest` on the built tree. It exited with rc=0 and its last line was `steps selftest: PASS` (64s). This is a gate. It covers the existing widen, split (T-0377 `--tree`) and lint cases, and all of them still pass.
- `steps.py selftest 2>&1 | grep -c 'ok: widen: (T-0382)' | grep -qx 7`: pass. Evidence: the count on the built tree is `7`. The seven are the no-lane stale-root case staying red, `--tree` to the lane accepting the prerequisite, the lane cwd as default with the stderr note, the unrelated-file negative control, `--tree` of another repo refusing, a non-directory `--tree` refusing, and the single-checkout case unchanged. The check bites: `grep -c 'T-0382'` on the base `steps.py` at `$SDLC_BASE_SHA` (fa5f37fc) returns `0`, so this criterion is red there.
- `check.py >/dev/null && tickets.py --root .sdlc check >/dev/null`: pass. Evidence: check=0 and tickets=0 on the built tree. This is a gate, and since it is green no base run was needed.
- `codex_roles.py generate --check && claude_roles.py generate --check`: pass. Evidence: codex=0 and claude=0 on the built tree. This is a gate.
- `steps.py widen --help | grep -q -- '--tree'`: pass. Evidence: help=0 on the built tree. At the base worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"`) the same command returned base_help=1, so it bites.
- Done-when, the maison T-0292 disposable repro (handoff in primary A, prerequisite committed in lane B, base-sha = B HEAD, widen run from the lane), red before the change: pass. No process-deviations.md exists. Evidence: I ran the same throwaway repro twice, once with each version of `steps.py` (/tmp/v0382/finish.sh). The lane edits `a.txt` (in scope) and adds `b.txt`.
  - Base `steps.py`: `widened scope span is red now (exit 1)` and `plan defect: steps widen refused: red now: ...`, rc=1, `-e b.txt` count 0.
  - Built `steps.py`: `evaluating the scope span in the work tree .../laneNew` and `added b.txt to the scope criterion`, rc=0, count 1.
- Done-when, widen without `--tree` in the ordinary single-checkout case behaves as before: pass. Evidence: selftest line `ok: widen: (T-0382) the ordinary single-checkout case is unchanged: no tree note, widened`. Every earlier widen selftest case still passes in the PASS run. `lane_tree` falls back to `git_toplevel(folder)` when the cwd is the same tree or no git tree (steps.py:655-672).
- Do, applying the same to `steps.py lint`: pass. Evidence: a plan in stale primary A whose `### Read first` lists `prerequisite.txt`, which exists only in the lane.
  - Base lint run from the lane: `### Read first lists a path that does not exist`, rc=1.
  - Built lint run from the lane: `steps lint: ok`, rc=0.
  - Built lint run from the primary: still red, rc=1.
  - Built lint run from the primary with `--tree <lane>`: ok, rc=0.

## Out of scope changes
None. I read the three diffs to clear each one:
- `docs/references/sdlc-internals.md` changes one line. It documents `widen --tree`, the lane-cwd default and `lint --tree`, so the reference matches the behavior change as the repo guidance requires.
- `.sdlc/0382-widen-in-lane-tree/handoff.md` only gains `## Acceptance criteria`. `agents/solo.md:48` tells an L2 solo to write that section when the handoff has none.

The untracked `base-sha`, `runs.jsonl` and `verifier-L2.attempt.json` are run records. A dash scan of `git diff` found 0 em or en dashes, and `git diff --check` is clean.

One note, not a failure. The Do said "Reuse T-0377's tree resolution". The build adds a new `lane_tree()` (steps.py:655) instead of reusing `git_toplevel(tree or task_dir)` from steps.py:767. As a result, `split` without `--tree` now resolves its lint Read first paths from the cwd lane, while its guards still use the task dir's toplevel. No criterion covers this, the selftest passes, and the behavior moves in the ticket's intended direction. The Codex host was not run live (unverified, per the ticket's constraints).

## For the next attempt
None
