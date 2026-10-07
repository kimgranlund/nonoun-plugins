<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
- 1. Hooks diff changes only the four `pf=` lines, and the replacement strips exactly backslash, single quote and double quote: pass. Evidence: `git diff 24ef333 HEAD --numstat -- plugins/sdlc-lite/hooks` lists four files at 1 added, 1 removed each. `git diff -U0` shows only `-pf=${cmd//[\\\'\"]/}` and `+pf=$(tr -d "\\\\'\"" <<<"$cmd")`, four times, with no mode changes.
  - I ran the shipped line from each hook (`eval "$(sed -n 31p block-disk-scan.sh)"`, likewise 27, 34, 31) on a 72-character string holding all three characters plus other punctuation. Output was 69 characters, none of the three left, and equal to the old substitution's output in all four hooks.
  - `od -c` shows the set `tr` receives is `\ \ ' "`.
  - Negative controls: a set without `"` and a set with an added backtick both printed DIFFERS, so the equality check can go red.
  - Trailing newlines are not a difference: `cmd=$(jq -r ...)` (block-pattern-kill.sh:23) already strips them.
- 2. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints PASS on HEAD: pass. Evidence: output `hook selftest: PASS`, exit 0, 12.9 s.
- 3. The new selftest bites on the base hooks: pass. Evidence: detached worktree at HEAD under `$SDLC_TMP_WORKTREES/mix`, the only location my role allows, with the four hooks overwritten from `git show 24ef333:...`.
  - Setup checks: `git hash-object` of each hook equals the base blob, `cmp` shows the selftest identical to HEAD's, and the selftest resolves hooks from its own directory (hook-selftest.sh:40).
  - Result: exit 1, `hook selftest: FAIL: large 20 KB command: ...` with 8 `timeout>2s` entries (the four hooks, both tails) and 0 `block-publish` entries.
  - The `pf=` line is the only difference between the green and red trees.
- 4. Each of the five Bash hooks finishes a 20 KB heredoc under 2 s, exit 0 on a harmless tail and 2 on a deny tail: fail. Evidence: my own harness (python `perf_counter` around `bash <hook>`, env as in the selftest) on HEAD. Exit codes were correct in every run; the time bound is what fails.

  | 20 KB body | Backslashes | Result |
  |---|---|---|
  | Report shape (`echo line N 'quoted text' "dq" done`) | 0 | all 10 runs ok, worst 0.269 s |
  | Prose, forward slashes | 0 | all 10 ok, worst 0.23 s |
  | Same prose, `C:\tmp\rowN` | 604 | 8 of 10 over 2 s |

  Times on the 604-backslash body:

  | Hook | Harmless tail | Deny tail |
  |---|---|---|
  | block-disk-scan.sh | 19.04 s (`ls -la`) | 19.97 s |
  | block-pattern-kill.sh | 16.29 s (`mypid=$!; kill $mypid`) | 14.71 s |
  | block-stray-worktree.sh | 21.73 s (`git worktree list`) | 18.85 s |
  | block-repo-format.sh | 13.25 s (`git status`, "format" only in the body) | 16.00 s |
  | block-publish.sh | 0.03 s | 0.11 s |

  - Cause: `raw=$(tr '\n' ' ' <<<"${cmd//\\/}")` at block-disk-scan.sh:268, block-pattern-kill.sh:117, block-repo-format.sh:314, block-stray-worktree.sh:322. Every heredoc command that gets past the cheap exit reaches it, because each analyzer exits 1 on `<<`.
  - Isolated on bash 3.2.57 at 9.4 KB: literal `${cmd//\\/}` takes 0.002 s with 0 backslashes and 1.973 s with 386.
  - Causal check: throwaway copies of the HEAD hooks with only that line swapped to `raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')` ran all 10 cases in 0.03 to 0.14 s with the same exit codes.
  - The selftest's own body and its own harmless tail (`ls -la`, block-disk-scan.sh, 26.5 KB) took 0.11 s with 0 backslashes, 4.37 s with 100, and 31.30 s with 700.
  - A real file (first 20 KB of hook-selftest.sh, 137 backslashes) took 1.41 to 1.54 s on the four hooks.
  - Steelman: the builder would say "my 20 KB heredoc passes, and the `raw=` line is a separate site". The finding survives: the criterion and the ticket Goal pin no body, backslashes are ordinary heredoc content, and it is the same defect class in the same four hooks. The lines are identical at base, so this is an incomplete fix, not a regression.
