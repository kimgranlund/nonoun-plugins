<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Add `plugins/sdlc-lite/scripts/evals.py` and a tracked `.sdlc/evals/` folder holding entry files, a baseline eval, and `table-lock.json`. After this, `check.py` fails whenever the model table in `run.sh` or `models.json` changes without a newer cited eval. No model or effort default changes.

## Step 1: Add evals.py with the eval format, the table hash, add, list, check, lock, and its selftest
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none.

Create `plugins/sdlc-lite/scripts/evals.py` with these properties:
- Executable (`chmod +x`), with the shebang `#!/usr/bin/env python3`.
- Standard library only and self-contained. It imports no other plugin script, `tickets.py` included, so a patched copy runs alone in a temp dir for the negative controls.
- Python 3.9 compatible, because the host runs 3.9.6: no `X | Y` annotations and no `match`.
- No em dashes.
- The module docstring documents the format and the CLI.
- Importing the module prints and runs nothing: `main()` is called only under `if __name__ == '__main__'`.

Wire the selftest into `plugins/sdlc-lite/scripts/check.sh`:
- add the line `python3 "$root/scripts/evals.py" selftest || fail=1` after the `results.py` line
- add `evals.py` to the header comment's list of selftests

Global options come before the subcommand, as in `tickets.py --root .sdlc <cmd>` (tickets.py:3644):
- `--root DIR` is the `.sdlc` folder, default `.sdlc` in the cwd. Evals live in `<root>/evals/`. The repo dir is the resolved `<root>/..`. Evidence paths and the lock's paths are relative to the repo dir, in posix form. Resolve both sides before taking a relative path, because macOS `mktemp -d` paths sit under the `/var` to `/private/var` symlink.
- `--plugin DIR` is the dir holding `scripts/run.sh` and `adapters/codex/models.json`. The default is the parent of this script's dir. evals.py only reads these two files and never writes them.

Eval file:
- The name matches `\d{4}-[a-z0-9][a-z0-9-]*\.md`, directly in `<root>/evals/`. `AGENTS.md`, `CLAUDE.md`, and non-`.md` files there are not evals.
- The text is a `---` line, one `key: value` line per field, a `---` line, then the body.
- The parser is evals.py's own: bare values, no quoting, no comments. It reports `bad front matter line <n>` for a non-blank line without `: `, and `duplicate field <name>` for a repeated key. Only `evidence` may hold a one-line `[a, b, c]` list.

`FIELDS` is this tuple, in this order. Validation reports the first problem in this order:
- `role`: regex `[a-z][a-z-]*`. It is syntactic, so renaming a role never invalidates an old record.
- `level`: `L1` to `L5`, or `all`.
- `model`: regex `[A-Za-z0-9][A-Za-z0-9._-]*`. Any model id passes, including one not in the table, and `all` matches.
- `effort`: regex `[a-z]+`. There is no fixed list, because Codex advertises `max` and `ultra` (`docs/validation/codex-account-models-2026-09-30.md`).
- `host`: `claude`, `codex`, or `all`.
- `task_set`: any non-empty one-line text, a short name or a path, never checked for existence.
- `pass_rate`: `<passed>/<total>`, both non-negative integers, with passed <= total. `0/0` is allowed.
- `cost_usd`: a non-negative number matching `\d+(\.\d+)?`, or `unknown`.
- `date`: `YYYY-MM-DD` that `datetime.date.fromisoformat` accepts.
- `evidence`: one item, or a `[a, b, ...]` list of one or more items. Each item is one of these:
  - an `http://` or `https://` URL with no whitespace, checked for form only and never fetched, because check.sh runs offline
  - a relative path with no `..` segment that exists under the repo dir

`all` in role, level, model, effort, and host marks a record that covers the whole table, which is what the step 2 baseline needs. The body needs a `## Method` line and a later `## Result` line. Each must have at least one non-blank line before the next `## ` line.

Reason strings, exact text:
- `no front matter`
- `missing field <name>`, for an absent or empty field
- `bad field <name>: <value> (want <expectation>)`
- `unknown field <name>`
- `duplicate field <name>`
- `bad front matter line <n>`
- `missing ## Method` and `missing ## Result`
- `## Result before ## Method`
- `empty ## Method` and `empty ## Result`
- from `validate_eval` only: `not an eval file name (NNNN-<slug>.md)` and `no such file`

Canonical table text and hash. This is the only definition; step 2 documents it in `.sdlc/evals/AGENTS.md`.
1. Find every match, with `re.M`, of the regex below in `<plugin>/scripts/run.sh`. It is the regex `check.py` already parses the table with (check.py:63) and finds 19 rows today.
2. Format each match as `<role>:<level> <model> <effort>`, sort with `sorted()`, and end each row with `\n`.
3. Append `json.dumps(json.load(models.json), sort_keys=True, separators=(',', ':'))` and a `\n`.
4. `table_sha256` is the sha256 hex of that text in UTF-8.

Zero parsed rows is an error naming run.sh. Whitespace and layout edits leave the hash alone; any change to a role, level, model, effort, or models.json value changes it.

```
^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)
```

The lock is `<root>/evals/table-lock.json`. Its keys are exactly these three:
- `eval`: the repo-relative path of the cited eval
- `previous_eval`: the eval it replaced, or `null`
- `table_sha256`

It is written as `json.dumps(lock, indent=2, sort_keys=True) + '\n'`, and only by `lock`.

Python API. check.py uses the CLI, and T-0186's `proposals.py accept` will call `validate_eval`:
- `FIELDS`
- `canonical_table(plugin)` and `table_sha256(plugin)`
- `validate_text(text, repo)` and `validate_eval(path, repo)`, each returning `None` or one reason string
- `check_problems(root, plugin)`, returning the list of problem lines

