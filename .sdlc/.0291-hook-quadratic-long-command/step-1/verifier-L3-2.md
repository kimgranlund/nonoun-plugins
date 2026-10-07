<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- 1. Hooks diff base..HEAD changes only the `pf=` and `raw=` lines of the four hooks, and the new `raw=` line yields the same text as the old: pass. Evidence:
  - `git diff -U0 24ef333 HEAD -- plugins/sdlc-lite/hooks` shows 8 changed lines, one `pf=` and one `raw=` per hook. `--numstat --summary` lists four files at 2 added, 2 removed, with no mode changes.
  - New line in all four: `raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')` (block-disk-scan.sh:268, block-pattern-kill.sh:117, block-stray-worktree.sh:322, block-repo-format.sh:314). Old line: `raw=$(tr '\n' ' ' <<<"${cmd//\\/}")`.
  - Equivalence run under `/bin/bash` 3.2.57: I `eval`ed the shipped line from each hook and the base line from `git show 24ef333:<hook>` on six strings and compared with `cmp`. Result: `cases=24 differing=0`, with 0 backslashes and 0 newlines left in every output.
  - The six strings: backslash before newline, double backslash, literal `\n`, trailing backslash, tabs, CR and multibyte text; an empty string; 8 backslashes only; a trailing newline; leading newlines; and 20,000 random characters with 1,220 backslashes and 820 newlines.
  - The result was the same under `LC_ALL=C` and `LC_ALL=en_US.UTF-8`.
  - Negative controls: the new form without the backslash delete, without the newline-to-space step, and with `_` as the replacement each printed DIFFERS, so the comparison can go red.
  - The `pf=` lines are unchanged since round 1 (`git diff HEAD~1 HEAD` on the hooks shows only the `raw=` lines), so round 1's `pf=` equivalence in verifier-L3.md still applies.
  - One `pf=` difference checked and dismissed: `$(...)` now drops trailing newlines that quote removal can expose. All four uses are substring globs or a regex with a `$` alternative (block-disk-scan.sh:32-33, block-pattern-kill.sh:28-29, block-stray-worktree.sh:32, block-repo-format.sh:35-36), so it cannot change the cheap exit.

- 2. Each of the five Bash hooks finishes a 20 KB heredoc with backslashes under 2 s, exit 0 on a harmless tail and 2 on a deny tail: pass. Evidence: my own harness (python `perf_counter` around `bash <hook>`, env handled as in the selftest, 3 runs per case, worst reported), with load average 13 to 20 on 20 cores.

  | Body | Bytes | Backslashes | HEAD hooks | HEAD~1 hooks (red control, 8 s cap) |
  |---|---|---|---|---|
  | Round-1 prose | 20,047 to 20,114 | 604 | 15 of 15 ok, worst 0.25 s | 8 of 15 time out |
  | Selftest body | 31,013 to 31,045 | 1,200 | 15 of 15 ok, worst 0.10 s | 8 of 15 time out |

  - Each body ran 15 cases: per hook one deny tail (exit 2 every run) and two harmless tails (exit 0 every run).
  - One harmless tail per hook gets past the cheap exit so the `raw=` line runs: `ls -la`, `mypid=$!; kill $mypid`, `git worktree list`, and `git status` with "format" in the body. That variant of the prose body holds 446 backslashes.
  - The 8 cases that time out on the HEAD~1 hooks are exactly the ones that reach the `raw=` line; the same 8 take 0.08 to 0.25 s on HEAD. block-publish.sh has no such line and took 0.02 to 0.08 s in both trees.
  - Stress extra, 20 KB of almost all backslashes (19,800): 15 of 15 ok, worst 0.10 s.
  - Stress extra, first 20 KB of hook-selftest.sh (137 backslashes): every run took 0.13 s or less, but the harmless tails exited 2 on the four hooks.
    - Draft fail: harmless tails are blocked.
    - Rebuttal: that body itself holds 25 `worktree add`, 27 `format` and 1 `pkill`, and the fail-closed heredoc scan reads the body.
    - Check: the HEAD~1 hooks gave the same exit codes in all 15 cases, at 1.31 to 1.34 s. This is unchanged behavior, so I dropped the finding.

