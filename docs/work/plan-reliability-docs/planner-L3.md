<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Build the 0.22.3 restart and blocked run tickets of `docs/specs/sdlc-lite/restart-and-blocked-run-plan.md` in order, one step per ticket to file, so G-002 ("a host restart or a blocked run costs minutes, not hours") has its measures and its fixes, and each candidate the spec marks diagnosis-first ends in a dated report with a verdict.

## Step 1: Collector fields for K-002, K-003, K-004 and verifier minutes
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/kpi/AGENTS.md`
### Do
Ticket: feature, size L2, serves G-002. Spec: section "Measures" of `docs/specs/sdlc-lite/restart-and-blocked-run-plan.md`. Depends on: none.

In `plugins/sdlc-lite/scripts/fleet_collect.py` (`collect_runs`, `fleet_collect.py:320-414`, and `collect`, `704-720`), add these keys; none of today's keys changes:
- `runs.interrupted.attempts[].lost_min`: minutes from the attempt's `started_at` to the `started_at` of the next attempt record of the same role in the same handoff dir, else to its own `finished_at`; plus `runs.interrupted.lost_min_median` and `lost_min_total` (null and 0 with no interrupted attempt).
- `runs.orphaned`: `{count, attempts: [{attempt_id, role, level, started_at, path}]}` for attempt records with status `running`, backend claude (default), started in the window, whose `parent_pid` (else `owner_pid`) is dead now, using the same `kill(pid, 0)` test as `dispatch.pid_alive` (`dispatch.py:216-225`). Deduplicate by `attempt_id` across worktree copies, as `interrupted` does.
- `results.builder`: `{total, blocked}`: builder rows of `runs.jsonl` in the window, deduplicated as `runs` is; `blocked` counts those whose result file (the row's `file` beside its `runs.jsonl`) holds `## Status` whose next non-blank line's first word is `blocked`.
- `plan_defects`: `{late, early}`: `late` counts builder and verifier rows in the window whose result file holds a line starting `plan defect:` (after an optional list marker); `early` counts lines of `refusals.jsonl` files in any scanned `.sdlc` dir whose `ts` is in the window, deduplicated by `(plan, text)`. The line format `{ts, tool, plan, step, text}` is settled in the spec section 4; step 5 writes it, so `early` reads 0 until then.
- `attempts.by_role`: `{role: {count, median_min, max_min}}` over completed attempt records in the window, minutes from `started_at` to `finished_at`.
Add selftest cases with exactly these labels: `interrupted: lost_min runs to the next attempt start in the same dir and role`, `orphaned: a running attempt whose parent pid is dead is counted`, `negative control: a running attempt whose parent pid is alive is not counted orphaned` (use the selftest's own pid), `results: a builder result whose Status is blocked is counted`, `plan_defects: a plan defect line in a builder or verifier result is counted late`, `plan_defects: a refusals.jsonl line in the window is counted early`, `attempts: completed verifier minutes run from started_at to finished_at`. Update the module docstring's field list.

Then remove the "absent until plan step 1" notes from the `read:` lines of `docs/kpi/002-restart-recovery-minutes.md`, `003-blocked-builders-per-wave.md` and `004-unsatisfiable-criteria-caught.md`, and the matching "cannot be read today" sentence in each Reading it, so the KPI files describe the fields as they now exist (K-004 keeps its note that early reads 0 until step 5).

Contract dependents (`git grep -l fleet_collect -- plugins scripts`): `fleet_detect.py`, `fleet_status.py`, `plan_check.py`, `check.py`, `check.sh`, `skills/fleet-retro/SKILL.md`, `skills/plan-goal/references/goal-rules.md`, `skills/plan-verification/references/outcome-block.md`. All read existing keys only; the new keys are additive, so none is edited. Validation scope: `fleet_collect.py selftest`, plus `fleet_detect.py selftest` and `fleet_status.py selftest` as the two dependents that parse the collector's JSON. A read-only stand-in that computes the same numbers today is `docs/work/plan-reliability-docs/kpi-baseline-probe.py`; compare one window by hand if a number looks off.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && for l in 'interrupted: lost_min runs to the next attempt start in the same dir and role' 'orphaned: a running attempt whose parent pid is dead is counted' 'negative control: a running attempt whose parent pid is alive is not counted orphaned'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && for l in 'results: a builder result whose Status is blocked is counted' 'plan_defects: a plan defect line in a builder or verifier result is counted late' 'plan_defects: a refusals.jsonl line in the window is counted early'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: attempts: completed verifier minutes run from started_at to finished_at'`
- (red) `test -f docs/kpi/002-restart-recovery-minutes.md && ! grep -qF 'absent until plan step 1' docs/kpi/002-restart-recovery-minutes.md docs/kpi/003-blocked-builders-per-wave.md docs/kpi/004-unsatisfiable-criteria-caught.md`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/fleet_collect.py -e docs/kpi/002-restart-recovery-minutes.md -e docs/kpi/003-blocked-builders-per-wave.md -e docs/kpi/004-unsatisfiable-criteria-caught.md)"`

## Step 2: record leaves the attempt running when no result exists yet
level: L2
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Ticket: bug, size L2, candidate 2 of the spec (section 2). Depends on: none; first of the three `dispatch.py` steps, which run in one lane in the order 2, 3, 4.

In `record` (`plugins/sdlc-lite/scripts/dispatch.py:865-991`): when the result file is missing or empty, stdin is empty or whitespace, and no transcript yields a result (the branch that today reaches `text, error = '', ... 'no result file at ...'` at `dispatch.py:927` with empty `said`), print `dispatch.py: no result yet at <path>; the attempt stays running: record again once the <role> writes it, or pass --no-result to close it failed` to stderr and return 2 without writing `<stem>.log`, a `runs.jsonl` line, a `.limit` marker, or a delivery, and without calling `close`. Add `record --no-result` (a store-true flag passed into `record` as `no_result=False`), which keeps today's path exactly: exit 1, the error text `no result file at <path> (the <role> must write its report there before it ends)`, attempt `failed`. Stdin holding error text and a transcript that stopped on `max_tokens` keep closing the attempt `failed` as now. Update the docstring's `failed` paragraph (`dispatch.py:90-92`) and the `record` usage line (`dispatch.py:5`).

Contract dependents (`git grep -n "no result file at\|returned no result" -- plugins`): the selftest case "a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line" (`dispatch.py:1994-1996`) records with no body; make it pass `--no-result` and keep its label. Any other selftest case that records with no file and no stdin and expects exit 1 gets `--no-result` the same way (the selftest run finds them). `run.sh:667` is the Codex runner's own failure and stays: it waits for its process, so it has no early-record window. `docs/references/sdlc-internals.md`: update only if it states that record fails with no result file. Add selftest cases with exactly these labels: `record with no result file and empty stdin exits 2 and leaves the attempt running`, `record after the late result file appears completes the attempt`, `record --no-result closes an attempt with no result file as failed, exit 1`, `negative control: error text on stdin with no result file still closes the attempt failed`. Write each label as one string literal on one line, so the (red) source grep finds it. Validation scope: `dispatch.py selftest` (about 130 s on this host under load).
### Acceptance criteria
- (red) `grep -qF 'record with no result file and empty stdin exits 2 and leaves the attempt running' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'record with no result file and empty stdin exits 2 and leaves the attempt running' 'record after the late result file appears completes the attempt' 'record --no-result closes an attempt with no result file as failed, exit 1' 'negative control: error text on stdin with no result file still closes the attempt failed'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py record --help | grep -qF -- '--no-result'`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line'`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e docs/references/sdlc-internals.md)"`

## Step 3: prepare --tree names the lane worktree as Tree and base
level: L3
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Ticket: bug, size L3, candidate 3 of the spec (section 3). Depends on: step 2 (same file, same lane). L3 because it touches the base order T-0381 and T-0376 settled.

In `plugins/sdlc-lite/scripts/dispatch.py`: add `prepare --tree PATH` to the parser (`dispatch.py:1105-1116`) and a `tree=''` parameter to `prepare` (`dispatch.py:542`). PATH must resolve (by `os.path.realpath`) to a path in `worktrees(<handoff's toplevel>)` (`dispatch.py:517-529`), else raise `Refuse(2, 'dispatch.py: --tree %s is not a worktree of this repository' % PATH)` before the lock, so no record is written. Settle the execution tree once: PATH when given, else `exec_tree(directory)` (`dispatch.py:306-320`). Use that tree's toplevel for `toplevel` (today the handoff's own toplevel, `dispatch.py:652`), so the Tree line, the `tree` key, the tmp prefix (`dispatch.py:653`) and the `worktrees_before` and `branches_before` snapshot follow it; and give `build_base` (`dispatch.py:340-389`) an optional `tree` argument used as its `cwd` in place of its own `exec_tree(directory)` call, so the Base sha comes from the same tree. With no `--tree`, the only behavior change is that a main-checkout handoff dispatched from inside a linked lane worktree gets the lane as Tree, matching the Base sha it already gets. The flag name matches `steps.py split --tree`.