CLI exit codes: 0 for ok, 1 for a refusal or a failed check, 2 for a usage error from argparse.

`add`:
- Usage: `add <slug> --role R --level L --model M --effort E --host H --task-set S --pass-rate P/T --cost-usd C --date D --evidence X [--evidence Y ...] --method TEXT --result TEXT`.
- argparse treats every option as optional. The composed text goes through `validate_text`, so a missing option reports `missing field <name>`, or `empty ## Method` for a missing method.
- The slug must match `[a-z0-9][a-z0-9-]*`, else the reason is `bad slug <slug>`.
- Front matter values may not hold a newline. Method and result text is written as given.
- The file holds the front matter in FIELDS order with only the options given. One evidence item is written bare; several are written as `[a, b]` on one line. Then come `## Method`, a blank line, the method text, a blank line, `## Result`, a blank line, and the result text.
- The number is one more than the highest `NNNN` among `<root>/evals/*.md` names, or `0000` when there is none.
- On a refusal it prints `evals.py: <reason>` on stderr, exits 1, and writes nothing, not even `<root>/evals/`.
- On success it creates `<root>/evals/` if needed and prints the new file's repo-relative path.

`list`:
- Prints one tab-separated line per eval file, by name: name, date, host, role, level, model, effort, pass_rate, cost_usd.
- An invalid file prints `<name>\tinvalid: <reason>`.
- Always exits 0.

`check`:
- Prints each problem as one stdout line, then `evals check: FAIL`, and exits 1.
- Otherwise it prints `evals check: ok (<n> evals, lock cites <eval>)` and exits 0.
- Subjects are repo-relative. The problems:
  - `<root>/evals` missing: `.sdlc/evals: missing`
  - a `.md` file without an eval name: `<file>: not an eval file name (NNNN-<slug>.md)`
  - an invalid eval: `<file>: <reason>`
  - two files with the same number: `<file>: number NNNN is used twice`
  - no lock: `<lock>: missing; add an eval, then run evals.py lock --eval <file>`
  - a malformed lock (not JSON, keys not exactly the three, `table_sha256` not 64 hex characters, a path that is not a string, or `previous_eval` neither a string nor null): `<lock>: malformed: <why>`
  - a different hash: `<lock>: model table changed: sha256 <current> is not the locked <locked>; add an eval, then run evals.py lock --eval <file>`
  - `eval` not a valid eval in `<root>/evals/`: `<lock>: lock names no valid eval: <path>: <reason>`
  - `previous_eval` set but invalid: `<lock>: previous_eval <path>: <reason>`
  - `previous_eval` set and `eval`'s date not later than its date, which also covers `eval` equal to `previous_eval`: `<lock>: eval <path> date <d> is not later than previous_eval <path> date <d0>; a changed table needs a new eval`

`lock --eval PATH`:
- `--eval` is required by argparse, so a bare `lock` exits 2.
- PATH resolves from the cwd. It must exist, else `evals.py: no such eval: <PATH>`. It must also sit directly in `<root>/evals/`, have an eval name, and pass `validate_eval`.
- With no lock file, it writes `{eval: PATH, previous_eval: null, table_sha256: <current>}`.
- With a lock file, it refuses a malformed lock and a lock whose `eval` is invalid. It also refuses a PATH whose date is not later than the cited eval's date: `evals.py: eval <PATH> date <d> is not later than the cited eval <old> date <d0>; a changed table needs a new eval`. Otherwise it writes `{eval: PATH, previous_eval: <old eval>, table_sha256: <current>}`.
- Every refusal exits 1 and leaves the lock byte-identical.

`hash` prints `table_sha256(plugin)` and nothing else.

`check` and `lock` both call one helper for the not-later rule. Three rules are each one `if` line ending in a marker comment, so the negative controls can remove them:
- `# rule: hash` marks the hash comparison in `check_problems`.
- `# rule: date` marks the not-later comparison in that helper.
- `# rule: required` marks the missing-field test in `validate_text`. The format check runs only on a present value, so removing this rule lets a missing field through instead of crashing.

`selftest` uses temp dirs only:
- A temp project `<t>/.sdlc` with an evidence file `<t>/docs/e.md`.
- A temp plugin `<t>/plugin` holding copies of the `--plugin` dir's `scripts/run.sh` and `adapters/codex/models.json`.
- Every command runs as a subprocess of this file, with explicit `--root` and `--plugin`.
- It prints `ok: <name>` per case, then `evals selftest: PASS`, and exits 0. Otherwise it prints `FAIL: <name>: <detail>` per miss, then `evals selftest: FAIL`, and exits 1.

The case names, exactly:
1. `add then list then check pass on a temp project`. It asserts the file `0000-<slug>.md`, each front matter line, both body sections, the list line, and the lock keys.
2. `add refuses each missing field by name`. One run per FIELDS name: exit 1, `missing field <name>`, no file written.
3. `add refuses each malformed field by name`. One bad value per field: exit 1, `bad field <name>`, no file written.
4. `add writes the next number`. A second add writes `0001-...`.
5. `check refuses a hand-written eval with a missing field`
6. `a stale lock makes check fail naming the model table`. With one model row changed in the temp run.sh: exit 1 and `model table changed`.
7. `lock without --eval is refused and leaves the lock unchanged`
8. `lock with the cited eval again is refused as not later`
9. `lock with an eval path that does not exist is refused`
10. `lock with a valid newer eval passes and stamps the lock`. It asserts `eval`, `previous_eval`, and that `table_sha256` equals the `hash` output, then that `check` exits 0.
11. `check refuses a lock whose eval is not later than previous_eval`
12. `check refuses a lock that names a missing eval`
13. `evals.py never writes run.sh or models.json`. It compares the sha256 of the real and the temp tables before and after every command.
14. `negative control: evals.py without the hash comparison passes a stale lock`
15. `negative control: evals.py without the date rule passes a reused eval`, using case 11's lock.
16. `negative control: evals.py without the required-field check accepts a missing field`. Case 2's add without `--date` exits 0 and writes the file.

