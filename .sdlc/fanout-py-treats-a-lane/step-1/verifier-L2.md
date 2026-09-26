<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -qE "^import steps\b" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: I ran it and it printed `C1 ok`. The diff shows `+import steps` next to `import tickets`.
- Inherited-red unit check (`step-1/builder-L2.md` has Status `inherited red: test_a`, expect `inherited red: step-1: test_a`): pass. Evidence: I ran the criterion's `python3 -c` command and it printed `C2 ok`.
- Done builder in `step-1` plus an inherited `step-2.superseded-1` returns `None`: pass. Evidence: I ran the criterion's `python3 -c` command and it printed `C3 ok`. `inherited_red` matches `STEP_DIR_RE.fullmatch`, so the `.superseded` dir is ignored.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: it printed `fanout selftest: PASS`. The `rc=` in that run's output came out empty because `PIPESTATUS` is not set in zsh, so the PASS line is the evidence. The `check.sh` run below also runs this selftest and passed.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it and got `rc=0`. The tail shows `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- Observable: the fanout selftest contains the inherited-red case with all the required assertions and a done-builder negative control: pass. Evidence: the diff adds case 5 in `fanout.py`. It asserts:
  - exit code 1;
  - the outcome is exactly `inherited red: step-1: test_a`;
  - T-0002 is `skipped`;
  - `rev-list --merges --count` is `0`;
  - the work file is absent from the integration branch;
  - the handoff still shows `status: ready`;
  - the lane worktree still holds `?? .sdlc/a/step-1/builder-L2.md`.

  The negative control uses Status `done` and asserts exit 0, outcome `merged`, and `status: done`. I also observed the case run and pass, as part of the selftest PASS above.
- Observable, the case bites: pass. Evidence: I copied `plugins/sdlc-lite/scripts` to a `mktemp -d` dir and inserted `return None` at the top of the copy's `inherited_red`. Its selftest printed `FAIL` and listed 7 misses, all from the inherited-red case. The first two were `run exits 1, got 0` and `T-0001 outcome ... got 'merged'`. I removed the temp dir afterward. The real tree is unchanged.
- `git diff --name-only HEAD -- plugins/sdlc-lite/scripts` lists only `fanout.py`: pass. Evidence: I ran it and it printed only `plugins/sdlc-lite/scripts/fanout.py`.

Other checks, read from the diff:
- The `run_ticket` call sits after the `driver failed` return and before `git add -A`, and returns `(inherited, '')`.
- The docstring has a new per-ticket step 3, the later steps are renumbered to 4 and 5, and the selftest paragraph names case 5.
- `read[0]` and `steps.section(..., 'Status')` are used as specified. The tests are stripped of the `inherited red:` prefix case-insensitively.

## Out of scope changes
None in the plugin. `.sdlc/fanout-py-treats-a-lane/handoff.md` is modified, and `planner-L2.md`, `runs.jsonl` and `step-*/` are untracked. These are task and pipeline artifacts, not code. I checked the handoff diff: it holds only the Goal, Intent and Constraints text, which matches the planner's brief. `git status --short` shows no other tracked changes.

## For the next attempt
None
