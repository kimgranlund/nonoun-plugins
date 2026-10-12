## Task goal
A solo L2 ticket whose acceptance criteria are all mechanical and each carry an observed-red control closes on green criteria with no independent verifier; the verifier runs by exception. A measured pilot over the next 20 qualifying tickets decides whether it stays.

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
