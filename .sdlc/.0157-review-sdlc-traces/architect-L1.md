<!-- role=architect level=L1 model=fable effort=high -->
## Approach

The traces subsystem is a read-only analyzer that turns a project's sdlc trail into one attempt table, runs deterministic detectors over it, and only then spends model calls, bounded and gated by the user. It ships as a `scripts/traces/` package with a thin `scripts/traces.py` entry (so parallel builders each own one file, the same reason `_vendor/` already sits under scripts) and a `review-traces` skill that drives stages 3 to 6.

Ingest is attempt-centric. `*.attempt.json` is the primary key because it is the only record that exists for interrupted and failed runs (run_lifecycle.py writes it before the backend starts; run.sh appends to runs.jsonl only after a result is saved). Everything else joins onto it: the runs.jsonl row by `attempt_id`, or by result name for legacy rows (here 671 of 837 rows carry `file`, only 157 carry `attempt_id`, and an orphan row gets a synthesized `legacy:<relpath>` id); the result file's Status/Verdict/plan-defect tag/Changes through the functions steps.py and order.py already export (never re-implemented, so the analyzer classifies exactly as `steps.py next` does); the stream-json transcript when present (tool calls, `timestamp` per event, hook denials, `rate_limit_event`), tolerating absence because `*.log` is gitignored and exists only on the machine that ran it; ticket id and status from `tickets.load`, which already includes closed dot folders; step number and superseded flag from the dir name. Fanout facts come from a lanes dir in both layouts (pre-T-0155 unprefixed logs and `gate-…-<k>.log`; post-T-0155/0156 `[fanout-<12hex>]` prefixes, `fanout.log`, `gate-…-<k>-a<n>.log`). Git facts come from `worktree list`, refs, `ls-files`, commit subjects (`Merge <lane>: <id>`, `close <id>`, `wip(<id>): <outcome>`) and the integration worktree's HEAD reflog for `reset: moving to` entries. The bench baseline is the median cost per verifier-passed step across `bench/results/*/`.

Outputs and the incremental cursor live in the reviewing project's `.sdlc/runtime/traces/<repo-key>/` (override `--out`), never in the analyzed repo, which resolves the handoff's tension between "read-only on the analyzed repo" and "cursor in .sdlc/runtime/". The cursor keys on source path plus size/mtime/digest; a re-ingest re-reads only changed dirs and the table is byte-stable for an unchanged corpus.

