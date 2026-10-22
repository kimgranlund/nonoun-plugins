# Changelog

SDLC Lite releases, newest first, in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) form. Each entry is built from the `T-NNNN:` commit subjects since the previous tag (`git log --format=%s <last tag>..HEAD`); the dated release report in `docs/reports/` holds the upgrade notes and the verification record. Releases before 0.23.0 are recorded only in those reports. Progressive Context is versioned separately.

## [0.33.0] - 2026-10-22

Report: [docs/reports/2026-10-22-release-0-33-0.md](docs/reports/2026-10-22-release-0-33-0.md). From CPU diagnostics on a second fleet machine (T-0716).

### Added

- `gate_lock.py run` samples the total RSS of the gate's process tree every 2 s and stops a tree over `max_rss_mb` (SIGTERM, then SIGKILL; descendants that left the group are killed before the drain), releases the grant, prints `gate_lock: stopped <name>: process tree RSS <x> MB over max_rss_mb <N>` and exits 137. `max_rss_mb` defaults to 25% of physical RAM; `policy set max_rss_mb=0` turns it off (T-0716).

## [0.32.0] - 2026-10-22

Report: [docs/reports/2026-10-22-release-0-32-0.md](docs/reports/2026-10-22-release-0-32-0.md). Addresses GitHub issues #46, #47 and #48 (T-0713 to T-0715).

### Added

