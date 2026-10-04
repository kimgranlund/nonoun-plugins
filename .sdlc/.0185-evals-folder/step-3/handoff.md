## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

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
