# Solo budget gate live run

Recorded: 2026-10-05. Live run for ticket T-0229: `solo_run.py` checks a ticket's budget before it starts a solo session, and `--new-task` lets a solo run with no named ticket leave a `role solo` record. Three real headless solo sessions, one refused before it started.

## Environment

- `claude --version`: `2.1.289 (Claude Code)` ([`claude-version.txt`](solo-budget-gate-live-run/claude-version.txt)).
- Plugin commit `1a1d903` ([`plugin-commit.txt`](solo-budget-gate-live-run/plugin-commit.txt)); `git status --porcelain -- plugins` printed nothing ([`plugins-dirty.txt`](solo-budget-gate-live-run/plugins-dirty.txt) is empty). Every command used this worktree's `plugins/sdlc-lite`.
- Models, from the session records: both sessions ran `claude-sonnet-5-5` (the `modelUsage` key in [`acked-raw-result.json`](solo-budget-gate-live-run/acked-raw-result.json) and [`newtask-raw-result.json`](solo-budget-gate-live-run/newtask-raw-result.json)); the `runs.jsonl` records say `model sonnet`, `effort low`, level `L1` (tier S).
- A throwaway Git project under `/tmp` ([`workdir.txt`](solo-budget-gate-live-run/workdir.txt)), not kept. Each command ran through [`env-wrapper.sh`](solo-budget-gate-live-run/env-wrapper.sh), which removes inherited Claude Code and `SDLC_*` variables because this run was itself launched from a Claude Code session. Run window 2026-10-05T05:53:45Z to 05:54:11Z ([`start.txt`](solo-budget-gate-live-run/start.txt), [`end.txt`](solo-budget-gate-live-run/end.txt)).

## What ran

Fixture: ticket `.sdlc/over/handoff.md` with `budget_usd: 1` and one seeded `runs.jsonl` line (a builder record, `cost_usd` 0.9), so the ticket stood at 90 percent ([`budget-before.txt`](solo-budget-gate-live-run/budget-before.txt): `percent: 90`, `state: warn`, `budget rc=3`).

| Step | Command | Result |
|---|---|---|
| 1 refused | `solo_run.py run --task-dir .sdlc/over --tier S --brief "Create hello.txt ..."` | exit 4, stderr `solo_run.py: budget 90%: ask the user; budget.py ack` ([`refused-rc.txt`](solo-budget-gate-live-run/refused-rc.txt), [`refused-stderr.txt`](solo-budget-gate-live-run/refused-stderr.txt)); stdout empty ([`refused-stdout.txt`](solo-budget-gate-live-run/refused-stdout.txt)); the seeded `runs.jsonl` was still one line when I counted it (`wc -l` printed 1 straight after the refusal; that count is in the run log, not a committed file), and the project root listing printed nothing, so no `hello.txt` existed then (also not a committed file); the committed evidence that no session started is exit 4 with empty stdout and the later record count of two lines in [`over-runs.jsonl`](solo-budget-gate-live-run/over-runs.jsonl) (the seed plus the acked run only) |
| 2 acked | `budget.py ack .sdlc/over --usd 5 --reason ...`, then the same `solo_run.py` command | `ack rc=0` ([`ack.txt`](solo-budget-gate-live-run/ack.txt), [`budget-ack.md`](solo-budget-gate-live-run/budget-ack.md)); the session ran, exit 0, `hello.txt` holds `ok` ([`hello.txt`](solo-budget-gate-live-run/hello.txt)), one `role solo` line appended with `cost_usd` 0.1274452, 2 turns ([`over-runs.jsonl`](solo-budget-gate-live-run/over-runs.jsonl)); `budget.py status` then reads spend 1.03, budget 5, percent 20, `state: ok` ([`budget-after.txt`](solo-budget-gate-live-run/budget-after.txt)) |
| 3 no ticket | `solo_run.py run --new-task quick-note --tier S --brief "Create note.txt ..."` | exit 0; `.sdlc/quick-note/handoff.md` created from the brief ([`quick-note-handoff.md`](solo-budget-gate-live-run/quick-note-handoff.md)); `note.txt` holds `hi` ([`note.txt`](solo-budget-gate-live-run/note.txt)); one `role solo` line with `cost_usd` 0.121484 ([`quick-note-runs.jsonl`](solo-budget-gate-live-run/quick-note-runs.jsonl), [`newtask-record.txt`](solo-budget-gate-live-run/newtask-record.txt)) |

Counted spend for the three sessions: $0.2489 recorded by the wrapper (steps 2 and 3), $0 for step 1.

## Negative controls and selftests

- Disabling the gate (`budget_hold` returning `None`) fails the `solo_run.py` selftest (nine FAIL lines, rc 1) and `fanout.py` selftest case 18 (three labels: the 80 percent ticket merged, the outcome did not name the gate, and a solo session started). Restored, both pass. I ran both mutants on disk in this worktree.
- `solo_run.py selftest` covers the 80 percent boundary (exactly 80 refused, 79 starts), over budget refused, an ack letting the same ticket start, a ticket with no budget and a task folder with no ticket id never blocked, the stderr message naming `budget.py ack`, `--new-task` writing a folder and a record, a refused repeat slug and a bad slug, the default slug under `ticket_root: tickets`, and the CLI end to end.
- `fanout.py selftest` case 18: a solo lane for a ticket at 80 percent of its budget stops as `driver failed rc=4 (budget gate: budget.py ack)` and starts no session; the control at 70 percent merges.
- `check.py` item 28 names the gate phrases in `solo_run.py`, `fanout.py`, `agents/solo.md`, `skills/agent/SKILL.md`, and `skills/fanout/SKILL.md`, with a negative control per phrase.

## Limits

- One trial of each step, one machine, Claude Code only. The Codex solo path was not run: it still records cost null, so a Codex solo run can never raise a ticket's spend and the gate does not stop it for spend it cannot see.
- The gate reads recorded cost, so it stops a start only after earlier runs pushed the ticket to 80 percent. A single solo session is not capped while it runs.
- A `full` fanout lane starts a conductor session, which neither passes through the gate nor writes a record.
- The raw command in `agents/solo.md` is still a fallback that skips both the gate and the record.
- The gate was exercised live through `solo_run.py` directly. A fanout lane hitting the gate is covered by the selftest (case 18) only.
- The `/agent solo` skill text was changed to call `--new-task`; no model followed that text in this run, which called the wrapper by hand.
