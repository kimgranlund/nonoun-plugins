<!-- role=planner level=L3 model=opus effort=high -->
## Goal
Run records (role results, attempt, dispatch, running, limit and request files, runs.jsonl, base-sha, budget-ack.md, step dirs) move from the ticket folder to the ignored records dir `.sdlc/runtime/tasks/<folder name without leading dot>/`, resolved by one rule in `order.py` and `scripts/records.sh`; `skips.md` stays in the task folder (decision 2026-10-13), and legacy folders keep recording in place.
guard timeout: 3960

## Step 1: Records-dir rule in order.py and records.sh
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none. Design: `.sdlc/.0539-lean-work-records/architect-L1.md` (Approach, Interfaces `order.records_dir`, row A; its Carry forward holds the code sites). This step builds the one rule every later step calls.

In `plugins/sdlc-lite/scripts/order.py` add:
- `records_dir(task_dir, create=False) -> pathlib.Path`.
  - Make paths absolute with `os.path.abspath`, never `realpath`, because the criteria compare against the `mktemp` path.
  - Base: the nearest ancestor named `.sdlc`, else the dir's parent.
  - Key: the folder name with leading dots stripped (`.0002-b` gives `0002-b`).
  - Rules, first match wins:
    1. A path already inside `<base>/runtime/tasks/` returns itself.
    2. A `step-<n>` dir (also `step-<n>.superseded-<k>`) returns `records_dir(parent)/<its name>`.
    3. If `<base>/runtime/tasks/<key>` exists, return it.
    4. Legacy: the dir holds `runs.jsonl`, any `*.attempt.json`, a role result (an `order.LOOSE` match ending `.md`, e.g. `planner-L2.md`, `builder-L2-2.md`), or a `step-<n>` dir. Return the dir itself.
    5. Else `<base>/runtime/tasks/<key>`.
  - `skips.md` is not a legacy marker. The maintainer decided on 2026-10-13 that `skips.md` stays in the task folder in this ticket (handoff Intent "Decided"), and `steps.py lane` writes it before any role runs (this ticket's own `skips.md` shows that order). As a marker, it would make every new ticket read as legacy and record in place.
  - The other markers are wider than the design's (`runs.jsonl` or `*.attempt.json`) on purpose. This file's own selftest fixtures at order.py:150-155 hold result files and no `runs.jsonl`, and the /fix skill writes hand-made `step-1/` dirs until T-0543. Under the narrower rule both would read as empty. A new task folder holds only `handoff.md` (and `skips.md`), so it still goes to runtime.
  - With `create=True`: make the dir (parents too), and write `<base>/runtime/.gitignore` containing `*` plus a newline when it is missing (the same content `dispatch.prune_edit` writes at dispatch.py:965-971). A legacy result is never created.
- `task_dir(path) -> pathlib.Path | None`, the reverse map.
  - For a path inside `<base>/runtime/tasks/<key>[/step-...]`, return the first existing dir holding `handoff.md` among `<base>/<key>`, `<base>/.<key>`, `<base>/tickets/<key>`, `<base>/tickets/.<key>`, `<base>/work/<key>`, `<base>/work/.<key>`. Else return None.
  - For any other path, a `step-<n>` dir returns its parent and everything else returns itself.
- `records`, `ordered`, `_results` and `_ranks` resolve their dir through `records_dir` (never create), so `newest(<task dir>, role)` finds results in runtime.
  - `counts_after` keeps working, because the `dirname` of a result is already its records dir.
  - This alone lets `steps.py lane` see a plan in runtime, because `steps.find_plan` and the lane's plan read go through `order.newest` (steps.py:460-467). The lane criterion below needs no `steps.py` edit.
- CLI:
  - `order.py records-dir <dir>` prints `records_dir` (absolute, no create).
  - `order.py task-dir <path>` prints `task_dir`, or prints nothing and exits 1 when it is None.
  - Update the module docstring's Usage lines. Fix the current usage path, which crashes on unknown arguments (main's `__doc__.split` raises at order.py:244).
- Selftest: add cases labelled `(g) records_dir: ...` and `(g) task_dir: ...`, printed through the existing `check` so the lines read `ok: (g) records_dir: ...`. The `records_dir` cases cover:
  - a new folder;
  - a dotted folder;
  - a step dir;
  - the legacy markers;
  - a folder holding only `handoff.md` and `skips.md`, which goes to runtime;
  - runtime precedence;
  - `create` writing `.gitignore`.

Create `plugins/sdlc-lite/scripts/records.sh` [creates: plugins/sdlc-lite/scripts/records.sh], a sourced file with no top-level side effects:
- `records_dir <dir>` follows the same five rules in bash, with the same markers (no `skips.md`). A relative input is prefixed with `$PWD/`. No symlink resolution. Legacy role results match `^[a-z][a-z-]*-L[0-9]+.*\.md$`.
- `records_dir_make <dir>` runs `mkdir -p` on the result (unless legacy), writes `<base>/runtime/.gitignore` (`*`) when it is missing, then prints the path.
- It must pass `shellcheck --severity=warning`, because check.sh runs it over `scripts/*.sh`.

