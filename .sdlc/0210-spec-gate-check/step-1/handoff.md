## Task goal
Add the free half of the spec gate: `scripts/specgate.py check`, the `run.sh` plan-reviewer refusal, and a plan-level `guard timeout:` line that `steps.py split --only` honors.

## Step 1: specgate.py check, split timeout default, run.sh plan-reviewer refusal
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none.

1. `plugins/sdlc-lite/scripts/steps.py` (the parser owner):
   - Add `GUARD_TIMEOUT_RE = re.compile(r'^guard timeout:\s*(\d+(?:\.\d+)?)\s*$')` and two helpers.
     - `plan_guard_timeout(plan)` returns the float from a matching line that sits outside every `## Step` block (for example the second line of `## Goal`), else None.
     - `step_guard_timeout(block)` returns the float from a matching line inside one step block, else None.
     - A value of 0 or less counts as no line.
   - `split(target, only=None, guard_timeout=None)` and `cmd_split` follow the same rule. An explicit `--guard-timeout` wins. Otherwise each chosen step uses its own step line, else the plan line, else 300.
   - `run_guards` takes per-step timeouts, a dict `{n: seconds}`. The red line format `timed out after {t:g}s` is unchanged.
   - In `main`, set argparse `--guard-timeout` default to None. Keep the finite and greater-than-0 check for an explicit value. Update the help text and the module docstring's split paragraph to name the `guard timeout:` line.
   - Add selftest cases labelled exactly:
     - `(guard timeout) a plan guard timeout line sets the split --only default`
     - `(guard timeout) a step guard timeout line overrides the plan line`
     - `(guard timeout) --guard-timeout overrides both lines`
   - Use a `sleep` guard just past a 1 s line, the same pattern as the existing case `(n)` near steps.py:2430.
   - `steps.py lint` stays as it is.
2. New `plugins/sdlc-lite/scripts/specgate.py` with `check <planner.md | task dir>` and `selftest`.
   - It imports `steps` from its own directory (`import steps` on its own line, the way `board.py` imports `tickets`). It uses `steps.find_plan`, `parse_steps`, `criteria_lines`, `line_spans`, `is_guard_line`, `plan_guard_timeout` and `step_guard_timeout`, and defines no parser of its own (cost-control.md:56, review finding 5).
   - It is read-only and has three finding kinds. Each finding prints to stderr as `specgate: <plan>: step <n>: <kind>: <detail>`, followed by a last line `specgate: <k> finding(s); fix the plan before plan review`, then exit 1.
   - Kind `slow guard`: a span on a `(guard)` line runs `check.sh`, and that step has neither its own line nor a plan line.
     - "Runs" means a command word ends in `check.sh`: at the start of the span, or after `;`, `&`, `|`, `(`, `$(`, `!`, `then`, `do` or `else`, past optional `VAR=x`, `bash`, `sh`, `env` or `timeout N` prefixes.
     - Probed regex: `(?:^|[;&|(!]|\$\(|\b(?:then|do|else)\s)\s*(?:\w+=\S*\s+)*(?:(?:timeout\s+\S+|bash|sh|env)\s+)*["']?\S*check\.sh["']?(?=\s|$|[;&|)])`.
     - It matched `bash plugins/sdlc-lite/scripts/check.sh` and `bash "$root/scripts/check.sh"`. It did not match `grep -qF x .../check.sh`, the `grep -vxF -e .../check.sh` scope guards, `shellcheck .../check.sh` or `check-packaging.py`.
   - Kind `duplicate span`: a command span on an untagged (non-`(guard)`) criterion line repeats verbatim a span from an earlier step. The detail names that earlier step.
     - Guard lines are exempt, because scope guards repeat by design.
     - Steps titled `Merge ...` are exempt, because the merge-step template repeats.
     - Repeats inside one step are not flagged.
   - Kind `red and guard`: a criterion line whose leading tag run, after `- ` or `* `, holds both `(guard)` and `(red)`.
   - A clean plan prints `specgate: ok: <plan>` on stdout and exits 0.
   - A target that does not exist exits 1.
   - A dir with no `planner-*.md`, or a plan that `steps.parse_steps` refuses (no step blocks, no level line), prints `specgate: skip: <reason>` on stderr and exits 0. Existing fixtures run plan-reviewer on such dirs: run-selftest.sh:207-244 (no planner, header-only planners), run-selftest.sh:323-328 (no planner) and codex-selftest.py:348-377 (`## Goal\nx` planner).
   - `selftest` prints `ok: <label>` per case and the last line `specgate selftest: PASS`. The labels are exactly those in criterion 1.
   - The replay fixtures copy criterion lines verbatim, because the T-0183 plan is untracked and lives only in `<main checkout>/.worktrees/t0183/.sdlc/0183-supervisor-script/planner-L3.md`.
     - From that file: the step 2 criteria (lines 281-286), the step 3 criteria (lines 341-345) and the step 7 `(guard) bash plugins/sdlc-lite/scripts/check.sh` line (line 538). Expect a `duplicate span` at step 3 and a `slow guard` at step 7.
     - From `.sdlc/.0195-runner-family-task-dir/planner-L3-2.md`: the step 4 check.sh guard line. Expect a `slow guard` at step 4.