Each negative control works the same way:
1. Write a copy of this file's text to a temp dir, with the marked line's condition replaced by `False` (a regex on the whole line, from `if <cond>:` to `if False:`).
2. Assert that exactly one line matched, so a rule that moved fails the control loudly instead of passing it.
3. Run the copy on the case's fixture.

Build each marker string by concatenation (`'# rule' + ': hash'`), so the selftest's own text holds no copy of it.

Focused checks: `python3 plugins/sdlc-lite/scripts/evals.py selftest` and the criteria below.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/evals.py selftest`
- `out=$(python3 plugins/sdlc-lite/scripts/evals.py selftest) && for n in "add then list then check pass on a temp project" "add refuses each missing field by name" "add refuses each malformed field by name" "add writes the next number" "check refuses a hand-written eval with a missing field" "a stale lock makes check fail naming the model table" "lock without --eval is refused and leaves the lock unchanged" "lock with the cited eval again is refused as not later" "lock with an eval path that does not exist is refused" "lock with a valid newer eval passes and stamps the lock" "check refuses a lock whose eval is not later than previous_eval" "check refuses a lock that names a missing eval" "evals.py never writes run.sh or models.json" "negative control: evals.py without the hash comparison passes a stale lock" "negative control: evals.py without the date rule passes a reused eval" "negative control: evals.py without the required-field check accepts a missing field"; do printf '%s\n' "$out" | grep -qxF "ok: $n" || exit 1; done`
- `test "$(python3 plugins/sdlc-lite/scripts/evals.py hash)" = "$(python3 -c 'import re,json,hashlib; r=open("plugins/sdlc-lite/scripts/run.sh").read(); rows=sorted("%s:%s %s %s" % m for m in re.findall(r"^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)", r, re.M)); j=json.dumps(json.load(open("plugins/sdlc-lite/adapters/codex/models.json")), sort_keys=True, separators=(",", ":")); print(hashlib.sha256(("".join(x + "\n" for x in rows) + j + "\n").encode()).hexdigest())')"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" "$t/docs" && echo e >"$t/docs/e.md" && E=plugins/sdlc-lite/scripts/evals.py && python3 "$E" --root "$t/.sdlc" add first --role builder --level L2 --model opus --effort low --host claude --task-set bench --pass-rate 3/4 --cost-usd 1.5 --date 2026-10-02 --evidence docs/e.md --method m --result r >/dev/null && grep -qx 'pass_rate: 3/4' "$t/.sdlc/evals/0000-first.md" && python3 "$E" --root "$t/.sdlc" lock --eval "$t/.sdlc/evals/0000-first.md" >/dev/null && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(not (d["eval"] == ".sdlc/evals/0000-first.md" and d["previous_eval"] is None and len(d["table_sha256"]) == 64))' "$t/.sdlc/evals/table-lock.json" && python3 "$E" --root "$t/.sdlc" list | grep -q '^0000-first\.md' && python3 "$E" --root "$t/.sdlc" check >/dev/null`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && out=$(python3 plugins/sdlc-lite/scripts/evals.py --root "$t/.sdlc" add x --role builder --level L1 --model sonnet --effort low --host claude --task-set s --pass-rate 1/1 --cost-usd unknown --evidence https://example.com/e --method m --result r 2>&1); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'missing field date' && test ! -e "$t/.sdlc/evals"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && out=$(python3 plugins/sdlc-lite/scripts/evals.py --root "$t/.sdlc" add x --role builder --level L1 --model sonnet --effort low --host claude --task-set s --pass-rate 1/1 --cost-usd unknown --date 2026-10-02 --evidence docs/nope.md --method m --result r 2>&1); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'bad field evidence' && test ! -e "$t/.sdlc/evals"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && out=$(python3 plugins/sdlc-lite/scripts/evals.py --root "$t/.sdlc" add x --role builder --level L1 --model sonnet --effort low --host gcp --task-set s --pass-rate 5/4 --cost-usd unknown --date 2026-13-01 --evidence https://example.com/e --method m --result r 2>&1); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'bad field host'`
- `t=$(mktemp -d) && mkdir -p "$t/p/scripts" "$t/p/adapters/codex" "$t/.sdlc" && cp plugins/sdlc-lite/scripts/run.sh "$t/p/scripts/" && cp plugins/sdlc-lite/adapters/codex/models.json "$t/p/adapters/codex/" && E=plugins/sdlc-lite/scripts/evals.py && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" add base --role all --level all --model all --effort all --host all --task-set s --pass-rate 0/0 --cost-usd unknown --date 2026-09-30 --evidence https://example.com/x --method m --result r >/dev/null && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0000-base.md" >/dev/null && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" check >/dev/null && python3 -c 'import re,sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"(builder:L1\)\s*model=)[\w-]+", r"\g<1>evals-probe", p.read_text()))' "$t/p/scripts/run.sh" || exit 1; out=$(python3 "$E" --root "$t/.sdlc" --plugin "$t/p" check); test "$?" -eq 1 || exit 1; printf '%s\n' "$out" | grep -qF 'model table changed'`
- `t=$(mktemp -d) && mkdir -p "$t/p/scripts" "$t/p/adapters/codex" "$t/.sdlc" && cp plugins/sdlc-lite/scripts/run.sh "$t/p/scripts/" && cp plugins/sdlc-lite/adapters/codex/models.json "$t/p/adapters/codex/" && E=plugins/sdlc-lite/scripts/evals.py && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" add base --role all --level all --model all --effort all --host all --task-set s --pass-rate 0/0 --cost-usd unknown --date 2026-09-30 --evidence https://example.com/x --method m --result r >/dev/null && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0000-base.md" >/dev/null && python3 -c 'import re,sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"(builder:L1\)\s*model=)[\w-]+", r"\g<1>evals-probe", p.read_text()))' "$t/p/scripts/run.sh" && cp "$t/.sdlc/evals/table-lock.json" "$t/lock.before" || exit 1; python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock >/dev/null 2>&1; test "$?" -eq 2 || exit 1; out=$(python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0000-base.md" 2>&1); test "$?" -eq 1 || exit 1; printf '%s\n' "$out" | grep -qF 'is not later than' || exit 1; out=$(python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0009-none.md" 2>&1); test "$?" -eq 1 || exit 1; printf '%s\n' "$out" | grep -qF 'no such eval' || exit 1; cmp -s "$t/lock.before" "$t/.sdlc/evals/table-lock.json"`
- `t=$(mktemp -d) && mkdir -p "$t/p/scripts" "$t/p/adapters/codex" "$t/.sdlc" && cp plugins/sdlc-lite/scripts/run.sh "$t/p/scripts/" && cp plugins/sdlc-lite/adapters/codex/models.json "$t/p/adapters/codex/" && E=plugins/sdlc-lite/scripts/evals.py && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" add base --role all --level all --model all --effort all --host all --task-set s --pass-rate 0/0 --cost-usd unknown --date 2026-09-30 --evidence https://example.com/x --method m --result r >/dev/null && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0000-base.md" >/dev/null && python3 -c 'import re,sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"(builder:L1\)\s*model=)[\w-]+", r"\g<1>evals-probe", p.read_text()))' "$t/p/scripts/run.sh" && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" add next --role builder --level L1 --model evals-probe --effort low --host claude --task-set s --pass-rate 1/1 --cost-usd 0.5 --date 2026-10-03 --evidence https://example.com/y --method m --result r >/dev/null && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" lock --eval "$t/.sdlc/evals/0001-next.md" >/dev/null && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(not (d["eval"] == ".sdlc/evals/0001-next.md" and d["previous_eval"] == ".sdlc/evals/0000-base.md"))' "$t/.sdlc/evals/table-lock.json" && test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["table_sha256"])' "$t/.sdlc/evals/table-lock.json")" = "$(python3 "$E" --plugin "$t/p" hash)" && python3 "$E" --root "$t/.sdlc" --plugin "$t/p" check >/dev/null`
- `out=$(python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import evals; sys.exit(not (evals.FIELDS == ("role", "level", "model", "effort", "host", "task_set", "pass_rate", "cost_usd", "date", "evidence") and callable(evals.validate_eval) and callable(evals.validate_text) and callable(evals.table_sha256) and callable(evals.check_problems)))' 2>&1) && test -z "$out"`
- `test -x plugins/sdlc-lite/scripts/evals.py`
- `grep -qF 'scripts/evals.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`

