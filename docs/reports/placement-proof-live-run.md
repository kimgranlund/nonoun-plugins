---
date: 2026-10-06
---
# Placement proof for the context registry, live run

Recorded: 2026-10-06 (scored runs 2026-10-07 01:20 to about 01:31 UTC). Ticket T-0248. Tests the claim in [the docs schema design](../planning/docs-schema/design.md), "The context registry pattern": a fresh session given only a path and a brief places a new document in the right home more often when the registry is in the entry files. One run per cell. No significance is claimed.

## Verdict

Not proven. The pass rule was fixed before any run: for a session type, proven only if the registry arm places at least 10 of 12 briefs correctly and beats the control arm by at least 3 briefs, and proven across all types only if every type run passes.

| Session type | Registry | Control | Margin | Pass rule |
| --- | --- | --- | --- | --- |
| Claude Code headless (`claude -p`) | 12/12 | 8/12 | +4 | pass |
| `solo` agent, headless | 11/12 | 10/12 | +1 | fail (margin under 3) |
| Codex `codex exec` from `docs/` | 12/12 | 10/12 | +2 | fail (margin under 3) |
| Codex native subagent | 12/12 | 9/12 | +3 | pass |
| Interactive Claude session | not run | not run | none | limit, see Limits |

Negative control: the control arm misplaced more briefs than the registry arm in all four types that ran (4 against 0, 2 against 1, 2 against 0, 3 against 0), so the rule "if it does not, the registry is not shown to help" does not fire. The registry is not shown to help enough to pass the fixed rule for two types, `solo` and `codex exec`.

Status line recorded in the design: grounded in the cited evidence, placement unproven. Failing types: `solo` agent, Codex `codex exec`. Not run: interactive Claude.

Read the two passes with care. The margin of 4 for `claude -p` includes two control cells where the session wrote nothing (B05 and B11), and the margin of 3 for the Codex subagent includes one (B04, answered in chat). The fixed rule counts a session that writes nothing as wrong, and that rule governs. Counting only wrong-home placements, every type's margin is 1 or 2 and none passes. See Findings.

## Fixture

Built by `build_fixture.py` in [the evidence folder](placement-proof-live-run/), run once into `/tmp/placement-proof-0248/fixtures/{registry,control}`. Each arm is a git repository with one commit. The script writes literal text; it is not `render_registry` and nothing keeps the registry in sync with the layout afterwards.

Both arms hold:

- `docs/` with one existing document in each of the nine homes (`specs/`, `planning/`, `decisions/`, `references/`, `guides/`, `reports/`, `assets/`, `archive/`, `other/`), `docs/layout.md` listing the nine home names under `## Homes`, a `docs/AGENTS.md`, and a `docs/CLAUDE.md` of `@AGENTS.md`.
- `.sdlc/` with `config`, `roadmap.md`, `notes.md` (one block), a ticket folder `0007-retry-rule/` (`handoff.md`, `builder-L2.md`), a closed ticket `.0003-board-colors/`, one old message under `messages/done/codex/`, one file each in `evals/` and `proposals/`, an `AGENTS.md`, and a `CLAUDE.md` of `@AGENTS.md`.

The registry arm adds:

- In `docs/AGENTS.md`, one managed block with the one-sentence statement of the system (including that work records live in `.sdlc/`), the how-to-use line, the nine-row `row` table, the nine-step `## Decide` list and a five-line add-a-document checklist.
- A card (`AGENTS.md` plus a `CLAUDE.md` of `@AGENTS.md`) in each of the nine docs homes, with the eleven fields.
- `## Kinds` (eleven columns) and `## Decide` in `docs/layout.md`.
- `.sdlc/layout.md` with the ten-row `## Kinds` and the five-step `## Decide`, the same block layout in `.sdlc/AGENTS.md`, and cards in `.sdlc/messages/`, `.sdlc/evals/` and `.sdlc/proposals/`.

The control arm is the registry arm with those removed and nothing else changed. `docs/AGENTS.md` and `.sdlc/AGENTS.md` keep one plain sentence each in place of the block. The control keeps the nine home names in `docs/layout.md` and one existing document per home as a naming example, so the test measures what the registry adds on top of folder names and examples, not on top of nothing. Tree hashes of both arms, the answer key and the brief file are in [`sealed.txt`](placement-proof-live-run/sealed.txt), written at 2026-10-07 01:17:48 UTC before any session started.

## Briefs and answer key