Validation scope: `order.py selftest` and the criteria below. This step changes no callers; steps 2 and 3 switch them.
### Acceptance criteria
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/.0002-b/step-2" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0001-a")" = "$d/.sdlc/runtime/tasks/0001-a" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/.0002-b")" = "$d/.sdlc/runtime/tasks/0002-b" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/.0002-b/step-2")" = "$d/.sdlc/runtime/tasks/0002-b/step-2"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0004-d" "$d/.sdlc/0006-f" "$d/.sdlc/runtime/tasks/0005-e" "$d/.sdlc/runtime/tasks/0006-f" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0004-d/planner-L2.md" && : > "$d/.sdlc/0006-f/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0004-d")" = "$d/.sdlc/0004-d" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/runtime/tasks/0005-e")" = "$d/.sdlc/runtime/tasks/0005-e" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0006-f")" = "$d/.sdlc/runtime/tasks/0006-f"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0008-h" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0008-h/handoff.md" && printf "# Skips\n" > "$d/.sdlc/0008-h/skips.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0008-h")" = "$d/.sdlc/runtime/tasks/0008-h"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0004-d" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0004-d/builder-L2-2.md" && . plugins/sdlc-lite/scripts/records.sh && test "$(records_dir "$d/.sdlc/.0002-b/step-2")" = "$d/.sdlc/runtime/tasks/0002-b/step-2" && test "$(records_dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(records_dir "$d/.sdlc/0004-d")" = "$d/.sdlc/0004-d" && test "$(records_dir_make "$d/.sdlc/0001-a")" = "$d/.sdlc/runtime/tasks/0001-a" && test -d "$d/.sdlc/runtime/tasks/0001-a" && test "$(cat "$d/.sdlc/runtime/.gitignore")" = "*"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0004-d" "$d/.sdlc/runtime/tasks/0004-d" && printf '## x\n' > "$d/.sdlc/runtime/tasks/0004-d/planner-L2.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py newest "$d/.sdlc/0004-d" planner)" = "$d/.sdlc/runtime/tasks/0004-d/planner-L2.md"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0005-e" "$d/.sdlc/tickets/.0006-f" && : > "$d/.sdlc/0005-e/handoff.md" && : > "$d/.sdlc/tickets/.0006-f/handoff.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/runtime/tasks/0005-e/step-1")" = "$d/.sdlc/0005-e" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/runtime/tasks/0006-f")" = "$d/.sdlc/tickets/.0006-f" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/0005-e")" = "$d/.sdlc/0005-e"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import order; d = sys.argv[1]; p = order.records_dir(d + '/.sdlc/0007-g', create=True); assert p.is_dir() and str(p) == d + '/.sdlc/runtime/tasks/0007-g'; assert open(d + '/.sdlc/runtime/.gitignore').read() == '*\n'" "$d"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && printf "<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n" > "$d/.sdlc/runtime/tasks/0001-a/planner-L2.md" && (cd "$d" && python3 "$p/steps.py" lane .sdlc/0001-a >/dev/null) && grep -q "^- lane: full; point: after planning;" "$d/.sdlc/0001-a/skips.md" && test ! -e "$d/.sdlc/runtime/tasks/0001-a/skips.md"`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/order.py selftest) && printf '%s\n' "$out" | grep -qF "ok: (g) records_dir"`
- (red) `shellcheck --severity=warning plugins/sdlc-lite/scripts/records.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh | { ! grep -q .; }`

## Step 2: Role, solo, budget and Codex runs write in the records dir
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1 (`order.records_dir`, `order.task_dir`, `records.sh`). Design and code sites: `.sdlc/.0539-lean-work-records/architect-L1.md` (Inventory rows for results, attempt, dispatch, running, limit, delivery, request, base-sha, runs.jsonl and budget-ack.md; Carry forward).

The two dispatch paths move together in this step: `dispatch.py prepare` (Claude), and `run.sh` with `run_lifecycle.py` (Codex and the legacy Claude branch). That way, their parity cases and `lifecycle-selftest.py` never see the two paths write in different dirs. This answers the plan review finding that `run_lifecycle.run` derives its dir from the handoff at run_lifecycle.py:62 and that its only caller is `run.sh:390`.

Settled rules:
- Brief:
  - `Artifacts dir:` is the records dir.
  - `Handoff:` stays the handoff path given. For step roles that is `<records dir>/step-N/handoff.md` once step 3 lands.
  - `records_dir` of a records step dir is the dir itself, so step-role adjacency is unchanged.
- `skips.md` stays in the task folder (handoff Intent "Decided"). Every reader or writer of it here resolves the folder with `order.task_dir(<dir>)` (in shell, `order.py task-dir`). Never use `.parent` or `records_dir` for it, because a step dir under runtime has no `handoff.md` beside it.
- `dispatch.py` `prepare`:
  - Keep `directory = handoff.parent` for the handoff gates (precheck, unfilled, links).
  - Set `records = order.records_dir(directory, create=not dry_run)`. Use it for `run_lifecycle.lock`, `settle`, `next_stem`, `result`, `attempt_file`, `dispatch_file`, `artifacts_dir`, the `.running` marker, and the brief's `Artifacts dir:` line.
  - `build_base(directory, tree)` receives the records dir. It reads `base-sha` and `*.dispatch.json` there. It reads the named `base:` line from `records/handoff.md` when present, else from `order.task_dir(records)/handoff.md`.
  - The `lane_override` line (dispatch.py:906-911) goes to `order.task_dir(directory)/skips.md`.
  - `lane_gate` (:431-440): `lane_dir = order.task_dir(directory)`, with skips read from `lane_dir/skips.md`.
- Other `dispatch.py` sites:
  - `family` and `step_build` glob `step-*` under `order.records_dir(directory)`.
  - `solo_model` already goes through `order.records`.
  - `slug_of`, `ticket_label`, `agent_name` and `list_title` take the task dir from `order.task_dir`, so a step role in runtime keeps its `<ticket>-<role>-L<n>` name.
  - `attempt_dirs(open_only=True)` maps a dir under `runtime/tasks/` to `order.task_dir` before `ticket_closed`.
  - `status <dir>` and `recover <dir>` (dispatch.py:1498-1515, where `recover_orphans(args.directory)` globs only the given dir) map the dir through `order.records_dir` only when it holds `handoff.md` or is a `step-<n>` dir. Any other argument passes through unchanged, so a dir with no `.sdlc` ancestor never maps outside the project.
  - `recover_root`, `running_attempt` and `resume` already walk `.sdlc` (runtime included): keep that.
  - `prune_edit` keeps its `.gitignore` write.
- `run_lifecycle.py`:
  - `run` sets `directory = order.records_dir(handoff.resolve().parent, create=True)` (run_lifecycle.py:62).
  - Its `recover <dir>` CLI maps the dir through `order.records_dir`, under the same condition as `dispatch.py recover`.
  - `dispatch.py` passes it the records dir from prepare.
- `run.sh`:
  - Source `records.sh` from `$plugin_root/scripts/records.sh`. Keep `hdir="$(dirname "$handoff")"` for the handoff gates (precheck :323-324, links :335-336, the step-dir tests).
  - Set `dir` to `records_dir "$hdir"` for a dry run and to `records_dir_make "$hdir"` for a real run.
  - Everything run.sh writes or numbers goes in `$dir`: result, log, `.request.json`, `base-sha`, `.limit`, `.running`, `runs.jsonl`, the `step-*` verifier-family loop at :249, and the `Artifacts dir:` brief line at :429.
  - The lane check (:346-359) sets `lane_dir="$(python3 "$plugin_root/scripts/order.py" task-dir "$hdir")"`. The override line still goes to `"$lane_dir/skips.md"`.
- `solo_run.py`:
  - `dispatch_json`, `append`, `complete`, the `solo.limit` marker, the Codex `solo-*.request.json` exchange and `artifacts_dir` use `order.records_dir(task_dir, create=True)`.
  - The `handoff.md` checks and any `skips.md` read or write stay on the task dir.
- `budget.py`:
  - `ticket_of` maps a path under `runtime/tasks/` through `order.task_dir` first. Otherwise the prepare budget gate reads $0 for every step role (design Risks, silent degraders).
  - `spend` takes the rglob of `runs.jsonl` over both `records_dir(ticket)` and the ticket folder, deduplicated by `attempt_id` as today.
  - `ack` writes `budget-ack.md` into `records_dir(ticket, create=True)`. The reader checks there first, then the ticket folder.
- `codex_exec.py` :31-34: native `native-<role>-*.request.json` files go to `Path.cwd()/.sdlc/runtime/`, created with parents and the `.gitignore` (`*`).
- `hooks/block-role-spawn.sh`:
  - Parse an `Artifacts dir: <path>` line the same way as the `Handoff:` line (quoted or first token, relative to `.cwd`).
  - Look for the record there first (`$name.dispatch.json`, then any `*.dispatch.json` naming it), then beside the handoff (:99-110).
  - The deny message names both places.
  - A missing or nonexistent Artifacts dir falls back silently, so the existing fixtures with `Artifacts dir: x` (hook-selftest.sh:436-441) keep passing.
- `hooks/warn-handoff-edit.sh`:
  - Source `records.sh` with `. "$(dirname "${BASH_SOURCE[0]}")/../scripts/records.sh"` and a `# shellcheck source=../scripts/records.sh` line (the `_role.sh` pattern at block-role-write.sh:10-11).
  - Collect `*.running` from `records_dir <handoff dir>` and from the handoff dir, deduplicated when the two are the same dir.
  - Append `stale-edits.log` in the records dir when a marker sits there, else beside the handoff.
- A selftest fixture that drives a writer gets a `.sdlc` ancestor (for example `<tmp>/.sdlc/<name>`). With none, the base is the dir's parent and the records would land in the system temp dir.
- Selftests and contract dependents in this step:
  - `dispatch.py` selftest:
    - Add `case('records dir: prepare plus record leaves only handoff.md in the task dir', ...)`. In a git fixture it prepares and records a scout. It asserts that `git status --porcelain -uall -- <task dir>` lists only `handoff.md`, with the result, attempt, dispatch and `runs.jsonl` under `.sdlc/runtime/tasks/<name>/`.
    - Add `case('records dir: a legacy task dir with runs.jsonl keeps recording in place', ...)` as the negative control.
    - Update the location-pinning cases (dispatch.py:1892-1909, 2336-2354, and the `base-sha` and `runs.jsonl` fixtures the run turns red) to read `order.records_dir(<task>)`.
    - The `skips.md` fixtures at :1877-1886 stay in the task dir.
    - Do not add legacy markers to hide a move.
  - `lifecycle-selftest.py` :56-77,148-204: read `.running`, attempt and `runs.jsonl` from `order.records_dir` of the fixture task dir.
  - `run-selftest.sh` :40-45 and :156: update the pins to the records dir and add a legacy case. The dispatch.py parity cases (dispatch.py:1579-1585) compare run.sh with prepare, so both must write the same records dir.
  - `hook-selftest.sh` T-0505 prepared cases (:640-700, `pt="$pr/.sdlc/task"` at :644):
    - The `record` calls at :667 and :677 pass `.sdlc/runtime/tasks/task/scout-L1.dispatch.json`.
    - `scout-L1.attempt.json` (:668, :678, :691) and `stale-edits.log` (:658) are read from `$pr/.sdlc/runtime/tasks/task`.
    - The `recover "$pt"` calls keep the task dir and go through the new `recover` mapping.
    - Add one case for the Artifacts-dir allow and one for the deny when neither place holds a record.
    - The hand-made `.running` fixtures at :600-628 sit beside a handoff with no `.sdlc` ancestor and still pass through the beside-the-handoff read.
  - `codex-selftest.py`: :725-760 reads `solo-*.request.json` and `runs.jsonl` from the ticket dir, and :588 reads `native-conductor-*.request.json` under `.sdlc/`. Point both at the new places.
  - `fanout.py` calls `solo_run.append` (:1809), `budget_hold`, `dispatch.py prepare` (:1790) and `run.sh verifier` (:1425), and it reads verifier results from the task dir (`verifier_files`, :996-999). Its selftest turns red in this step; step 3 fixes it.
  - `tickets.py` is unchanged (handoff Intent "Decided"). `skip_missing` reads `skips.md` in the task folder, and its result and `runs.jsonl` reads go through `order` (step 1).
  - The readers in B (`board.py`, `report.py`, `fleet_*`) build their fixtures by hand and stay green. T-0541 and T-0543 own them.
### Acceptance criteria
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && (cd "$d" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/task)" = ".sdlc/task/handoff.md" && test -f "$d/.sdlc/runtime/tasks/task/scout-L1.attempt.json" && test -f "$d/.sdlc/runtime/tasks/task/scout-L1.dispatch.json" && git -C "$d" check-ignore -q .sdlc/runtime/tasks/task/scout-L1.attempt.json`
- (guard) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && printf '{}\n' > "$d/.sdlc/task/runs.jsonl" && (cd "$d" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && test -f "$d/.sdlc/task/scout-L1.attempt.json" && test ! -e "$d/.sdlc/runtime/tasks/task"`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF "ok: records dir: prepare plus record leaves only handoff.md in the task dir" && printf '%s\n' "$out" | grep -qxF "ok: records dir: a legacy task dir with runs.jsonl keeps recording in place"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && printf "# Skips\n\n## Lane\n- lane: solo; point: p; reasons: r\n" > "$d/.sdlc/0001-a/skips.md" && (cd "$d" && SDLC_HEADLESS=1 python3 -c "import os, sys; sys.path.insert(0, sys.argv[1]); import solo_run; rc, got = solo_run.dispatch_json(\".sdlc/0001-a\", \"L2\", \"b\", worktree=\"w\"); assert rc == 0 and os.path.realpath(got[\"artifacts_dir\"]) == os.path.realpath(sys.argv[2] + \"/.sdlc/runtime/tasks/0001-a\"), got.get(\"artifacts_dir\")" "$p" "$d") && test -f "$d/.sdlc/runtime/tasks/0001-a/runs.jsonl" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/0001-a | sort | tr "\n" " ")" = ".sdlc/0001-a/handoff.md .sdlc/0001-a/skips.md "`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a/step-1" && printf -- '---\nid: T-0901\ntitle: "x"\ntype: chore\nstatus: ready\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-13\nbudget_usd: 100\n---\n\n## Goal\nx\n' > "$d/.sdlc/0001-a/handoff.md" && printf '{"role": "builder", "cost_usd": 9, "attempt_id": "a1"}\n' > "$d/.sdlc/runtime/tasks/0001-a/step-1/runs.jsonl" && python3 plugins/sdlc-lite/scripts/budget.py status "$d/.sdlc/0001-a" | grep -qx "spend: 9.00" && python3 plugins/sdlc-lite/scripts/budget.py status "$d/.sdlc/runtime/tasks/0001-a/step-1" | grep -qx "spend: 9.00"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && python3 -c "import os, sys; sys.path.insert(0, os.path.abspath('plugins/sdlc-lite/scripts')); os.environ['SDLC_CODEX_TRANSPORT'] = 'subagent'; import codex_exchange, codex_exec; got = []; codex_exchange.wait_for_agent = lambda *a: got.append(a[5]) or 0; d = os.path.realpath(sys.argv[1]); os.chdir(d); codex_exec.run('solo', 'L2', 'p'); assert got and got[0].startswith(d + '/.sdlc/runtime/native-solo-')" "$d"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/h" "$d/r" && : > "$d/h/handoff.md" && printf '{"name":"x-scout-L1","model":"sonnet"}' > "$d/r/scout-L1.dispatch.json" && jq -n --arg h "$d/h/handoff.md" --arg r "$d/r" '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:scout-L1",name:"x-scout-L1",model:"sonnet",prompt:("Handoff: " + $h + "\nArtifacts dir: " + $r + "\nYour final message is saved verbatim as y.")}}' | bash plugins/sdlc-lite/hooks/block-role-spawn.sh && mkdir -p "$d/.sdlc/task" "$d/.sdlc/runtime/tasks/task" && : > "$d/.sdlc/task/handoff.md" && : > "$d/.sdlc/runtime/tasks/task/scout-L1.running" && out=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$d/.sdlc/task/handoff.md" | bash plugins/sdlc-lite/hooks/warn-handoff-edit.sh 2>&1) && printf '%s\n' "$out" | grep -qF "scout-L1" && test -f "$d/.sdlc/runtime/tasks/task/stale-edits.log" && test ! -e "$d/.sdlc/task/stale-edits.log"`
- (guard) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/h" "$d/r" && : > "$d/h/handoff.md" && jq -n --arg h "$d/h/handoff.md" --arg r "$d/r" '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:scout-L1",name:"x-scout-L1",model:"sonnet",prompt:("Handoff: " + $h + "\nArtifacts dir: " + $r + "\nYour final message is saved verbatim as y.")}}' | bash plugins/sdlc-lite/hooks/block-role-spawn.sh; test $? -eq 2`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && out=$(cd "$d" && env -i PATH="$PATH" HOME="$HOME" SDLC_BACKEND=codex SDLC_DRY_RUN=1 bash "$p/run.sh" scout L1 .sdlc/task/handoff.md 2>&1) && printf '%s\n' "$out" | grep -qF -- "--request-file $d/.sdlc/runtime/tasks/task/scout-L1.request.json" && printf '%s\n' "$out" | grep -qF "Artifacts dir: $d/.sdlc/runtime/tasks/task" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/task)" = ".sdlc/task/handoff.md"`
- (guard) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && printf '{}\n' > "$d/.sdlc/task/runs.jsonl" && out=$(cd "$d" && env -i PATH="$PATH" HOME="$HOME" SDLC_BACKEND=codex SDLC_DRY_RUN=1 bash "$p/run.sh" scout L1 .sdlc/task/handoff.md 2>&1) && printf '%s\n' "$out" | grep -qF -- "--request-file $d/.sdlc/task/scout-L1.request.json"`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh && python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py && bash plugins/sdlc-lite/scripts/run-selftest.sh && python3 plugins/sdlc-lite/scripts/solo_run.py selftest && python3 plugins/sdlc-lite/scripts/budget.py selftest && python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run_lifecycle.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/budget.py -e plugins/sdlc-lite/scripts/codex_exec.py -e plugins/sdlc-lite/scripts/lifecycle-selftest.py -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/hook-selftest.sh -e plugins/sdlc-lite/scripts/codex-selftest.py -e plugins/sdlc-lite/hooks/block-role-spawn.sh -e plugins/sdlc-lite/hooks/warn-handoff-edit.sh | { ! grep -q .; }`

