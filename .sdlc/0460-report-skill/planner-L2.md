<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Ship `/sdlc-lite:report`. The new script `plugins/sdlc-lite/scripts/report.py` (`collect`, `render`, `selftest`) prints an executive summary of the current agent thread by default, and prints the named views when asked. It reads records and the session transcript and makes no model call. The skill at `plugins/sdlc-lite/skills/report/` is wired into routing, `check.py`, `check.sh`, and packaging.

guard timeout: 2700

## Step 1: report.py collector, renderer and selftest, with the controlled-language docs
level: L3
### Read first
- `docs/specs/doc-standards/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/report.py` [creates: plugins/sdlc-lite/scripts/report.py] with three subcommands:
- `collect` prints the `session-status/1` JSON record.
- `render [view...] [options]` prints the views.
- `selftest` runs the controls.

The contract is three draft files. Read all three first and follow them exactly:
- `.sdlc/0460-report-skill/draft/SKILL.md`
- `.sdlc/0460-report-skill/draft/references/views.md` (views, options, defaults, entry grammar)
- `.sdlc/0460-report-skill/draft/references/record-schema.md` (groups, sources, health signals, grade bands)

Build both stages in this step: stage 1 reads records only, stage 2 adds the transcript signals. Depends on: none.

Settled interface. Do not change these names, because step 2 and the criteria pin them:
- Python version: the script runs on the host `python3`, which is 3.9 here (`/Library/Developer/CommandLineTools/.../Python3.framework/Versions/3.9`, seen in plan probes). So no `match`, no `X | Y` type unions, and no 3.10+ stdlib calls. Use the standard library only. The script may import sibling scripts the way `check.py` imports `prompt_lint`, for example `cost_estimate.transcript_usage`, which `dispatch.py record --transcript` already uses for usage.
- Verbs: module constant `VERBS` is a tuple of exactly the 11 closed verbs in draft order: built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting. Build every timeline entry through one function, and have it raise `CollectorError` for a verb outside `VERBS`. Tense follows the draft: past for `recent`, present progressive for `now`, future with a trigger for `next`.
- Views and options:
  - Views are `summary full tasks signals needs context cost children identity evidence`.
  - Options are exactly the draft table plus the reserved `--session`.
  - Exit 2 on an unknown view or option, on `--session <x>`, or on an unreadable record. Stderr then names every valid view and every valid option (`--since --last --next --only --severity --format --evidence --compare --explain --no-snapshot`).
  - Every option string must appear literally in `report.py`. `prompt_lint` (check.py item 53, P-2) flags an unknown `--flag` on a real script in the SKILL.md that step 2 ships.
- Text output:
  - With no view, the summary prints at most 8 lines and no header.
  - When more than one section prints (`full`, or several views), each section starts with a line that is exactly `<view>:`, for example `tasks:`.
  - `full` prints `summary tasks signals context cost children identity evidence` in that order, with `--evidence` on.
- JSON output (`--format json`):
  - One object with top-level `"schema": "session-status/1"`, `generated_at`, and the nine group keys `identity state work timeline health cost needs outcome unknown`.
  - `unknown` is a list of dotted field paths, for example `cost.dollars` or `health.context.peak_context_fill`. A value the collector cannot read goes there and is never shown as 0.
  - An unpriced run is counted as `unpriced`, never `$0`.
  - `health.context` keys: `peak_context_fill`, `compactions`, `re_reads`, `read_to_use`, `exploration`, `workaround_chains`, `noisy_output`.
