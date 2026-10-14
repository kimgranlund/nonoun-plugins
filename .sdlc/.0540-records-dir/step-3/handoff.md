## Task goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

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

Fixture paths: [creates: .sdlc/0001-a, .sdlc/runtime]. They sit under the criteria's scratch dir `$d`, never in this repository; the marker is there because `steps.py lint` reads a `$d/.sdlc/...` path as a repo citation.
### Acceptance criteria
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && printf -- '---\nid: T-0001\ntitle: "a"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n' > "$d/.sdlc/0001-a/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n' > "$d/.sdlc/runtime/tasks/0001-a/planner-L2.md" && (cd "$d" && python3 "$p/steps.py" split .sdlc/0001-a >/dev/null) && test -f "$d/.sdlc/runtime/tasks/0001-a/step-1/handoff.md" && test "$(git -C "$d" ls-files --others --exclude-standard -- .sdlc/0001-a)" = ".sdlc/0001-a/handoff.md"`
- (guard) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- '---\nid: T-0001\ntitle: "a"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n' > "$d/.sdlc/0001-a/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\nMake a.\n\n## Step 1: Make a\nlevel: L1\n### Do\nCreate a.txt.\n### Acceptance criteria\n- a.txt exists\n\n## Assumptions\n- none\n\n## Risks\nNone\n' > "$d/.sdlc/0001-a/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' > "$d/.sdlc/0001-a/runs.jsonl" && (cd "$d" && python3 "$p/steps.py" split .sdlc/0001-a >/dev/null) && test -f "$d/.sdlc/0001-a/step-1/handoff.md" && test ! -e "$d/.sdlc/runtime"`
- (guard) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && p="$PWD/plugins/sdlc-lite/scripts" && git init -q "$d" && git -C "$d" -c user.name=t -c user.email=t@e.invalid -c commit.gpgsign=false commit --allow-empty -qm seed && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: \"a\"\ntype: chore\nstatus: ready\nsize: L3\npriority: P2\ndepends: []\ncreated: 2026-10-13\n---\n\n## Goal\nMake a.\n" > "$d/.sdlc/0001-a/handoff.md" && (cd "$d" && python3 "$p/steps.py" lane .sdlc/0001-a >/dev/null) && grep -q "^- lane: full; point: before planning;" "$d/.sdlc/0001-a/skips.md" && test ! -e "$d/.sdlc/runtime"`
- (red) `t=$(printf %s "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}") && t="${t%/}" && mkdir -p "$t" && d=$(mktemp -d "$t/rd.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" "$d/.sdlc/runtime/tasks/0001-a" && : > "$d/.sdlc/0001-a/handoff.md" && printf "## Verdict\npass\n" > "$d/.sdlc/runtime/tasks/0001-a/verifier-L"2.md && python3 -c "import sys; sys.path.insert(0, \"plugins/sdlc-lite/scripts\"); import fanout; got = fanout.verifier_files(sys.argv[1] + \"/.sdlc/0001-a\"); assert got == {\"verifier-L\" \"2.md\"}, got" "$d"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && printf '%s\n' "$out" | grep -qF "ok: (records dir) split writes step dirs in the records dir" && printf '%s\n' "$out" | grep -qF "ok: (records dir) lane keeps skips.md in the task folder"`
- `python3 plugins/sdlc-lite/scripts/redck.py selftest && python3 plugins/sdlc-lite/scripts/verify_scope.py selftest`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/order.py -e plugins/sdlc-lite/scripts/records.sh -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run_lifecycle.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/budget.py -e plugins/sdlc-lite/scripts/codex_exec.py -e plugins/sdlc-lite/scripts/lifecycle-selftest.py -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/hook-selftest.sh -e plugins/sdlc-lite/scripts/codex-selftest.py -e plugins/sdlc-lite/hooks/block-role-spawn.sh -e plugins/sdlc-lite/hooks/warn-handoff-edit.sh -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/redck.py -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/fanout.py | { ! grep -q .; }`

## Previous attempt
From .sdlc/0540-records-dir/step-3/verifier-L3.md (fail; `<t>` is a fixture task folder named t):

`plugins/sdlc-lite/scripts/steps.py`: a task-side step dir whose records twin exists but holds no `handoff.md` is unreadable. `dispatch.py prepare` creates that state for every hand-written step: it keeps `handoff=<task>/step-<n>/handoff.md` and creates `order.records_dir(step dir)` as the artifacts dir at dispatch.py:874, so from the second dispatch of the step on, the twin exists and is empty of handoffs. `records_of` (steps.py:480-487) falls back to the given dir only when the twin does not exist; `step_handoff_of` (:2081-2091) therefore maps to the twin, finds no `handoff.md`, returns None, and `cmd_lint <step dir>` (:2093, the form dispatch.py:837 calls) falls to `find_plan` and fails with `steps: no planner-*.md in .sdlc/<t>/step-1`; `next_action` (:2552) and `resume_action` (:2721) fail with `no builder result and no .sdlc/runtime/tasks/t/step-1/handoff.md to read a level from`. Observed on a fixture (`.sdlc/<t>/handoff.md`, `.sdlc/<t>/step-1/handoff.md` = `## Task goal\ng\n\n## Step 1: x\nlevel: L2\n`, empty `.sdlc/runtime/tasks/t/step-1/`): built tree `steps.py lint .sdlc/<t>/step-1` rc 1, `next .sdlc/<t>/step-1` rc 1, `resume .sdlc/<t>` rc 1; the pre-step-3 copy: all rc 0; the built tree with the twin removed: rc 0. Broken dependent: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` is red on the built tree (`AssertionError: prepare failed in the record selftest: steps: no planner-*.md in .../B/.sdlc/<t>/step-1` followed by `dispatch.py: steps.py lint refused the links ...`, dispatch.py:2456 via :837) and green at base 27a0cc9c and in the pre-step-3 copy, both with the system TMPDIR, so this step broke it. Fix: when the dir given holds `handoff.md` and the twin holds none, read the handoff (level, links, lint) from the dir given and keep results in the twin; add a `steps.py selftest` case for a task-side step handoff with an existing empty records twin covering lint (dir form), next and resume; rerun `dispatch.py selftest` as part of the step's checks.

`plugins/sdlc-lite/scripts/fanout.py:1028-1030` `planned_scope` lists `step-*` under `tickets.ticket_dir(root)/<slug>` only, so a ticket planned after this step (step dirs in `order.records_dir`) reads as unplanned and the dry-run overlap refusal (:1074, :1678) no longer fires for it. Observed on the built tree with root `.sdlc`: a step handoff holding `grep -vxF -e shared.txt -e a.txt` under `.sdlc/0001-a/step-1/` gives `{'shared.txt', 'a.txt'}`, the same file under `.sdlc/runtime/tasks/0001-a/step-1/` gives `None`. Fix: enumerate `order.records_dir(tdir).glob('step-*')` (the legacy rule keeps in-place dirs) and give case 14 a records-dir variant.