## Step 3: steps.py writes step dirs in the records dir, and fanout reads records there
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 and 2. Step 1 provides `order.records_dir` and `order.task_dir`. Step 2 moves the writers whose output `fanout.py` reads, which turns the fanout selftest red; this step makes it green. Design: `.sdlc/.0539-lean-work-records/architect-L1.md` (row A for `steps.py`; Inventory row for `step-N/`).

In `plugins/sdlc-lite/scripts/steps.py`, keep two dirs apart. Derive both from whatever path a command receives: a task dir, a records dir, or a step dir on either side.
- task = `order.task_dir(path)`. It holds `handoff.md`, `## Goal`, the front matter, `## Plan review`, and `skips.md`.
  - `skips.md` stays in the task folder (handoff Intent "Decided").
  - `record_lane` and `write_solo_skips` (:3176-3210) and the lane readers (`lane_sticky` and `cmd_lane`, :2985-3060) keep `<task>/skips.md`.
- records = `order.records_dir(task)`. It holds the planner and plan-reviewer results, `runs.jsonl`, `refusals.jsonl` (still written until T-0543 stops it), and the `step-<n>` and `step-<n>.superseded-<k>` dirs.

What changes in `steps.py`:
- `find_plan` returns the plan through `order` and the task dir separately. `read_goal` reads the task.
- split, `--supersede`, `earlier_widened`, swap and widen create and enumerate step dirs under records, with `create=True` on write. Sites: steps.py:1577, 1861, 1906, 1930, 1948, 2175, 2472-2490, 2676.
- `base_sha` and `result_ts` read from the records step dir.
- A legacy task (step 1's markers) keeps everything in place, because `records_dir` returns the task dir.
- `cmd_next`, `cmd_open`, `cmd_resume`, `cmd_review`, `cmd_lane`, `cmd_verifier_level`, `cmd_precheck` and `cmd_lint` accept either side. The `read:` and step paths they print are the records-side paths the conductor passes as `Handoff:`.

Also:
- `redck.py` (path only): its dir argument goes through `order.records_dir`. `red-checkpoint.jsonl`, `process-deviations.md` (stopped by T-0543, not here) and the `*.attempt.json` glob live in that dir.
- `verify_scope.py`:
  - The lane check (:245-260) reads `order.task_dir(<handoff dir>)/skips.md`.
  - The tests gate reads `red-checkpoint.jsonl` through `order.records_dir`.
  - `RECORD_NAMES` is unchanged.
- Contract dependents in `fanout.py`, found by `grep -n "verifier_files\|solo_verdict(\|runs.jsonl\|solo_run\." fanout.py`:
  - `verifier_files` (:996-999) lists `verifier-L*.md` in `order.records_dir(taskdir)`. That way `solo_verdict` (:1016) sees a result that `run.sh verifier` (:1425) or prepare (:1790) wrote in runtime.
  - `price_solo_row` (:1816) reads `order.records_dir(taskdir)/runs.jsonl`, the file `solo_run.append` now writes.
  - The T-0331 fixture (:2808-2820) reads `runs.jsonl` through `order.records_dir(td)`. Give `td` a `.sdlc` parent so the records stay inside the temp dir.
  - Case 17 (:3850-3890) needs a re-pin:
    - Why: `LANE_ADD` (:1284) honors ignores, so the solo row in the lane's runtime dir never reaches `fanout/meter`, and the `git show fanout/meter:...runs.jsonl` read (:3872) comes back empty.
    - Re-pin it to read the `role solo` rows from the closed lane's archive: `<rr_>/.git/sdlc-lane-archive/<lane name>/.sdlc/runtime/tasks/<slug>/runs.jsonl`.
    - Why that path holds them: `lanes.close_lane` copies the lane's `.sdlc` to `ctx.common / 'sdlc-lane-archive' / name` before it removes the worktree (lanes.py:688-692). `copy_sdlc` (lanes.py:630-642) lists ignored files too, because its `ls-files --others` has no `--exclude-standard`.
    - The lane worktree's runtime dir survives between tickets. `fanout.py`'s only `reset --hard` and `clean` calls run in the integration worktree (:1531-1589, the clean scoped to the slug). Confirm with `grep -n "'clean'\|'reset'" fanout.py` before relying on it.
    - Keep the git-object read as the legacy fallback. Keep the negative control (raw lane: no solo row) as it is.
    - This matches the maintainer's 2026-10-13 call for case 16: A keeps `check.sh` green, and T-0542 (C) restores the cross-worktree record and re-pins the case to it.
  - Case 16 is unchanged. `skips.md` stays in the task folder, so its git-object read and the `no ## Skipped entry` negative control keep working.
  - Do not change the cross-worktree transport, which T-0542 replaces with a copy:
    - `commit_lane_records`, `branch_verdict` and `host_branch_ticket`;
    - the :1574 and :1199-1213 copies;
    - the `<id>-solo.dispatch.json` host record at :1900, which block-role-spawn still finds beside the handoff.

    If a fanout case can pass only with that transport change, stop with Status blocked and name the case.
- Selftests:
  - Add `check('(records dir) split writes step dirs in the records dir', ...)` and `check('(records dir) lane keeps skips.md in the task folder', ...)` to `steps.py selftest`, plus a legacy control.
  - Update the location-pinning cases the run turns red to read `order.records_dir`.
### Acceptance criteria
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && printf -- '---\nid: T-0001\ntitle: "a"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n' > "$d/.sdlc/0001-a/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n' > "$d/.sdlc/runtime/tasks/0001-a/planner-L2.md" && (cd "$d" && python3 "$p/steps.py" split .sdlc/0001-a >/dev/null) && test -f "$d/.sdlc/runtime/tasks/0001-a/step-1/handoff.md" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/0001-a)" = ".sdlc/0001-a/handoff.md"`
- (guard) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- '---\nid: T-0001\ntitle: "a"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n' > "$d/.sdlc/0001-a/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n' > "$d/.sdlc/0001-a/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' > "$d/.sdlc/0001-a/runs.jsonl" && (cd "$d" && python3 "$p/steps.py" split .sdlc/0001-a >/dev/null) && test -f "$d/.sdlc/0001-a/step-1/handoff.md" && test ! -e "$d/.sdlc/runtime"`
- (guard) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && (cd "$d" && python3 "$p/steps.py" lane .sdlc/0001-a >/dev/null) && grep -q "^- lane: full; point: before planning;" "$d/.sdlc/0001-a/skips.md" && test ! -e "$d/.sdlc/runtime"`
- (red) `t="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}" && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && : > "$d/.sdlc/0001-a/handoff.md" && printf "## Verdict\npass\n" > "$d/.sdlc/runtime/tasks/0001-a/verifier-L2.md" && python3 -c "import sys; sys.path.insert(0, \"plugins/sdlc-lite/scripts\"); import fanout; got = fanout.verifier_files(sys.argv[1] + \"/.sdlc/0001-a\"); assert got == {\"verifier-L2.md\"}, got" "$d"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && printf '%s\n' "$out" | grep -qF "ok: (records dir) split writes step dirs in the records dir" && printf '%s\n' "$out" | grep -qF "ok: (records dir) lane keeps skips.md in the task folder"`
- `python3 plugins/sdlc-lite/scripts/redck.py selftest && python3 plugins/sdlc-lite/scripts/verify_scope.py selftest`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run_lifecycle.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/budget.py -e plugins/sdlc-lite/scripts/codex_exec.py -e plugins/sdlc-lite/scripts/lifecycle-selftest.py -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/hook-selftest.sh -e plugins/sdlc-lite/scripts/codex-selftest.py -e plugins/sdlc-lite/hooks/block-role-spawn.sh -e plugins/sdlc-lite/hooks/warn-handoff-edit.sh -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/redck.py -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/fanout.py | { ! grep -q .; }`

## Step 4: Layout docs, Codex resume packet, and gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2 and 3.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, the layout block :9-78:
  - The task folder holds `handoff.md` and `skips.md` and is committed. `skips.md` moves later (T-0542 or T-0543, per the 2026-10-13 decision).
  - `.sdlc/runtime/tasks/<task-slug>/` (the folder name without a leading dot) holds the role results, `runs.jsonl`, the attempt, dispatch, running, log and limit files, `base-sha`, `budget-ack.md`, and the `step-N/` dirs. It is ignored through `runtime/.gitignore`.
  - Write the legacy rule in one sentence, and name `${CLAUDE_PLUGIN_ROOT}/scripts/order.py records-dir <task dir>`. check.py item 42 refuses a `plugins/` or `../` path in a skill.
  - Replace the paragraph "Keep the results .md files, runs.jsonl, and *.attempt.json committed..." with "records are local and ignored". Drop the now-redundant per-file ignore list.
  - Keep the rest minimal. The docs specs belong to T-0545.
- `plugins/sdlc-lite/adapters/codex/instructions.md` resume packet (:37): leave the packet in the records dir that `order.py records-dir <task dir>` prints, not in the ticket folder. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` if `generate --check` reports stale output.
- Gates:
  - Run `bash plugins/sdlc-lite/scripts/check.sh` (about 1320 s on record; slower under load).
  - Fix any red that steps 1 to 3 introduced by pointing the failing read or fixture at `order.records_dir` (or at `order.task_dir` for `skips.md`). Never fix it by moving a writer back.
  - A gate that is red at the build-start HEAD is `inherited red`.
  - Then run `python3 scripts/check-packaging.py` and `git diff --check`.
### Acceptance criteria
- (red) `grep -qF ".sdlc/runtime/tasks/<task-slug>/" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (red) `! grep -qE "Keep the results .{1,2}\.md.{1,2} files, .{1,2}runs\.jsonl" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (red) `sed -n '/^Resume packet/,/^$/p' plugins/sdlc-lite/adapters/codex/instructions.md | grep -qF "records-dir"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/.*)$" | { ! grep -q .; }`

