## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 3: steps.py next, review, and split refuse an invalid result through results.py
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

In `plugins/sdlc-lite/scripts/steps.py`, add `import results` beside `import order` (line 220).

Remove the copies of the table:
- Delete `first_word` and `REVIEW_VERDICTS`.
- `build_status_or_none(path)` returns `results.key_value(path, 'builder')`, and `verdict_or_none(path)` returns `results.key_value(path, 'verifier')`. Both keep their contract: they return `done`, `blocked`, `inherited`, `pass`, `fail`, or `None` and never raise. Both still ignore the header, because step 1's `key_value` reads only the key section.
- `review_verdict(path)` returns `results.key_value(path, 'plan-reviewer')`.
- `build_status` and `verdict` keep raising `Fail` with their current messages when the value is not done/blocked or pass/fail: `steps next: <path> has no builder status (done/blocked) under ## Status` and `steps next: <path> has no verifier verdict (pass/fail) under ## Verdict`.
- Keep `section()`, because `fanout.py` lines 634 to 636, `is_plan_defect`, and the traces readers use it.

Invalid-result route. This is a settled design decision, with this evidence:
- `plugins/sdlc-lite/AGENTS.md` line 19 says "Missing verdicts, inherited failures, plan defects, and implementation failures are distinct outcomes. Preserve".
- `/chain` items 5 and 6 route a missing builder Status to `rebuild` and a missing verifier Verdict to `reverify`.
- The steps.py selftest pins those routes at lines 2212 and 2226.

So `next`, `review`, and `split` call `results.structure_error`, not `validate`. A missing or disallowed builder Status, verifier Verdict, or plan-reviewer Verdict keeps its existing `rebuild`, `reverify`, or `review L1` route. Every other schema failure (empty file, header, role, declared order, planner without `## Goal`) becomes the new action `invalid result`. Changes:
- `next_action`: after the newest builder `b` is found, if `results.structure_error(b, 'builder')` is not None, return `('invalid result', None, f'{b}: {err}', [b])` before any other branch. Do the same for the newest verifier `v` that counts after `b`, with role `verifier`, before its verdict is read. Its read list is `[b, v]`.
- `review_action`: check the newest plan (role `planner`) right after `plan = plans[-1]`, before `plan_facts`. Check the newest plan-reviewer result that counts after it (`r = after[-1]`, role `plan-reviewer`) the same way, before its verdict is read.
- `split()`: right after `find_plan`, if `results.structure_error(plan, 'planner')` is not None, raise `Fail(f'invalid result: {plan}: {err}')`. Then take the newest plan-reviewer result that counts after the plan. This is the same pick `rejected_by_review` makes: the last item of `order.ordered(task_dir, 'plan-reviewer')` filtered by `order.counts_after(r, plan)`. When there is one and `results.structure_error(r, 'plan-reviewer')` is not None, raise `Fail(f'invalid result: {r}: {err}')`. Both checks run before `rejected_by_review`, `read_goal`, and any write, so nothing is written (exit 1, message on stderr). The handoff requires this: split must check the newest result of the task before any action that depends on it, and split's refusal depends on that review.
- `cmd_next`, `cmd_resume` (after the step dir line), and `cmd_review` share one printer. For `invalid result` it prints three things and exits 0:
  - line 1: `invalid result: <path>: <reason>`
  - line 2: `reason: the newest result does not match its results.py schema; stop and ask the user`
  - then the `read:` lines.
- `resume_action` already returns any action other than `done`, so it needs no other change.
- `lint` is unchanged, because the handoff names only next, review, and split.
- Update the module docstring for `next`, `review`, `resume`, and `split` to name the `invalid result` route.

Fixtures and contract dependents. Each one is in this step's scope criterion and run by a criterion below:
- `plugins/sdlc-lite/scripts/steps.py` selftest: every builder, verifier, planner, and plan-reviewer fixture gets a header.
  - Add one helper `hdr(name, text)`. It prepends `<!-- role=<role> level=L<n> model=opus effort=low -->` and a newline, with role and level parsed from the file name, unless the text already starts with `<!--`.
  - Use `hdr` in `task()` (line 1690), in `step()` (line 2143), and in every direct `write_text` of a `planner-*`, `builder-*`, `verifier-*`, or `plan-reviewer-*` fixture. Examples: lines 1732, 1798, 1817, 2070, 2117, 2127, and the review fixtures near line 2586.
  - Give `guard_plan()` (line 1999), and every other planner fixture that lacks one, a `## Goal` line with a one-line body before its first step. Keep Goal, Assumptions, Risks in that order. `PLAN` (line 1642) already has one.
  - No existing expectation changes: the missing-Status `rebuild` and missing-Verdict `reverify` cases keep their routes.
