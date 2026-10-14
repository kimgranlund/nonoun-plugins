<!-- role=architect level=L1 model=opus effort=xhigh -->
## Approach
A ticket's committed record is its task `handoff.md`. Everything else a ticket's work writes (role results, step folders, attempt, dispatch, limit, delivery and Codex request files, `runs.jsonl`, `base-sha`, `skips.md`, `red-checkpoint.jsonl`, `budget-ack.md`, design and decompose drafts) moves to a records dir under the already-ignored `.sdlc/runtime/`. The records dir is keyed by the task folder name without its leading dot: `.sdlc/runtime/tasks/<name>/`, with step folders inside it. The key does not change when close renames `NNNN-slug/` to `.NNNN-slug/`, so a close that reaches another checkout by merge leaves no stray files behind. `.sdlc/runtime/.gitignore` already holds `*` (dispatch.py:965-970), so consumer repos need no `.gitignore` edit. One rule resolves the dir: `records_dir(task_dir)`, in Python in `order.py` and in shell in a new `scripts/records.sh`.

Inside the records dir, a result, its attempt file, its dispatch file, `runs.jsonl` and `base-sha` stay next to each other. Code that finds these files by adjacency (dispatch record, results.attempt_reported, block-role-write.sh, next_stem, the run lock) therefore keeps working once `artifacts_dir` points at runtime. The only cross-boundary pair is a task handoff and its records. Readers that start from a task dir go through `records_dir`. `order.records/ordered` resolve it internally, so steps.py next, lane, resume and review need no call-site edits. Legacy rule: if the runtime dir does not exist and the task dir already holds `runs.jsonl` or `*.attempt.json`, `records_dir` returns the task dir. In-flight tickets therefore finish where they started, and closed folders stay readable with no migration.

Close replaces the filer. `tickets.py close` writes `## Outcome` into the handoff: one header line (date, lane, verdict, verifier, base) and then `Changed`, `Commits`, `Check`, `Deviation` and `Follow-up` lines. Their sources are the newest verifier result in the records dir, `git log` subjects starting `T-NNNN:`, redck audit rows, and the close flags. Without a passing verifier result or a recorded verifier skip, close refuses unless `--reason` is given; this replaces the filer-warnings gate. Follow-up candidates come from the verifier's `## Notes` bullets and keep today's explicit `--ticket <i> --expect <digest>` selection. The filer remains available only when asked (`/file`, `close --filer`). The side files stop, and their content moves as follows:
- Redck deviations stay as audit rows in `red-checkpoint.jsonl` and become Outcome `Deviation:` lines.
- Split refusals become one `## Plan review` line in the task handoff.
- `hints.md` has no writer to stop.
- Fleet-retro interview answers go by `messages.py send`.
- Retro intermediates go to the retro's records dir. The retro report stays in `docs/reports`.

Fanout is the only place where records cross worktrees through git, so its transport changes from commit to copy. Land copies the lane worktree's records dir into the integration worktree before close, and copies the closed ticket's records into the main checkout's runtime afterwards. The verdict is read from the lane's records dir. Git objects remain the fallback when the branch has no worktree, and in that case close untracks those files (`git ls-files -ci --exclude-standard`) before its commit. A dry-run-default `tickets.py tidy` moves loose top-level `.sdlc` entries into `archive/`, and `check` warns on them.

Decomposition: `.sdlc/0539-lean-work-records/decompose/manifest-v1.json` (technical-architecture, plan mode), coverage_check clean, quadrant load-bearing. A sub-agent derived the inside-out plane from the handoff text alone.

Build tickets. Lane is chain for each (L3 and up). Waves keep one writer per file.