3. `plugins/sdlc-lite/scripts/run.sh`, inside the `{ ... }` group (run.sh:92-97), placed immediately before the `exec python3 "$plugin_root/scripts/run_lifecycle.py"` block (run.sh:254-257):
   - When `SDLC_LIFECYCLE_CHILD` is not 1 and the role is `plan-reviewer`, the gate runs. It runs on dry runs too, so a dry run previews the refusal.
   - With `SDLC_SPECGATE=off`, it prints one stderr line `run.sh: SDLC_SPECGATE=off: spec gate skipped` and continues.
   - Otherwise it captures `python3 "$plugin_root/scripts/specgate.py" check "$dir"` (stdout and stderr). On a nonzero exit it prints the captured lines and `run.sh: specgate.py check refused the plan in <dir>; replan, or set SDLC_SPECGATE=off` to stderr and exits 2. On exit 0 it prints nothing.
   - Because the gate sits before the exec, no attempt record, `.running` file or `runs.jsonl` line exists yet (the lifecycle writes those).
   - The run-line `jq` (run.sh:474-480) adds `specgate: "off"` only when the role is plan-reviewer and `SDLC_SPECGATE` is `off`. The env reaches the child through run_lifecycle.py:94 `dict(os.environ, ...)`.
   - Update the header: an `Exit codes` line saying 2 also covers a spec gate refusal, plus an env note for `SDLC_SPECGATE`.
   - Both backends pass through this code. Codex native exchange still enters through run.sh (codex-selftest.py:349).
4. `plugins/sdlc-lite/scripts/run-selftest.sh` gets spec gate cases in its stub-claude harness. Failures read `spec gate: <reason>`.
   - A dry run on a plan with a check.sh guard and no line exits 2 and prints `slow guard`.
   - A real run on that plan exits 2, the stub is never called, and no `runs.jsonl` or `*.running` exists.
   - A plan with the line dry-runs to exit 0.
   - With `SDLC_SPECGATE=off`, a real run exits 0 and its run line has `"specgate":"off"`.
   - The existing no-planner and header-only cases keep exit 0.
5. `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/specgate.py" selftest || fail=1` after the footprint line (check.sh:27) and name `specgate.py` in the header comment's selftest list.
6. Contract dependent left as it is: `traces/sources/runs.py:15` reads a fixed field list and ignores the extra `specgate` key.