Twelve briefs in [`briefs.json`](placement-proof-live-run/briefs.json), the answer key in [`answer-key.json`](placement-proof-live-run/answer-key.json). No brief names a home.

| Brief | Request | Start folder | Accepted home |
| --- | --- | --- | --- |
| B01 | design of an approved but unbuilt feature (boundary) | `docs/` | `docs/specs/`, alternate `docs/planning/` |
| B02 | proposal under review, nothing decided | `docs/` | `docs/planning/` |
| B03 | one decision with reason and cost | `docs/` | `docs/decisions/` |
| B04 | command cheat sheet to restart a failed ticket (boundary) | `docs/` | `docs/references/`, alternate `docs/guides/` |
| B05 | numbered steps to rotate the model table | `docs/` | `docs/guides/` |
| B06 | today's benchmark results | `docs/` | `docs/reports/` |
| B07 | an SVG file to embed | `docs/` | `docs/assets/` |
| B08 | retire an out-of-date guide, keep it for history | `docs/` | `docs/archive/` |
| B09 | unsorted loose notes | `docs/` | `docs/other/` |
| B10 | verifier result for ticket T-0007 | `docs/` | `.sdlc/0007-retry-rule/` |
| B11 | steps to add a role to the runner | `.sdlc/` | `docs/guides/` |
| B12 | follow-up from closing T-0007, not a ticket | `docs/` | `.sdlc/notes.md` |

Scoring rule, in the answer key: a run's placement is the paths it added or renamed to, or, when it added none, the existing files it modified. A run is correct when that set is not empty and every path starts with an accepted prefix. A session that writes nothing is wrong. Extra edits to other existing files are not placements. Placement is read with `git diff --cached -M --name-status` against the commit each copy started from, and the copy is then committed.

## Method

Every cell is one fresh session on a fresh copy of one fixture arm in `/tmp`, outside any repository that holds an entry file. The prompt is two parts and nothing else: `Path: <start folder in the copy>` and the brief. The start folder is also the working directory. 12 briefs, 2 arms, 4 types, 96 scored cells, one run each. Three cells ran at a time per type, all four types at once, with the host at load average 19.6.

| Type | Command |
| --- | --- |
| claude | `claude -p --model sonnet --effort low --setting-sources project --disable-slash-commands --strict-mcp-config --dangerously-skip-permissions --no-session-persistence --output-format stream-json --verbose` (Claude Code 2.1.292, `claude-sonnet-5-5`) |
| solo | the same, plus `--plugin-dir plugins/sdlc-lite --agent sdlc-lite:solo` and `SDLC_ROLE=solo`; no ticket, no `solo_run.py` (it would create a task folder in the fixture) |
| codex | `codex exec -C <start> -s workspace-write --add-dir <fixture root> -m gpt-6.1-sol -c model_reasoning_effort="low" --ephemeral --json` (Codex CLI 0.160.0) |
| codex-sub | the same, with a parent prompt that starts one native subagent and hands it the path and brief as its whole task; the subagent got no other instruction |

A check after the runs confirmed the Claude sessions load no user-level instruction file and do load the project `CLAUDE.md` and the `AGENTS.md` it imports (`--setting-sources project`). Codex was not checked the same way. Four pilot cells (one per type, registry arm, brief P0 outside the twelve) tested the plumbing and are not scored.

## Per-run placements

`ok` means the placement matches an accepted home, `WRONG` that it does not, `none` that the session wrote no file. The first added path is shown. Full records (all paths, tools used, final message, tokens or cost) are in [`runs.jsonl`](placement-proof-live-run/runs.jsonl).

