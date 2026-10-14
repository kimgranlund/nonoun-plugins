## Task goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

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
  - `build_base` takes the records dir as a new argument beside `directory`. It reads `base-sha` and `*.dispatch.json` in the records dir. It reads the named `base:` line from `<directory>/handoff.md` first, the handoff prepare received (today's read at dispatch.py:410, the interface at :378-380 and :426), and falls back to `order.task_dir(records)/handoff.md` only when that file has none. Reason (plan review plan-reviewer-L1-2): a hand-written task-side `step-<n>/handoff.md` (chain §5) resolves `records` to `runtime/tasks/<key>/step-<n>`, where no handoff sits, so a records-only read would skip its `base:` line.
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
  - `lifecycle-selftest.py` :56-77,148-204: read `.running`, attempt and `runs.jsonl` from `order.records_dir` of the fixture task dir. Its direct `run_lifecycle.recover(directory)` call (:62, under `assertRaisesRegex(ValueError, 'still owns')`) passes `order.records_dir(directory)`, because `run` now locks the records dir and `recover` locks the dir it is given (run_lifecycle.py:55-69); on the task dir the lock no longer contends and the assertion fails.
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

Fixture paths: [creates: .sdlc/task, .sdlc/0001-a, .sdlc/runtime]. They sit under the criteria's scratch dir `$d` or the hook-selftest fixture root `$pr`, never in this repository; the marker is there because `steps.py lint` reads those paths as repo citations.
### Acceptance criteria
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && (cd "$d" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/task)" = ".sdlc/task/handoff.md" && test -f "$d/.sdlc/runtime/tasks/task/scout-L1.attempt.json" && test -f "$d/.sdlc/runtime/tasks/task/scout-L1.dispatch.json" && git -C "$d" check-ignore -q .sdlc/runtime/tasks/task/scout-L1.attempt.json`
- (guard) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && printf '{}\n' > "$d/.sdlc/task/runs.jsonl" && (cd "$d" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && test -f "$d/.sdlc/task/scout-L1.attempt.json" && test ! -e "$d/.sdlc/runtime/tasks/task"`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF "ok: records dir: prepare plus record leaves only handoff.md in the task dir" && printf '%s\n' "$out" | grep -qxF "ok: records dir: a legacy task dir with runs.jsonl keeps recording in place"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && printf "# Skips\n\n## Lane\n- lane: solo; point: p; reasons: r\n" > "$d/.sdlc/0001-a/skips.md" && (cd "$d" && SDLC_HEADLESS=1 python3 -c "import os, sys; sys.path.insert(0, sys.argv[1]); import solo_run; rc, got = solo_run.dispatch_json(sys.argv[3], \"L2\", \"b\", worktree=\"w\"); assert rc == 0 and os.path.realpath(got[\"artifacts_dir\"]) == os.path.realpath(sys.argv[2] + \"/.sdlc/runtime/tasks/0001-a\"), got.get(\"artifacts_dir\")" "$p" "$d" ".sdlc/0001-a") && test -f "$d/.sdlc/runtime/tasks/0001-a/runs.jsonl" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/0001-a | sort | tr "\n" " ")" = ".sdlc/0001-a/handoff.md .sdlc/0001-a/skips.md "`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a/step-1" && printf -- '---\nid: T-0901\ntitle: "x"\ntype: chore\nstatus: ready\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-13\nbudget_usd: 100\n---\n\n## Goal\nx\n' > "$d/.sdlc/0001-a/handoff.md" && printf '{"role": "builder", "cost_usd": 9, "attempt_id": "a1"}\n' > "$d/.sdlc/runtime/tasks/0001-a/step-1/runs.jsonl" && python3 plugins/sdlc-lite/scripts/budget.py status "$d/.sdlc/0001-a" | grep -qx "spend: 9.00" && python3 plugins/sdlc-lite/scripts/budget.py status "$d/.sdlc/runtime/tasks/0001-a/step-1" | grep -qx "spend: 9.00"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && python3 -c "import os, sys; sys.path.insert(0, os.path.abspath('plugins/sdlc-lite/scripts')); os.environ['SDLC_CODEX_TRANSPORT'] = 'subagent'; import codex_exchange, codex_exec; got = []; codex_exchange.wait_for_agent = lambda *a: got.append(a[5]) or 0; d = os.path.realpath(sys.argv[1]); os.chdir(d); codex_exec.run('solo', 'L2', 'p'); assert got and got[0].startswith(d + '/.sdlc/runtime/native-solo-')" "$d"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/h" "$d/r" && : > "$d/h/handoff.md" && printf '{"name":"x-scout-L1","model":"sonnet"}' > "$d/r/scout-L1.dispatch.json" && jq -n --arg h "$d/h/handoff.md" --arg r "$d/r" '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:scout-L1",name:"x-scout-L1",model:"sonnet",prompt:("Handoff: " + $h + "\nArtifacts dir: " + $r + "\nYour final message is saved verbatim as y.")}}' | bash plugins/sdlc-lite/hooks/block-role-spawn.sh && mkdir -p "$d/.sdlc/task" "$d/.sdlc/runtime/tasks/task" && : > "$d/.sdlc/task/handoff.md" && : > "$d/.sdlc/runtime/tasks/task/scout-L1.running" && out=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$d/.sdlc/task/handoff.md" | bash plugins/sdlc-lite/hooks/warn-handoff-edit.sh 2>&1) && printf '%s\n' "$out" | grep -qF "scout-L1" && test -f "$d/.sdlc/runtime/tasks/task/stale-edits.log" && test ! -e "$d/.sdlc/task/stale-edits.log"`
- (guard) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/h" "$d/r" && : > "$d/h/handoff.md" && jq -n --arg h "$d/h/handoff.md" --arg r "$d/r" '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:scout-L1",name:"x-scout-L1",model:"sonnet",prompt:("Handoff: " + $h + "\nArtifacts dir: " + $r + "\nYour final message is saved verbatim as y.")}}' | bash plugins/sdlc-lite/hooks/block-role-spawn.sh; test $? -eq 2`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && out=$(cd "$d" && env -i PATH="$PATH" HOME="$HOME" SDLC_BACKEND=codex SDLC_DRY_RUN=1 bash "$p/run.sh" scout L1 .sdlc/task/handoff.md 2>&1) && printf '%s\n' "$out" | grep -qF -- "--request-file $d/.sdlc/runtime/tasks/task/scout-L1.request.json" && printf '%s\n' "$out" | grep -qF "Artifacts dir: $d/.sdlc/runtime/tasks/task" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/task)" = ".sdlc/task/handoff.md"`
- (guard) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/task" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' > "$d/.sdlc/task/handoff.md" && printf '{}\n' > "$d/.sdlc/task/runs.jsonl" && out=$(cd "$d" && env -i PATH="$PATH" HOME="$HOME" SDLC_BACKEND=codex SDLC_DRY_RUN=1 bash "$p/run.sh" scout L1 .sdlc/task/handoff.md 2>&1) && printf '%s\n' "$out" | grep -qF -- "--request-file $d/.sdlc/task/scout-L1.request.json"`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh && python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py && bash plugins/sdlc-lite/scripts/run-selftest.sh && python3 plugins/sdlc-lite/scripts/solo_run.py selftest && python3 plugins/sdlc-lite/scripts/budget.py selftest && python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run_lifecycle.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/budget.py -e plugins/sdlc-lite/scripts/codex_exec.py -e plugins/sdlc-lite/scripts/lifecycle-selftest.py -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/hook-selftest.sh -e plugins/sdlc-lite/scripts/codex-selftest.py -e plugins/sdlc-lite/hooks/block-role-spawn.sh -e plugins/sdlc-lite/hooks/warn-handoff-edit.sh | { ! grep -q .; }`