## Step 2: Add the .sdlc/evals folder: entry files, the baseline eval, the lock, and the router line
level: L2
### Read first
- `.sdlc/AGENTS.md`
### Do
Depends on: step 1. Run from the repository root. Change nothing outside `.sdlc/evals/` and `.sdlc/AGENTS.md`, and use no em dashes.

1. Write `.sdlc/evals/CLAUDE.md` as exactly `@AGENTS.md` and a newline.
2. Write `.sdlc/evals/AGENTS.md`. It must be self-contained, so a role that reads only this file can add, list, check, and lock (handoff Common rules: no skill is added). Its sections, in order:
   - `# Evals`, then one paragraph:
     - The folder holds dated records of model and effort experiments.
     - A change to a model or effort row in `plugins/sdlc-lite/scripts/run.sh` (the `case "$role:$level"` rows) or to `plugins/sdlc-lite/adapters/codex/models.json` lands only with a new eval and `evals.py lock`, else `python3 plugins/sdlc-lite/scripts/check.py` fails.
     - Model and effort defaults stay user decisions; an eval never changes one.
     - Run commands from the repository root.
   - `## File format`: the name rule, each FIELDS entry with its rule from step 1, what `all` means, the evidence forms, the `## Method` and `## Result` body, and one example eval.
   - `## Table lock`:
     - the three keys
     - the canonical text, spelled out as in step 1: the `role:level model effort` rows from the run.sh regex, sorted, one per line, then models.json as `json.dumps(..., sort_keys=True, separators=(',', ':'))` and a newline, hashed to sha256 hex
     - the rules that `evals.py check` and `check.py` enforce
   - `## Procedures`:
     - Add an eval: `python3 plugins/sdlc-lite/scripts/evals.py add ...` with every option.
     - List: `evals.py list`.
     - Check: `evals.py check`.
     - Hash: `evals.py hash`.
     - Change the model table: run the experiment, `evals.py add` it, change the row (a user decision), `evals.py lock --eval .sdlc/evals/<file>`, then run `check.py`.
     - Never edit `table-lock.json` by hand.
   - `## Limits`:
     - URLs are checked for form only.
     - A hand edit of `table_sha256` alone is not detected, so the lock is reviewed in the diff.
     - The date rule allows one table change per day per lock chain.
     - Eval numbers are not unique across parallel worktrees; `check` reports a duplicate after a merge.