| Brief | Accepted home | claude registry | claude control | solo registry | solo control | codex registry | codex control | codex-sub registry | codex-sub control |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | `docs/specs/` or `docs/planning/` | ok: `docs/planning/notification-digest-design.md` | ok: `docs/specs/notification-digest.md` | ok: `docs/planning/notification-digest-design.md` | ok: `docs/specs/notification-digest.md` | ok: `docs/planning/notification-digest-design.md` | ok: `docs/specs/notification-digest.md` | ok: `docs/planning/notification-digest.md` | ok: `docs/specs/notification-digest.md` |
| B02 | `docs/planning/` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` | ok: `docs/planning/board-output-cache-proposal.md` | ok: `docs/planning/board-render-cache-proposal.md` |
| B03 | `docs/decisions/` | ok: `docs/decisions/0002-use-jsonl-for-run-logs.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` | ok: `docs/decisions/0002-run-logs-as-json-lines.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` | ok: `docs/decisions/0002-use-json-lines-for-run-logs.md` |
| B04 | `docs/references/` or `docs/guides/` | ok: `docs/references/restart-failed-ticket-commands.md` | ok: `docs/guides/restart-failed-ticket-cheatsheet.md` | ok: `docs/references/restart-failed-ticket-cheatsheet.md` | ok: `docs/guides/restart-failed-ticket-cheatsheet.md` | ok: `docs/references/failed-ticket-commands.md` | none (wrote nothing) | ok: `docs/references/restart-failed-ticket-commands.md` | none (wrote nothing) |
| B05 | `docs/guides/` | ok: `docs/guides/rotate-the-model-table.md` | none (wrote nothing) | ok: `docs/guides/rotate-the-model-table.md` | ok: `docs/guides/rotate-the-model-table.md` | ok: `docs/guides/rotate-the-model-table.md` | ok: `docs/guides/rotate-the-model-table.md` | ok: `docs/guides/rotate-the-model-table.md` | ok: `docs/guides/rotate-the-model-table.md` |
| B06 | `docs/reports/` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` | ok: `docs/reports/2026-10-06-benchmark.md` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` | ok: `docs/reports/2026-10-06-benchmark.md` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` | ok: `docs/reports/2026-10-06-lane-scripts-benchmark.md` |
| B07 | `docs/assets/` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` | ok: `docs/assets/board-flow.svg` |
| B08 | `docs/archive/` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` | ok: `docs/archive/resume-a-stopped-run.md` |
| B09 | `docs/other/` | ok: `docs/other/unsorted-notes-2026-10.md` | ok: `docs/other/unsorted-notes-2026-10.md` | ok: `docs/other/unsorted-notes-2026-10.md` | ok: `docs/other/unsorted-notes-2026-10.md` | ok: `docs/other/unsorted-call-notes.md` | ok: `docs/other/unsorted-notes-2026-09.md` | ok: `docs/other/unsorted-notes-2026-09.md` | ok: `docs/other/unsorted-notes-2026-09.md` |
| B10 | `.sdlc/0007-retry-rule/` | ok: `.sdlc/0007-retry-rule/verifier-L2.md` | WRONG: `docs/reports/2026-10-06-T-0007-verification.md` | ok: `.sdlc/0007-retry-rule/verifier-L3.md` | WRONG: `docs/reports/2026-10-06-T-0007-verifier-result.md` | ok: `.sdlc/0007-retry-rule/verifier-L1.md` | WRONG: `docs/reports/T-0007-verifier-result.md` | ok: `.sdlc/0007-retry-rule/verifier-L2.md` | WRONG: `docs/reports/T-0007-verifier-result.md` |
| B11 | `docs/guides/` | ok: `docs/guides/add-a-role-to-the-runner.md` | none (wrote nothing) | none (wrote nothing) | ok: `docs/guides/add-a-role.md` | ok: `docs/guides/add-a-runner-role.md` | ok: `docs/guides/add-a-runner-role.md` | ok: `docs/guides/add-a-runner-role.md` | ok: `docs/guides/add-a-runner-role.md` |
| B12 | `.sdlc/notes.md` | ok: `.sdlc/notes.md` | WRONG: `docs/planning/retry-timeout-default-followup.md` | ok: `.sdlc/notes.md` | WRONG: `docs/planning/retry-timeout-default-followup.md` | ok: `.sdlc/notes.md` | ok: `.sdlc/notes.md` | ok: `.sdlc/notes.md` | WRONG: `docs/planning/follow-ups.md` |

Per-type totals by brief group:

| Type and arm | Docs homes B01 to B09 | `.sdlc` or `docs/` B10 to B12 | Wrote nothing | Wrong home |
| --- | --- | --- | --- | --- |
| claude registry | 9/9 | 3/3 | 0 | 0 |
| claude control | 8/9 | 0/3 | 2 | 2 |
| solo registry | 9/9 | 2/3 | 1 | 0 |
| solo control | 9/9 | 1/3 | 0 | 2 |
| codex registry | 9/9 | 3/3 | 0 | 0 |
| codex control | 8/9 | 2/3 | 1 | 1 |
| codex-sub registry | 9/9 | 3/3 | 0 | 0 |
| codex-sub control | 8/9 | 1/3 | 1 | 2 |

## Findings

These are readings of this run, not hypotheses set before it.

