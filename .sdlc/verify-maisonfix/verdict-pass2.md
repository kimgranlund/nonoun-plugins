# Independent verification, second pass: T-0349 to T-0351 and findings 1 to 5 of the maisonfix verdict

Scope: local main at `e3b72ad1`. Scratch copy `/tmp/verify-v2` (git archive, re-initialised as a git repo for the ticket and ref scans). Controls ran the same inputs against the pre-lane commit `57274103` (`/tmp/verify-v2-old`) and the v0.21.1 tree (`/tmp/verify-v2-v0211`). Mixed trees under `/tmp/verify-v2-mix.*` hold the HEAD selftests over the pre-fix logic; `/tmp/verify-v2-plant.*` holds the planted-edit tree. Control scripts and logs: `/tmp/verify-v2/ctl/`, `/tmp/verify-v2/logs/`. Verifier model family: Fable (the three lanes were Sonnet solo L1). No repo file was edited; no checkout or reset ran in the real checkout; nothing pushed, tagged or published.

## Verdict

pass

All three Done-when criteria hold on HEAD and each new selftest fails against the pre-fix logic. Findings 1 to 5 of the earlier verdict are closed end to end. The release-candidate checks are green: check.py x3, tickets.py check, docs_check (0 errors, 11 warnings), check-packaging, codex-selftest, both generate --check runs, the selftests of dispatch, solo_run, steps, tickets, fanout, budget and hooks, and check.sh once. The findings below are record and neighbour defects, none a release blocker.

## Criteria

