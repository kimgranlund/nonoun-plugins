<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `plugins/sdlc-lite/scripts/results.py` as the one declared result schema per role. `run.sh` and `steps.py` (`next`, `review`, `split`) validate every result against it before the pipeline advances, and a malformed result is refused (`run.sh` exit 3, `steps.py` `invalid result: <path>: <reason>`).

## Step 1: Add results.py with the schema table, validator, CLI, and selftest
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/results.py` (python3, stdlib only, executable, no em dashes) and wire its selftest into `plugins/sdlc-lite/scripts/check.sh`. Depends on: none.

Settled table `SCHEMA` (the only copy in the repo). Each role has `key` (the gating section), `allowed` (tuples of token, regex, display; empty for roles with no allowed set) and `sections` (the declared output order, taken from the `## ` lines of each `agents/<role>.md` output template):
- builder: key Status; allowed done, blocked, and inherited (regex `inherited red: .+`, display `inherited red: <tests>`); sections Status, Changes, Checks, Notes
- verifier: key Verdict; allowed pass, fail, inherited (same regex and display); sections Verdict, Criteria, Out of scope changes, For the next attempt
- plan-reviewer: key Verdict; allowed pass, replan, blocked; sections Verdict, Findings, Missing decisions
- planner: key Goal; sections Goal, Assumptions, Risks (`## Step <n>: ...` headings are not declared and are ignored)
- researcher: key Answer; sections Answer, Findings, Conflicts and gaps
- scout: key Map; sections Map, Entry points, Not found
- archaeologist: key Summary; sections Summary, Decisions, Landmines, Inferred
- architect: key Approach; sections Approach, Interfaces, Constraints and assumptions, Rejected alternatives, Risks
- filer: key Warnings; sections Warnings, PR title, PR body, Changelog entry, Follow-ups

Only the key section is required to be present. Every other declared section is optional, but when two or more declared sections are present, their first occurrences must follow the declared order. Evidence that keeps every previously valid result valid:
- `run-selftest.sh` lines 256 to 276 pin `## Verdict\npass` alone and `## Status\ninherited red: test_a` alone as exit 0.
- A scan of all 8048 historical result files under every `.sdlc/` in this checkout found 0 order violations and 0 missing key sections.

Parsing rules (they match `run.sh` lines 472 to 482 and `steps.py` `section()` at line 942):
- A heading matches when `line.rstrip() == '## <Name>'`.
- A key section's body runs to the next line starting with `## `.
- Its value is the first non-blank line, stripped and lowercased, and must `re.fullmatch` one allowed regex.
- An empty key body passes for roles with no allowed set (as `run.sh` accepts today).

Header rule: the first line, rstripped, must fullmatch this regex:

```
^<!-- role=([a-z-]+) level=(L[1-5]) model=(\S+) effort=(\S+)((?: [a-z_]+=\S+)*) -->$
```

Extra `key=value` tokens are accepted, such as `shared_with_builder=yes` written by `run.sh` line 461.

Python API, which steps 2 to 4 rely on:
- `validate(path, role=None)` returns `None` when the result is valid, else one reason string.
- `structure_error(path, role=None)` runs the same checks except the key-section presence and value checks for roles that have an allowed set (builder, verifier, plan-reviewer). For every other role it still requires the key section.
- `key_value(path, role)` returns the token (`done`, `blocked`, `inherited`, `pass`, `fail`, `replan`) for the key value, or `None`, and never raises.
- `ROLES` is the tuple of the nine roles.

With no `role`, the role is read from the header.

Settled reason strings, checked in this order:
1. `no such file`
2. `empty result` (zero bytes, or only whitespace)
3. `first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header`
4. `unknown role <x> in header`
5. `header role=<x> does not match --role <r>`
6. `lacks ## <Key>` for a missing key section, with ` (<display values joined by |>)` appended when the role has an allowed set, for example `lacks ## Status (done|blocked|inherited red: <tests>)`
7. `## <Key> first line "<value>" is not one of <display joined by |>`
8. `## <B> comes before ## <A>` for the first pair where declared-earlier A appears after B

