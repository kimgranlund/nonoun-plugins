## Task goal
`/sdlc-lite:report` prints a short executive summary of the current agent thread by default, and the named views (tasks, signals, needs, context, cost, children, identity, evidence, full) on request, from records and the transcript, with no model call in the collector.

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
