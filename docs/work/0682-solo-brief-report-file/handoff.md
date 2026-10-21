---
id: T-0682
title: "solo_run.py briefs carry Report file and pointer lines, and record reads the solo report file"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo sub-agent writes its report to a file in the records dir and ends with a one-line pointer, as every `prepare` role does since T-0646, so solo completion notices stay short and `dispatch.py record` reads the report from the file.

## Intent
- Do: in `dispatch_json` (`plugins/sdlc-lite/scripts/solo_run.py`, the prompt built near line 190) and in `subagent_dispatch` (`plugins/sdlc-lite/scripts/fanout.py` near line 1980, prompt `SOLO_SUBAGENT_PROMPT` near line 520), add the `Report file: <records dir>/<name>.md` line (write the report there with the Write tool, check it with `results.py solo-report <file> --handoff <handoff>` when it says `verify: needed`) and the `End with one line: solo <status> <path>` line, through one shared helper; store the path as `result` in the dispatch JSON and as `file` in the solo `runs.jsonl` row (`build_record` near line 279 writes `file: ''` today).
- Do: in `dispatch.py` main, the solo branch of `record` (near line 2112, `solo_dispatch`), read the report at the dispatch's `result`: when present print its path; when missing, take the transcript's final message as `record` does for other roles and write it there; with neither, exit 2 and leave the row and live marker unchanged. Update `plugins/sdlc-lite/agents/solo.md` `## Output` (near line 59) to say the report goes to the brief's Report file and the final message is the pointer line, then run `claude_roles.py generate` and `codex_roles.py generate`.
- Do: add selftest cases: the `solo_run.py run` dispatch prompt carries `Report file:` and `End with one line`; `fanout.py prep` solo dispatch carries both; `dispatch.py record` on a solo dispatch with the report file present prints its path and the runs row's `file` names it.
- Non-goals: changing the verifier flow after a solo; the `Ports:` line (T-0693).
- Done when: the criteria pass.

## Context
Source: GitHub issue #10 (reopened), ui-kit 0.27 vs 0.28 measurement 2026-10-21.
All 11 solo briefs under 0.28.1 lack both lines; the 0173 solo notice was 1,833 chars against 350 for a 0.28.1 verifier pointer; in 0.27, 197 of 453 notices were truncated and 12 results were hand-fed to `record`. Solos were 87 of 413 runs. Confirmed on main 8624f984: `prepare` adds the lines at `plugins/sdlc-lite/scripts/dispatch.py:1261` to `1266`; `solo_run.py:190` and `fanout.py` `SOLO_SUBAGENT_PROMPT` add neither; the solo record branch at `dispatch.py:2112` only prices the row (`solo_run.complete`, `solo_run.py:358`). Because sub-agent solo rows carry `file: ''`, `tickets.solo_report` (`plugins/sdlc-lite/scripts/tickets.py:2356`) finds no report for them, so the tests-gate waiver cannot read one; setting `file` fixes that too.

## Constraints
The spawn gate finds the dispatch record from the `Handoff` line on line 2 of the prompt; keep lines 1 to 3 in place and add the new lines after `Artifacts dir`. Generated agent files are regenerated, not hand-edited. T-0693 adds a line to the same prompts; whichever lands second rebases.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0 with the new prompt case, and it fails with the prompt change reverted.
2. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the new prep case.
3. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new solo record case.
4. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
5. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
6. `git diff --check <base sha>` exits 0.

## Outcome
- `solo_run.report_lines` is the shared helper: `solo_run.dispatch_json` and `fanout.subagent_dispatch` (`SOLO_SUBAGENT_PROMPT`) add `Report file: <records dir>/<name>.md` and `End with one line: solo <status> <path>` right after the Artifacts dir line; the dispatch JSON stores the path as `result` and the solo `runs.jsonl` row as `file` (fanout: `write_solo_row(..., file)`, an absolute path in the prep checkout's records dir).
- `dispatch.py record` on a solo dispatch with a `result` (`solo_report_file`): the file present prints `solo report: <path>`; missing, it writes the transcript's final message there (a lone `solo ...` pointer or a max_tokens stop is no report); with neither it exits 2 before pricing, so the row and live marker are unchanged. A dispatch with no `result` (older records) records as before.
- `agents/solo.md` Output and the record sentence updated; Claude and Codex agents regenerated.
- Checks: `solo_run.py selftest`, `fanout.py selftest`, `dispatch.py selftest` exit 0; `claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0; `check.py` exit 0; `git diff --check 1b6dc243` exit 0. With the code changes reverted (tests kept) the new solo_run, fanout and dispatch cases fail.
