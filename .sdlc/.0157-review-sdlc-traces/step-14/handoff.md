## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 14: Hygiene detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/hygiene.py` with `detect(rows, aux, thresholds)` over the git, lanes, and ticket facts in aux:
- `stray-worktree`: a worktree with `nested` True or under `.worktrees/tmp/`; evidence the path; cause `scripts/run.sh`.
- `tracked-runtime-file`: each `tracked_runtime` path; cause `skills/handoff-format/SKILL.md`.
- `integration-reset`: a `reset: moving to` reflog entry paired with a lost-edit signal in the lanes facts (a `red: ... rc=` outcome, an `integration dirty` outcome, or a `wip(` commit); evidence the reflog line and the lane line; cause `scripts/fanout.py`; when report.md names an integration worktree that no longer exists, one severity-1 `reflog-gone` finding instead.
- `stale-log-lines`: a driver or gate log whose lines carry two or more distinct run ids (severity 2), or no run id at all (legacy, severity 1); evidence the log path and, for mixed ids, the first line of the second id; cause `scripts/fanout.py`.
- `overwritten-gate-log`: a legacy `gate-<lane>-<id>-<k>.log` name with no `-a<n>`; severity 1; evidence the path; cause `scripts/fanout.py`.
- `ticket-id-collision`: each `duplicate id` problem line; evidence the ticket root and the line; cause `scripts/tickets.py`.
- `unregistered-external-branch`: a report.md external lane branch absent from the registered `external` names, and a registered name with no local branch; evidence the report or config path; cause `scripts/tickets.py`.
Register the `hygiene` cases: the step 7 throwaway repo and the step 6 legacy lanes fixture fire one finding per defect with the file or worktree path as evidence; a clean throwaway repo and the prefixed lanes fixture fire none; printed as `ok: hygiene: <detector> fires` and `ok: hygiene: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene`
- `for d in stray-worktree tracked-runtime-file integration-reset stale-log-lines overwritten-gate-log ticket-id-collision unregistered-external-branch; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene | grep -qF "ok: hygiene: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene | grep -qF "ok: hygiene: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/hygiene.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