## Assumptions
- Replan scope: the plan review (handoff `## Plan review`) names steps 2 and 3 and the step 3 dependency claim.
  - Step 1 also changes in one place: `skips.md` is dropped from the legacy markers. The 2026-10-13 decision keeps `skips.md` in the task folder, and `steps.py lane` writes it before any role runs, so as a marker it would send every new ticket to the legacy path.
  - Verified: this ticket's own `.sdlc/0540-records-dir/skips.md` holds lane lines written before planning. The step 1 criterion with a `handoff.md` plus `skips.md` folder is red at base only because the `records-dir` CLI is missing.
- The `run.sh`, `run_lifecycle.py`, `lifecycle-selftest.py` and `run-selftest.sh` changes moved from step 4 into step 2, beside `dispatch.py prepare`.
  - The plan review found that `run_lifecycle.run` derives its dir at run_lifecycle.py:62 and that its only caller is `run.sh:390`.
  - The two dispatch paths share parity cases (dispatch.py:1579-1585), and fanout's `run.sh verifier` path (:1425) reads the same results.
  - Moving both paths in one step keeps every step's criteria green on their own.
- The `steps.py lane` after-planning criterion sits in step 1. `steps.find_plan` reads the plan through `order.newest` (steps.py:460-467), so step 1's `order` change alone turns it green. Verified red at base: the lane printed `point: before planning` because it cannot see a plan in runtime.
- Fanout case 17 is re-pinned to the lane archive rather than left red.
  - `LANE_ADD` (fanout.py:1284-1285) honors ignores, so a runtime `runs.jsonl` never reaches the lane branch.
  - `lanes.copy_sdlc` (lanes.py:630-642, `ls-files --others` without `--exclude-standard`) copies ignored `.sdlc` files into `ctx.common / 'sdlc-lane-archive' / name` before `close_lane` removes the worktree (lanes.py:688-692).
  - Fanout resets and cleans only the integration worktree (`grep -n "'clean'\|'reset'" fanout.py`: :1531-1589).
  - This follows the maintainer's case 16 call: A keeps `check.sh` green, and C owns the cross-worktree record.