Reasons 6 and 7 contain `lacks ## <Key>` and `## <Key>`, which the existing greps in `run-selftest.sh` (lines 257, 264, 266, 275) and `codex-selftest.py` line 102 (`lacks ## Map`) need.

CLI (handoff Intent):
- `results.py validate <result.md> [--role R]` exits 0 silently. On an invalid result it prints exactly one stderr line, `results.py: <file>: <reason>`, with `<file>` as given on the command line, and exits 1.
- `results.py schema [--role R]` prints one tab-separated line per role in the table order above: `<role>\t<key>\t<allowed displays joined by | or ->\t<sections joined by |>`.
- `results.py key <role>` prints the key section name, for example `Status`. `run.sh` uses it in step 2.
- `results.py selftest` prints `ok: <name>` per case, then `results selftest: PASS` and exits 0, else names the misses and exits 1.
- Usage errors (unknown subcommand or role) exit 2.

Selftest cases (temp files only):
- A valid result for each of the nine roles passes, including one with ` shared_with_builder=yes`.
- `inherited red: test_a` is accepted for builder and verifier. Bare `inherited red` is rejected.
- A missing key section, a disallowed first value (builder `maybe`, verifier `maybe`, plan-reviewer `maybe`), no header, an empty file, a role mismatch, and a verifier with `## Criteria` before `## Verdict` each fail with their exact reason.
- `structure_error` ignores a builder's missing Status but still reports a planner's missing Goal.

In `check.sh`, add `python3 "$root/scripts/results.py" selftest || fail=1` before the steps.py line, and add `results.py` to the header comment's selftest list.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/results.py selftest`
- `python3 plugins/sdlc-lite/scripts/results.py schema | grep -qxF "$(printf 'plan-reviewer\tVerdict\tpass|replan|blocked\tVerdict|Findings|Missing decisions')"`
- `python3 plugins/sdlc-lite/scripts/results.py schema | grep -qxF "$(printf 'builder\tStatus\tdone|blocked|inherited red: <tests>\tStatus|Changes|Checks|Notes')"`
- `test "$(python3 plugins/sdlc-lite/scripts/results.py key scout)" = Map`
- `f=$(mktemp) && printf '<!-- role=builder level=L1 model=sonnet effort=low -->\n## Status\ndone\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f"`
- `f=$(mktemp) && printf '## Status\ndone\n' >"$f" && out=$(python3 plugins/sdlc-lite/scripts/results.py validate "$f" --role builder 2>&1); rc=$?; test "$rc" -eq 1 && test "$(printf '%s\n' "$out" | wc -l)" -eq 1 && printf '%s\n' "$out" | grep -qF "results.py: $f: first line is not a"`
- `f=$(mktemp) && : >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" --role scout 2>&1 | grep -qxF "results.py: $f: empty result"`
- `f=$(mktemp) && printf '<!-- role=verifier level=L1 model=sonnet effort=medium -->\n## Criteria\nx\n\n## Verdict\npass\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" 2>&1 | grep -qxF "results.py: $f: ## Verdict comes before ## Criteria"`
- `f=$(mktemp) && printf '<!-- role=plan-reviewer level=L1 model=opus effort=high -->\n## Verdict\nmaybe\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" 2>&1 | grep -qF 'is not one of pass|replan|blocked'`
- `for f in $(git ls-files -- '.sdlc/*' ':(exclude).sdlc/.*' | grep -E '/(builder|verifier|planner|plan-reviewer|researcher|architect|scout|archaeologist|filer)-L[1-5](-[0-9]+)?\.md$'); do python3 plugins/sdlc-lite/scripts/results.py validate "$f" || exit 1; done`
- `grep -qF 'scripts/results.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`

