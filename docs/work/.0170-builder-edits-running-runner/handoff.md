---
id: T-0170
title: "A builder that edits run.sh loses its own result"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A role that changes `scripts/run.sh` during its own run still gets its result saved, or is stopped before it can change the running file. A test that failed before the fix passes after it.

## Repro
1. Give a builder a step whose Do changes `plugins/sdlc-lite/scripts/run.sh`.
2. Run it with `run.sh builder L3 <step handoff>`.

## Expected
`builder-L3.md` and a `runs.jsonl` line are written, or the run fails with a clear message.

## Actual
Observed 2026-09-29 on T-0163 step 1: the builder added a `shared_note` variable to `run.sh`. The running `run.sh` exited 0, the attempt record says `completed`, and neither `builder-L3.md` nor a `runs.jsonl` line was written. The report was only in `builder-L3.log`. The maintainer recovered it with the same pick rule `run.sh` uses and marked the header `recovered-from-log`.

## Context
Bash reads a script as it runs, so a change to the file on disk changes the rest of the running process. The repository guidance already says not to edit runtime scripts while a role uses them, but a builder in this repository edits its own runner.

Options, not decided: `run.sh` copies itself to a temporary file and runs the copy, or reads its whole body into a function before running; or a role-run hook refuses writes to the plugin's `scripts/run.sh` and `scripts/run_lifecycle.py` from inside a role.

Exit 0 with no result file also breaks the stated exit code contract ("1 run failed or returned no result").

## Constraints
The failing test lands before or with the fix. Consumer projects are not affected unless a role edits the plugin's own runner.
