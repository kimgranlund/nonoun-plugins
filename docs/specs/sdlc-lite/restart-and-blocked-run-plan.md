# Restart and blocked run plan (0.22.3 candidates)

Status: proposal, not built. Version 0.1, 2026-10-09, written by the planner of task `plan-reliability-docs`. It serves [G-002](../../goals/002-restart-and-blocked-run-cost.md), measured by [K-002](../../kpi/002-restart-recovery-minutes.md), [K-003](../../kpi/003-blocked-builders-per-wave.md) and [K-004](../../kpi/004-unsatisfiable-criteria-caught.md). The ordered tickets are the steps of `docs/work/plan-reliability-docs/plan.md`; no ticket is filed yet.

Sources: [the fleet retro of 2026-10-09](../../reports/2026-10-09-fleet-retro-00.md) and the 12 hour answers in ui-kit-maison, agent-ui and ultimate-tokens (`.sdlc/fleet-retro-2026-10-09-12.md` in each). Evidence labels: [V] read in the file or command named, [U] reported by a conductor and not checked here. Line numbers are at commit 011a2577; the cited files are unchanged at 8277055c.

## Summary

| # | Candidate | Verdict | Size | KPI | Plan step |
|---|---|---|---|---|---|
| 1 | Orphaned attempts after a host restart | The block is already handled; what remains is finding every lost run at once | L2 | K-002 | 4 |
| 2 | `record` before the result file exists | Confirmed defect | L2 | none of G-002's; see section 2 | 2 |
| 3 | Stale primary checkout as Tree and Base sha | Partly fixed by T-0381; the Tree line and a main-checkout conductor remain | L3 | K-003 | 3 |
| 4 | Circular criteria | Mostly covered by T-0408 held criteria; a lexical lint remains | L3 | K-004 | 5 |
| 5 | Scope lists missing tests, guards that cannot read 0 | Guards are already run before build; the scope half needs a diagnosis first | L2 | K-003, K-004 | 6 |
| 6 | Prune stops waiting agents | The script is safe for recorded agents; `--add` and conductor text remain | L2 | K-002 | 4 |
| 7 | Delta verifier | Measure first; no build in this plan | L1 | none yet | 7 |

Plan step 1 adds the collector fields the three KPIs read, and step 8 runs the repository gates. Order: 1 first (the KPIs need it), then 2, 3 and 4 in one lane because all three edit `dispatch.py` and 3 and 4 both edit the conductor, while 5 and 6 can run beside them; 7 after 1; 8 last.

## Measures (plan step 1, and the refusal record of step 5)

`fleet_collect.py` lists interrupted attempts with `started_at` only (`fleet_collect.py:371-389`) [V], never counts an attempt still `running` whose parent is dead, sums `duration_ms` from `runs.jsonl` (`fleet_collect.py:362`) which `record` fills only from `--duration-ms` (`dispatch.py:958`) [V], and reads no result file. So K-002 to K-004 and the verifier minutes of candidate 7 cannot be read from it. Step 1 adds: per interrupted attempt `lost_min` with `runs.interrupted.lost_min_median` and `lost_min_total`; `runs.orphaned` (count and list); `results.builder` (`total`, `blocked`); `plan_defects` (`late` from result files, `early` from `refusals.jsonl`); and `attempts.by_role` (count, median and max minutes of completed attempts from `started_at` to `finished_at`). All keys are new, so `fleet_detect.py`, `fleet_status.py`, `plan_check.py` and the fleet-retro skill, which read the collector's output, keep working unchanged. A read-only stand-in for these fields is `docs/work/plan-reliability-docs/kpi-baseline-probe.py`, which gave the unverified baselines in the KPI files.

## 1. Orphaned attempts after a host restart

**Outcome and why.** After a restart the conductor finds every run the restart killed with one command and re-dispatches each, instead of discovering them one handoff dir at a time. Maison reports about 2 hours of repeated verification and 4 manual recovery turns over three restarts [U]; agent-ui reports four crashed planner and reviewer runs [U].

