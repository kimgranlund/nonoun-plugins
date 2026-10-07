<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a merge-time file-overlap check to `fanout.py`. It reports overlapping files between lanes in `report.md` and makes a lane that overlaps an earlier lane merge after it. A `--dry-run` also reports scope allow-list overlap for tickets that are already planned.

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

## Step 2: Dry-run overlap of planned scope allow-lists
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Target: `plugins/sdlc-lite/scripts/fanout.py`, covering a new `planned_scope`, `print_plan`, the docstring's `--dry-run` paragraph and the selftest. Depends on: step 1 (same file).

`steps.py` is not edited, because it is outside the owning files. The parse is composed from the existing public helpers that `fanout.py` already imports through `import steps`: `steps.criteria_indexed`, `steps.list_item`, `steps.line_spans`, `steps.INVERT_GREP_RE`, `steps.widen_forms` and `steps.widen_listed`. These are the forms `steps.py widen` recognizes (F `grep -vxF -e`, E `grep -vxE "..."`, A `grep -vE "^(...)$"`; `steps.py:1526-1538`), and design.md line 68 settles this choice ("parsed with the forms `widen` already recognizes").

`planned_scope(root, slug)` returns the set of allow-listed paths, or `None` when the ticket is not planned:
- It reads every `root/<slug>/step-<n>/handoff.md` whose dir name fully matches `step-\d+` (a `.superseded-<k>` dir never counts).
- For each line from `criteria_indexed` that is a `list_item`, it takes each `line_spans` span containing `git diff --name-only` that matches `INVERT_GREP_RE`.
- For each `widen_forms` match, it takes the entries from `widen_listed`. E and A entries are ERE-unescaped with `re.sub(r'\\(.)', r'\1', e)`.
- It returns the union, or `None` when no step handoff yields an entry.

`print_plan` adds lines after the lane blocks and before the gate lines:
- One line per pair of tickets in different lanes whose scopes intersect, in spec and ticket order: `overlap (planned scope): <laneA> <idA> and <laneB> <idB>: <paths sorted, joined ", ">`. Tickets in the same lane run in sequence and are not compared.
- With no such pair, the line `overlap (planned scope): none`.
- When any ticket is unplanned, or belongs to an external lane (its folder lives on the branch), one line `overlap (planned scope): not planned, checked at merge time: <ids joined ", ">`.

The dry run still creates nothing.

Selftest case 14:
- Repo fixture:
  - `a` T-0001, whose `step-1/handoff.md` has an `### Acceptance criteria` item with the code span `` `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | grep -vxF -e shared.txt -e a.txt)"` ``;
  - `b` T-0002, whose step-1 span uses the E form `grep -vxE "shared\.txt|b\.txt"`;
  - `c` T-0003 with no step dir;
  - `d` T-0004, whose step-1 span uses `grep -vxF -e b.txt`.
- `--dry-run alpha=T-0001 beta=T-0002,T-0003` prints `overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt` and `overlap (planned scope): not planned, checked at merge time: T-0003`. These literals appear verbatim in the selftest.
- Negative control: `--dry-run alpha=T-0001 beta=T-0004` prints `overlap (planned scope): none` and no pair line.
- Both runs create no branch, worktree or lanes dir.

Existing dry-run asserts use substring checks, so they stay green. Focused check: `python3 plugins/sdlc-lite/scripts/fanout.py selftest`.
### Acceptance criteria
- `grep -qF 'overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'overlap (planned scope): none' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'overlap (planned scope): not planned, checked at merge time: T-0003' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py)"`
- The verifier observes the negative control: in a temp copy of `plugins/sdlc-lite` outside the repo, `planned_scope` is made to return `None` and that copy's selftest is run. It exits 1 with a miss naming case 14. The real tree is never edited.

## Step 3: Internals doc and gates green
level: L2
### Do
Target: the `scripts/fanout.py` entry in `docs/references/sdlc-internals.md`. This is the owning doc per the handoff, and its fanout entry is at line 47. Depends on: steps 1 and 2.

In that entry, add:
- the merge-time overlap behavior: a later lane in spec order waits outside the lock for an earlier, unfinished lane whose pending files overlap its own, with the event `waiting for lane <name> (overlap: <files>)`;
- the report's `- Overlap:` lines (`- Overlap: none` when no lanes overlap);
- the dry run's `overlap (planned scope)` lines, read from the step handoffs' scope allow-lists in the forms `steps.py widen` recognizes;
- the remaining limit: an overlap first visible after a later lane has started its merge is not reordered.

Keep the docstring in `fanout.py` and this entry consistent; do not copy a table. `skills/fanout/SKILL.md` stays unchanged, because it prints report.md verbatim and is outside the owning files.

Then run every gate below. Fix any red that steps 1 and 2 introduced, in `fanout.py` or this doc only. A gate already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- `grep -qF -- '- Overlap:' docs/references/sdlc-internals.md`
- `grep -qF 'overlap (planned scope)' docs/references/sdlc-internals.md`
- `grep -qF 'waiting for lane' docs/references/sdlc-internals.md`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py -e docs/references/sdlc-internals.md)"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`

## Assumptions
- Merge order follows spec order: a lane waits only for earlier lanes, so there is no deadlock. Verified by the handoff Intent ("an overlapping lane merges after the lane it overlaps"), which sets no tie-break, and by threads all starting at once in `cmd_run` (`fanout.py:822-827`). Spec order is the one deterministic order available.
- The wait sits outside the merge lock, so sync and merge for the earlier lane are never blocked. Verified by `run_ticket` taking `lock` for sync (`fanout.py:653`) and `merge_gate_close` taking it for the merge (`fanout.py:704`).
- Read-only git calls into a lane worktree while its driver runs must not take `index.lock`. Verified by git's `--no-optional-locks` global option, which exists to skip the opportunistic index refresh.
- The scope allow-list parse can be built from steps.py public helpers without editing steps.py. Verified by `steps.py:333` (`criteria_indexed`), `390` (`line_spans`), `1401` (`list_item`), `1508` (`INVERT_GREP_RE`), `1526-1538` (`widen_forms`, `widen_listed`), and by `fanout.py:183` already importing `steps`.
- Lane worktrees sit at `<lanes-dir>/<lane>`, next to `<lanes-dir>/logs`, so the case 13 stub can use `../logs/fanout.log` and `../alpha`. Verified by `fanout.py:402` and the docstring at line 50.
- Every gate is green at HEAD. Verified by running `check.sh`, `check-packaging.py`, `codex_roles.py generate --check`, `tickets.py --root .sdlc check` and `fanout.py selftest`: all exit 0.
- The selftest guard can go red. Verified in a temp copy with one expect broken, where it printed `fanout selftest: FAIL`.
- `plugins/sdlc-lite/AGENTS.md` is the nearest non-root entry for `fanout.py`. No `docs/AGENTS.md` or `docs/maintenance/AGENTS.md` exists (checked with `ls`).

## Risks
- Case 13 depends on timing. If beta's merge-time check runs before alpha writes `shared.txt`, beta would not wait. The stub ordering prevents this: beta polls for alpha's edit before it finishes. A slow host still needs the 60 s bounds.
- An earlier lane with many tickets that keep touching a shared file can delay a later lane for a long time. Each merge empties the earlier lane's pending set, so the later lane gets through in that gap, but there is no hard cap.
- An overlap that appears only after a later lane has already started its merge is reported but not reordered. Step 3 states this limit in the docs.
- The second merge in an overlapping pair can still hit a real textual conflict (`merge conflict`). Ordering does not remove conflicts.