- 5. Timings and claims in docs/reports/hook-perf.md match within an order of magnitude: pass. Evidence, report-shaped body:

  | Claim | Report | Observed |
  |---|---|---|
  | Base hooks at 1 / 2 / 4 / 8 KB | 0.23 to 0.27 / 1.32 to 1.40 / 8.78 to 9.32 / over 20 | 0.23 to 0.25 / 1.10 to 1.14 / 5.66 to 6.78 / timeout at 21 s |
  | HEAD hooks at 1 to 8 KB | 0.02 to 0.03 | 0.015 to 0.022 |
  | HEAD at 20 KB, pass tail | 0.01 to 0.03 | 0.021 to 0.035 |
  | HEAD at 20 KB, deny tail | 0.07 to 0.09, exit 2 | 0.086 to 0.269, exit 2 |
  | Bracket substitution, 9.4 KB | 56.5 s | 53.1 s |
  | Literal substitution, same string | under 0.01 s | 0.002 s |
  | Selftest on pre-fix hooks | 8 of 10 `timeout>2s` | 8 of 10 |

  - "No such substitution" in the other four hooks: `grep -nE '\$\{[A-Za-z_][A-Za-z0-9_]*//?'` finds none there.
  - block-publish.sh took 0.016 s at 8 KB and block-background.sh 0.033 s at 20 KB. I did not time block-role-spawn.sh or warn-handoff-edit.sh.
  - Caveat: the literal-substitution figure is true only because that string has zero backslashes; see below.

## Out of scope changes
- `.sdlc/0292-machine-wide-gate-semaphore/handoff.md`: new idea ticket with no code. Its front matter parses (`tickets.py --root .sdlc check` in the throwaway, after regenerating, printed `ok: 269 tickets, roadmap current`, up from 267 at base). Adding it left `.sdlc/AGENTS.md` stale; see below.
- `.sdlc/roadmap.md`: two rows added for T-0291 and T-0292. Regenerating in the throwaway left roadmap.md unmodified, so the rows are current.
- `docs/references/claude-hooks.md`: two lines added. `git diff --check 24ef333 HEAD` exits 0, the link target exists, and the diff holds 0 em dashes. Its guidance is incomplete; see below.
- Dismissed with checks: hooks.json is unchanged (`git diff --name-only 24ef333 HEAD -- plugins/sdlc-lite/adapters` lists 0 files), `check.py` prints `ok: 19 role levels, 9 agents checked`, and `hook-live-probe.sh --selftest` prints PASS. I did not run the full `check.sh`.

## For the next attempt
plan defect: criterion 1 ("changes only those four `pf=` lines") contradicts criterion 4, because the under-2 s bound cannot hold for a 20 KB heredoc containing backslashes without also changing the `raw=` line in the same four hooks: plugins/sdlc-lite/hooks/block-disk-scan.sh:268, block-pattern-kill.sh:117, block-repo-format.sh:314, block-stray-worktree.sh:322. Widen criterion 1 to those lines, and add `.sdlc/AGENTS.md` to the scope.

What the build still needs:
1. Replace `raw=$(tr '\n' ' ' <<<"${cmd//\\/}")` in the four hooks with a linear form. `raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')` ran in 0.13 s with unchanged exit codes in my throwaway copy.
2. Put backslashes in the selftest's 20 KB body. Today the body has none, so the perf case passes on HEAD while four hooks still take 13 to 22 s. One backslash per line makes current HEAD red (31 s on block-disk-scan.sh with `ls -la`). Confirm red on current HEAD, then green after item 1.
3. Run `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap` and commit `.sdlc/AGENTS.md`.
   - `tickets.py --root .sdlc check` exits 1 at HEAD (`AGENTS.md: router block stale`) and exits 0 at 24ef333.
   - The block still says `proposed: 16` and lacks T-0291 and T-0292.
   - In the throwaway the same command also rewrote `.sdlc/messages/**/AGENTS.md` with that copy's script path. Leave those out of the commit.
4. Correct the prose that says the literal form is safe:
   - The ticket Context says "a literal pattern is not" quadratic.
   - docs/maintenance/claude-hooks.md:39 warns only against `${var//[class]/}`.
   - The Cause section of docs/reports/hook-perf.md compares the two forms on a string with zero backslashes. The literal form took 1.97 s at 9.4 KB with 386 backslashes.
5. Minor:
   - docs/reports/hook-perf.md is not in docs/README.md, which docs/AGENTS.md asks for. Seven other reports were already unindexed at base, so this is not a regression.
   - "A 20 KB case per hook" overstates coverage: the selftest covers five of the six Bash-matcher hooks. block-background.sh is not covered; it took 0.033 s at 20 KB.
