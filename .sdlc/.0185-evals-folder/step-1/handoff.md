## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

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
- `effort`: regex `[a-z]+`. There is no fixed list, because Codex advertises `max` and `ultra` (`docs/reports/codex-account-models-2026-09-30.md`).
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