Focused checks: `python3 plugins/sdlc-lite/scripts/specgate.py selftest`, `python3 plugins/sdlc-lite/scripts/steps.py selftest`, `bash plugins/sdlc-lite/scripts/run-selftest.sh`, `python3 plugins/sdlc-lite/scripts/codex-selftest.py`.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/specgate.py selftest) && test "$(printf "%s\n" "$out" | tail -n 1)" = "specgate selftest: PASS" && for l in "check: a plan with a guard timeout line passes" "check: a check.sh guard with no guard timeout line is refused" "check: a step guard timeout line covers only its own step" "check: a guard that only names check.sh is not flagged" "check: a criterion repeated across steps is refused" "check: a guard repeated across steps is not flagged" "check: a merge step template criterion is not flagged" "check: (red) beside (guard) on one line is refused" "check: no planner result or no step blocks skips with exit 0" "replay: T-0183 step 3 duplicate and step 7 timeout are flagged" "replay: T-0195 step 4 timeout is flagged"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/specgate.py check .sdlc/.0195-runner-family-task-dir/planner-L3-2.md 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "step 4: slow guard:"`
- `p=$(ls -d .sdlc/0184-role-result-schema .sdlc/.0184-role-result-schema 2>/dev/null | head -n 1) && test -n "$p" && out=$(python3 plugins/sdlc-lite/scripts/specgate.py check "$p/planner-L2.md" 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "step 7: slow guard:" && ! printf "%s\n" "$out" | grep -qE "step (1|3): " && out=$(python3 plugins/sdlc-lite/scripts/specgate.py check .sdlc/.0197-lane/planner-L3.md 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "step 3: slow guard:" && ! printf "%s\n" "$out" | grep -qE "step 2: "`
- `d=$(mktemp -d) && mkdir -p "$d/t" && printf "## Goal\nx\n" >"$d/t/handoff.md" && printf "<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\nguard timeout: 1\n\n## Step 1: A\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140sleep 3\140\n\n## Assumptions\nNone\n\n## Risks\nNone\n" >"$d/t/planner-L1.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" --only 1 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "timed out after 1s" && test ! -e "$d/t/step-1/handoff.md"`
- `d=$(mktemp -d) && mkdir -p "$d/t" && printf "## Goal\nx\n" >"$d/t/handoff.md" && printf "<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\nguard timeout: 10\n\n## Step 1: A\nlevel: L1\nguard timeout: 1\n### Do\nx\n### Acceptance criteria\n- (guard) \140sleep 3\140\n\n## Assumptions\nNone\n\n## Risks\nNone\n" >"$d/t/planner-L1.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" --only 1 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "timed out after 1s"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && test "$(printf "%s\n" "$out" | tail -n 1)" = "steps selftest: PASS" && for l in "(guard timeout) a plan guard timeout line sets the split --only default" "(guard timeout) a step guard timeout line overrides the plan line" "(guard timeout) --guard-timeout overrides both lines"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `d=$(mktemp -d) && r=$PWD/plugins/sdlc-lite/scripts/run.sh && git -C "$d" init -q && mkdir -p "$d/.sdlc/t" "$d/bin" && printf "## Goal\nx\n" >"$d/.sdlc/t/handoff.md" && printf "<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\n\n## Step 1: Gates\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140bash plugins/sdlc-lite/scripts/check.sh\140\n\n## Assumptions\nNone\n\n## Risks\nNone\n" >"$d/.sdlc/t/planner-L1.md" && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -qm i && out=$(cd "$d" && env -u SDLC_LIFECYCLE_CHILD -u SDLC_ATTEMPT_NAME -u SDLC_SPECGATE SDLC_BACKEND=claude SDLC_DRY_RUN=1 PATH="$d/bin:$PATH" bash "$r" plan-reviewer L1 .sdlc/t/handoff.md 2>&1); rc=$?; test "$rc" -eq 2 && printf "%s\n" "$out" | grep -qF "step 1: slow guard:"`
- `d=$(mktemp -d) && r=$PWD/plugins/sdlc-lite/scripts/run.sh && git -C "$d" init -q && mkdir -p "$d/.sdlc/t" "$d/bin" && printf "## Goal\nx\n" >"$d/.sdlc/t/handoff.md" && printf "<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\n\n## Step 1: Gates\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140bash plugins/sdlc-lite/scripts/check.sh\140\n\n## Assumptions\nNone\n\n## Risks\nNone\n" >"$d/.sdlc/t/planner-L1.md" && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -qm i && printf "%s\n" '{"type":"result","is_error":false,"result":"## Verdict\npass","total_cost_usd":0,"duration_ms":1,"num_turns":1}' >"$d/res.json" && printf "%s\n" "#!/bin/sh" "touch $d/called" "cat $d/res.json" >"$d/bin/claude" && chmod +x "$d/bin/claude" && (cd "$d" && env -u SDLC_LIFECYCLE_CHILD -u SDLC_ATTEMPT_NAME -u SDLC_SPECGATE -u SDLC_DRY_RUN SDLC_BACKEND=claude PATH="$d/bin:$PATH" bash "$r" plan-reviewer L1 .sdlc/t/handoff.md >/dev/null 2>&1); rc=$?; test "$rc" -eq 2 && test ! -e "$d/called" && test ! -e "$d/.sdlc/t/runs.jsonl" && test -z "$(find "$d/.sdlc/t" -name "*.running")"`
- `d=$(mktemp -d) && r=$PWD/plugins/sdlc-lite/scripts/run.sh && git -C "$d" init -q && mkdir -p "$d/.sdlc/t" "$d/bin" && printf "## Goal\nx\n" >"$d/.sdlc/t/handoff.md" && printf "<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\n\n## Step 1: Gates\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140bash plugins/sdlc-lite/scripts/check.sh\140\n\n## Assumptions\nNone\n\n## Risks\nNone\n" >"$d/.sdlc/t/planner-L1.md" && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -qm i && printf "%s\n" '{"type":"result","is_error":false,"result":"## Verdict\npass","total_cost_usd":0,"duration_ms":1,"num_turns":1}' >"$d/res.json" && printf "%s\n" "#!/bin/sh" "touch $d/called" "cat $d/res.json" >"$d/bin/claude" && chmod +x "$d/bin/claude" && (cd "$d" && env -u SDLC_LIFECYCLE_CHILD -u SDLC_ATTEMPT_NAME -u SDLC_DRY_RUN SDLC_SPECGATE=off SDLC_BACKEND=claude PATH="$d/bin:$PATH" bash "$r" plan-reviewer L1 .sdlc/t/handoff.md >/dev/null 2>&1) && test -e "$d/called" && tail -n 1 "$d/.sdlc/t/runs.jsonl" | jq -e ".specgate == \"off\""`
- `f=plugins/sdlc-lite/scripts/specgate.py; test -f "$f" && grep -qxF "import steps" "$f" && ! grep -qE "^def (find_plan|parse_steps|criteria_lines|line_spans|guard_spans|is_guard_line|is_command)\(" "$f" && grep -qF "python3 \"\$root/scripts/specgate.py\" selftest" plugins/sdlc-lite/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/specgate.py)"`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh >/dev/null && python3 plugins/sdlc-lite/scripts/codex-selftest.py >/dev/null 2>&1`
