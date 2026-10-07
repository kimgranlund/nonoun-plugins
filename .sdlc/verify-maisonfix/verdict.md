# Independent verification: maisonfix lanes T-0343 to T-0348

Scope: local main at `891ff8c0` (merge of `maisonfix-*` lanes). Scratch copy `/tmp/verify-maisonfix` (git archive HEAD, re-initialised as a git repo so the ticket and ref scans run). Controls ran the same inputs against a full `git archive v0.21.1` tree at `/tmp/verify-maisonfix/v0211full`, and against the pre-lane commit `9a4735a7` (`/tmp/verify-maisonfix/old`) and the merge before T-0346, `3a22e729` (`/tmp/verify-maisonfix/pre46`), to isolate regressions. Control scripts are under `/tmp/verify-maisonfix/ctl/`. Verifier model family: Fable (builders were Sonnet solo lanes). No repo file was edited; nothing pushed, tagged or published.

## Verdict

fail

Two regressions on main plus one Done-when criterion only half met. Each ticket's own selftest is green; the failures live in the neighbours the lanes did not run.

- 🔴 `fanout.py selftest` is red on main (case 16 real lane, both cases). Green at `9a4735a7` and at `3a22e729`; red from the T-0346 merge `244f9075`. Root cause below.
- 🔴 `codex_roles.py generate --check` reports drift on `adapters/codex/agents/sdlc-conductor-l1.toml`. T-0344 edited `agents/conductor.md` and did not regenerate; the plugin AGENTS.md lists generated-agent parity as a required check for a role change.
- 🟡 T-0343: a truncated stdin that still holds one `## ` heading is recorded as the artifact as-is; the transcript is never consulted. Only the empty-stdin half of "empty or truncated" is delivered.
- 🟡 T-0345: nothing on the Claude conductor path clears the live marker (`solo_run.py complete` is not documented in any agent or skill; only `fanout.py land` calls it), so after one sub-agent solo every later solo dispatch in that checkout defaults to a worktree for 6 hours.

## Did the reported defects reproduce on v0.21.1

| Ticket | Reproduced on v0.21.1 | How |
|---|---|---|
| T-0343 | yes | `dispatch.py record --transcript <good jsonl> <dispatch>` with empty stdin: rc 1, attempt error `no result file at .../builder-L1.md`. The transcript held a complete builder report. (`ctl/t0343.sh`, case c5) |
| T-0344 | yes | HEAD's `hook-selftest.sh` copied into the v0.21.1 tree: `FAIL: spawn gate allows trailing text on the Handoff line (T-0344): exit 2, want 0`; the plain-line and no-line cases pass on both. (`st-hooks-v0211.log`) |
| T-0345 | yes | Two `solo_run.py run --task-dir ... --cwd <repo>` dispatches in one checkout: the second dispatch JSON has no `worktree` and `.worktrees/` stays empty. (`ctl/t0346b.sh`, v0.21.1 run with `--tier S`) |
| T-0346 | yes | `claude` shim printing `not json {broken`, `run --exec` with stderr to /dev/null: rc 0, stdout is only the raw line, no failure text; `runs.jsonl` gets a `cost none (no result event)` row. (`ctl/t0346b.sh`) |
| T-0347 | yes | Fixture plans with `- \`node --test tests\`` and `- all 12 tests pass`: v0.21.1 `steps.py lint` prints only the pre-existing lean warnings, rc 0 for both. (`ctl/t0347.sh`) |
| T-0348 | yes | Numbered ticket cited by `docs/spec.md`: v0.21.1 refusal names only `--rewrite-refs` or `--force`; `--keep-refs` is `unrecognized arguments`. (`ctl/t0348.sh`) |

All six were real on v0.21.1, so the "close without code if not reproduced" branch was correctly not taken. None of the six `## Closed` notes states that the reproduction was done; the handoffs say only "delivered by the solo agent".

## Criteria