| Ticket | Size | Wave | Files | Done when |
|---|---|---|---|---|
| A. Records dir | L4 | 1 | `scripts/order.py` (`records_dir`; a `records-dir <task dir>` CLI that prints the path for the conductor, skills and Codex; `records`/`ordered`/`_results` resolve it), `dispatch.py` (prepare `artifacts_dir`, `build_base`, `next_stem`, `attempt_dirs`/`recover`/`resume`/`status` walk `runtime/tasks/*` plus legacy dirs, `lane_gate`, `solo_model`), `run.sh`, `run_lifecycle.py`, `solo_run.py`, `steps.py` (split/swap/widen write step dirs in the records dir; `record_lane`, `write_solo_skips`, `base_sha`, `result_ts`), `redck.py` (path only), `budget.py` (ack and `spend`), `verify_scope.py`, `codex_exec.py` (top-level `native-*` request files into `runtime/`), new `scripts/records.sh`, `hooks/block-role-spawn.sh` (read the prompt's `Artifacts dir:` line, else beside the handoff), `hooks/warn-handoff-edit.sh`, `lifecycle-selftest.py`, `run-selftest.sh`, `hook-selftest.sh`, `skills/handoff-format/SKILL.md` layout block :9-78, `adapters/codex/instructions.md` resume packet | `bash plugins/sdlc-lite/scripts/check.sh` exits 0. A new dispatch.py selftest case: prepare plus record in a git fixture leaves `git status --porcelain -- <task dir>` listing only `handoff.md`, with the records under `.sdlc/runtime/tasks/<name>/`. Negative control: a legacy fixture with `runs.jsonl` in the task dir keeps recording in place. Hook selftest: spawn allowed through the `Artifacts dir:` line, denied when neither location holds a dispatch file |
| B. Cost, board and fleet readers | L3 | 2 | `report.py`, `solo_stats.py`, `board.py`, `fleet_collect.py` (`scan_sdlc`, `ticket_of` maps `runtime/tasks/<name>` to `<name>`, lane from Outcome for closed rows, plan defects from `## Plan review` lines), `fleet_status.py`, `traces/ingest.py` (`SKIP_TASK`), `traces/sources/*.py`, `traces/rerun.py`, `proposals.py` (`SKIP_TOP`), `footprint.py`, `plan_done.py` (`runs.jsonl`; `plan-state.json` into the plan folder's records dir), `reorg.py` (`held_locks` :386-400 looks for `.run.lock` in records dirs), `statusline.sh`, `bench-summary.sh` | Selftests of report, solo_stats, board, fleet_collect, fleet_status, plan_done and traces exit 0 with a runtime-only fixture that reports nonzero cost under the right ticket key. Negative control: the same fixture with the runtime dir removed reads the legacy in-folder records |
| C. Fanout carries records by copy | L3 | 2 | `fanout.py` (`commit_lane_records` becomes a copy; `branch_verdict` and `host_branch_ticket` read the lane worktree's records dir, else git objects; the :1574 copy condition no longer keys on `filer-L*.md`; the :1199-1213 copy includes the records dir; the close commit untracks ignored records; integration records are copied to the main checkout's runtime; headless prompt :446-450 drops the filer), `lanes.py` (`copy_sdlc` archive includes `runtime/tasks/<name>`), `skills/fanout/SKILL.md`. An external lane with no worktree delivers its verdict by committing the verifier result into the ticket folder with `git add -f`, which is the prefix the git-objects fallback reads, and land untracks it in the close commit | `fanout.py selftest` exits 0 with a land whose close commit tracks only `handoff.md` under the ticket folder, and a branch with no worktree still lands from git objects. Negative control: with the copy step removed, land reports `no verifier result` |
| D. Close writes the Outcome | L3 | 3 | `tickets.py` (`cmd_close` Outcome composer, verdict gate, follow-ups from verifier `## Notes`, `--filer`, `--changed`, `--reason` writes an Outcome, T-0529 placeholder gate, citation scan skips `runtime/` plus T-0535 `citation_skip:`, `skip_problems` reads open folders only, claim staleness from `.running` at :1363 through `records_dir`, help text and selftests that name `## Closed` at :53,91,94,3528,4248,6052, router close procedure :1815-1825), `redck.py` (`deviations` subcommand; no `process-deviations.md`), `steps.py` (split refusal becomes a `## Plan review` line; no `refusals.jsonl`), `check.py` :186,:695, `agents/{conductor,verifier,builder,solo,filer}.md` plus regenerated agents (`claude_roles.py`, `codex_roles.py`), `skills/{chain,file,fix,ticket,open-questions}/SKILL.md` (/fix and chain loose ends write hand-written step handoffs under `order.py records-dir`) | `tickets.py selftest` and `redck.py selftest` exit 0 with: a close over a passing verifier result appends `## Outcome` with `lane:`, `verdict: pass`, `Check:` and `Commits:` lines; a failing newest verifier makes close refuse (negative control); a handoff still holding the bug template's Repro prompt refuses and the filled-in one closes (T-0529); a marked inventory file is skipped by the citation scan and the unmarked one refuses (T-0535); no `process-deviations.md` or `refusals.jsonl` exists after the fixtures run. Generated-agent parity check passes |
| E. Layout rule and tidy | L2 | 4 | `tickets.py` (top-level allow-list `check` warning, `tidy [--apply]`, router `Folder layout` and `Ticket lifecycle` sections, `claim --by <word>` from T-0534), `skills/fleet-retro/{SKILL.md,interview.md}`, `skills/{grill,review-traces,bench}/SKILL.md` (write in the records dir), `onboard.py` "Work records" block :382-391 | `tickets.py selftest` exits 0 with: `check` warns on a stray top-level file and stays silent for an allowed name (negative control); `tidy` without `--apply` changes nothing; `tidy --apply` moves the stray file into `archive/` and refuses while a `*.running` marker exists; `claim --by astra` is accepted |
| F. Docs and release 0.23.0 | L2 | 5 | `skills/handoff-format/{run-operations.md,references/writing-rules.md}` (the T-0529 rules, cut down to the handoff and Outcome), `docs/specs/sdlc-lite/{design.md,solo-lane-contract.md,cost-control.md,cascade-guard.md,plan-doc-executor.md,restart-and-blocked-run-plan.md}`, `docs/specs/ticket-stages/design.md`, `docs/planning/docs-schema/design.md` (B-2, B-4, B-5), `docs/references/sdlc-internals.md`, `docs/specs/doc-standards/{delivery.md,knowledge-ops.md}`, `plugins/sdlc-lite/AGENTS.md`:66, CHANGELOG built from `git log --format=%s <last tag>..HEAD` subjects starting `T-`, both plugin manifests and marketplace parity, dated release report | `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py` and `git diff --check` pass. `git diff --quiet <wave base> -- plugins/sdlc-lite/adapters/claude/levels.json plugins/sdlc-lite/adapters/codex/models.json` exits 0. In a throwaway project, a live solo L2 ticket on the release build leaves `git ls-files .sdlc/.NNNN-*` equal to that ticket's `handoff.md` |

Queue verdicts. When filing, rewrite each `depends:` line to the new order.

| Ticket | Verdict | Reason |
|---|---|---|
| T-0528 detect delivered tickets | keep, wave 1 | Does not touch run records. It also strengthens the `T-NNNN:` commit-subject convention that the Outcome and release notes now rely on |
| T-0529 writing rules and placeholder gate | merge | The placeholder gate edits `cmd_close`, so it goes into D. The writing rules now govern only the handoff and Outcome, so they go into F. A separate ticket would be a third writer of the same function |
| T-0530 lane record on the ticket | keep, rescoped, wave 3 after B and C | The need (verified but unmerged work is visible) stays. The committed `branch:` field is dropped because it adds two committed edits per lane to the one committed file. `lanes.py list --all` instead finds the ticket and newest verdict in each worktree's `.sdlc/runtime/tasks/*` |
| T-0533 split lint creates marker | keep, wave 2 after A | Independent lint fix in `steps.py`. Its evidence file `refusals.jsonl` stops, which does not change the fix |
| T-0534 top-level layout, claim names, lifecycle page | merge into E | It is the same allow-list, check and router text E writes. `claim --by` changes the same router block |
| T-0535 close inventory skip marker | merge into D | D already edits the citation scan, which must skip `runtime/`, so the marker belongs in the same change |
| T-0536 plan-defect order and amend route | keep, wave 4 after D | Independent `steps.py` behavior. Record the amend as a `## Plan review` handoff line, not a new file |
| T-0537 dispatch limit stop and row-change notice | keep, wave 2 after A | `.limit` and `runs.jsonl` now sit in the records dir that A defines. Otherwise unchanged |

Wave plan: 1 is A with T-0528. 2 is B, C, T-0537 and T-0533. 3 is D with T-0530. 4 is E with T-0536. 5 is F. Release only after wave 5. The installed 0.22.7 build runs from the plugin cache, so intermediate states on main affect no running tool.

Migration for consumer repos:
- Closed ticket folders: left untouched. Their tracked records stay, and the legacy rule reads them.
- Open tickets started before 0.23.0: finish in place under the legacy rule, then close with an Outcome.
- `tickets.py tidy` (dry run by default; `--apply` acts):
  - It lists each top-level entry under `.sdlc/` that git tracks or shows as untracked, is not ignored, and is not allowed. Allowed: `AGENTS.md`, `CLAUDE.md`, `config`, `roadmap.md`, `board.md`, `notes.md`, `notes/`, `fleet.json`, `gate-ledger.jsonl`, `messages/`, `runtime/`, `supervisor/`, `evals/`, `proposals/`, `goals/`, `tickets/`, `work/`, `archive/`, any folder holding `handoff.md` or `plan-doc.md`, and the `top_level_allow:` globs in `config`.
  - Each listed entry gets the destination `archive/<name>`.
  - `--apply` uses `git mv` for tracked entries and a rename for untracked ones. It refuses while any `*.running` exists under `.sdlc/` or a destination exists.
  - It never touches the project root or a closed ticket folder. `check` names `tidy` when it warns.

## Interfaces
- `order.records_dir(task_dir, create=False) -> Path` (new). Base: the nearest ancestor named `.sdlc`, else the task dir's parent. It returns `<base>/runtime/tasks/<task_dir.name.lstrip('.')>/`. It returns `task_dir` itself when the task dir sits inside `runtime/tasks` already, or when that runtime dir is absent and the task dir holds `runs.jsonl` or `*.attempt.json` (legacy). A `step-*` dir whose parent is a task dir resolves to `records_dir(parent)/step-N/`, so a hand-written step never gets a key of its own. With `create=True` it makes the dir and writes `runtime/.gitignore` (`*`) if missing, reusing the `prune_edit` code.
- `scripts/records.sh` (new): the same rule as a sourced shell function `records_dir <task dir>`, for run.sh and the hooks.
- `python3 order.py records-dir <task dir>` (new): prints the path, for the conductor, skills and the Codex adapter, which cannot import `order.py`.
- Brief: `Artifacts dir:` (dispatch.py:818, run.sh:429) becomes the records dir. `Handoff:` stays the task handoff for task-level roles and becomes `<records dir>/step-N/handoff.md` for step roles.
- `tickets.py close <folder> [--changed "<line>"] [--filer] [--reason "<why>"] [--dry-run] [--ticket <i> --expect <digest>] [--skip ...] [--ack-warnings "<why>"] [--rewrite-refs|--keep-refs]`. Default route: verdict gate, then Outcome. `--filer`: today's filer route. `## Closed` is no longer written. Only tickets.py's own help and selftests name it (tickets.py:53,91,94,3528,4248,6052), and no reader parses it.
- `tickets.py tidy [--apply]` (new). `tickets.py check` gains the top-level warning. `config` gains `top_level_allow:` (E) and `citation_skip:` (D).
- `redck.py deviations <dir>` (new): one line per deviation audit row.
- Outcome contract, written by D and read by B (fleet_collect, board) and T-0530:
  ```
  ## Outcome

  <YYYY-MM-DD> · lane: <solo|full|fix> <level> · verdict: <pass|skipped (<why>)|closed by reason> · verifier: <role-level> (<model>) · base: <sha12>
  - Changed: <--changed text, else "see commits">
  - Commits: <sha7> <subject>; ... (git log <base>..HEAD, subjects starting T-NNNN:) | none
  - Check: #<k> <criterion>: pass   (one per verifier criterion)
  - Deviation: <redck deviation | acknowledged warning | kept stale ref | docs or tests-gate waiver>
  - Follow-up: <tag>: <title> -> T-NNNN | notes.md
  ```
- Split refusal line in the task handoff `## Plan review`: `- <YYYY-MM-DD> plan defect at split: step <n>: <why>`.

Inventory and fates. Locations: H is the handoff dir (step dir for step roles, task dir otherwise), T is the task dir, top is the top level of `.sdlc/`. Fates: keep (committed or as today), runtime (records dir, ignored), stop.

| File | Where today | Writer | Readers | Fate |
|---|---|---|---|---|
| `handoff.md` (task) | T | tickets.py new/claim/close, steps.py:2788, budget.py:174, solo_run.py:323; handoff, clarify and chain skills | every role, tickets.py, steps.py | keep, plus `## Outcome` |
| `## Plan review`, `## Acceptance criteria` sections | T handoff | chain/SKILL.md, conductor.md:44, solo.md:53 | planner, verifier, steps.py:2763 | keep |
| `## Closed` section | T handoff | tickets.py:2370,2521 | none | stop (Outcome replaces it) |
| `step-N/handoff.md`, `step-N.superseded-k/` | T | steps.py:1895-1908,3391,3638; chain and fix skills | builder, verifier, steps.py | runtime |
| `<role>-<level>[-k].md` results, `solo-<level>-<id>.md` | H, T | dispatch.py:1196, run.sh:673, solo_run.py:636 | order.py, steps.py, tickets.py, fanout.py:1959, fleet_collect.py:364 | runtime |
| `filer-L*.md` | T | filer via /file, chain 5.1, fanout.py:446 | tickets.py:2386, open-questions | stop by default; runtime when asked |
| `*.attempt.json` (+ `.tmp-*`) | H | dispatch.py:863,1106,1144, run_lifecycle.py | dispatch status/resume/recover, report.py:646, fleet_collect.py:441, fleet_status.py:354, traces | runtime |
| `*.dispatch.json`, `<ticket>-solo-<level>.dispatch.json` | H, T | dispatch.py:864, solo_run.py:186, fanout.py:1900 | block-role-spawn.sh, block-role-write.sh, dispatch.py:385, board.py:512, fanout.py:2313 | runtime |
| `*.running`, `.run.lock`, `*.log`, `solo.stream.log` | H | dispatch.py:866, run.sh:643,655, run_lifecycle.py:30, solo_run.py:652 | warn-handoff-edit.sh, board, statusline.sh, fleet_status, reorg.py:386 | runtime (already ignored) |
| `*.limit`, `solo.limit` | H, T | dispatch.py:942, run.sh:636, solo_run.py:292 | resume, fleet_collect | runtime |
| `*.delivery.json` | H | dispatch.py:1246-1318 | dispatch deliver | runtime |
| `*.request.*` (Codex exchange); top-level `native-*.request.json` | H; top | run.sh:437, codex_exchange.py, codex_exec.py:31-34 | codex_exchange.py | runtime (`native-*` into `runtime/`) |
| `base-sha` | H | dispatch.py:816, run.sh:502 | dispatch.py:381, run.sh:448, steps.py:861, tickets.py:1517, board.py:508, fanout.py:2312, redck, specgate, traces/rerun.py | runtime |
| `runs.jsonl` | H | dispatch.py:1222, run.sh:704, solo_run.py:333,371, fanout.py:1802 | order.py, board, report, solo_stats, budget, plan_done, fleet_collect, fleet_status, traces, proposals, footprint | runtime |
| `skips.md` | T | dispatch.py:852, run.sh:354, steps.py:3160,3176, tickets.py:1582, fanout.py:1980; conductor.md:63, fix skill | dispatch.py:425, steps.py:2953, tickets.py:1476, verify_scope.py:254, board, solo_stats, fleet_collect | runtime; the lane also goes on the Outcome header |
| `red-checkpoint.jsonl` | H | redck.py:62,149 | redck audit, verify_scope.py:267 | runtime |
| `process-deviations.md` | step dir | redck.py:63,296 | verifier.md:13, filer.md:8-14 (prose), check.py:186,695 | stop; Outcome `Deviation:` |
| `refusals.jsonl` | T | steps.py:1638,1689 | fleet_collect.py:527 | stop; `## Plan review` line |
| `hints.md` | T | no plugin writer (legacy `.0463` only) | none | stop (nothing to change) |
| `budget-ack.md` | T | budget.py:40,193 | budget.py | runtime |
| `design.md`, `decompose/` | T | grill/SKILL.md:33, decompose/SKILL.md:39, architect | plan-reviewer.md:14, coverage_check | runtime |
| `plan-doc.md` | `.sdlc/<plan>/` | plan doc skill | plan_check, plan_done | keep |
| `plan-state.json` | plan dir | plan_done.py:303 | plan_done.py | runtime |
| bench `handoff.md`/`grade.md`; review-traces `cluster-*`, `finding-*`, `propose/`, `report.md` | T | bench, review-traces skills | those skills | runtime (task `handoff.md` keeps) |
| Codex resume packet | T | adapters/codex/instructions.md:37 | next session | runtime |
| `roadmap.md`, router `AGENTS.md`/`CLAUDE.md`, `config` | top | tickets.py:1764,1980,498 | all | keep |
| `notes.md` | top | tickets.py close, promote.py, plan skills, run-plan | ask, conductor | keep |
| `board.md` | top | no script writer | user | keep (allowed) |
| `fleet.json`, `gate-ledger.jsonl` | top | fleet_config.py:64, fanout.py:2687 | fleet scripts, fanout cover | keep |
| `messages/`, `supervisor/` | top | messages.py, supervisor.py | messenger, supervisor | keep (ignored or self-ignored) |
| `runtime/` (`prune.json`, `report/`, `traces/`, `load.jsonl`, `fleet-status.json`) | top | dispatch.py:948, report.py:247, traces/store.py:46, fleet_status.py:265 | same scripts | keep; gains `tasks/` |
| `fleet-retro-<date>.md` interview answer | top (consumers) | fleet-retro/interview.md:40 | fleet-retro/SKILL.md:36 | stop; `messages.py send` |
| `fleet-retro-<date>/` work folder | top | fleet-retro/SKILL.md:24-32 | fleet_detect, verifier | runtime (`runtime/tasks/fleet-retro-<date>/`) |
| `docs/reports/fleet-retro-<date>.md`, release reports | docs/reports | fleet-retro/SKILL.md:40, release | verifier, readers | keep |
| per-ticket `docs/reports/*` | none found | none | none | stop (rule in F) |
| `docs/<home>/<name>.md` via promote | docs | promote.py:85 | readers | keep (explicit only) |
| `pause-*.md`, root-cause and rollout notes | top (hand or role) | no plugin writer | none | tidy moves into `archive/` |
| `.worktrees/fanout/` logs, `report.md`, `land.jsonl`; `.lane.json`; host lane records | worktrees | fanout.py, lanes.py | same | keep (ignored) |
| `.git/solo_run.lock`, `solo_live/`, `sdlc-lane-archive/` | git dir | solo_run.py, lanes.py:630 | same | keep (the archive gains `runtime/tasks`) |
| `~/.cache/.../board-state`, `~/.local/state/.../gate-lock` | home | board.py:413, gate_lock.py | same | keep |
| `.codex/agents/*.toml`, `.codex/config.toml` | project root | codex_roles.py | Codex | keep (install) |
| `CLAUDE.local.md` section | project root | compaction `--write-handoff` (opt-in) | host | keep (opt-in) |

Per-reader replacement:

| Reader | Input today | Replacement |
|---|---|---|
| report.py, solo_stats.py cost views | `runs.jsonl`, attempts, `skips.md` in each task folder | the same files through `records_dir` for open and closed folders. Closed folders without a runtime dir use in-folder legacy records. A ticket closed in another clone shows no cost (local by decision) |
| budget.py spend | rglob of `runs.jsonl` per ticket | rglob of `records_dir(task)` (in A, since dispatch prepare gates on it) |
| steps.py next, lane, resume, review | `runs.jsonl` and results via order.py; `step-*` in the task dir | order.py resolves `records_dir`; step dirs live in the records dir |
| dispatch.py resume, recover, status | `**/*.attempt.json` under task dirs | walk `runtime/tasks/*` plus legacy task dirs. `--open` maps a key to an open folder |
| tickets.py close: filer warnings | `filer-L*.md` Warnings and Follow-ups | newest verifier verdict gate. Follow-ups from verifier `## Notes`, or the filer with `--filer` |
| tickets.py close: skip records | `skips.md`, `runs.jsonl` in the task dir | same files through `records_dir`. `check` reads open folders only |
| tickets.py close: red checkpoint audit | verify_scope tests_gate reads `red-checkpoint.jsonl` beside the handoff | through `records_dir`. Deviation rows are copied to the Outcome |
| fleet_collect.py (other repos) | os.walk of `.sdlc` in each worktree; `ticket_of` by first path part; nearest `skips.md`; `refusals.jsonl` | the walk includes `runtime/tasks/<name>`, mapped to `<name>`. The lane comes from the records-dir `skips.md`, else the Outcome `lane:`. Plan defects come from `## Plan review` "plan defect at split" lines |
| fleet_status.py | markers, attempt pids and `runs.jsonl` beside the handoff | through `records_dir` |
| board.py | cost, attempt n, base, solo lane, `.running` | through `records_dir`. The lane of a closed row comes from the Outcome |
| traces ingest, proposals, footprint | task-dir walk that skips `runtime` | treat `runtime/tasks/*` as task dirs |
| verifier evidence | builder or solo results, step handoffs, `base-sha`, `process-deviations.md` beside the handoff | brief `Artifacts dir:` = records dir. Deviations through `redck.py deviations`. The durable copy is the Outcome `Check:` lines |
| hooks | `dispatch.json` and `.running` beside the handoff | block-role-spawn reads the `Artifacts dir:` line; warn-handoff-edit maps through `records.sh`; block-role-write unchanged |
| fanout branch_verdict, host_branch_ticket | git objects on the lane branch | the lane worktree's records dir, else git objects |
| plan_done.py | `runs.jsonl`, `plan-state.json` in the plan dir | through `records_dir` |

## Constraints and assumptions
- More than 30 code sites find records by adjacency, plus three hooks and run.sh: verified by a reader search over `plugins/sdlc-lite/scripts` and `hooks` (dispatch.py:1129, results.py:202, order.py:26-52, block-role-spawn.sh:101-110, block-role-write.sh:30, warn-handoff-edit.sh:15).
- `.sdlc/runtime/` ignores itself in consumer repos: verified by `runtime/.gitignore` = `*` and dispatch.py:968-970.
- The brief already names the artifacts dir: verified at dispatch.py:818 and run.sh:429.
- `tickets.py close` runs no git commands. Fanout land force-adds the whole ticket folder: verified at fanout.py:2156-2166. Close commits use `add -A` and honor ignores (fanout.py:1598-1604).
- An external lane can have no worktree: verified at fanout.py:2119 (`checked_out.get(branch)`).
- Nothing parses `## Outcome` or `## Closed` in a handoff today. `## Outcome` appears only in plan docs: verified by the reader search, plan_check.py:587-590, and a grep for `Closed` over scripts, skills and agents, which finds only tickets.py help, tickets.py selftests and a section-parser fixture at fleet_collect.py:998.
- `hints.md` has no writer in the plugin: verified by the writer and brief searches.
- Intermediate waves on main do not affect running tools, because the installed plugin runs from the 0.22.7 cache: verified from this role's own plugin path. Unverified for every consumer setup.
- A task folder name is unique across ticket roots: unverified for the topics layout (`tickets/` and `work/`).
- Verifier `## Criteria` and `## Notes` sections can be parsed for the Outcome: the contract is verified at agents/verifier.md:43-60; parser reuse (`results.notes_lines`, fanout.py:1583) is unverified for Criteria.

## Rejected alternatives
- Keep records in the task folder and ignore them by name through a committed `.sdlc/.gitignore`. This is the smallest reader change, since about 30 adjacency readers stay untouched. Rejected because a close rename that reaches another checkout by merge would leave the ignored files in a stray `NNNN-slug/` beside `.NNNN-slug/` (the main checkout after every fanout wave). Hiding that needs both land pre-folding and a tidy fold. Name patterns can also swallow real files, and the maintainer decision names a runtime folder.
- Delete records at close: breaks local cost views and the restart path for that ticket.
- Keep committing records and `git rm` them in the close commit: every lane merge still commits them, and history keeps them.
- Key the runtime dir by ticket id: un-numbered task folders (plan docs, `merge-*`, fleet-retro) have no id. The undotted folder name covers every case and does not change on close.
- One shared runtime in the git common dir for all worktrees: it would remove fanout copying, but concurrent worktrees would share one tree with no per-task lock, and consumers do not look there. Left as a possible later step.
- Keep the filer by default for follow-ups: against the maintainer decision. The verifier's Notes plus an explicit `--ticket` pick keep follow-up selection explicit.
- T-0530's committed `branch:` field: the lane link is runtime state, and the field would add two commits per lane to the one committed file.

## Risks
- Silent degraders. A reader missed in A or B fails quietly:
  - budget.py:80-107 reads $0 and the gate never trips.
  - tickets.py:1476-1514 `skip_missing` returns None and the close guard is off.
  - order.py:26-33 falls back to name order and flips every "newest" pick.
  - fleet_collect.py:315-322 files every row under ticket `runtime`.

  Each needs a runtime-only fixture in its ticket's done-when. A guard grep in check.py that rejects a `runs.jsonl` or `*.attempt.json` path joined to a task dir outside `records_dir` would catch new ones. It needs its own negative control.
- A spike's deliverable result (this design, for example) leaves git at close. The conductor must carry it into the filed tickets, or promote it with `promote.py`, before closing. D's dry run should name unpromoted architect, researcher and archaeologist results.
- Claude-host isolated sub-agent worktrees start from HEAD without the runtime dir. Solo lanes need only the committed handoff, but a role whose brief points at the main checkout's runtime must not be cut off. C's selftest has to cover this.
- A fresh clone has no run history for closed tickets. Cross-machine fleet retros see local records only, which follows from the maintainer decision.
- Between waves 1 and 2 on main, the cost and fleet views read zero for new tickets. Release only after wave 5.
- If the maintainer intended step handoffs to stay in git, A's scope shrinks, but the adjacency argument for moving them still holds.

## Carry forward
- Records rule: `<nearest .sdlc>/runtime/tasks/<folder name without leading dot>/`, with step dirs nested inside it. Legacy fallback when that dir is absent and the task dir holds `runs.jsonl` or `*.attempt.json` (this design, Interfaces).
- `runtime/.gitignore` = `*` is written by `prune_edit` (dispatch.py:965-970); reuse it.
- The brief carries `Artifacts dir:` at dispatch.py:818 and run.sh:429. block-role-spawn.sh:101-110 looks beside the handoff.
- fanout.py:2156-2166 `commit_lane_records` force-adds the folder. `branch_verdict` (:1959-1979) and `host_branch_ticket` (:1989-2010) read git objects. `lane_wt` may be None (:2119).
- fanout.py:1574-1576 copies the lane folder into integration only when no `filer-L*.md` is there.
- tickets.py:2386-2397 refuses close without a filer file unless `--reason`. `## Closed` is written at :2370 and :2521.
- Silent degraders (reader search over scripts/ and hooks/): budget.py:80-107, tickets.py:1476-1514, order.py:26-33, fleet_collect.py:315-322, traces/ingest.py:43, proposals.py:89.
- Location-pinning selftests: lifecycle-selftest.py:56-77,148-204; run-selftest.sh:40-45,156; dispatch.py:1892-1909,2336-2354; tickets.py:3386-3409,5427; board.py:891-910; fleet_status.py:1495-1692; report.py:1712-1724; solo_run.py:945-953.
- `process-deviations.md` is written at redck.py:293-297. Only prose reads it (agents/verifier.md:13, agents/filer.md:8-14); check.py:186,695 pin the phrase.
- `refusals.jsonl` is written at steps.py:1638,1689. Its only reader is fleet_collect.py:527-541.
- Docs that state the old rule: skills/handoff-format/SKILL.md:78 ("keep results, runs.jsonl, attempt.json committed"), docs/planning/docs-schema/design.md:48-51 (B-2), docs/specs/sdlc-lite/design.md:138-154.
- Router close procedure: tickets.py:1815-1825 (filer step :1816). Fanout headless filer prompt: fanout.py:446-450.
- Filer runs by default in chain/SKILL.md:31,79,85 and the fanout full lane. Solo, /fix and solo fanout lanes skip it (fanout.py:935).
- Decompose manifest: .sdlc/0539-lean-work-records/decompose/manifest-v1.json, coverage_check exit 0.