3. Create the baseline:
   - The command:

     ```
     python3 plugins/sdlc-lite/scripts/evals.py add baseline --role all --level all --model all --effort all --host all --task-set pre-eval-baseline --pass-rate 0/0 --cost-usd unknown --date 2026-09-30 --evidence docs/validation/haiku-alias-2026-09-30.md --evidence docs/validation/planner-l3-opus-2026-09-30.md --evidence docs/validation/codex-account-models-2026-09-30.md --method "<method>" --result "<result>"
     ```

   - It writes `.sdlc/evals/0000-baseline.md`, because the folder holds no eval yet.
   - The date is the date of the three deciding records, so a later eval dated 2026-10-01 or after can replace it.
   - Method: no experiment was run. This record marks the model table, as it stood when evals.py landed, as the pre-eval baseline, decided by the three dated records cited as evidence.
   - Result, one line per record:
     - haiku-alias: the Claude scout runs the pinned `claude-haiku-4-5`, because the `haiku` alias ran Sonnet 5.5.
     - planner-l3-opus: Claude planner L3 moved from Fable xhigh to Opus xhigh.
     - codex-account-models: these are the Codex defaults in `models.json`, with `gpt-6.1-sol` as the verifier alternate.
   - Close the Result with this line: no pass rate or cost was measured, and every later table change cites a newer eval.
   - Afterwards edit only the body text, if anything, and rerun `evals.py check`.
4. Run `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0000-baseline.md`. It writes `.sdlc/evals/table-lock.json` with `previous_eval` null.
5. In `.sdlc/AGENTS.md`, append the lines below after the `<!-- sdlc-lite:managed:end -->` line, outside the generated block. Do not edit inside the block.

   ```

   ## Other records

   - Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
   ```

   The line goes outside the block, not into `tickets.py`'s `ROUTER_TEMPLATE`, for two reasons:
   - `tickets.py` keeps every byte outside the markers (its docstring, line 140). A temp-root probe showed that a line appended after the end marker survives `tickets.py roadmap`, and that `tickets.py check` stays ok.
   - The lock covers this repository's plugin table, so the line does not belong in the router that every consumer project gets.