- Without the registry, all four types placed every written docs-home brief correctly: the three control misses among B01 to B09 are sessions that wrote nothing (claude B05, codex B04, codex-sub B04). The control kept the nine home names in `layout.md` and one example document per home, which is probably enough for that part.
- The difference sits in the `.sdlc` versus `docs/` briefs. In the control arm they went to the wrong system 7 times out of 12 cells (B10 verifier result into `docs/reports/` in all four types; B12 follow-up into `docs/planning/` for claude, solo and codex-sub) and 4 of 12 were correct. In the registry arm 11 of 12 were correct and the one miss wrote nothing.
- The registry moved boundary choices toward the registry's primary home: B01 went to `planning/` in all four registry cells and to `specs/` in all four control cells; B04 went to `references/` in all four registry cells and to `guides/` in the two control cells that wrote a file (the other two wrote nothing).
- Two of the four passes depend on cells where the control wrote nothing. B05 and B11 named facts the fixture does not hold (the model table, the runner), so sessions without a registry sometimes declined to write rather than misplace. That is a weakness of those two briefs and not a placement effect.
- The `solo` agent has the fixture's registry loaded the same way as the others, yet its control arm placed 10 of 12; its one registry miss (B11) was a session that changed directory into the real plugin folder it knew from `--plugin-dir`, read those files and answered in chat without writing.
- Codex sessions often also edited `docs/layout.md` or another existing file to link the new document. Those edits are not placements and were not scored.

## Limits

- One run per cell, 12 briefs, no repeat runs: no significance, and a single re-draw could move a margin of 3 to 2. The Codex subagent pass sits exactly on the line.
- The briefs, fixture and design share an author. The answer key and fixture were sealed before any run, but the briefs were not reviewed by anyone else, and B05 and B11 name facts the fixture lacks.
- The control keeps home names and examples. A control with no `layout.md` or no existing documents was not run. No equal-length placebo block was run, so the result cannot separate "the registry" from "any longer entry file".
- Two models only: Sonnet 5.5 at low effort on Claude, `gpt-6.1-sol` at low effort on Codex. The Claude sessions were limited to project settings; Codex loads whatever global config the account has.
- The `solo` agent ran with no ticket and with the real sdlc-lite plugin readable through `--plugin-dir`.
- Codex native subagent: spawned from a parent `codex exec` prompt, so the parent had one extra instruction; the subagent got only the path and brief. The subagent's own events do not appear in the parent's JSON stream, so each pass is inferred from the created file with no parent file or shell event. Ten first attempts never started a subagent ("no rollout found for thread id", or a context load failure), which suggests the missing parent rollout of an ephemeral session (not tested), and one of those cells failed twice. They are kept in [`runs-infra-failed.jsonl`](placement-proof-live-run/runs-infra-failed.jsonl) and were rerun with the same command at one cell at a time; a cell that never started a subagent is not a placement and was not counted.
- Interactive Claude session: not run. The host has no terminal multiplexer (`tmux` is absent), the runner is a headless session, and no pty harness for the Claude TUI was built. The verdict does not depend on it: two types already fail.
- Cost. Claude cells: $1.07 for `claude -p`, $1.19 for `solo` (reported by the host), plus $0.23 for the pilot and a few cents for the loading check. Codex reports tokens and no cost: `codex exec` 2,734,756 input (2,453,120 cached) and 12,536 output over 24 cells; subagent 2,364,264 input (2,109,184 cached) and 8,004 output over 24 cells.

## Open

- The registry parts of T-0242 and T-0243 (`render_registry`, R-1, R-2, `.sdlc/layout.md`) wait on a pass; this run is not one, so the gate stays closed. Whether to run a stronger second pass or change the pattern is the user's call.
- Candidate follow-up tickets, not done here: a rerun with briefs that carry their own facts (B05, B11) and several runs per cell; a placebo arm of equal length; testing only the `.sdlc` versus `docs/` pointer, which is where the effect appeared.

## Files

In [`placement-proof-live-run/`](placement-proof-live-run/): `build_fixture.py` (builds both arms), `briefs.json`, `answer-key.json`, `sealed.txt` (hashes written before the runs), `run_cells.py` (runs a cell and scores), `runs.jsonl` (96 scored cells), `runs-infra-failed.jsonl` (10 cells that never started a subagent). To redo: `python3 build_fixture.py /tmp/placement-proof-0248/fixtures`, then `python3 run_cells.py run --type <type> --arm both`, then `python3 run_cells.py score`.