## Step 2: run.sh validates through results.py; check.py's plan-reviewer guard reads the schema
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

In `plugins/sdlc-lite/scripts/run.sh`:
- Delete the per-role `case "$role" in builder) sect=Status; allowed=...` table (lines 124 to 134) and its comment.
- In the child path, just before the `events=` result pick (line 450), set `sect=$(python3 "$plugin_root/scripts/results.py" key "$role")`. The jq pick at line 451 keeps using `## $sect` unchanged.
- Replace the awk `val=` / `bad=` block (lines 472 to 486) with a call to `python3 "$plugin_root/scripts/results.py" validate "$result" --role "$role"`. On any nonzero exit, take the reason by stripping the literal prefix `results.py: $result: ` from its output line, print `run.sh: $role result <reason>; see $result` on stderr, and exit 3. On success, keep `echo "$result"; exit 0`.
- Exit codes and the `run.sh: <role> result ... ; see <file>` shape are unchanged.
- The missing-section message becomes `run.sh: builder result lacks ## Status (done|blocked|inherited red: <tests>); see ...`, which still satisfies every existing grep: `run-selftest.sh` 257, 264, 266, 275 and `codex-selftest.py` 102 (`lacks ## Map`).
- Keep all new code inside the `{ ... }` group (self-edit rule, header lines 82 to 87).
- Rewrite the header comment lines 17 to 21: the result check is `scripts/results.py validate` against the table that `results.py schema` prints (header line, key section with builder `inherited red: <tests>` and verifier `inherited red: <tests>` accepted, declared section order), and the result-pick heading comes from `results.py key`. The words `inherited red` must stay in run.sh, because `check.py` `INHERITED_RED_DOCS` (line 163) requires them.
- The Codex backend shares this path (`run.sh` builds `cmd` for `codex_exec.py`, and the check runs after it), so no Codex transport change is needed. `codex_exec.py` has no section check of its own (`grep` found none).

In `plugins/sdlc-lite/scripts/run-selftest.sh`, after line 276, add an order case: `want_rc 3 verifier L1` with a result holding `## Criteria` before `## Verdict` (pass), then `grep -q 'comes before' "$tmp/rerr"`, failing otherwise.

Contract dependent: `plugins/sdlc-lite/scripts/check.py` lines 344 to 352 pin the deleted line `plan-reviewer) sect=Verdict; allowed='pass|replan|blocked' ;;`. Replace that guard:
- Import `results` with `sys.path.insert(0, str(root/'scripts'))`.
- Require `results.SCHEMA['plan-reviewer']` to have key `Verdict` and allowed tokens exactly pass, replan, blocked.
- Require run.sh to contain `results.py" validate`.
- Keep the `plan-reviewer:L1` row check and a negative control that a mutated schema copy and a run.sh text without the validate call are each flagged.
- Remove the constant `PR_SECT`.

`lifecycle-selftest.py` pins none of these messages (grep found no `lacks`); run it as a guard.