- `plugins/sdlc-lite/scripts/fanout.py` imports `steps.next_action` (line 630) in `inherited_red`. Its selftest stub drivers at line 1066 (builder) and lines 1148 to 1149 (builder and verifier) write headerless results. Those would now read as `invalid result` and break the inherited-red cases.
  - Prepend `<!-- role=builder level=L2 model=opus effort=low -->` to each builder printf, followed by a newline.
  - Prepend `<!-- role=verifier level=L1 model=sonnet effort=medium -->` to the verifier printf, followed by a newline.
  - The filer stubs stay as they are: no steps.py path reads a filer result.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: the case `results: on the same fixtures as step dirs, steps.next_action agrees` (line 385) runs `steps.next_action` on step dirs. It expects `verify`, `replan`, `inherited`, `rebuild`, `done`, and `reverify`. Its builder header at line 340 has no `level=` token and `_verifier_text` (line 345) writes no header, so both would read as `invalid result`.
  - Change line 340 to `head = '<!-- role=builder level=L2 model=opus effort=high -->\n'`.
  - In `_results_next` only, write each verifier fixture as `'<!-- role=verifier level=L1 model=sonnet effort=medium -->\n' + text`.
  - Keep `_verifier_text` itself headerless, because `_results_read` (line 351) asserts that a headerless verifier reads model and effort as None.
  - Add one assertion to `_results_next`: in a step dir whose `handoff.md` holds `level: L2\n` and whose `builder-L2.md` is `_builder_text('done')` without its first line, `steps.next_action(d)[0] == 'invalid result'`.
  - Evidence: I copied `scripts/` to /tmp and added a header check to `next_action`. This case then failed with `('done', 'invalid result')`. With the fixture changes above it passed, and `traces selftest: PASS`.
- Left untouched on purpose:
  - `board.py` keeps its own lenient readers, prints no action, and the handoff does not name it.
  - `traces/sources/results.py`, `traces/sources/bench.py`, `traces/rerun.py`, and `traces/detectors/escalation.py` read results only through `section`, `build_status_or_none`, and `verdict_or_none`. Those contracts hold and ignore the header.
  - The `traces/sources/results.py` docstring stays true: it classifies Status and Verdict values exactly as `steps.py` does.

Extend `results.py selftest` with these cases, locating `steps.py` next to `results.py`:
1. `ok: steps.py next on a headerless builder result prints invalid result, not verify`. Use a temp step dir holding a handoff with `level: L2`, `builder-L2.md` = `## Status\ndone`, and a runs.jsonl line. Run `steps.py next` by subprocess and require that the first line starts `invalid result:`.
2. `ok: steps.py next on a valid builder result prints verify L1`, the same dir with the header added.
3. `ok: negative control: an accept-all results.py lets steps.py next print verify`. In a temp dir, copy `steps.py` and `order.py`, plus a `results.py` copy with `validate = lambda path, role=None: None` and `structure_error = lambda path, role=None: None` appended. Run the copied `steps.py next` on case 1's fixture and require the first line `verify L1`.

Focused checks: `python3 plugins/sdlc-lite/scripts/steps.py selftest`, `python3 plugins/sdlc-lite/scripts/fanout.py selftest`, `python3 plugins/sdlc-lite/scripts/traces.py selftest`, and `python3 plugins/sdlc-lite/scripts/results.py selftest`.

### Acceptance criteria
- `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -q '^invalid result: .*builder-L2\.md: '`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py review "$d" | head -1 | grep -q '^invalid result: .*planner-L2\.md: '`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && err=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d" 2>&1 >/dev/null); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$err" | grep -q 'invalid result: .*planner-L2\.md: ' && test ! -e "$d/step-1"`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '<!-- role=planner level=L3 model=opus effort=xhigh -->\n## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L3.md" && printf '## Verdict\npass\n' >"$d/plan-reviewer-L1.md" && printf '{"file": "planner-L3.md"}\n{"file": "plan-reviewer-L1.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py review "$d" | head -1 | grep -q '^invalid result: .*plan-reviewer-L1\.md: '`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '<!-- role=planner level=L3 model=opus effort=xhigh -->\n## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L3.md" && printf '## Verdict\npass\n' >"$d/plan-reviewer-L1.md" && printf '{"file": "planner-L3.md"}\n{"file": "plan-reviewer-L1.md"}\n' >"$d/runs.jsonl" && err=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d" 2>&1 >/dev/null); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$err" | grep -q 'invalid result: .*plan-reviewer-L1\.md: ' && test ! -e "$d/step-1"`
- `python3 plugins/sdlc-lite/scripts/results.py selftest | grep -qxF 'ok: negative control: an accept-all results.py lets steps.py next print verify'`
- `python3 plugins/sdlc-lite/scripts/results.py selftest | grep -qxF 'ok: steps.py next on a headerless builder result prints invalid result, not verify'`
- `! grep -qE "REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'" plugins/sdlc-lite/scripts/steps.py`
- `grep -qF '<!-- role=builder level=L2 model=opus effort=high -->' plugins/sdlc-lite/scripts/traces/selftest.py`
- `grep -qF '<!-- role=verifier level=L1 model=sonnet effort=medium -->' plugins/sdlc-lite/scripts/traces/selftest.py`
- `grep -qF "'invalid result'" plugins/sdlc-lite/scripts/traces/selftest.py`
- `grep -qF '<!-- role=builder level=L2 model=opus effort=low -->' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '<!-- role=builder level=L2 model=opus effort=low -->\n## Status\ndone\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = 'verify L1'`
- (guard) `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '<!-- role=builder level=L2 model=opus effort=low -->\n## Changes\nx\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = 'rebuild L2'`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py split "$d" >/dev/null && test -f "$d/step-1/handoff.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '<!-- role=planner level=L3 model=opus effort=xhigh -->\n## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L3.md" && printf '<!-- role=plan-reviewer level=L1 model=fable effort=high -->\n## Verdict\npass\n' >"$d/plan-reviewer-L1.md" && printf '{"file": "planner-L3.md"}\n{"file": "plan-reviewer-L1.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py review "$d" | head -1)" = split && python3 plugins/sdlc-lite/scripts/steps.py split "$d" >/dev/null && test -f "$d/step-1/handoff.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/scripts/traces/selftest.py | { ! grep -q .; }`
