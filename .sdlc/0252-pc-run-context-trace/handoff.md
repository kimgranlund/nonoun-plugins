---
id: T-0252
title: "Record which context a run loaded"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Make a role run record which entry files and references it actually read, so loaded context is inspectable.

## Intent
- Do: Extend plugins/sdlc-lite/scripts/run.sh and trace ingestion to write a loaded-context list (paths read, from the Claude stream-json log and the Codex rollout when present) into the runs.jsonl record.
- Non-goals: enforcing what a role may read.
- Done when: a live run on Claude Code records its read paths, the Codex arm records them or states 'rollout absent', and a negative control shows a missing log is reported, not silently empty.

## Context
Gap analysis R3 (docs/generative-constructs/progressive-context-gap-analysis.md): only routing_reason is stored today (run.sh:520-524). Codex rollout files can be absent (docs/reports/codex-conductor-solo-live-run.md:23). Do not edit run.sh while a role run uses it. Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.

## Acceptance criteria
Run from the repository root. The change is in `plugins/sdlc-lite/scripts/` (`run.sh`, `traces.py`, `run-selftest.sh`, `traces/`) and `docs/maintenance/sdlc-internals.md`.
1. Claude arm, live: in a throwaway git project with an `AGENTS.md` and `docs/guide.md` and a task handoff that tells the role to read both, `bash plugins/sdlc-lite/scripts/run.sh scout L1 <handoff>` exits 0 and the last `runs.jsonl` line has `loaded_context.source == "stream-json"` and `loaded_context.paths` naming the handoff, `AGENTS.md`, and `docs/guide.md`.
2. Codex arm: `python3 plugins/sdlc-lite/scripts/traces.py selftest -k context` exits 0 and its Codex cases show a rollout found by thread id gives the files its `cat`/`sed`/`head`/`tail` reads opened, and a log with no rollout, no thread id, or a thread id that is not a UUID-like token gives `{"status": "rollout absent"}`. Live: `SDLC_BACKEND=codex bash plugins/sdlc-lite/scripts/run.sh scout L1 <handoff>` records `loaded_context == {"status":"rollout absent"}` and prints `run.sh: loaded context not recorded: rollout absent` (`codex_exec.py` runs `codex exec --ephemeral`, which writes no rollout).
3. Negative control: `python3 plugins/sdlc-lite/scripts/traces.py context /tmp/no-such.log` prints `{"status": "log absent"}` and exits 0, never an empty `paths` list; an ingest of a result `.md` with no `.log` beside it gives its row `loaded_context == {"status": "log absent"}`; a `run.sh` whose collector exits 1 records `{"status":"collector failed"}`, prints the stderr line, and still exits 0. Each control goes red when the guarded line is mutated (a missing log returned as `paths: []`, `rollout absent` returned as `paths: []`, ingest dropping the status, run.sh's fallback returning `paths: []`).
4. `python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0, including the existing byte-identical re-ingest case (a record's keys stay in sorted order).
5. `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`.
6. `bash plugins/sdlc-lite/scripts/check.sh` exits 0, `python3 scripts/check-packaging.py` exits 0, and `git diff --check` is clean.
7. (guard) `git status --short` lists only these paths: `plugins/sdlc-lite/scripts/{run.sh,run-selftest.sh,traces.py}`, `plugins/sdlc-lite/scripts/traces/{cli.py,ingest.py,selftest.py,table.py}`, `plugins/sdlc-lite/scripts/traces/sources/{runs.py,context.py}`, `docs/maintenance/sdlc-internals.md`, and `.sdlc/0252-pc-run-context-trace/`.