| Ticket | Criterion | Result | Evidence command | Output excerpt |
|---|---|---|---|---|
| T-0343 | empty stdin + transcript writes a valid `<role>-<level>.md` | pass | `bash ctl/t0343.sh <HEAD scripts>` (c5) | `record rc=0`, result head `<!-- role=builder level=L1 model=sonnet effort=low -->`, 1 runs.jsonl line |
| T-0343 | truncated transcript message (`stop_reason max_tokens`) rejected with a clear error | pass | same (c6) | rc 1, attempt error `the builder final message in the transcript is truncated (stop_reason max_tokens); rerun it or have it write .../builder-L1.md`, no result file |
| T-0343 | complete stdin behaves as before | pass | same (c7: full report on stdin, truncated transcript) | rc 0, result written from stdin, transcript ignored |
| T-0343 | truncated stdin falls back to the transcript | fail | `ctl` run c9: stdin = first 28 chars of the builder report (`## Status\ndone\n\n## Changes\nx` cut before `## Checks`) + complete transcript | rc 0, artifact holds the truncated text (no `## Checks`); transcript never read because `said` already matches `^## ` |
| T-0343 | neighbour: error text on stdin + transcript with headings | changed | same (c8: stdin `Error: session limit reached`, transcript = complete report) | v0.21.1: rc 1 and `builder-L1.limit` written. HEAD: rc 0, artifact written from the transcript, no limit marker |
| T-0343 | dispatch selftest | pass | `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` | `dispatch selftest: PASS` |
| T-0344 | plain Handoff line spawns, trailing text spawns, no line denied | pass | `bash plugins/sdlc-lite/scripts/hook-selftest.sh` | `hook selftest: PASS`; the three T-0344 cases are in the script at lines 455 to 461 |
| T-0344 | observed failing on old behaviour | pass | HEAD hook-selftest.sh against v0.21.1 hooks | `FAIL: spawn gate allows trailing text on the Handoff line (T-0344): exit 2, want 0` |
| T-0344 | live reasoning on `block-role-spawn.sh` | pass | read lines 73 to 81 | `handoff="${line#Handoff: }"`, leading whitespace stripped, then `${handoff%%[[:space:]]*}` keeps the first token; a path with a space in it would be cut, which the repo's `.sdlc/<nnnn>-<slug>/handoff.md` convention never produces |
| T-0344 | generated-agent parity | fail | `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` | `generated agent drift: .../adapters/codex/agents/sdlc-conductor-l1.toml`; regenerating in scratch changes exactly the conductor's spawn-gate sentence (the T-0344 edit) |
| T-0345 | second live solo in one checkout defaults to a worktree, the choice is printed | pass | `bash ctl/t0346b.sh <HEAD scripts> L1` and `ctl/t0345_46.sh` | second dispatch `worktree=/private/tmp/.../.worktrees/solo-par2`, stderr `another solo is live in this checkout; using worktree solo-par2 (--no-worktree to stay)` |
| T-0345 | single run keeps today's behaviour | pass (with the marker caveat under Findings) | same | first dispatch: `worktree=<none>`, no `.worktrees/` |
| T-0345 | explicit flags win | pass | same | `--no-worktree` with a live marker: `worktree=<none>`; `--worktree lane-z`: `.worktrees/lane-z` on branch `lane-z` |
| T-0345 | solo_run selftest | pass | `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` | `solo_run selftest: PASS` |
| T-0346 | malformed stream, stderr to /dev/null: error on stdout, non-zero exit, log path | pass | `bash ctl/t0346b.sh <HEAD scripts> L1` | rc 1; stdout `solo_run.py: FAILED: session stream has no readable result event (JSON parse failure); first line: not json {broken; raw stream log: .../bad/solo.stream.log`; file exists |
| T-0346 | neighbour: an empty stream (session prints nothing, exit 0) | changed, breaks fanout | same, `empty` case | v0.21.1 rc 0; HEAD rc 1 with `first line: (empty)` |
| T-0346 | fanout selftest (consumer of `solo_run.py run --exec`) | fail | `python3 plugins/sdlc-lite/scripts/fanout.py selftest` | `case 16 real lane: both solo tickets merge and close with the skips guard live, got rc=1 done=[]`, lane table `T-0001 driver failed rc=1`, `T-0002 skipped`; PASS at `9a4735a7` and at `3a22e729` |
| T-0347 | `node --test <dir>` is a lint error | pass | `bash ctl/t0347.sh <HEAD steps.py>` | `dir: rc=1 :: steps: ... acceptance criterion runs node --test on a directory: node --test tests ... plan defect: replan this step (/chain 3)` |
| T-0347 | bare count warns, count with a named command passes, glob or file passes | pass | same | `bare: rc=0 ... criterion cites a count without a named source file or command: - all 12 tests pass`; `named` and `glob` print only the pre-existing lean warnings |
| T-0347 | no change to other lint results | pass | old vs new `steps.py lint` over 14 existing plans in `.sdlc/.0195` to `.sdlc/.0233` (`ctl/plans.txt`, `ctl/lint-old-*` vs `ctl/lint-new-*`) | all 14 `same`, rc 0, byte-identical stdout+stderr |
| T-0347 | steps selftest | pass | `python3 plugins/sdlc-lite/scripts/steps.py selftest` | `steps selftest: PASS` |
| T-0348 | `--keep-refs` closes a cited ticket and the close note lists the citing files | pass | `bash ctl/t0348.sh <HEAD tickets.py>` | rc 0, `moved to .0003-x; left refs to .sdlc/0003-x in docs/spec.md`; handoff `## Closed` holds `kept stale refs to .sdlc/0003-x in: docs/spec.md`; `docs/spec.md` unchanged |
| T-0348 | without the flag the refusal still happens | pass | same | rc 1, `rerun with --rewrite-refs (...) or --keep-refs (close, leave them and record them in the close note) or --force (...); nothing written`; folder still `0003-x` |
| T-0348 | `--keep-refs` + `--rewrite-refs` refused; `--dry-run` lists `keep <file>` | pass | same | rc 1 `do not combine ... nothing written`; dry run prints `keep docs/spec.md` before `expect` |
| T-0348 | reference-safety invariant in `plugins/sdlc-lite/AGENTS.md` intact | pass | `sed -n 22,32p plugins/sdlc-lite/AGENTS.md` | line "Ticket changes must preserve cross-worktree ID uniqueness, reference-safe closure, and explicit follow-up selection" unchanged; `--keep-refs` still refuses to combine with `--rewrite-refs` and does not override open warnings |
| T-0348 | tickets selftest | pass | `python3 plugins/sdlc-lite/scripts/tickets.py selftest` | `tickets selftest: PASS` |
| all | `check.py` x3 | pass | `python3 plugins/sdlc-lite/scripts/check.py` (check1..3.log) | `ok: 19 role levels, 9 agents, 22 generated definitions checked`, exit 0 each time; item 43 (retired S/M/L vocabulary) is part of this run and passed |
| all | `tickets.py check` | pass | `python3 plugins/sdlc-lite/scripts/tickets.py check` | `ok: 341 tickets, roadmap current` plus the pre-existing placeholder-text warnings |
| all | `docs_check.py` | pass, 13 warnings | `python3 plugins/sdlc-lite/scripts/docs_check.py` | `0 errors, 13 warnings (B-2a 5, B-3a 3, D-10 3, D-11 2)` |
| all | `check-packaging.py` | pass | `python3 scripts/check-packaging.py` | `PASS: catalog parity, identity, skill routes, hook isolation and context links` |
| all | `claude_roles.py generate --check` and selftest | pass | both commands | `Claude agent definitions verified (22 files)`, `claude_roles selftest: PASS` |
| all | hook selftest | pass | `bash plugins/sdlc-lite/scripts/hook-selftest.sh` | `hook selftest: PASS` |
| all | `git diff --check 9a4735a7..HEAD -- plugins scripts docs` | pass | | no output, rc 0 |
| all | em or en dashes in the lane diffs | pass | `git diff 9a4735a7..HEAD -- plugins scripts \| grep '^+' \| grep -P '[\x{2014}\x{2013}]'` | only two hits, both inside Codex TOML `developer_instructions` strings from T-0342 (`59a3697c`), not the six lanes |