### Acceptance criteria
- `grep -qF 'results.py" validate' plugins/sdlc-lite/scripts/run.sh`
- `grep -qF 'results.py" key' plugins/sdlc-lite/scripts/run.sh`
- `! grep -qE "allowed='|sect=[A-Z]" plugins/sdlc-lite/scripts/run.sh`
- `grep -qF 'comes before' plugins/sdlc-lite/scripts/run-selftest.sh`
- `! grep -qF 'PR_SECT = "plan-reviewer) sect=' plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `grep -qF 'inherited red' plugins/sdlc-lite/scripts/run.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py | { ! grep -q .; }`

## Step 3: steps.py next, review, and split refuse an invalid result through results.py
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

In `plugins/sdlc-lite/scripts/steps.py`, add `import results` beside `import order` (line 220).

Remove the copies of the table:
- Delete `first_word` and `REVIEW_VERDICTS`.
- `build_status_or_none(path)` returns `results.key_value(path, 'builder')`, and `verdict_or_none(path)` returns `results.key_value(path, 'verifier')`. Both keep their contract: `done`, `blocked`, `inherited`, `pass`, `fail`, or `None`, never raising.
- `review_verdict(path)` returns `results.key_value(path, 'plan-reviewer')`.
- `build_status` and `verdict` keep raising `Fail` with their current messages when the value is not done/blocked or pass/fail.
- Keep `section()`, because `fanout.py` lines 634 to 636 and `is_plan_defect` use it.

Invalid-result route. This is a settled design decision, with this evidence:
- `plugins/sdlc-lite/AGENTS.md` says "Missing verdicts, inherited failures, plan defects, and implementation failures are distinct outcomes. Preserve".
- `/chain` items 5 and 6 route a missing builder Status to `rebuild` and a missing verifier Verdict to `reverify`.
- The steps.py selftest pins those routes at lines 2212 and 2226.

So `next` and `review` call `results.structure_error`, not `validate`. A missing or disallowed builder Status, verifier Verdict, or plan-reviewer Verdict keeps its existing `rebuild`, `reverify`, or `review L1` route. Every other schema failure (empty file, header, role, declared order, planner without `## Goal`) becomes the new action `invalid result`. Changes:
- `next_action`: after the newest builder `b` is found, if `results.structure_error(b, 'builder')` is not None, return `('invalid result', None, f'{b}: {err}', [b])` before any other branch. Do the same for the newest verifier `v` that counts after `b`, with role `verifier`, before its verdict is read.
- `review_action`: check the newest plan (role `planner`) right after it is picked, and the newest plan-reviewer result counting after it (role `plan-reviewer`) right after it is picked, the same way.
- `cmd_next`, `cmd_resume` (after the step dir line), and `cmd_review` share one printer. For `invalid result` it prints line 1 `invalid result: <path>: <reason>`, line 2 `reason: the newest result fails results.py validate; stop and ask the user`, then the `read:` lines, and exits 0.
- `split()`: right after `find_plan`, if `results.structure_error(plan, 'planner')` is not None, raise `Fail(f'invalid result: {plan}: {err}')`, so nothing is written (exit 1, stderr).
- `lint` is unchanged, because the handoff names only next, review, and split.
- Update the module docstring for `next`, `review`, and `split` to name the `invalid result` route.

Fixtures and contract dependents:
- The steps.py selftest helpers `task()` and `step()` (lines 1690 and 2143) write results with no header. Make them prepend `<!-- role=<role> level=L<n> model=opus effort=low -->`, with role and level parsed from the file name, unless the text already starts with `<!--`.
- Give the `PLAN` fixture (line 1642) and any other planner fixture a `## Goal` line before the first step if it lacks one.
- `plugins/sdlc-lite/scripts/fanout.py` imports `steps.next_action` (line 630). Its selftest stub drivers write headerless results (lines 1066 and 1148 and any verifier or planner stub). Prepend the same kind of header there.
- `board.py` keeps its own lenient readers. It prints no action and the handoff does not name it, so it is untouched on purpose.

Extend `results.py selftest` with these cases:
1. `ok: steps.py next on a headerless builder result prints invalid result, not verify`. Use a temp step dir holding a handoff with `level: L2`, `builder-L2.md` = `## Status\ndone`, and a runs.jsonl line, run `steps.py next` by subprocess, and require that the first line starts `invalid result:`.
2. `ok: steps.py next on a valid builder result prints verify L1`, the same dir with the header added.
3. `ok: negative control: an accept-all results.py lets steps.py next print verify`. In a temp dir, copy `steps.py` and `order.py`, plus a `results.py` copy with `validate = lambda path, role=None: None` and `structure_error = lambda path, role=None: None` appended. Run the copied `steps.py next` on case 1's fixture and require the first line `verify L1`.

