<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: step 2, attempt 8f6804e851134c36b5939d404b24e58d, handoff sha256 561d5d11bef9. 5 of 5 `(red)` criteria have no pre-edit red control. They are the skill-phrase and `docs/` check, the `| report |` route check, the check.py item 54 pin, the check.py negative control, and the `notes.md` check. The step 2 builder also reports that the first `(red)` criterion, the skill-phrase `for ... done` loop, got no control line at all. Step 1's uncommitted files already differed from base, so `redck.py` stored the checkpoint as retrospective. The verifier ran each check on the built tree and they pass. A passing verdict does not clear the deviation.
- process deviation: red-checkpoint: retrospective: step 3, attempt 72b3b14fc2e649a0a8745e569611f21d, handoff sha256 067a9a9e30fd. The 1 `(red)` criterion has no pre-edit red control: the grep for "at most 8 lines" plus "recent" and "unknown" in `SKILL.md` and `views.md`. The tree already held uncommitted edits from steps 1 and 2. The step 3 verifier built its own negative control on stripped copies, and the criterion exited 1 there. The deviation stands. The recorded run also shows exit 2, which the verifier traced to a span cut short at an embedded backtick, so it is not a real red.
- All three steps have verifier verdict pass: step 1 passes 10 of 10 criteria, step 2 passes 12 of 12, step 3 passes 3 of 3. Step 1 has no process deviation file.

## PR title
T-0460: Build /sdlc-lite:report, a thread report with views, health signals and a hygiene grade

## PR body
Summary
- Adds `/sdlc-lite:report`. By default it prints an executive summary of the current agent thread. On request it prints the named views: tasks, signals, needs, context, cost, children, identity, evidence and full.
- The collector reads records and the session transcript and makes no model call. It is read-only apart from one snapshot under the gitignored `.sdlc/runtime/report/`.

Changes
- New `plugins/sdlc-lite/scripts/report.py` with `collect`, `render` and `selftest`.
  - Stage 1 reads records only: identity, state, work, timeline, cost, needs and the records-only health signals.
  - Stage 2 reads the transcript: peak context fill, compactions, re-reads, exploration and noisy output.
  - Views and options follow the draft.
  - An unknown view or option, and `--session`, exit 2 with the valid names listed.
  - `--format json` returns the `session-status/1` record, `--compare last` marks changes, and `--explain` prints rule, value and threshold.
  - Unknown values go under `unknown`, never shown as 0. Every flag is `[U]` until calibrated.
- New skill `plugins/sdlc-lite/skills/report/SKILL.md` with `references/views.md` and `references/record-schema.md`.
  - The schema reference is rewritten to match the real script.
  - `AskUserQuestion` is added to `allowed-tools`, as fleet-status does.
  - The Codex transcript mapping is stated as unverified.
  - Step 3 aligned the `SKILL.md` and `views.md` summary description with the real output: state, needs, now, next, grade, plus `recent` and `unknown` lines when not empty, at most 8 lines.
- Controlled language: an 11-verb closed list (built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting) and a tense rule. They are added to `docs/specs/doc-standards/core.md` and `docs/references/glossary.md`. A verb outside the list is a collector error.
- Wiring:
  - a routing row in `skills/sdlc-lite/SKILL.md`
  - the selftest line in `check.sh`
  - `check.py` item 54, pinning the skill and script phrases with negative controls
  - a Verification bullet in `plugins/sdlc-lite/AGENTS.md`
  - a `scripts/report.py` entry in `docs/references/sdlc-internals.md`
- Live run recorded in `.sdlc/0460-report-skill/notes.md`.

Verification
- Step 1, `report.py` and the controlled-language docs:
  - `report.py selftest` exits 0. It prints 25 `control ... red without the rule, green with it` lines, including all 12 required ones.
  - The selftest first failed three controls. They were fixed by reading untracked files, giving the fixture a running attempt, and reading the criteria heading level.
  - The verifier broke the rules in a copy and saw `compare last` and `dead pid` go red.
  - `render nosuchview` exits 2 and lists the views and options.
  - The summary is 6 to 7 lines. `render full` prints all 8 headers. The JSON has the schema, the nine groups and the seven `health.context` keys.
  - `docs_check.py` reports 0 errors.
- Step 2, skill and wiring:
  - `check.py`, `check-packaging.py` and `docs_check.py` all exit 0.
  - The step 2 verifier ran `check.sh` to rc 0. It logged `report.py selftest: all cases passed`, `run selftest: PASS` and `hook selftest: PASS`.
  - The verifier added two more `check.py` negative controls in a copy: a planted `harness:` reference, and the route removed. Both fail with `check.py: report:`.
  - `git diff --check` is clean against base `ebac4973`.
- Step 3, summary wording:
  - The verifier ran the criterion on the built tree (exit 0).
  - On stripped copies it exited 1, and each of the two files can fail it alone.
  - `report.py render --no-snapshot` printed 7 lines: state, needs, now, next, recent, grade, unknown.
  - `check.py` and `check-packaging.py` exit 0.
- The selftest stubs `gate_lock.py`, `budget.py` and `steps.py next`, so it does not read machine-wide gate-lock state (the T-0459 flake).

Process deviations (not cleared by the passing verdicts): the red checkpoints for step 2 (5 `(red)` criteria) and step 3 (1 `(red)` criterion) were recorded retrospectively, so none of those criteria has a pre-edit red control. See Warnings.

## Changelog entry
- Added `/sdlc-lite:report` and `scripts/report.py`. It prints an executive summary of the current thread and the views tasks, signals, needs, context, cost, children, identity, evidence and full, with a health grade (A to D, every flag `[U]` until calibrated). It uses no model call. Added a closed status-verb list and tense rule to the doc standards and glossary.

## Follow-ups
- note: The 5 fields that read `unknown` on the live run were `health.unpushed_commits`, `identity.level`, `identity.name`, `identity.parent` and `outcome.last_result`. They may be gaps in the record sources rather than missing data.
- note: A sub-agent inherits `CLAUDE_PID` and `CLAUDE_CODE_SESSION_ID`, so a report run inside a role describes the conductor's thread, not the role's own.
- note: Thresholds are the draft's starting values, and `check first run late`, `dead-end work` and `dead` are fixed in code without a `report.*` key. A later retro calibrates them.
- note: `waiting-on-user` is partly guessed from transcript text: an `AskUserQuestion` with no result, or a last assistant line that ends in `?`.