- `dispatch.py record --update <dispatch>` re-records a completed attempt after a review-fix resume: it restores the report header, validates the report, and for a builder moves end-sha so the verifier's Diff range covers the fix; it adds no runs.jsonl line. `advance` and the conductor's review relay name it (T-0714, #47).

### Changed

- A lane close clears the ticket's `branch:`/`worktree:` record in the integration tree first and leaves main untouched when the integration branch carries the clear, so `git merge --ff-only` of the integration branch no longer refuses; a clear that must land in main when the target is not main is committed there (T-0713, #46).
- `steps.py review` prints repo-relative `reason:` and `read:` paths, and every line `steps.py` appends under `## Plan review` strips the repo prefix; `/chain` says to write the replan result path repo-relative (T-0715, #48).

## [0.31.0] - 2026-10-22

Report: [docs/reports/2026-10-22-release-0-31-0.md](docs/reports/2026-10-22-release-0-31-0.md). Fixes found in an agent-ui planner run and by verifiers: T-0706 to T-0712.

### Changed

- `block-role-write.sh` lets a read-only role Write under this repo's scratch root, the parent of the brief's `Scratch files ... only under` dir, compared as real paths; Edit, NotebookEdit and every other Write stay blocked, and the hook fails closed without `python3` or `wtroot.py` (T-0706).
- Prepared briefs say to write each worktree and rm path literally under the brief's prefix, never through `$T`, `$S` or `$SDLC_TMP_WORKTREES` (T-0707).
- `block-role-rm.sh` and `block-stray-worktree.sh` map `$SDLC_TMP_WORKTREES` to the prefix only when the variable is set in the hook's environment; unset, the path is refused, since the shell would run it at `/` (T-0708).
- Builder, verifier, planner and plan-reviewer definitions show `"<throwaway prefix>/base"` instead of the variable form (T-0709).
- `run.sh` prompts, Claude and Codex, name the throwaway prefix as a literal path (T-0711).
- Briefs and the builder definition say the runner removes the throwaway prefix and scratch dir after the run, so roles no longer `rm -rf` them (T-0712).
- The gate_lock `case_rr` load-cap cases now fail when the cap check is removed; three docs corrected (T-0710).

## [0.30.0] - 2026-10-22

Report: [docs/reports/2026-10-22-release-0-30-0.md](docs/reports/2026-10-22-release-0-30-0.md). Addresses GitHub issue #44 (machine-wide concurrency): T-0697 to T-0703, plus follow-ups T-0704 and T-0705.

### Added

- `fanout.py prep` warns when a `--gate` runs `node --test`, `vitest`, `playwright` or `jest` with no worker cap; `skills/fanout/references/land.md` lists each runner's flag for `$SDLC_GATE_WORKERS` (T-0699).
- `fanout.py prep` prints the live gate-lock holders from other repos and, when the load is over `max_load`, opens 1 lane with `prep: load <x> over <max>: opening 1 of <n> lanes`; `prep --force` opens every lane (T-0700).
- `dispatch.py status` flags `report-unrecorded` for a report newer than its unrecorded attempt, including interrupted and limit-stopped ones; the resume message tells the agent to `SendMessage` "main" when done (T-0703).
- Every brief carries a search-scope line: search only inside Tree and the Artifacts dir (T-0702).

### Changed

- `gate_lock.py` caps admission at `0.8 x` the CPU count when `policy.json` sets no `max_load`; `max_load=0` turns it off. The cap applies only while a grant is held, so outside load never starves the queue (T-0697).
- Builder, solo and verifier run full test suites, browser tests and `check.sh` through `gate_lock.py run --need compute_units=N --nice` (T-0698).
- `settle --forward --gate` runs its gates at the integration tip when main is already in the integration branch, unless the ledger already holds a pass there (T-0701).
- Role hooks resolve a named teammate's role from its real agent type (`customAgentType` in the sub-agent meta file), falling back to the spawn name; before this, every role hook skipped named teammates (T-0702, T-0704).
- `block-disk-scan` also blocks `mdfind` with no `-onlyin` below the blocked roots (T-0702).
- `report-written-unrecorded` is merged into `report-unrecorded`; `status` prints one token (T-0705).

## [0.29.0] - 2026-10-21

Report: [docs/reports/2026-10-21-release-0-29-0.md](docs/reports/2026-10-21-release-0-29-0.md). Addresses GitHub issues #32 to #43 and the reopened #10, #11 and #22, from the ui-kit 0.27 vs 0.28 measurement.

### Added

- `steps.py routes [<path>...]` prints the resolved repo skill routes; `onboard.py check` warns when an AGENTS.md names `.agents/skills/*/SKILL.md` but resolves no route (T-0677, #11).
- `fanout.py settle <integration> --catch-up` merges main into an integration branch, regenerating the roadmap, router and notes files, and stops (T-0681, #34).
- `.sdlc/config` `merge_union: <globs>` and `merge_union_gate: <cmd>`: land union-merges those paths and runs the gate before committing the merge (T-0683, #38).
- `dispatch.py settle-held <verifier result> --by conductor --evidence <path>` settles a `deferred: conductor` held criterion, which steps, close and land then read as pass; a result with any unparsed criteria line never reads as settled (T-0684, T-0696, #35).
- `fanout.py queue` prints the land holding `merge.lock` and the lands waiting on it (T-0687, #37).
- `--tickets T-1,T-2` on `lanes.py open` and `tickets.py claim` (T-0691, #43).
- `lanes.py ready --notify-cmd <cmd>` runs a command when a ready is pinned (T-0694, #39).
- Briefs carry `Ports: SDLC_LANE_PORT=<n>` when the lane holds a port (T-0693, #41).

### Changed

- Skill routing reads markdown links to a SKILL.md and cued prose lines in a nested AGENTS.md, so repos that route skills that way get `Read first:` lint and the `Repo skills for this step:` brief line (T-0676, #11).
- `prepare` stamps `plugin_version` on the dispatch and attempt; `record` accepts a result prepared under another version that fails the current format as `legacy-format`, instead of failing a pass (T-0678, #33).
- `dispatch.py`, `solo_run.py` and `fanout.py` print one stderr line when a newer plugin version is in the cache; `conductor.md` says to re-resolve the scripts path after `/reload-plugins` (T-0679, #33).
- `lanes.py open --into <integration>` records the claim and lane in the integration tree, not on main, and `lanes.py close` clears it there (T-0680, T-0695, #34).
- Solo briefs from `solo_run.py` and `fanout.py prep` carry `Report file:` and a one-line pointer, and `record` reads the solo report file (T-0682, #10).
- `record --agent-id` ignores stdin under 40 characters with no heading when the transcript holds a complete result (T-0685, #36).
- `record` prints a repo-relative `- Review record:` line for ui-designer reviews; `steps.py lint` warns on an absolute home path in a criterion (T-0686, #22).
- `dispatch.py advance` also handles solo, ticket verifier and review completions (T-0688, #32).
- `fanout.py prep` and `land` reuse an integration branch checked out in another worktree (T-0689, #42).
- `dispatch.py status` lists `step-*/` attempts and says where to look when it finds none (T-0690, #40).
- `lane_setup:` runs every config line in order and prints `setup: ok` or the failing command (T-0692, #41).
- `lanes.py ready` prints the missing-mailbox warning once per session (T-0694, #39).

## [0.28.1] - 2026-10-20

Report: [docs/reports/2026-10-20-release-0-28-1.md](docs/reports/2026-10-20-release-0-28-1.md).

### Fixed

- `tickets.py close` no longer drops a follow-up as a duplicate because it starts with the same file path as a filed ticket: the slug key skips leading path-like words, and a same-title follow-up is still a duplicate (T-0675, reported by agent-ui).

## [0.28.0] - 2026-10-20

Report: [docs/reports/2026-10-20-release-0-28-0.md](docs/reports/2026-10-20-release-0-28-0.md). All 23 open GitHub issues (#9 to #31, a context-routing audit of a ui-kit-neue session) are addressed.

### Added

- `dispatch.py advance`: record, prune, `steps.py next` and the next `prepare` in one call per role completion; it prints the TaskStop id and the next Agent JSON (T-0645, #9).
- Every role writes its result to the `Report file:` its brief names and ends with one line `<role> <status> <path>`; `record` reads the file (T-0646, #10).
- Plan steps carry routed repo skills under `### Read first`, and `steps.py lint` refuses a step that edits a routed path without its skill; a list item routes only with a cue such as `->`, read, use or follow (T-0647, T-0672, #11).
- `prepare` adds `Repo skills for this step:` to builder and solo briefs from the repo's skill routing (T-0648, #11).
- ui-designer review writes `## Verdict pass | pass-with-notes | changes-required`, marks each finding blocking or advisory with `Rule: <skill>#<section>` or `Rule: gap`, and lists `## Guidance gaps`; `results.py` refuses a pass beside a blocking finding (T-0649, #12).
- `traces` finding `guidance-gap`: a proposed rule recurring in 3 or more tickets, offered by `/review-traces` as a chore ticket (T-0650, #12).
- `tickets.py close --lessons TEXT` writes `- Lessons:` lines; the roadmap lists unrouted `decide:` and `source-fix:` NOTES.md items under `## Open follow-ups`, and `check` counts them (T-0652, T-0653, #13).
- `fanout.py sync <lane>` merges the integration branch into a running lane, takes generated and hash-bound files from it, and `--paths` copies guidance only (T-0654, #14).
- `prepare` warns when a lane's AGENTS.md or CLAUDE.md differs from main, and refuses (exit 5) a named guidance path present on main or the integration branch but missing in the lane (T-0655, T-0674, #15).
- `steps.py review` runs each `(red)` criterion at the base commit and reports one already green as a plan defect (T-0657, #17).
- A verifier brief carries `Diff range: <base>..<end>` from the `end-sha` that `record` writes after a build (T-0661, #21).
- A write-once `designs/` docs home for grill output with `supersedes:`; docs_check D-15 flags a missing superseded file (T-0664, #24).

### Changed

- A `--reason` close files follow-ups like a verified close, and refuses a reason that names a different lane from the recorded one (T-0651, T-0670, #13, #30).
- `settle --forward` refuses while a role runs against the integration branch; `--force` skips the check (T-0656, #16).
- `redck` ignores the ticket folder under the work root when judging the tree dirty (T-0658, #18).
- Every SKILL.md stays under 18,000 characters, with detail moved word for word into `references/`; `check-packaging.py` fails a larger one (T-0659, #19).
- Plan lint flags an every, all or each criterion with no command, and `git stash` or `--autostash` in Do text; the verifier answers a quantified criterion as k of N (T-0660, T-0666, #20, #26).
- NOTES.md, the Outcome and the gate ledger hold repo- or lane-relative paths; `check` warns on an absolute machine path in a tracked record (T-0662, #22).
- Conductor guidance and every skill say `record --agent-id <id>` finds the transcript, with nothing on stdin; `check.py` item 41 now forbids `--transcript` in skill record calls (T-0667, T-0673, #27).
- The ui-designer reads a repo skill's SKILL.md first and opens a reference only when its cue matches (T-0668, #28).
- Solo dispatch records go to the records dir; close moves leftover untracked files out of the ticket folder, and `check` warns on an undotted folder with no handoff (T-0669, #29).
- Onboard's AGENTS.md block says `.sdlc/` holds tickets and their task plans, plan docs under review go to `docs/planning/`, and `docs/work/AGENTS.md` shows the stage counts; `docs/AGENTS.md` links a frozen home's router only when it exists (T-0663, T-0671, #23, #31).
- Each generated level-variant agent carries a one-line description, `<role> at level <Ln>: <model> <effort>. Same role as the <role> agent.`; the longest drops from 408 to 81 characters (T-0665, #25).

### Removed

- The `plan-goal`, `plan-campaign`, `plan-doc` and `plan-fanout` redirect stubs and `check.py` item 58; run `/sdlc-lite:plan <kind>` (T-0665, #25).

## [0.27.0] - 2026-10-19

Report: [docs/reports/2026-10-19-release-0-27-0.md](docs/reports/2026-10-19-release-0-27-0.md).

### Added

- `tickets.py inventory [--into BRANCH]... [--days N] [--json]`: a read-only row per open or recently closed ticket and branch with its landed state (`ancestor`, `pr merged`, `patch`, `content`, `not landed`, `cannot decide`) and its newest verifier verdict. `lanes.patch_landed` holds the `git cherry` test that `orphans` and `inventory` share; `lanes.landed` checks it only when called with `patch=True` (T-0644, design T-0584).
- `traces` finding `idle-wakes`: conductor turns fired by a loop or cron that changed nothing; `traces.py ingest --conductor-transcript` feeds it (T-0643).

### Changed

- `plan_check.py loop` fails a fixed-interval status loop with `status-polls-running-work`. `plan-loop` no longer offers status loops, and `run-plan` names the interval-free driver turn: run `plan_done.py`, dispatch the first open item in the background, end the turn (T-0643, design T-0583).

### Fixed

- `--rewrite-refs` on `close`, `archive`, `number` and `migrate-layout` leaves files under the `docs/layout.md` Frozen paths (and `rewrite_skip:` globs in `.sdlc/config`) unchanged and lists each as `kept frozen:`. The `onboard.py` refusal for a malformed Frozen paths list names the one-backticked-glob-per-line form (T-0577).

## [0.26.0] - 2026-10-19

Report: [docs/reports/2026-10-19-release-0-26-0.md](docs/reports/2026-10-19-release-0-26-0.md).

### Added

- `.sdlc/by-hand.md`, generated by `tickets.py roadmap` beside the router: how to create, claim, release and close a ticket with git and a POSIX shell when the plugin is not installed, plus the rules the plugin's hooks enforce. The router links it in one line; a close by hand writes `verdict: closed by hand (unverified)` and `tickets.py check` warns on each one (T-0641).

### Fixed

- The onboard-generated "Adding a document" steps in `docs/AGENTS.md` name the numbered form and how to reserve a number (`docs_check.py next`, or by hand with a create-only `refs/sdlc/doc-ids/` ref), and say to add the index link outside the managed block (T-0642).

## [0.25.1] - 2026-10-19

Report: [docs/reports/2026-10-19-release-0-25-1.md](docs/reports/2026-10-19-release-0-25-1.md).

### Fixed

- `/sdlc-lite:onboard` outside a Git work tree asks one question (run `git init` here, use another folder, or stop) instead of ending with advice; it runs `git init` only on that choice and then continues with `--init` (T-0640).

## [0.25.0] - 2026-10-19

Report: [docs/reports/2026-10-19-release-0-25-0.md](docs/reports/2026-10-19-release-0-25-0.md).

### Added

- Opt-in work root: one `.sdlc/config` line, `work_root: docs/work`, moves tracked work records (tickets, closed tickets, `ROADMAP.md`, `NOTES.md`, evals, proposals, `fleet.json`) into `docs/work/`, while `.sdlc/` keeps config, `runtime/`, `messages/` and the generated router. With no line every path is unchanged (T-0618, T-0621 to T-0634, T-0637).
- `scripts/roots.py`, the one resolver for every root path, replacing five separate `.sdlc` walkers (T-0621).
- `tickets.py migrate-work-root --to docs/work [--rewrite-refs] [--dry-run]` moves a flat, nested or topics `.sdlc` into one `docs/work` shape; closed tickets move unchanged (T-0635). This repository now runs on it (T-0636).
- `work/` is a first-class docs home in the onboard layout (T-0634).
- Docs naming: each folder's index is the onboard-generated `## Contents` list in its `AGENTS.md`; a Kinds row can declare a numbered form for new files, with `docs_check.py next <folder>` reserving numbers through a git ref; UPPERCASE names only for ecosystem files and declared singletons; `## Levels`, `## Grandfathered` and `## Caps` sections in `docs/layout.md` (T-0620).
- `docs_check` D-13 (a document not listed in its folder's `AGENTS.md`) and D-14 (more than 12 documents directly in a folder), as warnings by default (T-0619).

### Fixed

- `steps.py lint` refuses a criterion that runs a git command the verifier may not run (`stash`, `checkout`, `reset`, `restore`, `commit`); `planner.md` names them (T-0617).
- `results.py` and `plan_check.py` selftests no longer depend on the live repository layout (T-0638).
- `lanes.py close` carries lane records into the main checkout under a work root (T-0639).

## [0.24.5] - 2026-10-18

Report: [docs/reports/2026-10-18-release-0-24-5.md](docs/reports/2026-10-18-release-0-24-5.md).

### Fixed

- The `traces` detector `wrong-resume-order` stays quiet when a completed planner run lies between a blocked step and a later build, and reports once per blocked step instead of once per step pair; on ui-kit-maison its live rows fell from 120 to 15 (T-0614).
- The `traces` detector `replan-loop` counts only completed planner attempts, so cancelled launches are no longer reported as replans (T-0615).

## [0.24.4] - 2026-10-17

Report: [docs/reports/2026-10-17-release-0-24-4.md](docs/reports/2026-10-17-release-0-24-4.md).

### Fixed

- `messages.py send` with an absolute `--root` writes the mailbox entry files exactly as a relative root does, so a peer's reply no longer rewrites the receiving repo's tracked `.sdlc/messages/*AGENTS.md` with absolute paths (T-0612).
- `steps.py lint` and `plan_check.py` no longer report "reads this step's own verifier result" for a verifier file at an absolute path in another repository (T-0613).
- `solo_run.py run --worktree` without `--cwd` records the session checkout's base (T-0587).
- The `gate_lock.py` selftest status checks run again; they compared a label to the real value and passed vacuously (T-0603).

### Changed

- `builder.md` no longer says a second `redck` record is only a base control, stale since T-0473 (T-0605).

## [0.24.3] - 2026-10-17

Report: [docs/reports/2026-10-17-release-0-24-3.md](docs/reports/2026-10-17-release-0-24-3.md).

### Changed

- `roadmap.md` lists only open tickets and ends with one `Closed: <n> done, <m> dropped` line, so it stays small and rarely conflicts on merge (T-0572).
- `close --reason` writes the `## Skipped` lines a lane needs instead of refusing (T-0581).

### Added

- `tickets.py close <slug> --preflight`: read-only, prints `ready` or one line per item close will demand. Closes take a lock (`.sdlc/runtime/close.lock`) and run one at a time (T-0581).
- The plan reviewer replays each criterion's check on current main; a `criterion-only` finding is applied as a logged amend at split and does not spend the replan. The design-replan cap is unchanged (T-0582).

### Maintenance

- This repo's closed ticket folders keep only `handoff.md` (and the newest verifier result where no `## Outcome` exists); 4638 run-record files left the tree, still at `51cbf1ba` (T-0571). The tests-gate pilot ended.

## [0.24.2] - 2026-10-15

Report: [docs/reports/2026-10-15-release-0-24-2.md](docs/reports/2026-10-15-release-0-24-2.md).

### Fixed

- `lanes.py open` makes no commit on a main that tracks an upstream, so PR repos keep local main fast-forwardable to origin; with no upstream it commits the record as before (T-0609).
- `lanes.py ready` warns and exits 0 when no conductor mailbox is registered and the ref is pinned (T-0610).

### Added

- `lanes.py ready` pins the lane's review state as `refs/sdlc/ready/<id>` (uncommitted work becomes a snapshot commit; stash and index untouched), unlocks the lane and messages the conductor; `list --ready` shows each pin and marks it stale once the lane moves. `dispatch.py prepare verifier` adds `Review sha:` and warns when the tree moved (T-0590).
- The multi-host rule for Claude Code, Codex and Pi in one repo lives in the plugin `AGENTS.md` Lanes section; `conductor.md` and the onboarding block link to it. Prepared verifier briefs now carry the run rules (uncommitted build, foreground only, no full check.sh, no git stash) (T-0591).
- A live two-host rehearsal (Claude Code and Codex) passed: one claim winner, both tickets done ([report](docs/reports/2026-10-15-two-host-rehearsal.md), T-0592).

## [0.24.1] - 2026-10-15

Report: [docs/reports/2026-10-15-release-0-24-1.md](docs/reports/2026-10-15-release-0-24-1.md).

### Fixed

- `onboard.py setup` only refreshes managed blocks a repo already has; creating a root block, `docs/` entry stubs or `docs/layout.md` needs `--init` (T-0608).
- The root `AGENTS.md` block states the repo's real lane root (`wtroot.py root`, so `<bare parent>/lanes/` in a bare clone), its ticket root, and says SDLC Lite is not set up when there is no `.sdlc/`; the mailbox line is advice (T-0607).
- Topic-layout repos: `tidy` uses the same allowed names as `check`, still honours `top_level_allow:`, and the router names `work/archive/` (T-0586).
- `dispatch.py prune` queues the agent's real spawn name, lists only this session's entries, and `--forget-stale` drops the rest (T-0601).
- `check.py` anchors the spec-gate order check on the `specgate.py check` command, not the header comment (T-0602).
- `close --ticket N` reserves the follow-up's id ref (T-0606).

### Added

- Claims and new ticket ids are reserved as git refs (`refs/sdlc/claims/<id>`, `refs/sdlc/ids/<id>`), so two hosts or worktrees cannot take the same ticket or id; `check` warns when front matter and refs disagree (T-0588).
- `lanes.py open` locks the lane with its owner; `list` shows it `running (<owner> <ticket>)`, sweeps keep it, and close unlocks it (T-0589).

## [0.24.0] - 2026-10-15

Report: [docs/reports/2026-10-15-release-0-24-0.md](docs/reports/2026-10-15-release-0-24-0.md).

### Changed

- Worktrees move out of the repo to the sibling `<main checkout parent>/<repo>.worktrees/` on Claude Code and Codex alike (`wtroot.py root`); `.claude/worktrees/` and `.worktrees/` are read as legacy for one release, and `scripts/migrate-worktrees.sh` (dry run, then `--apply`) moves them, judging landed against the default branch and rewriting each moved ticket's `worktree:` line (T-0563, T-0569, T-0575). `migrate-0.23.sh` now calls it.
- Root `AGENTS.md` and the onboarding block name the worktree root and say that under Codex every lane step needs full access, not `workspace-write` (T-0564, T-0570).
- `lanes.py open` commits the ticket's `branch:` and `worktree:` record in main and never sweeps in a path that was already dirty (T-0599), and installs the Codex agents in a new lane when the main checkout has them (T-0598).

### Added

- `lanes.py finish <lane>`: record, verdict, commit, land, settle, close, lane removal and an optional `--backup` push in one rerunnable command (T-0594, T-0595).
- `plugin_min: X.Y.Z` in `.sdlc/config`: `dispatch.py prepare`, `run.sh`, `solo_run.py run` and `lanes.py open` refuse an older running plugin or an older installed hook plugin, naming the update command (T-0593, T-0596).
- `wtroot.py evidence <ticket>`: a user-cache folder for screenshots and other binaries; `tickets.py check` warns on tracked binaries under `.sdlc/` (T-0568).
- `lanes.py orphans` lists snapshot refs and dangling commits that hold unique work; `claim --handover` pins the branch as `refs/archive/<date>/<branch>` first (T-0580).

### Fixed

- Lane merges through `fanout.py land` resolve and regenerate `.sdlc/AGENTS.md`, `roadmap.md`, `notes.md` and the mailbox routers instead of stopping, and stage tracked files under an ignored mailbox (T-0565, T-0597).
- `fanout.py land` and `lanes.py close` carry the lane's `.sdlc/runtime/tasks/<ticket>/` records into main without overwriting newer ones (T-0566).
- `dispatch.py prepare --tree` no longer takes a lane's base from a solo record made in another tree (T-0578).
- `tickets.py close --reason` refuses a "landed" or "on main" claim that names no commit on the default branch; appended verifier notes are exempt (T-0579).
- Topic-layout repos: the onboarding block names `.sdlc/notes/notes.md` and `.sdlc/work/archive/`, and `tidy` archives there (T-0576, T-0585).
- Codex docs name the records dir for request files (T-0600).
- Sweeps and stray reports skip Codex and Claude Code host-owned worktrees (T-0564).

## [0.23.1] - 2026-10-15

Report: [docs/reports/2026-10-15-release-0-23-1.md](docs/reports/2026-10-15-release-0-23-1.md).

### Fixed

- Bare-clone repos (lanes beside a bare git dir, as in gen-ui-kit): the worktree root is `<bare parent>/lanes`, or a `worktree_root:` line in `.sdlc/config`, for `wtroot.py`, `lanes.py`, `fanout.py`, the tmp reaper and both role hooks, so nothing nests inside a lane; `migrate-0.23.sh` prints the root and "nothing to move" there (T-0561).
- Role sub-agents can no longer run Bash in the background or use Monitor, so they cannot go idle waiting for a notification that never reaches them; the main session and the conductor are unaffected (T-0562).
- A fanout close writes the real `base:` and `Commits:` into `## Outcome` for solo lanes, from the solo dispatch's `base_sha` (T-0559).
- `tickets.py close` moves `skips.md` into the records dir, so a closed ticket tracks only `handoff.md` (T-0560).
- `dispatch.py selftest` uses a private `TMPDIR`, so another run's scratch under `$TMPDIR/sdlc-lite/` cannot fail it (T-0558).
- Release CI uses actions/checkout and setup-node v7 (Node 24) and pins `ubuntu-24.04`.

## [0.23.0] - 2026-10-14

Report: [docs/reports/2026-10-14-release-0-23-0.md](docs/reports/2026-10-14-release-0-23-0.md).

### Added

- Records dir: role results, step dirs, attempts, dispatch files, `runs.jsonl`, `base-sha`, `red-checkpoint.jsonl` and `budget-ack.md` go to `.sdlc/runtime/tasks/<folder>/`, local and ignored; `order.py records-dir <task dir>` prints it (T-0540).
- `tickets.py close` appends a `## Outcome` (lane, verdict, verifier, base, changed, commits, checks, deviations, follow-ups) and gates on the newest verifier verdict; `--changed "<line>"` fills the changed line (T-0543).
- `tickets.py tidy [--apply]` moves loose top-level `.sdlc/` entries into `archive/`; `check` warns on them; `top_level_allow:` and `citation_skip:` config lines (T-0544, T-0535).
- `tickets.py claim <id> --by <agent>` and `release <id>`, with claim lint (T-0526); a `successor:` field, for which `check` prints the ready `close --reason` line once the successor is done (T-0528).
- `branch:` and `worktree:` ticket fields, written by `lanes.py open` and `tickets.py branch`, removed by `lanes.py close`; `lanes.py list --all` shows the newest verdict of verified, unmerged work (T-0530, T-0550).
- `scripts/migrate-0.23.sh`: a per-repo dry run, then `--apply`, that moves `.worktrees/` lanes to `.claude/worktrees/` and runs `tickets.py tidy` (T-0550).
- Hard gates: a third planner run on a ticket, and a plan with more steps than its level allows (L1 and L2 3, L3 6, L4 10, L5 15), stop until `--approved "<who: why>"` (T-0553).
- Wall-clock budgets per role level and per ticket in `dispatch.py`: `status` and `recover` flag a role past its budget, and `prepare` refuses the next role on a ticket past its budget until `--approved` (T-0555).
- `/sdlc-lite:fleet-doctor`: why runs are slow or stuck, with ranked resolutions carried out only on a yes (T-0552).
- `dispatch.py resume --limit <name>` for a sub-agent stopped by a spend or session limit; `prepare` prints a line when a role's model or effort changed since the last attempt (T-0537).
- Builder amend route: `steps.py amend` changes one criterion of an unbuilt step after a builder-reported plan defect; lint catches a criterion that needs a later step (T-0536).
- `check.sh --fast`, a quick tier for builders and CI; the full suite runs its selftests in parallel (T-0557).
- Release-only CI: `.github/workflows/release-check.yml` runs the fast tier and the packaging check on `v*` tags and manual dispatch only (T-0554).
- Writing rules for the handoff and its Outcome: `skills/handoff-format/references/writing-rules.md` (T-0529, T-0545).

### Changed

- A closed ticket's committed record is its `handoff.md` with the Outcome. The filer runs only when asked (`/file`, `close --filer`); `## Closed` is no longer written. Fanout carries records between worktrees by copy, and its close commit keeps only `handoff.md` in the closed folder (T-0539, T-0541, T-0542, T-0543).
- Cost, board, fleet, traces and budget readers read the records dir, and still read legacy in-folder records (T-0541).
- Every worktree lives under `<main checkout>/.claude/worktrees/`, role scratch under `$TMPDIR/sdlc-lite/`, each with an `.owner.json`; `lanes.py sweep` removes a dead owner's folder (T-0550).
- Builders run their step's own checks and the narrow suites they touch, not the full `check.sh` when a land gate runs it (T-0551).
- Heavy checks a role runs inside its lane go through `gate_lock.py` (T-0556).
- Role guidance: run each check as a plain command, never a built string through `bash -c`, `sh -c` or `eval` (T-0549); the solo brief needs the `Tree:` line and leaves the verifier to the parent (T-0550).
- A role's result header is added at record time, and cleanup under the role's tmp prefix is allowed (T-0538).
- Run records: a retry is named `-2` like the host names it, a filer with follow-ups is pruned, and an empty solo result is a failed run (T-0531).
- `prices.json` recalibrated for the model rows changed in 0.22.7 (T-0521).
- Live host check of the new model rows: `effort:` in agent front matter applies to sub-agent spawns and is ignored for a session agent (`--agent`), so the conductor and messenger `effort:` lines have no effect there (T-0522).

### Fixed

- The build base is taken from the tree the role builds in, also for `solo_run --cwd` and resumed lanes (T-0546).
- A role's Bash call that reads stdin no longer hangs the run: a hook closes stdin for role calls (T-0548).
- `check.sh` stays green inside a role run with in-flight attempt records under `.sdlc/runtime/tasks/` (T-0547).
- `steps.py split` lints each step alone, so a path an earlier step creates (`[creates: ...]`) is no plan defect (T-0533).
- Step tooling for long suites, close references and router links, the launcher and its root guard (T-0532, T-0527).

### Removed

- Side files in task folders: `process-deviations.md` (deviations are audit rows and Outcome lines), `refusals.jsonl` (a `## Plan review` line), and per-ticket dated reports (T-0543, T-0545).