### Acceptance criteria
- `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -q '^invalid result: .*builder-L2\.md: '`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py review "$d" | head -1 | grep -q '^invalid result: .*planner-L2\.md: '`
- `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && err=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d" 2>&1 >/dev/null); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$err" | grep -q 'invalid result: .*planner-L2\.md: ' && test ! -e "$d/step-1"`
- `python3 plugins/sdlc-lite/scripts/results.py selftest | grep -qxF 'ok: negative control: an accept-all results.py lets steps.py next print verify'`
- `python3 plugins/sdlc-lite/scripts/results.py selftest | grep -qxF 'ok: steps.py next on a headerless builder result prints invalid result, not verify'`
- `! grep -qE "REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'" plugins/sdlc-lite/scripts/steps.py`
- (guard) `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '<!-- role=builder level=L2 model=opus effort=low -->\n## Status\ndone\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = 'verify L1'`
- (guard) `d=$(mktemp -d) && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf '<!-- role=builder level=L2 model=opus effort=low -->\n## Changes\nx\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = 'rebuild L2'`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n' >"$d/handoff.md" && printf '<!-- role=planner level=L2 model=opus effort=medium -->\n## Goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n- x\n' >"$d/planner-L2.md" && printf '{"file": "planner-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py split "$d" >/dev/null && test -f "$d/step-1/handoff.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py | { ! grep -q .; }`

## Step 4: check.py guards agent bodies against the schema and refuses schema copies
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 2 (check.py already imports `results`) and step 3 (steps.py holds no copy any more, else the copy guard is red).

In `plugins/sdlc-lite/scripts/check.py`, add two guards and a docstring item for them.

The first guard checks the result schema against the agent bodies:
- For each role in `results.SCHEMA`, read `agents/<role>.md`. Every declared section must appear as a line exactly `## <Section>` (rstripped), and their first occurrences must be in the declared order.
- A failure appends `agents/<role>.md: result schema: <what>`, for example `missing ## Checks` or `## Checks before ## Changes`, so the printed line starts `FAIL agents/<role>.md: result schema`.
- Add an inline negative control: the builder body with `## Changes` and `## Checks` swapped must be flagged, else append `check.py: result-schema agent guard negative control not flagged`.
- The current bodies already satisfy this. Verified: builder 24/27/30/33, verifier 25/30/33/36, plan-reviewer 41/44/50, planner 64/80/86, and every other role matches in order.

The second guard keeps the table in one place:
- `scripts/run.sh` must not match the regex `allowed='|sect=[A-Z]`, and `scripts/steps.py` must not match the regex below.

```
REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'
```

- A match appends `scripts/<file>: holds a copy of the result schema`.
- Add an inline negative control: run.sh text with an appended `allowed='x'` line must be flagged.

