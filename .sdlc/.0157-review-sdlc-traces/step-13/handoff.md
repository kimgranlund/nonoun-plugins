## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 13: Plan-quality detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/plan.py` with `detect(rows, aux, thresholds)`, `traces/rerun.py`, and a `rerun_criteria=False` flag on `ingest.run`:
- `criteria-never-red` (only with the flag): during ingest, `rerun.run(repo, rows)` takes each step dir whose newest verifier passed and that holds a `base-sha` file, the non-guard command spans of its `handoff.md` (`steps.command_spans` minus `steps.guard_spans`, skipping spans `steps.guard_skipped` flags), and runs each with `bash -c` from a detached throwaway worktree of the analyzed repo at that base-sha (under `$SDLC_TMP_WORKTREES/traces-rerun-<pid>` when that variable is set, else under a `tempfile.mkdtemp()` dir outside the repo; `git worktree remove --force` and `git worktree prune` in `finally`), with `SDLC_BASE_SHA` set to the base-sha and a per-span timeout from thresholds (default 60 s), and stores the outcomes in aux.json under `criteria_reruns`; the detector turns each span that exited 0 at base (it never went red) into a finding with evidence the step handoff path and criterion line; cause `agents/planner.md`. Without the flag aux has no `criteria_reruns` and the detector is quiet.
- `contract-dependents`: a verifier fail row in step m whose `next_note` names a path (a code span, or a token holding `/`) that an earlier step's (n < m) done builder `changes` lists; evidence both result paths; cause `agents/planner.md`.
- `scope-prose`: two or more blocked builder rows on one step whose `next_note` names the same path, with no `scope widened:` line under `## Plan review` in the task handoff and no `## Scope widened` section in the step handoff; evidence both builder paths; cause `skills/chain/SKILL.md`.
Register the `plan` cases on a throwaway git repo: a passed step whose criterion is `test -f README.md` with README.md present at base-sha fires `criteria-never-red` only when the flag is set, and `git worktree list` after the run equals the list before it; a criterion `test -f added.txt` for a file the build added is quiet; a later fail note citing a path an earlier step's `## Changes` listed fires `contract-dependents`; two scope-blocked builders naming one path with no `scope widened:` line fire `scope-prose`; each negative control fires none; printed as `ok: plan: <detector> fires` and `ok: plan: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan`
- `for d in criteria-never-red contract-dependents scope-prose; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan | grep -qF "ok: plan: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan | grep -qF "ok: plan: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/plan.py && test -f plugins/sdlc-lite/scripts/traces/rerun.py`
- `grep -q 'rerun_criteria' plugins/sdlc-lite/scripts/traces/ingest.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
