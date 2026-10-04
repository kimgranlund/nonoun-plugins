<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/evals.py selftest`: pass. Evidence: all 16 cases print `ok:`, then `evals selftest: PASS`, exit 0.
- The 16 exact `ok: <name>` lines (the `out=$(...) && for n in ...` loop): pass. Evidence: ran verbatim and printed `names-ok`; the loop's `grep -qxF` matched every name.
- `hash` equals the inline recomputation: pass. Evidence: the `test "$(... hash)" = "$(python3 -c ...)"` command exited 0. `hash` printed `ab3aa58b…6ecd`. The TABLE_RE regex finds 19 rows, as the handoff says.
- add, lock, list, check flow on a temp project: pass. Evidence: ran verbatim, exit 0.
- Missing `--date`: pass. Evidence: exit 1, stderr has `missing field date`, and no `$t/.sdlc/evals` was created. Exit 0.
- Bad evidence path: pass. Evidence: exit 1, `bad field evidence`, no evals dir.
- Bad host together with bad pass_rate and date: pass. Evidence: exit 1, `bad field host`. This is the first problem in FIELDS order.
- Stale lock after a run.sh row change: pass. Evidence: `check` exits 1 and prints `model table changed`.
- Lock refusals: pass. Evidence: a bare `lock` exits 2. Locking the cited eval again exits 1 with `is not later than`. A missing eval exits 1 with `no such eval`. `cmp -s` shows the lock byte-identical.
- Newer-eval relock: pass. Evidence: `eval` is 0001-next, `previous_eval` is 0000-base, `table_sha256` equals `hash`, and `check` exits 0.
- Python API: pass. Evidence: `FIELDS` tuple equal, all four callables present, and the import printed 0 bytes.
- Executable: pass. Evidence: `test -x` exits 0, and `ls -l` shows `-rwxr-xr-x` with the `#!/usr/bin/env python3` shebang.
- check.sh wiring: pass. Evidence: `grep -qF 'scripts/evals.py" selftest'` exits 0. The `git diff` shows the new line right after the `results.py` line and `evals.py` added to the header comment. A full `bash plugins/sdlc-lite/scripts/check.sh` exits 0 and its output lists the evals cases.
- (guard) run.sh and models.json unchanged: pass. Evidence: `git diff --quiet "$SDLC_BASE_SHA" -- ...` exits 0 (the base sha is 433125d, the same commit as HEAD). This is a new-behavior guard on files the step must not touch. I did not run it at base, because it holds trivially there.
- (guard) no files outside scope: pass. Evidence: the command exits 0. `git status` shows only `check.sh` modified and `evals.py` untracked outside `.sdlc`.
- Negative controls bite: pass. Evidence, mutating a temp copy under mktemp:
  - Setting the real `# rule: hash` condition to `if False:` made case 6 and negative control 14 fail ("real check passed the stale lock").
  - Stripping the `# rule: date` marker made control 15 fail loudly ("matched 0 lines, want exactly 1").
  - So the controls go red, and a moved rule fails loudly.
- Format constraints: pass. Evidence: the file imports only stdlib modules (lines 62-72) and no other plugin script. `python3 --version` is 3.9.6, and no `X | Y` annotations or `match` turned up in a grep. A grep for em dashes returned nothing. `git diff --check` is clean. `main()` runs only under the `__main__` guard (line 820).
- Dismissal: I judged the builder's note about `add` writing `## Method` directly after the closing `---` harmless. The handoff's file layout lists the `---` followed by `## Method`, and selftest case 1 asserts exactly those lines. This follows the spec.

## Out of scope changes
None. Besides `evals.py` and `check.sh`, only `.sdlc/` artifacts changed. The scope guard confirms this.

## For the next attempt
None