- Snapshot: `render` writes the record to `.sdlc/runtime/report/<UTC %Y%m%dT%H%M%SZ>.json` unless `--no-snapshot` is given. `.sdlc/runtime/` is gitignored (`.gitignore:12`). `--compare last` reads the newest snapshot by file name, never by mtime, because plugin AGENTS.md says `order.py` owns ordering.
- Thresholds: read them from `.sdlc/config` lines of the form `report.<key>: <number>`. The file is `key: value` lines, for example `ticket_folders: numbered`. The defaults are the draft starting values:
  - `report.late_failure_ratio: 0.8`
  - `report.late_failure_min_minutes: 15`
  - `report.trivial_failure_minutes: 20`
  - `report.rework_rounds: 1`
  - `report.peak_context_pct: 70`
  - `report.context_window_tokens: 200000`
  - `report.compactions: 2`
  - `report.re_reads: 3`
  - `report.read_to_use: 15`
  - `report.exploration: 25`
  - `report.workaround_chain: 2`
  - `report.retries: 3`
  - `report.noisy_output_tokens: 20000`
  - `report.stall_minutes: 15`
  - `report.gate_wait_minutes: 5`

  Every flag prints `[U]` until calibrated; calibration is a non-goal. `--explain` prints each flag's rule, value and threshold.
- Severity and grade:
  - A `problem` flag records a failure or a stopped session: late failure, trivial last failure, rework, dead-end work, stall, or state `dead`. Every other flag is `likely`.
  - Grade A means no flags, B one likely flag, C two or more likely flags, D any problem flag. The grade line names the flags that set it.
- Identity and state:
  - The pid comes from `CLAUDE_PID`. Check liveness with `os.kill(pid, 0)`; a dead pid reads `dead`.
  - The session id comes from `CLAUDE_CODE_SESSION_ID`.
  - The thread's task is the `.sdlc/*/` dir that holds a running `*.attempt.json` whose `parent_pid` equals that pid. If there is none, the task is unknown.
  - State is `stalled` when the minutes since the last tool call or file change exceed `report.stall_minutes`.
- Timeline and sources:
  - `recent` comes from closed tickets and passed verifier results.
  - `now` comes from the open attempt and `steps.py next`.
  - `next` comes from ticket `depends:` and the ready queue. Each item is marked `planned` (it has a ticket or step) or `intended` (it has neither).
  - Cost comes from `runs.jsonl` and `budget.py`; gate wait comes from `gate_lock.py status`.
  - Call sibling scripts read-only through `subprocess` with a timeout. A failure lists the field under `unknown`.
- Transcript (stage 2):
  - The path is `$SDLC_REPORT_TRANSCRIPT` when set. Otherwise it is `<SDLC_CLAUDE_PROJECTS or ~/.claude/projects>/<slug>/<CLAUDE_CODE_SESSION_ID>.jsonl`, where slug is the project path with every `/` and `.` replaced by `-`. Verified: `~/.claude/projects/-Users-kimgranlund-Projects-nonoun-sdlc-lite--worktrees-fanout40-t/2a98c8fc-....jsonl` exists for this session.
  - Mirror `find_subagent_transcript` in `dispatch.py` for the projects root.
  - Peak context fill is the highest per-message `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`, divided by `report.context_window_tokens`.
  - Re-reads, read-to-use, exploration, workaround chains, retries and noisy output come from the tool_use and tool_result blocks.
  - With no transcript, or an unreadable one, every `health.context.*` field goes under `unknown`.
  - Codex transcripts are a non-goal.

Selftest:
- Build every fixture in a temp dir inside `selftest`, as `dispatch.py selftest` does: a fixture repo with `.sdlc/` tickets, attempts, results and `runs.jsonl`, plus a fixture transcript jsonl. Add no fixture files to the repo.
- Each control runs its case once with the rule replaced by a no-op and asserts the case fails. It then runs the case with the rule and asserts it passes. It prints one line: `ok: control <name>: red without the rule, green with it`.
- Required control names:
  - `dead pid`
  - `stalled`
  - `unknown cost` (an unreadable cost is in `unknown`, not 0)
  - `unknown view`
  - `verb outside list`
  - `late failure` (a 4-turn fixture whose first failing check falls in the last turn)
  - `re-reads` (one file read 3 times with no edit between)
  - `snapshot`
  - `compare last`
  - `explain`
  - `session refused`
  - `intended next`
