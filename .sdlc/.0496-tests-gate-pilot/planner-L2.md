<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A solo L2 ticket whose criteria are all command spans with pre-edit red controls closes on its own green checks through a new `tests-gate` skip class in `verify_scope.py`, on only where `.sdlc/config` says `tests_gate: pilot`, with the gate visible in `solo_stats.py`.

## Step 1: tests-gate class in verify_scope.py, close integration, pilot flag
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: none.

Targets: `plugins/sdlc-lite/scripts/verify_scope.py` (`scope`, `main`, `selftest`, module docstring), `plugins/sdlc-lite/scripts/tickets.py` (`docs_waiver`, `note_docs_waiver`, the two call sites in close, the selftest), `.sdlc/config`.

Settled interface for `verify_scope.py`:
- Signature `scope(root, base, handoff=None, report=None, need_report=False)`, still returning `(ok, detail)`. The CLI gains `--report FILE`, which sets `need_report`.
- Evaluation order:
  1. The existing `verifier requested by <handoff>` check, unchanged.
  2. `no changes against <base>`, unchanged.
  3. The docs-only path: an all-docs diff behaves exactly as today.
  4. Only when a non-docs path exists, `handoff` is given, and `<root>/.sdlc/config` has a line matching `tests_gate: pilot`, evaluate tests-gate. Read the key with a local regex in the style of `CONFIG_RE` at `tickets.py:272`; do not import `lanes.py`.
  5. In every other case return `(False, <first non-docs path>)`, byte-identical to today. The existing selftest pins `scope(r, b) == (False, 'tool.py')`, and the `(docs-only)` cases of `tickets.py selftest` run in repos with no pilot flag.
- All tests-gate conditions pass: `(True, 'tests-gate')`. Otherwise `(False, 'tests-gate: <label>: <detail>')` for the first unmet condition, checked in this order with these exact labels:
  1. `level`: the handoff front matter `size:` is not `L2` (legacy `M` counts as L2).
  2. `lane`: the last `- lane:` line of `<handoff dir>/skips.md` is not `solo`, or the file or line is missing. Read it with a small regex; do not import `steps.py` at module top.
  3. `criteria`: the criteria set is the bullets under `## Acceptance criteria` plus the `- Done when:` lines, outside fences (the rule of `results.criterion_spans`, `results.py:262`). Unmet when the set is empty or any bullet has no command span per `steps.line_spans`.
  4. `red-control`: `redck.red_items(handoff)` is empty, or for any `(red)` span the newest `type: control` entry in `<handoff dir>/red-checkpoint.jsonl` whose `criterion_sha256` equals `redck.criterion_hash(line, span)` is missing, or lacks `phase: pre-edit`, or lacks `result: red`. Import `redck` inside the function. The attempt id is not checked.
  5. `protected-path`: a changed path outside `.sdlc/` has a path component `agents`, `hooks` or `adapters`; or a basename `levels.json`, `models.json`, `run.sh`, `dispatch.py`, `results.py` or `gate_lock.py`; or a component containing, case-insensitive, `security`, `secret`, `auth`, `credential` or `permission`.
  6. `size`: over the changed paths outside `.sdlc/`, more than 8 files, or more than 300 changed lines. Changed lines are added plus deleted from `git diff --numstat --no-renames <base>`, plus the line count of each untracked file; a binary file counts as over.
  7. `shared-name`: collect tokens from the `-` lines of `git diff -U0 --no-renames <base>` outside `.sdlc/` that appear on no `+` line of that diff. Token classes: quoted literals of 4 or more characters (single, double or backtick quotes); names defined on the line (`def X`, `class X`, `function X`, a line-start `X =`, a JSON `"key":`, a `--flag`); and the basename of each deleted file. Unmet when `git grep -F -l` for a token finds a tracked file that is not a changed path and not under `.sdlc/` or `docs/reports/`. Detail is `<token> in <path>`. An added name has no dependents and is not searched.
  8. `report`: evaluated only when `need_report` is true. Unmet when `report` is missing or unreadable, or any span of `results.criterion_spans(handoff text)` lacks a report line holding the span in backticks and `exit 0`.