Detectors are grouped by input family, not one node per detector: escalation (results and `## Plan review`: replan loops, `recurring finding:` entries, a bump whose next fail note repeats the last one, plan-defect refusals grouped by the steps.py lint rule that named them, resume that built step m>n before blocked step n finished, exit-3 results, statusless and no-verdict runs, attempts with no run row, stale `.running` markers), plan quality (criteria never red via an opt-in rerun at `base-sha` in a detached temp worktree, a later fail note citing a path an earlier step's `## Changes` listed, two scope-blocked builders on one path with no `scope widened:` line), hygiene (stray and nested `.worktrees/*/.worktrees/tmp` worktrees, tracked `*.log`/`*.running`/`.run.lock`, integration resets paired with red-gate and `integration dirty`/`wip(` signals, mixed or missing run ids per log, overwritten legacy gate logs, `tickets.problems` duplicates and unregistered `external_branch` names), and cost/transcript (cost per verified step vs baseline, builder attempts per step, repeated identical `sleep`/`kill -0`/`ls *.running` Bash calls with durations from event timestamps, `run_in_background`/Monitor denials, rate limits; host load is an optional external series and reads `unknown` otherwise, because no trace carries it). Every finding carries evidence pointers (path and line, or attempt id), a cause hint (layer: sdlc-lite, project, host, task text; plugin file), a stable id (hash of detector plus evidence keys) with first/last seen, and a severity; `clusters --max N` groups by cause-hint file and caps what reaches a model.

Stages 3 to 6 are a skill, not code. Per cluster it writes a question handoff citing only the evidence paths and runs archaeologist L1 (scout L1 when the question is "where is the rule"); per surviving finding it writes a step handoff whose acceptance criteria are the finding's own evidence commands and runs verifier L1, so a finding that cannot be reproduced by command is dropped; one planner L2 run drafts a ticket per confirmed sdlc-lite finding with a red check as its criterion; one AskUserQuestion round approves filing through `tickets.py new bug`, non-sdlc findings go to `<review task>/report.md`, and unattended runs file nothing. Model calls are bounded by construction: clusters + findings + 1.

## Interfaces

- `plugins/sdlc-lite/scripts/traces.py` (new, thin entry): `ingest <repo> [--lanes-dir DIR]... [--out DIR] [--rerun-criteria]`, `detect`, `clusters --max N`, `selftest [-k NAME]`.
- `plugins/sdlc-lite/scripts/traces/` (new package): `sources/{attempts,runs,results,transcripts,fanout,git,tickets,bench}.py`, `table.py` (row schema: attempt_id, ticket, task_dir, step, superseded, role, level, attempt_k, status, verdict, plan_defect, turns, cost_usd, secs, tool_calls, denials, rate_limits, exit_code, sources[]), `store.py` (events.jsonl, aux.json for lanes/gates/git/baseline, cursor.json), `detectors/{escalation,plan,hygiene,cost}.py` with one thresholds table, `findings.py` (findings.jsonl, clusters.json), `selftest.py`.
- `plugins/sdlc-lite/skills/review-traces/SKILL.md` (new) with three templates: cluster question handoff, finding verification step, ticket-draft planner handoff.
- Edits in one serial slice: `scripts/check.sh` (add `traces.py selftest`), `agents/conductor.md` (route), `skills/handoff-format/SKILL.md` (ignore `.sdlc/runtime/`), `skills/sdlc-lite/SKILL.md` (Codex adapter skill list), `docs/README.md`.
- Manifest for /plan: `.sdlc/0157-review-sdlc-traces/decompose/manifest-v1.json` (26 nodes, 39 actions, `--plan --strict` clean); report at `decompose/report.md`. The handoff's Context line was not added (this role writes only under `decompose/`).

## Constraints and assumptions

- attempt.json exists for runs that never reach runs.jsonl: verified by reading run_lifecycle.py (record written before Popen, status set in `finally`) and the local trail (158 completed, 1 failed, 1 running records; this run's own record has no runs.jsonl row yet).
- Legacy runs.jsonl rows lack attempt_id and sometimes `file`: verified by key counts over every runs.jsonl here (837 rows, 671 `file`, 157 `attempt_id`).
- Transcripts are gitignored and may be absent: verified by `.gitignore` (`*.log`) and `git check-ignore`; only one .log exists locally.
- Stream-json events carry `timestamp`, tool_use inputs, `hook_response`, `rate_limit_event`: verified on this run's own log.
- Lane logs exist in two layouts and gate logs were overwritten before T-0156: verified by `.worktrees/fanout-night/logs` (no prefixes, `gate-…-<k>.log`, no fanout.log) against fanout.py's current `say`, `run_logged` and `-a<n>` naming.
- Driver logs are the conductor's plain final text, not stream-json: verified by reading `fanout-T-0152.log`.
- Reset evidence lives in the integration worktree's HEAD reflog and dies with the worktree: verified (`fanout-night2/integration` shows `reset: moving to`; `fanout-night/integration` is already removed).
- steps.py, order.py, tickets.py, board.py are importable from the scripts dir: verified by board.py's `import tickets, order`.
- scout and archaeologist have only L1 in run.sh: verified by the level table; the handoff's "L2" cannot be honored without a user decision on models.
- No trace records host load: verified by inspecting attempt.json, runs.jsonl keys, and event types; T-0159 cites load only in ticket prose.
- The gen-ui-system-svelte-lite repo and `sdlc-feedback-batch3.md` are on this machine: unverified, searches of ~/Projects and Spotlight found neither.
- `git worktree add --detach` for the opt-in criteria rerun writes only `.git/worktrees` metadata and is removed afterward: unverified at runtime, stated from git semantics.

## Rejected alternatives

- One file `scripts/traces.py` like fanout.py or steps.py: matches repo convention but forbids the one-writer-per-file fan-out the handoff's size L implies; the package keeps the same CLI surface.
- Cursor and outputs inside the analyzed repo's `.sdlc/runtime/`: violates the read-only constraint whenever the analyzed repo is another project, and would dirty a committed `.sdlc/` trail.
- runs.jsonl as the primary key: drops every interrupted and failed attempt, which is exactly the waste the tool must see.
- Re-implementing Status/Verdict/escalation parsing in traces.py: two readings of the same files would drift; steps.py already exports the rules `/chain` runs on.
- One node per detector: over-decomposition; a detector family over one input is the one-owner unit, and thresholds belong in one table.
- Filer as the ticket drafter: it drafts records for a finished task; the planner is the role that writes red criteria, which each proposed ticket needs.
- A model in stage 2 (an LLM judge over lane logs): the done-condition says stages 1 and 2 cost no model calls, and judgment findings would not be reproducible by a verifier command.

## Risks

- The done-condition names a corpus that is not here. If the gen-ui run cannot be supplied, the batch-3 items can only be proven on synthetic fixtures plus this repo's own night run; the T-0148, T-0149 and T-0153 shapes were found by a human reading lane prose, and a deterministic detector may name them only as advisories.
- Pre-T-0155 lane logs have no run id and driver logs are overwritten, so "stale line" detection on old runs degrades to mtime heuristics.
- Reflog-based reset evidence disappears when fanout worktrees are removed; the detector must run before cleanup or report "reflog gone".
- The opt-in `--rerun-criteria` executes plan criteria from the analyzed repo; a criterion with side effects could write into the temp worktree's toplevel checkout. It stays off by default and must run in a detached worktree outside the repo.
- If the planner splits detectors across builders without first pinning `table.py` and `findings.py`, the readers and detectors will diverge on field names; the manifest's edges make that prep slice serial.