The docs_check B-2a question: the fifth B-2a is `.sdlc/verify-one-level/`, added by `f2eb500d` "Close T-0342 with its independent verifier verdict", before the six lanes. `docs_check.py` at `9a4735a7` (pre-lane) already prints the same 13 warnings with B-2a 5, and the v0.21.1 tree also prints 13 with B-2a 5 (a different fifth entry at that point). No maisonfix change caused it; the warning is the verifier folder of T-0342 not being a known record folder.

## Findings

1. T-0346 turns an empty session stream into a failure and leaves `fanout.py selftest` red on main. Root cause: `_run_locked` now treats `rc == 0 and result is None` as `FAILED`, and an empty stdout is a `None` result. `fanout.py selftest` case 16 uses a `claude` shim that prints nothing (it writes `$FANOUT_TICKET.txt` and exits 0), so both real-lane cases fail with `driver failed rc=1`. The T-0346 lane ran only the touched selftest; the AGENTS.md matrix names "relevant regression checks" for an execution change and `fanout.py` is the only consumer of `solo_run.py run --exec`. Fix is either to keep an empty, exit-0 stream as not-a-parse-failure (only a non-empty stream with no result event is "unreadable") or to update the fixture to emit a result event; the first keeps the ticket's intent (a malformed line) without widening it. Evidence: `st-fanout.log` (HEAD, FAIL), `st-fanout-old.log` (9a4735a7, PASS), `st-fanout-pre46.log` (3a22e729, PASS), `ctl/t0346b.sh` empty case (v0.21.1 rc 0, HEAD rc 1).

