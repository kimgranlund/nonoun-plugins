---
id: T-0181
title: "messages.py wait: one blocking call that returns when a message arrives"
type: feature
status: done
size: M
priority: P2
depends: [T-0180]
created: 2026-10-01
---

## Goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

## Intent
- Do: add `messages.py [--root DIR] wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]` to `plugins/sdlc-lite/scripts/messages.py`. It polls the same count that `count` uses (a valid message file in `new/<receiver>/`) every `--interval` seconds (default 5, minimum 1). As soon as at least one is present it exits 0 and prints one line per new message, `<id>\t<absolute path>`, sorted by id, and nothing else. When `--timeout` (default 120, maximum 600, minimum 1) elapses first it exits 3 and prints `no new messages`. `--timeout` and `--interval` out of range, non-integer, or a bad `--receiver` exit 1 with the usual `messages.py: <reason>` stderr line and nothing on stdout. `wait` never calls the claim, never moves, writes, or stamps anything, and never prints a body or front matter beyond the id and path.
- Cover it in the generated entry files (`ENTRY_TEMPLATE` Read section and Messenger section: `wait` is the cheaper alternative to a polling subagent while the parent is active; it still returns only into an active parent, so it does not wake an idle host, which T-0180 states), in `plugins/sdlc-lite/agents/messenger.md` (the messenger loop may use `wait`, or the parent may skip the messenger and call `wait` itself), in the module docstring and argparse help, in `docs/maintenance/sdlc-internals.md`, and in `docs/ticket-stages/design.md`. Regenerate Codex agents. Add `wait` to the selftest per the cases below; `scripts/check.sh` already runs the selftest.
- Non-goals: waking an idle host (T-0182); a daemon; changing any existing command; a new exit code besides 3 for timeout.
- Done when: the selftest cases below pass, `bash plugins/sdlc-lite/scripts/check.sh` and `python3 scripts/check-packaging.py` pass, `codex_roles.py generate --check` passes, and the live proof below is recorded.

## Context
Design: `docs/ticket-stages/design.md` (mailbox, transition table) and the T-0180 note. The existing `count` subcommand (`cmd_count`) counts valid files in `new/<receiver>/` through `load_or_none`; reuse that so a malformed file does not wake a waiter. The selftest drives the CLI as a subprocess in throwaway git repos with its own parser and literals (see the `Harness` class and `SELFTEST_CASES`); add cases in that style. A selftest wait must use short timeouts (1 to 3 seconds) so the suite stays fast.

Selftest cases (each a labelled entry in `SELFTEST_CASES`):
1. wait returns immediately (well under the interval) with exit 0 and `<id>\t<path>` when a message already exists, and the message file is unchanged (same bytes, still in `new/`, `read_time` empty).
2. wait returns with exit 0 after a message is sent mid-wait by another process (start `wait --timeout 10 --interval 1`, send after about 1.5 seconds, assert it exits 0 within the timeout with that message's id).
3. wait times out with exit 3, stdout exactly `no new messages`, and the mailbox tree is byte-identical before and after (no state change).
4. wait refuses a bad receiver, a timeout above the maximum, a timeout of 0, a non-integer interval: exit 1, nothing on stdout, nothing written.
5. wait ignores a malformed file in `new/<receiver>/` (no wake) and a message for another receiver.
6. wait never prints a body: a message whose body holds a unique marker string is not echoed.
7. Negative control: run the same checks against a copy of the script patched so `wait` claims the message (calls the claim, so the file moves to `read/`); the state-unchanged assertion must fail on the patched copy. The selftest proves it by building the patched copy in the temp dir and asserting case 1's no-state-change check fails there.

Live proof, recorded in `docs/validation/messages-wait-live-run.md` with a dated header, environment (host versions, models, plugin commit), exact commands, evidence files under `docs/validation/messages-wait-live-run/`, and limits (single run per arm, one machine): on Claude Code and on Codex, a fresh host process is given a prompt telling it to run `messages.py wait --receiver <harness> --timeout 120 --interval 2` as one command, then read, reply, and ack as `.sdlc/messages/AGENTS.md` says. A separate process sends the message about 20 seconds after the host starts. Show that the host's single `wait` call returned with the message id, that `send_time <= read_time <= ack_time`, and that the host made no polling calls of its own. Use the same project setup and isolation approach as `docs/validation/messages-live-run.md` (read its Environment and Method sections and its probe script `docs/validation/messages-live-run/probe.py`). Hosts: Claude Code with `--model sonnet --effort low` and Codex with the model of `docs/validation/messages-live-run.md`'s path-only arm. If a host cannot run, record the arm as unverified with the reason; never substitute fixtures.

## Constraints
Existing selftest cases, command outputs, exit codes, and entry-file procedures keep working unchanged. Message bodies stay data; `wait` adds no way to authorize anything. Generated Codex agent TOML files are never edited by hand. No em dashes anywhere.

## Plan review
split refused (plan defect), planner L2 result .sdlc/0181-messages-wait/planner-L2.md:
steps: .sdlc/0181-messages-wait/planner-L2.md step 2: acceptance criterion command does not parse: grep -qF "\
  bash: -c: line 0: unexpected EOF while looking for matching `"'
  bash: -c: line 1: syntax error: unexpected end of file
plan defect: replan this step (/chain 3)
plan review: replan: .sdlc/0181-messages-wait/plan-reviewer-L1-4.md
plan review: replan: step 3: goal coverage: the criteria accept a failed live proof, so step 3 can verify pass while the handoff's Done-when ("the live proof below is recorded", showing the single `wait` call returned the id, ordered stamps, and no polling) is unmet. The handoff allows only one fallback, "If a host cannot run, record the arm as unverified with the reason"; a `result=fail` arm is not an accepted end state, and no step or criterion routes it anywhere.
plan review: replan: step 3: acceptance criteria: no criterion can go red on the behavior the step exists to prove. With both arms recorded as `result=fail reason=...` or `result=unverified reason=...`, every step 3 criterion is green.
plan review: replan: step 1: acceptance criteria: the negative control (selftest case 7) asserts only that `st_wait_present` raises `SelftestFail` on the patched copy, so it cannot tell which assertion fired. A patched copy that exits nonzero for any other reason (a broken replacement line, a traceback) fails the earlier "exit 0" assertion, raises the same `SelftestFail`, and the case prints `ok`. The handoff requires that "the state-unchanged assertion must fail on the patched copy". The plan defines the distinguishing message `wait changed the mailbox` but case 7 never matches on it, and criterion 1 only checks the `ok: wait: a claiming wait is caught` label.
plan review: replan: step 1: builder readiness: selftest case 4 lists the `b.refused` calls as `--timeout 601`, `--timeout 0`, `--timeout 1.5`, `--interval abc`, `--interval 0` with no `--receiver bob` and no `want=`. The Do validates the receiver first, and `need()` refuses a missing `--receiver` with exit 1, so a literal build passes all five on the missing-receiver branch and never reaches the timeout or interval checks. `Box.refused` has a `want` parameter for the stderr text that the Do does not use.
plan review: replan: step 2: builder readiness: level L2 does not fit the builder table row "Small change in a known pattern, 1 to 3 files". The step hand-edits four files (`messages.py`, `agents/messenger.md`, `docs/maintenance/sdlc-internals.md`, `docs/ticket-stages/design.md`), regenerates a fifth, and leaves the entry-file sentences for the builder to compose from "It says that ..." descriptions.

## Closed

2026-10-01: built and verified step by step (5 steps) by /chain; live proof on Claude and Codex in docs/validation/messages-wait-live-run.md