In `plugins/sdlc-lite/agents/conductor.md`, at the dispatch step, add one sentence: when a build runs in a lane worktree while its handoff lives in the primary checkout, run `prepare --tree <lane worktree>`. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to refresh `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`. `docs/references/sdlc-internals.md`: add `--tree` where it lists the prepare flags, if it does.

Contract dependents: the selftest case "a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree" (`dispatch.py:1611-1613`) must still pass unchanged; `record` reads `d['tree']` for `remove_tmp` and `strays` (`dispatch.py:880`) and `deliver` reads it (`dispatch.py:1045`), both consistent as long as `tree` and `tmp_prefix` come from the same execution tree; `redck.py` is left alone (it follows the base `prepare` hands it). Add selftest cases with exactly these labels: `prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree`, `prepare --tree: a path that is not a worktree of this repository is refused, exit 2`, `prepare from a lane worktree for a main-checkout handoff: Tree names the lane, as Base sha does`. Write each label as one string literal on one line, so the (red) source grep finds it. Validation scope: `dispatch.py selftest`, `codex_roles.py generate --check`.
### Acceptance criteria
- (red) `grep -qF 'prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree' 'prepare --tree: a path that is not a worktree of this repository is refused, exit 2' 'prepare from a lane worktree for a main-checkout handoff: Tree names the lane, as Base sha does'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py prepare --help | grep -qF -- '--tree'`
- (red) `grep -qF 'prepare --tree' plugins/sdlc-lite/agents/conductor.md`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree'`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/agents/conductor.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml -e docs/references/sdlc-internals.md)"`