| Ticket or finding | Criterion | Result | Evidence command | Output excerpt |
|---|---|---|---|---|
| T-0349 | complete stdin, no transcript: recorded as before | pass | `bash ctl/t0349.sh <HEAD scripts>` r1 | rc 0, result `## Status|done||## Changes|x||## Checks|x` |
| T-0349 | empty stdin + transcript: transcript recorded | pass | same, r2 | rc 0, full report, attempt `completed` |
| T-0349 | truncated stdin (cut after the first heading) + transcript: full report recorded | pass | same, r3 (`## Status\ndone\n`) and r3b (cut before `## Checks`) | rc 0, result holds `## Checks|x`; pre-fix (`57274103`) r3 result ends at `## Status|done|` and r3b at `## Changes|x` |
| T-0349 | error stdin `Error: session limit reached` + transcript with an interim `## Status`: failed attempt and the `.limit` marker as v0.21.1 | pass | same, r4 on HEAD, pre-fix, and v0.21.1 (`notranscript`) | HEAD rc 1, `builder-L1.limit` written, attempt `('failed', 'Error: session limit reached')`, stderr `session limit: resume with: ...`; marker keys and `evidence` identical to the v0.21.1 marker (only `ts` and the script path differ); pre-fix: rc 3, no marker, interim text written as the artifact |
| T-0349 | error stdin + complete transcript stays a failure | pass | same, r4b | HEAD rc 1 with marker; pre-fix rc 0 (recorded as done) |
| T-0349 | transcript with tool-use turns before the final text | pass | same, r5 (tool-use + text `x`, tool-only, full) and r5b (full, then a tool-only turn) | rc 0, full report both times |
| T-0349 | truncated stdin + max_tokens transcript is refused as truncated | pass | same, r9 | rc 1, attempt error `the builder final message in the transcript is truncated (stop_reason max_tokens)`; pre-fix rc 0 recorded the stub |
| T-0349 | complete stdin wins over an interim or a max_tokens transcript | pass | same, r7, r10 | rc 0, stdin recorded |
| T-0349 | new selftest cases fail on the pre-fix logic, pass on HEAD | pass | HEAD `dispatch.py` with the pre-fix `record` block spliced in (`/tmp/verify-v2-mix.*`), `dispatch.py selftest` | `FAIL: record t1: result is the transcript final message`, `FAIL: record t2: error stdin stays a failure with the limit marker despite an interim heading`, `dispatch selftest: FAIL`; HEAD `dispatch selftest: PASS` (277 lines, 0 FAIL) |
| T-0350 | after one recorded sub-agent solo the next solo in the checkout keeps the checkout | pass | `bash ctl/t0350.sh <HEAD scripts>` | seq1 `worktree=<none>` (1 marker), `record seq1` rc 0 `solo recorded; live marker cleared` (0 markers), seq2 `worktree=<none>`; pre-fix: record rc 2 `is not a dispatch file (missing result, tmp_prefix, ...)`, seq2 and seq3 each got `.worktrees/solo-seq*` |
| T-0350 | record with a transcript prices the solo row and clears the marker | pass | same, `record seq2 --transcript tr.jsonl` | rc 0 `solo recorded, cost_usd 0.513394; live marker cleared`; runs.jsonl row now carries `usage` and `cost_usd` |
| T-0350 | two live solos: the second uses a worktree | pass | same, seq3 live then `par` | `worktree=/private/tmp/.../.worktrees/solo-par`, stderr `another solo is live in this checkout; using worktree solo-par (--no-worktree to stay)` |
| T-0350 | recording the same solo twice is harmless | pass | same, final `record seq1` | rc 0, the other live marker (seq3) untouched |
| T-0350 | new selftest fails on the pre-fix dispatch.py, passes on HEAD | pass | HEAD `solo_run.py` over the pre-fix scripts dir | `solo_run selftest FAIL: recorded solo: record exits 0 and clears the marker, the next solo keeps the checkout`; HEAD `solo_run selftest: PASS` |
| T-0350 | the closing step is stated in the agent texts | pass (see finding 1) | `grep -n record agents/conductor.md agents/solo*.md` | conductor.md line 21 `when the sub-agent ends, run dispatch.py record <ticket folder>/<name>.dispatch.json to close it and clear its live marker`; solo.md, solo-L1..L3.md each hold the paragraph |
| T-0351 | check.py fails when an agent source is edited without regenerating (observed failing on the pre-fix check.py first) | pass | planted `planted edit` line on `agents/conductor.md` in `/tmp/verify-v2-plant.*`; pre-fix `check.py` then HEAD `check.py` | pre-fix: `ok: 19 role levels, 9 agents, 22 generated definitions checked` rc 0 (the defect); HEAD: `FAIL Codex generated agent definitions drift from their sources; run codex_roles.py generate: generated agent drift: .../sdlc-conductor-l1.toml` rc 1; a planted `agents/solo.md` edit fails both the Codex and the Claude guard |
| T-0351 | the guard passes on the clean tree, three runs | pass | `python3 plugins/sdlc-lite/scripts/check.py` x3 (`logs/check1..3.log`) | `ok: 19 role levels, 9 agents, 22 generated definitions checked`, rc 0 each; wall time 4.7 s (pre-fix 2.7 s) |
| T-0351 | `codex_roles.py generate --check` and `claude_roles.py generate --check` pass on HEAD | pass | both commands | `Codex agent definitions verified`; `Claude agent definitions verified (22 files)` |
| T-0351 | docs_check stops warning on `.sdlc/verify-*`; 13 warnings go to 11 | pass | HEAD `docs_check.py`; pre-fix `docs_check.py` on the HEAD tree | HEAD `0 errors, 11 warnings (B-2a 3, B-3a 3, D-10 3, D-11 2)`, no `verify-` line; pre-fix script on the same tree `14 warnings (B-2a 6 ...)` (two verify folders plus one for `verify-maisonfix` added since), pre-fix tree 13 |
| T-0351 | docs_check selftest (boundary gate with the `verify-x/verdict.md` fixture) | pass | `docs_check.py selftest` | `gate boundary: positive ok, negative ok`, `docs_check selftest: PASS` |
| finding 1 | `fanout.py selftest` green on HEAD | pass | `python3 plugins/sdlc-lite/scripts/fanout.py selftest` | `fanout selftest: PASS`; also PASS at `57274103`, so the T-0346 regression was already repaired before these lanes |
| finding 2 | generate --check both pass; the T-0351 guard bites on a planted edit | pass | rows above | see T-0351 |
| findings 3, 4 | record cases | pass | rows above | see T-0349 |
| finding 5 | sequential solos not forced into a worktree; two live solos use one | pass | rows above | see T-0350 |
| release | `tickets.py check` | pass | `python3 plugins/sdlc-lite/scripts/tickets.py check` | rc 0; the pre-existing placeholder-text and flat-layout warnings only |
| release | `scripts/check-packaging.py` | pass | | `PASS: catalog parity, identity, skill routes, hook isolation and context links` |
| release | `codex-selftest.py` | pass | | rc 0, `Installed 28 project agents ...` |
| release | selftests: dispatch, solo_run, steps, tickets, fanout, budget | pass | `logs/st-*.log` | each `... selftest: PASS`, rc 0 |
| release | hook selftest | pass | `bash plugins/sdlc-lite/scripts/hook-selftest.sh` | `hook selftest: PASS` first run, no rerun needed |
| release | `check.sh` once | CHECKSH_RESULT | `bash plugins/sdlc-lite/scripts/check.sh` (`logs/check-sh.log`) | CHECKSH_EXCERPT |
| release | L1 to L5 guard (check.py item 43) clean | pass | part of the check.py runs above | no `one level system` line, rc 0 |
| regression | other callers of the changed functions | pass | `grep -rn "solo_dispatch\|regen_drift\|startswith('verify-')\|\.complete(\|import solo_run" plugins scripts` | `solo_run.complete` callers: `dispatch.py` main (new) and `fanout.py` land (unchanged); `solo_dispatch` and `regen_drift` have only their in-file callers; `transcript_final` is called only from `record`; `LIMIT_RE` users (`limit_marker`, `solo_run.py` 196) unchanged |
| regression | `steps.py lint` old vs new over 14 existing plans | pass | loop over `/tmp/verify-maisonfix/ctl/plans.txt`, `cmp` stdout+stderr and rc | `plans=14 same=14` |
| regression | em or en dashes in lane-authored lines | pass | `git diff 57274103 e3b72ad1 \| grep '^+' \| grep -P '[\x{2014}\x{2013}]'` | no hits |
| regression | `git diff --check 57274103 e3b72ad1` | pass | | no output, rc 0 |