2. T-0344 left the generated Codex conductor stale. Root cause: `agents/conductor.md` is the source for `adapters/codex/agents/sdlc-conductor-l1.toml`, the lane edited the source sentence and did not run `codex_roles.py generate`; `check.py` does not cover this parity (it passed), only `codex_roles.py generate --check` does, and that check is in the plugin's required list. Fix: regenerate and commit the TOML. Evidence: `codex_roles.py generate --check` on the scratch copy; the only textual diff after regeneration is the T-0344 sentence `(the path is the first token of the prompt's Handoff: line; trailing text is ignored)`.

3. T-0343 handles an empty stdin but not a truncated one. Root cause: in `record`, the transcript is consulted only when `said` has no `^## ` line (`fin = ... if transcript and not re.search(r'^## ', said, re.M) else None`), so a notice cut off after its first heading is recorded verbatim as the artifact and the complete message in the transcript is ignored; there is no comparison of stdin against the transcript's final message and no selftest for a truncated stdin. The ticket text says "when stdin is empty or truncated". Fix: when `--transcript` is given and its final message is complete (`end_turn`) and `said` is a strict prefix (or shorter than) that message, prefer the transcript; add the selftest case. Evidence: `ctl` run c9, HEAD artifact ends at `## Changes\nx` with no `## Checks` while the transcript held the full report, rc 0.

4. T-0343 changes the meaning of error text on stdin when a transcript is given. Root cause: the same branch ordering, so stdin that is the sub-agent's error (for example `Error: session limit reached`) is overridden by any transcript message with a `## ` heading; v0.21.1 recorded a failed attempt and wrote the `.limit` resume marker, HEAD records a success and writes no marker. If a role posted an interim `## Status` message and then hit a 429, record now closes the attempt as done on the interim text. Fix: only fall back to the transcript when stdin is empty or whitespace (the ticket's empty case) or a prefix of the transcript's final message (finding 3); keep non-matching error text on stdin authoritative. Evidence: `ctl/t0343.sh` case c8 on both trees.

5. T-0345 live markers are never cleared on the conductor path. Root cause: `mark_live` runs on every non-worktree sub-agent dispatch and only `complete` (or a 6 hour TTL) removes the marker; `solo_run.py complete` is called by `fanout.py land` only, and no agent or skill text (`agents/solo.md`, `skills/agent/SKILL.md`, `agents/conductor.md`) tells a conductor to run it, which `docs/reports/2026-10-07-subagent-mode-live.md` line 131 already notes ("priced rows do not exist" on that path). So after one solo sub-agent dispatch, every later solo dispatch in that checkout for 6 hours gets `.worktrees/solo-<task>` and a branch even when run one after another, which is the "single run" the Done-when says keeps today's behaviour. Fix: document and call `complete` (or `dispatch.py record`-style closure) on the conductor path, or key liveness on something that ends with the sub-agent (the attempt file in `.sdlc` has no pid either), or shorten the TTL. Evidence: `ctl/t0345_46.sh` HEAD run, `par2` got a worktree while `par1` was only a dispatch JSON that never ran; markers listed under `.git/solo_live/`.

6. Minor, T-0346 output: on a malformed stream the raw stream is printed to stdout in full (`print(out, end='')`, pre-existing) and then its first line again inside the `FAILED` line, so the raw text appears twice. Cosmetic; the message and exit code are correct.

7. Minor, T-0343 selftest fixture: the c5 and c6 transcripts hold one message each, so the "last assistant message with text" selection (a transcript with tool-use turns before the final text) is not exercised; `transcript_final` walks every line and keeps the last text-bearing assistant message, which reads correct.

8. Process: none of the six `## Closed` notes records that the defect was reproduced on main before the change, although each ticket asked for that first. The reproductions above show all six were real, so no code was written for a non-defect, but the record does not say so.

## What was run

check.py x3, tickets.py check, docs_check.py, scripts/check-packaging.py, codex_roles.py generate --check, claude_roles.py generate --check and selftest, selftests of dispatch, solo_run, steps, tickets, fanout, hook-selftest.sh; the same fanout selftest at 9a4735a7 and 3a22e729; HEAD's hook-selftest.sh against the v0.21.1 hooks; per-ticket control scripts in `/tmp/verify-maisonfix/ctl/` against v0.21.1 and HEAD; old-vs-new lint over 14 existing plans; callers grep for `record`, `dispatch_json`, `complete`, `cmd_close`, `lint_steps`, `count_warnings`, `live_solos`, `auto_worktree`, `mark_live`, `unmark_live`, `transcript_final` (only the expected in-script and fanout callers; no other consumer changed).

Limitations: no live Claude session was started (shims stood in for `claude -p`); the T-0344 hook reasoning is from the script and the selftest, not a live spawn; `codex-selftest.py` and the bench were not run (no Codex behaviour changed). One `git checkout -q -- .` was run by mistake in the real checkout while resetting the scratch copy; the real tree was clean before and after, so nothing changed.