**Current behavior.** `prepare` already recovers the case the retro names. Under the directory lock it calls `settle` (`dispatch.py:645-648`), which marks every running attempt whose recorded parent pid is dead as interrupted (`recover_orphans`, `dispatch.py:443-458`; the dead-pid test is `attempt_state`, `dispatch.py:432-440`) and refuses only while a running attempt's parent is a live process other than the caller (`dispatch.py:456-457`, refusal at `dispatch.py:461-466`). The caller's own running attempts are skipped since T-0371 (in v0.22.0 and later, `git tag --contains 8f1a6d96`) [V]. Maison's records fit this: `.sdlc/tickets/.0154-wire-standalone-scripts-and-regenerate-once/verifier-L3.attempt.json` was marked interrupted at 16:09:03Z and `verifier-L3-2` started at 16:09:04Z, and the parent pid changed at each restart (26358, 32887, 3278, all dead now) [V], so the next `prepare` recovered each one without a separate `recover`.

Two gaps remain [V]. `dispatch.py status` and `recover` take one handoff dir (`dispatch.py:1129`, `1164-1171`), so a conductor learns of each dead run only when it next touches that dir; on 2026-10-09, 13 attempts were still `running` with a dead parent (maison 3, ultimate-tokens 1, sdlc-lite 9, from the probe), invisible to the collector. `attempt_state` trusts `kill(pid, 0)` alone (`dispatch.py:216-225`), so a parent pid the host reused after a restart reads as alive and `prepare` refuses; `fleet_status.py` already reads a pid that started after its marker as dead (`fleet_status.py:236`, rule at `379`). The refusal names `run_lifecycle.py recover` (`dispatch.py:465`), which marks every running attempt in the dir interrupted with no pid check (`run_lifecycle.py:39-52`); that is the deliberate force path for a spawn that was denied or never started, pinned by the selftest case "a second prepare with a running attempt and a live parent refuses" (`dispatch.py:1718-1719`), and it stays.

**Change.** `dispatch.py recover --root DIR` walks `DIR/.sdlc` (skipping `.git`, `.worktrees` and `node_modules`), runs `recover_orphans` on every dir that holds an attempt record, and prints one `recovered: <path>` line per orphan followed by its `resume:` line, the `dispatch.py prepare <role> <level> <handoff>` command; a live attempt prints `running: <path> (pid N)` and is left alone. `attempt_state` reads a parent whose process started after the attempt's `started_at` as dead (reused), with the `ps -o lstart=` read `fleet_status.py` uses. The conductor gets one rule: after a host or session restart, run `dispatch.py recover --root .` once before any other dispatch and re-dispatch what it prints. The per-dir form stays.