The lock and the eval files must stay tracked, not git-ignored. `.gitignore` ignores only `.sdlc/dogfood/`, `.sdlc/runtime/`, and `.sdlc/messages/` under `.sdlc`.
### Acceptance criteria
- `test "$(cat .sdlc/evals/CLAUDE.md)" = '@AGENTS.md'`
- `for s in "## File format" "## Table lock" "## Procedures" "## Limits" "role:level model effort" "sort_keys" "table_sha256" "previous_eval" "evals.py add" "evals.py list" "evals.py check" "evals.py lock" "task_set" "pass_rate" "cost_usd" "evidence" "## Method" "## Result"; do grep -qF "$s" .sdlc/evals/AGENTS.md || exit 1; done`
- `python3 -c 'import sys, pathlib; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import evals; r = evals.validate_eval(pathlib.Path(".sdlc/evals/0000-baseline.md"), pathlib.Path(".")); print(r); sys.exit(r is not None)'`
- `f=.sdlc/evals/0000-baseline.md && grep -qx 'pass_rate: 0/0' "$f" && grep -qx 'cost_usd: unknown' "$f" && grep -qx 'date: 2026-09-30' "$f" && grep -qx 'host: all' "$f" && for e in haiku-alias-2026-09-30 planner-l3-opus-2026-09-30 codex-account-models-2026-09-30; do grep -q "^evidence: .*docs/validation/$e\.md" "$f" || exit 1; done`
- `python3 -c 'import json,sys; d=json.load(open(".sdlc/evals/table-lock.json")); sys.exit(not (sorted(d) == ["eval", "previous_eval", "table_sha256"] and d["eval"] == ".sdlc/evals/0000-baseline.md" and d["previous_eval"] is None))'`
- `test "$(python3 -c 'import json; print(json.load(open(".sdlc/evals/table-lock.json"))["table_sha256"])')" = "$(python3 -c 'import re,json,hashlib; r=open("plugins/sdlc-lite/scripts/run.sh").read(); rows=sorted("%s:%s %s %s" % m for m in re.findall(r"^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)", r, re.M)); j=json.dumps(json.load(open("plugins/sdlc-lite/adapters/codex/models.json")), sort_keys=True, separators=(",", ":")); print(hashlib.sha256(("".join(x + "\n" for x in rows) + j + "\n").encode()).hexdigest())')"`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `python3 plugins/sdlc-lite/scripts/evals.py list | grep -q '^0000-baseline\.md'`
- `awk '/sdlc-lite:managed:end/{e=1; next} e && /evals\/AGENTS\.md/{f=1} END{exit !f}' .sdlc/AGENTS.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `for f in .sdlc/evals/table-lock.json .sdlc/evals/0000-baseline.md .sdlc/evals/AGENTS.md .sdlc/evals/CLAUDE.md; do ! git check-ignore -q "$f" || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`

## Step 3: check.py guard: the model table must match the eval lock
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1 (evals.py) and step 2 (the lock; without it the guard is red on this repository).

In `plugins/sdlc-lite/scripts/check.py`, add the guard just before the final `for e in errors: print('FAIL', e)` loop, and add docstring item 14:
- Set `sdlc = root.resolve().parent.parent / '.sdlc'`. The plugin sits at `plugins/<name>` in its repository, so this is the repository's `.sdlc`.
- When `sdlc` is a directory, run this command and capture its output:

  ```
  [sys.executable, str(root/'scripts/evals.py'), '--root', str(sdlc), '--plugin', str(root), 'check']
  ```

- On a nonzero exit, append `evals: <line>` for each non-blank stdout or stderr line that does not start with `evals check:`. If there is no such line, append `evals: evals.py check exited <rc>`.
- Negative control, run only when that check passed:
  - Build a temp dir holding `scripts/run.sh` and a copy of `adapters/codex/models.json`. The run.sh is the text `rt` (read at check.py:360) with this substitution applied:

    ```
    re.sub(r'(builder:L1\)\s*model=)[\w-]+', r'\g<1>evals-negative-control', rt)
    ```

  - Run the same command with `--plugin <temp dir>`.
  - It must print a line containing `model table changed`, else append `check.py: evals lock guard negative control not flagged`.
- When `sdlc` is not a directory, print `skip: evals lock guard (no <sdlc>)` and add no error. A copied plugin dir has no repository around it. `check.sh` line 15 is the only caller that passes a root (grep), so copies made by earlier tickets' criteria, such as `cp -R plugins/sdlc-lite "$t/p"`, keep passing.
- Docstring item 14, `Evals lock`, says the following:
  - When `<plugin>/../../.sdlc` exists, `scripts/evals.py check` must pass for it: every eval is valid, and `evals/table-lock.json` holds the current model-table hash and cites a valid eval dated later than its `previous_eval`.
  - Each problem line prints as `FAIL evals: <line>`.
  - With no such folder, the guard prints `skip: evals lock guard`.
  - Negative control: run.sh with the builder:L1 model changed gives `model table changed`.

`subprocess`, `tempfile`, `shutil`, and `re` are already imported (check.py:51). No other file depends on this: nothing reads check.py output beyond its exit code (check.sh line 15).
### Acceptance criteria
- `t=$(mktemp -d) && mkdir -p "$t/r/plugins" "$t/r/.sdlc" "$t/r/docs" && cp -R plugins/sdlc-lite "$t/r/plugins/" && cp -R .sdlc/evals "$t/r/.sdlc/" && cp -R docs/validation "$t/r/docs/" && python3 "$t/r/plugins/sdlc-lite/scripts/check.py" "$t/r/plugins/sdlc-lite"`
- `t=$(mktemp -d) && mkdir -p "$t/r/plugins" "$t/r/.sdlc" "$t/r/docs" && cp -R plugins/sdlc-lite "$t/r/plugins/" && cp -R .sdlc/evals "$t/r/.sdlc/" && cp -R docs/validation "$t/r/docs/" && python3 -c 'import re,sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"(builder:L1\)\s*model=)[\w-]+", r"\g<1>evals-probe", p.read_text()))' "$t/r/plugins/sdlc-lite/scripts/run.sh" || exit 1; out=$(python3 "$t/r/plugins/sdlc-lite/scripts/check.py" "$t/r/plugins/sdlc-lite"); test "$?" -eq 1 || exit 1; printf '%s\n' "$out" | grep -q '^FAIL evals: .*model table changed'`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" || exit 1; out=$(python3 "$t/p/scripts/check.py" "$t/p"); test "$?" -eq 0 || exit 1; printf '%s\n' "$out" | grep -q '^skip: evals lock guard'`
- `t=$(mktemp -d) && mkdir -p "$t/r/plugins" "$t/r/.sdlc" && cp -R plugins/sdlc-lite "$t/r/plugins/" || exit 1; out=$(python3 "$t/r/plugins/sdlc-lite/scripts/check.py" "$t/r/plugins/sdlc-lite"); test "$?" -eq 1 || exit 1; printf '%s\n' "$out" | grep -q '^FAIL evals: '`
- `grep -qF '14. Evals lock' plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py | { ! grep -q .; }`

## Step 4: Document evals.py and the table lock where the model table is described
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 3. Use no em dashes. Each fact has one authoritative place: the format, the canonical text, and the lock rules live in `.sdlc/evals/AGENTS.md` (step 2) and in evals.py. These edits link there instead of copying them.

`docs/maintenance/sdlc-internals.md`: add an entry headed exactly ``## `scripts/evals.py` ``, after the `scripts/results.py` entry. It covers:
- the purpose: dated eval records, and the lock that ties the model table to one of them
- the CLI: `add`, `list`, `check`, `lock`, `hash`, `selftest`, the global `--root` and `--plugin`, and the exit codes
- the Python API, including `validate_eval` for later callers
- `table-lock.json` and its three keys
- the check.py guard: docstring item 14, skipped when no `.sdlc` sits beside the plugin's repository
- the selftest and its three negative controls
- a link `../../.sdlc/evals/AGENTS.md` for the format and the canonical text

`plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block, add this line after the `.sdlc/messages/` line, aligned like its neighbours:

```
.sdlc/evals/            the plugin repository's dated model and effort evals (NNNN-<slug>.md) and table-lock.json, written by scripts/evals.py add and lock; check.py fails a model-table change that cites no newer eval; its AGENTS.md documents the format
```

handoff-format is not a preloaded skill (the agents preload only level-rubric), so the Codex TOML does not change.

`plugins/sdlc-lite/AGENTS.md`:
- Extend the Contracts bullet that starts "Claude models and efforts live in `scripts/run.sh`". A change to either table needs a new eval in `.sdlc/evals/` and `scripts/evals.py lock`, else `scripts/check.py` fails; read [the evals entry file](../../.sdlc/evals/AGENTS.md) first.
- Add to the Verification list: `- Evals and the model-table lock: python3 plugins/sdlc-lite/scripts/evals.py check (and selftest).`

`docs/codex-role-execution.md`: after "Regenerate the agent files after changes." (line 46), add "A change also needs a new eval in `.sdlc/evals/` and `evals.py lock`, or `check.py` fails; see [the evals entry file](../.sdlc/evals/AGENTS.md)."

Left untouched on purpose:
- `skills/level-rubric/SKILL.md`: the planner and plan-reviewer preload it, so an edit would regenerate the Codex TOML. It is consumer guidance, and the lock is a maintainer gate.
- Root `AGENTS.md`: it routes SDLC changes to `plugins/sdlc-lite/AGENTS.md`, which now carries the rule.
- `docs/lean-sdlc/design.md`: a design record whose line 152 already says each planned folder gets its own entry file when built.

Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`. It must stay green.
### Acceptance criteria
- ``grep -qxF '## `scripts/evals.py`' docs/maintenance/sdlc-internals.md``
- `grep -qF 'table-lock.json' docs/maintenance/sdlc-internals.md`
- `grep -qF '.sdlc/evals/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'scripts/evals.py' plugins/sdlc-lite/AGENTS.md`
- `grep -qF 'evals.py lock' docs/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/codex-role-execution.md | { ! grep -q .; }`

## Step 5: Live run in a throwaway copy of the repository
level: L2
### Do
Depends on: steps 1 to 3. Record the run in `docs/validation/evals-live-run.md`, with no em dashes, in the shape of `docs/validation/role-result-schema-live-run.md`. No model call is needed.

Setup:
- Run `T=$(mktemp -d)`.
- Run `rsync -a --exclude .git --exclude .worktrees "$(git rev-parse --show-toplevel)/" "$T/repo/"`. This copies the working tree, including the steps' uncommitted changes.
- Run every arm from `$T/repo`.
- Never edit the real repository's `run.sh`, `models.json`, level-rubric, or `.sdlc/evals/`.

Record each arm's exact command and exit code:
1. Baseline: `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` gives exit 0.
2. Negative control on a Claude row:
   - In the copy's `plugins/sdlc-lite/scripts/run.sh`, change `builder:L2` from `effort=low` to `effort=medium`.
   - In the copy's `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, change the builder `| L2 | Opus low |` row to `Opus medium`, so the level-rubric guard stays green.
   - `check.py` gives exit 1, and its only FAIL line is the `FAIL evals: ... model table changed ...` line.
3. A reused eval is refused: `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0000-baseline.md` gives exit 1 with `is not later than`.
4. A new eval passes:
   - `python3 plugins/sdlc-lite/scripts/evals.py add live-probe --role builder --level L2 --model opus --effort medium --host claude --task-set evals-live-run --pass-rate 0/0 --cost-usd unknown --date "$(date +%F)" --evidence docs/validation/planner-l3-opus-2026-09-30.md --method "<text>" --result "<text>"` writes `.sdlc/evals/0001-live-probe.md`.
   - `evals.py lock --eval .sdlc/evals/0001-live-probe.md` gives exit 0.
   - `check.py` then gives exit 0.
5. Negative control on Codex: change scout L1's effort from `low` to `medium` in the copy's `models.json`. `check.py` gives exit 1 with `model table changed`.
6. Revert:
   - Run `rm -rf "$T"`.
   - In the real repository, `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json` gives exit 0.
   - `python3 plugins/sdlc-lite/scripts/evals.py check` still cites `.sdlc/evals/0000-baseline.md`.

An arm that cannot run is recorded as unverified, never replaced by a fixture.

The doc has these sections, holding the exact strings the criteria grep for:
- `## Environment`: the date (`2026-..-..`), the OS, `python3 --version`, the repository commit (`git rev-parse --short HEAD`), and a note that the copy includes this ticket's uncommitted changes.
- `## Commands`: the exact commands, including `evals.py add` and `evals.py lock`.
- `## Evidence`: for each arm, the exit code written as `exit 0` or `exit 1`, and the relevant output line (`model table changed`, `is not later than`).
- `## Limits`:
  - one machine
  - the hash covers parsed rows, not comments or layout
  - URLs are not fetched
  - a hand edit of `table_sha256` alone is not detected
  - only `check.py`, not the full `check.sh`, ran in the copy
### Acceptance criteria
- `f=docs/validation/evals-live-run.md && for s in "## Environment" "## Commands" "## Evidence" "## Limits" "check.py" "evals.py add" "evals.py lock" "model table changed" "is not later than" "exit 0" "exit 1" "models.json"; do grep -qF "$s" "$f" || exit 1; done`
- `grep -qE "2026-[0-9]{2}-[0-9]{2}" docs/validation/evals-live-run.md`
- `python3 -c 'import json,sys; d=json.load(open(".sdlc/evals/table-lock.json")); sys.exit(not (sorted(d) == ["eval", "previous_eval", "table_sha256"] and d["eval"] == ".sdlc/evals/0000-baseline.md" and d["previous_eval"] is None))'`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/codex-role-execution.md -e docs/validation/evals-live-run.md | { ! grep -q .; }`

## Step 6: Gates green
level: L2
### Do
Depends on: steps 1 to 5. Run every gate the handoff's Common rules name, and fix any red the earlier steps introduced, inside the files those steps changed:
- `bash plugins/sdlc-lite/scripts/check.sh`, which now includes `evals.py selftest` and check.py's evals guard
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `git diff --check`
- no em dash and no trailing whitespace in added lines or new files
- no change to the model rows of run.sh or to models.json

A gate already red at the build-start HEAD is reported as Status `inherited red: <tests>`. Do not bump versions, tag, push, or publish.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins docs .sdlc/AGENTS.md | grep '^+' | grep -q "$(printf '\342\200\224')"`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/evals); do ! grep -q "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/evals); do ! grep -qE '[[:space:]]$' "$f" || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`