## Findings

None is a release blocker.

1. Record defect, T-0350 (🟡): the new paragraph in `agents/solo.md`, `solo-L1.md`, `solo-L2.md`, `solo-L3.md` was inserted between the sentence `The headless start ... is the same command with --exec, or raw and unrecorded:` and the raw `claude -p` command it introduces, so the colon now points at the record paragraph and the command line floats after it. Root cause: the lane appended at a line number instead of after the paragraph it belongs to (the Agent-spawn sentence). Fix: move the paragraph above the "headless start" sentence, regenerate `solo-L1..L3.md` and the Codex TOMLs, run check.py. Size S.

2. Neighbour, T-0349 (🟡): stdin that is an error but matches neither `LIMIT_RE` nor `^(API )?Error:` (control r6: `Agent terminated unexpectedly`) still yields to the transcript; with a complete final message it is recorded as done (r6b rc 0), with an interim `## Status\nworking` it fails only because validation rejects `working` (rc 3). The ticket text scoped the error patterns, so this is within spec, but a stopped or killed sub-agent whose last text was a valid-looking report would be closed as completed. Root cause: `is_err` is pattern-based; the empty-or-prefix rule the earlier verdict proposed (fall back only when stdin is empty or a prefix of the final message) was not taken. Fix: treat any non-empty stdin without a heading that is not a prefix of the final message as the error. Size S, with a selftest case.

3. Record gap, T-0350 (🟡): `skills/agent/SKILL.md` step 3 (the `solo` row) names `solo_run.py` and the Agent spawn but not the closing `dispatch.py record` step; it defers to `agents/solo.md` "## Start", which now has it, so the contract is reachable but not where the skill lists the other steps. `dispatch.py`'s usage docstring (line 5) also does not say `record` accepts a `solo_run.py` dispatch file. Size S.

4. Behaviour note, T-0350: `dispatch.py record` on a solo dispatch file ignores stdin, `--agent-id`, `--tool-uses` and `--duration-ms` silently (only `--transcript` and `--tokens` reach `solo_run.complete`), so the solo runs.jsonl row never gets an `agent_id` or duration. Not in the ticket's Done-when; ticketable for the cost record. Size S.

5. Cost, T-0351: check.py now takes 4.7 s against 2.7 s because it runs both generate --check scripts twice (once on the tree, once on a full `copytree` of the plugin for the negative control). Acceptable for a gate run three times per release; noting for the performance pillar.

6. Process: the three `## Closed` notes again say only "delivered by the solo agent" although each Done-when asked for the defect "observed, failing on the current main first"; the controls above show all three were real on `57274103`, so no code was written for a non-defect, but the record does not say so (same as finding 8 of the earlier verdict).

## What was run

See the Criteria table. Control scripts: `ctl/rc.sh` (release checks), `ctl/old.sh` (pre-fix selftests: dispatch, solo_run, check, docs_check, fanout all PASS at `57274103`), `ctl/t0349.sh` (15 record cases on HEAD, pre-fix, v0.21.1), `ctl/t0350.sh` (sequential, priced, parallel, repeated record). Limitations: no live Claude session was started (no sub-agent ran; `dispatch.py record` was driven with stdin and jsonl fixtures); the T-0350 Codex path was not exercised (the change is Claude-only); `codex-selftest.py` ran offline fixtures, not a live Codex host.
