<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/evals.py` (new, executable): the eval format and its parser and validator, the canonical table text and hash, `add`, `list`, `check`, `lock`, `hash`, and a `selftest` with 16 cases, including the three negative controls.
- `plugins/sdlc-lite/scripts/check.sh`: added the `python3 "$root/scripts/evals.py" selftest || fail=1` line after the `results.py` line, and added `evals.py` to the header comment's list of selftests.

## Checks
- `python3 plugins/sdlc-lite/scripts/evals.py selftest`: exit 0. All 16 named cases print `ok:`, then `evals selftest: PASS`.
- Acceptance criteria 1 to 13 (selftest, the 16 exact `ok:` names, hash equal to the inline recomputation, the add/lock/list/check flow, missing date, bad evidence, bad host, stale lock, the lock refusals with the lock byte-identical, the newer-eval relock, the import API with no output, the executable bit, the check.sh wiring): each run exactly as written, all PASS.
- Guard: `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`: PASS.
- Guard: changed and untracked files outside `.sdlc`, less the two allowed paths, came out empty: PASS.
- Manual spot checks on a temp project: a missing evals dir, a duplicate field, a bad front matter line, a reused number, a non-eval `.md` name, a malformed lock, `list` showing invalid lines (exit 0), and `add` with a bad slug. Every reason string matched the handoff text.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. shellcheck was skipped because it is not installed; `claude plugin validate` printed ok.
- `git diff --check`: clean.
- No em dashes in evals.py.

## Notes
These are choices the handoff left open:
- `add` writes `## Method` on the line right after the closing `---`, with no blank line in between.
- Front matter lines are split on the first `: `. So `date:` with nothing after it is reported as `bad front matter line <n>`, while `date: ` (with a trailing space) is reported as `missing field date`.
- `unknown field` is reported before the per-field checks that run in FIELDS order.
- A `task_set` value shaped like a `[a, b]` list is refused, because only evidence may hold a list.
- Two evals with the same number: the later file in name order gets the `number NNNN is used twice` line.
- `lock` refusal messages show PATH as given on the command line. The lock file itself stores the repo-relative path.
- `previous_eval` has to pass the same test as `eval`: it exists, sits directly in `<root>/evals/`, and is a valid eval.
- In the selftest, project one sits at `<t>` itself. Cases that need a clean state use more projects under `<t>/more/<name>`, each with its own `docs/e.md` and plugin copy. Case 13 tracks the sha256 of every temp table and both real tables after every subprocess. It runs last but is printed in 13th position.
- Each negative control first checks that the real script refuses the same fixture: in case 14 directly, and through cases 11 and 2 for the other two.