## Assumptions
- `evals.py` hashes the same 19 rows `check.py` checks. Verified: the regex at check.py:63, run on `plugins/sdlc-lite/scripts/run.sh`, returns 19 rows.
- The host Python is 3.9.6. Verified by `python3 --version`.
- An eval cites its evidence as a list. The handoff asks one baseline file to cite three records as evidence, so `evidence` accepts a `[a, b, c]` list. Verified by reading the handoff Intent.
- The baseline uses `all` in role, level, model, effort, and host. It covers every row on both hosts, because it cites two Claude records and one Codex record, and one front matter cannot name a single row. The handoff's `claude` or `codex` list describes a single experiment. This is settled here; see Risks.
- The baseline is dated 2026-09-30, the date of all three deciding records. Verified by their file names and headings under `docs/validation/`.
- URLs are checked for form only, because check.sh runs offline. Verified at `plugins/sdlc-lite/scripts/check.sh` lines 6 to 8: the live probe "never runs here".
- Effort cannot be a fixed list. Verified: `docs/validation/codex-account-models-2026-09-30.md` lists `max` and `ultra` as Codex efforts.
- Two handoff phrases are read this way:
  - "the lock's previous value" is the date of `previous_eval`.
  - "updating the lock without an eval" is two cases: `lock` with no `--eval` (exit 2), and `lock` that cites the current eval again (exit 1, not later).
  Both readings are verified by the handoff Context, which says the lock stores `previous_eval` for this rule.
- The router line can sit outside the managed block. `tickets.py` keeps bytes outside it (tickets.py:140). Verified on a temp root: a line appended after `<!-- sdlc-lite:managed:end -->` survived `tickets.py roadmap`, and `tickets.py check` printed ok.
- A folder without a `handoff.md` is invisible to tickets and board. Verified on the same temp root: an `evals/` folder there left `board.py` showing only the ticket, and `tickets.py check` ok, matching `board.py:206-210` and `tickets.load`.
- `.sdlc/evals/` files stay tracked. Verified: `git check-ignore` exits 1 on them, and `.gitignore` ignores only `.sdlc/dogfood/`, `.sdlc/runtime/`, and `.sdlc/messages/` under `.sdlc`.
- Changing check.py's output breaks no caller. Verified by `git grep` over `plugins` and `scripts`: only `check.sh` passes a root to check.py, nothing reads its output beyond the exit code, and no script pins the contents of `check.sh`.
- The step 4 doc edits leave the Codex TOML unchanged. Verified: agent front matter preloads only `level-rubric`, so handoff-format and plugin `AGENTS.md` are not preloaded.
- The docs files need no `### Read first` entry. Verified by `git ls-files`: the only `AGENTS.md` files are the root, `.sdlc`, `plugins/progressive-context`, and `plugins/sdlc-lite`.
- Step 3's criteria are red for the missing guard. Verified at HEAD:
  - check.py on a copied plugin dir exits 0 and prints no skip line.
  - A repo copy with a `.sdlc` but no evals exits 0.
  - A repo copy with the builder:L1 model changed exits 1 with only the level-rubric FAIL and no `FAIL evals` line.
- check.py is a plain guard because it is green at the base, so "no new findings" equals a clean run. Verified by running it: `ok: 19 role levels, 9 agents checked`.
- Every gate guard is green at HEAD:
  - check.sh exit 0 (264 s, `skip: shellcheck not installed`)
  - packaging PASS
  - `codex_roles.py generate --check` ok
  - `tickets.py check` ok (208 tickets)
  - `git diff --check`, the em dash guards, and the whitespace guards green
- Each guard was also seen red:
  - check.sh exits 1 on a plugin copy with a changed row.
  - Packaging FAILs on an empty root.
  - `codex_roles.py --check` reports drift on a copy with a changed models.json.
  - `tickets.py check` reports `router block stale` on a temp root with an edited block.
  - `git diff --check` exits 2 on a fixture with trailing whitespace.
  - The em dash and whitespace greps match fixture text when un-negated.
  - The table-diff guard exits 1 on a fixture repo.
  - The check-ignore loop goes red on `.sdlc/messages/x`.
  - The scope guard goes red on a fixture path.
- Every new-behavior criterion was run once at HEAD. Each is red because evals.py, `.sdlc/evals/`, the guard, a doc line, or the live-run doc is missing. None is red from a typo or a wrong path. `steps.py lint` on this plan text prints `steps lint: ok`.

## Risks
- A hand edit of only `table_sha256` passes `check`. The lock cannot prove its own history, so `.sdlc/evals/AGENTS.md` says to update it only through `evals.py lock`, and the diff review catches the rest.
- `all` widens the handoff's host list. If the user wants strict `claude` or `codex` only, step 1's host rule and the baseline change.
- The strict later-date rule allows one model-table change per day per lock chain.
- Another lane might change a model row before this lane merges. Then the baseline lock is stale at merge time, and `check.py` goes red. The lock has no history yet, so the merge can delete it and rerun `evals.py lock --eval .sdlc/evals/0000-baseline.md`, or add a new eval.
- Any checkout with a `.sdlc` beside `plugins/<name>` but no lock now fails `check.py`, for example a fork that vendors the plugin.
- The router line lives outside the managed block, so a later layout migration (T-0206) must carry it over.
- Parallel lanes that add evals can pick the same number. `check` reports the duplicate after the merge, not before.
- T-0186 will call `validate_eval(path, repo)`, so a later signature change breaks it.
- The step 3 copy criteria copy about 6 MB per run, which takes a few seconds.