- Also add controls for the other draft signals.
- Exit nonzero on any failed case.

Docs:
- In `docs/specs/doc-standards/core.md`, add a new `## Status verbs` section after `## Status words`. It holds the closed verb list (the 11 verbs on one line, comma separated, in the order above) and the tense rule.
- In `docs/references/glossary.md`, add one row `| status verb | noun | ... |` with the list and the tense rule.
- These are repository docs only. The skill in step 2 does not cite them.

Validation scope: the criteria below, `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` for the two docs, and a live `render` on this repo. The broad gates run in step 2. `report.py` is a new script that no existing file imports, so there are no contract dependents to update here.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/report.py selftest) && for c in "dead pid" "stalled" "unknown cost" "unknown view" "verb outside list" "late failure" "re-reads" "snapshot" "compare last" "explain" "session refused" "intended next"; do printf "%s\n" "$out" | grep -qF "ok: control $c:" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/report.py render nosuchview --no-snapshot 2>&1 >/dev/null); test $? -eq 2 && for w in summary full tasks signals needs context cost children identity evidence --no-snapshot --compare; do printf "%s\n" "$out" | grep -qF -- "$w" || exit 1; done`
- (red) `set -o pipefail; n=$(python3 plugins/sdlc-lite/scripts/report.py render --no-snapshot | wc -l) && test "$n" -ge 1 && test "$n" -le 8`
- (red) `set -o pipefail; out=$(python3 plugins/sdlc-lite/scripts/report.py render full --no-snapshot) && for s in summary tasks signals context cost children identity evidence; do printf "%s\n" "$out" | grep -qx "$s:" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/report.py render --format json --no-snapshot | python3 -c "import json, sys; d = json.load(sys.stdin); assert d[\"schema\"] == \"session-status/1\"; assert all(k in d for k in (\"identity\", \"state\", \"work\", \"timeline\", \"health\", \"cost\", \"needs\", \"outcome\", \"unknown\")); c = d[\"health\"][\"context\"]; assert \"peak_context_fill\" in c or \"health.context.peak_context_fill\" in d[\"unknown\"]"`
- (red) `python3 -c "import sys; sys.path.insert(0, \"plugins/sdlc-lite/scripts\"); import report; t = open(\"docs/specs/doc-standards/core.md\").read(); assert len(report.VERBS) == 11 and all(v in t for v in report.VERBS)"`
- (red) `grep -qF "built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting" docs/specs/doc-standards/core.md`
- (red) `grep -qF "| status verb |" docs/references/glossary.md`
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md")" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md")"`

## Step 2: report skill, routing, check.py pins, live run, gates green
level: L3
guard timeout: 2700
### Do
Depends on: step 1.

Create the skill folder `plugins/sdlc-lite/skills/report/` [creates: plugins/sdlc-lite/skills/report/SKILL.md]. Copy the three drafts into it:
- `.sdlc/0460-report-skill/draft/SKILL.md` becomes `SKILL.md`.
- `draft/references/views.md` becomes `references/views.md`.
- `draft/references/record-schema.md` becomes `references/record-schema.md`.

Then adjust the copies:
- In the SKILL.md Rules, replace the `docs/specs/doc-standards/core.md` citation with a link to `references/views.md#entry-grammar`, where the verb list already lives. A consumer install has no `docs/`, and plugin AGENTS.md requires a self-contained skill (check.py item 42).
- State in the skill that the Codex transcript mapping is unverified.
- Align `references/record-schema.md` with what step 1 built: the `schema` key, the nine groups, the `health.context` keys, the `unknown` dotted paths, the `report.<key>` config thresholds, and the problem versus likely severity.
- Keep the `**Codex host:**` paragraph. check-packaging.py requires the `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` route in every skill.