- The records rule, key and base follow the ratified design: verified in `.sdlc/.0539-lean-work-records/architect-L1.md` Interfaces (records_dir) and Carry forward.
- A step role's `Handoff:` becomes `<records dir>/step-N/handoff.md`, so prepare's adjacency logic holds for step roles unchanged. The design Interfaces ("Brief") says so, and the step 3 split writes there.
- `dispatch.py recover <dir>` and `status <dir>` take a handoff dir and glob only it (dispatch.py:1498-1515), so the hook-selftest `recover "$pt"` calls need the conditional records-dir mapping that step 2 adds. Verified by reading the CLI.
- Prepare in a fresh git fixture works under `env -i` with only PATH and HOME. Verified by the base probe of the step 2 legacy guard: exit 0, and its un-negated form (runtime dir present) exits 1.
- The run.sh Codex dry run prints `Artifacts dir: <dir>` and `--request-file <dir>/<role>-<level>.request.json`, and writes nothing. Verified at base: the request file is under `.sdlc/task/`.
- The hook deny guard exits 2 at base: verified by the first plan's probe and the plan review ("the deny criterion exits 2").
- `codex_exec.run` imports `wait_for_agent` at call time, so the criterion's patch reaches it. Verified by the first plan's base probe and by the plan review.
- `guard timeout: 3960` is three times the 1320 s `check.sh` run recorded in `.sdlc/.0520-ui-designer-agent/planner-L3-2.md:125`.
- Probe results at base for this replan, one Bash call per probe script under `$SDLC_TMP_WORKTREES`:
  - Red because the behavior is missing:
    - step 1 skips-only folder: no `records-dir` CLI, usage crash;
    - step 1 lane after planning: prints `point: before planning`;
    - step 2 solo with `skips.md`: `artifacts_dir` is the task folder;
    - step 2 run.sh dry run: request file under `.sdlc/task`;
    - step 3 `fanout.verifier_files`: returns an empty set.
  - Guards green:
    - every scope guard with `SDLC_BASE_SHA=HEAD`;
    - `git diff --check`;
    - the step 2 prepare and run.sh legacy guards;
    - the step 3 lane guard.
  - Un-negated forms red: a path outside the allow-list, a runtime dir after a legacy prepare, and `skips.md` in runtime after a lane call.
  - Criteria unchanged from the first plan (`.sdlc/0540-records-dir/planner-L3.md`) keep its probe results. The focused selftests named in steps 2 and 3 passed at base there.
  - `steps.py lint` and `specgate.py check` passed on this plan text.

