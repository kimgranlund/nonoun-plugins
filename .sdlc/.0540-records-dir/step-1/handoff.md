## Task goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

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

Fixture paths: [creates: .sdlc/0001-a, .sdlc/.0002-b, .sdlc/0003-c, .sdlc/0004-d, .sdlc/0005-e, .sdlc/0006-f, .sdlc/0007-g, .sdlc/0008-h, .sdlc/tickets/.0006-f, .sdlc/runtime]. Every one of these sits under the criteria's scratch dir `$d`, never in this repository; the marker is there because `steps.py lint` reads a `$d/.sdlc/...` path as a repo citation.
### Acceptance criteria
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/.0002-b/step-2" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0001-a")" = "$d/.sdlc/runtime/tasks/0001-a" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/.0002-b")" = "$d/.sdlc/runtime/tasks/0002-b" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/.0002-b/step-2")" = "$d/.sdlc/runtime/tasks/0002-b/step-2"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0004-d" "$d/.sdlc/0006-f" "$d/.sdlc/runtime/tasks/0005-e" "$d/.sdlc/runtime/tasks/0006-f" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0004-d/planner-L2.md" && : > "$d/.sdlc/0006-f/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0004-d")" = "$d/.sdlc/0004-d" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/runtime/tasks/0005-e")" = "$d/.sdlc/runtime/tasks/0005-e" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0006-f")" = "$d/.sdlc/runtime/tasks/0006-f"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0008-h" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0008-h/handoff.md" && printf "# Skips\n" > "$d/.sdlc/0008-h/skips.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(python3 plugins/sdlc-lite/scripts/order.py records-dir "$d/.sdlc/0008-h")" = "$d/.sdlc/runtime/tasks/0008-h"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0003-c" "$d/.sdlc/0004-d" && : > "$d/.sdlc/0003-c/runs.jsonl" && : > "$d/.sdlc/0004-d/builder-L2-2.md" && . plugins/sdlc-lite/scripts/records.sh && test "$(records_dir "$d/.sdlc/.0002-b/step-2")" = "$d/.sdlc/runtime/tasks/0002-b/step-2" && test "$(records_dir "$d/.sdlc/0003-c")" = "$d/.sdlc/0003-c" && test "$(records_dir "$d/.sdlc/0004-d")" = "$d/.sdlc/0004-d" && test "$(records_dir_make "$d/.sdlc/0001-a")" = "$d/.sdlc/runtime/tasks/0001-a" && test -d "$d/.sdlc/runtime/tasks/0001-a" && test "$(cat "$d/.sdlc/runtime/.gitignore")" = "*"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0004-d" "$d/.sdlc/runtime/tasks/0004-d" && printf '## x\n' > "$d/.sdlc/runtime/tasks/0004-d/planner-L2.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py newest "$d/.sdlc/0004-d" planner)" = "$d/.sdlc/runtime/tasks/0004-d/planner-L2.md"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0005-e" "$d/.sdlc/tickets/.0006-f" && : > "$d/.sdlc/0005-e/handoff.md" && : > "$d/.sdlc/tickets/.0006-f/handoff.md" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/runtime/tasks/0005-e/step-1")" = "$d/.sdlc/0005-e" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/runtime/tasks/0006-f")" = "$d/.sdlc/tickets/.0006-f" && test "$(python3 plugins/sdlc-lite/scripts/order.py task-dir "$d/.sdlc/0005-e")" = "$d/.sdlc/0005-e"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import order; d = sys.argv[1]; p = order.records_dir(d + '/.sdlc/0007-g', create=True); assert p.is_dir() and str(p) == d + '/.sdlc/runtime/tasks/0007-g'; assert open(d + '/.sdlc/runtime/.gitignore').read() == '*\n'" "$d"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && printf "<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n" > "$d/.sdlc/runtime/tasks/0001-a/planner-L2.md" && (cd "$d" && python3 "$p/steps.py" lane .sdlc/0001-a >/dev/null) && grep -q "^- lane: full; point: after planning;" "$d/.sdlc/0001-a/skips.md" && test ! -e "$d/.sdlc/runtime/tasks/0001-a/skips.md"`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/order.py selftest) && printf '%s\n' "$out" | grep -qF "ok: (g) records_dir"`
- (red) `shellcheck --severity=warning plugins/sdlc-lite/scripts/records.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh | { ! grep -q .; }`