Wiring. Each item is a contract dependent found by `git grep -l fleet-status -- . ':(exclude).sdlc' ':(exclude)docs/reports'`, fleet-status being the nearest existing render-never-compose skill:
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: add the routing row `| This thread's state: what finished, what runs, what is next, what needs the user, what is wrong | report |` beside the `board` and `fleet-status` rows.
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/report.py" selftest || fail=1` after the `fleet_status.py` line, and name `report.py` in its header comment list.
- `plugins/sdlc-lite/scripts/check.py`: add a docstring item starting `<n>. Report`, where `<n>` is the next free number after the highest present. Other wave-40 lanes may also add items, so take the number at build time. Add a block modeled on item 37 (`FLEET_STATUS_NEEDS`, `fleet_status_bad`):
  - `REPORT_NEEDS` pins these phrases in `skills/report/SKILL.md`: `report.py render`, `Render, never compose`, `Codex host`, `Exit 2 is a refusal`, `references/views.md`, `references/record-schema.md`.
  - It pins these phrases in `scripts/report.py`: `VERBS`, `CollectorError`, `session-status/1`, `def selftest`.
  - It pins `report.py" selftest` in `scripts/check.sh`, and the routing row `| report |` in `skills/sdlc-lite/SKILL.md`.
  - A planted `harness:` reference in the skill is flagged.
  - Errors print with the prefix `check.py: report:`.
  - Negative controls: each phrase removed from each file, a harness reference, and the routing row removed must each be flagged, else check.py fails.
- `plugins/sdlc-lite/AGENTS.md` Verification list: add `- Thread report: \`python3 plugins/sdlc-lite/scripts/report.py selftest\`.`
- `docs/references/sdlc-internals.md`: add one short entry for `report.py` (subcommands, sources, snapshot path, `report.<key>` thresholds). The file has one entry per script.
- `docs/README.md` names fleet-status only inside a dated release line. Leave it unchanged on purpose, because release notes are history.

Live run:
- Run `python3 plugins/sdlc-lite/scripts/report.py render` once on this repo. The default writes one snapshot under the gitignored `.sdlc/runtime/report/`.
- Run it once more with `full`.
- Write `.sdlc/0460-report-skill/notes.md` [creates: .sdlc/0460-report-skill/notes.md] with the date, the command `report.py render`, what it printed, and what was listed under `unknown`.

Gates. This is the gates green step. Run each of these and fix any red that step 1 or this step introduced in the files in scope:
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- `git diff --check "$SDLC_BASE_SHA"`
- `bash plugins/sdlc-lite/scripts/check.sh` (about 900 s on record)