**KPI.** K-002 (it cuts the gap after the crash; the lost work before it stays, see the KPI's Reading it).

**Rubric.**
1. Every orphan under the root is recovered and printed with its prepare command | pass: the step's selftest case.
2. A live attempt is untouched, and a reused pid reads as dead | pass: the two selftest cases.
3. The conductor names the sweep | pass: `agents/conductor.md` holds `dispatch.py recover --root` and `codex_roles.py generate --check` exits 0.
4. No regression | pass: `dispatch.py selftest` and `lifecycle-selftest.py` exit 0.

**Negative control.** A running attempt whose parent pid is the selftest's own (alive, started before the attempt) must still read `running` after `recover --root`; a sweep that marks it interrupted fails the case.

**Size, files, order.** L2. `plugins/sdlc-lite/scripts/dispatch.py`, `plugins/sdlc-lite/agents/conductor.md`, the generated `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`, optionally `plugins/sdlc-lite/skills/chain/SKILL.md` (its resume paragraph) and `docs/references/sdlc-internals.md`. Plan step 4, with candidate 6, after step 3 in the same lane.

## 2. `dispatch.py record` before the role wrote its result

**Outcome and why.** Recording a role before its file exists never closes the attempt, so the role's report, written a moment later, can still be recorded. Maison saw four attempt rows (architect, planner, plan-reviewer, builder) closed `failed` this way, read as invalid by the board and `steps.py review` [U].

**Current behavior.** Confirmed [V]. With no result file, empty stdin and no transcript result, `record` sets the error `no result file at <path> (the <role> must write its report there before it ends)` (`dispatch.py:927`), writes `<stem>.log`, and closes the attempt `failed` with exit 1 (`dispatch.py:928-938`). A second `record` is then refused because the attempt is not running (`dispatch.py:890-891`). The T-0330 selftest case pins the failure on purpose: "a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line" (`dispatch.py:1994-1996`).

**Change.** When the result file is missing or empty, stdin is empty or whitespace, and no transcript yields a result, `record` exits 2 and leaves the attempt `running`, with no `.log`, no `runs.jsonl` line and no verdict delivery, printing `dispatch.py: no result yet at <path>; the attempt stays running: record again once the <role> writes it, or pass --no-result to close it failed`. A new `--no-result` flag keeps today's path (exit 1, the T-0330 error text, attempt `failed`). Stdin with error text and a `max_tokens` transcript still close the attempt `failed`, as now. The T-0330 case passes `--no-result` and keeps its label; the module docstring's `failed` paragraph (`dispatch.py:90-92`) is updated. `run.sh` is untouched: the Codex runner waits for its process and has no such window.

**KPI.** None of G-002's counts it: a false `failed` row is neither an interruption nor a blocked builder. The count to watch is attempts closed `failed` with the error `no result file at` whose result file exists afterwards; it can be read with a one-line grep over `.attempt.json` files and is not promoted to a KPI.

**Rubric.**
1. No file and empty stdin exits 2 and leaves the attempt running | pass: selftest case.
2. A record after the file appears completes the attempt | pass: selftest case.
3. `--no-result` keeps the T-0330 failure | pass: the T-0330 case, label unchanged, and a `--no-result` case.
4. No regression | pass: `dispatch.py selftest` exits 0.

**Negative control.** Error text on stdin with no file must still close the attempt `failed`, exit 1; a change that leaves every no-file record running fails that case.

**Size, files, order.** L2. `plugins/sdlc-lite/scripts/dispatch.py`, `docs/references/sdlc-internals.md` if it describes the failed path. Plan step 2, first in the dispatch lane.

## 3. Dispatch prompts name the stale primary checkout

**Outcome and why.** A builder dispatched for a lane worktree is told that worktree as its Tree and that worktree's base as its Base sha, even when the conductor runs `prepare` from the primary checkout. Maison had three builders block on `stale lane` because the primary checkout sat on branch candidate-8, 329 commits behind main [U]; one builder's Notes confirm its red checkpoint was recorded against the primary checkout (`ui-kit-maison/.sdlc/tickets/0346-gap-buildout-wave-plan/step-2/builder-L3.md:33`) [V].

**Current behavior.** T-0381 (merged 2026-10-08, in v0.22.1) fixed the base order: `build_base` picks a base named in the handoff, then the recorded `base-sha`, then HEAD of the execution tree (`dispatch.py:340-389`), and `exec_tree` makes the execution tree a lane worktree only when `prepare` itself runs inside that linked worktree (`dispatch.py:306-320`) [V]. Two gaps remain [V]: the Tree line and the tmp prefix use the handoff's own toplevel (`dispatch.py:652-653`, prompt at `661-665`), not `exec_tree`, so a main-checkout handoff dispatched from inside a lane gets the lane as Base sha but the main checkout as Tree; and a conductor whose shell is in the primary checkout has no way to name the lane, because `prepare` takes no tree option (`dispatch.py:1105-1116`), so both lines name the stale checkout.

**Change.** `prepare --tree PATH`: PATH must be a worktree registered in `git worktree list` of the handoff's repository, else exit 2 (`--tree <path> is not a worktree of this repository`). With it, PATH is the execution tree for the Tree line, the `tree` key, the tmp prefix, the worktree and branch snapshot, and the git calls of `build_base`. Without it, the Tree line and tmp prefix use the toplevel of `exec_tree`, the same tree the base comes from. The conductor's dispatch text names `prepare --tree <lane worktree>` for a build that runs in a lane while the handoff lives in the primary checkout. Name chosen to match `steps.py split --tree` [V].

**KPI.** K-003 (each stale-tree block is a blocked builder).

**Rubric.**
1. `--tree` sets Tree, Base sha and the tmp prefix to the lane | pass: selftest case.
2. A path that is not a worktree of the repository is refused | pass: selftest case.
3. Without `--tree`, a main-checkout handoff dispatched from a lane gets the lane as Tree | pass: selftest case.
4. The existing lane-handoff case still holds | pass: "a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree" (`dispatch.py:1611-1613`).
5. No regression | pass: `dispatch.py selftest` exits 0 and `codex_roles.py generate --check` exits 0.

**Negative control.** `--tree` naming a directory outside the repository must exit 2 and write no attempt record; accepting it fails the case.

**Size, files, order.** L3: it touches the base order T-0381 and T-0376 settled, a known landmine. `plugins/sdlc-lite/scripts/dispatch.py`, `plugins/sdlc-lite/agents/conductor.md`, `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`, `docs/references/sdlc-internals.md`. Plan step 3, after step 2 in the dispatch lane. Left alone: `redck.py`, whose checkpoint follows the base and tree `prepare` hands it.

## 4. Unsatisfiable or circular criteria

**Outcome and why.** A criterion that can pass only after its own step's verifier passes is refused before the build, and a criterion the lane cannot meet is declared held instead of failed. Maison's T-0154 criterion 2 (`npm run check` green) needed a pair that `renderer-adoption.mjs:137` adopts only after a verifier pass, which cost one L3 verifier run [U].

**Current behavior.** T-0408 (on main after v0.22.2, untagged: `git tag --contains ee59144b` is empty) lets a handoff end a criterion with a held clause (`CLAUSE_RE`, `steps.py:1794`, keys stage, owner, needs), so a verifier reports `deferred <owner>` instead of fail [V]. That is the designed answer for maison's case, whose dependency sits inside a project script and is invisible in the criterion text: no lint can see it, and this plan does not try. `lint_steps` checks parse, `||` joins, pinned shas, fixed counts, `grep -P`, clean status and clean diff, and never runs a span (`steps.py:1507-1581`) [V]. It has no rule for a span that reads the step's own verifier result, and no refusal is recorded anywhere (`cmd_lint`, `steps.py:1766-1785`, prints and exits).

**Change.** Two parts in `steps.py`. (a) Lint refuses a criterion span in step n that names a verifier result (`verifier-L<d>`) and names no `step-<m>/` folder other than its own, unless the criterion line ends with a held clause; the message says to move the check to a later step or declare it held. (b) Each refusal from `lint` or `split` appends one JSON line `{ts, tool, plan, step, text}` to `refusals.jsonl` in the task dir, the record K-004's early count reads; the same refusal of the same plan file is written once. Since 0.23.0 a split refusal is instead one `- <YYYY-MM-DD> plan defect at split: step <n>: <why>` line under the task handoff's `## Plan review`, which `fleet_collect.py` counts; `refusals.jsonl` is no longer written.

**KPI.** K-004.

**Rubric.**
1. A criterion reading its own step's verifier result is refused | pass: selftest case.
2. The same criterion with a held clause passes | pass: negative control case.
3. A criterion reading an earlier step's verifier result passes | pass: selftest case.
4. A refusal leaves one line in `refusals.jsonl` (0.23.0: one `plan defect at split` line in `## Plan review`) | pass: selftest case.
5. No regression | pass: `steps.py selftest` exits 0.

**Negative control.** A criterion that greps `step-1/verifier-L2.md` from step 2 must pass lint; a rule that flags every `verifier-` path fails it.

**Size, files, order.** L3 (two mechanisms, and a write added to a command that was read-only). `plugins/sdlc-lite/scripts/steps.py` only. Plan step 5, independent of the dispatch lane.

## 5. Scope lists that miss tests, and guards that cannot read 0

**Outcome and why.** A plan whose scope list forbids a test the change must edit is flagged before the build. agent-ui's T-0060 step 4 builder blocked on `mcp-enablement.test.ts` and then asked for `replay.test.ts` [U]; ultimate-tokens' T-0040 step 2 builder blocked on `test/engine/semantic.mjs` and `test/engine/exports.mjs` outside the scope guard, and on a `report-compute-neutral` guard that reads 0 at base but cannot read 0 once the step's change renders differently (`ultimate-tokens/.sdlc/match-peer-lightness/step-2.superseded-1/builder-L5.md:31-32`) [V].

**Current behavior.** Guards are already evaluated before the build: `split --only N` runs every `(guard)` span at HEAD and refuses a red one or one that changed the tree (`run_guards`, `steps.py:865-893`) [V]. The ultimate-tokens guard was green at base, so no pre-build run catches it; it is red only against the finished change, which is the verifier's job, and the architect had named the problem in prose. That half is not a lint and is dropped. Scope lists are checked by nothing: a scope allow-list and the tests that reference the files it allows are never compared [V].

**Change.** Diagnosis first, no build in this plan. Replay one heuristic by hand on the two recorded plans: for each source file a step's scope allow-list holds, list the test files that name its basename and sit outside the allow-list. Write the result as a dated report under `docs/reports/` with a `Verdict:` line: `build` when the heuristic flags at least one of the four tests above, otherwise `do not build`. A build, if any, is a `steps lint: warning:` line (never a refusal), filed as its own ticket from the report.

**KPI.** K-003 and K-004, only if the build follows.

**Rubric.**
1. The report exists under `docs/reports/` with a date-led name | pass: file present.
2. Each of the four missed tests is named with whether the heuristic flags it | pass: grep for each.
3. The report ends in a `Verdict:` line, build or do not build | pass: grep.
4. Docs stay clean | pass: `docs_check.py` reports 0 errors.

**Negative control.** The report must also run the heuristic on one step whose scope was right (a passed step of the same plans) and state whether it flags a test there; a heuristic that flags every test is the noise that makes `do not build` the verdict.

**Size, files, order.** L2. One new report. Plan step 6, independent.

## 6. Prune safety

**Outcome and why.** Only agents whose result is recorded are ever stopped. ultimate-tokens' cron job `e5fa0b85`, every 10 minutes, stopped a solo that was waiting on a background `npm test`, losing about 40 minutes of work [U].

**Current behavior.** The script is safe for what `record` queues [V]: `queue_prune` runs only after a completed record, only for a dispatch with `prune` true, and skips an agent with another open attempt or pending follow-ups (`dispatch.py:848-862`, called at `990`); a builder defaults to `prune` false (`PRUNE_ROLES`, `dispatch.py:138`, applied at `679`). `dispatch.py prune` only prints `TaskStop` lines; it stops nothing (`dispatch.py:822-827`). The conductor is told to make only the calls it lists (`agents/conductor.md:36`). Two holes remain [V]: `prune --add NAME` queues any name with no attempt check (`dispatch.py:808-812`, CLI at `1149-1151`), and nothing says not to stop an agent for looking idle. The cron's rule ("stop idle agents") was the conductor's own, not the script's [U].

**Change.** `prune --add NAME` exits 2 when an attempt record under the root's `.sdlc` with that agent name is `running` with a live parent, printing that it must be recorded first. One sentence in `agents/conductor.md` item 4: stop only the agents `dispatch.py prune` lists; never stop a sub-agent because it looks idle (one waiting on a background command looks idle); a prune cron or loop runs `dispatch.py prune` and makes only the calls it prints.

**KPI.** K-002 (a stopped run is lost work).

**Rubric.**
1. `--add` refuses a running agent | pass: selftest case.
2. `--add` queues a completed one | pass: negative control case.
3. The conductor rule is present | pass: grep in `agents/conductor.md`, and `codex_roles.py generate --check` exits 0.
4. No regression | pass: `dispatch.py selftest` exits 0.

**Negative control.** `--add` of an agent whose attempt is `completed` must still queue it; a check that refuses every `--add` fails the case.

**Size, files, order.** L2, in plan step 4 with candidate 1 (same two files, same lane).

## 7. Delta verifier

**Outcome and why.** A re-verify after a fix checks only the delta, if the numbers show whole-ticket re-verifies cost enough. ultimate-tokens reports whole-ticket L3 verifiers of 43 and 56 minutes [U].

**Current behavior.** No measure exists. The collector's durations come from `runs.jsonl` `duration_ms` (`fleet_collect.py:362`), which sub-agent rows leave null unless `--duration-ms` is passed (`dispatch.py:958`); agent-ui reports `duration 0.0` for every run [U]. The probe read attempt records instead: ultimate-tokens' 15 completed verifier attempts on 2026-10-09 ran a median 8.6 and a maximum 50.6 minutes, maison's 60 a median 14.6 and a maximum 109.9 (attempt start to record, which includes the wait for `record`) [V, probe run once].

**Change.** None in this plan. After plan step 1, measure with the collector's `attempts.by_role` per repository for one retro window and count re-verifies (second and later verifier attempts in one handoff dir) and their minutes. Write a dated report with a `Verdict:` line: `build a delta verifier` when re-verifies take 25 percent or more of verifier minutes in the window, else `do not build a delta verifier`. A build is its own design and ticket.

**KPI.** None yet; the report proposes a verifier-minutes KPI if the verdict is build.

**Rubric.**
1. The report exists with a date-led name | pass: file present.
2. It cites the collector command it ran | pass: grep `fleet_collect.py collect`.
3. It covers ultimate-tokens and ui-kit-maison | pass: grep.
4. It ends in a `Verdict:` line | pass: grep.

**Negative control.** The report states the re-verify share for maison too, where verifier rounds came from unmet prerequisites rather than fixes; a verdict that would read build on maison's numbers alone shows the share is measuring rounds, not deltas.

**Size, files, order.** L1. One new report. Plan step 7, after step 1.

## Not covered

Checkpointing a role's partial work so a restarted run resumes it (the larger lever for K-002), host load (T-0386), the batched verifier of several steps (maison), and `steps.py widen` keeping the red checkpoint hash (agent-ui). Each is a ticket of its own if wanted.