## Step 4: Restart sweep, reused parent pids, and a safe prune --add
level: L2
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Ticket: feature, size L2, candidates 1 and 6 of the spec (sections 1 and 6). Depends on: step 3 (same files, same lane).

In `plugins/sdlc-lite/scripts/dispatch.py`:
- `recover --root DIR` (the `recover` parser, `dispatch.py:1129`; handler `1164-1171`): mutually exclusive with the positional handoff dir. Walk `DIR/.sdlc`, skipping `.git`, `.worktrees` and `node_modules` folders, and for each folder holding a `*.attempt.json` run `recover_orphans` (`dispatch.py:443-458`). Print `recovered: <attempt path>` per orphan, then `  resume: python3 <dispatch.py> prepare <role> <level> <handoff>` from that record; print `running: <attempt path> (pid N)` for a live attempt and leave it alone; print `no orphaned attempts` when there are none. Exit 0.
- `attempt_state` (`dispatch.py:432-440`): a parent pid that is alive but whose process started after the attempt's `started_at` is read as dead (the host reused the pid). Read the start time with `ps -o lstart=` under `LC_ALL=C` as `fleet_status.py:236` does; when it cannot be read, keep today's answer.
- `prune --add NAME` (`dispatch.py:1149-1151`, `prune_add` `808-812`): exit 2 with `dispatch.py: <NAME> has a running attempt <path>; record it before queueing it for pruning` when an attempt record under `<root>/.sdlc` with `agent_name` or `name` equal to NAME reads `running` by `attempt_state`. An orphaned or finished attempt does not block it.
- The refusal text at `dispatch.py:465` that names `run_lifecycle.py recover` stays: it is the force path for a spawn that never started, pinned by the case "a second prepare with a running attempt and a live parent refuses" (`dispatch.py:1718-1719`).
Add selftest cases with exactly these labels: `recover --root marks every orphan under the root interrupted and prints its prepare command`, `negative control: recover --root leaves a live-parent attempt running`, `orphaned: a parent pid that started after the attempt is read as dead (reused)`, `prune --add refuses an agent whose attempt is still running, exit 2`, `negative control: prune --add queues an agent whose attempt is completed`.

