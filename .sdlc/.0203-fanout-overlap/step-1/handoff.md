## Task goal
Add a merge-time file-overlap check to fanout.py.

## Step 1: Merge-time overlap: wait, record, report
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Target: `plugins/sdlc-lite/scripts/fanout.py`, covering its module docstring, `Lane`, `run_lane`, `merge_gate_close`, `report`, `cmd_run` and `selftest`. Depends on: none.

These interface decisions are settled. Evidence: the handoff Intent ("order the locked merges so an overlapping lane merges after the lane it overlaps"; "`git diff --name-only` of each lane against the integration branch") and design.md section Parallelize ("fanout's locked merge already serializes").

- Order rule: lanes rank by their position in the spec list (`ctx['lanes']` index). A lane waits only for an earlier lane, never a later one, so no wait cycle can form.
  - When a later lane reaches its merge, it waits while any earlier lane that has not finished has pending files overlapping its own.
  - It waits outside the merge lock. Taking the lock unchanged keeps the locked merge and the integration-dirty refusal intact.
- `Lane.__init__` gains two fields:
  - `self.files = set()`: every path this lane brought to a merge.
  - `self.done = False`.
- `cmd_run` sets `ctx['cond'] = threading.Condition()` before it starts the threads.
- `run_lane`:
  - wraps its ticket loop in `try/finally`. The `finally` sets `lane.done = True` and calls `notify_all()` under `ctx['cond']`.
  - also calls `notify_all()` under the condition after each ticket's outcome is appended.
- New `lane_pending(ctx, lane)` returns the set of paths an earlier lane may still merge. Every git call passes `--no-optional-locks` as its first argument, so a read never takes `index.lock` while that lane's driver runs git. Any git failure gives an empty set, so a failed read never blocks.
  - Regular lane: in `lane.dir`, run `merge-base <integration> HEAD`, then `diff --name-only <merge-base>` (working tree against the merge base, which covers committed and uncommitted lane edits), plus `ls-files --others --exclude-standard`.
  - External lane: `diff --name-only <integration>...refs/heads/<branch>` from `ctx['cwd']`.
- New `wait_for_overlap(ctx, lane, t, ref)` is called first in `merge_gate_close`, before `with lock:`.
  - It computes its own paths once: `git --no-optional-locks diff --name-only <integration>...<ref>` in `ctx['integ_dir']`.
  - Under `ctx['cond']`, it loops over the earlier lanes that are not `done` and intersects its paths with `lane_pending`. With no overlap it returns.
  - With an overlap it calls `say(ctx, lane, t.id, f'waiting for lane {other.name} (overlap: {", ".join(sorted(files))})')`, but only when that lane/file set differs from the last one it printed. It then calls `cond.wait(2)` and checks again.
- Inside the lock in `merge_gate_close`, after the integration-dirty refusal and before `git merge`, add the output of `git diff --name-only HEAD...<ref>` (run in the integration worktree) to `lane.files`.
- `report()`: after the `- Logs:` line, write one line per lane pair `i<j`, in spec order, whose `files` intersect: ``- Overlap: `<a>` and `<b>`: `<f1>`, `<f2>` `` (paths sorted). With no such pair, write the single line `- Overlap: none`.
- Docstring:
  - step 5 describes the wait and the `waiting for lane` event;
  - the report fields list the `- Overlap:` lines;
  - the selftest section gains a case 13 paragraph.
- Selftest case 13 (overlap):
  - Repo fixture: `make_repo` with `a` T-0001 and `b` T-0002, both `ready`, plus a root `shared.txt`. Its line 1 is `top`, then 20 lines `mid <n>`, then the last line `bottom`, so the two edits are far enough apart to merge cleanly.
  - Driver: one stub script that branches on `$FANOUT_TICKET`. It writes files with temp file + `mv`, never `sed -i` (macOS/GNU differ), and writes `$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md` as `STUB` does.
    - T-0001 (lane alpha) rewrites line 1 to `top alpha`. It then polls `../logs/fanout.log` (at most 600 x 0.1 s, else exit 1) until a line holds `[beta] T-0002 waiting for lane alpha (overlap: shared.txt)`.
    - T-0002 (lane beta) polls until line 1 of `../alpha/shared.txt` is `top alpha` (same bound), then rewrites the last line to `bottom beta`.
  - Run: `alpha=T-0001 beta=T-0002`, with `--integration fanout/ov` and an explicit `--lanes-dir`.
  - Expected results. The selftest source must contain these expect texts verbatim:
    - exit 0, both rows `merged`;
    - an expect labelled `overlap order: alpha merges before beta`, asserting that `git log --first-parent --merges --format=%s fanout/ov`, reversed, is `['Merge fanout/ov-alpha: T-0001', 'Merge fanout/ov-beta: T-0002']`;
    - fanout.log contains `waiting for lane alpha (overlap: shared.txt)`;
    - report.md has the line ``- Overlap: `alpha` and `beta`: `shared.txt` ``;
    - the integration `shared.txt` holds both `top alpha` and `bottom beta`.
  - Negative control (disjoint lanes): a second repo of the same shape, run `alpha=T-0001 beta=T-0002` with the existing `STUB`. It merges both, report.md holds `- Overlap: none`, and fanout.log holds no `waiting for lane`.
  - Before the change, case 13 is red because alpha's stub times out: nothing ever prints the waiting line.

Focused check: `python3 plugins/sdlc-lite/scripts/fanout.py selftest`. The run-id logging, the locked merge and the integration-dirty refusal stay unchanged. Contract dependents:
- `board.py --lanes` reads worktrees, not report.md.
- `skills/fanout/SKILL.md` prints report.md verbatim, so it needs no change and stays out of scope (it is not an owning file).
- `traces.py` reads the fanout logs dir. A new event line `[<run_id>] [<lane>] <id> waiting for lane ...` keeps the existing line shape.
### Acceptance criteria
- `grep -qF 'waiting for lane alpha (overlap: shared.txt)' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qE -- '- Overlap: .alpha. and .beta.: .shared\.txt.' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF -- '- Overlap: none' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'overlap order: alpha merges before beta' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF -- '--no-optional-locks' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py)"`
- The verifier observes the negative control: in a temp copy of `plugins/sdlc-lite` outside the repo, the `wait_for_overlap(...)` call in `merge_gate_close` is replaced by `pass` and that copy's selftest is run. It exits 1 with a miss naming case 13 (the overlap order or alpha's driver timeout). The real tree is never edited.