- 3. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints PASS on HEAD and fails on the hooks with only the `pf=` lines fixed: pass. Evidence:
  - HEAD tree: `hook selftest: PASS`, exit 0, 13.1 s.
  - Red run: a detached worktree at HEAD under `$SDLC_TMP_WORKTREES/mix` with the four hooks overwritten from `git show HEAD~1:...`. `git hash-object` matched the HEAD~1 blobs, and `git diff HEAD` there showed only the four `raw=` lines, with the selftest identical to HEAD's.
  - Result: exit 1, 23.3 s, `hook selftest: FAIL: large 20 KB command:` with 5 `timeout>2s` entries: disk-scan `ls -la`, plus the deny tails of pattern-kill, disk-scan, stray-worktree and repo-format.
  - The biting variable is the `raw=` line. The other harmless tails leave at the cheap exit, and block-publish.sh has no such line.
  - The HEAD PASS is not a crashed block: the same block and the same python3 produced the FAIL in the mix tree.
  - The selftest body is about 31 KB, not the 20 KB its comment and the docs say. That is stricter than stated.
  - Caveat, not a fail: in the throwaway I made the perf block raise before any case, and the selftest printed `hook selftest: PASS`, exit 0, on the HEAD~1 hooks. The traceback went to stderr only.
    - Cause: `perf=$(python3 ...)` drops the exit status under `set -uo pipefail`, and empty output counts as success.
    - Draft fail: a guard that passes silently.
    - Rebuttal: the criterion asks for PASS on HEAD and FAIL on the HEAD~1 hooks, and both were observed. A crash needs an edit to the block or a missing python3.
    - Dropped to a note below.

- 4. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0: pass. Evidence:
  - Built tree: `ok: 269 tickets, roadmap current`, exit 0. `git status --short` and the ignored set were identical before and after.
  - Red control: a throwaway at HEAD~1 (4272134) printed `AGENTS.md: router block stale; run tickets.py --root .sdlc roadmap`, exit 1.

## Out of scope changes
None that break anything. Checked items:
- Dependents of the hooks: `bash plugins/sdlc-lite/scripts/check.sh` on the built tree exited 0 in 413 s, including `hook selftest: PASS`, `hook live probe selftest: PASS`, `run selftest: PASS` and `ok: plugin validate`. `check.py` printed `ok: 19 role levels, 9 agents checked`. `bash -n` passed on the four hooks.
- Unverified: the shellcheck part of check.sh printed `skip: shellcheck not installed`, so the changed lines were not linted on this machine.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: 32 lines added, 0 removed (`git diff --numstat 24ef333 HEAD`), so no earlier case was changed.
- `.sdlc/AGENTS.md` and `.sdlc/roadmap.md`: regenerated router and two roadmap rows. The criterion 4 run shows them current, and no `.sdlc/messages` file is in the diff.
- `docs/references/claude-hooks.md` and the ticket Context now say the literal backslash form is also quadratic, as round 1 asked. `git diff --check 24ef333 HEAD` exits 0.
- `docs/reports/hook-perf.md` spot-check on the report's own body, all within an order of magnitude:

  | Claim | Report | Observed |
  |---|---|---|
  | Base hooks at 1 / 2 / 4 KB | 0.20 to 0.35 / 1.15 to 1.60 / 8.01 to 8.93 s | 0.16 to 0.23 / 0.82 to 0.90 / 4.97 to 5.27 s |
  | `pf=`-only disk-scan at 8 KB | 4.09 s | 1.27 s |
  | `pf=`-only pattern-kill, stray-worktree, repo-format at 20 KB | 0.02 to 0.05 s | 0.02 to 0.03 s |
  | After, 1 to 20 KB | 0.02 to 0.21 s | 0.02 to 0.09 s |
  | Selftest cases failing on the `pf=`-only state | 5 | 5 |

- `docs/reports/hook-perf.md` is not in docs/README.md. Seven other reports are also unindexed, so this is not a regression.
- Constraints: 0 em dashes on added lines (`git diff 24ef333 HEAD`, added lines, `grep -c`), and 0 files changed under `plugins/sdlc-lite/agents`, `adapters` or `skills`.
- `.sdlc/.0292-machine-wide-gate-semaphore/handoff.md` and the step-1 run records in HEAD are ticket and run records, with no code.
- Working tree: the modified `step-1/handoff.md` is the brief I verified against, and `verifier-L3-2.attempt.json` is this run's record. Both throwaway worktrees are removed (`git worktree list` shows 0 under the prefix).
- A scratch folder, `/tmp/vfy0291-31435`, is left outside the repo because the cleanup command was denied.

## For the next attempt
None