- The ninth condition is the existing verifier line (`verifier requested by`).
- A diff failing a tests-gate condition is never docs-only, so it prints the tests-gate reason and exits 1.
- Solo calls the CLI without `--report`, because `solo_run.py` writes the report file only after solo ends (T-0485, commit 854575ab). `tickets.py close` is the authority and always requires the report.

Selftest in `verify_scope.py`. Use these `expect` name prefixes:
- `tests-gate ok: ` for the positive case: a qualifying L2 solo fixture repo with the pilot config, a handoff, a `skips.md`, a `red-checkpoint.jsonl` and a report returns `(True, 'tests-gate')`, and the CLI with `--report` prints `tests-gate` and exits 0.
- `tests-gate red: <label>` for one negative control per condition. Each flips exactly one property of the positive fixture and asserts the detail starts with `tests-gate: <label>` (for the verifier line, `verifier requested by`). The `red-control` condition gets two controls: a `retrospective` entry, and no `(red)` criterion.
- `tests-gate red: pilot off` asserts that removing the config line returns the legacy first non-docs path.

`tickets.py`:
- Generalize `docs_waiver(d)` to return `(base, klass)` with klass `docs-only` or `tests-gate`, or `None`.
- Call `verify_scope.scope(top, base, handoff, report=<path or None>, need_report=True)`. The report path is the `file` of the last `role: solo` row in `<task dir>/runs.jsonl`, resolved in the task dir.
- The skip line keeps the form at `tickets.py:2014` with the class in the reason: `- skip: verifier; step: all; reason: tests-gate diff against <base12> (verify_scope.py); decided: tickets.py close`. The docs-only line is unchanged; the selftest at `tickets.py:4943` pins it.
- That skips.md line is the record of the skip.
- Add selftest cases named with the prefix `(tests-gate)`: a qualifying pilot ticket closes with no verifier result and writes the line; the same ticket without the config line still needs a verifier; a report missing one exit line still needs a verifier.

`.sdlc/config`: append the line `tests_gate: pilot`.

Dependents (search: `git grep -n "verify_scope\|docs_waiver\|docs-only" -- plugins scripts docs/references`):
- `tickets.py` is in this step.
- `agents/solo.md`, its generated copies, `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/AGENTS.md` are step 2.
- `plan_check.py` and `skills/clarify/evals/*` only quote the T-0429 ticket text and stay untouched.
- `results.py` is read, not changed.

Focused checks: `verify_scope.py selftest`, `tickets.py selftest` (about 65 s), `redck.py selftest`.
### Acceptance criteria
- `f=plugins/sdlc-lite/scripts/verify_scope.py; python3 "$f" selftest && for l in "tests-gate: level" "tests-gate: lane" "tests-gate: criteria" "tests-gate: red-control" "tests-gate: report" "tests-gate: shared-name" "tests-gate: size" "tests-gate: protected-path" "verifier requested by"; do grep -qF "$l" "$f" || exit 1; done`
- `f=plugins/sdlc-lite/scripts/verify_scope.py; grep -qF "tests-gate ok: " "$f" && grep -qF "tests-gate red: pilot off" "$f" && test "$(grep -c "tests-gate red: " "$f")" -ge 10`
- `out=$(python3 plugins/sdlc-lite/scripts/verify_scope.py "$SDLC_BASE_SHA" --handoff .sdlc/0496-tests-gate-pilot/handoff.md); printf "%s\n" "$out" | grep -qF "tests-gate: level"`
- `grep -qxF "tests_gate: pilot" .sdlc/config`
- `f=plugins/sdlc-lite/scripts/tickets.py; grep -qF "(tests-gate)" "$f" && grep -qF "reason: tests-gate diff against" "$f" && python3 "$f" selftest`
- `python3 plugins/sdlc-lite/scripts/redck.py selftest`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/tickets.py)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Step 2: solo.md rule, gate field in solo_stats.py, references, gates green
level: L2
guard timeout: 2700
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1.

