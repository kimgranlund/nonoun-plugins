## Task goal
When a fanout lane's task stops on an `inherited red` builder, `fanout.py` reports that cause and the inherited tests, and does not merge or close the half-done ticket, so the operator sees "main was already red" instead of a misleading merge or close refusal.

## Step 1: Detect inherited red in fanout.py, with a selftest case and a negative control
level: L3
### Do
Edit only `plugins/sdlc-lite/scripts/fanout.py`.

1. Add a separate line `import steps` next to `import tickets`. It sits in the same scripts/ dir, and importing it has no side effects.
2. Add a module-level function `inherited_red(ticket_dir)`. It takes the ticket folder path in the lane worktree and returns either an outcome string or `None`:
   - Look only at child dirs whose name fully matches `step-(\d+)`. Never look at `step-<n>.superseded-<k>`. Take them in numeric order.
   - For each dir, call `steps.next_action(dir)`. A `steps.Fail` or any exception means "not inherited" for that dir.
   - At the first dir whose action is `inherited`, find the tests. Take the newest builder result, which is `read[0]` of the returned tuple (the file `order.newest` picked). Take the first non-blank line under its `## Status` (use `steps.section`). The tests are the text after the `inherited red:` prefix (match the prefix in any case), stripped.
   - Return `f'inherited red: step-<n>: <tests>'`.
   - If no dir matches, return `None`.
3. In `run_ticket`, call `inherited_red(wt / rel / t.slug)` right after the `driver failed` check (driver rc 0) and before `git add -A`. When it returns a string, return `(that string, '')`. This skips the lane commit, the merge, the gates, and the close, and leaves the lane worktree as it is. `run_lane` then stops the lane and marks later tickets `skipped`, and `cmd_run` exits 1. No other outcome and no part of the merge, gate, or close flow changes.
4. Update the module docstring:
   - In the per-ticket list, add a step between the driver and the lane commit. It covers the inherited-red check: step dirs, `steps.next_action`, the outcome text, nothing committed, merged, or closed, and the tree left for inspection.
   - In the `selftest` paragraph, name the new case.
5. Add a selftest case 5 on its own throwaway repo. Use `make_repo` and a `.gitignore` with `.worktrees/`, or `--lanes-dir` in tmp.
   - Two tickets in one lane, `a=T-0001,T-0002`, plus a gate.
   - The stub driver, for T-0001, writes `$FANOUT_ROOT/$FANOUT_SLUG/step-1/builder-L2.md` with `## Status\ninherited red: test_a\n`, a filer file, and a work file.
   - Assert all of these:
     - The run exits 1.
     - The report.md Outcome cell for T-0001 is exactly `inherited red: step-1: test_a`.
     - The integration branch has no merge commits and does not hold the work file.
     - T-0001's handoff on the integration branch still says `status: ready`.
     - T-0002 is `skipped`.
     - The lane worktree still holds the uncommitted step-1 file.
   - Negative control, in the same or another repo: a stub whose step-1 builder Status is `done` merges and closes normally (outcome `merged`).
### Acceptance criteria
- `grep -qE "^import steps\b" plugins/sdlc-lite/scripts/fanout.py`
- `python3 -c "import sys,tempfile,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import fanout; d=pathlib.Path(tempfile.mkdtemp()); s=d/'step-1'; s.mkdir(); (s/'builder-L2.md').write_text('## Status\ninherited red: test_a\n'); r=fanout.inherited_red(d); assert r=='inherited red: step-1: test_a', r"`
- `python3 -c "import sys,tempfile,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import fanout; d=pathlib.Path(tempfile.mkdtemp()); s=d/'step-1'; s.mkdir(); (s/'builder-L2.md').write_text('## Status\ndone\n'); t=d/'step-2.superseded-1'; t.mkdir(); (t/'builder-L2.md').write_text('## Status\ninherited red: test_b\n'); r=fanout.inherited_red(d); assert r is None, r"`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- Observable: fanout.py's selftest contains the inherited-red case. It asserts the exact outcome `inherited red: step-1: test_a`, no merge on the integration branch, the ticket still `ready`, the next ticket `skipped`, and the uncommitted step file kept in the lane. It also contains a done-builder negative control that asserts `merged`.
- Observable, the case bites: copy `plugins/sdlc-lite/scripts/` to a temp dir and edit the copy's `inherited_red` to `return None`. Running `python3 <tmp>/fanout.py selftest` there must exit 1 and list at least one miss from the inherited-red case. The real tree is untouched.
- `git diff --name-only HEAD -- plugins/sdlc-lite/scripts` lists only `plugins/sdlc-lite/scripts/fanout.py`.
