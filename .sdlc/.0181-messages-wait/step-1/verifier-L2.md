<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, selftest PASS plus the seven new `ok:` lines: pass. Evidence: `messages.py selftest` printed `messages selftest: PASS` with 33 `ok:` lines. All seven `wait` labels matched exactly, and the criterion's loop exited 0.
- Criterion 2, a present message returns in under 3 s, prints `<id>\t<path>`, and leaves the file unchanged: pass. Evidence: the verbatim command returned rc=0.
- Criterion 3, timeout exits 3, prints `no new messages`, and creates nothing: pass. Evidence: the verbatim command returned rc=0.
- Criterion 4, six bad values each exit 1 with `messages.py: <flag> must ...`, empty stdout, and nothing created: pass.
  - The first run under zsh printed nothing. That is zsh not word-splitting `$a`, not a defect.
  - Rerun under bash gave rc=1 with empty stdout for all six: `Bob`, timeout `601`, `0`, `1.5`, and interval `abc`, `0`. Each stderr was `messages.py: --receiver must match ...`, `--timeout must be an integer from 1 to 600: '601'`, and so on, and the final `ls -A` check passed (C4 rc=0).
  - `--timeout 99999999999` also exits 1 with the timeout reason, so the 9-digit cap works.
- Criterion 5, malformed file plus another receiver's message gives exit 3: pass. Evidence: the verbatim command returned rc=0.
- Criterion 6, no body on stdout or stderr: pass. Evidence: the verbatim command returned rc=0, and the output was non-empty.
- Criterion 7, `wait --help` lists `--timeout` and `--interval`: pass. Evidence: C7 rc=0.
- Criterion 8, the usage docstring line is present: pass. Evidence: `grep -qF` matched, C8 rc=0.
- Criterion 9, `wait changed the mailbox` occurs at least twice: pass. Evidence: the count is 3, C9 rc=0.
- Criterion 10, the diff and untracked files outside `.sdlc` are only `messages.py`: pass. Evidence: C10 rc=0 against `SDLC_BASE_SHA=bc21b53c…`.
- Checks bite: pass. I loaded mutated copies and ran the seven `wait` cases against each; the originals are all `ok`.

  | Mutation | Cases that went red |
  |---|---|
  | `wait_ready` stops skipping a malformed file | case 5 |
  | timeout cap raised to 700 | case 4 |
  | interval 0 allowed | case 4 |
  | timeout returns 0 instead of 3 | cases 3 and 5 |
  | `wait` also prints the body | cases 1, 5, 6 and 7 |

  Case 7 is the claiming control. It passes only when check (d) fires, and the selftest shows `ok:` for it.
- Python 3.9 compatibility: pass. The selftest ran on `/usr/bin/python3` (3.9.6) with no syntax errors.
- Neighbors: pass.
  - `case_entry_parses` and the other existing cases stayed `ok` in the full selftest.
  - `python3 plugins/sdlc-lite/scripts/check.py` printed `ok: 19 role levels, 9 agents checked`.
  - `git diff --check` is clean.
  - `run.sh` only calls `count`, which is unchanged.
- Builder claims: accepted only where I confirmed them. The two I checked:
  - `ENTRY_TEMPLATE` is unchanged: the diff has no hunk touching it.
  - The anchor occurs once in the source: the case asserts it and passed.
- Docstring updates: pass. The diff shows the usage line, the exit 3 sentence, the `wait` commands entry, the schema sentence plus `wait skips an invalid file instead.`, the layout sentence, and the metavar.

## Out of scope changes
None in tracked project files. The only diff is `messages.py`. Under `.sdlc/0181-messages-wait/` there are run records (`runs.jsonl`, the step folders, the plan-reviewer files), which are runner artifacts. Beyond the handoff text, the builder reworded the layout sentence to "list, count, wait, and expire on a missing mailbox create nothing; list, count, and expire exit 0". Its stated reason: `wait` on a missing mailbox exits 3 at the timeout, so the original "exit 0" would be false. I confirmed that behavior in criterion 3 (rc=3 on an empty root). I checked this against the Do text and it fits the intent, so I am not filing it.

## For the next attempt
None