`plugins/sdlc-lite/agents/solo.md` (one writer). Both additions are affirmative sentences, so the prompt_lint P-6 prohibition count stays at or below base (19 now).
- Loop step 2, the `(red)` sentence: after `specgate.py red` exits 0, solo also runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/redck.py" record <task dir>/handoff.md` before the first edit. It writes each control to `red-checkpoint.jsonl`. `specgate.py red` writes no record (`specgate.py:153`), and the tests-gate `red-control` condition reads that file.
- `## Verification`: one line stating that when `verify_scope.py` prints `tests-gate` and exits 0, solo ends its report with `verify: skipped (tests-gate; criteria green, red controls pre-edit)` and still lists every span with its exit code, which `tickets.py close` re-checks against the report file.
- Regenerate with `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. `check.py` compares `solo.md` to `agents/solo-L<n>.md` byte for byte, and the three `adapters/codex/agents/sdlc-solo-l<n>.toml` files carry it. Never edit generated files by hand.

`plugins/sdlc-lite/scripts/solo_stats.py`:
- Add count keys `gate_tests_only` and `gate_verifier`.
- `gate_tests_only`: the ticket's `skips.md` holds `reason: tests-gate diff against` (the line step 1 writes).
- `gate_verifier`: the ticket has at least one verifier round, which is the existing `verified` condition.
- `render` prints two lines that start `gate: tests-only` and `gate: verifier`, each followed by spaces and the count.
- `--json` carries both keys.
- Update the docstring key list.
- Add selftest cases for both values, including a control where the skip line is absent.

References:
- `docs/references/sdlc-internals.md`: in the `verify_scope.py` section (line 57), add the tests-gate class, its nine conditions, the pilot flag and the `--report` option. In the `solo_stats.py` section (line 77), add the two keys.
- `plugins/sdlc-lite/AGENTS.md` line 59: name the tests-gate cases next to the docs-only skip check.

Not changed: `lanes.py` (see Assumptions) and `docs/kpi/005-solo-first-pass-rate.md`.

Then run every gate below, plus `python3 scripts/check-packaging.py` and `git diff --check`, and fix any red that step 1 or this step introduced.
### Acceptance criteria
- `f=plugins/sdlc-lite/agents/solo.md; grep -qF "tests-gate" "$f" && grep -qF "redck.py" "$f" && grep -qF "verify: skipped (tests-gate" "$f"`
- `f=plugins/sdlc-lite/scripts/solo_stats.py; python3 "$f" selftest && grep -qF "gate: tests-only" "$f" && grep -qF "gate: verifier" "$f"`
- `out=$(python3 plugins/sdlc-lite/scripts/solo_stats.py stats .) && printf "%s\n" "$out" | grep -qE "^gate: tests-only +[0-9]+" && printf "%s\n" "$out" | grep -qE "^gate: verifier +[0-9]+"`
- `grep -qF "tests-gate" docs/references/sdlc-internals.md && grep -qF "tests-gate" plugins/sdlc-lite/AGENTS.md`
- (guard) `t=$(mktemp); git show "$SDLC_BASE_SHA":plugins/sdlc-lite/agents/solo.md > "$t"; b=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py "$t" | sed -n "s/.*prohibitions \([0-9]*\),.*/\1/p"); n=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py plugins/sdlc-lite/agents/solo.md | sed -n "s/.*prohibitions \([0-9]*\),.*/\1/p"); test -n "$b" && test -n "$n" && test "$n" -le "$b"`
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 plugins/sdlc-lite/scripts/prompt_lint.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/solo_stats.py -e plugins/sdlc-lite/agents/solo.md -e plugins/sdlc-lite/agents/solo-L1.md -e plugins/sdlc-lite/agents/solo-L2.md -e plugins/sdlc-lite/agents/solo-L3.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l1.toml -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l2.toml -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l3.toml -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Assumptions
- unresolved: where `lanes.py` prints `gate: tests-only` or `gate: verifier`: `lanes.py list` prints one row per lane and has no per-ticket surface (`lanes.py:1172`), and the Done-when tests only `solo_stats.py`. The user settles it by naming the surface (a per-lane column in `lanes.py list`, the `/report` lanes view, or drop it). This plan leaves `lanes.py` untouched, so "drop it" needs no replan.
- The nine conditions are level, lane, criteria, red-control, report, shared-name, size, protected-path and the verifier line. The pilot flag is a tenth control whose off state keeps today's output: verified by the handoff's Do list, and by the existing selftest pin `scope(r, b) == (False, 'tool.py')` in `plugins/sdlc-lite/scripts/verify_scope.py`.
- A ticket with no `(red)` criterion never qualifies: verified by the handoff Constraints line "The skip never applies when a criterion lacks an observed-red control", read in the safe direction it names.
- Solo must run `redck.py record`, because `specgate.py red` writes no checkpoint: verified by reading `cmd_red` at `plugins/sdlc-lite/scripts/specgate.py:153` and `cmd_record` in `plugins/sdlc-lite/scripts/redck.py`.
- The report condition is enforced at close, not in solo's own call: verified by commit 854575ab, where `solo_run.py` writes `solo-L<n>-<attempt>.md` only after solo returns.
- The mechanical rules for shared name and security-sensitive paths in step 1 are this plan's reading of the handoff words ("added, renamed or removed", `git grep`, "no dependent outside the diff"), erring toward verifier still needed: verified by the handoff Intent only, not by code.
- The skips.md line is the close-note record of a skip, as for T-0429: verified by `plugins/sdlc-lite/scripts/tickets.py:2014`.
- Probes: every new-behavior criterion exited 1 on the current tree because the behavior is absent, and every guard except `check.sh` exited 0: verified by running `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/g/.worktrees/tmp/0496-planner-L2/probe.sh`. `redck.py selftest` was not probed.
- Guard red states: the scope guard went red against `HEAD~1`; the prohibition guard went red against a 20-line base (8 against 19); the four named gates went red in a `git archive` copy with one unregenerated line added to `solo.md`. In that copy `check.py` failed on a file the copy lacks, so its red on generated-agent drift was not isolated.
- `guard timeout: 2700` is the value seven earlier plans used for `check.sh`: verified by `git grep -h "guard timeout" -- '.sdlc/**/planner-*.md'`.

## Risks
- `check.sh` was not run at plan time. Its last recorded PASS is at commit 20f2900c (`docs/reports/2026-10-12-release-0-22-5.md`), one merge behind HEAD; a red already at HEAD comes back as `inherited red`.
- `tickets.py close` evaluates the diff against the recorded base in the tree where close runs. On an integration branch that already holds other lanes, the `size` and `shared-name` conditions can fail for a ticket that qualified in its lane, so the pilot may skip less often than intended. The docs-only skip has the same property today.
- A sub-agent solo lane may have no report file in `runs.jsonl`; the `report` condition then keeps the verifier. This is the safe direction, but it lowers the pilot's reach.
- The shared-name rule can be noisy (a removed quoted literal that also occurs elsewhere), which lowers the qualifying rate; it never skips a verifier wrongly because of noise.
- K-005 for pilot tickets is not defined by this plan: a tests-only ticket has no verifier round, so `first_pass / verified` does not cover it. Rework after close (a reopen, or a follow-up within 7 days) is not built here; the Done-when asks only for the gate field. Both need a follow-up ticket before the 20-ticket readout.
- The red-control check ignores attempt ids, so a control recorded by an earlier attempt on the same criterion text counts.
- A scratch copy and the probe script remain under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/g/.worktrees/tmp/0496-planner-L2`. The worktree hook denied `git worktree add` (`SDLC_TMP_WORKTREES` is unset), so no worktree was created, and nothing was deleted.