In `plugins/sdlc-lite/agents/conductor.md`: add a restart rule (after a host or session restart, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py recover --root .` once before any other dispatch and re-dispatch each run it prints with its resume line); and in item 4 (Prune, `conductor.md:36`) add this sentence verbatim: "Stop only the agents `dispatch.py prune` lists; never stop a sub-agent because it looks idle (one waiting on a background command looks idle), and a prune cron or loop runs `dispatch.py prune` and makes only the calls it prints." Then run `codex_roles.py generate` to refresh `sdlc-conductor-l1.toml`. Optionally point the resume paragraph of `plugins/sdlc-lite/skills/chain/SKILL.md:56` at `recover --root`; update `docs/references/sdlc-internals.md` where it describes `recover` or `prune --add`.

Contract dependents (`git grep -n "dispatch.py recover\|prune --add\|run_lifecycle.py recover" -- plugins docs/references`): `conductor.md:36`, `skills/chain/SKILL.md:56`, `docs/references/sdlc-internals.md:31`, the generated Codex agent TOMLs (regenerated, never edited), and `run_lifecycle.py:79` (Codex refusal, unchanged). Write each label as one string literal on one line, so the (red) source greps find them. Validation scope: `dispatch.py selftest`, `lifecycle-selftest.py` (the plugin guide requires it after a recovery change), `codex_roles.py generate --check`.
### Acceptance criteria
- (red) `grep -qF 'recover --root marks every orphan under the root interrupted and prints its prepare command' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'recover --root marks every orphan under the root interrupted and prints its prepare command' 'negative control: recover --root leaves a live-parent attempt running' 'orphaned: a parent pid that started after the attempt is read as dead (reused)'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `grep -qF 'prune --add refuses an agent whose attempt is still running, exit 2' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'prune --add refuses an agent whose attempt is still running, exit 2' 'negative control: prune --add queues an agent whose attempt is completed'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py recover --help | grep -qF -- '--root'`
- (red) `grep -qF 'dispatch.py recover --root' plugins/sdlc-lite/agents/conductor.md`
- (red) `grep -qF 'never stop a sub-agent because it looks idle' plugins/sdlc-lite/agents/conductor.md`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a second prepare with a running attempt and a live parent refuses'`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/agents/conductor.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml -e plugins/sdlc-lite/skills/chain/SKILL.md -e docs/references/sdlc-internals.md)"`

## Step 5: Lint refuses circular criteria and records every refusal
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Ticket: feature, size L3, candidate 4 of the spec (section 4). Depends on: none (it may run beside steps 2 to 4; it touches only `steps.py`).

In `plugins/sdlc-lite/scripts/steps.py`:
- `lint_steps` (`steps.py:1507-1581`): for each command span of step n, when the span holds `verifier-L` followed by a digit and holds no `step-<m>/` with m other than n, and the criterion line does not end with a held clause (`CLAUSE_RE`, `steps.py:1794`), add the finding `steps: <plan> step <n>: acceptance criterion reads this step's own verifier result, so it can pass only after the verifier passes: <span>` with the hint line `move it to a later step, or declare it held with a trailing [stage: ..., owner: ...] clause`. A span naming `step-<n>/verifier-L...` for its own n is flagged too.
- Refusal record: wherever `lint_or_fail` raises (`steps.py:1584-1587`) and wherever `split` refuses a plan defect (`run_guards`, `steps.py:865-893`, and the red-first refusal), append one JSON line `{"ts": <UTC ISO>, "tool": "steps.py lint" or "steps.py split", "plan": <plan path relative to the task dir's git toplevel>, "step": <n or null>, "text": <first line of the finding>}` per finding to `<task dir>/refusals.jsonl`, skipping a line whose `(plan, text)` is already in the file. The step-handoff link check in `cmd_lint` (`steps.py:1766-1774`) records too. Never record a clean run. Design decision: the record is append-only, lives under `.sdlc` (which every scope criterion excludes), and a write failure (read-only tree) is skipped silently, so no caller's exit code or output changes; it is the only record K-004's early count can read.
Add selftest cases with exactly these labels: `(circ) lint refuses a criterion that reads its own step verifier result`, `(circ) negative control: the same criterion with a held clause passes lint`, `(circ) negative control: a criterion that reads an earlier step verifier result passes lint`, `(circ) a lint refusal appends one line to refusals.jsonl in the task dir`, `(circ) the same refusal of the same plan is written once`. Update the module docstring's lint and split paragraphs (`steps.py:14-60`).

Contract dependents: `dispatch.py prepare` runs `steps.py lint <step dir>` for builder and verifier (`dispatch.py:603-607`); a refusal there now leaves a `refusals.jsonl` line in the task dir under `.sdlc`, which no scope criterion counts (they exclude `.sdlc`). `run_guards` treats a guard that changes the work tree as a defect, but `refusals.jsonl` is written after the guards ran, outside the snapshot. The planner's own probe of `steps.py lint` on a clean plan writes nothing. Validation scope: `steps.py selftest`.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && for l in '(circ) lint refuses a criterion that reads its own step verifier result' '(circ) negative control: the same criterion with a held clause passes lint' '(circ) negative control: a criterion that reads an earlier step verifier result passes lint'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && for l in '(circ) a lint refusal appends one line to refusals.jsonl in the task dir' '(circ) the same refusal of the same plan is written once'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py)"`

## Step 6: Replay a scope-versus-tests heuristic and decide
level: L2
### Read first
- `docs/reports/AGENTS.md`
### Do
Ticket: spike, size L2, candidate 5 of the spec (section 5). Depends on: none. Diagnosis only: no code changes.

Read the two recorded plans read-only: agent-ui T-0060 step 4 (its builder blocked on `mcp-enablement.test.ts` and then asked for `replay.test.ts`; find the step folder from `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-09-12.md` and a search for `builder-L4` results naming those files, lane worktrees included; at plan time no folder named `*0060*` sat within four levels of agent-ui's `.sdlc/`, `.worktrees/` or `.claude/worktrees/`, so search the T-0060 ticket's `handoff.md` front matter by id, and if the step folder cannot be found, replay from the builder report text the retro answer cites and say so in the report) and ultimate-tokens `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/match-peer-lightness/step-2.superseded-1/` (`handoff.md` and `builder-L5.md:31-32`, which name `test/engine/semantic.mjs` and `test/engine/exports.mjs`). For each plan, take the step's scope allow-list and apply the heuristic: for each source path it allows, list the test files in that repository (paths with a `test/`, `tests/` or `__tests__/` segment, or a `.test.` or `.spec.` name) that contain the source file's basename without extension and are not in the allow-list. Also run it on one step of the same plans that passed with its scope unchanged, as the noise control.

Write `docs/reports/<YYYY-MM-DD>-scope-test-lint-replay.md` (the build date): a table per plan of each flagged test and whether it is one of the four known misses, the control step's flags, the commands run, and a last line exactly `Verdict: build` (the heuristic flags at least one of the four known misses and three or fewer tests on the control step) or `Verdict: do not build`. Name all four files in the report whatever the verdict. Do not file the build ticket. Do not edit those two repositories. Validation scope: `docs_check.py`.
### Acceptance criteria
- (red) `ls docs/reports | grep -qxE '[0-9]{4}-[0-9]{2}-[0-9]{2}-scope-test-lint-replay\.md'`
- (red) `for t in mcp-enablement.test.ts replay.test.ts test/engine/semantic.mjs test/engine/exports.mjs; do cat docs/reports/*-scope-test-lint-replay.md | grep -qF "$t" || exit 1; done`
- (red) `cat docs/reports/*-scope-test-lint-replay.md | grep -qxE 'Verdict: (build|do not build)'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'docs/reports/[0-9]{4}-[0-9]{2}-[0-9]{2}-scope-test-lint-replay\.md')"`

## Step 7: Measure verifier minutes and decide on a delta verifier
level: L1
### Read first
- `docs/reports/AGENTS.md`
### Do
Ticket: spike, size L1, candidate 7 of the spec (section 7). Depends on: step 1 (it reads `attempts.by_role`). Measurement only: no code changes.

Run `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>` (read-only; about 90 s per repository on this host) for ultimate-tokens, ui-kit-maison and agent-ui over the last full retro window, and read `attempts.by_role.verifier`. From the same repositories' attempt records, count re-verifies: second and later verifier attempts in one handoff dir, and their minutes. Write `docs/reports/<YYYY-MM-DD>-verifier-minutes.md` (the build date): the commands run, a table per repository (verifier count, median and max minutes, re-verify count and share of verifier minutes), and a last line exactly `Verdict: build a delta verifier` when re-verifies take 25 percent or more of verifier minutes in ultimate-tokens or agent-ui, else `Verdict: do not build a delta verifier`. Report maison's share beside them as the control the spec names (its rounds came from unmet prerequisites, not fixes) and do not let it decide the verdict. If the verdict is build, the report proposes a verifier-minutes KPI in one line; it files nothing and adds no `docs/kpi/` file. Validation scope: `docs_check.py`.
### Acceptance criteria
- (red) `ls docs/reports | grep -qxE '[0-9]{4}-[0-9]{2}-[0-9]{2}-verifier-minutes\.md'`
- (red) `for t in 'fleet_collect.py collect' ultimate-tokens ui-kit-maison; do cat docs/reports/*-verifier-minutes.md | grep -qF "$t" || exit 1; done`
- (red) `cat docs/reports/*-verifier-minutes.md | grep -qxE 'Verdict: (build a delta verifier|do not build a delta verifier)'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py`
- (guard) `test -z "$( { git diff --name-only "${SDLC_BASE_SHA:?}" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'docs/reports/[0-9]{4}-[0-9]{2}-[0-9]{2}-verifier-minutes\.md')"`

## Step 8: Gates green
level: L2
guard timeout: 1900
### Do
Not a ticket to file: the integration check after steps 1 to 7 land on one branch. Depends on: steps 1 to 7. Run every gate below and fix any red the earlier steps introduced; a gate already red at this step's build-start HEAD is reported as `inherited red`. `check.sh` took 615 s at plan time of task 0233 (`docs/work/.0233-reorg-apply/planner-L3-2.md`, Assumptions); the timeout is about three times that.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "${SDLC_BASE_SHA:?}"`

## Assumptions
- `prepare` already recovers dead-parent attempts, so candidate 1 needs no prepare change: verified by `dispatch.py:443-466` and `645-648`, and by maison's `.sdlc/tickets/.0154-wire-standalone-scripts-and-regenerate-once/verifier-L3.attempt.json` (finished_at 16:09:03Z) and `verifier-L3-2.attempt.json` (started_at 16:09:04Z), parent pids 26358, 32887, 3278, all dead (`ps -p`).
- `record` with no file and empty stdin closes the attempt failed for good: verified by `dispatch.py:906-938` and `890-891`.
- The Tree line ignores `exec_tree`, and `prepare` has no tree option: verified by `dispatch.py:652-653`, `306-320`, `1105-1116`, and `dispatch.py prepare --help` (no `--tree`, probe run).
- T-0408 held clauses are on main and unreleased: verified by `steps.py:1788-1794` and `git tag --contains ee59144b` (empty); T-0371 is in v0.22.0 and later (`git tag --contains 8f1a6d96`); T-0381 is in v0.22.1 and v0.22.2 (`git tag --contains 5a3334a1`).
- `split --only` already runs guards before build: verified by `steps.py:865-893` and its docstring (`steps.py:31-46`).
- `queue_prune` queues only recorded completions, and `prune --add` checks nothing: verified by `dispatch.py:848-862`, `808-812`, `1149-1151`.
- Every `(red)` criterion is red now for the reason the step removes (a missing selftest label, a missing flag in `--help`, a missing sentence, a missing report, or the KPI note still present), and every `(guard)` is green at base: verified by one probe run per criterion on 2026-10-09 with `SDLC_BASE_SHA=HEAD` (reds in the tree, guards in a `git worktree add --detach` copy at 8277055c). The `dispatch.py` and `steps.py` selftest criteria were evaluated against one cached run of each selftest at this HEAD (both exit 0; `dispatch.py selftest` took 129 s), not re-run per criterion. `check.sh` was not run at plan time; its time comes from the record named in step 8.
- The goal, KPI and spec documents and this plan are committed before step 1 is split: assumed, not verified. While `docs/goals/`, `docs/kpi/` and `docs/specs/sdlc-lite/restart-and-blocked-run-plan.md` stay untracked, every scope guard reads them as untracked files and is red (observed in this tree).
- The K-002, K-003 and K-004 baselines are from `docs/work/plan-reliability-docs/kpi-baseline-probe.py`, run once over four repositories on 2026-10-09: verified as a command output, unverified as a KPI value (the collector cannot read them yet).

## Risks
- Step 1's orphan count uses `kill(pid, 0)`, which reads a reused pid as alive; step 4 adds the start-time check to `dispatch.py` only. The collector undercounts orphans until it reuses that check; a later ticket can share it.
- Step 2 changes what conductors see when they record early: exit 2 instead of 1. A conductor script that treats any nonzero exit as failed and re-dispatches would now re-dispatch a run that is still going; the message names the path and the `--no-result` flag, and the conductor text is not changed in this step.
- Step 3's default change (Tree follows `exec_tree`) moves the tmp prefix for a main-checkout handoff dispatched from a lane; a run started before the change and recorded after it reads the old `tmp_prefix` from its dispatch file, so it is unaffected.
- Step 5 adds a write to `steps.py lint`, which plans and guards call. A guard that runs `steps.py lint` on a plan that refuses would now change `.sdlc`; the scope guards exclude `.sdlc`, but `split --only`'s work-tree snapshot covers the whole tree. The step writes the record after the guard snapshot; if a plan's own guard runs a refusing lint, that guard was red anyway.
- Step 6 and step 7 read other repositories' records, which move; their reports are dated evidence of one window, and their verdicts can flip on another window.
- `check.sh` was not run at plan time (it takes about 10 minutes and other agents share the host); step 8 may come back `inherited red`.
- The spec sits in `docs/specs/sdlc-lite/` as the handoff named, though the docs layout puts unbuilt proposals in `planning/`; its status line says proposal. The `docs/specs/sdlc-lite/AGENTS.md` managed block does not list it, because `onboard.py setup --dry-run` would also rewrite the root `AGENTS.md` and `docs/references/AGENTS.md`, which this task must not edit; `docs_check.py` does not require the listing.