A gate that is already red at the build-start HEAD is reported as `inherited red`. check.sh and check.py are hot files: one writer at a time.
### Acceptance criteria
- (red) `for ph in "report.py render" "Render, never compose" "Codex host" "Exit 2 is a refusal" "references/views.md" "references/record-schema.md"; do grep -qF "$ph" plugins/sdlc-lite/skills/report/SKILL.md || exit 1; done && test -f plugins/sdlc-lite/skills/report/references/views.md && test -f plugins/sdlc-lite/skills/report/references/record-schema.md`
- (red) `test -f plugins/sdlc-lite/skills/report/SKILL.md && ! grep -rqF "docs/" plugins/sdlc-lite/skills/report`
- (red) `grep -qF "| report |" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md && grep -qF "report.py\" selftest" plugins/sdlc-lite/scripts/check.sh && grep -qF "report.py selftest" plugins/sdlc-lite/AGENTS.md && grep -qF "report.py" docs/references/sdlc-internals.md`
- (red) `grep -qE "^[0-9]+\. Report" plugins/sdlc-lite/scripts/check.py && grep -qF "skills/report/SKILL.md" plugins/sdlc-lite/scripts/check.py`
- (red) `t=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/rep.XXXX") && cp -R plugins/sdlc-lite "$t/sdlc-lite" && python3 -c "import pathlib, sys; f = pathlib.Path(sys.argv[1]); f.write_text(f.read_text().replace(\"Render, never compose\", \"x\"))" "$t/sdlc-lite/skills/report/SKILL.md" && python3 "$t/sdlc-lite/scripts/check.py" "$t/sdlc-lite" | grep -qF "check.py: report:"`
- (red) `grep -qF "report.py render" .sdlc/0460-report-skill/notes.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vE "^plugins/sdlc-lite/skills/report/" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md|plugins/sdlc-lite/skills/sdlc-lite/SKILL.md|plugins/sdlc-lite/scripts/check.sh|plugins/sdlc-lite/scripts/check.py|plugins/sdlc-lite/AGENTS.md|docs/references/sdlc-internals.md")" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^plugins/sdlc-lite/skills/report/" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md")"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `git diff --check "$SDLC_BASE_SHA"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Assumptions
- The drafts in `.sdlc/0460-report-skill/draft/` are maintainer-approved and are the behavior contract: verified by the handoff Intent ("starting from the maintainer-approved drafts ... the draft SKILL.md is the contract").
- The host `python3` is 3.9: verified by the plan probe traceback path `.../Python3.framework/Versions/3.9/...`.
- The main session transcript is at `<projects>/<slug>/<CLAUDE_CODE_SESSION_ID>.jsonl`, with `/` and `.` mapped to `-`: verified by `ls ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-sdlc-lite--worktrees-fanout40-t/$CLAUDE_CODE_SESSION_ID.jsonl` (exists, 319801 bytes). `CLAUDE_PID` and `CLAUDE_CODE_SESSION_ID` are set in this environment (`env`).
- `.sdlc/runtime/` is gitignored, so the snapshot never dirties the tree: verified by `git check-ignore -v .sdlc/runtime/report/x.json` (`.gitignore:12`).
- `.sdlc/config` is `key: value` lines: verified by `cat .sdlc/config` (`ticket_folders: numbered`).
- check.py item 42 flags only links and `plugins/` prose paths, not a `docs/` code span: verified at `plugins/sdlc-lite/scripts/check.py` `skill_ref_bad`. The step 2 criterion bans `docs/` in the skill folder anyway, for self-containment.
- Every skill needs the Codex route line: verified by `scripts/check-packaging.py:53`.
- check.py run on a `cp -R` plugin copy prints item-specific FAIL lines: verified by a probe that removed `Render, never compose` from a copied fleet-status skill and saw `FAIL check.py: fleet status: skill missing "Render, never compose"`. Other items fail in the copy for unrelated missing repo docs, so the criterion greps the `check.py: report:` prefix.
- check.sh takes about 900 s: verified by `.sdlc/.0451-lanes-core/step-1/builder-L3.md` ("check.sh exited 0 in 897 s"). The guard timeout is 2700.
- This plan settles the `problem` versus `likely` split and the `report.<key>` config names, because the draft names the grade bands but not each signal's severity. Both stay `[U]`, and a later retro calibrates them (a handoff non-goal).

## Risks
- `bash plugins/sdlc-lite/scripts/check.sh` was not run at plan time, because it is a broad suite of about 900 s. The other step 2 guards were run green at base. If check.sh is red at base, it comes back as `inherited red`.
- The skill description claims "status", which `/board` also claims. This ticket does not settle the routing overlap between report, board and fleet-status.
- Thresholds and severities are uncalibrated `[U]`, and the Codex transcript mapping is unverified. The live summary runs in a repo with hundreds of tickets, so the 8-line cap is the main live proof.
- Other wave-40 lanes may edit `check.py` and `check.sh`. The builder takes the item number at build time, and the criteria match `^[0-9]+\. Report`, not a fixed number.
- Step 1 is large for one L3 build, since it holds both stages. If it blocks, the replan can split stage 2 into its own step.