## Risks
- `check.sh` was not run at plan time. At split, the step 4 `check.sh` guard may run longer than 3960 s under load. That is a flaky-gates matter, not a defect.
- Step 2 is large: two dispatch paths, solo, budget, Codex exec, two hooks and six selftests. It stays one step because the parity cases and `lifecycle-selftest.py` need both dispatch paths to move together. It sits at the 12-criterion cap, with the two hook red checks joined into one criterion.
- Case 17's re-pin depends on the lane worktree's ignored runtime dir surviving until `close_lane`. If a later change cleans ignored files in a lane worktree between tickets, the archive holds only the last ticket's row.
- Between this ticket and T-0541, T-0542 and T-0543 on main, readers that still look in the task folder quietly read nothing new for new tickets:
  - `tickets.py` `skip_missing` stops checking per-step verifiers, because it lists `step-<n>` in the task folder.
  - `recorded_base` reads nothing.
  - Claim staleness misses runtime `.running` markers.
  - `board.py`, `report.py`, `fleet_*`, `plan_done.py` and fanout's git-object verdict transport read nothing new.
  - A real sub-agent solo lane verified through prepare leaves its verdict in the sub-agent worktree's runtime. `commit_lane_records` does not commit it, so `land` reports no verifier result until T-0542.

  The design accepts this ("release only after wave 5"). No release happens in A.
- A fanout selftest case other than 16 and 17 may need the cross-worktree copy (T-0542). Step 3 then blocks by design, and the fix is a replan or a resequence.
- The `task_dir` search covers `<base>`, `tickets/` and `work/` only. A ticket root under any other name, or the same folder name under two roots, maps to the first match.
- Roles still find task-folder files such as `design.md` or `decompose/` only through the `Handoff:` path, not the `Artifacts dir:`. /grill and /decompose write those files there until T-0544.
- The scratch fixtures use `$SDLC_TMP_WORKTREES` when it is set, else `$TMPDIR`. The criteria never remove them.