### Acceptance criteria
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c 'import sys,pathlib; p=pathlib.Path(sys.argv[1]); s=p.read_text(); p.write_text(s.replace("## Changes", "## TMPX").replace("## Checks", "## Changes").replace("## TMPX", "## Checks"))' "$t/p/agents/builder.md" && out=$(python3 "$t/p/scripts/check.py" "$t/p"); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'FAIL agents/builder.md: result schema'`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && printf "%s\n" "# allowed='x'" >>"$t/p/scripts/run.sh" && out=$(python3 "$t/p/scripts/check.py" "$t/p"); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'FAIL scripts/run.sh: holds a copy of the result schema'`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py | { ! grep -q .; }`

## Step 5: Document the invalid-result stop and results.py ownership
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 2, 3, 4. Make these edits, with no em dashes:
- `plugins/sdlc-lite/skills/chain/SKILL.md`, the action list at line 45: `invalid result: <path>: <reason>` from `steps.py next` (also from `steps.py review`, and the `steps.py split` refusal) is a stop. Interactive: report it and ask the user. Unattended: stop the task and report the line. It is never a rebuild, reverify, bump, or replan. Update the sentence "`run.sh` exits 3 when the result lacks its required section" to say that `run.sh` exits 3 when the result fails `results.py validate`, and that a missing or disallowed Status or Verdict still routes through items 5 and 6.
- `plugins/sdlc-lite/skills/fix/SKILL.md` step 3: add `invalid result` from `steps.py next` to the stop list.
- `docs/references/sdlc-internals.md`:
  - Add an entry headed exactly ``## `scripts/results.py` `` (table, CLI, reasons, `structure_error` versus `validate`, selftest and negative control).
  - Update the `scripts/run.sh` entry (line 11): the post-run check is `results.py validate`, the heading comes from `results.py key`, and the order case.
  - Update the `scripts/steps.py` entry (line 35): the `invalid result` action for `next`, `review`, and `resume`, and the `split` refusal.
- `plugins/sdlc-lite/AGENTS.md`: under Contracts and routing, add one bullet. `scripts/results.py` owns each role's result schema (key section, allowed first values, header, declared order). `run.sh` and `steps.py` call it, `check.py` checks agent bodies against it, and no other file copies it.

Left untouched on purpose:
- `agents/conductor.md`: it says "Escalation follows /chain", and an edit there would regenerate Codex agent TOML.
- `skills/handoff-format/SKILL.md`: the `.sdlc` layout does not change, since this ticket adds no file or folder under `.sdlc/`.
- `.sdlc/AGENTS.md`: no new folder, so no router line.

Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`. It must stay green, because chain and fix are not preloaded skills.
### Acceptance criteria
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/fix/SKILL.md`
- ``grep -qxF '## `scripts/results.py`' docs/references/sdlc-internals.md``
- `grep -qF 'invalid result' docs/references/sdlc-internals.md`
- `grep -qF 'scripts/results.py' plugins/sdlc-lite/AGENTS.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/skills/chain/SKILL.md -e plugins/sdlc-lite/skills/fix/SKILL.md -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md | { ! grep -q .; }`

## Step 6: Live run proving a malformed builder result does not advance
level: L3
### Do
Depends on: steps 2 and 3.

Run a real Claude `run.sh builder L1` in a throwaway project and record the evidence in `docs/reports/role-result-schema-live-run.md`, following the shape of `docs/reports/plan-reviewer-live-run.md`. No em dashes.

Setup:
- Use a throwaway project made with `mktemp -d`: `git init`, one commit, and `.sdlc/t/step-1/handoff.md`. Never use this repository's `.sdlc`.
- Run `bash <abs path>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t/step-1/handoff.md` from that project root.

Arms:
1. Malformed: the handoff tells the builder to make a trivial change and end its final message with only a `## Changes` section, with no `## Status`. Expect `run.sh` exit 3 with a `run.sh: builder result lacks ## Status ...` stderr line. Then `python3 <abs>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t/step-1` must print `rebuild L1`, not `verify`, so the pipeline does not advance.
2. Structural: copy that run's saved `builder-L1.md` with its header line removed into a second step dir that has its own handoff and runs.jsonl line. `steps.py next` must print `invalid result: ...`.
3. Normal: a fresh step dir with a handoff that asks for the normal output. Expect exit 0, and `steps.py next` prints `verify L1`.

If the model ignores the malformed instruction, rerun once with a stronger instruction. If it still emits Status, record that arm as unverified, never as a fixture.

The doc has these sections, each containing the exact strings named:
- `## Environment`: date `2026-10-..`, host OS, `claude --version`, and the repo commit.
- `## Commands`: the exact commands, including the literal `run.sh builder L1`.
- `## Evidence`: per arm, the exit code, written as `exit 3` or `exit 0`, the stderr line, and the `steps.py next` first line (`rebuild L1`, `invalid result`, `verify L1`).
- `## Limits`: the Codex backend arm is unverified unless run, and it is one model at one level.
### Acceptance criteria
- `f=docs/reports/role-result-schema-live-run.md && for s in "## Environment" "## Commands" "## Evidence" "## Limits" "run.sh builder L1" "exit 3" "exit 0" "rebuild L1" "verify L1" "invalid result"; do grep -qF "$s" "$f" || exit 1; done`
- `grep -qE "2026-[0-9]{2}-[0-9]{2}" docs/reports/role-result-schema-live-run.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/skills/chain/SKILL.md -e plugins/sdlc-lite/skills/fix/SKILL.md -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md -e docs/reports/role-result-schema-live-run.md | { ! grep -q .; }`

## Step 7: Gates green
level: L3
### Do
Depends on: steps 1 to 6. Run every gate the handoff's Common rules name and fix any red the earlier steps introduced, inside the files those steps changed:
- `bash plugins/sdlc-lite/scripts/check.sh`, which includes the results.py, steps.py, and fanout.py selftests, run-selftest, codex-selftest, lifecycle-selftest, check.py, and plugin validate
- packaging
- Codex generation check
- tickets check
- `git diff --check`
- no em dash in added lines or new files

A gate already red at the build-start HEAD is reported as Status `inherited red: <tests>`. Do not bump versions, tag, push, or publish.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins docs | grep '^+' | grep -q '—'`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs); do ! grep -q "—" "$f" || exit 1; done`

## Assumptions
- Only the key section is required, and other declared sections are order-checked only when present. Verified by `run-selftest.sh:256-276` (exit 0 for `## Verdict\npass` alone and `## Status\ninherited red: test_a` alone) and by a scan of 8048 historical result files under every `.sdlc/` in this checkout: 0 order violations, 0 missing key sections.
- Tracked results in open ticket dirs all pass the proposed header and key-value rules. Verified by a scan of `git ls-files .sdlc`: 1019 results, and the only failure is `.sdlc/.0163-codex-default-models-rejected/step-1/builder-L3.md`, a closed history dir with a hand-recovered header lacking `model=`/`effort=`. The step 1 history criterion therefore excludes `.sdlc/.*` closed dirs.
- A missing or disallowed builder Status, verifier Verdict, or plan-reviewer Verdict keeps its rebuild, reverify, or review route rather than `invalid result`. Verified by `plugins/sdlc-lite/AGENTS.md` ("distinct outcomes. Preserve"), `skills/chain/SKILL.md:52-53`, and `steps.py` selftest lines 2212 and 2226.
- `fanout.py` depends on `steps.next_action` and `steps.section`, and its selftest writes headerless results. Verified by `fanout.py:183,630-636,1066,1148`.
- `check.py` pins the run.sh plan-reviewer case line. Verified by `check.py:345`. `check.py` runs on a copied plugin dir: verified by running `python3 "$t/p/scripts/check.py" "$t/p"` (ok).
- The Codex backend reaches the same run.sh post-run check, and `codex_exec.py` holds no section check. Verified by `run.sh:291-296,447-486` and a grep of `codex_exec.py`.
- shellcheck is not installed on this host. Verified by `command -v shellcheck` (exit 127), so no shellcheck criterion is used, and check.sh skips it.
- check.sh, packaging, codex generate --check, and tickets check are green at HEAD. Verified by running each (check.sh rc=0).

## Risks
- The handoff says "an invalid result makes `next` print `invalid result`". This plan keeps the missing-Status and missing-Verdict rebuild/reverify routes, per the plugin AGENTS.md rule to preserve distinct outcomes. A missing Status therefore fails `results.py validate` but `next` prints `rebuild`. If the user wanted every validate failure to stop, step 3 and the chain docs change.
- The live run (step 6) depends on the model obeying an instruction to drop `## Status`. If it refuses, that arm is recorded unverified.
- The live run also spends real model calls from inside a builder run.
- Another lane adding a malformed tracked result in an open ticket dir would turn the step 1 history criterion red.
- Steps 1 to 6 are uncommitted while later steps run, so each scope allow-list is cumulative.
