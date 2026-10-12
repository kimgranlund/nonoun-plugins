#!/usr/bin/env python3
"""Run ticket lanes in parallel: one git worktree and one headless conductor per lane, each lane
merged into an integration branch under a lock, gated, and closed there. Main is never touched, except
by `roll`, which lands one rolling lane on main and moves main only by fast-forward.
An external lane merges a registered branch an outside agent owns, with no worktree and no driver.

Usage: fanout.py run <spec>... [--root .sdlc] [--base REF] [--integration BRANCH]
                     [--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run]
                     [--lane auto|solo|full] [--max-lanes N] [--yes-many] [--stagger SECS] [--allow-overlap] [--allow-empty-gate]
                     [--no-gate-lock]
       fanout.py prep <spec>... [the run flags but --driver and --dry-run]
       fanout.py land <branch> [--ticket T-NNNN] [--root .sdlc] [--base REF] [--integration BRANCH] [--lanes-dir DIR]
                      [--gate CMD]... [--rewrite-refs] [--lane auto|solo|full] [--allow-empty-gate] [--no-gate-lock]
       fanout.py roll <branch> [--ticket T-NNNN] [--root .sdlc] [--main BRANCH] [--lanes-dir DIR] [--gate CMD]...
                      [--rewrite-refs] [--lane auto|solo|full] [--allow-empty-gate] [--no-gate-lock]
       fanout.py settle <integration>
       fanout.py selftest
  where each <spec> is <lane>=<id>[,<id>...] or <lane>@<branch>=<id>[,<id>...]

Sub-agent lanes (T-0285): `run` starts one process per lane. On the Claude host the parent conductor can instead
dispatch each lane as a background sub-agent in an isolated worktree and keep only the deterministic work here:
`prep` is preflight, the overlap check and the lane choice, and prints what to spawn; `land` is the locked merge, the
gates, the vacuous-gate refusal, the close and the report for one finished branch. `run --driver` stays (the selftest
and the headless default, which on Claude needs SDLC_CLAUDE_EXEC=1, T-0288).

prep
  The preflight of `run` (the same refusals, the same messages, exit 2, nothing created: an unknown, done or twice-
  listed id, an uncommitted handoff, more lanes than --max-lanes, a planned-scope overlap unless --allow-overlap, a
  lanes dir inside the tree that is not gitignored) plus one more: `.claude/worktrees/` must be gitignored, because the
  host puts each sub-agent worktree there (add it to .gitignore and exclude it from watchers, as for `.worktrees/`).
  After the refusals it sweeps landed lanes as `run` does (lanes.sweep --apply, unless `lane_sweep: off`).
  Per ticket it prints the lane from `steps.py lane` (read only: prep writes no skips.md, runs.jsonl or branch), then
  for a solo ticket the dispatch JSON: `subagent_type` sdlc-lite:solo-<L1|L2|L3>, `name` <id>-solo, `model`, `effort`,
  `isolation` worktree, `run_in_background` (false when SDLC_HEADLESS=1), the `branch` the host will make
  (worktree-<id>-solo, known before the spawn) and its `worktree` (.claude/worktrees/<id>-solo), and a `prompt` brief
  that asks the solo to commit `<id>: <title>` on its branch (SOLO_SUBAGENT_PROMPT; the headless SOLO_PROMPT says
  never commit). For solo level L2 and L3 it also prints the verifier command, prepared against the sub-agent worktree after the
  solo reports (`dispatch.py prepare verifier L2`, or L3 for the tickets steps.py verifier-level names; SOLO_VERIFIER, T-0356); its result is committed on the
  branch. Every ticket gets its `land` command, pinning the integration branch, the base sha, the lanes dir and the
  gates. Per solo ticket prep also writes the host lane record through lanes.host_record (<lanes root>/host/<id>-solo.lane.json,
  kind host, into the integration branch, base the start sha) and prints `    host record: <path>`.
  A ticket at its budget gate prints `blocked: budget gate: budget.py ack` instead of a dispatch and prep exits 4.
  A `full` ticket gets no dispatch: the parent conductor drives the chain, each role a sub-agent against the lane tree
  (`<lanes-dir>/<lane>` on branch <integration>-<lane>, made with the printed `tree: python3 <scripts>/lanes.py open
  <lane> --kind fanout --ticket <id>... --base <start> --into <integration> --path <tree> --branch <integration>-<lane>
  --no-claim` line, which writes the lane's .lane.json, each brief carrying a
  `Tree: <path>` line), commits `<id>: <title>` there, and lands that branch. Lane tickets run one after another: the
  next is spawned after the previous one landed. The first land creates the integration branch and worktree (under
  --lanes-dir) and each later land reuses them.

land
  `land <branch>` takes the ticket from `--ticket` or from a worktree-<id>-solo branch name, resolves it from git
  objects on the branch (so the branch needs no `external_branch:` registration), and refuses (exit 2, nothing
  created) a branch that is not a local branch, the integration branch, a ticket that is done or absent on the branch,
  or an integration worktree path that is something else. It then follows the external-lane path of `run` unchanged:
  the overlap wait, the integration-dirty refusal, `git merge --no-ff` as `Merge <branch>: <id>` (a conflict is
  aborted as `merge conflict`: the parent asks the sub-agent, by name, to merge the integration branch on its side,
  then lands again), each --gate through gate_lock.py (a vacuous gate is `gate vacuous`, a red one resets the merge:
  `red: <gate> rc=<n>`), `tickets.py close` (a solo lane closes with --reason after `steps.record_lane` writes the lane
  record and the skipped planner and filer into skips.md) and the `close <id>` commit. Two outcomes come first and merge
  nothing: `no changes` when the branch holds no commit the integration branch lacks (a stub that never committed),
  and, after committing any record left in the sub-agent worktree's ticket folder onto the branch (T-0439), for a solo level L2 or L3, `no verifier result` or `verifier <verdict>` read from the verifier results committed on
  the branch that the integration branch does not hold (git objects, newest by order.py). Exit 0 only for `merged`.
  Each land appends one line to <lanes-dir>/logs/land.jsonl and rewrites report.md from it: every ticket landed so far
  (the latest outcome each), with the `- Lane for <id>` line and the level model line, as for `run`.
  Lanes (T-0452), after the merge lock is released: a `merged` branch checked out under .claude/worktrees/<leaf> whose
  leaf is not <id>-solo (the host names it agent-<agent_id>) gets its host record rebound, host_record(<leaf>) written
  and the provisional <id>-solo record removed; that host lane stays open (dispatch.py prune --done closes it). A
  branch whose tree holds a .lane.json of kind fanout is closed with lanes.close_lane(<tree>, into=<integration>) when
  this ticket is the record's last: it prints the close message (the archive ref is written first), or
  `lane still open: <path> (<outcome>)` when the land did not merge or the close refuses.

roll (T-0374)
  Every lane has a merge class (steps.merge_class, defined in docs/references/sdlc-internals.md under
  scripts/fanout.py): `rolling` when its newest verifier verdict is pass (every level), its recorded base
  is an ancestor of main, and it touches no path a `hash_bound: <glob>` line in <root>/config declares;
  else `integration (<reason>)`. `roll <branch>` resolves the ticket as land does, then under the merge
  lock: `no changes`, the class from git objects on the branch (a lane that is not rolling is that
  outcome and nothing merges), then merge_gate_close in the scratch worktree <lanes-dir>/rolling,
  detached at main's tip, and only after `merged` main fast-forwards to it (`merge --ff-only` where main
  is checked out, else update-ref); a refused fast-forward is `main not advanced: <reason>`. At the end of every
  roll, whatever the outcome, the scratch tree is removed (`git worktree remove --force <lanes-dir>/rolling`, then
  `git worktree prune`; it is detached and holds no branch), and the next roll makes it again.

settle (T-0438, T-0452)
  `settle <integration>` fast-forwards the current branch to the integration branch (nothing to do when it is already
  merged, as after a hand merge; a diverged branch exits 2 and is left whole), then closes the integration branch's
  worktree with lanes.close_lane(<worktree path>, into=<current branch>): the archive ref
  refs/archive/<UTC date>/<integration> is written before the tree is removed (`--force`, so an untracked copied
  .sdlc/config does not stop it) and the branch deleted, and the close message prints. A close that refuses (not a
  plugin lane, lanes still open into the branch, no worktree) prints `lane still open: <path or branch> (<outcome>)`,
  keeps the branch and exits 1.

Solo first (the default driver). For each ticket, after the lane syncs, `steps.py lane <task dir>` decides
  the lane and appends its record to the task's skips.md (committed with the lane): `solo` (ticket level L1 and
  L2 by default) starts the solo agent (agents/solo.md) from a typed brief at the level's model and effort (Claude:
  `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo` at L1 Sonnet low, L2 Sonnet high; Codex: `codex_exec.py solo
  L1|L2|L3`, honoring SDLC_BACKEND), both started through `solo_run.py` so each lane's solo session cost lands in
  the ticket's runs.jsonl and the budget and board meter it (T-0226); anything else (`full`, or `lean` after a plan) keeps the headless conductor
  running /sdlc-lite:chain. A solo ticket of level L2 or L3 then needs one independent batched verifier: a new
  task-dir verifier result with Verdict pass, from the solo itself or else one fanout runs once
  (`run.sh verifier L2 <task dir>/handoff.md`, or L3 where steps.py verifier-level says so); a missing or non-pass verdict is
  the outcome `verifier fail` or `no verifier result`, with no merge. --lane solo or full forces the choice for
  every ticket (no lane call, no record); --driver CMD overrides everything and skips the lane call. The run
  report lists each ticket's lane. Safety: --max-lanes N (default 4) is the most regular lanes one run may
  hold, and above 16 it also needs --yes-many (a run over the cap refuses with exit 2); --stagger SECS (default
  20, 0 for none) waits between lane starts so a plan limit is not hit by 16 sessions at once; two tickets in
  different lanes whose planned scope overlaps refuse in preflight unless --allow-overlap (the merge-time wait
  below still serializes real overlap). --dry-run prints the cap, the stagger, and each ticket's lane.

run
  Lane specs: <lane>=<id>[,<id>...] is a regular lane (a worktree and a driver per ticket).
  <lane>@<branch>=<id>[,<id>...] is an external lane: <branch> is a local branch an outside agent
  (Codex, say) owns and commits to, registered by an `external_branch: <branch>` line in
  <root>/config (the line tickets.py reads to mint ids above the ones committed there, so a
  branch never joins a run while its ids are unguarded). A spec is split at its last `=` for the
  ids, then at the first `@` for the branch; an empty branch (`alpha@=T-0001`) or no `=`
  (`alpha@x`) refuses with the usage text.
  Preflight (every refusal prints on stderr, exits 2, and creates nothing): the cwd is in a git
  work tree with a commit; --root (default .sdlc, relative to the cwd) lies inside the toplevel,
  and its path relative to the toplevel (rel) is the ticket root in every worktree (handoff, step,
  and filer paths in each worktree use tickets.ticket_dir(root): <root>/tickets under
  `ticket_root: tickets`, else <root>); lane names
  match ^[a-z0-9]+(-[a-z0-9]+)*$ (not `integration`, `logs` or `rolling`, which name the lanes dir's
  own entries); each id is T-NNNN, resolves through tickets.load(tickets.ticket_dir(root)) to exactly one folder whose
  status is not done or dropped, has its handoff committed at the start commit, and appears once
  across all lanes. An external lane's branch must be registered in <root>/config (else the
  refusal names the `external_branch: <branch>` line and that file), refs/heads/<branch> must
  resolve to a commit, the branch must not be the integration branch or any <integration>-<lane>
  of this run, and no two lanes may name one branch; its ids resolve through
  tickets.branch_tickets(root, <branch>) (read from git objects, so a ticket may exist only on
  that branch; a missing one refuses with `<id>: no ticket on branch <branch> has this id`) with
  the same one-folder, not-done-or-dropped and once-across-all-lanes checks. The lane-branch and
  lane-dir checks, the branch-name format check, and the handoff-at-start check below are for
  regular lanes only (an external ticket's handoff was read from its branch).
  The integration branch is --integration or fanout/<YYYY-MM-DD>; lane branches
  are <integration>-<lane> (a slash form would collide with the integration ref). --lanes-dir
  (relative to the cwd) defaults to <toplevel>/.worktrees/fanout. The lanes dir is never the
  toplevel itself; inside the toplevel it must be gitignored: for the default,
  `git check-ignore -q .worktrees/x` run from the toplevel must pass (else it refuses, naming
  `.worktrees/` to add to .gitignore); for an explicit --lanes-dir inside the toplevel, the same
  check runs on <its path relative to the toplevel>/x and a refusal names that path. An explicit
  --lanes-dir outside the toplevel needs no ignore check. It refuses when a lane branch,
  <lanes-dir>/<lane> or <lanes-dir>/integration exists, or when the integration branch is
  checked out in some worktree.
  --dry-run prints the plan (base sha, integration branch, per lane its branch, worktree and
  tickets, the gates, the driver, the close command) and exits 0, creating nothing; an external
  lane prints `lane <name>: external branch <branch> (registered; no worktree, no driver)`.
  After the lanes it prints the planned-scope overlap: the allow-list paths of each ticket's
  step-<n>/handoff.md scope criteria (the grep -vxF/-vxE/-vE forms `steps.py widen` reads), one
  `overlap (planned scope): <laneA> <idA> and <laneB> <idB>: <paths>` line per intersecting pair
  of tickets in different lanes, else `overlap (planned scope): none`, and one
  `overlap (planned scope): not planned, checked at merge time: <ids>` line for tickets with no
  such scope (unplanned, or in an external lane).
  Setup, sequential: create the integration branch at --base (default HEAD) unless it exists
  (then reuse it; --base is ignored); touch <lanes-dir>/merge.lock; `git worktree add
  <lanes-dir>/integration <integration>`; per regular lane lanes.open_lane (kind fanout, the
  lane's ticket ids with the claim check off, base and into <integration>, path <lanes-dir>/<lane>,
  branch <lane branch>), which writes the lane's .lane.json and picks its port (an
  external lane gets no worktree and no branch); make <lanes-dir>/logs/. A ticket handoff missing
  in a regular lane worktree removes what this run created and exits 2 (the .sdlc/ trail must be
  committed).
  Then one thread per lane. A lane walks its tickets in order and stops at its first outcome
  other than `merged`; every later ticket is `skipped`. Per ticket of a regular lane:
    1. sync, under the lock: `git merge --ff --no-edit <integration>` in the lane worktree;
       a conflict is aborted (`sync conflict`). Under the lock so a lane never picks up a merge
       whose gates are still running.
    2. driver, outside the lock: `bash -c <driver>`, cwd the lane worktree, stdin /dev/null,
       output to <lanes-dir>/logs/<lane>-<id>.log, env FANOUT_LANE, FANOUT_TICKET, FANOUT_SLUG,
       FANOUT_HANDOFF (absolute, in the ticket folder), FANOUT_ROOT (absolute lane root), FANOUT_INTEGRATION,
       FANOUT_PLUGIN_ROOT, SDLC_HEADLESS=1 (hooks/block-background.sh denies Bash and Agent run_in_background),
       SDLC_ROLE=conductor (hooks/block-publish.sh blocks git push, gh writes, and package publishing
       in the Claude sessions the driver launches),
       and BASH_DEFAULT_TIMEOUT_MS=BASH_MAX_TIMEOUT_MS=3600000 as bench.sh sets them. Default: a headless conductor (on Claude needs SDLC_CLAUDE_EXEC=1; claude -p --agent sdlc-lite:conductor, Opus
       medium) told to run /sdlc-lite:chain on the handoff unattended, run the filer but not
       close the ticket, and never commit, push, or publish. --driver replaces it (stubs,
       tests). After the driver returns, whatever its rc and before step 3 or any lane commit,
       `bash reap-tmp-worktrees.sh <lane worktree>` runs (exit code ignored): it removes each
       <lane>/.worktrees/tmp/<role>-<pid> prefix whose owner pid is dead, which the lane's last
       role run leaves when SIGKILLed, since no later run.sh in the lane would reap it. Non-zero exit: the lane's step dirs are checked for an inherited-red step as in
       step 3, giving `inherited red: step-<n>: <tests> (driver rc=<n>)`; with none, the outcome
       stays `driver failed rc=<n>`. On step 2 (driver non-zero exit) and on any outcome
       other than `merged`, a dirty lane tree is committed as `wip(<id>): <outcome>` on the
       lane branch only. It is never merged, and the report's Commit cell shows `wip <sha>`.
       A lane tree already dirty before a ticket's sync is committed as
       `wip(<id>): dirty before sync` on the lane branch, and that ticket stops with the outcome
       `dirty before sync`: no sync, driver, lane commit, or merge.
    3. inherited red: each <rel>/<slug>/step-<n>/ dir in the lane worktree (numeric order; a
       step-<n>.superseded-<k> dir never counts) goes through steps.next_action; at the first
       whose action is `inherited` (a builder Status or newer verifier Verdict
       `inherited red: <tests>`, a gate already red at the pre-build HEAD) the outcome is
       `inherited red: step-<n>: <tests>`, the tests read from the verifier's Verdict line when
       the verifier reported the inherited red, else from the builder result's Status line. No lane commit, merge, or close; as for any stop,
       the lane tree is WIP-committed on the lane branch and kept there for inspection.
    4. commit in the lane: `git add -A` minus run artifacts (*.log, .run.lock, *.running; LANE_ADD), `git commit -m "<id>: <title>"`; nothing staged:
       `no changes` (no merge, no close).
    5. first, outside the lock, the overlap wait: lanes rank by their position in the spec list,
       and the ticket's paths (`git diff --name-only <integration>...<ref>`, ref the lane branch,
       or refs/heads/<branch> for an external lane) are compared with the pending paths of each
       earlier lane that has not finished: a regular lane's working tree against its merge base
       with the integration branch plus its untracked files, an external lane's
       `<integration>...refs/heads/<branch>` (every such read passes --no-optional-locks, so it
       never takes that lane's index.lock; a failed read counts as no paths). While any overlap
       remains the ticket waits, rechecking on each ticket outcome, each lane finishing, or every
       2 s, and prints `waiting for lane <other> (overlap: <paths, sorted>)` each time the lane or
       path set changes. A lane waits only for an earlier lane, so no wait cycle can form, and an
       overlapping lane merges after the lane it overlaps. Limit: an overlap first visible after
       the later lane has started its merge is not reordered. Then
       under an exclusive fcntl.flock on <lanes-dir>/merge.lock, in the integration worktree:
       uncommitted tracked changes there refuse the ticket first (`integration dirty: <first path>`;
       no merge, reset, or gate runs, so the edit survives); else the paths of
       `git diff --name-only HEAD...<ref>` join the lane's merged paths (the report's Overlap
       lines), then
       `git merge --no-ff --no-edit -m "Merge <lane branch>: <id>" <lane branch>` (a conflict
       is aborted: `merge conflict`); each --gate in order via bash -c, run through
       `gate_lock.py run --name <lane>/<id> --` (T-0303, T-0409: the machine-wide weighted
       FIFO admission, built-in capacity 6 compute units and 3 browser jobs, two undeclared gates at once;
       `SDLC_GATE_SLOTS=0` or --no-gate-lock runs the gate
       bare; a wait past the lock's timeout is gate rc 3 with the `gate_lock: timeout` line in the
       log), output to
       logs/gate-<lane>-<id>-<k>-a<n>.log (<k> numbers the gates, a<n> the attempts: n is 1 plus
       the highest attempt already logged for that gate, so it grows on each rerun); the first red one runs `git reset --hard <pre-merge HEAD>`
       (`red: <gate> rc=<n>`). All green: copy the lane's <rel>/<slug>/ in when the integration
       copy has no filer-L*.md, run `tickets.py --root <rel> close <slug>` there (with
       --rewrite-refs when given: in numbered mode, files outside the ticket folder that cite
       <rel>/NNNN-<slug> are rewritten to <rel>/.NNNN-<slug>), and commit `close <id>`
       (`merged`), staging <rel> plus every path outside it that the close changed (a
       `git status --porcelain` snapshot before and after; never the whole worktree); a close
       refusal gives `merged, close refused: <first line>` (without --rewrite-refs, a refusal
       naming that flag adds `; fanout.py run --rewrite-refs rewrites them`) and the merge stands.
  Per ticket of an external lane: no pre-sync wip, no sync, no driver (so no driver log), and no
  lane commit; straight to step 5, sharing its code: the overlap wait, then under the lock the
  integration-dirty refusal and the merged-paths record, then
  `git merge --no-ff --no-edit -m "Merge <branch>: <id>" refs/heads/<branch>` (a
  conflict is aborted: `merge conflict`, and the outside agent merges the integration branch on
  their side before a rerun). When HEAD is unchanged after the merge (the branch was already
  merged, as for the second ticket on one branch or a resume) the gates are skipped; else they run
  as above, the first red one resetting to the pre-merge commit. There is no lane dir, so nothing
  is copied in: the ticket folder came in with the merge. Then the same close and `close <id>`
  commit. The outside branch is never written (no sync merge onto it, no ref update, no wip
  commit), and a stopped external lane leaves nothing to inspect but the report.
  Run id: each non-dry run mints ctx run_id `fanout-<12 hex>` (uuid4), never read from
  SDLC_ATTEMPT_ID: run_lifecycle.py sets that only for a run.sh role process, a fanout run is not a
  role attempt (the roles its driver launches record their own attempt_id), and a fanout run inside
  a role would inherit the role's id, so two runs, or a run and its resume, would share it.
  Prints `[<run_id>] [<lane>] <id> <event>` lines as they happen and appends each, under the
  print lock, to <lanes-dir>/logs/fanout.log (append-only: earlier runs' lines survive a resume).
  Driver logs are overwritten; gate logs are never overwritten, one file per attempt. Each output line is written as
  `[<run_id>] <line>` (a last line without a newline too); driver and gate env carry
  FANOUT_RUN_ID=<run_id>. Writes <lanes-dir>/report.md
  (| Lane | Ticket | Outcome | Commit |, a `- Run: <run_id>` line, the integration branch and its tip, the worktree paths,
  an external lane's `- Lane <name>: external branch <branch> at <sha>` line (each value in
  backticks, the full sha of the branch tip), the gates or that none were given, the `- Logs:`
  line, then one ``- Overlap: `<a>` and `<b>`: `<f1>`, `<f2>` `` line per lane pair a before b in
  spec order whose merged paths (step 5) intersect, the shared paths sorted, or the single line
  `- Overlap: none`) and prints it.
  An external lane's Commit cell is the merge commit when the merge made one, the integration HEAD (the previous `close` commit) when it merged nothing new, else the branch tip's sha7.
  Exit 0 only when every ticket is `merged`, else 1; 2 for a refusal. checkout, switch, reset and
  commit run only inside the lanes dir; nothing is pushed.
  Lane lifecycle (T-0452, through lanes.py; docs/specs/sdlc-lite/lane-lifecycle.md). Sweep at start: after preflight
  and the overlap refusal, before setup, `lanes.sweep(apply=True)` from the toplevel closes every landed plugin lane
  and prints each result line as `lanes sweep: <line>`; `lane_sweep: off` in .sdlc/config skips it, and a sweep error
  prints and never blocks the run (a refusal, exit 2, still creates and removes nothing). Open: each regular lane is
  opened through lanes.open_lane as in setup above; the integration tree is a plain worktree beside merge.lock and
  logs/, which lanes.py reads as a fanout integration lane. Port: when `lane_ports:` gives the lane a port, the driver
  and each gate of that lane's tickets get SDLC_LANE_PORT=<port>; otherwise an inherited SDLC_LANE_PORT is removed.
  Close: after every lane thread has joined (never inside a lane thread), a lane whose every ticket is `merged` is
  closed with lanes.close_lane, which writes refs/archive/<UTC date>/<lane branch> before it removes the tree and the
  branch; report.md gets `- <close message first line>` (as `- closed alpha (ancestor)`). A stopped lane, or a close
  that refuses, stays (tree and WIP commit kept) with `- lane still open: <path> (<outcome>)`, the lane's first
  non-`merged` outcome or the close outcome. The integration tree stays: `- lane still open: <integ dir>
  (integration: stays until main contains <integration>)`. These lines follow the Overlap lines and print with the
  report. lanes.open_lane takes its flock at <lanes root>/lanes.lock (default <toplevel>/.worktrees), so that dir
  must be gitignored even with an outside --lanes-dir.

selftest
  A throwaway repo in a temp dir, a stub driver, two lanes: proves three merges, a red gate's
  merge reset, main untouched, closes on the integration branch, the pre-ticket sync, a lane
  stopping at its first failure, board.py --lanes listing both lanes, and that --dry-run and
  the refusals create nothing. A numbered-mode repo with docs/spec.md citing the ticket folder
  proves that without --rewrite-refs the close is refused (naming the flag) and the ticket stays
  open, that with it the ticket closes to .0001-x and the `close <id>` commit carries the
  rewritten docs/spec.md, the integration worktree stays clean either way, and the dry-run
  close: line matches each mode. An inherited-red repo (case 5) proves that a step-1 builder
  Status `inherited red: test_a` gives the outcome `inherited red: step-1: test_a`, no merge on
  the integration branch, the ticket still ready, the next ticket skipped, and the step file
  kept in the lane's `wip(T-0001): inherited red: ...` commit, not merged; its negative control,
  a builder Status `done`, gives `merged`. A variant with builder Status `done` and a newer
  verifier Verdict `inherited red: test_v` proves the outcome names the verifier's tests,
  `inherited red: step-1: test_v`, not `done`.
  A full stub-driver run in the default lanes dir under .worktrees/fanout (case 6) proves lane
  commits `<id>: <title>`, merges and closes, with `git status` in the main tree left clean.
  A one-lane case (case 7) with a driver that writes a file and exits 3
  proves the stopped lane is WIP-committed: a clean lane tree, a `wip(T-0001): driver failed
  rc=3` tip holding the file, not merged into the integration branch, integration and main at
  the fixture commit, and a `wip <sha7>` Commit cell in the report.
  A dirty-sync case (case 8), one lane `alpha=T-0001,T-0002` with the stub driver and a gate that
  writes dirty.txt into the lane tree, proves that T-0001 merges, T-0002 stops with the outcome
  `dirty before sync` and a `wip <sha7>` Commit cell, the lane tip is
  `wip(T-0002): dirty before sync` and not an ancestor of the integration branch, the integration
  branch holds T-0001.txt but not dirty.txt, T-0002 stays ready there, and main is untouched; its
  negative control, the same run with no gate, merges both tickets with no `wip(` lane tip.
  A resume case (case 9), one lane `alpha=T-0001` with a driver that exits 3 on the first run,
  then its worktrees and lane branch removed and a rerun on the reused integration branch where
  the driver succeeds, proves logs/fanout.log keeps the first run's `driver failed rc=3` line and
  holds the second run's `merged` line under two distinct `fanout-<12 hex>` ids, that every line
  of the second run's lane and gate logs starts with its id, that the driver saw FANOUT_RUN_ID,
  and that report.md names the id.
  A gate retry case (case 10), one lane `alpha=T-0001` with a gate red until a marker exists, a red
  first run, then worktrees and lane branch removed and a green rerun, proves the first attempt's
  output survives in gate-alpha-T-0001-1-a1.log and the second lands in gate-alpha-T-0001-1-a2.log.
  An external lane case (case 12), a repo whose .sdlc/config registers `external_branch: ext`
  (committed on main) and a branch `ext` made by `checkout -b` holding .sdlc/b (T-0002) and
  .sdlc/c (T-0003), each with a handoff and a filer-L1.md, plus a file: a mixed run
  `alpha@ext=T-0002,T-0003 beta=T-0001` with the stub driver and `--gate true` exits 0, merges
  both lanes (two merge commits on the integration branch), closes a, b and c there, leaves the
  ext tip and main unchanged, creates no <integration>-alpha ref and no <lanes-dir>/alpha dir,
  writes no alpha-T-0002.log driver log, one gate-alpha-T-0002-1-a1.log and no gate log for
  T-0003, and report.md holds the external lane line and every row; `--dry-run` prints the plan
  line and creates nothing. Negative control: the same lane with the config line absent exits 2
  naming `external_branch: ext` and .sdlc/config, with no fanout/* branch and no lanes dir.
  Refusals, each exit 2 creating nothing: `alpha@=T-0002`, `alpha@ext`, a registered name with
  no local ref, one branch in two lanes, an id absent on the branch, and the branch as the
  integration branch. A `--gate false` run reports `red: false rc=1` and leaves the integration
  branch at its base and ext unchanged.
  An overlap case (case 13), a repo with a root shared.txt (`top`, 20 `mid <n>` lines, `bottom`)
  and a stub driver per ticket: alpha (T-0001) rewrites line 1 to `top alpha` and holds until
  fanout.log shows `[beta] T-0002 waiting for lane alpha (overlap: shared.txt)`; beta (T-0002)
  holds until alpha's shared.txt starts with `top alpha`, then rewrites the last line to
  `bottom beta`. The run `alpha=T-0001 beta=T-0002` exits 0 with both merged, alpha's merge
  before beta's on the integration branch, the waiting line in fanout.log, the report line
  ``- Overlap: `alpha` and `beta`: `shared.txt` ``, and both edits in the merged shared.txt.
  Without the wait alpha's driver times out and the case is red. Negative control: the same
  shape with the stub driver (disjoint lanes) merges both, reports `- Overlap: none`, and logs
  no `waiting for lane` line.
  A planned-scope case (case 14): tickets a T-0001 (step-1 scope `grep -vxF -e shared.txt -e a.txt`),
  b T-0002 (`grep -vxE "shared\\.txt|b\\.txt"`), c T-0003 (no step dir) and d T-0004
  (`grep -vxF -e b.txt`). `--dry-run alpha=T-0001 beta=T-0002,T-0003` prints the alpha/beta
  shared.txt pair line and the not-planned line for T-0003; negative control
  `--dry-run alpha=T-0001 beta=T-0004` prints `overlap (planned scope): none` and no pair line.
  Neither creates a branch, worktree or lanes dir.
  A gate lock case (case 21, T-0303): every selftest run gets a private TMPDIR and SDLC_GATE_DIR (so a
  private state root) and no other SDLC_GATE_* variables, so all cases run their gates through gate_lock.py. The probe gate
  prints SDLC_GATE_WORKERS and SDLC_GATE_LOCK_HELD and the output of `gate_lock.py context --json`. The gate log of a
  default run shows 3 workers, the marker set and `alpha/T-0001` as the grant's name; SDLC_GATE_SLOTS=3 gives 2
  workers (6 // 3); the same run with --no-gate-lock, and with SDLC_GATE_SLOTS=0, shows neither and no holder.
  A prep case (case 22, T-0285): three tickets (sizes L1, L2, and the alias of L1) in two lanes print one lane line each, the T-0001 dispatch JSON
  (name T-0001-solo, sdlc-lite:solo-L1, sonnet, isolation worktree, branch worktree-T-0001-solo, the brief carrying
  `T-0001: Ticket t1` and no "Never commit"), a level L2 verifier command against the worktree and none for level L1, a land
  command per ticket with the base sha and the gate, and create no branch, worktree, lanes dir or file; SDLC_HEADLESS=1
  gives run_in_background false; `--lane full` prints the tree and sync commands, a `Tree:` line and no JSON; a ticket at
  80 percent of its budget prints `budget gate: budget.py ack`, no dispatch, and exits 4 while the other ticket still
  dispatches. Parity: for a planned-scope overlap, an uncommitted handoff, `--max-lanes 1` with two lanes, one id in two
  lanes and an unknown id, `run` and `prep` both exit 2 with the same stderr and create nothing; `--allow-overlap`
  lets prep print the plan; `.claude/worktrees/` not gitignored exits 2 naming it. A land case (case 23, T-0285):
  branches worktree-T-0001-solo and worktree-T-0003-solo, each with one commit, land through a green gate to `merged`
  on a reused integration worktree (two merge commits, `close <id>` commits, status done, a solo lane in skips.md,
  main untouched and clean, the report listing both tickets with `Lane for` and the level line); a red gate resets the
  merge (`red: false rc=1`, tip unchanged, ticket still ready); `Ran 0 tests` is `gate vacuous` and --allow-empty-gate
  merges it; a branch with no commits is `no changes`; a size L2 ticket with no verifier result, then a failing one, is
  refused and with a passing one merges; a missing branch, a branch naming no ticket and the integration branch refuse
  with exit 2. Case 24 (T-0285): a `--driver true` stub that commits nothing gives `no changes`.
  A lane lifecycle case (case 29, T-0452): a fixture whose .sdlc/config has `lane_ports: 47400-47499` and
  `lane_min_age_hours: 0`, holding a plugin lane T-0003-pre made with `lanes.py open` and merged into main, runs
  `alpha=T-0001 beta=T-0002` with a driver that writes $SDLC_LANE_PORT to a file and exits 3 for T-0002, and a gate
  that logs it. It proves alpha's tree and branch are gone with a refs/archive/<UTC date>/<integration>-alpha ref at
  its tip and `- closed alpha (ancestor)` in the report; beta's tree and branch remain with `lane still open: <beta
  path> (driver failed rc=3)`; the driver and gate saw the lane record's port, inside the range; the run start closed
  the pre lane, logged as `lanes sweep: closed`. Control: the same fixture with `lane_sweep: off` leaves the pre lane
  open and prints no `lanes sweep:` line. Cases that read a merged lane's tree or branch after a run (1, 6, 8, 12,
  15) read it on the integration branch or at its archive ref, since the run closed the lane.
  Case 28 (settle archive): integration trees at <lanes dir>/<n>/integration beside merge.lock and logs/, as fanout
  makes them; after settle the trees and branches are gone and refs/archive/<UTC date>/fanout/ff and .../fanout/hand
  exist; a diverged branch exits 2 and is kept; a tree outside a lanes dir is kept with `lane still open` and exit 1.
  Case 30 (host record): prep writes <lanes root>/host/T-0001-solo.lane.json (kind host, ticket T-0001); a land from
  a worktree under .claude/worktrees/agent-x rebinds it to agent-x.lane.json. Case 31 (roll scratch): after a merged
  roll and after a refused one, <lanes-dir>/rolling is absent and `git worktree list` names no rolling tree. Case 32
  (full lane close): a tree made with prep's printed `lanes.py open` line for two tickets stays after the first land
  and, after the land of its last ticket, is gone with an archive ref and its branch deleted.
"""
import argparse, contextlib, datetime, fcntl, json, os, pathlib, re, shlex, shutil, subprocess, sys, tempfile, threading, time, uuid

import tickets  # same scripts/ dir: the only front matter parser
import steps  # same scripts/ dir: next_action and section read step results
import order  # same scripts/ dir: newest result file of a role
import lanes  # same scripts/ dir: the lane lifecycle (open, close, sweep)

SCRIPTS = pathlib.Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
LANE_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
RESERVED = ('integration', 'logs', 'rolling')  # the lanes dir's own entries
ENV = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
# No auto gc or maintenance while lanes write refs and objects concurrently.
GIT_CFG = ('-c', 'gc.auto=0', '-c', 'maintenance.auto=false')
TIMEOUT_MS = '3600000'
PROMPT = ('Run /sdlc-lite:chain {handoff} unattended. No person is present: never ask the user and '
          'never use AskUserQuestion; where a step would ask, take its recommended option and go on. '
          'In the file stage run the filer only and do not close the ticket (no tickets.py close), '
          'because /fanout closes it on the integration branch after the merge. '
          'Never commit, push, or publish: fanout.py commits this lane when you finish.')


# Solo levels (agents/solo.md): ticket level -> (Claude model, Claude effort, Codex level). The Codex agents are
# sdlc-solo-l1..l3 from adapters/codex/models.json. check.py guards that solo.md and these agree.
SOLO_TIERS = {'L1': ('sonnet', 'low', 'L1'), 'L2': ('sonnet', 'high', 'L2'), 'L3': ('opus', 'xhigh', 'L3')}
SOLO_VERIFIED = ('L2', 'L3')  # the solo levels that need one independent batched verifier before the merge
SOLO_VERIFIER = 'L2'  # the default level of a solo ticket's batched verifier (T-0356); solo_verifier raises it to L3


def solo_verifier(handoff):
    """The level of a solo ticket's one batched verifier, read from its handoff.md (steps.ticket_verifier): L2 by
    default, L3 only for a ticket of size L4 or L5, a merge or security ticket, or one whose criteria pin an exact
    label or string. Off the Claude host it stays L3: the replay behind T-0356 measured the Claude levels only.
    The independence rule is the dispatch family rule (a Sonnet solo gets an Opus L2 verifier), not the level."""
    if os.environ.get('SDLC_BACKEND', 'claude') != 'claude':
        return 'L3'
    try:
        return steps.ticket_verifier(pathlib.Path(handoff).read_text(encoding='utf-8'))[0]
    except OSError:
        return SOLO_VERIFIER
MAX_LANES_DEFAULT, MAX_LANES_HARD, STAGGER_DEFAULT = 4, 16, 20
# A test gate that ran nothing: unittest "Ran 0 tests", pytest "no tests ran" or exit code 5 (nothing collected).
VACUOUS_GATE = re.compile(r'\bRan 0 tests\b|\bno tests ran\b|\bcollected 0 items\b', re.M)
SOLO_PROMPT = ('Brief: deliver ticket {handoff} end to end in this session as the solo agent. Read the ticket and the '
               'files it names, make the smallest change that meets its done criterion, run every check command it '
               'names and after a fix rerun the checks that fix can affect (every check when unsure), keeping any `(red)` control, and report files changed, each check with its outcome, and '
               'anything still open. For a ticket of level L2 or L3 write the handoff\'s ## Acceptance criteria if it has '
               'none, then run the one batched independent verifier agents/solo.md names. No person is present: '
               'never ask the user and never use AskUserQuestion. Never commit, push, open a PR, or publish: '
               'fanout.py commits this lane when you finish and closes the ticket after the merge.')

# Sub-agent lanes (T-0285): the parent conductor spawns each solo ticket as a named background sub-agent with
# isolation worktree. The host cuts <name> a worktree under .claude/worktrees/<name> on branch worktree-<name>.
HOST_WORKTREES = '.claude/worktrees'
SUBAGENT_BRANCH = re.compile(r'worktree-(T-\d{4})-solo', re.I)
HOST_BRANCH = re.compile(r'worktree-agent-([A-Za-z0-9_-]+)')  # the host's own name for a sub-agent worktree branch
SOLO_SUBAGENT_PROMPT = ('{head}\nHandoff: {handoff}\n{sync}Brief: deliver ticket {handoff} end to end in this session as the solo agent. Read the ticket '
                        'and the files it names, make the smallest change that meets its done criterion, run every '
                        'check command it names and after a fix rerun the checks that fix can affect (every check when unsure), keeping any `(red)` control, and report files changed, each check '
                        'with its outcome, and anything still open. For a ticket of level L2 or L3 write the handoff\'s '
                        '## Acceptance criteria if it has none, end with your report, and say `verify: needed`: the '
                        'parent runs the one batched independent verifier. No person is present: never ask the user '
                        'and never use AskUserQuestion. You work on your own worktree branch: commit early and often, '
                        'one `WIP {id}` commit after each green check and a final commit `{id}: {title}` when every '
                        'check is green. Never push, open a PR, or publish: fanout.py land merges your branch, runs '
                        'the gates, and closes the ticket.')


class Refuse(Exception):
    """A preflight or setup refusal: the message goes to stderr and run exits 2."""


def git(cwd, *args):
    return subprocess.run(['git', *GIT_CFG, '-C', str(cwd), *args], env=ENV, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True)


def git_out(cwd, *args):
    p = git(cwd, *args)
    if p.returncode:
        raise Refuse(f'git {" ".join(args)} failed: {p.stderr.strip() or p.returncode}')
    return p.stdout.strip()


def first_line(text, default=''):
    lines = [ln.strip() for ln in (text or '').splitlines() if ln.strip()]
    return lines[0] if lines else default


def cell(text):
    return ' '.join(str(text).split()).replace('|', '\\|')


def solo_tier(size):
    """The solo level for a ticket size: L1, L2, or L3, a deprecated alias read as its level (tickets.size_level);
    L4, L5, or an unknown size has no solo level: None."""
    level = tickets.size_level(size)
    return level if level in SOLO_TIERS else None


def solo_model_label(tier, backend=None):
    """`<model> <effort>` the solo agent runs at for a level on the backend: the Claude row from SOLO_TIERS, or the
    Codex model and effort of sdlc-solo-l1..l3 read from adapters/codex/models.json (never a hardcoded guess)."""
    backend = backend or os.environ.get('SDLC_BACKEND', 'claude')
    model, effort, level = SOLO_TIERS[solo_tier(tier)]
    if backend == 'codex':
        try:
            model, effort = json.loads((PLUGIN / 'adapters' / 'codex' / 'models.json').read_text())['solo'][level]
        except (OSError, ValueError, KeyError):
            return f'codex {level} (model unreadable)'
    return f'{model} {effort}'


def gate_slots_off():
    """True when SDLC_GATE_SLOTS says no gate lock (0 or below): gates then run bare, as gate_lock.py itself would."""
    try:
        return int(ENV.get('SDLC_GATE_SLOTS') or 1) < 1
    except ValueError:
        return False


def gate_argv(ctx, lane, t, gate):
    """The argv that runs one --gate command: bash -c, through gate_lock.py run unless the lock is off."""
    argv = ['bash', '-c', gate]
    if ctx.get('gate_lock'):
        argv = [sys.executable, str(SCRIPTS / 'gate_lock.py'), 'run', '--name', f'{lane.name}/{t.id}', '--', *argv]
    return argv


def gate_vacuous(rc, text, gate=''):
    """True when a gate's output shows it ran no tests (rc 0 or 5 only: any other failure is plain red)."""
    return rc in (0, 5) and bool(VACUOUS_GATE.search(text) or (rc == 5 and 'pytest' in gate))


def solo_command(handoff_rel, size, backend=None):
    """The shell command that starts the solo agent for one ticket at its size's level, or raises Refuse.

    It starts through scripts/solo_run.py (T-0226), which runs `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`
    at the level's model and effort (or codex_exec.py solo L1..L3) and appends one `role solo` record with the
    session's cost to the ticket's runs.jsonl, so budget.py and the board meter the lane. SDLC_SELFTEST_RAW_SOLO
    restores the raw unmetered command, which the selftest uses as its negative control."""
    backend = backend or os.environ.get('SDLC_BACKEND', 'claude')
    tier = solo_tier(size)
    if tier is None:
        raise Refuse(f'no solo level for size {size!r}: want L1, L2, or L3')
    model, effort, level = SOLO_TIERS[tier]
    prompt = SOLO_PROMPT.format(handoff=handoff_rel)
    if backend not in ('claude', 'codex'):
        raise Refuse('unknown SDLC_BACKEND: ' + backend)
    if os.environ.get('SDLC_SELFTEST_RAW_SOLO'):
        if backend == 'codex':
            return ' '.join(shlex.quote(x) for x in (sys.executable, str(SCRIPTS / 'codex_exec.py'), 'solo', level, prompt))
        return 'SDLC_ROLE=solo ' + ' '.join(shlex.quote(x) for x in (
            'claude', '-p', '--plugin-dir', str(PLUGIN), '--agent', 'sdlc-lite:solo', '--model', model,
            '--effort', effort, '--dangerously-skip-permissions', '--', prompt))
    task_dir = pathlib.PurePosixPath(handoff_rel).parent.as_posix()
    return ' '.join(shlex.quote(x) for x in (
        sys.executable, str(SCRIPTS / 'solo_run.py'), 'run', '--task-dir', task_dir, '--tier', tier,
        '--backend', backend, '--exec', '--brief', prompt))  # --exec: the headless start of a `run` lane; sub-agent lanes use prep and land (T-0285), the Claude start refuses without SDLC_CLAUDE_EXEC=1 (T-0288, T-0361)


def default_driver(handoff_rel, kind='full', size=None):
    backend = os.environ.get('SDLC_BACKEND', 'claude')
    if kind == 'solo':
        if backend == 'claude' and os.environ.get('SDLC_CLAUDE_EXEC') != '1' and not os.environ.get('SDLC_SELFTEST_RAW_SOLO'):
            raise Refuse('no default claude -p driver: use fanout.py prep and land (sub-agent lanes), --driver CMD, or SDLC_CLAUDE_EXEC=1')
        return solo_command(handoff_rel, size)
    if backend == 'codex':
        return ' '.join(shlex.quote(x) for x in (
            sys.executable, str(SCRIPTS / 'codex_exec.py'), 'conductor', 'L1',
            PROMPT.format(handoff=handoff_rel)))
    if backend != 'claude':
        raise Refuse('unknown SDLC_BACKEND: ' + backend)
    if os.environ.get('SDLC_CLAUDE_EXEC') != '1':
        raise Refuse('no default claude -p driver: use fanout.py prep and land (sub-agent lanes), --driver CMD, or SDLC_CLAUDE_EXEC=1')
    return ' '.join(shlex.quote(x) for x in (
        'claude', '-p', '--plugin-dir', str(PLUGIN), '--agent', 'sdlc-lite:conductor', '--model', 'opus',
        '--effort', 'medium', '--dangerously-skip-permissions', PROMPT.format(handoff=handoff_rel)))


class Ticket:
    def __init__(self, tid, slug, title, size=''):
        self.id, self.slug, self.title, self.size = tid, slug, title, size


SPEC_FORMS = '<lane>=<id>[,<id>...] or <lane>@<branch>=<id>[,<id>...]'


class Lane:
    def __init__(self, name, tids, external=None):
        self.name, self.tids, self.tickets = name, tids, []
        # external: the registered branch an outside agent owns (<lane>@<branch>=...), else None;
        # an external lane's branch is that branch and its dir stays None (no worktree, no driver)
        self.external, self.tip = external, None  # tip: the external branch's commit at preflight
        self.branch = self.dir = self.port = None  # port: the lane record's port (lane_ports:), else None
        self.results = []  # (ticket id, outcome, commit)
        self.files = set()  # every path this lane brought to a merge (report.md's Overlap lines)
        self.done = False  # set when run_lane returns, under ctx['cond']; a later lane stops waiting on it


def branch_clash(name, refs):
    """An existing ref that blocks creating refs/heads/<name>: the same ref, or a directory/file clash."""
    full = 'refs/heads/' + name
    for r in refs:
        if r == full or full.startswith(r + '/') or r.startswith(full + '/'):
            return r
    return None


def norm_tid(x):
    """T-0123, 0123, and 123 are one id: return T-NNNN; anything else comes back unchanged."""
    m = re.fullmatch(r'(?:T-)?(\d{1,4})', x)
    return f'T-{int(m.group(1)):04d}' if m else x


def resolve_lanes_dir(a, cwd, top):
    """The lanes dir (--lanes-dir, else <toplevel>/.worktrees/fanout); inside the work tree it must be gitignored."""
    lanes_dir = (cwd / a.lanes_dir).resolve() if a.lanes_dir else top / '.worktrees' / 'fanout'
    if lanes_dir == top:
        raise Refuse(f'--lanes-dir {lanes_dir} is the work tree toplevel; lanes need their own dir')
    if top in lanes_dir.parents:
        # lanes inside the work tree must be gitignored, or every lane shows up as untracked files
        inner = lanes_dir.relative_to(top).as_posix()
        probe, want = ('.worktrees/x', '.worktrees/') if not a.lanes_dir else (f'{inner}/x', f'{inner}/')
        p = git(top, 'check-ignore', '-q', probe)
        if p.returncode == 1:
            what = 'the default lanes dir' if not a.lanes_dir else '--lanes-dir'
            raise Refuse(f'{what} {lanes_dir} is inside the work tree {top} but {want} is not gitignored; '
                         f'add {want} to .gitignore, or pass --lanes-dir outside the repo')
        if p.returncode:
            raise Refuse(f'git check-ignore {probe} failed: {p.stderr.strip() or p.returncode}')
    return lanes_dir


def preflight(a):
    """Every check before any write. Returns the run context; raises Refuse."""
    cwd = pathlib.Path.cwd()
    p = git(cwd, 'rev-parse', '--is-inside-work-tree')
    if p.returncode or p.stdout.strip() != 'true':
        raise Refuse('not a git repo: run fanout.py inside a git work tree with a commit')
    if git(cwd, 'rev-parse', '--verify', '-q', 'HEAD').returncode:
        raise Refuse('git repo has no commit: commit first')
    top = pathlib.Path(git_out(cwd, 'rev-parse', '--show-toplevel')).resolve()
    root = (cwd / a.root).resolve()
    try:
        rel = root.relative_to(top)
    except ValueError:
        raise Refuse(f'--root {a.root} is {root}, outside the git toplevel {top}')
    if not root.is_dir():
        raise Refuse(f'--root {a.root}: {root} is not a dir')

    try:
        tdir = tickets.ticket_dir(root)
        ts = tickets.load(tdir)
    except tickets.Fail as e:
        raise Refuse(str(e))
    except (OSError, UnicodeDecodeError) as e:
        raise Refuse(f'{root}: cannot read tickets: {e}')
    trel = tdir.relative_to(top)
    registered = tickets.external_branches(root)
    lanes, seen, errs = [], {}, []
    for spec in a.lanes:
        left, eq, ids = spec.rpartition('=')
        name, at, ext = left.partition('@')
        tids = [norm_tid(x.strip()) for x in ids.split(',') if x.strip()]
        if not eq or not tids or (at and not ext):
            errs.append(f'{spec!r}: want {SPEC_FORMS}')
            continue
        if not LANE_RE.fullmatch(name):
            errs.append(f'lane {name!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
        elif name in RESERVED:
            errs.append(f'lane {name!r} is reserved (the lanes dir holds {", ".join(RESERVED)})')
        elif any(x.name == name for x in lanes):
            errs.append(f'lane {name!r} is given twice')
        lane = Lane(name, tids, ext or None)
        lanes.append(lane)
        pool = ts
        if lane.external:
            # an external lane's tickets may exist only on its branch: read them from git objects there
            pool = None
            other = next((x.name for x in lanes[:-1] if x.external == ext), None)
            if other:
                errs.append(f'branch {ext} is named by lane {other} and lane {name}; a branch runs in one lane only')
            p = git(cwd, 'rev-parse', '-q', '--verify', f'refs/heads/{ext}^{{commit}}')
            if ext not in registered:
                errs.append(f'lane {name}: branch {ext} is not registered; an external lane needs the line '
                            f'`external_branch: {ext}` in {root / "config"}')
            elif p.returncode:
                errs.append(f'lane {name}: external branch {ext} is registered but refs/heads/{ext} is not a '
                            f'local branch with a commit')
            else:
                lane.tip = p.stdout.strip()
                pool = tickets.branch_tickets(root, ext)
        for tid in tids:
            if not tickets.ID_RE.fullmatch(tid):
                errs.append(f'{name}: {tid!r} is not a ticket id like T-0001')
                continue
            if tid in seen:
                errs.append(f'{tid} appears in lane {seen[tid]} and lane {name}; a ticket runs in one lane only')
                continue
            seen[tid] = name
            if pool is None:  # the branch itself was refused above
                continue
            hits = [(s, m) for s, m in pool if m.get('id') == tid]
            if not hits:
                errs.append(f'{tid}: no ticket on branch {ext} has this id' if lane.external
                            else f'{tid}: no ticket under {tdir} has this id')
            elif len(hits) > 1:
                errs.append(f'{tid}: {len(hits)} folders share this id ({", ".join(s for s, _ in hits)})')
            elif hits[0][1].get('status') in ('done', 'dropped'):
                errs.append(f'{tid} ({hits[0][0]}): status is {hits[0][1]["status"]}, nothing to run')
            else:
                s, m = hits[0]
                lane.tickets.append(Ticket(tid, s, str(m.get('title', '')), str(m.get('size', ''))))
    if not lanes and not errs:
        errs.append(f'no lanes given: want {SPEC_FORMS}')
    if errs:
        raise Refuse('\n'.join(errs))

    integration = a.integration or f'fanout/{datetime.date.today().isoformat()}'
    names = [integration] + [f'{integration}-{x.name}' for x in lanes if not x.external]
    for n in names:
        if git(cwd, 'check-ref-format', '--branch', n).returncode:
            raise Refuse(f'{n!r} is not a valid branch name')
    ours = {integration} | {f'{integration}-{x.name}' for x in lanes}
    for lane in lanes:
        if lane.external in ours:
            raise Refuse(f'lane {lane.name}: external branch {lane.external} is the integration branch or an '
                         f'<integration>-<lane> branch of this run; name the outside agent\'s own branch')
    refs = git_out(cwd, 'for-each-ref', '--format=%(refname)', 'refs/heads/').splitlines()
    reuse = ('refs/heads/' + integration) in refs
    if reuse:
        start = git_out(cwd, 'rev-parse', '--verify', f'refs/heads/{integration}^{{commit}}')
    else:
        clash = branch_clash(integration, refs)
        if clash:
            raise Refuse(f'integration branch {integration} clashes with the existing ref {clash}')
        base = a.base or 'HEAD'
        p = git(cwd, 'rev-parse', '--verify', '-q', f'{base}^{{commit}}')
        if p.returncode:
            raise Refuse(f'--base {base} is not a commit')
        start = p.stdout.strip()

    lanes_dir = resolve_lanes_dir(a, cwd, top)
    if lanes_dir.exists() and not lanes_dir.is_dir():
        raise Refuse(f'--lanes-dir {lanes_dir} exists and is not a dir')
    wts = git_out(cwd, 'worktree', 'list', '--porcelain').splitlines()
    wt_path = None
    for line in wts:
        if line.startswith('worktree '):
            wt_path = line[len("worktree "):]
        elif line == f'branch refs/heads/{integration}':
            raise Refuse(f'integration branch {integration} is checked out in {wt_path}; '
                         f'git worktree add cannot check it out twice')
    integ_dir = lanes_dir / 'integration'
    if integ_dir.exists():
        raise Refuse(f'{integ_dir} exists (an earlier run?); remove it with git worktree remove, '
                     f'or pass another --lanes-dir')
    for lane in lanes:
        if lane.external:  # no lane branch or worktree to create; the dir stays None
            lane.branch = lane.external
            continue
        lane.branch, lane.dir = f'{integration}-{lane.name}', lanes_dir / lane.name
        clash = branch_clash(lane.branch, refs)
        if clash:
            raise Refuse(f'lane branch {lane.branch} already exists or clashes with {clash}')
        if lane.dir.exists():
            raise Refuse(f'{lane.dir} already exists')

    relp = trel.as_posix()
    missing = []
    for lane in lanes:
        if lane.external:  # its handoffs were read from the branch itself
            continue
        for t in lane.tickets:
            path = f'{t.slug}/handoff.md' if relp == '.' else f'{relp}/{t.slug}/handoff.md'
            if git(cwd, 'cat-file', '-e', f'{start}:{path}').returncode:
                missing.append(path)
    if missing:
        raise Refuse(f'not committed at {start[:12]}: {", ".join(missing)}; lanes see only committed '
                     f'files, so commit the .sdlc/ trail first (it is usually gitignored: `git add -f <path>` then commit)')

    max_lanes = getattr(a, 'max_lanes', MAX_LANES_DEFAULT)
    if max_lanes < 1:
        raise Refuse('--max-lanes must be at least 1')
    if max_lanes > MAX_LANES_HARD and not getattr(a, 'yes_many', False):
        raise Refuse(f'--max-lanes {max_lanes} is above {MAX_LANES_HARD}: add --yes-many to confirm, and expect '
                     f'your plan limit and merge conflicts to be the limit, not this machine')
    n_regular = sum(1 for x in lanes if not x.external)
    if n_regular > max_lanes:
        raise Refuse(f'{n_regular} lanes exceed --max-lanes {max_lanes}: fewer lanes, or raise --max-lanes N '
                     f'(above {MAX_LANES_HARD} also needs --yes-many)')
    if getattr(a, 'stagger', STAGGER_DEFAULT) < 0:
        raise Refuse('--stagger must be 0 or more seconds')
    return {'cwd': cwd, 'top': top, 'root': root, 'rel': rel, 'trel': trel, 'lanes': lanes, 'integration': integration,
            'reuse': reuse, 'start': start, 'base': a.base or 'HEAD', 'lanes_dir': lanes_dir,
            'integ_dir': integ_dir, 'logs': lanes_dir / 'logs', 'gates': list(a.gate or []),
            'driver': a.driver, 'rewrite_refs': bool(getattr(a, 'rewrite_refs', False)),
            'numbered': tickets.config_numbered(root), 'lane_mode': getattr(a, 'lane', 'auto') or 'auto',
            'max_lanes': getattr(a, 'max_lanes', MAX_LANES_DEFAULT), 'stagger': getattr(a, 'stagger', STAGGER_DEFAULT),
            'allow_overlap': bool(getattr(a, 'allow_overlap', False)), 'kinds': {},
            'allow_empty_gate': bool(getattr(a, 'allow_empty_gate', False)),
            'gate_lock': not getattr(a, 'no_gate_lock', False) and not gate_slots_off()}


def lane_decision(ctx, taskdir=None):
    """(kind, why) for a ticket: kind is solo or full. --lane solo or full forces it; with --driver the
    driver decides (kind driver); else `steps.py lane` decides (read only when taskdir is given for a dry
    run, a recorded subprocess call otherwise is lane_run). lean after a plan runs as the chain."""
    mode = ctx['lane_mode']
    if ctx['driver']:
        return 'driver', '--driver given'
    if mode in ('solo', 'full'):
        return mode, f'--lane {mode}'
    try:
        lane, _point, reasons, _read = steps.lane_action(taskdir)
    except steps.Fail as e:
        return 'full', f'lane failed ({first_line(str(e))}): taking the full chain'
    return ('solo' if lane == 'solo' else 'full'), (reasons[0] if reasons else lane)


def lane_run(ctx, wt, t):
    """The lane for a ticket in its lane worktree, recorded in its skips.md by `steps.py lane`."""
    if ctx['driver'] or ctx['lane_mode'] in ('solo', 'full'):
        return lane_decision(ctx)
    taskdir = wt / ctx['trel'] / t.slug
    p = subprocess.run([sys.executable, str(SCRIPTS / 'steps.py'), 'lane', str(taskdir)], cwd=str(wt), env=ENV,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if p.returncode:
        return 'full', f'steps.py lane failed ({first_line(p.stderr, f"rc={p.returncode}")}): taking the full chain'
    out = [ln for ln in p.stdout.splitlines() if ln.strip()]
    lane = out[0].strip() if out else 'full'
    why = next((ln[len('reason: '):] for ln in out if ln.startswith('reason: ')), lane)
    return ('solo' if lane == 'solo' else 'full'), why


def driver_for(ctx, t, kind='full'):
    if ctx['driver']:
        return ctx['driver']
    return default_driver((ctx['trel'] / t.slug / 'handoff.md').as_posix(), kind, t.size)


def close_reason(ctx, t):
    """The `tickets.py close --reason` text for a ticket a solo agent delivered (a solo lane writes no filer
    file, which close needs otherwise), or None for every other lane."""
    kind, tier = ctx['kinds'].get(t.id, ('', None))
    if kind != 'solo':
        return None
    return (f'delivered by the solo agent (level {tier}); one independent batched verifier passed before the merge'
            if tier in SOLO_VERIFIED or ctx.get('roll') else f'delivered by the solo agent (level {tier}); the ticket\'s own checks and the fanout gates passed')


def write_solo_skips(taskdir, tier):
    """The solo lane's skipped planner and filer under ## Skipped, written by steps.write_solo_skips (the one
    writer, shared with `steps.py lane` itself); called again here for the level-sized reason and for an
    already-recorded lane. True when it wrote."""
    return steps.write_solo_skips(taskdir, tier)


def verifier_files(taskdir):
    """The task dir's verifier result file names now (the batched-verification baseline)."""
    try:
        return {f.name for f in pathlib.Path(taskdir).iterdir() if re.fullmatch(r'verifier-L\d+(-\d+)?\.md', f.name)}
    except OSError:
        return set()


def newest_verifier(d, names):
    """Path of the newest verifier result in `d` among the file `names`, or None (T-0398). order.py ranks a file with no
    runs.jsonl record below every recorded one, but a result a lane just produced is the one still unrecorded (the parent
    records it after the solo reports), so an older recorded result of a prior attempt must not outrank it: the unrecorded
    ones win when there are any, else the recorded order decides."""
    got = [p for p in order.ordered(d, 'verifier') if pathlib.Path(p).name in names]
    recorded = order._ranks(d)
    fresh = [p for p in got if pathlib.Path(p).name not in recorded]
    pick = fresh or got
    return pick[-1] if pick else None


def solo_verdict(taskdir, before):
    """'pass', 'fail', or None for the newest task-dir verifier result that is not in `before`."""
    new = {f for f in verifier_files(taskdir) if f not in before}
    newest = newest_verifier(taskdir, new)
    return steps.verdict_or_none(newest) if newest else None


def planned_scope(root, slug):
    """The paths allow-listed by the scope criteria of <ticket dir>/<slug>/step-<n>/handoff.md, where the
    ticket dir is tickets.ticket_dir(root), or None when no step handoff yields an entry (the ticket is not planned)."""
    found, any_entry = set(), False
    tdir = tickets.ticket_dir(pathlib.Path(root)) / slug
    steps_dirs = sorted(d for d in tdir.iterdir() if d.is_dir() and re.fullmatch(r'step-\d+', d.name)) \
        if tdir.is_dir() else []
    for d in steps_dirs:
        h = d / 'handoff.md'
        if not h.is_file():
            continue
        for _, line in steps.criteria_indexed(h.read_text(encoding='utf-8').splitlines()):
            if not steps.list_item(line):
                continue
            for span in steps.line_spans(line):
                if 'git diff --name-only' not in span or not steps.INVERT_GREP_RE.search(span):
                    continue
                for form, m in steps.widen_forms(span):
                    for e in steps.widen_listed(form, m):
                        if form != 'F':
                            e = re.sub(r'\\(.)', r'\1', e)
                        found.add(e)
                        any_entry = True
    return found if any_entry else None


def overlap_pairs(ctx):
    """([(lane a, ticket a, lane b, ticket b, shared paths)], [unplanned ticket ids]) by planned scope."""
    scoped, unplanned = [], []
    for lane in ctx['lanes']:
        for t in lane.tickets:
            sc = None if lane.external else planned_scope(ctx['root'], t.slug)
            if sc is None:
                unplanned.append(t.id)
            else:
                scoped.append((lane, t, sc))
    pairs = []
    for i, (la, ta, sa) in enumerate(scoped):
        for lb, tb, sb in scoped[i + 1:]:
            if la is not lb and sa & sb:
                pairs.append((la, ta, lb, tb, sorted(sa & sb)))
    return pairs, unplanned


def plan_overlap(ctx):
    """The dry run's planned-scope overlap lines."""
    pairs, unplanned = overlap_pairs(ctx)
    out = [f"overlap (planned scope): {la.name} {ta.id} and {lb.name} {tb.id}: {', '.join(paths)}"
           for la, ta, lb, tb, paths in pairs]
    if pairs:
        out.append('overlap (planned scope): run refuses unless --allow-overlap')
    if not out:
        out.append('overlap (planned scope): none')
    if unplanned:
        out.append(f"overlap (planned scope): not planned, checked at merge time: {', '.join(unplanned)}")
    return out


INSTALL_WORDS = re.compile(r'\b(npm (ci|install|i)|pnpm (i|install)|yarn( install)?|bun install)\b')


def deps_note(ctx):
    """A preflight note when the gates run in a fresh worktree that will lack node_modules: package.json is
    tracked at the start commit and no gate installs. A node_modules symlink is no fix (drift checks fail)."""
    if not ctx['gates'] or any(INSTALL_WORDS.search(g) for g in ctx['gates']):
        return ''
    if git(ctx['top'], 'cat-file', '-e', f"{ctx['start']}:package.json").returncode:
        return ''
    return ('note: gates run in a fresh worktree with no node_modules; start the gate with `npm ci && ...` '
            '(a node_modules symlink makes drift checks such as build-editor-demo --check fail)')


def print_plan(ctx):
    out = ['fanout plan (dry run: nothing created)']
    if ctx['reuse']:
        out.append(f"integration branch {ctx['integration']} exists at {ctx['start']}: reuse it (--base ignored)")
    else:
        out.append(f"base: {ctx['start']} ({ctx['base']})")
        out.append(f"integration branch: {ctx['integration']} (new, at the base)")
    out.append(f"integration worktree: {ctx['integ_dir']}")
    out.append(f"ticket root in each worktree: {ctx['rel'].as_posix()}")
    if ctx['trel'] != ctx['rel']:
        out.append(f"ticket folders in each worktree: {ctx['trel'].as_posix()}")
    n_reg = sum(1 for x in ctx['lanes'] if not x.external)
    out.append(f"lane cap: {n_reg} regular lane(s) of at most {ctx['max_lanes']} (--max-lanes; above "
               f"{MAX_LANES_HARD} also needs --yes-many); stagger: {ctx['stagger']} s between lane starts (--stagger)")
    for lane in ctx['lanes']:
        if lane.external:
            out.append(f'lane {lane.name}: external branch {lane.branch} (registered; no worktree, no driver)')
        else:
            out.append(f'lane {lane.name}: branch {lane.branch}, worktree {lane.dir}')
        for t in lane.tickets:
            out.append(f'  {t.id} {t.slug}: {t.title}')
            if not lane.external:
                kind, why = lane_decision(ctx, tickets.ticket_dir(ctx['root']) / t.slug)
                tier = solo_tier(t.size) if kind == 'solo' else None
                shown = f'solo, level {tier}: {solo_model_label(tier)}' if tier else kind
                out.append(f'    lane: {shown} ({why})')
    out += plan_overlap(ctx)
    if ctx['gates']:
        out += [f'gate {k}: {g}' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('gates: none given (merges will not be gated)')
    if deps_note(ctx):
        out.append(deps_note(ctx))
    if ctx['driver']:
        out.append(f"driver: {ctx['driver']}")
    else:
        out.append(f"driver: solo first (--lane {ctx['lane_mode']}): steps.py lane picks solo or the full chain per ticket")
        out.append(f"  solo (ticket level L1 and L2): {solo_command('<handoff>', 'L2')}")
        try:
            out.append(f"  full: {default_driver('<handoff>')}")
        except Refuse as e:
            out.append(f"  full: {e}")
        out.append("  (<handoff> is each ticket's handoff path relative to the lane worktree)")
    if ctx['rewrite_refs']:
        out.append('close: tickets.py close <slug> --rewrite-refs '
                   '(files citing a ticket folder are rewritten to its .NNNN-<slug> path)')
    elif ctx['numbered']:
        out.append('close: tickets.py close <slug> (numbered folders: a file citing a ticket folder '
                   'refuses the close; --rewrite-refs rewrites them)')
    else:
        out.append('close: tickets.py close <slug>')
    out.append(f"logs: {ctx['logs']}")
    print('\n'.join(out))


def setup(ctx):
    """Branches and worktrees, sequentially. On any failure, remove what this run created and raise."""
    made_dir, worktrees, branches = False, [], []
    cwd, lanes_dir, integration = ctx['cwd'], ctx['lanes_dir'], ctx['integration']

    def rollback():
        for w in reversed(worktrees):
            git(cwd, 'worktree', 'remove', '--force', str(w))
        for b in reversed(branches):
            git(cwd, 'branch', '-D', b)
        git(cwd, 'worktree', 'prune')
        if made_dir:
            shutil.rmtree(lanes_dir, ignore_errors=True)

    try:
        if not lanes_dir.exists():
            lanes_dir.mkdir(parents=True)
            made_dir = True
        if ctx['reuse']:
            print(f"reusing integration branch {integration} at {ctx['start'][:12]}", flush=True)
        else:
            git_out(cwd, 'branch', integration, ctx['start'])
            branches.append(integration)
            print(f"created integration branch {integration} at {ctx['start'][:12]} ({ctx['base']})", flush=True)
        # merge.lock beside logs/ marks the lanes dir, so lanes.py reads the integration tree as a fanout integration lane
        (lanes_dir / 'merge.lock').touch()
        # the integration tree stays a plain worktree add: its branch may be reused, and open_lane makes a new one
        git_out(cwd, 'worktree', 'add', '-q', str(ctx['integ_dir']), integration)
        worktrees.append(ctx['integ_dir'])
        print(f"worktree integration: {ctx['integ_dir']}", flush=True)
        regular = [lane for lane in ctx['lanes'] if not lane.external]
        for lane in regular:
            r = lanes.open_lane(lane.name, kind='fanout', tickets=[t.id for t in lane.tickets], base=integration,
                                into=integration, root=str(ctx['root']), path=lane.dir, branch=lane.branch,
                                check_claim=False, cwd=ctx['cwd'])
            if r['rc']:
                raise Refuse(f"lanes.py open {lane.name}: {r['message']}; removed what this run created")
            worktrees.append(lane.dir)
            branches.append(lane.branch)
            lane.port = r.get('port')
            port = f', port {lane.port}' if lane.port else ''
            print(f'worktree {lane.name}: {lane.dir} (branch {lane.branch}{port})', flush=True)
        for lane in ctx['lanes']:
            if lane.external:
                print(f'external {lane.name}: branch {lane.branch} (no worktree, no driver)', flush=True)
        # .sdlc/config is often untracked (the trail is gitignored): without it a fresh worktree reads the
        # default ticket root and numbering, so tickets.py close would look for <root>/<slug>, not <root>/tickets/<slug>
        src_cfg = ctx['root'] / 'config'
        if src_cfg.is_file():
            for wt in [ctx['integ_dir']] + [lane.dir for lane in regular]:
                dst_cfg = wt / ctx['rel'] / 'config'
                if not dst_cfg.exists() and dst_cfg.parent.is_dir():
                    shutil.copyfile(str(src_cfg), str(dst_cfg))
        missing = [str(lane.dir / ctx['trel'] / t.slug / 'handoff.md')
                   for lane in regular for t in lane.tickets
                   if not (lane.dir / ctx['trel'] / t.slug / 'handoff.md').is_file()]
        if missing:
            raise Refuse(f'missing in the lane worktrees: {", ".join(missing)}; the .sdlc/ trail must be '
                         f'committed; removed what this run created')
        ctx['logs'].mkdir(parents=True, exist_ok=True)
    except BaseException:
        rollback()
        raise


class MergeLock:
    """Exclusive fcntl.flock on <lanes-dir>/merge.lock (macOS has no flock binary), plus a thread lock
    so lane threads in this process serialize whatever the platform's flock semantics."""

    def __init__(self, path):
        self.path, self.local, self.f = path, threading.Lock(), None

    def __enter__(self):
        self.local.acquire()
        try:
            self.f = open(self.path, 'a')
            fcntl.flock(self.f, fcntl.LOCK_EX)
        except BaseException:
            if self.f:
                self.f.close()
            self.local.release()
            raise
        return self

    def __exit__(self, *exc):
        try:
            fcntl.flock(self.f, fcntl.LOCK_UN)
            self.f.close()
        finally:
            self.f = None
            self.local.release()


PRINT = threading.Lock()


def say(ctx, lane, tid, event):
    """Print `[<run_id>] [<lane>] <id> <event>` and append the same line to logs/fanout.log."""
    line = f"[{ctx['run_id']}] [{lane.name}] {tid} {event}"
    with PRINT:
        print(line, flush=True)
        with open(ctx['logs'] / 'fanout.log', 'a', encoding='utf-8') as f:
            f.write(line + '\n')


def run_logged(argv, cwd, env, log, run_id):
    """Run argv with stdin /dev/null, writing each output line to a fresh log file (the caller picks a unique name) as
    `[<run_id>] <line>`; a final line without a newline still gets the prefix. Returns the exit code."""
    prefix = f'[{run_id}] '.encode()
    with open(log, 'wb') as f:
        p = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, env=env)
        for line in p.stdout:
            f.write(prefix + line)
        p.stdout.close()
        return p.wait()


def in_merge(wt):
    return git(wt, 'rev-parse', '-q', '--verify', 'MERGE_HEAD').returncode == 0


# Run artifacts a lane commit never stages: they fail consumer repo gates (T-0339).
LANE_ADD = ('add', '-A', '--', '.', ':(exclude,glob)**/*.log', ':(exclude,glob)**/.run.lock',
            ':(exclude,glob)**/*.running')
LANE_ADD_SH = 'git ' + ' '.join(shlex.quote(a) for a in LANE_ADD)  # the same add as a printed shell command (T-0341)


def wip_commit(wt, tid, outcome):
    """Commit whatever a stopped ticket left in the lane worktree wt as `wip(<id>): <outcome>`.
    Runs git only in wt (never the integration worktree, main, or the stash). Returns the new
    short sha, or '' when the tree is clean or the add or commit fails; never raises."""
    try:
        dirty = git(wt, 'diff', '--quiet', 'HEAD').returncode != 0
        untracked = git(wt, 'ls-files', '--others', '--exclude-standard')
        if not dirty and not (untracked.returncode == 0 and untracked.stdout.strip()):
            return ''
        if git(wt, *LANE_ADD).returncode:
            return ''
        if git(wt, 'commit', '-q', '-m', f'wip({tid}): {outcome}').returncode:
            return ''
        p = git(wt, 'rev-parse', 'HEAD')
        return p.stdout.strip()[:7] if p.returncode == 0 else ''
    except Exception:
        return ''


def porcelain(wt):
    """The set of (status, path) entries in `git status --porcelain`, as paths tagged by status,
    so a before/after diff names every path whose state changed."""
    p = git(wt, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    if p.returncode:
        raise Refuse(f'git status failed: {p.stderr.strip() or p.returncode}')
    items, parts, k = set(), p.stdout.split('\0'), 0
    while k < len(parts):
        e = parts[k]
        k += 1
        if len(e) < 4:
            continue
        items.add((e[:2], e[3:]))
        if e[0] in 'RC' and k < len(parts):
            items.add((e[:2], parts[k]))
            k += 1
    return items


STEP_DIR_RE = re.compile(r'step-(\d+)')


def inherited_red(ticket_dir):
    """`inherited red: step-<n>: <tests>` for the first step-<n> dir (numeric order; never a
    step-<n>.superseded-<k> dir) whose steps.next_action is `inherited`, the tests taken after the
    `inherited red:` prefix from the newest verifier result's ## Verdict line when the verifier
    reported it, else from the newest builder result's ## Status line; else None."""
    base = pathlib.Path(ticket_dir)
    if not base.is_dir():
        return None
    dirs = sorted((int(m.group(1)), d) for d in base.iterdir()
                  if d.is_dir() and (m := STEP_DIR_RE.fullmatch(d.name)))
    for n, d in dirs:
        try:
            action, _, _, read = steps.next_action(d)
            if action != 'inherited':
                continue
            if len(read) == 2:  # verifier-inherited: its Verdict names the tests
                body = steps.section(read[1], 'Verdict') or []
            else:  # builder-inherited
                body = steps.section(read[0], 'Status') or []
            first = next((ln.strip() for ln in body if ln.strip()), '')
            tests = re.sub(r'(?i)^inherited red:', '', first).strip()
        except Exception:  # steps.Fail included: this dir is not inherited
            continue
        return f'inherited red: step-{n}: {tests}'
    return None


def lane_port_env(env, lane):
    """Set SDLC_LANE_PORT in env to the lane record's port, or drop an inherited value when the lane has none."""
    if lane.port:
        env['SDLC_LANE_PORT'] = str(lane.port)
    else:
        env.pop('SDLC_LANE_PORT', None)
    return env


def run_ticket(ctx, lane, t, lock):
    """One ticket through sync, driver, lane commit, and the locked merge. Returns (outcome, commit).
    An external lane (no dir) goes straight to the locked merge of its branch: no pre-sync wip, sync,
    driver, or lane commit, and the outside branch is never written."""
    if lane.dir is None:
        tip = git_out(ctx['cwd'], 'rev-parse', '--verify', f'refs/heads/{lane.branch}^{{commit}}')
        return merge_gate_close(ctx, lane, t, lock, f'refs/heads/{lane.branch}', tip[:7])
    wt, rel, integration = lane.dir, ctx['rel'], ctx['integration']
    with lock:
        # a lane tree already dirty before the sync: set its work aside on the lane branch and stop
        # the ticket (no sync, driver, lane commit, or merge), so that wip commit is never merged
        sha = wip_commit(wt, t.id, 'dirty before sync')
        if sha:
            say(ctx, lane, t.id, f'wip {sha} on {lane.branch}')
            return 'dirty before sync', f'wip {sha}'
        p = git(wt, 'merge', '--ff', '--no-edit', integration)
        if p.returncode:
            if in_merge(wt):
                git(wt, 'merge', '--abort')
                return 'sync conflict', ''
            return f'sync failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', ''

    env = dict(ENV, FANOUT_LANE=lane.name, FANOUT_TICKET=t.id, FANOUT_SLUG=t.slug,
               FANOUT_HANDOFF=str(wt / ctx['trel'] / t.slug / 'handoff.md'), FANOUT_ROOT=str(wt / rel),
               FANOUT_INTEGRATION=integration, FANOUT_PLUGIN_ROOT=str(PLUGIN), SDLC_HEADLESS='1', SDLC_ROLE='conductor',
               BASH_DEFAULT_TIMEOUT_MS=TIMEOUT_MS, BASH_MAX_TIMEOUT_MS=TIMEOUT_MS, FANOUT_RUN_ID=ctx['run_id'])
    lane_port_env(env, lane)
    log = ctx['logs'] / f'{lane.name}-{t.id}.log'
    kind, why = lane_run(ctx, wt, t)
    tier = solo_tier(t.size) if kind == 'solo' else None
    if kind == 'solo' and tier is None:  # an L4, L5, or unsized ticket has no solo level: the chain takes it
        kind, why = 'full', f'size {t.size or "unset"} has no solo level'
    ctx['kinds'][t.id] = (kind, tier)
    env['FANOUT_LANE_KIND'] = kind
    if kind in ('full', 'driver') and (ctx['driver'] or ctx['lane_mode'] == 'full') and not env.get('SDLC_LANE_OVERRIDE'):
        env['SDLC_LANE_OVERRIDE'] = 'fanout forced the full chain (--lane full or --driver)'  # run.sh lane gate
    say(ctx, lane, t.id, f'lane {kind}' + (f' level {tier}' if tier else '') + f' ({why})')
    taskdir = wt / ctx['trel'] / t.slug
    if kind == 'solo' and tier:
        write_solo_skips(taskdir, tier)
    before = verifier_files(taskdir)
    say(ctx, lane, t.id, f'driver started (log {log})')
    rc = run_logged(['bash', '-c', driver_for(ctx, t, kind)], str(wt), env, log, ctx['run_id'])
    # The lane's last role run has no successor run.sh to reap a SIGKILLed run's prefix; reap it here,
    # before any lane commit. Only dead-owner prefixes go; the exit code is ignored.
    subprocess.run(['bash', str(SCRIPTS / 'reap-tmp-worktrees.sh'), str(wt)], stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=ENV)
    inherited = inherited_red(wt / ctx['trel'] / t.slug)
    if rc:  # a non-zero exit still reports an inherited-red cause, with the driver rc kept visible
        if not inherited and rc == 4:  # solo_run.py's budget gate (T-0229): the ticket is at 80 percent with no ack
            return 'driver failed rc=4 (budget gate: budget.py ack)', ''
        return (f'{inherited} (driver rc={rc})' if inherited else f'driver failed rc={rc}'), ''
    if inherited:  # main was already red: no lane commit, merge, or close; run_lane WIP-commits the tree
        return inherited, ''
    if kind == 'solo' and tier in SOLO_VERIFIED:  # one independent batched verifier decides before any merge
        verdict = solo_verdict(taskdir, before)
        if verdict is None:  # the solo did not run it (Codex solo, say): fanout runs it once
            vlevel = solo_verifier(taskdir / 'handoff.md')
            say(ctx, lane, t.id, f'verifier {vlevel} started (the solo left no new verifier result)')
            vrc = run_logged(['bash', str(SCRIPTS / 'run.sh'), 'verifier', vlevel,
                              str(taskdir / 'handoff.md')], str(wt), env,
                             ctx['logs'] / f'{lane.name}-{t.id}-verifier.log', ctx['run_id'])
            verdict = solo_verdict(taskdir, before) if not vrc else None
            if verdict is None:
                return (f'no verifier result (run.sh rc={vrc})' if vrc else 'no verifier result'), ''
        if verdict != 'pass':
            return f'verifier {verdict}', ''

    p = git(wt, *LANE_ADD)
    if p.returncode:
        return f'lane add failed: {first_line(p.stderr, f"rc={p.returncode}")}', ''
    if git(wt, 'diff', '--cached', '--quiet').returncode == 0:
        return 'no changes', ''
    p = git(wt, 'commit', '-q', '-m', f'{t.id}: {t.title}')
    if p.returncode:
        return f'lane commit failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', ''
    lane_sha = git_out(wt, 'rev-parse', 'HEAD')
    say(ctx, lane, t.id, f'committed {lane_sha[:7]} on {lane.branch}')
    return merge_gate_close(ctx, lane, t, lock, lane.branch, lane_sha[:7])


def lane_pending(ctx, lane):
    """The set of paths lane may still merge: for a regular lane, its working tree against the merge base
    with the integration branch (committed and uncommitted edits) plus its untracked files; for an external
    lane, `<integration>...refs/heads/<branch>`. Every git call passes --no-optional-locks first, so a read
    never takes index.lock while that lane's driver runs git. Any git failure gives an empty set, so a
    failed read never blocks a waiting lane."""
    def names(cwd, *args):
        p = git(cwd, '--no-optional-locks', *args)
        if p.returncode:
            raise Refuse(p.stderr.strip() or f'rc={p.returncode}')
        return {ln for ln in p.stdout.splitlines() if ln}

    integration = ctx['integration']
    try:
        if lane.dir is None:
            return names(ctx['cwd'], 'diff', '--name-only', f'{integration}...refs/heads/{lane.branch}')
        base = names(lane.dir, 'merge-base', integration, 'HEAD')
        if len(base) != 1:
            return set()
        return (names(lane.dir, 'diff', '--name-only', base.pop())
                | names(lane.dir, 'ls-files', '--others', '--exclude-standard'))
    except Exception:
        return set()


def wait_for_overlap(ctx, lane, t, ref):
    """Before the merge lock: while an earlier lane (spec order) that has not finished may still merge a
    path this ticket brings (`git diff --name-only <integration>...<ref>`), wait for it, so the lane it
    overlaps merges first. A lane waits only for an earlier lane, never a later one, so no wait cycle can
    form. Prints `waiting for lane <other> (overlap: <paths>)` once per distinct lane and path set;
    rechecks on each notify of ctx['cond'] (a ticket outcome or a lane finishing) or every 2 s."""
    p = git(ctx['integ_dir'], '--no-optional-locks', 'diff', '--name-only', f"{ctx['integration']}...{ref}")
    mine = {ln for ln in p.stdout.splitlines() if ln} if p.returncode == 0 else set()
    if not mine:
        return
    lanes, cond, shown = ctx['lanes'], ctx['cond'], None
    earlier = lanes[:next(k for k, x in enumerate(lanes) if x is lane)]
    with cond:
        while True:
            hit = None
            for other in earlier:
                if other.done:
                    continue
                files = mine & lane_pending(ctx, other)
                if files:
                    hit = (other, files)
                    break
            if hit is None:
                return
            other, files = hit
            if (other.name, frozenset(files)) != shown:
                shown = (other.name, frozenset(files))
                say(ctx, lane, t.id, f'waiting for lane {other.name} (overlap: {", ".join(sorted(files))})')
            cond.wait(2)


def merge_gate_close(ctx, lane, t, lock, ref, cell):
    """Step 5 for both lane kinds: first, outside the lock, wait_for_overlap; then under the merge lock in
    the integration worktree: refuse a dirty tree, record the paths ref brings in lane.files, merge ref
    --no-ff as `Merge <lane branch>: <id>`, run the gates (skipped when the merge left HEAD
    unchanged: an external branch already merged, as for its second ticket or a resume), close the
    ticket, and commit `close <id>`. cell is the Commit cell for an outcome before the merge stands (the
    lane commit, or an external branch's tip). Returns (outcome, commit)."""
    integ, rel, trel = ctx['integ_dir'], ctx['rel'], ctx['trel']
    wait_for_overlap(ctx, lane, t, ref)
    with lock:
        # uncommitted tracked edits in the integration tree: refuse before the merge, so neither
        # `reset --hard <before>` below can discard them (untracked files survive a reset)
        p = git(integ, 'status', '--porcelain', '--untracked-files=no')
        if p.returncode:
            return f'integration status failed: {first_line(p.stderr, f"rc={p.returncode}")}', cell
        if p.stdout.strip():
            return f'integration dirty: {p.stdout.splitlines()[0][3:]}', cell
        p = git(integ, 'diff', '--name-only', f'HEAD...{ref}')
        if p.returncode == 0:
            lane.files.update(ln for ln in p.stdout.splitlines() if ln)
        before = git_out(integ, 'rev-parse', 'HEAD')
        p = git(integ, 'merge', '--no-ff', '--no-edit', '-m', f'Merge {lane.branch}: {t.id}', ref)
        if p.returncode:
            conflict = in_merge(integ)
            if not conflict or git(integ, 'merge', '--abort').returncode:
                git(integ, 'reset', '-q', '--hard', before)
            if conflict:
                return 'merge conflict', cell
            return f'merge failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', cell
        merge_sha = git_out(integ, 'rev-parse', 'HEAD')
        gates = ctx['gates']
        if merge_sha == before:  # nothing new came in, so there is nothing to gate
            say(ctx, lane, t.id, f'{lane.branch} already merged: nothing new, gates skipped')
            gates = []
        for k, gate in enumerate(gates, 1):
            stem = f'gate-{lane.name}-{t.id}-{k}-a'
            pat = re.compile(re.escape(stem) + r'(\d+)\.log$')
            n = 1 + max((int(m.group(1)) for f in ctx['logs'].iterdir() if (m := pat.match(f.name))), default=0)
            genv = lane_port_env(dict(ENV, FANOUT_RUN_ID=ctx['run_id']), lane)
            rc = run_logged(gate_argv(ctx, lane, t, gate), str(integ), genv, ctx['logs'] / f'{stem}{n}.log', ctx['run_id'])
            logtext = ''
            if rc in (0, 5):
                try:
                    logtext = (ctx['logs'] / f'{stem}{n}.log').read_text(errors='replace')
                except OSError:
                    pass
            if gate_vacuous(rc, logtext, gate):
                if not ctx.get('allow_empty_gate'):
                    git_out(integ, 'reset', '-q', '--hard', before)
                    return f'gate vacuous: {gate} ran no tests (--allow-empty-gate accepts it)', cell
                say(ctx, lane, t.id, f'gate vacuous accepted (--allow-empty-gate): {gate}')
            elif rc:
                git_out(integ, 'reset', '-q', '--hard', before)
                hint = ''
                if (integ / 'package.json').is_file() and not (integ / 'node_modules').exists():
                    hint = ' (no node_modules in the gate worktree: start the gate with `npm ci && ...`)'
                return f'red: {gate} rc={rc}{hint}', cell
        if lane.dir is not None:  # an external lane has no lane dir: its ticket folder came in with the merge
            src, dst = lane.dir / trel / t.slug, integ / trel / t.slug
            if not any(dst.glob('filer-L*.md')) and src.is_dir():
                shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
        if ctx.get('land') and ctx['kinds'].get(t.id, ('', None))[0] == 'solo':
            record_solo_lane(integ / trel / t.slug, ctx['kinds'][t.id][1])
        argv = [sys.executable, str(SCRIPTS / 'tickets.py'), '--root', rel.as_posix(), 'close', t.slug]
        if close_reason(ctx, t):
            argv += ['--reason', close_reason(ctx, t)]
        if ctx['rewrite_refs']:
            argv.append('--rewrite-refs')
        pre = porcelain(integ)
        p = subprocess.run(argv, cwd=str(integ), stdin=subprocess.DEVNULL, env=ENV, capture_output=True, text=True)
        if p.returncode:
            # the close wrote nothing; drop any copied files so a later close commit cannot sweep them in
            git(integ, 'clean', '-fdq', '--', (trel / t.slug).as_posix())
            why = f'merged, close refused: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}'
            if not ctx['rewrite_refs'] and '--rewrite-refs' in (p.stderr or '') + (p.stdout or ''):
                why += '; fanout.py run --rewrite-refs rewrites them'
            return why, merge_sha[:7]
        relp = rel.as_posix()
        changed = {path for _, path in porcelain(integ) - pre}
        extra = sorted(path for path in changed
                       if relp != '.' and path != relp and not path.startswith(relp + '/'))
        git_out(integ, 'add', '-A', '--', relp, *extra)
        if git(integ, 'diff', '--cached', '--quiet').returncode:
            git_out(integ, 'commit', '-q', '-m', f'close {t.id}')
        return 'merged', merge_sha[:7]


def run_lane(ctx, lane, lock):
    cond = ctx['cond']
    try:
        stopped = False
        for t in lane.tickets:
            if stopped:
                outcome, commit = 'skipped', ''
            else:
                try:
                    outcome, commit = run_ticket(ctx, lane, t, lock)
                except Exception as e:  # a git or IO failure mid-ticket: record it, stop the lane
                    outcome, commit = f'error: {first_line(str(e), type(e).__name__)}', ''
                stopped = outcome != 'merged'
                if stopped and lane.dir is not None:  # an external lane has no tree here and its branch is not ours
                    # a stopped ticket's work stays on the lane branch as a wip commit, never merged
                    sha = wip_commit(lane.dir, t.id, outcome)
                    if sha:
                        say(ctx, lane, t.id, f'wip {sha} on {lane.branch}')
                        commit = commit or f'wip {sha}'
            lane.results.append((t.id, outcome, commit))
            with cond:  # a later lane waiting on this one rechecks its overlap now
                cond.notify_all()
            say(ctx, lane, t.id, outcome)
    finally:
        with cond:
            lane.done = True
            cond.notify_all()


def report(ctx):
    integ = ctx['integ_dir']
    tip = git(integ, 'rev-parse', 'HEAD').stdout.strip()
    out = ['# fanout report', '', f"- Run: `{ctx['run_id']}`",
           f"- Integration branch: `{ctx['integration']}` at `{tip}`"
           + (' (reused)' if ctx['reuse'] else f" (from `{ctx['start'][:12]}`)"),
           f'- Integration worktree: `{integ}`']
    for x in ctx['lanes']:
        if x.external:  # the branch tip now (fanout never writes it), else the tip preflight saw
            sha = git(ctx['cwd'], 'rev-parse', '-q', '--verify', f'refs/heads/{x.branch}^{{commit}}').stdout.strip()
            out.append(f'- Lane `{x.name}`: external branch `{x.branch}` at `{sha or x.tip}`')
        else:
            out.append(f'- Lane `{x.name}`: `{x.dir}` (branch `{x.branch}`)')
    if ctx['gates']:
        out += [f'- Gate {k}: `{g}`' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('- No gates given: merges were not gated.')
    out.append(f"- Logs: `{ctx['logs']}`")
    lanes = ctx['lanes']
    overlap = [f'- Overlap: `{x.name}` and `{y.name}`: ' + ', '.join(f'`{f}`' for f in sorted(x.files & y.files))
               for k, x in enumerate(lanes) for y in lanes[k + 1:] if x.files & y.files]
    out += overlap or ['- Overlap: none']
    if 'closes' in ctx:  # run only: each closed lane, each lane kept open, and the integration tree
        out += [f'- {line}' for line in ctx['closes']]
        out.append(f"- lane still open: {integ} (integration: stays until main contains {ctx['integration']})")
    for lane in ctx['lanes']:
        for tid, _outcome, _commit in lane.results:
            if tid in ctx['kinds']:
                kind, tier = ctx['kinds'][tid]
                out.append(f'- Lane for `{tid}`: {kind}' + (f' (level {tier}: {solo_model_label(tier)})' if tier else ''))
    out += ['', '| Lane | Ticket | Outcome | Commit |', '|---|---|---|---|']
    for lane in ctx['lanes']:
        for tid, outcome, commit in lane.results:
            out.append(f'| {lane.name} | {tid} | {cell(outcome)} | {commit or "-"} |')
    text = '\n'.join(out) + '\n'
    (ctx['lanes_dir'] / 'report.md').write_text(text, encoding='utf-8')
    return text


def refuse_overlap(ctx):
    """Refuse (run and prep alike) two tickets in different lanes whose planned scope overlaps, unless --allow-overlap."""
    if ctx['allow_overlap']:
        return
    pairs, _ = overlap_pairs(ctx)
    if pairs:
        la, ta, lb, tb, paths = pairs[0]
        raise Refuse(f"{ta.id} (lane {la.name}) and {tb.id} (lane {lb.name}) plan to change the same "
                     f"files ({', '.join(paths)}): run them in one lane, or pass --allow-overlap and let "
                     f"the merge-time wait serialize them")


def sweep_lanes(top):
    """Close every landed plugin lane before a run starts (lanes.py sweep --apply), unless `lane_sweep: off` in
    .sdlc/config. Prints each result line as `lanes sweep: <line>`; an error is printed too and never blocks the run."""
    try:
        if lanes.config(top)['lane_sweep'] == 'off':
            return
        res, _ = lanes.sweep(apply=True, cwd=str(top))
    except lanes.LaneError as e:
        print(f'lanes sweep: {e}', flush=True)
        return
    for r in res:
        for line in (r.get('message') or '').splitlines():
            print(f'lanes sweep: {line}', flush=True)


def close_lanes(ctx):
    """After the run, close each regular lane whose every ticket merged (lanes.py writes the archive ref first); a
    stopped lane, or one whose close refuses, keeps its tree and WIP commit. Sets ctx['closes'] to the report lines."""
    lines = []
    for lane in ctx['lanes']:
        if lane.external:
            continue
        bad = next((o for _, o, _ in lane.results if o != 'merged'), None)
        if bad is None and lane.results:
            try:
                r = lanes.close_lane(str(lane.dir), cwd=str(ctx['top']))  # LANE-CLOSE
            except lanes.LaneError as e:
                r = dict(rc=1, message=str(e))
            msg = first_line(r['message'], f"rc={r['rc']}")
            if not r['rc']:
                lines.append(msg)
                continue
            bad = msg
        lines.append(f'lane still open: {lane.dir} ({bad or "no tickets ran"})')
    ctx['closes'] = lines


def cmd_run(a):
    try:
        ctx = preflight(a)
        if a.dry_run:
            print_plan(ctx)
            return 0
        # fanout mints its own id on every run; an inherited SDLC_ATTEMPT_ID belongs to a role attempt
        ctx['run_id'] = 'fanout-' + uuid.uuid4().hex[:12]
        refuse_overlap(ctx)
        sweep_lanes(ctx['top'])
        setup(ctx)
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    lock = MergeLock(ctx['lanes_dir'] / 'merge.lock')
    ctx['cond'] = threading.Condition()  # wait_for_overlap waits on it; run_lane notifies it
    threads = [threading.Thread(target=run_lane, args=(ctx, lane, lock), name=lane.name, daemon=True)
               for lane in ctx['lanes']]
    for k, th in enumerate(threads):
        if k and ctx['stagger'] > 0:  # a gap between lane starts: 16 sessions at once is how a plan limit is hit
            time.sleep(ctx['stagger'])
        th.start()
    for th in threads:
        th.join()
    close_lanes(ctx)  # after every join, never inside run_lane: no lane thread races a close
    text = report(ctx)
    print()
    print(text, end='')
    results = [r for lane in ctx['lanes'] for r in lane.results]
    ok = bool(results) and all(outcome == 'merged' for _, outcome, _ in results)
    return 0 if ok else 1


# ---------- sub-agent lanes: prep and land (T-0285) ----------

def subagent_name(tid):
    """The sub-agent name of a solo ticket: <ticket>-solo, so the host puts it on branch worktree-<name>."""
    return f'{tid}-solo'


def subagent_head(tid, title, tier, limit=50):
    """The first prompt line, at most 50 characters (T-0363, docs/references/subagent-list-style.md): `T-0153 harness coverage | solo L2`."""
    tail = f' | solo {tier}'
    room = limit - len(tid) - len(tail) - 1
    cut = title[:room] if room > 0 else ''
    if cut and len(title) > room and title[room] != ' ' and ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]
    cut = cut.strip(' ,.;:-')
    return f'{tid} {cut}{tail}' if cut else f'{tid}{tail}'


SOLO_SYNC = ('Base sha: {sha}. The host may make your worktree from origin/main, which can lack the claim commit: before anything else run '
             '`git merge --ff-only {sha}` in your worktree so the ticket folder is visible, and stop with a blocked report if it refuses.\n')


def subagent_dispatch(ctx, t, tier):
    """The Agent call for one solo ticket: a background sub-agent in its own worktree, told to commit `<id>: <title>`."""
    tier = solo_tier(tier)
    model, effort, _ = SOLO_TIERS[tier]
    name = subagent_name(t.id)
    handoff = (ctx['trel'] / t.slug / 'handoff.md').as_posix()
    base_sha = subprocess.run(['git', '-C', str(ctx['top']), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() or None
    verifier = None
    if tier in SOLO_VERIFIED:  # prepared against the sub-agent worktree once the solo reports; the level is the ticket's at prep
        verifier = ' '.join(shlex.quote(x) for x in (
            sys.executable, str(SCRIPTS / 'dispatch.py'), 'prepare', '--solo-model', model, 'verifier', solo_verifier(ctx['top'] / handoff),
            f'{HOST_WORKTREES}/{name}/{handoff}'))
    return {'subagent_type': f'sdlc-lite:solo-{tier}', 'name': name, 'description': ' '.join(([t.id, 'solo', tier] + t.title.split())[:5]),  # 3 to 5 words
            'model': model, 'effort': effort,
            'prompt': SOLO_SUBAGENT_PROMPT.format(head=subagent_head(t.id, t.title, tier), handoff=handoff, id=t.id, title=t.title,
                                                  sync=SOLO_SYNC.format(sha=base_sha) if base_sha else ''),
            'run_in_background': os.environ.get('SDLC_HEADLESS') != '1', 'isolation': 'worktree',
            'ticket': t.id, 'tier': tier, 'prune': False, 'branch': f'worktree-{name}', 'worktree': f'{HOST_WORKTREES}/{name}',
            'handoff': handoff, 'verifier': verifier,
            'base_sha': base_sha}


def write_solo_row(taskdir, tier):
    """Append the unpriced `role solo` row of a sub-agent lane to the ticket's runs.jsonl; returns its attempt_id (T-0331)."""
    import solo_run
    model, effort, _ = solo_run.TIERS[solo_run.tier_of(tier)]
    attempt = uuid.uuid4().hex
    rec = solo_run.build_record(tier, 'claude', model, effort, None, attempt, time.monotonic(), 0)
    rec.update(transport='subagent', cost_reason='subagent usage not priced', duration_ms=None, turns=None)
    solo_run.append(taskdir, rec)
    return attempt


def price_solo_row(taskdir, tier, transcript, tokens):
    """Price the lane's unpriced solo row from the sub-agent transcript (or notice tokens); the price, or None."""
    import solo_run
    f = pathlib.Path(taskdir) / 'runs.jsonl'
    if not f.is_file() or (not transcript and tokens is None):
        return None
    for line in reversed(f.read_text(encoding='utf-8').splitlines()):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get('role') == 'solo' and r.get('usage') is None and r.get('attempt_id'):
            return solo_run.complete(taskdir, r['attempt_id'], tier, transcript, tokens)
    return None


def land_command(ctx, branch, tid):
    """The `fanout.py land` command for one finished branch, pinning the run's integration branch, base, lanes dir and gates."""
    argv = [sys.executable, str(SCRIPTS / 'fanout.py'), 'land', branch, '--ticket', tid,
            '--integration', ctx['integration'], '--base', ctx['start'], '--lanes-dir', str(ctx['lanes_dir'])]
    if ctx['root'] != ctx['top'] / '.sdlc':
        argv += ['--root', os.path.relpath(ctx['root'], ctx['cwd'])]
    for g in ctx['gates']:
        argv += ['--gate', g]
    if ctx['allow_empty_gate']:
        argv.append('--allow-empty-gate')
    if ctx['rewrite_refs']:
        argv.append('--rewrite-refs')
    return ' '.join(shlex.quote(x) for x in argv)


def host_record_path(top, name):
    """<lanes root>/host/<name>.lane.json, the host lane record lanes.host_record writes (lanes root from .sdlc/config)."""
    return lanes.Ctx(str(top)).root / 'host' / f'{name}.lane.json'


def write_host_record(ctx, name, branch, tid, base=None):
    """Write the host lane record of a sub-agent lane (kind host, into the integration branch); its path, or why not."""
    try:
        lanes.host_record(name, branch=branch, into=ctx['integration'], tickets=[tid], base=base or ctx['start'],
                          cwd=str(ctx['top']))
        return str(host_record_path(ctx['top'], name))
    except (lanes.LaneError, OSError) as e:
        return f'not written ({e})'


def print_prep(ctx):
    """The prep plan: per ticket the lane, then the dispatch JSON of a solo ticket or the tree commands of a full one.
    Returns 4 when a ticket stops at the budget gate, else 0."""
    out = ['fanout prep (sub-agent lanes: creates only each solo ticket\'s <name>.dispatch.json, the record the spawn gate checks, '
           'and its host lane record <lanes root>/host/<name>.lane.json)']
    if ctx['reuse']:
        out.append(f"integration branch {ctx['integration']} exists at {ctx['start']}: land reuses it")
    else:
        out.append(f"base: {ctx['start']} ({ctx['base']})")
        out.append(f"integration branch: {ctx['integration']} (the first land creates it at the base)")
    out.append(f"integration worktree: {ctx['integ_dir']} (the first land creates it)")
    out.append(f"ticket root in each worktree: {ctx['rel'].as_posix()}")
    n_reg = sum(1 for x in ctx['lanes'] if not x.external)
    out.append(f"lane cap: {n_reg} lane(s) of at most {ctx['max_lanes']} (--max-lanes); stagger: {ctx['stagger']} s "
               f"between spawns (--stagger): the parent spaces its Agent calls")
    rc = 0
    for lane in ctx['lanes']:
        out.append(f'lane {lane.name}: its tickets run one after another; spawn the next after the previous one lands')
        for k, t in enumerate(lane.tickets):
            out.append(f'  {t.id} {t.slug}: {t.title}')
            taskdir = tickets.ticket_dir(ctx['root']) / t.slug
            kind, why = lane_decision(ctx, taskdir)
            tier = solo_tier(t.size) if kind == 'solo' else None
            if kind == 'solo' and tier is None:
                kind, why = 'full', f'size {t.size or "unset"} has no solo level'
            shown = f'solo, level {tier}: {solo_model_label(tier)}' if tier else kind
            out.append(f'    lane: {shown} ({why})')
            if tier:
                import solo_run  # same scripts/ dir: the budget gate a solo lane starts through
                hold = solo_run.budget_hold(taskdir)
                if hold:
                    out.append(f"    blocked: budget gate: budget.py ack (budget {hold['percent']}%: ask the user); no dispatch")
                    rc = 4
                    continue
                d = subagent_dispatch(ctx, t, tier)
                d['attempt_id'] = write_solo_row(taskdir, tier)  # the unpriced row `land --transcript` prices (T-0331)
                # The spawn gate (hooks/block-role-spawn.sh) finds this record beside the prompt's Handoff line (T-0326).
                (taskdir / f"{d['name']}.dispatch.json").write_text(
                    json.dumps({**d, 'role': 'solo', 'level': solo_run.TIERS[tier][2]}, indent=2) + '\n', encoding='utf-8')
                out.append(f"    branch: {d['branch']}; worktree: {d['worktree']} (host-made at the spawn)")
                out.append(f"    host record: {write_host_record(ctx, d['name'], d['branch'], t.id)}")
                out.append(f"    dispatch {t.id}:")
                out.append('\n'.join('    ' + ln for ln in json.dumps(d, indent=2).splitlines()))
                if d['verifier']:
                    out.append(f"    verifier (after the solo reports; commit its result on {d['branch']}): {d['verifier']}")
                out.append(f"    land: {land_command(ctx, d['branch'], t.id)}")
            else:
                tree = ctx['lanes_dir'] / lane.name
                out.append(f'    full: driven by the parent conductor, not a lane process (skills/fanout/SKILL.md): '
                           f'roles run as sub-agents against {tree}, each brief carrying `Tree: {tree}`')
                if k == 0:
                    out.append('    tree: ' + ' '.join(['python3', shlex.quote(str(SCRIPTS / 'lanes.py')), 'open', lane.name, '--kind', 'fanout']
                                                   + [x for tt in lane.tickets for x in ('--ticket', tt.id)]
                                                   + ['--base', ctx['start'], '--into', shlex.quote(ctx['integration']),
                                                      '--path', shlex.quote(str(tree)), '--branch', shlex.quote(lane.branch), '--no-claim']))
                else:
                    out.append(f"    sync: git -C {tree} merge --ff --no-edit {ctx['integration']}")
                out.append(f"    commit: git -C {tree} {LANE_ADD_SH[4:]} && git -C {tree} commit -m {shlex.quote(f'{t.id}: {t.title}')}")
                out.append(f"    land: {land_command(ctx, lane.branch, t.id)}")
    out += plan_overlap(ctx)
    if ctx['gates']:
        out += [f'gate {k}: {g}' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('gates: none given (merges will not be gated)')
    if deps_note(ctx):
        out.append(deps_note(ctx))
    out.append(f"logs: {ctx['logs']}")
    print('\n'.join(out))
    return rc


def cmd_prep(a):
    try:
        ctx = preflight(a)
        probe = git(ctx['top'], 'check-ignore', '-q', f'{HOST_WORKTREES}/x')
        if probe.returncode == 1:
            raise Refuse(f'{HOST_WORKTREES}/ is not gitignored: the host puts each sub-agent worktree there; add '
                         f'{HOST_WORKTREES}/ to .gitignore (and exclude it from watchers, as .worktrees/)')
        if probe.returncode:
            raise Refuse(f'git check-ignore {HOST_WORKTREES}/x failed: {probe.stderr.strip() or probe.returncode}')
        refuse_overlap(ctx)
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    sweep_lanes(ctx['top'])  # after every refusal, so a refused prep changes nothing
    return print_prep(ctx)


def branch_names(cwd, ref, prefix):
    """The file names directly under <prefix>/ at ref (git objects, no checkout); empty when ref or dir is missing."""
    p = git(cwd, 'ls-tree', '--name-only', ref, prefix + '/' if prefix != '.' else '')
    return {pathlib.PurePosixPath(x).name for x in p.stdout.splitlines() if x} if p.returncode == 0 else set()


def branch_verdict(ctx, ref, t, with_held=False):
    """'pass', 'fail', ... or None: the newest task-dir verifier result committed on ref that the integration branch
    does not hold yet (read from git objects into a temp dir, never from a tree). With with_held, the pair
    (verdict, held): held is the subjects or owners of a `fail` result's `deferred:` or `unmet-dependency:` note
    (steps.held_note, T-0408), else ''."""
    prefix = (ctx['trel'] / t.slug).as_posix()
    on_ref = branch_names(ctx['cwd'], ref, prefix)
    new = sorted(n for n in on_ref - branch_names(ctx['cwd'], ctx['integration'], prefix)
                 if re.fullmatch(r'verifier-L\d+(-\d+)?\.md', n))
    if not new:
        return (None, '') if with_held else None
    with tempfile.TemporaryDirectory() as td:
        for n in new + (['runs.jsonl'] if 'runs.jsonl' in on_ref else []):
            blob = git(ctx['cwd'], 'show', f'{ref}:{prefix}/{n}' if prefix != '.' else f'{ref}:{n}')
            if blob.returncode == 0:
                (pathlib.Path(td) / n).write_text(blob.stdout, encoding='utf-8')
        newest = newest_verifier(td, set(new))
        v = steps.verdict_or_none(newest) if newest else None
        return (v, steps.held_note(newest) if newest and v == 'fail' else '') if with_held else v


def record_solo_lane(taskdir, tier):
    """A solo delivery's lane record in its skips.md (with the skipped planner and filer), when none is recorded yet."""
    skips = pathlib.Path(taskdir) / 'skips.md'
    if skips.is_file() and re.search(r'(?m)^- lane: ', skips.read_text(encoding='utf-8')):
        return
    steps.record_lane(taskdir, 'solo', 'fanout land', [f'sub-agent lane: level {tier} ran as one solo sub-agent'])
    steps.write_solo_skips(taskdir, tier)


def host_branch_ticket(root, branch, m):
    """(ticket id, role) of the lane a host branch `worktree-agent-<agent_id>` belongs to, found through the agent_id
    in a runs.jsonl line of a ticket folder on the branch or in the tree; ('', '') when no record names that agent."""
    aid = m.group(1)
    for slug, meta in tickets.branch_tickets(root, branch):
        texts = []
        p = root / slug / 'runs.jsonl'
        if p.is_file():
            texts.append(p.read_text(encoding='utf-8', errors='replace'))
        rel = git_out(root, 'rev-parse', '--show-prefix').strip()
        q = git(root, 'show', f'refs/heads/{branch}:{rel}{slug}/runs.jsonl')
        if q.returncode == 0:
            texts.append(q.stdout)
        for text in texts:
            for ln in text.splitlines():
                try:
                    rec = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(rec, dict) and rec.get('agent_id') == aid:
                    return str(meta.get('id', '')), str(rec.get('role', ''))
    return '', ''


def land_lane_name(branch, tid):
    name = re.sub(r'[^a-z0-9]+', '-', re.sub(r'^worktree-', '', branch).lower()).strip('-')
    return name if name and LANE_RE.fullmatch(name) and name not in RESERVED else f'{tid.lower()}-land'


def branch_repo(a):
    """(cwd, top, root, rel, ticket dir, branch tip) for a land or roll of a.branch: the git work tree and --root
    checks and the branch's tip. Raises Refuse."""
    cwd = pathlib.Path.cwd()
    p = git(cwd, 'rev-parse', '--is-inside-work-tree')
    if p.returncode or p.stdout.strip() != 'true':
        raise Refuse('not a git repo: run fanout.py inside a git work tree with a commit')
    if git(cwd, 'rev-parse', '--verify', '-q', 'HEAD').returncode:
        raise Refuse('git repo has no commit: commit first')
    top = pathlib.Path(git_out(cwd, 'rev-parse', '--show-toplevel')).resolve()
    root = (cwd / a.root).resolve()
    try:
        rel = root.relative_to(top)
    except ValueError:
        raise Refuse(f'--root {a.root} is {root}, outside the git toplevel {top}')
    if not root.is_dir():
        raise Refuse(f'--root {a.root}: {root} is not a dir')
    try:
        tdir = tickets.ticket_dir(root)
    except tickets.Fail as e:
        raise Refuse(str(e))
    tip = git(cwd, 'rev-parse', '-q', '--verify', f'refs/heads/{a.branch}^{{commit}}')
    if tip.returncode:
        raise Refuse(f'{a.branch} is not a local branch with a commit')
    return cwd, top, root, rel, tdir, tip.stdout.strip()


def branch_ticket(a, root, branch):
    """(Ticket, lane kind, solo tier) for the ticket a finished branch delivers, read from git objects on the branch:
    from --ticket, a worktree-<id>-solo name, or a host worktree-agent-<id> branch's run record. Raises Refuse."""
    m = SUBAGENT_BRANCH.fullmatch(branch)
    hm = HOST_BRANCH.fullmatch(branch)
    host_tid, host_role = host_branch_ticket(root, branch, hm) if hm else ('', '')
    tid = norm_tid(a.ticket) if a.ticket else (norm_tid(m.group(1).upper()) if m else host_tid)
    if not tickets.ID_RE.fullmatch(tid):
        raise Refuse(f'cannot tell which ticket {branch} delivers: pass --ticket T-NNNN (a branch named '
                     f'worktree-<id>-solo carries it)')
    hits = [(s, mt) for s, mt in tickets.branch_tickets(root, branch) if mt.get('id') == tid]
    if not hits:
        raise Refuse(f'{tid}: no ticket on branch {branch} has this id')
    if len(hits) > 1:
        raise Refuse(f'{tid}: {len(hits)} folders share this id ({", ".join(s for s, _ in hits)})')
    slug, meta = hits[0]
    if meta.get('status') in ('done', 'dropped'):
        raise Refuse(f'{tid} ({slug}): status is {meta["status"]} on {branch}, nothing to land')
    t = Ticket(tid, slug, str(meta.get('title', '')), str(meta.get('size', '')))
    kind = a.lane
    if kind == 'auto':
        # fanout spawns only solo lanes as sub-agents, so a host branch worktree-agent-<id> is a solo lane unless a
        # record on it says another role: a solo sub-agent writes no runs.jsonl line, so no record is the usual case
        kind = 'solo' if m or (hm and (not host_role or (host_role == 'solo' and host_tid == tid))) else 'full'
    tier = solo_tier(t.size) if kind == 'solo' else None
    if kind == 'solo' and tier is None:
        kind = 'full'
    return t, kind, tier


def land_preflight(a):
    """Every check before any write for one `land <branch>`. Returns the run context; raises Refuse."""
    cwd, top, root, rel, tdir, tip = branch_repo(a)
    branch = a.branch
    integration = a.integration or f'fanout/{datetime.date.today().isoformat()}'
    if git(cwd, 'check-ref-format', '--branch', integration).returncode:
        raise Refuse(f'{integration!r} is not a valid branch name')
    if branch == integration:
        raise Refuse(f'{branch} is the integration branch; land a branch an agent worked on')
    t, kind, tier = branch_ticket(a, root, branch)
    tid = t.id

    refs = git_out(cwd, 'for-each-ref', '--format=%(refname)', 'refs/heads/').splitlines()
    reuse = ('refs/heads/' + integration) in refs
    if reuse:
        start = git_out(cwd, 'rev-parse', '--verify', f'refs/heads/{integration}^{{commit}}')
    else:
        clash = branch_clash(integration, refs)
        if clash:
            raise Refuse(f'integration branch {integration} clashes with the existing ref {clash}')
        base = a.base or 'HEAD'
        p = git(cwd, 'rev-parse', '--verify', '-q', f'{base}^{{commit}}')
        if p.returncode:
            raise Refuse(f'--base {base} is not a commit')
        start = p.stdout.strip()
    lanes_dir = resolve_lanes_dir(a, cwd, top)
    if lanes_dir.exists() and not lanes_dir.is_dir():
        raise Refuse(f'--lanes-dir {lanes_dir} exists and is not a dir')
    integ_dir = lanes_dir / 'integration'
    checked_out, wt_path = {}, None
    for line in git_out(cwd, 'worktree', 'list', '--porcelain').splitlines():
        if line.startswith('worktree '):
            wt_path = pathlib.Path(line[len('worktree '):]).resolve()
        elif line.startswith('branch refs/heads/'):
            checked_out[line[len('branch refs/heads/'):]] = wt_path
    where = checked_out.get(integration)
    if where is not None and where != integ_dir.resolve():
        raise Refuse(f'integration branch {integration} is checked out in {where}; land works in {integ_dir}')
    if integ_dir.exists() and where is None:
        raise Refuse(f'{integ_dir} exists but is not a worktree on {integration}; remove it with git worktree remove, '
                     f'or pass another --lanes-dir')
    lane = Lane(land_lane_name(branch, tid), [tid], branch)
    lane.branch, lane.tip, lane.tickets = branch, tip, [t]
    return {'lane_wt': checked_out.get(branch), 'cwd': cwd, 'top': top, 'root': root, 'rel': rel, 'trel': tdir.relative_to(top), 'lanes': [lane],
            'lane': lane, 'ticket': t, 'integration': integration, 'reuse': reuse, 'start': start, 'base': a.base or 'HEAD',
            'lanes_dir': lanes_dir, 'integ_dir': integ_dir, 'integ_exists': where is not None, 'logs': lanes_dir / 'logs',
            'gates': list(a.gate or []), 'driver': None, 'rewrite_refs': bool(a.rewrite_refs),
            'numbered': tickets.config_numbered(root), 'kinds': {tid: (kind, tier)}, 'land': True,
            'allow_empty_gate': bool(a.allow_empty_gate), 'gate_lock': not a.no_gate_lock and not gate_slots_off()}


def land_setup(ctx):
    """The integration branch and worktree for a land, created on the first land of a fanout and reused after."""
    cwd, integration, integ = ctx['cwd'], ctx['integration'], ctx['integ_dir']
    made_dir = not ctx['lanes_dir'].exists()
    made_branch = False
    try:
        ctx['lanes_dir'].mkdir(parents=True, exist_ok=True)
        if not ctx['reuse']:
            git_out(cwd, 'branch', integration, ctx['start'])
            made_branch = True
        if not ctx['integ_exists']:
            git_out(cwd, 'worktree', 'add', '-q', str(integ), integration)
        src_cfg = ctx['root'] / 'config'  # .sdlc/config is often untracked: a fresh worktree would read the defaults
        dst_cfg = integ / ctx['rel'] / 'config'
        if src_cfg.is_file() and not dst_cfg.exists() and dst_cfg.parent.is_dir():
            shutil.copyfile(str(src_cfg), str(dst_cfg))
        ctx['logs'].mkdir(parents=True, exist_ok=True)
    except BaseException:
        if not ctx['integ_exists']:
            git(cwd, 'worktree', 'remove', '--force', str(integ))
        if made_branch:
            git(cwd, 'branch', '-D', integration)
        git(cwd, 'worktree', 'prune')
        if made_dir:
            shutil.rmtree(ctx['lanes_dir'], ignore_errors=True)
        raise


def commit_lane_records(ctx, t):
    """T-0439: the verifier result and run records a driver left in the sub-agent worktree's ticket folder (ignored or
    untracked there) go onto the lane branch, so the merge carries them in: git add -f of the ticket folder without
    logs or lock files, then one commit of that folder only. Nothing when the branch has no worktree or no change."""
    wt = ctx.get('lane_wt')
    if not wt or not pathlib.Path(wt).is_dir():
        return
    folder = (ctx['trel'] / t.slug).as_posix()
    git(wt, 'add', '-f', '--', folder, ':(exclude,glob)**/*.log', ':(exclude,glob)**/.run.lock', ':(exclude,glob)**/*.running')
    if git(wt, 'diff', '--cached', '--quiet', '--', folder).returncode:
        git(wt, 'commit', '-q', '-m', f'{t.id}: run records', '--', folder)


def land_ticket(ctx, lock):
    """One finished branch through the external-lane merge: `no changes` when it adds nothing, the verifier verdict
    for a solo level L2 or L3, then the locked merge, gates, and close. Returns (outcome, commit)."""
    lane, t = ctx['lane'], ctx['ticket']
    ref = f'refs/heads/{lane.branch}'
    tip = git_out(ctx['cwd'], 'rev-parse', '--verify', f'{ref}^{{commit}}')
    p = git(ctx['cwd'], 'rev-list', '--count', f"{ctx['integration']}..{ref}")
    if p.returncode == 0 and p.stdout.strip() == '0':
        return 'no changes', tip[:7]
    commit_lane_records(ctx, t)
    tip = git_out(ctx['cwd'], 'rev-parse', '--verify', f'{ref}^{{commit}}')
    kind, tier = ctx['kinds'][t.id]
    if kind == 'solo' and tier in SOLO_VERIFIED:  # one independent batched verifier decides before any merge
        verdict, held = branch_verdict(ctx, ref, t, with_held=True)
        if verdict is None:
            return 'no verifier result (commit the verifier result on the branch, then land again)', tip[:7]
        if verdict != 'pass':
            return f'verifier {verdict}' + (f' (held {held}: not a defect, settle it in the owner stage)' if held else ''), tip[:7]
    return merge_gate_close(ctx, lane, t, lock, ref, tip[:7])


def read_journal(path):
    out = {}
    try:
        for ln in path.read_text(encoding='utf-8').splitlines():
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if isinstance(rec, dict) and rec.get('ticket'):
                out[rec['ticket']] = rec  # a later land of the same ticket replaces the earlier one
    except OSError:
        pass
    return out


def queue_prune(ctx, lane, t, tier):
    """T-0368: a merged solo's work has landed, so it is no longer resumable: queue it for pruning."""
    try:
        import dispatch  # same scripts/ dir
        dispatch.prune_add(str(ctx['top']), subagent_name(t.id), 'solo', tier or '')
        say(ctx, lane, t.id, f'prune: {subagent_name(t.id)}')
    except OSError as e:
        say(ctx, lane, t.id, f'prune queue not written: {e}')


def land_lanes(ctx, t, outcome):
    """After a land, outside the merge lock (T-0452). A merged branch checked out under .claude/worktrees/<leaf> whose leaf
    is not <id>-solo (the host names it agent-<agent_id>) gets its host record rebound to <leaf>, and the provisional
    <id>-solo record goes; that host lane stays open (dispatch.py prune --done closes it). A tree whose .lane.json is
    kind fanout is closed through lanes.close_lane after the record's last ticket merged. Returns the lines to print."""
    wt = ctx.get('lane_wt')
    if not wt or not pathlib.Path(wt).is_dir():
        return []
    top, wt = ctx['top'], pathlib.Path(wt)
    hosts = top / HOST_WORKTREES
    rec = lanes.read_json(wt / lanes.RECORD) or {}
    if lanes.under(wt, hosts) and not lanes.samepath(wt, hosts):
        name = subagent_name(t.id)
        if outcome != 'merged' or wt.name == name:
            return []
        prov = host_record_path(top, name)
        old = lanes.read_json(prov) or {}
        got = write_host_record(ctx, wt.name, ctx['lane'].branch, t.id, base=old.get('base_sha') or old.get('base'))
        if got.startswith('not written'):
            return [f'host record: {got}']
        with contextlib.suppress(OSError):
            prov.unlink()
        return [f'host record: {got} (rebound from {prov.name})']
    tids = rec.get('tickets') or []
    if rec.get('kind') != 'fanout' or not tids or tids[-1] != t.id:
        return []
    if outcome != 'merged':
        return [f'lane still open: {wt} ({outcome})']
    try:
        r = lanes.close_lane(str(wt), into=ctx['integration'], cwd=str(top))
    except lanes.LaneError as e:
        r = dict(rc=1, message=str(e))
    if r['rc']:
        return [f"lane still open: {wt} ({first_line(r['message'], 'rc=%s' % r['rc'])})"]
    return r['message'].splitlines()


def cmd_land(a):
    try:
        ctx = land_preflight(a)
        land_setup(ctx)
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    ctx['run_id'] = 'fanout-' + uuid.uuid4().hex[:12]
    ctx['cond'] = threading.Condition()
    lane, t = ctx['lane'], ctx['ticket']
    kind, tier = ctx['kinds'][t.id]
    say(ctx, lane, t.id, f'land {lane.branch} (lane {kind}' + (f' level {tier}' if tier else '') + ')')
    if kind == 'solo' and tier and (a.transcript or a.tokens is not None):
        cost = price_solo_row(ctx['root'] / t.slug, tier, a.transcript, a.tokens)
        say(ctx, lane, t.id, 'solo row priced $%.4f (estimate)' % cost if cost is not None else 'solo row not priced (no unpriced row or no usage)')
    try:
        outcome, commit = land_ticket(ctx, MergeLock(ctx['lanes_dir'] / 'merge.lock'))
    except Exception as e:  # a git or IO failure mid-land: record it
        outcome, commit = f'error: {first_line(str(e), type(e).__name__)}', ''
    lane.results.append((t.id, outcome, commit))
    say(ctx, lane, t.id, outcome)
    if kind == 'solo' and outcome == 'merged':
        queue_prune(ctx, lane, t, tier)
    try:
        closes = land_lanes(ctx, t, outcome)  # the merge lock is released here
    except Exception as e:  # a lane record or close failure never changes the land outcome
        closes = [f'lane still open: {ctx.get("lane_wt")} (error: {first_line(str(e), type(e).__name__)})']
    journal = ctx['logs'] / 'land.jsonl'
    with open(journal, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'run_id': ctx['run_id'], 'lane': lane.name, 'branch': lane.branch, 'ticket': t.id,
                            'outcome': outcome, 'commit': commit, 'kind': kind, 'tier': tier,
                            'files': sorted(lane.files)}) + '\n')
    prior = read_journal(journal)  # report every ticket landed so far in this lanes dir, the latest outcome each
    lanes, kinds = [], {}
    for tid, rec in prior.items():
        ln = lane if tid == t.id else Lane(rec['lane'], [tid], rec['branch'])
        ln.branch, ln.results, ln.files = rec['branch'], [(tid, rec['outcome'], rec['commit'])], set(rec.get('files') or [])
        lanes.append(ln)
        kinds[tid] = (rec['kind'], solo_tier(rec['tier']) if rec.get('tier') else None)  # a 0.21.x journal holds S, M, L
    ctx['lanes'], ctx['kinds'] = lanes, kinds
    text = report(ctx)
    print()
    print(text, end='')
    for ln in closes:
        print(ln)
    return 0 if outcome == 'merged' else 1


# ---------- roll (T-0374): a rolling lane lands on main at once ----------

def branch_base(ctx, ref, t):
    """The lane's recorded base sha, read from git objects on ref in the order the ledger reads a lane tree: the task
    dir's base-sha, else a solo *.dispatch.json base_sha; '' when neither is committed (the lane is then based at its
    fork point from main, an ancestor by construction)."""
    prefix = (ctx['trel'] / t.slug).as_posix()

    def show(name):
        q = git(ctx['cwd'], 'show', f'{ref}:{prefix}/{name}' if prefix != '.' else f'{ref}:{name}')
        return q.stdout if q.returncode == 0 else ''

    words = show('base-sha').split()
    if words:
        return words[0]
    for name in sorted(n for n in branch_names(ctx['cwd'], ref, prefix) if n.endswith('.dispatch.json')):
        try:
            rec = json.loads(show(name))
            sha = str(rec.get('base_sha') or '').strip() if rec.get('role') == 'solo' else ''
        except (ValueError, AttributeError):
            sha = ''
        if sha:
            return sha
    return ''


def roll_preflight(a):
    """Every check before any write for one `roll <branch>`. Returns the run context; raises Refuse."""
    cwd, top, root, rel, tdir, tip = branch_repo(a)
    wts, wt_path = [], None  # (path, branch or None) per `git worktree list` entry, the main worktree first
    for line in git_out(cwd, 'worktree', 'list', '--porcelain').splitlines():
        if line.startswith('worktree '):
            wt_path = pathlib.Path(line[len('worktree '):]).resolve()
            wts.append([wt_path, None])
        elif line.startswith('branch refs/heads/') and wts:
            wts[-1][1] = line[len('branch refs/heads/'):]
    main = a.main or (wts[0][1] if wts else None)
    if not main:
        raise Refuse('the main worktree is on no branch: pass --main BRANCH')
    if git(cwd, 'rev-parse', '-q', '--verify', f'refs/heads/{main}^{{commit}}').returncode:
        raise Refuse(f'main branch {main} is not a local branch with a commit')
    if a.branch == main:
        raise Refuse(f'{a.branch} is main; roll a branch an agent worked on')
    t, kind, tier = branch_ticket(a, root, a.branch)
    lanes_dir = resolve_lanes_dir(a, cwd, top)
    if lanes_dir.exists() and not lanes_dir.is_dir():
        raise Refuse(f'--lanes-dir {lanes_dir} exists and is not a dir')
    roll_dir = lanes_dir / 'rolling'
    registered = any(w == roll_dir.resolve() for w, _ in wts)
    if roll_dir.exists() and not registered:
        raise Refuse(f'{roll_dir} exists but is not a worktree; remove it with git worktree remove, or pass another '
                     f'--lanes-dir')
    lane = Lane(land_lane_name(a.branch, t.id), [t.id], a.branch)
    lane.branch, lane.tip, lane.tickets = a.branch, tip, [t]
    return {'cwd': cwd, 'top': top, 'root': root, 'rel': rel, 'trel': tdir.relative_to(top), 'lanes': [lane],
            'lane': lane, 'ticket': t, 'integration': main, 'main': main,
            'main_wt': next((w for w, b in wts if b == main), None), 'lanes_dir': lanes_dir, 'integ_dir': roll_dir,
            'roll_exists': registered, 'logs': lanes_dir / 'logs', 'gates': list(a.gate or []), 'driver': None,
            'rewrite_refs': bool(a.rewrite_refs), 'numbered': tickets.config_numbered(root), 'kinds': {t.id: (kind, tier)},
            'land': True, 'roll': True, 'globs': tickets.hash_bound_globs(root),
            'allow_empty_gate': bool(a.allow_empty_gate), 'gate_lock': not a.no_gate_lock and not gate_slots_off()}


def roll_setup(ctx):
    """The scratch worktree <lanes-dir>/rolling, detached at main's tip: made on the first roll and reused after."""
    cwd, roll = ctx['cwd'], ctx['integ_dir']
    made_dir = not ctx['lanes_dir'].exists()
    try:
        ctx['lanes_dir'].mkdir(parents=True, exist_ok=True)
        if not ctx['roll_exists']:
            git_out(cwd, 'worktree', 'add', '-q', '--detach', str(roll), f"refs/heads/{ctx['main']}")
        src_cfg = ctx['root'] / 'config'  # as land_setup: an untracked .sdlc/config would read as the defaults
        dst_cfg = roll / ctx['rel'] / 'config'
        if src_cfg.is_file() and not dst_cfg.exists() and dst_cfg.parent.is_dir():
            shutil.copyfile(str(src_cfg), str(dst_cfg))
        ctx['logs'].mkdir(parents=True, exist_ok=True)
    except BaseException:
        if not ctx['roll_exists']:
            git(cwd, 'worktree', 'remove', '--force', str(roll))
        git(cwd, 'worktree', 'prune')
        if made_dir:
            shutil.rmtree(ctx['lanes_dir'], ignore_errors=True)
        raise


def roll_ticket(ctx, lock):
    """One finished branch onto main, all under the merge lock: `no changes`, then the merge class from git objects
    on the branch (steps.merge_class), and for a rolling lane the merge, gates and close in the scratch worktree at
    main's tip (merge_gate_close), then main fast-forwards to it. Returns (outcome, commit)."""
    lane, t, cwd, roll, main = ctx['lane'], ctx['ticket'], ctx['cwd'], ctx['integ_dir'], ctx['main']
    ref = f'refs/heads/{lane.branch}'
    with lock:
        tip = git_out(cwd, 'rev-parse', '--verify', f'{ref}^{{commit}}')
        old = git_out(cwd, 'rev-parse', '--verify', f'refs/heads/{main}^{{commit}}')
        p = git(cwd, 'rev-list', '--count', f'{old}..{ref}')
        if p.returncode == 0 and p.stdout.strip() == '0':
            return 'no changes', tip[:7]
        base = branch_base(ctx, ref, t)
        stale = base if base and git(cwd, 'merge-base', '--is-ancestor', base, old).returncode else ''
        hits = steps.declared_hits(ctx['top'], ctx['globs'], f'{old}...{ref}')
        verdict, held = branch_verdict(ctx, ref, t, with_held=True)  # the verdict: results main lacks
        cls, why = steps.merge_class(verdict, stale, hits, held)
        say(ctx, lane, t.id, f'merge class: {cls}' + (f' ({why})' if why else ''))
        if cls != 'rolling':
            return f'integration ({why}): land it through the integration branch (fanout.py land)', tip[:7]
        p = git(roll, 'status', '--porcelain', '--untracked-files=no')
        if p.returncode or p.stdout.strip():
            return f'rolling dirty: {(p.stdout.splitlines() or [first_line(p.stderr, "status failed")])[0][3:]}', tip[:7]
        git_out(roll, 'checkout', '-q', '--detach', old)
        outcome, commit = merge_gate_close(ctx, lane, t, contextlib.nullcontext(), ref, tip[:7])
        if outcome != 'merged':
            return outcome, commit
        new = git_out(roll, 'rev-parse', 'HEAD')
        if ctx['main_wt'] is not None:  # git refuses itself when a local change or untracked file would be overwritten
            p = git(ctx['main_wt'], 'merge', '--ff-only', '-q', new)
        else:
            p = git(cwd, 'update-ref', f'refs/heads/{main}', new, old)
        if p.returncode:
            return f'main not advanced: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', new[:7]
        return 'merged', commit


def cmd_settle(a):
    """Bring a landed integration branch back into the checkout it was cut from and retire it (T-0438, T-0452): fast-forward
    the current branch to it (nothing to do when it is already merged, as after a hand merge), then close its worktree
    through lanes.close_lane, which writes refs/archive/<UTC date>/<branch> before it removes the tree and deletes the
    branch. A branch that is neither merged nor a fast-forward is refused (exit 2) and left whole; a close that refuses
    (not a plugin lane, lanes still open into it, no worktree) prints `lane still open: <path or branch> (<outcome>)`,
    keeps the branch and exits 1. Local only, never a push."""
    cwd = pathlib.Path.cwd()
    try:
        if git(cwd, 'rev-parse', '--verify', '-q', f'refs/heads/{a.integration}').returncode:
            print(f'settle: no branch {a.integration}: nothing to settle')
            return 0
        head = git_out(cwd, 'symbolic-ref', '--short', '-q', 'HEAD')
        if git(cwd, 'merge-base', '--is-ancestor', a.integration, 'HEAD').returncode:
            p = git(cwd, 'merge', '--ff-only', a.integration)
            if p.returncode:
                raise Refuse(f'{a.integration} is not a fast-forward of {head}: {(p.stderr or p.stdout).strip().splitlines()[0] if (p.stderr or p.stdout).strip() else p.returncode}; '
                             f'stop with state written, the branch is kept')
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    wt, cur = None, None
    for line in git_out(cwd, 'worktree', 'list', '--porcelain').splitlines():
        if line.startswith('worktree '):
            cur = line[len('worktree '):]
        elif line == f'branch refs/heads/{a.integration}':
            wt = cur
    if wt is None:
        print(f'lane still open: {a.integration} (no worktree)')
        return 1
    try:
        r = lanes.close_lane(wt, into=head or 'HEAD', cwd=str(cwd))
    except lanes.LaneError as e:
        r = dict(rc=1, message=str(e))
    if r['rc']:
        print(f"lane still open: {wt} ({first_line(r['message'], 'rc=%s' % r['rc'])})")
        return 1
    print(r['message'])
    print(f'settled: {a.integration} is in {head or "HEAD"}; its worktree and branch are removed (archive {r.get("archive")})')
    return 0


def cmd_roll(a):
    try:
        ctx = roll_preflight(a)
        roll_setup(ctx)
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    try:
        ctx['run_id'] = 'fanout-' + uuid.uuid4().hex[:12]
        ctx['cond'] = threading.Condition()
        lane, t = ctx['lane'], ctx['ticket']
        kind, tier = ctx['kinds'][t.id]
        say(ctx, lane, t.id, f"roll {lane.branch} onto {ctx['main']} (lane {kind}" + (f' level {tier}' if tier else '') + ')')
        try:
            outcome, commit = roll_ticket(ctx, MergeLock(ctx['lanes_dir'] / 'merge.lock'))
        except Exception as e:  # a git or IO failure mid-roll: report it
            outcome, commit = f'error: {first_line(str(e), type(e).__name__)}', ''
        say(ctx, lane, t.id, outcome)
        if outcome == 'merged':
            say(ctx, lane, t.id, f"{ctx['main']} at {git(ctx['cwd'], 'rev-parse', '--short', 'refs/heads/' + ctx['main']).stdout.strip()} "
                                 f'(merge {commit})')
            if kind == 'solo':
                queue_prune(ctx, lane, t, tier)
        return 0 if outcome == 'merged' else 1
    finally:  # T-0452: the detached scratch holds no branch; roll_setup makes it again on the next roll
        git(ctx['cwd'], 'worktree', 'remove', '--force', str(ctx['integ_dir']))
        git(ctx['cwd'], 'worktree', 'prune')


# ---------- selftest ----------

STUB = r'''#!/usr/bin/env bash
set -eu
[ "${SDLC_HEADLESS:-}" = 1 ] || { echo "SDLC_HEADLESS not set" >&2; exit 1; }
[ "${SDLC_ROLE:-}" = conductor ] || { echo "SDLC_ROLE not conductor" >&2; exit 1; }
[ "${BASH_DEFAULT_TIMEOUT_MS:-}" = 3600000 ] || { echo "BASH_DEFAULT_TIMEOUT_MS not 3600000" >&2; exit 1; }
[ "${BASH_MAX_TIMEOUT_MS:-}" = 3600000 ] || { echo "BASH_MAX_TIMEOUT_MS not 3600000" >&2; exit 1; }
echo "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"
ls >"$FANOUT_TICKET.saw"
printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"
if [ "$FANOUT_TICKET" = T-0003 ]; then touch RED; fi
if [ "$FANOUT_TICKET" = T-0002 ]; then
  i=0
  until git cat-file -e "$FANOUT_INTEGRATION:T-0001.txt" 2>/dev/null; do
    i=$((i + 1))
    [ "$i" -le 600 ] || { echo "timed out waiting for T-0001.txt on $FANOUT_INTEGRATION" >&2; exit 1; }
    sleep 0.1
  done
fi
'''

# A driver that leaves a dead-owner run.sh tmp prefix in the lane, as a SIGKILLed last role run would.
REAP_STUB = r'''#!/usr/bin/env bash
set -eu
git worktree add -q --detach "$PWD/.worktrees/tmp/builder-$DEADPID/w" HEAD
echo "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"
printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"
'''

# Case 13: alpha (T-0001) and beta (T-0002) edit far-apart lines of one root file. Alpha's driver holds
# until beta logs its wait on alpha, so the run only merges both when fanout makes beta wait for alpha.
# Files are rewritten through a temp file and mv, never sed -i (macOS and GNU sed differ).
OVERLAP_STUB = r'''#!/usr/bin/env bash
set -eu
printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"
if [ "$FANOUT_TICKET" = T-0001 ]; then
  { echo 'top alpha'; tail -n +2 shared.txt; } >shared.txt.tmp
  mv shared.txt.tmp shared.txt
  i=0
  until grep -qF '[beta] T-0002 waiting for lane alpha (overlap: shared.txt)' ../logs/fanout.log 2>/dev/null; do
    i=$((i + 1))
    [ "$i" -le 600 ] || { echo "timed out waiting for beta to log its wait on alpha" >&2; exit 1; }
    sleep 0.1
  done
fi
if [ "$FANOUT_TICKET" = T-0002 ]; then
  i=0
  until [ "$(head -n 1 ../alpha/shared.txt 2>/dev/null)" = 'top alpha' ]; do
    i=$((i + 1))
    [ "$i" -le 600 ] || { echo "timed out waiting for top alpha in ../alpha/shared.txt" >&2; exit 1; }
    sleep 0.1
  done
  { sed '$d' shared.txt; echo 'bottom beta'; } >shared.txt.tmp
  mv shared.txt.tmp shared.txt
fi
'''


def selftest():
    misses = []
    ENV['SDLC_CLAUDE_EXEC'] = '1'  # T-0361: ENV was copied at import, lane subprocesses read it
    os.environ['SDLC_CLAUDE_EXEC'] = '1'  # T-0288: the legacy Claude driver stays testable; case 15 checks the refusal without it

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def sh(cwd, *args):
        return subprocess.run(['git', '-C', str(cwd), *args], env=ENV, capture_output=True, text=True)

    def archived(repo, branch):
        """The refs/archive/<date>/<branch> ref lanes.py wrote when the run closed that lane, else ''."""
        refs = sh(repo, 'for-each-ref', '--format=%(refname)', 'refs/archive/').stdout.split()
        return next((r for r in refs if r.split('/', 3)[-1] == branch), '')

    # T-0331: prep writes an unpriced solo row; land --transcript prices it (negative control: no usage prices nothing)
    with tempfile.TemporaryDirectory() as t331:
        td = pathlib.Path(t331)
        (td / 'handoff.md').write_text('---\nid: T-0001\n---\n', encoding='utf-8')
        aid = write_solo_row(td, 'L1')
        row = json.loads((td / 'runs.jsonl').read_text().splitlines()[-1])
        expect('T-0331 prep writes an unpriced solo row', row.get('role') == 'solo' and row.get('usage') is None and row.get('attempt_id') == aid)
        expect('T-0331 negative control: no transcript or tokens prices nothing', price_solo_row(td, 'L1', None, None) is None)
        tr = td / 'tr.jsonl'
        tr.write_text(json.dumps({'message': {'id': 'm', 'usage': {'input_tokens': 6, 'output_tokens': 847,
                      'cache_read_input_tokens': 58134, 'cache_creation_input_tokens': 32972}}}) + '\n', encoding='utf-8')
        cost = price_solo_row(td, 'S', str(tr), None)  # ALIAS_OK: a 0.21.x tier name still prices the row
        row = json.loads((td / 'runs.jsonl').read_text().splitlines()[-1])
        expect('T-0331 land prices the solo row from the transcript', cost and row.get('cost_usd') == cost and row.get('cost_estimated') is True)

    def make_repo(repo, specs, extra=None):
        (repo / '.sdlc').mkdir(parents=True)
        for name, body in (extra or {}).items():
            (repo / name).write_text(body, encoding='utf-8')
        for slug, tid, status in specs:
            (repo / '.sdlc' / slug).mkdir()
            (repo / '.sdlc' / slug / 'handoff.md').write_text(
                f'---\nid: {tid}\ntitle: "Ticket {slug}"\ntype: chore\nstatus: {status}\nsize: S\n'
                f'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\n{slug}\n', encoding='utf-8')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(repo, *args)
            expect(f'fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)

    def gate_env(**extra):
        # a private SDLC_GATE_DIR gives every run a private gate_lock state root (and a private TMPDIR its
        # legacy slot dir), and a gate-locked caller's own SDLC_GATE_* (this selftest may run inside
        # gate_lock.py) must not leak in
        env = {k: v for k, v in ENV.items() if not k.startswith('SDLC_GATE_')}
        env['TMPDIR'] = str(gate_tmp)
        env['SDLC_GATE_DIR'] = str(gate_tmp / 'gate-state')
        env.update(extra)
        return env

    def fanout(cwd, *args, **extra_env):
        if not any(x == '--stagger' for x in args):
            args = (*args, '--stagger', '0')  # the default 20 s gap would slow every case
        return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', *args],
                              cwd=str(cwd), env=gate_env(**extra_env), capture_output=True, text=True, timeout=300)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp).resolve()
        gate_tmp = tmp / 'gate-tmp'
        gate_tmp.mkdir()

        # 1. Two lanes, a stub driver, a gate that goes red on T-0003.
        repo, lanes = tmp / 'repo', tmp / 'lanes'
        # .worktrees/ is ignored: lanes.py open takes its flock at <toplevel>/.worktrees/lanes.lock
        make_repo(repo, [(s, f'T-000{i}', 'ready') for i, s in enumerate('abcde', 1)], {'.gitignore': '.worktrees/\n'})
        stub = tmp / 'stub.sh'
        stub.write_text(STUB)
        stub.chmod(0o755)
        main0 = sh(repo, 'rev-parse', 'main').stdout.strip()
        proc = fanout(repo, 'alpha=T-0001,T-0003,T-0005', 'beta=T-0002,T-0004', '--base', 'main',
                      '--integration', 'fanout/test', '--lanes-dir', str(lanes), '--driver', shlex.quote(str(stub)),
                      '--gate', 'test ! -e RED')
        ran = f'(stdout={proc.stdout!r} stderr={proc.stderr!r})'
        expect(f'run exits 1 (T-0003 red, T-0005 skipped), got {proc.returncode} {ran}', proc.returncode == 1)
        expect('main sha unchanged', sh(repo, 'rev-parse', 'main').stdout.strip() == main0 and main0)
        expect('the repo still has main checked out',
               sh(repo, 'symbolic-ref', 'HEAD').stdout.strip() == 'refs/heads/main')
        status = sh(repo, 'status', '--porcelain')
        expect(f'git status --porcelain empty in the repo, got {status.stdout!r}',
               status.returncode == 0 and status.stdout == '')
        merges = sh(repo, 'rev-list', '--merges', '--count', 'fanout/test').stdout.strip()
        expect(f'fanout/test has exactly three merge commits, got {merges!r}', merges == '3')
        for f in ('T-0001.txt', 'T-0002.txt', 'T-0004.txt'):
            expect(f'fanout/test holds {f}', sh(repo, 'cat-file', '-e', f'fanout/test:{f}').returncode == 0)
        for f in ('T-0003.txt', 'RED'):
            expect(f'fanout/test does not hold {f} (the red merge was reset)',
                   sh(repo, 'cat-file', '-e', f'fanout/test:{f}').returncode != 0)
        for slug, want in (('a', 'done'), ('b', 'done'), ('c', 'ready'), ('d', 'done'), ('e', 'ready')):
            shown = sh(repo, 'show', f'fanout/test:.sdlc/{slug}/handoff.md')
            expect(f'fanout/test:.sdlc/{slug}/handoff.md says status: {want}, got {shown.stdout[:120]!r}',
                   shown.returncode == 0 and re.search(rf'^status: {want}\b', shown.stdout, re.M))
        rows = {}
        rep = lanes / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        for line in text.splitlines():
            c = [x.strip() for x in line.strip('|').split('|')]
            if line.startswith('| ') and len(c) == 4 and tickets.ID_RE.fullmatch(c[1]):
                rows[c[1]] = (c[0], c[2])
        expect(f'report rows for all five tickets, got {rows}', len(rows) == 5)
        for tid, lane in (('T-0001', 'alpha'), ('T-0002', 'beta'), ('T-0004', 'beta')):
            expect(f'report: {tid} merged in {lane}, got {rows.get(tid)}', rows.get(tid) == (lane, 'merged'))
        expect(f'report: T-0003 red, got {rows.get("T-0003")}',
               rows.get('T-0003', ('', ''))[1].startswith('red: test ! -e RED rc='))
        expect(f'report: T-0005 skipped, got {rows.get("T-0005")}', rows.get('T-0005') == ('alpha', 'skipped'))
        expect('the report was printed', 'fanout report' in proc.stdout and '| alpha | T-0005 | skipped |' in proc.stdout)
        expect('alpha worktree kept, holding its red T-0003.txt', (lanes / 'alpha' / 'T-0003.txt').is_file())
        expect('alpha stopped after T-0003: no T-0005.txt in the alpha worktree',
               (lanes / 'alpha').is_dir() and not (lanes / 'alpha' / 'T-0005.txt').exists())
        seen = sh(repo, 'show', 'fanout/test:T-0004.saw').stdout.split()  # beta merged both tickets, so the run closed it
        expect(f'T-0004.saw from beta (lane closed, read on fanout/test) lists T-0001.txt (synced before the ticket), '
               f'got {seen}', 'T-0001.txt' in seen)
        expect('beta merged every ticket: the run closed it (tree gone, branch archived)',
               not (lanes / 'beta').exists() and archived(repo, 'fanout/test-beta')
               and sh(repo, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/test-beta').returncode != 0)
        board = subprocess.run([sys.executable, str(SCRIPTS / 'board.py'), '--lanes', '--root', str(repo / '.sdlc')],
                               env=ENV, capture_output=True, text=True)
        cells = {}
        for line in board.stdout.splitlines():
            c = [x.strip() for x in line.strip('|').split('|')]
            if line.startswith('| ') and len(c) >= 3:
                cells[c[0]] = c[1]
        expect(f'board.py --lanes exits 0, got {board.returncode} stderr={board.stderr!r}', board.returncode == 0)
        expect(f'board.py --lanes lists alpha on fanout/test-alpha, got {cells}', cells.get('alpha') == 'fanout/test-alpha')
        expect(f'board.py --lanes no longer lists beta (lane closed), got {cells}', 'beta' not in cells)

        # 2. --dry-run and refusals create nothing.
        rr, rl = tmp / 'refuse', tmp / 'rlanes'
        make_repo(rr, [('x', 'T-0001', 'ready'), ('y', 'T-0002', 'done')], {'.gitignore': '.worktrees/\n'})
        default_lanes = rr / '.worktrees' / 'fanout'
        proc = fanout(rr, '--dry-run', '--integration', 'fanout/dry', 'alpha=T-0001')
        expect(f'--dry-run exits 0 naming the lane branch and the default lanes dir under .worktrees/fanout, '
               f'got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'fanout/dry-alpha' in proc.stdout
               and f'integration worktree: {default_lanes / "integration"}' in proc.stdout
               and f'worktree {default_lanes / "alpha"}' in proc.stdout)
        proc = fanout(rr, '--dry-run', '--lanes-dir', str(rl), 'alpha=T-0001')
        expect(f'--dry-run with --lanes-dir exits 0, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0 and str(rl) in proc.stdout)
        for label, args in (('the same id in two lanes', ('alpha=T-0001', 'beta=T-0001')),
                            ('the same id bare and prefixed', ('alpha=0001', 'beta=T-0001')),
                            ('an unknown id', ('alpha=T-0009',)),
                            ('a done ticket', ('alpha=T-0002',))):
            # a no-op driver: if a refusal regresses, the run must never reach the default claude driver
            proc = fanout(rr, '--lanes-dir', str(rl), '--driver', 'exit 3', *args)
            expect(f'{label} exits 2 with a reason, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 2 and proc.stderr.strip() and 'Traceback' not in proc.stderr)
        outs = [fanout(rr, '--dry-run', '--lanes-dir', str(rl), f'alpha={v}') for v in ('T-0001', '0001', '1')]
        expect('bare 0001, 1 and T-0001 resolve the same ticket in a dry run: '
               f'{[(o.returncode, o.stderr) for o in outs]}',
               all(o.returncode == 0 for o in outs) and outs[0].stdout == outs[1].stdout == outs[2].stdout)
        proc = fanout(rr, '--lanes-dir', str(rl), '--driver', 'exit 3', 'alpha=0001', 'beta=T-0001')
        expect(f'alpha=0001 beta=T-0001 refuses as twice listed, got {proc.returncode} {proc.stderr!r}',
               proc.returncode == 2 and 'T-0001 appears in lane alpha and lane beta' in proc.stderr)
        expect('dry run and refusals create no fanout/* branch',
               sh(rr, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        expect('dry run and refusals add no worktree',
               len([ln for ln in sh(rr, 'worktree', 'list').stdout.splitlines() if ln.strip()]) == 1)
        expect('dry run and refusals create no lanes dir', not rl.exists() and not default_lanes.exists())
        expect('dry run and refusals leave the status clean', sh(rr, 'status', '--porcelain').stdout == '')

        # 3. A repo that does not ignore .worktrees/ refuses the default lanes dir, creating nothing.
        ru = tmp / 'unignored'
        make_repo(ru, [('x', 'T-0001', 'ready')])
        proc = fanout(ru, '--dry-run', 'alpha=T-0001')
        expect(f'unignored .worktrees/: default-dir --dry-run exits 2 naming .gitignore and .worktrees/, '
               f'got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 2 and '.gitignore' in proc.stderr and '.worktrees/' in proc.stderr
               and 'Traceback' not in proc.stderr)
        expect('unignored .worktrees/: no .worktrees dir created', not (ru / '.worktrees').exists())
        expect('unignored .worktrees/: no fanout/* branch', sh(ru, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        expect('unignored .worktrees/: no worktree added',
               len([ln for ln in sh(ru, 'worktree', 'list').stdout.splitlines() if ln.strip()]) == 1)

        # 4. Numbered mode, a file outside the ticket root citing the ticket folder: without
        # --rewrite-refs the close is refused; with it the close commit carries the rewrite.
        numbered_stub = ('printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" '
                         '> "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo x > x.txt')

        def make_numbered(repo):
            (repo / '.sdlc' / '0001-x').mkdir(parents=True)
            (repo / 'docs').mkdir()
            (repo / '.sdlc' / 'config').write_text('ticket_folders: numbered\n', encoding='utf-8')
            (repo / '.sdlc' / '0001-x' / 'handoff.md').write_text(
                '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
                'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n', encoding='utf-8')
            (repo / 'docs' / 'spec.md').write_text('see .sdlc/0001-x/handoff.md\n', encoding='utf-8')
            (repo / '.gitignore').write_text('.worktrees/\n', encoding='utf-8')
            for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                         ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                         ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
                q = sh(repo, *args)
                expect(f'numbered fixture git {args} exited 0, got {q.returncode}', q.returncode == 0)

        def outcome(repo):
            rep = repo / '.worktrees' / 'fanout' / 'report.md'
            for line in (rep.read_text() if rep.is_file() else '').splitlines():
                c = [x.strip() for x in line.strip('|').split('|')]
                if line.startswith('| ') and len(c) == 4 and c[1] == 'T-0001':
                    return c[2]
            return None

        integ_clean = lambda repo: sh(repo / '.worktrees' / 'fanout' / 'integration', 'status', '--porcelain').stdout == ''
        nr = tmp / 'numbered-off'
        make_numbered(nr)
        proc = fanout(nr, '--dry-run', 'a=T-0001')
        expect(f'numbered dry run without the flag names the refusal, got {proc.stdout!r}',
               proc.returncode == 0 and '\nclose: tickets.py close <slug> (numbered folders' in proc.stdout)
        proc = fanout(nr, '--dry-run', '--rewrite-refs', 'a=T-0001')
        expect(f'dry run with the flag shows it, got {proc.stdout!r}',
               proc.returncode == 0 and '\nclose: tickets.py close <slug> --rewrite-refs' in proc.stdout)
        proc = fanout(nr, 'a=T-0001', '--integration', 'fanout/t', '--driver', numbered_stub)
        got = outcome(nr) or ''
        expect(f'numbered without the flag exits 1, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 1)
        expect(f'numbered without the flag: merged, close refused naming --rewrite-refs, got {got!r}',
               got.startswith('merged, close refused') and '--rewrite-refs' in got)
        shown = sh(nr, 'show', 'fanout/t:.sdlc/0001-x/handoff.md').stdout
        expect(f'numbered without the flag: 0001-x still ready, got {shown[:120]!r}',
               re.search(r'^status: ready\b', shown, re.M))
        expect('numbered without the flag: integration worktree clean', integ_clean(nr))

        nw = tmp / 'numbered-on'
        make_numbered(nw)
        proc = fanout(nw, 'a=T-0001', '--integration', 'fanout/t', '--rewrite-refs', '--driver', numbered_stub)
        expect(f'numbered with the flag exits 0, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 0)
        expect(f'numbered with the flag: merged, got {outcome(nw)!r}', outcome(nw) == 'merged')
        expect('numbered with the flag: tip is close T-0001',
               sh(nw, 'log', '-1', '--format=%s', 'fanout/t').stdout.strip() == 'close T-0001')
        expect('numbered with the flag: close commit changes docs/spec.md',
               'docs/spec.md' in sh(nw, 'diff', '--name-only', 'fanout/t~1', 'fanout/t').stdout.split())
        expect('numbered with the flag: docs/spec.md cites the dot path',
               sh(nw, 'show', 'fanout/t:docs/spec.md').stdout == 'see .sdlc/.0001-x/handoff.md\n')
        expect('numbered with the flag: .sdlc/.0001-x/handoff.md on the branch',
               sh(nw, 'cat-file', '-e', 'fanout/t:.sdlc/.0001-x/handoff.md').returncode == 0)
        expect('numbered with the flag: integration worktree clean', integ_clean(nw))

        # 5. Inherited red: a step-1 builder Status `inherited red: test_a` stops the lane with that
        # cause; nothing is committed, merged, or closed. Negative control: Status `done` merges.
        def inherited_stub(status):
            return ('if [ "$FANOUT_TICKET" = T-0001 ]; then '
                    'mkdir -p "$FANOUT_ROOT/$FANOUT_SLUG/step-1"; '
                    f'printf "<!-- role=builder level=L2 model=opus effort=low -->\\n## Status\\n{status}\\n" '
                    '> "$FANOUT_ROOT/$FANOUT_SLUG/step-1/builder-L2.md"; fi; '
                    'printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" '
                    '> "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo "$FANOUT_TICKET" > "work-$FANOUT_TICKET.txt"')

        def report_rows(lanes_dir):
            rep, got = lanes_dir / 'report.md', {}
            for line in (rep.read_text() if rep.is_file() else '').splitlines():
                c = [x.strip() for x in line.strip('|').split('|')]
                if line.startswith('| ') and len(c) == 4 and tickets.ID_RE.fullmatch(c[1]):
                    got[c[1]] = c[2]
            return got

        ir, il = tmp / 'inherited', tmp / 'ilanes'
        make_repo(ir, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')])
        proc = fanout(ir, 'a=T-0001,T-0002', '--integration', 'fanout/ir', '--lanes-dir', str(il),
                      '--driver', inherited_stub('inherited red: test_a'), '--gate', 'true')
        got = report_rows(il)
        expect(f'inherited red: run exits 1, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 1)
        expect(f'inherited red: T-0001 outcome is exactly inherited red: step-1: test_a, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'inherited red: step-1: test_a')
        expect(f'inherited red: T-0002 skipped, got {got.get("T-0002")!r}', got.get('T-0002') == 'skipped')
        merges = sh(ir, 'rev-list', '--merges', '--count', 'fanout/ir').stdout.strip()
        expect(f'inherited red: fanout/ir has no merge commits, got {merges!r}', merges == '0')
        expect('inherited red: fanout/ir does not hold work-T-0001.txt',
               sh(ir, 'cat-file', '-e', 'fanout/ir:work-T-0001.txt').returncode != 0)
        shown = sh(ir, 'show', 'fanout/ir:.sdlc/a/handoff.md').stdout
        expect(f'inherited red: fanout/ir:.sdlc/a/handoff.md still says status: ready, got {shown[:120]!r}',
               re.search(r'^status: ready\b', shown, re.M))
        kept = il / 'a' / '.sdlc' / 'a' / 'step-1' / 'builder-L2.md'
        lane_status = sh(il / 'a', 'status', '--porcelain', '--untracked-files=all').stdout
        expect(f'inherited red: the lane tree is clean after the stop (WIP-committed), got {lane_status!r}',
               kept.is_file() and lane_status == '')
        subj = sh(ir, 'log', '-1', '--format=%s', 'fanout/ir-a').stdout.strip()
        expect(f'inherited red: lane tip is wip(T-0001): inherited red: step-1: test_a, got {subj!r}',
               subj == 'wip(T-0001): inherited red: step-1: test_a')
        expect('inherited red: the lane branch keeps the step-1 builder file',
               sh(ir, 'cat-file', '-e', 'fanout/ir-a:.sdlc/a/step-1/builder-L2.md').returncode == 0)
        expect('inherited red: the lane branch is not an ancestor of fanout/ir',
               sh(ir, 'merge-base', '--is-ancestor', 'fanout/ir-a', 'fanout/ir').returncode == 1)

        # 5b. Inherited red after a non-zero driver exit: the cause is still reported, with the
        # driver rc as a suffix. Negative control: a non-zero exit with no step stays plain.
        nr, nl = tmp / 'inherited-rc', tmp / 'nlanes'
        make_repo(nr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')])
        proc = fanout(nr, 'a=T-0001,T-0002', '--integration', 'fanout/nr', '--lanes-dir', str(nl),
                      '--driver', inherited_stub('inherited red: test_a') + '; exit 7', '--gate', 'true')
        got = report_rows(nl)
        expect(f'inherited red rc=7: run exits 1, got {proc.returncode}', proc.returncode == 1)
        expect(f'inherited red rc=7: T-0001 outcome, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'inherited red: step-1: test_a (driver rc=7)')
        expect(f'inherited red rc=7: T-0002 skipped, got {got.get("T-0002")!r}', got.get('T-0002') == 'skipped')
        merges = sh(nr, 'rev-list', '--merges', '--count', 'fanout/nr').stdout.strip()
        expect(f'inherited red rc=7: fanout/nr has no merge commits, got {merges!r}', merges == '0')
        shown = sh(nr, 'show', 'fanout/nr:.sdlc/a/handoff.md').stdout
        expect(f'inherited red rc=7: ticket still ready on fanout/nr, got {shown[:120]!r}',
               re.search(r'^status: ready\b', shown, re.M))
        lane_status = sh(nl / 'a', 'status', '--porcelain', '--untracked-files=all').stdout
        expect(f'inherited red rc=7: lane tree clean (WIP-committed), got {lane_status!r}', lane_status == '')
        cr, cl = tmp / 'plain-rc', tmp / 'clanes'
        make_repo(cr, [('a', 'T-0001', 'ready')])
        fanout(cr, 'a=T-0001', '--integration', 'fanout/cr', '--lanes-dir', str(cl), '--driver', 'exit 7')
        got = report_rows(cl)
        expect(f'no inherited step, rc=7 (negative control): outcome is driver failed rc=7, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'driver failed rc=7')

        dr, dl = tmp / 'inherited-done', tmp / 'dlanes'
        make_repo(dr, [('a', 'T-0001', 'ready')])
        proc = fanout(dr, 'a=T-0001', '--integration', 'fanout/dr', '--lanes-dir', str(dl),
                      '--driver', inherited_stub('done'), '--gate', 'true')
        got = report_rows(dl)
        expect(f'done builder (negative control): run exits 0, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0)
        expect(f'done builder (negative control): T-0001 merged, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'merged')
        shown = sh(dr, 'show', 'fanout/dr:.sdlc/a/handoff.md').stdout
        expect(f'done builder (negative control): ticket closed on fanout/dr, got {shown[:120]!r}',
               re.search(r'^status: done\b', shown, re.M))

        # 5c. Verifier-inherited: builder Status `done`, a newer verifier Verdict
        # `inherited red: test_v`; the outcome names the verifier's tests, not `done`.
        vstub = ('if [ "$FANOUT_TICKET" = T-0001 ]; then '
                 's="$FANOUT_ROOT/$FANOUT_SLUG/step-1"; mkdir -p "$s"; '
                 'printf "<!-- role=builder level=L2 model=opus effort=low -->\\n## Status\\ndone\\n" '
                 '> "$s/builder-L2.md"; '
                 'printf "<!-- role=verifier level=L1 model=sonnet effort=medium -->\\n'
                 '## Verdict\\ninherited red: test_v\\n" > "$s/verifier-L1.md"; '
                 'printf \'{"file": "builder-L2.md"}\\n{"file": "verifier-L1.md"}\\n\' > "$s/runs.jsonl"; fi; '
                 'printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" '
                 '> "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo "$FANOUT_TICKET" > "work-$FANOUT_TICKET.txt"')
        vr, vl = tmp / 'inherited-verifier', tmp / 'vlanes'
        make_repo(vr, [('a', 'T-0001', 'ready')])
        proc = fanout(vr, 'a=T-0001', '--integration', 'fanout/vr', '--lanes-dir', str(vl),
                      '--driver', vstub, '--gate', 'true')
        got = report_rows(vl)
        expect(f'verifier inherited red: run exits 1, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 1)
        expect(f'verifier inherited red: outcome is inherited red: step-1: test_v, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'inherited red: step-1: test_v')

        # 5d. A human edit in the integration worktree before the merge: the ticket is refused
        # with `integration dirty`, no merge or reset runs, and the edit survives.
        xr, xl = tmp / 'integ-dirty', tmp / 'xlanes'
        make_repo(xr, [('a', 'T-0001', 'ready')], {'notes.txt': 'base\n'})
        proc = fanout(xr, 'a=T-0001', '--integration', 'fanout/xr', '--lanes-dir', str(xl),
                      '--driver', 'echo human >> ../integration/notes.txt; echo x > work.txt',
                      '--gate', 'test -z "$(git status --porcelain --untracked-files=no)"')
        got = report_rows(xl)
        expect(f'integration dirty: run exits 1, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 1)
        expect(f'integration dirty: outcome is integration dirty: notes.txt, got {got.get("T-0001")!r}',
               got.get('T-0001') == 'integration dirty: notes.txt')
        diff = sh(xl / 'integration', 'diff').stdout
        expect(f'integration dirty: the edit survives in the integration worktree, got {diff!r}', '+human' in diff)
        merges = sh(xr, 'rev-list', '--merges', '--count', 'fanout/xr').stdout.strip()
        expect(f'integration dirty: fanout/xr has no merge commits, got {merges!r}', merges == '0')

        # 6. A full stub-driver run in the default lanes dir (<toplevel>/.worktrees/fanout, no
        # --lanes-dir): lane commits, merges and closes, with the main tree's status left clean.
        fr = tmp / 'default-dir'
        make_repo(fr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')], {'.gitignore': '.worktrees/\n'})
        fmain0 = sh(fr, 'rev-parse', 'main').stdout.strip()
        proc = fanout(fr, 'alpha=T-0001', 'beta=T-0002', '--integration', 'fanout/dd',
                      '--driver', shlex.quote(str(stub)), '--gate', 'true')
        expect(f'default lanes dir: run exits 0, got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0)
        flanes = fr / '.worktrees' / 'fanout'
        expect(f'default lanes dir: {flanes / "report.md"} exists', (flanes / 'report.md').is_file())
        got = report_rows(flanes)
        for tid in ('T-0001', 'T-0002'):
            expect(f'default lanes dir: {tid} merged, got {got.get(tid)!r}', got.get(tid) == 'merged')
        for lane, tid, slug in (('alpha', 'T-0001', 'a'), ('beta', 'T-0002', 'b')):
            subjects = sh(fr, 'log', '--format=%s', archived(fr, f'fanout/dd-{lane}') or 'missing-archive-ref').stdout.splitlines()
            expect(f'default lanes dir: fanout/dd-{lane} (lane closed, read at its archive ref) has a commit '
                   f'"{tid}: Ticket {slug}", got {subjects!r}', f'{tid}: Ticket {slug}' in subjects)
            expect(f'default lanes dir: fanout/dd holds {tid}.txt',
                   sh(fr, 'cat-file', '-e', f'fanout/dd:{tid}.txt').returncode == 0)
            shown = sh(fr, 'show', f'fanout/dd:.sdlc/{slug}/handoff.md').stdout
            expect(f'default lanes dir: fanout/dd:.sdlc/{slug}/handoff.md says status: done, got {shown[:120]!r}',
                   re.search(r'^status: done\b', shown, re.M))
        merges = sh(fr, 'rev-list', '--merges', '--count', 'fanout/dd').stdout.strip()
        expect(f'default lanes dir: fanout/dd has two merge commits, got {merges!r}', merges == '2')
        fmain1 = sh(fr, 'rev-parse', 'main').stdout.strip()
        expect(f'default lanes dir: main sha unchanged, {fmain0!r} -> {fmain1!r}', fmain0 and fmain1 == fmain0)
        head = sh(fr, 'symbolic-ref', 'HEAD').stdout.strip()
        expect(f'default lanes dir: HEAD is refs/heads/main, got {head!r}', head == 'refs/heads/main')
        status = sh(fr, 'status', '--porcelain', '--untracked-files=all')
        expect(f'default lanes dir: git status --porcelain --untracked-files=all empty in the main tree, '
               f'got {status.stdout!r}', status.returncode == 0 and status.stdout == '')
        ignored = sh(fr, 'status', '--porcelain', '--ignored').stdout
        expect(f'default lanes dir: git status --ignored lists .worktrees/ (non-vacuity), got {ignored!r}',
               '!! .worktrees/' in ignored.splitlines())
        wts = sh(fr, 'worktree', 'list').stdout
        for name, want in (('alpha', False), ('beta', False), ('integration', True)):
            expect(f'default lanes dir: git worktree list shows {flanes / name} is {want} (merged lanes closed), got {wts!r}',
                   any(ln.split()[0] == str(flanes / name) for ln in wts.splitlines() if ln.strip()) is want)

        # 7. A driver that edits the lane and fails: the lane is WIP-committed, never merged.
        rw, wl = tmp / 'wip', tmp / 'wlanes'
        make_repo(rw, [('w', 'T-0001', 'ready')])
        fixture = sh(rw, 'rev-parse', 'main').stdout.strip()
        proc = fanout(rw, 'alpha=T-0001', '--integration', 'fanout/wip', '--lanes-dir', str(wl),
                      '--driver', 'echo x >edit.txt; exit 3')
        ran = f'(stdout={proc.stdout!r} stderr={proc.stderr!r})'
        lane_wt = wl / 'alpha'
        expect(f'wip case: run exits 1, got {proc.returncode} {ran}', proc.returncode == 1)
        expect('wip case: the lane tree is clean (no tracked changes, no untracked files)',
               lane_wt.is_dir() and sh(lane_wt, 'diff', '--quiet', 'HEAD').returncode == 0
               and sh(lane_wt, 'ls-files', '--others', '--exclude-standard').stdout.strip() == '')
        subj = sh(rw, 'log', '-1', '--format=%s', 'fanout/wip-alpha').stdout.strip()
        expect(f'wip case: lane branch tip subject starts wip(T-0001): driver failed rc=, got {subj!r}',
               subj.startswith('wip(T-0001): driver failed rc='))
        expect('wip case: the lane branch holds edit.txt',
               sh(rw, 'cat-file', '-e', 'fanout/wip-alpha:edit.txt').returncode == 0)
        expect('wip case: the lane branch is not an ancestor of the integration branch',
               sh(rw, 'merge-base', '--is-ancestor', 'fanout/wip-alpha', 'fanout/wip').returncode == 1)
        expect('wip case: the integration branch still equals the fixture commit',
               sh(rw, 'rev-parse', 'fanout/wip').stdout.strip() == fixture and fixture)
        expect('wip case: main still equals the fixture commit', sh(rw, 'rev-parse', 'main').stdout.strip() == fixture)
        rep = wl / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        expect(f'wip case: report row Commit cell is wip <sha7>, got {text!r}',
               re.search(r'^\| alpha \| T-0001 \| driver failed rc=3 \| wip [0-9a-f]{7} \|$', text, re.M))

        # 8. A gate leaves the lane tree dirty after T-0001 merges: T-0002's pre-sync wip commit
        # stops the ticket, so it is never synced, driven, committed, or merged.
        # Negative control: the same run with no gate merges both tickets.
        sr, sl = tmp / 'dirty-sync', tmp / 'slanes'
        make_repo(sr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')])
        sfixture = sh(sr, 'rev-parse', 'main').stdout.strip()
        proc = fanout(sr, 'alpha=T-0001,T-0002', '--integration', 'fanout/ds', '--lanes-dir', str(sl),
                      '--driver', shlex.quote(str(stub)), '--gate', f'echo x >{shlex.quote(str(sl))}/alpha/dirty.txt')
        ran = f'(stdout={proc.stdout!r} stderr={proc.stderr!r})'
        expect(f'dirty-sync case: run exits 1, got {proc.returncode} {ran}', proc.returncode == 1)
        rep = sl / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        expect(f'dirty-sync case: report row | alpha | T-0002 | dirty before sync | wip <sha7> |, got {text!r}',
               re.search(r'^\| alpha \| T-0002 \| dirty before sync \| wip [0-9a-f]{7} \|$', text, re.M))
        subj = sh(sr, 'log', '-1', '--format=%s', 'fanout/ds-alpha').stdout.strip()
        expect(f'dirty-sync case: lane tip subject is wip(T-0002): dirty before sync, got {subj!r}',
               subj == 'wip(T-0002): dirty before sync')
        expect('dirty-sync case: the lane tip is not an ancestor of the integration branch',
               sh(sr, 'merge-base', '--is-ancestor', 'fanout/ds-alpha', 'fanout/ds').returncode == 1)
        expect('dirty-sync case: the integration branch holds T-0001.txt',
               sh(sr, 'cat-file', '-e', 'fanout/ds:T-0001.txt').returncode == 0)
        expect('dirty-sync case: the integration branch does not hold dirty.txt',
               sh(sr, 'cat-file', '-e', 'fanout/ds:dirty.txt').returncode != 0)
        shown = sh(sr, 'show', 'fanout/ds:.sdlc/b/handoff.md').stdout
        expect(f'dirty-sync case: fanout/ds:.sdlc/b/handoff.md still says status: ready, got {shown[:120]!r}',
               re.search(r'^status: ready\b', shown, re.M))
        expect('dirty-sync case: main still equals the fixture commit',
               sfixture and sh(sr, 'rev-parse', 'main').stdout.strip() == sfixture)

        cr, cl = tmp / 'dirty-sync-control', tmp / 'sclanes'
        make_repo(cr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')])
        proc = fanout(cr, 'alpha=T-0001,T-0002', '--integration', 'fanout/dc', '--lanes-dir', str(cl),
                      '--driver', shlex.quote(str(stub)))
        got = report_rows(cl)
        expect(f'dirty-sync control: run exits 0, got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0)
        for tid in ('T-0001', 'T-0002'):
            expect(f'dirty-sync control: {tid} merged, got {got.get(tid)!r}', got.get(tid) == 'merged')
        subj = sh(cr, 'log', '-1', '--format=%s', archived(cr, 'fanout/dc-alpha') or 'missing-archive-ref').stdout.strip()
        expect(f'dirty-sync control: lane tip subject (lane closed, read at its archive ref) does not start with wip(, got {subj!r}',
               subj and not subj.startswith('wip('))
        expect('dirty-sync control: the integration branch holds T-0002.txt',
               sh(cr, 'cat-file', '-e', 'fanout/dc:T-0002.txt').returncode == 0)

        # 9. Resume: a failed run, its worktrees and lane branch removed, then a rerun on the reused
        # integration branch. logs/fanout.log keeps both runs' lines under two distinct run ids,
        # and the second run's lane and gate log lines all carry its own id.
        qr, ql, ok = tmp / 'resume', tmp / 'qlanes', tmp / 'resume-ok'
        make_repo(qr, [('a', 'T-0001', 'ready')])
        qdriver = (f'if test -e {shlex.quote(str(ok))}; then echo rid=$FANOUT_RUN_ID; '
                   'printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" > "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; '
                   'else exit 3; fi')
        qargs = ('alpha=T-0001', '--integration', 'fanout/q', '--lanes-dir', str(ql), '--driver', qdriver,
                 '--gate', 'echo gated')
        p1 = fanout(qr, *qargs)
        expect(f'resume case: first run exits 1, got {p1.returncode} stderr={p1.stderr!r}', p1.returncode == 1)
        ok.touch()
        for args in (('worktree', 'remove', '--force', str(ql / 'integration')),
                     ('worktree', 'remove', '--force', str(ql / 'alpha')), ('branch', '-D', 'fanout/q-alpha')):
            q = sh(qr, *args)
            expect(f'resume case: git {args} exited 0, got {q.returncode} stderr={q.stderr!r}', q.returncode == 0)
        p2 = fanout(qr, *qargs)
        expect(f'resume case: second run exits 0, got {p2.returncode} stdout={p2.stdout!r} stderr={p2.stderr!r}',
               p2.returncode == 0)
        rid = r'fanout-[0-9a-f]{12}'
        flog = ql / 'logs' / 'fanout.log'
        ftext = flog.read_text() if flog.is_file() else ''
        ma = re.search(rf'^\[({rid})\] \[alpha\] T-0001 driver failed rc=3$', ftext, re.M)
        mb = re.search(rf'^\[({rid})\] \[alpha\] T-0001 merged$', ftext, re.M)
        a_id, b_id = (ma.group(1) if ma else ''), (mb.group(1) if mb else '')
        expect(f'resume case: fanout.log keeps the first run driver failed line, got {ftext!r}', a_id)
        expect(f'resume case: fanout.log holds the second run merged line, got {ftext!r}', b_id)
        expect(f'resume case: the two runs have distinct ids, got {a_id!r} and {b_id!r}', a_id and a_id != b_id)
        expect(f'resume case: every fanout.log line starts with a run id, got {ftext!r}',
               ftext and all(re.match(rf'\[{rid}\] ', ln) for ln in ftext.splitlines()))
        for name in ('alpha-T-0001.log', 'gate-alpha-T-0001-1-a1.log'):
            lg = ql / 'logs' / name
            lines = lg.read_text().splitlines() if lg.is_file() else []
            expect(f'resume case: every {name} line starts with [{b_id}] , got {lines!r}',
                   b_id and lines and all(ln.startswith(f'[{b_id}] ') for ln in lines))
        dlog = ql / 'logs' / 'alpha-T-0001.log'
        expect(f'resume case: the driver saw FANOUT_RUN_ID={b_id}',
               b_id and dlog.is_file() and f'[{b_id}] rid={b_id}' in dlog.read_text().splitlines())
        gl = ql / 'logs' / 'gate-alpha-T-0001-1-a1.log'
        expect('resume case: the gate log holds the prefixed gate output',
               b_id and gl.is_file() and f'[{b_id}] gated' in gl.read_text().splitlines())
        expect(f'resume case: the second run printed [{b_id}] [alpha] T-0001 merged',
               b_id and f'[{b_id}] [alpha] T-0001 merged' in p2.stdout.splitlines())
        qrep = ql / 'report.md'
        expect(f'resume case: report.md names the run id {b_id}',
               b_id and qrep.is_file() and f'- Run: `{b_id}`' in qrep.read_text())

        # 10. Gate retry case: a red gate run, then a green rerun on the reused integration branch.
        # Each attempt gets its own gate log, so the first failure survives the retry.
        gr, gls, gok = tmp / 'gretry', tmp / 'glanes', tmp / 'gretry-ok'
        make_repo(gr, [('a', 'T-0001', 'ready')])
        gdriver = ('echo hi > f.txt; '
                   'printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" > "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"')
        ggate = f'if test -e {shlex.quote(str(gok))}; then echo attempt-two; else echo attempt-one; exit 1; fi'
        gargs = ('alpha=T-0001', '--integration', 'fanout/g', '--lanes-dir', str(gls), '--driver', gdriver,
                 '--gate', ggate)
        g1 = fanout(gr, *gargs)
        expect(f'gate retry case: first run exits 1, got {g1.returncode} stderr={g1.stderr!r}', g1.returncode == 1)
        gok.touch()
        for args in (('worktree', 'remove', '--force', str(gls / 'integration')),
                     ('worktree', 'remove', '--force', str(gls / 'alpha')), ('branch', '-D', 'fanout/g-alpha')):
            q = sh(gr, *args)
            expect(f'gate retry case: git {args} exited 0, got {q.returncode} stderr={q.stderr!r}', q.returncode == 0)
        g2 = fanout(gr, *gargs)
        expect(f'gate retry case: second run exits 0, got {g2.returncode} stdout={g2.stdout!r} stderr={g2.stderr!r}',
               g2.returncode == 0)
        for name, word in (('gate-alpha-T-0001-1-a1.log', 'attempt-one'), ('gate-alpha-T-0001-1-a2.log', 'attempt-two')):
            lg = gls / 'logs' / name
            text = lg.read_text() if lg.is_file() else ''
            expect(f'gate retry case: {name} holds {word}, got {text!r}', word in text)

        # 11. The lane's last driver leaves a dead-owner tmp prefix; fanout reaps it after the driver.
        rp, rpl = tmp / 'reap', tmp / 'rplanes'
        make_repo(rp, [('a', 'T-0001', 'ready')])
        dead = subprocess.Popen(['true'])
        dead.wait()
        rstub = tmp / 'reap-stub.sh'
        rstub.write_text(REAP_STUB)
        rstub.chmod(0o755)
        proc = fanout(rp, 'alpha=T-0001', '--integration', 'fanout/rp', '--lanes-dir', str(rpl),
                      '--driver', f'DEADPID={dead.pid} {shlex.quote(str(rstub))}', '--gate', 'true')
        prefix = rpl / 'alpha' / '.worktrees' / 'tmp' / f'builder-{dead.pid}'
        wts = sh(rp, 'worktree', 'list', '--porcelain').stdout
        expect(f'lane tmp prefix reaped: {prefix} gone and unlisted, got exists={prefix.exists()} '
               f'rc={proc.returncode} worktrees={wts!r}',
               not prefix.exists() and f'builder-{dead.pid}' not in wts)
        expect(f'lane tmp prefix reaped: T-0001 merged, got {report_rows(rpl).get("T-0001")!r}',
               report_rows(rpl).get('T-0001') == 'merged')

        # 12. External lane: a registered branch `ext` that an outside agent owns joins as alpha@ext, with
        # no worktree, no lane branch, and no driver, beside a regular beta lane. The branch is never written.
        def make_ext(repo, config):
            fm = ('---\nid: {}\ntitle: "Ticket {}"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
                  'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n')
            (repo / '.sdlc' / 'a').mkdir(parents=True)
            (repo / '.sdlc' / 'a' / 'handoff.md').write_text(fm.format('T-0001', 'a'), encoding='utf-8')
            if config:
                (repo / '.sdlc' / 'config').write_text(config, encoding='utf-8')
            for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                         ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                         ('add', '-A'), ('commit', '-q', '-m', 'fixture'), ('checkout', '-q', '-b', 'ext')):
                q = sh(repo, *args)
                expect(f'external fixture git {args} exited 0, got {q.returncode} stderr={q.stderr!r}',
                       q.returncode == 0)
            for slug, tid in (('b', 'T-0002'), ('c', 'T-0003')):
                (repo / '.sdlc' / slug).mkdir()
                (repo / '.sdlc' / slug / 'handoff.md').write_text(fm.format(tid, slug), encoding='utf-8')
                (repo / '.sdlc' / slug / 'filer-L1.md').write_text('## Warnings\nNone\n\n## Follow-ups\nNone\n',
                                                                   encoding='utf-8')
            (repo / 'ext.txt').write_text('ext\n', encoding='utf-8')
            for args in (('add', '-A'), ('commit', '-q', '-m', 'outside agent work'), ('checkout', '-q', 'main')):
                q = sh(repo, *args)
                expect(f'external fixture git {args} exited 0, got {q.returncode} stderr={q.stderr!r}',
                       q.returncode == 0)

        er, el = tmp / 'external', tmp / 'elanes'
        make_ext(er, 'external_branch: ext\nexternal_branch: gone\n')
        with open(er / '.git' / 'info' / 'exclude', 'a') as f_:  # lanes.py open takes its flock at <toplevel>/.worktrees/lanes.lock
            f_.write('.worktrees/\n')
        e0, em0 = sh(er, 'rev-parse', 'ext').stdout.strip(), sh(er, 'rev-parse', 'main').stdout.strip()
        eargs = ('--integration', 'fanout/ext', '--lanes-dir', str(el))
        proc = fanout(er, '--dry-run', *eargs, 'alpha@ext=T-0002,T-0003', 'beta=T-0001')
        expect(f'external: --dry-run exits 0 with the plan line and no alpha lane branch, got {proc.returncode} '
               f'stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0
               and 'lane alpha: external branch ext (registered; no worktree, no driver)' in proc.stdout.splitlines()
               and 'fanout/ext-alpha' not in proc.stdout and 'lane beta: branch fanout/ext-beta' in proc.stdout)
        for label, args, want in (
                ('an empty branch', ('alpha@=T-0002',), SPEC_FORMS),
                ('no =', ('alpha@ext',), SPEC_FORMS),
                ('a registered name with no local ref', ('alpha@gone=T-0002',), 'refs/heads/gone'),
                ('one branch in two lanes', ('alpha@ext=T-0002', 'beta@ext=T-0003'),
                 'branch ext is named by lane alpha and lane beta'),
                ('an id absent on the branch', ('alpha@ext=T-0009',), 'T-0009: no ticket on branch ext has this id')):
            proc = fanout(er, *eargs, '--driver', 'exit 3', *args)
            expect(f'external refusal, {label}: exit 2 naming {want!r}, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 2 and want in proc.stderr and 'Traceback' not in proc.stderr)
        proc = fanout(er, '--integration', 'ext', '--lanes-dir', str(el), '--driver', 'exit 3', 'alpha@ext=T-0002')
        expect(f'external refusal, the branch as the integration branch: exit 2, got {proc.returncode} '
               f'stderr={proc.stderr!r}', proc.returncode == 2 and 'is the integration branch' in proc.stderr)
        expect('external: dry run and refusals create no fanout/* branch',
               sh(er, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        expect('external: dry run and refusals create no lanes dir', not el.exists())
        expect('external: dry run and refusals add no worktree',
               len([ln for ln in sh(er, 'worktree', 'list').stdout.splitlines() if ln.strip()]) == 1)

        proc = fanout(er, *eargs, 'alpha@ext=T-0002,T-0003', 'beta=T-0001', '--driver', shlex.quote(str(stub)),
                      '--gate', 'true')
        expect(f'external: the mixed run exits 0, got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0)
        expect('external: the ext tip is unchanged', e0 and sh(er, 'rev-parse', 'ext').stdout.strip() == e0)
        expect('external: main is unchanged', em0 and sh(er, 'rev-parse', 'main').stdout.strip() == em0)
        expect('external: no fanout/ext-alpha ref or archive, while the regular fanout/ext-beta was made (lane closed: archived)',
               sh(er, 'branch', '--list', 'fanout/ext-alpha').stdout.strip() == '' and not archived(er, 'fanout/ext-alpha')
               and archived(er, 'fanout/ext-beta'))
        expect('external: no <lanes-dir>/alpha dir, while <lanes-dir>/beta was made (lane closed: its driver log exists)',
               not (el / 'alpha').exists() and not (el / 'beta').exists() and (el / 'logs' / 'beta-T-0001.log').is_file())
        expect('external: no alpha driver log, while beta-T-0001.log exists',
               not (el / 'logs' / 'alpha-T-0002.log').exists() and not (el / 'logs' / 'alpha-T-0003.log').exists()
               and (el / 'logs' / 'beta-T-0001.log').is_file())
        glogs = sorted(f.name for f in (el / 'logs').iterdir() if f.name.startswith('gate-alpha-')) \
            if (el / 'logs').is_dir() else []
        expect(f'external: exactly one alpha gate log, gate-alpha-T-0002-1-a1.log (T-0003 merged nothing new), '
               f'got {glogs}', glogs == ['gate-alpha-T-0002-1-a1.log'])
        merges = sh(er, 'rev-list', '--merges', '--count', 'fanout/ext').stdout.strip()
        expect(f'external: fanout/ext has two merge commits (one per lane), got {merges!r}', merges == '2')
        for f in ('ext.txt', 'T-0001.txt'):
            expect(f'external: fanout/ext holds {f}', sh(er, 'cat-file', '-e', f'fanout/ext:{f}').returncode == 0)
        for slug in 'abc':
            shown = sh(er, 'show', f'fanout/ext:.sdlc/{slug}/handoff.md').stdout
            expect(f'external: fanout/ext:.sdlc/{slug}/handoff.md says status: done, got {shown[:120]!r}',
                   re.search(r'^status: done\b', shown, re.M))
        rep = el / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        expect(f'external: report.md holds the external lane line at the ext tip, got {text!r}',
               e0 and f'- Lane `alpha`: external branch `ext` at `{e0}`' in text.splitlines())
        got = report_rows(el)
        expect(f'external: report rows T-0002 and T-0003 (alpha) and T-0001 (beta) all merged, got {got}',
               got == {'T-0001': 'merged', 'T-0002': 'merged', 'T-0003': 'merged'})
        expect('external: the main tree status stays clean', sh(er, 'status', '--porcelain').stdout == '')

        en, enl = tmp / 'external-unregistered', tmp / 'enlanes'
        make_ext(en, None)
        proc = fanout(en, '--integration', 'fanout/ext', '--lanes-dir', str(enl), '--driver', 'exit 3',
                      'alpha@ext=T-0002,T-0003')
        expect(f'external negative control, no config line: exit 2 naming external_branch: ext and .sdlc/config, '
               f'got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 2 and 'external_branch: ext' in proc.stderr and '/.sdlc/config' in proc.stderr)
        expect('external negative control: no fanout/* branch and no lanes dir',
               sh(en, 'branch', '--list', 'fanout/*').stdout.strip() == '' and not enl.exists())

        erl = tmp / 'erlanes'
        proc = fanout(er, '--integration', 'fanout/ext-red', '--lanes-dir', str(erl), '--driver', 'exit 3',
                      '--gate', 'false', 'alpha@ext=T-0002')
        got = report_rows(erl)
        expect(f'external red gate: exit 1 with red: false rc=1, got {proc.returncode} {got} stderr={proc.stderr!r}',
               proc.returncode == 1 and got.get('T-0002') == 'red: false rc=1')
        expect('external red gate: the integration branch stays at its base',
               em0 and sh(er, 'rev-parse', 'fanout/ext-red').stdout.strip() == em0)
        expect('external red gate: the ext tip is unchanged', e0 and sh(er, 'rev-parse', 'ext').stdout.strip() == e0)

        # A regular lane under `ticket_root: tickets`: ids, handoff, filer, and close use <root>/tickets.
        tr, trl = tmp / 'troot', tmp / 'trlanes'
        (tr / '.sdlc' / 'tickets' / 'x').mkdir(parents=True)
        (tr / '.sdlc' / 'config').write_text('ticket_root: tickets\n', encoding='utf-8')
        (tr / '.sdlc' / 'tickets' / 'x' / 'handoff.md').write_text(
            '---\nid: T-0001\ntitle: "Ticket x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
            'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n', encoding='utf-8')
        for slug, tid, grep in (('y', 'T-0002', 'grep -vxF -e shared.txt -e y.txt'),
                                ('z', 'T-0003', 'grep -vxF -e shared.txt -e z.txt')):
            (tr / '.sdlc' / 'tickets' / slug / 'step-1').mkdir(parents=True)
            (tr / '.sdlc' / 'tickets' / slug / 'handoff.md').write_text(
                f'---\nid: {tid}\ntitle: "Ticket {slug}"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
                f'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\n{slug}\n', encoding='utf-8')
            (tr / '.sdlc' / 'tickets' / slug / 'step-1' / 'handoff.md').write_text(
                '## Step 1\n### Acceptance criteria\n'
                f'- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | {grep})"`\n', encoding='utf-8')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(tr, *args)
            expect(f'ticket_root lane: fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}',
                   p.returncode == 0)
        tdrv = ('printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" > "$(dirname "$FANOUT_HANDOFF")/filer-L1.md"; '
                'echo x > x.txt')
        proc = fanout(tr, '--dry-run', '--integration', 'fanout/tr', '--lanes-dir', str(trl), 'a=T-0001')
        expect(f'ticket_root lane: dry run exits 0 naming the ticket folders, got {proc.returncode} '
               f'stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'ticket folders in each worktree: .sdlc/tickets' in proc.stdout)
        proc = fanout(tr, '--dry-run', '--integration', 'fanout/tr', '--lanes-dir', str(trl), 'a=T-0002', 'b=T-0003')
        lines = proc.stdout.splitlines()
        expect(f'ticket_root lane: planned scopes under .sdlc/tickets print the a/b shared.txt pair line, '
               f'got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'overlap (planned scope): a T-0002 and b T-0003: shared.txt' in lines
               and not any('not planned' in x for x in lines))
        proc = fanout(tr, '--integration', 'fanout/tr', '--lanes-dir', str(trl), '--driver', tdrv, 'a=T-0001')
        got = report_rows(trl)
        expect(f'ticket_root lane: run exits 0 merged, got {proc.returncode} {got} stderr={proc.stderr!r}',
               proc.returncode == 0 and got.get('T-0001') == 'merged')
        shown = sh(tr, 'show', 'fanout/tr:.sdlc/tickets/x/handoff.md')
        expect(f'ticket_root lane: the integration handoff says status: done, got {shown.stdout[:160]!r}',
               shown.returncode == 0 and re.search(r'^status: done\b', shown.stdout, re.M))
        subj = sh(tr, 'log', '-1', '--format=%s', 'fanout/tr').stdout.strip()
        expect(f'ticket_root lane: the integration tip is close T-0001, got {subj!r}', subj == 'close T-0001')
        expect('ticket_root lane: no .sdlc/x folder on the integration branch',
               sh(tr, 'cat-file', '-e', 'fanout/tr:.sdlc/x').returncode != 0)
        # T-0258: numbered folders under `ticket_root: tickets` with .sdlc/config untracked (gitignored): the
        # integration worktree has no config, so the close must still resolve the ticket through ticket_root.
        nt, ntl = tmp / 'ntroot', tmp / 'ntlanes'
        (nt / '.sdlc' / 'tickets' / '0001-x').mkdir(parents=True)
        (nt / '.sdlc' / 'config').write_text('ticket_folders: numbered\nticket_root: tickets\n', encoding='utf-8')
        (nt / '.gitignore').write_text('.sdlc/config\n.worktrees/\n', encoding='utf-8')
        (nt / '.sdlc' / 'tickets' / '0001-x' / 'handoff.md').write_text(
            '---\nid: T-0001\ntitle: "Ticket x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
            'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n', encoding='utf-8')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(nt, *args)
            expect(f'untracked config lane: fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}',
                   p.returncode == 0)
        proc = fanout(nt, '--integration', 'fanout/nt', '--lanes-dir', str(ntl), '--driver', tdrv, 'a=T-0001')
        got = report_rows(ntl)
        expect(f'untracked config lane: run exits 0 merged and closed, got {proc.returncode} {got} '
               f'stderr={proc.stderr!r}', proc.returncode == 0 and got.get('T-0001') == 'merged')
        expect('untracked config lane: the ticket folder is archived under .sdlc/tickets on the branch',
               sh(nt, 'cat-file', '-e', 'fanout/nt:.sdlc/tickets/.0001-x/handoff.md').returncode == 0)
        expect('untracked config lane: no .sdlc/0001-x folder on the branch',
               sh(nt, 'cat-file', '-e', 'fanout/nt:.sdlc/0001-x').returncode != 0)
        # 13. Overlap: alpha and beta both edit shared.txt (line 1 and the last line). Beta reaches its merge
        # while alpha's driver still runs, waits for alpha (the earlier lane), and merges after it; without
        # the wait, alpha's driver times out. Negative control: disjoint lanes report none and never wait.
        shared = 'top\n' + ''.join(f'mid {n}\n' for n in range(1, 21)) + 'bottom\n'
        ostub = tmp / 'overlap-stub.sh'
        ostub.write_text(OVERLAP_STUB)
        ostub.chmod(0o755)
        ovr, ovl = tmp / 'overlap', tmp / 'ovlanes'
        make_repo(ovr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')], {'shared.txt': shared})
        proc = fanout(ovr, 'alpha=T-0001', 'beta=T-0002', '--integration', 'fanout/ov', '--lanes-dir', str(ovl),
                      '--driver', shlex.quote(str(ostub)))
        got = report_rows(ovl)
        expect(f'overlap: exit 0, both rows merged, got {proc.returncode} {got} stdout={proc.stdout!r} '
               f'stderr={proc.stderr!r}',
               proc.returncode == 0 and got == {'T-0001': 'merged', 'T-0002': 'merged'})
        order = sh(ovr, 'log', '--first-parent', '--merges', '--format=%s', 'fanout/ov').stdout.splitlines()[::-1]
        expect(f'overlap order: alpha merges before beta, got {order!r}',
               order == ['Merge fanout/ov-alpha: T-0001', 'Merge fanout/ov-beta: T-0002'])
        olog = ovl / 'logs' / 'fanout.log'
        otext = olog.read_text() if olog.is_file() else ''
        expect(f'overlap: fanout.log contains waiting for lane alpha (overlap: shared.txt), got {otext!r}',
               'waiting for lane alpha (overlap: shared.txt)' in otext)
        rep = ovl / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        expect(f'overlap: report.md has the line - Overlap: `alpha` and `beta`: `shared.txt`, got {text!r}',
               '- Overlap: `alpha` and `beta`: `shared.txt`' in text.splitlines())
        merged = sh(ovr, 'show', 'fanout/ov:shared.txt').stdout.splitlines()
        expect(f'overlap: the integration shared.txt holds both top alpha and bottom beta, got {merged!r}',
               'top alpha' in merged and 'bottom beta' in merged)

        jr, jl = tmp / 'disjoint', tmp / 'jlanes'
        make_repo(jr, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready')], {'shared.txt': shared})
        proc = fanout(jr, 'alpha=T-0001', 'beta=T-0002', '--integration', 'fanout/dj', '--lanes-dir', str(jl),
                      '--driver', shlex.quote(str(stub)))
        got = report_rows(jl)
        expect(f'disjoint lanes (negative control): exit 0, both rows merged, got {proc.returncode} {got} '
               f'stderr={proc.stderr!r}', proc.returncode == 0 and got == {'T-0001': 'merged', 'T-0002': 'merged'})
        rep = jl / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        expect(f'disjoint lanes (negative control): report.md holds - Overlap: none, got {text!r}',
               '- Overlap: none' in text.splitlines())
        jlog = jl / 'logs' / 'fanout.log'
        jtext = jlog.read_text() if jlog.is_file() else ''
        expect(f'disjoint lanes (negative control): fanout.log holds both merged lines and no waiting for lane, '
               f'got {jtext!r}',
               '[alpha] T-0001 merged' in jtext and '[beta] T-0002 merged' in jtext and 'waiting for lane' not in jtext)

        # 14. Planned-scope overlap in the dry run, read from step handoffs' scope criteria.
        pr = tmp / 'planned'
        def scope_step(slug, grep):
            d = pr / '.sdlc' / slug / 'step-1'
            d.mkdir(parents=True)
            d.joinpath('handoff.md').write_text(
                '## Step 1\n### Acceptance criteria\n'
                f'- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | {grep})"`\n', encoding='utf-8')
        pr.mkdir()
        (pr / '.sdlc').mkdir()
        pspecs = [('a', 'T-0001'), ('b', 'T-0002'), ('c', 'T-0003'), ('d', 'T-0004')]
        for slug, tid in pspecs:
            (pr / '.sdlc' / slug).mkdir()
            (pr / '.sdlc' / slug / 'handoff.md').write_text(
                f'---\nid: {tid}\ntitle: "Ticket {slug}"\ntype: chore\nstatus: ready\nsize: S\n'
                f'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\n{slug}\n', encoding='utf-8')
        scope_step('a', 'grep -vxF -e shared.txt -e a.txt')
        scope_step('b', 'grep -vxE "shared\\.txt|b\\.txt"')
        scope_step('d', 'grep -vxF -e b.txt')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(pr, *args)
            expect(f'planned fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)
        pl = tmp / 'pllanes'
        proc = fanout(pr, '--dry-run', '--lanes-dir', str(pl), 'alpha=T-0001', 'beta=T-0002,T-0003')
        lines = proc.stdout.splitlines()
        expect(f'case 14 planned scope: dry run exits 0 with the alpha/beta shared.txt pair line and T-0003 not '
               f'planned, got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0
               and 'overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt' in lines
               and 'overlap (planned scope): not planned, checked at merge time: T-0003' in lines
               and 'overlap (planned scope): none' not in lines)
        proc = fanout(pr, '--dry-run', '--lanes-dir', str(pl), 'alpha=T-0001', 'beta=T-0004')
        lines = proc.stdout.splitlines()
        expect(f'case 14 planned scope negative control: disjoint scopes print none and no pair line, '
               f'got {proc.returncode} stdout={proc.stdout!r}',
               proc.returncode == 0 and 'overlap (planned scope): none' in lines
               and not any(' and beta ' in x for x in lines if x.startswith('overlap (planned scope):')))
        expect('case 14 planned scope: dry runs create no fanout/* branch, worktree or lanes dir',
               sh(pr, 'branch', '--list', 'fanout/*').stdout.strip() == ''
               and len(sh(pr, 'worktree', 'list').stdout.splitlines()) == 1 and not pl.exists())

        # 15. Solo first: the lane per ticket, the commands, the lane cap and stagger, and the overlap refusal.
        sr = tmp / 'solofirst'
        sr.mkdir()
        (sr / '.sdlc').mkdir()
        sizes = [('s1', 'T-0001', 'L1'), ('m1', 'T-0002', 'M'), ('l1', 'T-0003', 'L3'), ('s2', 'T-0004', 'S'),
                 ('s3', 'T-0005', 'S'), ('s4', 'T-0006', 'S')]
        for slug, tid, size in sizes:
            (sr / '.sdlc' / slug).mkdir()
            (sr / '.sdlc' / slug / 'handoff.md').write_text(
                f'---\nid: {tid}\ntitle: "Ticket {slug}"\ntype: chore\nstatus: ready\nsize: {size}\n'
                f'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\n{slug}\n', encoding='utf-8')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(sr, *args)
            expect(f'solo-first fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)
        sl = tmp / 'sololanes'
        proc = fanout(sr, '--dry-run', '--lanes-dir', str(sl), 'a=T-0001', 'b=T-0002', 'c=T-0003')
        out = proc.stdout
        expect(f'case 15 lane: size L1 prints solo level L1 (sonnet low), the alias M level L2 (sonnet high), and L3 the full chain '
               f'(steps.py lane decides), got {proc.returncode} stdout={out!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'lane: solo, level L1: sonnet low' in out
               and 'lane: solo, level L2: sonnet high' in out
               and re.search(r'T-0003 l1: .*\n    lane: full \(', out) and 'driver: solo first (--lane auto)' in out)
        expect('case 15 lane negative control: no solo line for the size L3 ticket',
               not re.search(r'T-0003 l1: .*\n    lane: solo', out))
        proc = fanout(sr, '--dry-run', '--lane', 'full', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 --lane full forces the chain for a size L1 ticket, got {proc.stdout!r}',
               proc.returncode == 0 and 'lane: full (--lane full)' in proc.stdout)
        for label, size in (('L1', 'L1'), ('L2', 'L2'), ('L3', 'L3'), ('L1', 'S'), ('L2', 'M'), ('L3', 'L')):
            cmd = solo_command('h.md', size, 'claude')
            expect(f'case 15 command: size {size} starts through solo_run.py with --tier {label}, got {cmd}',
                   'solo_run.py' in cmd and ' run ' in cmd and f'--tier {label}' in cmd and '--backend claude' in cmd
                   and '--task-dir .' in cmd and 'sdlc-lite:conductor' not in cmd)
        saved_raw = os.environ.get('SDLC_SELFTEST_RAW_SOLO')
        os.environ['SDLC_SELFTEST_RAW_SOLO'] = '1'
        try:
            for label, size, want in (('L1', 'L1', ('--model sonnet', '--effort low')),
                                      ('L2', 'M', ('--model sonnet', '--effort high')),
                                      ('L3', 'L3', ('--model opus', '--effort xhigh'))):
                cmd = solo_command('h.md', size, 'claude')
                expect(f'case 15 raw fallback: level {label} starts sdlc-lite:solo with {want}, got {cmd}',
                       '--agent sdlc-lite:solo' in cmd and all(w in cmd for w in want) and cmd.startswith('SDLC_ROLE=solo ')
                       and 'sdlc-lite:conductor' not in cmd and '--dangerously-skip-permissions' in cmd and 'solo_run.py' not in cmd)
        finally:
            if saved_raw is None: os.environ.pop('SDLC_SELFTEST_RAW_SOLO', None)
            else: os.environ['SDLC_SELFTEST_RAW_SOLO'] = saved_raw
        for size, level in (('L1', 'L1'), ('L2', 'L2'), ('L3', 'L3'), ('S', 'L1'), ('M', 'L2'), ('L', 'L3')):
            cmd = solo_command('.sdlc/t/h/handoff.md', size, 'codex')
            expect(f'case 15 command: Codex size {size} runs solo_run.py --backend codex --tier {level}, got {cmd}',
                   'solo_run.py' in cmd and '--backend codex' in cmd and f'--tier {level} ' in cmd and '--task-dir .sdlc/t/h' in cmd)
        saved_ex = os.environ.pop('SDLC_CLAUDE_EXEC', None)
        try:
            default_driver('h.md', 'full', 'L2')
            expect('case 15 T-0288: no default claude -p driver without SDLC_CLAUDE_EXEC=1 (Refuse)', False)
        except Refuse:
            pass
        for sz in ('L1', 'L2'):
            try:
                default_driver('h.md', 'solo', sz)
                expect(f'case 15 T-0362: solo {sz} default driver refuses without SDLC_CLAUDE_EXEC=1 (Refuse)', False)
            except Refuse:
                pass
        os.environ['SDLC_CLAUDE_EXEC'] = '1'
        for sz in ('L1', 'L2'):
            expect(f'case 15 T-0362: solo {sz} default driver returns the solo_run command with the flag',
                   'solo_run.py' in default_driver('h.md', 'solo', sz))
        full = default_driver('h.md', 'full', 'L2')
        if saved_ex is None: os.environ.pop('SDLC_CLAUDE_EXEC', None)
        else: os.environ['SDLC_CLAUDE_EXEC'] = saved_ex
        expect(f'case 15 command negative control: the full driver starts the conductor, never solo, got {full}',
               'sdlc-lite:conductor' in full and 'sdlc-lite:solo' not in full)
        for big in ('L4', 'L5', 'XL'):
            try:
                solo_command('h.md', big, 'claude')
                expect(f'case 15: a size {big} ticket has no solo level (Refuse)', False)
            except Refuse:
                pass
        fake = {'kinds': {'T-1': ('solo', 'L2'), 'T-2': ('solo', 'L1'), 'T-3': ('full', None), 'T-4': ('driver', None)}}
        expect('case 15 close: a solo L2 ticket closes with a reason naming the verifier',
               'verifier passed' in (close_reason(fake, Ticket('T-1', 'x', 't')) or ''))
        expect('case 15 close: a solo L1 ticket closes with a reason naming the checks',
               'solo agent (level L1)' in (close_reason(fake, Ticket('T-2', 'x', 't')) or ''))
        expect('case 15 close negative control: a chain or driver ticket closes through its filer, no --reason',
               close_reason(fake, Ticket('T-3', 'x', 't')) is None and close_reason(fake, Ticket('T-4', 'x', 't')) is None)
        # the solo verifier gate reads only a result that is new since the driver started
        vd = tmp / 'verdict-task'
        vd.mkdir()
        before = verifier_files(vd)
        expect('case 15 verdict: no new verifier result is None', solo_verdict(vd, before) is None)
        (vd / 'verifier-L3.md').write_text('<!-- role=verifier level=L3 model=fable effort=xhigh -->\n'
                                           '## Verdict\npass\n\n## Evidence\nran\n\n'
                                           '## For the next attempt\nNone\n', encoding='utf-8')
        expect('case 15 verdict: a stale result present before the driver is ignored',
               solo_verdict(vd, {'verifier-L3.md'}) is None)
        got = solo_verdict(vd, before)
        expect(f'case 15 verdict: a new passing result reads pass, got {got!r}', got == 'pass')
        (vd / 'verifier-L3-2.md').write_text('<!-- role=verifier level=L3 model=fable effort=xhigh -->\n'
                                             '## Verdict\nfail\n\n## Evidence\nbroke\n\n'
                                             '## For the next attempt\nfix it\n', encoding='utf-8')
        got = solo_verdict(vd, before)
        expect(f'case 15 verdict negative control: a newer failing result reads fail, not pass, got {got!r}',
               got == 'fail')
        # T-0398: an older recorded failing result from attempt 1 must not outrank the newer unrecorded one of attempt 2
        vs = tmp / 'verdict-stale'
        vs.mkdir()
        (vs / 'verifier-L2.md').write_text('<!-- role=verifier level=L2 model=opus effort=high -->\n'
                                           '## Verdict\nfail\n\n## Evidence\nbroke\n\n'
                                           '## For the next attempt\nfix it\n', encoding='utf-8')
        (vs / 'verifier-L3.md').write_text('<!-- role=verifier level=L3 model=fable effort=xhigh -->\n'
                                           '## Verdict\npass\n\n## Evidence\nran\n\n'
                                           '## For the next attempt\nNone\n', encoding='utf-8')
        (vs / 'runs.jsonl').write_text('{"role":"verifier","level":"L2","file":"verifier-L2.md"}\n'
                                       '{"role":"solo","level":"L2","file":""}\n', encoding='utf-8')
        got = solo_verdict(vs, set())
        expect(f'case 15 verdict T-0398: an older recorded fail and a newer unrecorded pass read pass, got {got!r}',
               got == 'pass')
        got = solo_verdict(vs, {'verifier-L2.md'})
        expect(f'case 15 verdict T-0398: only the new file counts when the stale one is in the baseline, got {got!r}',
               got == 'pass')
        (vs / 'runs.jsonl').write_text('{"role":"verifier","level":"L3","file":"verifier-L3.md"}\n'
                                       '{"role":"verifier","level":"L2","file":"verifier-L2.md"}\n', encoding='utf-8')
        got = solo_verdict(vs, set())
        expect(f'case 15 verdict T-0398 negative control: both recorded, the later record wins (fail), got {got!r}',
               got == 'fail')
        # cap and stagger
        six = [f'l{k}={tid}' for k, (_slug, tid, _size) in enumerate(sizes, 1)]
        proc = fanout(sr, '--dry-run', '--lanes-dir', str(sl), *six[:5])
        expect(f'case 15 cap: five lanes over the default cap of 4 exit 2 naming --max-lanes, got '
               f'{proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 2 and '--max-lanes 4' in proc.stderr)
        proc = fanout(sr, '--dry-run', '--max-lanes', '5', '--lanes-dir', str(sl), *six[:5])
        expect(f'case 15 cap: --max-lanes 5 accepts five lanes and the plan prints the cap, got '
               f'{proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'at most 5 (--max-lanes' in proc.stdout)
        proc = fanout(sr, '--dry-run', '--max-lanes', '17', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 cap: --max-lanes 17 without --yes-many exits 2 naming --yes-many, got '
               f'{proc.returncode} stderr={proc.stderr!r}', proc.returncode == 2 and '--yes-many' in proc.stderr)
        proc = fanout(sr, '--dry-run', '--max-lanes', '17', '--yes-many', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 cap: --max-lanes 17 --yes-many is accepted, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0)
        proc = fanout(sr, '--dry-run', '--stagger', '-1', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 stagger: a negative stagger exits 2, got {proc.returncode}', proc.returncode == 2)
        proc = fanout(sr, '--dry-run', '--stagger', '7', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 stagger: the plan prints the stagger, got {proc.stdout!r}',
               proc.returncode == 0 and 'stagger: 7.0 s' in proc.stdout)
        starter = tmp / 'start.sh'
        starter.write_text('#!/usr/bin/env bash\nset -eu\npython3 -c "import time;print(time.time())" >"$FANOUT_TICKET.start"\n'
                           'printf \'## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n\' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"\n')
        starter.chmod(0o755)
        spread = {}
        for gap in ('0', '2'):
            gr, gl = tmp / f'stag{gap}', tmp / f'stag{gap}-lanes'
            make_repo(gr, [(s_, f'T-000{i}', 'ready') for i, s_ in enumerate('abc', 1)])
            proc = fanout(gr, 'x=T-0001', 'y=T-0002', 'z=T-0003', '--base', 'main', '--integration', 'fanout/g',
                          '--lanes-dir', str(gl), '--driver', shlex.quote(str(starter)), '--stagger', gap)
            ts = []
            for tid in ('T-0001', 'T-0002', 'T-0003'):  # each lane merged and was closed: read the start on fanout/g
                f = sh(gr, 'show', f'fanout/g:{tid}.start')
                ts.append(float(f.stdout) if f.returncode == 0 and f.stdout.strip() else 0.0)
            spread[gap] = max(ts) - min(ts) if all(ts) else -1
            expect(f'case 15 stagger {gap}: all three lanes ran and merged, got rc={proc.returncode} {proc.stderr!r}',
                   proc.returncode == 0 and all(ts))
        expect(f'case 15 stagger: --stagger 2 spreads three lane starts by at least 3.5 s, got {spread}',
               spread['2'] >= 3.5)
        expect(f'case 15 stagger negative control: --stagger 0 starts them within 2.5 s of each other, got {spread}',
               0 <= spread['0'] < 2.5)
        # overlap refusal (the case 14 fixture): planned scopes that share shared.txt refuse a run
        proc = fanout(pr, '--lanes-dir', str(tmp / 'solo-ovlanes'), '--integration', 'fanout/ov', '--driver', 'true',
                      'alpha=T-0001', 'beta=T-0002')
        expect(f'case 15 overlap: planned scopes sharing shared.txt refuse the run, naming both tickets, got '
               f'{proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 2 and 'T-0001' in proc.stderr and 'T-0002' in proc.stderr
               and 'shared.txt' in proc.stderr and '--allow-overlap' in proc.stderr
               and sh(pr, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        proc = fanout(pr, '--lanes-dir', str(tmp / 'solo-ovlanes2'), '--integration', 'fanout/ov2', '--driver', 'true',
                      'alpha=T-0001', 'beta=T-0004')
        expect(f'case 15 overlap negative control: disjoint planned scopes are not refused, got '
               f'{proc.returncode} stderr={proc.stderr!r}', 'plan to change the same files' not in proc.stderr)

        # 16. A solo lane closes through the real lane decision and the real tickets.py close (T-0222): a
        # `claude` shim on PATH stands in only for the model session; nothing bypasses steps.py lane, the
        # driver choice, the skips.md write, or the skips guard. Negative control: with the Skipped write off,
        # the close is refused and the second ticket never runs.
        shim = tmp / 'shim'
        shim.mkdir()
        (shim / 'claude').write_text('#!/usr/bin/env bash\nset -eu\necho "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"\n'
                                       'echo \'{"type":"result","result":"ok","is_error":false}\'\n')  # T-0346: a stream with no result event now fails
        (shim / 'claude').chmod(0o755)
        shim_env = dict(ENV, PATH=f'{shim}:{ENV.get("PATH", "")}')

        def real_lane(name, disable):
            rr_, ll_ = tmp / f'real-{name}', tmp / f'real-{name}-lanes'
            make_repo(rr_, [('one', 'T-0001', 'ready'), ('two', 'T-0002', 'ready')])
            env_ = dict(shim_env, SDLC_SELFTEST_NO_SKIPPED='1') if disable else shim_env
            proc_ = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', 'x=T-0001,T-0002',
                                    '--base', 'main', '--integration', 'fanout/real', '--lanes-dir', str(ll_),
                                    '--stagger', '0'], cwd=str(rr_), env=env_, capture_output=True, text=True, timeout=300)
            return rr_, ll_, proc_

        rr1, ll1, pr1 = real_lane('on', False)
        st1 = {t_: sh(rr1, 'show', f'fanout/real:.sdlc/{s_}/handoff.md').stdout for t_, s_ in (('T-0001', 'one'), ('T-0002', 'two'))}
        done1 = [t_ for t_, body in st1.items() if re.search(r'^status: done\b', body, re.M)]
        expect(f'case 16 real lane: both solo tickets merge and close with the skips guard live, got rc={pr1.returncode} '
               f'done={done1} out={pr1.stdout[-400:]!r} err={pr1.stderr[-300:]!r}',
               pr1.returncode == 0 and done1 == ['T-0001', 'T-0002'])
        sk = sh(rr1, 'show', 'fanout/real:.sdlc/.0001-one/skips.md').stdout or sh(rr1, 'show', 'fanout/real:.sdlc/one/skips.md').stdout
        expect(f'case 16 real lane: skips.md records lane solo and a ## Skipped entry for planner and filer, got {sk!r}',
               '- lane: solo' in sk and '- skip: planner; step: all;' in sk and '- skip: filer; step: all;' in sk
               and 'decided: lane' in sk)
        rr0, ll0, pr0 = real_lane('off', True)
        expect(f'case 16 negative control: with the Skipped write off the close is refused, got rc={pr0.returncode} '
               f'out={pr0.stdout[-300:]!r}', pr0.returncode == 1 and 'close refused' in pr0.stdout
               and 'no ## Skipped entry' in pr0.stdout)
        # write_solo_skips directly: idempotent, and a forced --lane solo (no lane record) writes nothing
        tdir_ = tmp / 'skiptask'
        tdir_.mkdir()
        (tdir_ / 'skips.md').write_text('# Skips\n\n## Lane\n- lane: solo; point: p; reasons: r\n', encoding='utf-8')
        expect('case 16 write_solo_skips: writes once', write_solo_skips(tdir_, 'L1') is True)
        expect('case 16 write_solo_skips: a second call is a no-op', write_solo_skips(tdir_, 'L1') is False)
        (tdir_ / 'skips.md').write_text('# Skips\n', encoding='utf-8')
        expect('case 16 write_solo_skips negative control: no lane record writes nothing',
               write_solo_skips(tdir_, 'L1') is False and 'skip:' not in (tdir_ / 'skips.md').read_text())

        # 17. Solo lanes are metered (T-0226): solo_command starts through solo_run.py, so a solo lane writes a
        # `role solo` record with the session cost into the ticket's runs.jsonl. A `claude` shim on PATH prints a
        # result event with total_cost_usd and stands in only for the model. Negative control: with the wrapper
        # bypassed (SDLC_SELFTEST_RAW_SOLO restores the raw command) the same lane writes no solo record.
        mshim = tmp / 'metered-shim'
        mshim.mkdir()
        (mshim / 'claude').write_text('#!/usr/bin/env bash\nset -eu\necho "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"\n'
                                      'printf \'%s\' \'{"type":"result","is_error":false,"result":"ok","total_cost_usd":2.5,'
                                      '"duration_ms":10,"num_turns":3,"usage":{"output_tokens":7}}\'\n')
        (mshim / 'claude').chmod(0o755)
        mshim_env = dict(ENV, PATH=f'{mshim}:{ENV.get("PATH", "")}')

        def metered_lane(name, raw):
            rr_, ll_ = tmp / f'meter-{name}', tmp / f'meter-{name}-lanes'
            make_repo(rr_, [('one', 'T-0001', 'ready'), ('two', 'T-0002', 'ready')])
            env_ = dict(mshim_env, SDLC_SELFTEST_RAW_SOLO='1') if raw else mshim_env
            proc_ = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', 'x=T-0001,T-0002',
                                    '--base', 'main', '--integration', 'fanout/meter', '--lanes-dir', str(ll_),
                                    '--stagger', '0'], cwd=str(rr_), env=env_, capture_output=True, text=True, timeout=300)
            recs_ = []
            for s_ in ('one', 'two'):
                for d_ in (s_, '.' + {'one': '0001', 'two': '0002'}[s_] + '-' + s_):
                    body_ = sh(rr_, 'show', f'fanout/meter:.sdlc/{d_}/runs.jsonl').stdout
                    for ln_ in body_.splitlines():
                        try:
                            r_ = json.loads(ln_)
                        except ValueError:
                            continue
                        if isinstance(r_, dict) and r_.get('role') == 'solo':
                            recs_.append(r_)
            return proc_, recs_

        pm, solo_recs = metered_lane('on', False)
        expect(f'case 17 metered lane: both solo tickets merge and close, got rc={pm.returncode} out={pm.stdout[-300:]!r} '
               f'err={pm.stderr[-300:]!r}', pm.returncode == 0)
        expect(f'case 17 metered lane: each solo ticket has one role solo record with cost_usd 2.5, got {solo_recs!r}',
               len(solo_recs) == 2 and all(r_.get('cost_usd') == 2.5 and r_.get('level') in ('L1', 'L2') for r_ in solo_recs))
        pr_raw, raw_recs = metered_lane('off', True)
        expect(f'case 17 negative control: with the wrapper bypassed the lane writes no solo record, got rc={pr_raw.returncode} '
               f'records={raw_recs!r}', pr_raw.returncode == 0 and raw_recs == [])

        # 18. The budget gate (T-0229): a solo lane for a ticket already at 80 percent of its budget with no ack does not
        # start a session; the lane stops as `driver failed rc=4 (budget gate: budget.py ack)`, nothing is merged and the
        # shim is never run. Control: the same fixture with the ticket under 80 percent merges.
        def budget_lane(name, spent):
            rr_, ll_ = tmp / f'budget-{name}', tmp / f'budget-{name}-lanes'
            make_repo(rr_, [('one', 'T-0001', 'ready')])
            h_ = rr_ / '.sdlc' / 'one' / 'handoff.md'
            h_.write_text(h_.read_text().replace('size: S\n', 'size: S\nbudget_usd: 10\n'), encoding='utf-8')
            (rr_ / '.sdlc' / 'one' / 'runs.jsonl').write_text(
                json.dumps({'role': 'solo', 'attempt_id': 'seeded', 'cost_usd': spent}) + '\n', encoding='utf-8')
            for args_ in (('add', '-A'), ('commit', '-q', '-m', 'budget fixture')):
                sh(rr_, *args_)
            proc_ = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', 'x=T-0001',
                                    '--base', 'main', '--integration', 'fanout/budget', '--lanes-dir', str(ll_),
                                    '--stagger', '0'], cwd=str(rr_), env=mshim_env, capture_output=True, text=True,
                                   timeout=300)
            ran_ = (ll_ / 'x' / 'T-0001.txt').exists() or any(ll_.rglob('T-0001.txt'))
            return proc_, ran_

        pb, ran_over = budget_lane('over', 8.0)
        expect(f'case 18 budget gate: an 80 percent ticket does not merge, got rc={pb.returncode}',
               pb.returncode != 0)
        expect(f'case 18 budget gate: outcome names the gate, got out={pb.stdout[-300:]!r}',
               'budget gate' in pb.stdout and 'rc=4' in pb.stdout)
        expect('case 18 budget gate: no solo session started', not ran_over)
        pu, ran_under = budget_lane('under', 7.0)
        expect(f'case 18 control: a 70 percent ticket merges, got rc={pu.returncode} out={pu.stdout[-300:]!r}',
               pu.returncode == 0 and ran_under)

        # case 19: report names the real model per backend; a gate that ran no tests is flagged
        for be, tier, want in (('claude', 'L1', 'sonnet low'), ('claude', 'L2', 'sonnet high'), ('claude', 'L3', 'opus xhigh'),
                               ('codex', 'L1', 'gpt-6.1-sol low'), ('codex', 'L2', 'gpt-6.1-sol high'),
                               ('codex', 'L3', 'gpt-6.1-sol xhigh'), ('claude', 'M', 'sonnet high'), ('codex', 'L', 'gpt-6.1-sol xhigh')):
            got = solo_model_label(tier, be)
            expect(f'case 19 model label: {be} level {tier} is {want!r}, got {got!r}', got == want)
        expect('case 19 codex label is not the Claude model', 'sonnet' not in solo_model_label('L1', 'codex'))
        for rc, text, gate, want in ((0, 'Ran 0 tests in 0.000s\nOK', 'x', True), (5, '', 'python -m pytest', True),
                                     (0, '=== no tests ran in 0.01s ===', 'x', True), (0, 'Ran 3 tests in 0.1s\nOK', 'x', False),
                                     (1, 'Ran 0 tests', 'x', False), (0, '', 'true', False)):
            got = gate_vacuous(rc, text, gate)
            expect(f'case 19 gate_vacuous({rc}, {text[:20]!r}, {gate!r}) is {want}, got {got}', got == want)
        vdrv = ('printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" > "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; '
                'echo work > "$FANOUT_SLUG.txt"')

        def vac_run(name, gate, *extra):
            vr = tmp / f'vac-{name}'
            make_repo(vr, [('a', 'T-0001', 'ready')])
            return fanout(vr, 'alpha=T-0001', '--integration', f'fanout/v{name}', '--lanes-dir', str(tmp / f'vl-{name}'),
                          '--driver', vdrv, '--gate', gate, *extra)

        pv = vac_run('empty', 'echo "Ran 0 tests in 0.000s"')
        expect(f'case 19 vacuous gate: refused, got rc={pv.returncode} out={pv.stdout[-300:]!r}',
               pv.returncode != 0 and 'gate vacuous' in pv.stdout)
        pa = vac_run('allow', 'echo "Ran 0 tests in 0.000s"', '--allow-empty-gate')
        expect(f'case 19 --allow-empty-gate: merges, got rc={pa.returncode} out={pa.stdout[-300:]!r}',
               pa.returncode == 0 and 'gate vacuous' not in pa.stdout.split('| Lane')[-1])
        pn = vac_run('real', 'echo "Ran 3 tests in 0.1s"')
        expect(f'case 19 control: a gate that ran tests merges, got rc={pn.returncode} out={pn.stdout[-300:]!r}',
               pn.returncode == 0)

        # case 20 (T-0259): preflight messages for an uncommitted handoff and a gate worktree without node_modules
        pj = tmp / 'deps-pkg'
        make_repo(pj, [('a', 'T-0001', 'ready')], {'package.json': '{}\n'})
        npj = tmp / 'deps-nopkg'
        make_repo(npj, [('a', 'T-0001', 'ready')])
        for label, repo_, gate, want in (('package.json and a bare gate', pj, 'true', True),
                                         ('gate installs first', pj, 'npm ci && true', False),
                                         ('no package.json', npj, 'true', False)):
            dp = fanout(repo_, '--dry-run', '--lanes-dir', str(tmp / 'dl'), '--integration', 'fanout/d', 'alpha=T-0001',
                        '--gate', gate)
            has = 'npm ci' in dp.stdout and 'note: gates run in a fresh worktree' in dp.stdout
            expect(f'case 20 deps note ({label}): note present is {want}, got rc={dp.returncode} out={dp.stdout!r}',
                   dp.returncode == 0 and has == want)
        for label, repo_, want in (('package.json', pj, True), ('no package.json', npj, False)):
            rp = fanout(repo_, 'alpha=T-0001', '--integration', f'fanout/r{want}', '--lanes-dir', str(tmp / f'rl-{want}'),
                        '--driver', vdrv, '--gate', 'false')
            has = 'no node_modules in the gate worktree' in rp.stdout
            expect(f'case 20 red gate hint ({label}): hint present is {want}, got rc={rp.returncode} out={rp.stdout[-300:]!r}',
                   rp.returncode != 0 and 'red: false rc=1' in rp.stdout and has == want)
        (pj / '.sdlc' / 'b').mkdir()
        (pj / '.sdlc' / 'b' / 'handoff.md').write_text(
            '---\nid: T-0002\ntitle: "Ticket b"\ntype: chore\nstatus: ready\nsize: S\n'
            'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nb\n', encoding='utf-8')
        up = fanout(pj, '--dry-run', '--lanes-dir', str(tmp / 'ul'), '--integration', 'fanout/u', 'alpha=T-0002')
        expect(f'case 20 uncommitted handoff: refused naming git add -f, got rc={up.returncode} err={up.stderr!r}',
               up.returncode == 2 and 'not committed' in up.stderr and 'git add -f' in up.stderr)

        # case 21 (T-0303): each --gate runs through gate_lock.py; --no-gate-lock and SDLC_GATE_SLOTS=0 skip it
        gprobe = ('echo "W=[$SDLC_GATE_WORKERS] H=[$SDLC_GATE_LOCK_HELD]"; ' + shlex.quote(sys.executable) + ' '
                  + shlex.quote(str(SCRIPTS / 'gate_lock.py')) + ' context --json 2>/dev/null; echo; echo "Ran 1 tests"')

        def gate_run(name, *extra, **extra_env):
            gr = tmp / f'gl-{name}'
            make_repo(gr, [('a', 'T-0001', 'ready')])
            pr = fanout(gr, 'alpha=T-0001', '--integration', f'fanout/g{name}', '--lanes-dir', str(tmp / f'gll-{name}'),
                        '--driver', vdrv, '--gate', gprobe, *extra, **extra_env)
            log = tmp / f'gll-{name}' / 'logs' / 'gate-alpha-T-0001-1-a1.log'
            return pr, log.read_text() if log.is_file() else ''

        for name, extra, env_extra, workers, locked in (
                ('on', (), {}, '3', True),
                ('slots3', (), {'SDLC_GATE_SLOTS': '3'}, '2', True),
                ('flag', ('--no-gate-lock',), {}, '', False),
                ('zero', (), {'SDLC_GATE_SLOTS': '0'}, '', False)):
            pr, text = gate_run(name, *extra, **env_extra)
            expect(f'case 21 {name}: merges, got rc={pr.returncode} out={pr.stdout[-300:]!r}', pr.returncode == 0)
            expect(f'case 21 {name}: the gate saw SDLC_GATE_WORKERS=[{workers}], log={text!r}', f'W=[{workers}]' in text)
            expect(f'case 21 {name}: lock marker is {"set" if locked else "unset"}, log={text!r}',
                   (' H=[1]' in text) == locked)
            expect(f'case 21 {name}: the grant context names the lane and ticket is {locked}, log={text!r}',
                   ('"name": "alpha/T-0001"' in text) == locked)

        # case 22 (T-0285): prep prints the lane and the dispatch JSON per ticket, refuses what run refuses, creates nothing
        gi = '.worktrees/\n.claude/worktrees/\n'

        def verb(cwd, name, *args, **extra_env):
            return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), name, *args], cwd=str(cwd),
                                  env=gate_env(**extra_env), capture_output=True, text=True, timeout=300)

        def dispatch_of(text, tid):
            at = text.index(f'dispatch {tid}:\n') + len(f'dispatch {tid}:\n')
            return json.JSONDecoder().raw_decode(text[at:].lstrip())[0]

        def sized_repo(path, sizes, extra=None):
            make_repo(path, [(f't{k}', f'T-000{k}', 'ready') for k in range(1, len(sizes) + 1)], extra)
            for k, size in enumerate(sizes, 1):
                hp = path / '.sdlc' / f't{k}' / 'handoff.md'
                hp.write_text(hp.read_text().replace('size: S\n', f'size: {size}\n'), encoding='utf-8')
            for args_ in (('add', '-A'), ('commit', '-q', '-m', 'sizes')):
                sh(path, *args_)

        p1 = tmp / 'prep1'
        sized_repo(p1, ['L1', 'L2', 'S'], {'.gitignore': gi})  # levels, and the alias S read as L1
        pl1 = tmp / 'prep1-lanes'
        main_p1 = sh(p1, 'rev-parse', 'main').stdout.strip()
        pp = verb(p1, 'prep', 'alpha=T-0001,T-0002', 'beta=T-0003', '--lanes-dir', str(pl1), '--integration', 'fanout/p',
                  '--gate', 'true', '--stagger', '0', SDLC_HEADLESS='')
        expect(f'case 22 prep: exits 0, got {pp.returncode} out={pp.stdout[-400:]!r} err={pp.stderr!r}', pp.returncode == 0)
        expect('case 22 prep: one lane line per ticket with its level, the alias S as L1',
               pp.stdout.count('lane: solo, level L1: sonnet low') == 2 and 'lane: solo, level L2: sonnet high' in pp.stdout)
        try:
            d1, d2 = dispatch_of(pp.stdout, 'T-0001'), dispatch_of(pp.stdout, 'T-0002')
        except (ValueError, KeyError) as e:
            d1 = d2 = {}
            expect(f'case 22 prep: the dispatch JSON parses, got {e!r} in {pp.stdout!r}', False)
        expect(f'case 22 prep: T-0001 dispatch names the sub-agent, model and worktree isolation, got {d1}',
               d1.get('name') == 'T-0001-solo' and d1.get('subagent_type') == 'sdlc-lite:solo-L1'
               and d1.get('model') == 'sonnet' and d1.get('isolation') == 'worktree'
               and d1.get('run_in_background') is True and d1.get('branch') == 'worktree-T-0001-solo'
               and d1.get('worktree') == '.claude/worktrees/T-0001-solo')
        expect(f'case 22 prep: the brief carries the commit instruction `<id>: <title>`, got {d1.get("prompt")!r}',
               'final commit `T-0001: Ticket t1`' in d1.get('prompt', '') and 'Never push' in d1.get('prompt', '')
               and 'Never commit' not in d1.get('prompt', ''))
        # T-0438: the host makes the worktree from origin/main, so the brief syncs it to the local base before the solo reads the ticket
        expect(f'case 22 prep: the brief starts with `git merge --ff-only <base sha>` (negative control: a wrong sha is absent), got {d1.get("prompt")!r}',
               f'`git merge --ff-only {main_p1}`' in d1.get('prompt', '') and d1.get('base_sha') == main_p1
               and d1.get('prompt', '').splitlines()[1].startswith('Handoff: ') and '--ff-only 0000' not in d1.get('prompt', ''))
        expect(f'case 22 prep: level L1 has no verifier, level L2 prepares verifier L2 (negative control: not L3) against the '
               f'worktree, got {d1.get("verifier")!r} {d2.get("verifier")!r}',
               d1.get('verifier') is None and d2.get('subagent_type') == 'sdlc-lite:solo-L2'
               and 'prepare --solo-model sonnet verifier L2 .claude/worktrees/T-0002-solo/.sdlc/t2/handoff.md' in (d2.get('verifier') or '')
               and 'verifier L3' not in (d2.get('verifier') or ''))
        # T-0356: the positive control: a `verifier: L3` line in the handoff prepares verifier L3; the others stay L2
        pv = tmp / 'prep-verifier'
        sized_repo(pv, ['L2', 'L2', 'L2'], {'.gitignore': gi})
        for k, extra_line in ((2, '\nverifier: L3\n'), (3, '\n## Acceptance criteria\n- [ ] the exact label reads `cost`\n')):
            hv = pv / '.sdlc' / f't{k}' / 'handoff.md'
            hv.write_text(hv.read_text() + extra_line, encoding='utf-8')
        for args_ in (('add', '-A'), ('commit', '-q', '-m', 'verifier marks')):
            sh(pv, *args_)
        pvp = verb(pv, 'prep', 'alpha=T-0001,T-0002,T-0003', '--lanes-dir', str(tmp / 'pv-lanes'), '--integration', 'fanout/pv',
                   '--stagger', '0')
        try:
            vv = {x: dispatch_of(pvp.stdout, x).get('verifier') or '' for x in ('T-0001', 'T-0002', 'T-0003')}
        except (ValueError, KeyError) as e:
            vv = {}
            expect(f'case 22 verifier level: the dispatch JSON parses, got {e!r} in {pvp.stdout[-400:]!r}', False)
        expect(f'case 22 verifier level: a plain L2 ticket prepares verifier L2; a `verifier: L3` line and an exact-label '
               f'criterion prepare verifier L3, got {vv}',
               '--solo-model sonnet verifier L2 ' in vv.get('T-0001', '') and '--solo-model sonnet verifier L3 ' in vv.get('T-0002', '')
               and '--solo-model sonnet verifier L3 ' in vv.get('T-0003', ''))
        hp1 = p1 / '.sdlc' / 't2' / 'handoff.md'
        saved_backend = os.environ.pop('SDLC_BACKEND', None)
        try:
            claude_level = solo_verifier(hp1)
            os.environ['SDLC_BACKEND'] = 'codex'
            codex_level = solo_verifier(hp1)
        finally:
            os.environ.pop('SDLC_BACKEND', None)
            if saved_backend is not None:
                os.environ['SDLC_BACKEND'] = saved_backend
        expect(f'case 22 verifier level: a plain L2 ticket is L2 on Claude; off the Claude host it stays L3 (the replay measured '
               f'Claude only), got {claude_level} {codex_level}', claude_level == 'L2' and codex_level == 'L3')
        expect('case 22 prep: each ticket gets its land command naming the branch, the ticket, the base and the gate',
               all(f'land worktree-{x}-solo --ticket {x}' in pp.stdout for x in ('T-0001', 'T-0002', 'T-0003'))
               and f'--base {main_p1}' in pp.stdout and '--gate true' in pp.stdout)
        p1_files = [ln for ln in sh(p1, 'status', '--porcelain', '--untracked-files=all', '--ignored').stdout.splitlines()
                    if not ln.endswith(('-solo.dispatch.json', '/runs.jsonl', '.worktrees/lanes.lock'))
                    and not re.fullmatch(r'!! \.worktrees/host/T-000[123]-solo\.lane\.json', ln)]
        expect(f'case 22 prep: creates no branch, worktree, lanes dir or file in the repo but the dispatch records and the host '
               f'lane records (T-0452), got {p1_files}',
               sh(p1, 'branch', '--list', 'fanout/*', 'worktree-*').stdout.strip() == ''
               and len(sh(p1, 'worktree', 'list').stdout.splitlines()) == 1 and not pl1.exists() and p1_files == []
               and all((p1 / '.worktrees' / 'host' / f'{x}-solo.lane.json').is_file() for x in ('T-0001', 'T-0002', 'T-0003')))
        # T-0363: the list title is line 1 (ticket id first, at most 50 characters), Handoff is line 2, the description 3 to 5 words.
        for dd_ in (d1, d2):
            pl_ = dd_.get('prompt', '').splitlines()
            print(f"  list row: {dd_.get('name'):<26} | {pl_[0] if pl_ else '':<50} | {dd_.get('description')}")
        expect('case 22 prep: line 1 is a title of at most 50 characters starting with the ticket id, line 2 is Handoff, the description is 3 to 5 words',
               all(len(dd_['prompt'].splitlines()[0]) <= 50 and dd_['prompt'].startswith(dd_['ticket'] + ' ')
                   and dd_['prompt'].splitlines()[1].startswith('Handoff: ') and 3 <= len(dd_['description'].split()) <= 5 for dd_ in (d1, d2))
               and d1['name'][:24] != d2['name'][:24])
        # T-0326: both lane prompts pass the spawn gate; the same prompt without its Handoff line is still refused
        def gate_rc(d, prompt):
            ev = json.dumps({'tool_name': 'Agent', 'agent_type': 'sdlc-lite:conductor', 'cwd': str(p1), 'tool_input': {
                'subagent_type': d.get('subagent_type'), 'name': d.get('name'), 'model': d.get('model'), 'prompt': prompt}})
            return subprocess.run(['bash', str(PLUGIN / 'hooks' / 'block-role-spawn.sh')], input=ev, capture_output=True, text=True).returncode
        nohand = lambda d: '\n'.join(ln for ln in d.get('prompt', '').splitlines() if not ln.startswith('Handoff: '))
        expect('case 22 prep: both lane prompts pass the spawn gate, one without its Handoff line is refused',
               gate_rc(d1, d1.get('prompt', '')) == 0 and gate_rc(d2, d2.get('prompt', '')) == 0
               and gate_rc(d1, nohand(d1)) == 2 and gate_rc(d2, nohand(d2)) == 2)
        ph = verb(p1, 'prep', 'alpha=T-0001', '--lanes-dir', str(pl1), '--integration', 'fanout/p', '--stagger', '0',
                  SDLC_HEADLESS='1')
        expect('case 22 prep: a headless parent gets a foreground spawn (run_in_background false)',
               ph.returncode == 0 and dispatch_of(ph.stdout, 'T-0001').get('run_in_background') is False)
        pf = verb(p1, 'prep', 'alpha=T-0001,T-0002', '--lane', 'full', '--lanes-dir', str(pl1), '--integration', 'fanout/p',
                  '--stagger', '0')
        expect(f'case 22 prep --lane full: no dispatch JSON, the parent drives the chain against the lane tree with a '
               f'Tree: line, got rc={pf.returncode} out={pf.stdout!r}',
               pf.returncode == 0 and 'dispatch T-0001' not in pf.stdout and 'full: driven by the parent conductor' in pf.stdout
               and f'`Tree: {pl1 / "alpha"}`' in pf.stdout
               and (f'lanes.py open alpha --kind fanout --ticket T-0001 --ticket T-0002 --base {main_p1} --into fanout/p '
                    f'--path {pl1 / "alpha"} --branch fanout/p-alpha --no-claim') in pf.stdout
               and f'merge --ff --no-edit fanout/p' in pf.stdout and 'commit -m \'T-0001: Ticket t1\'' in pf.stdout)
        # budget gate: an 80 percent ticket gets no dispatch and prep exits 4 (control: the others still print)
        pb1 = tmp / 'prep-budget'
        sized_repo(pb1, ['S', 'S'], {'.gitignore': gi})
        hb = pb1 / '.sdlc' / 't1' / 'handoff.md'
        hb.write_text(hb.read_text().replace('size: S\n', 'size: S\nbudget_usd: 10\n'), encoding='utf-8')
        (pb1 / '.sdlc' / 't1' / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'attempt_id': 'seeded', 'cost_usd': 8.0}) + '\n')
        for args_ in (('add', '-A'), ('commit', '-q', '-m', 'budget')):
            sh(pb1, *args_)
        pbg = verb(pb1, 'prep', 'alpha=T-0001', 'beta=T-0002', '--lanes-dir', str(tmp / 'pbl'), '--stagger', '0')
        expect(f'case 22 prep budget gate: T-0001 is blocked with no dispatch, T-0002 dispatches, exit 4, got rc={pbg.returncode} '
               f'out={pbg.stdout[-500:]!r}', pbg.returncode == 4 and 'budget gate: budget.py ack' in pbg.stdout
               and 'dispatch T-0001:' not in pbg.stdout and 'dispatch T-0002:' in pbg.stdout)

        # prep refuses what run refuses: the same message and exit 2, nothing created (dry-run parity)
        pu = tmp / 'prep-unignored'
        sized_repo(pu, ['S'], {'.gitignore': '.worktrees/\n'})
        puo = verb(pu, 'prep', 'alpha=T-0001', '--lanes-dir', str(tmp / 'pul'), '--stagger', '0')
        expect(f'case 22 prep: .claude/worktrees/ not ignored exits 2 naming it and .gitignore, got rc={puo.returncode} '
               f'err={puo.stderr!r}', puo.returncode == 2 and '.claude/worktrees/' in puo.stderr and '.gitignore' in puo.stderr)
        pr_ov = tmp / 'prep-overlap'
        sized_repo(pr_ov, ['S', 'S'], {'.gitignore': gi})
        for slug in ('t1', 't2'):
            sd = pr_ov / '.sdlc' / slug / 'step-1'
            sd.mkdir(parents=True)
            sd.joinpath('handoff.md').write_text(
                '## Step 1\n### Acceptance criteria\n- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | '
                'grep -vxF -e shared.txt)"`\n', encoding='utf-8')
        for args_ in (('add', '-A'), ('commit', '-q', '-m', 'scopes')):
            sh(pr_ov, *args_)
        pr_unc = tmp / 'prep-uncommitted'
        sized_repo(pr_unc, ['S'], {'.gitignore': gi})
        (pr_unc / '.sdlc' / 'x').mkdir()
        (pr_unc / '.sdlc' / 'x' / 'handoff.md').write_text(
            '---\nid: T-0002\ntitle: "Ticket x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\n'
            'created: 2026-01-01\n---\n\n## Goal\nx\n', encoding='utf-8')
        for label, repo_, args_, want in (
                ('planned-scope overlap', pr_ov, ('alpha=T-0001', 'beta=T-0002'), 'plan to change the same files'),
                ('an uncommitted handoff', pr_unc, ('alpha=T-0002',), 'not committed at'),
                ('--max-lanes 1 with two lanes', p1, ('alpha=T-0001', 'beta=T-0003', '--max-lanes', '1'), 'exceed --max-lanes 1'),
                ('one id in two lanes', p1, ('alpha=T-0001', 'beta=T-0001'), 'appears in lane alpha and lane beta'),
                ('an unknown id', pr_unc, ('alpha=T-0009',), 'no ticket under')):
            lanes_arg = ('--lanes-dir', str(tmp / 'parity-lanes'), '--integration', 'fanout/par')
            run_o = fanout(repo_, *args_, *lanes_arg, '--driver', 'exit 3')
            prep_o = verb(repo_, 'prep', *args_, *lanes_arg, '--stagger', '0')
            expect(f'case 22 parity ({label}): run and prep both exit 2 with the same message, got run '
                   f'{run_o.returncode} {run_o.stderr!r} prep {prep_o.returncode} {prep_o.stderr!r}',
                   run_o.returncode == 2 and prep_o.returncode == 2 and run_o.stderr == prep_o.stderr
                   and want in prep_o.stderr)
        expect('case 22 parity: the refusals created no branch, worktree or lanes dir',
               sh(pr_ov, 'branch', '--list', 'fanout/*').stdout.strip() == '' and not (tmp / 'parity-lanes').exists()
               and len(sh(pr_ov, 'worktree', 'list').stdout.splitlines()) == 1)
        po = verb(pr_ov, 'prep', 'alpha=T-0001', 'beta=T-0002', '--allow-overlap', '--lanes-dir', str(tmp / 'pol'), '--stagger', '0')
        expect(f'case 22 parity control: --allow-overlap lets prep print the plan, got rc={po.returncode} err={po.stderr!r}',
               po.returncode == 0 and 'overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt' in po.stdout)

        # case 23 (T-0285): land merges one sub-agent branch behind the locked merge, gates and close
        ld = tmp / 'land'
        sized_repo(ld, ['L1', 'L2', 'S', 'S', 'S', 'S', 'S'], {'.gitignore': gi})
        main_ld = sh(ld, 'rev-parse', 'main').stdout.strip()

        def make_branch(repo_, branch, files, msg=None):
            sh(repo_, 'checkout', '-q', '-b', branch, 'main')
            for name, body in files.items():
                path_ = repo_ / name
                path_.parent.mkdir(parents=True, exist_ok=True)
                path_.write_text(body, encoding='utf-8')
            if files:
                sh(repo_, 'add', '-A')
                sh(repo_, 'commit', '-q', '-m', msg or branch)
            sh(repo_, 'checkout', '-q', 'main')

        lanes_l, integ = tmp / 'land-lanes', 'fanout/l'
        pin = ('--integration', integ, '--lanes-dir', str(lanes_l), '--base', 'main')
        make_branch(ld, 'worktree-T-0001-solo', {'f1.txt': 'one\n'}, 'T-0001: Ticket t1')
        make_branch(ld, 'worktree-T-0003-solo', {'f3.txt': 'three\n'}, 'T-0003: Ticket t3')
        l1 = verb(ld, 'land', 'worktree-T-0001-solo', *pin, '--gate', 'test -e f1.txt')
        expect(f'case 23 land: a green gate merges and closes, got rc={l1.returncode} out={l1.stdout[-500:]!r} err={l1.stderr!r}',
               l1.returncode == 0 and '| t-0001-solo | T-0001 | merged |' in l1.stdout)
        expect('case 23 land: the integration branch holds f1.txt and the ticket is done there, main is untouched',
               sh(ld, 'cat-file', '-e', f'{integ}:f1.txt').returncode == 0
               and re.search(r'^status: done\b', sh(ld, 'show', f'{integ}:.sdlc/t1/handoff.md').stdout, re.M)
               and sh(ld, 'rev-parse', 'main').stdout.strip() == main_ld and sh(ld, 'status', '--porcelain').stdout == '')
        subjects = sh(ld, 'log', '--format=%s', integ).stdout.splitlines()
        expect(f'case 23 land: the merge commit and the `close <id>` commit are on the integration branch, got {subjects[:4]}',
               'Merge worktree-T-0001-solo: T-0001' in subjects and 'close T-0001' in subjects)
        expect('case 23 land: the report carries the Lane line with the level and model',
               '- Lane for `T-0001`: solo (level L1: sonnet low)' in l1.stdout)
        expect('case 23 land: the solo lane is recorded in the ticket skips.md on the integration branch',
               '- lane: solo' in sh(ld, 'show', f'{integ}:.sdlc/t1/skips.md').stdout)
        l3 = verb(ld, 'land', 'worktree-T-0003-solo', *pin, '--gate', 'test -e f1.txt && test -e f3.txt')
        rep_ld = (lanes_l / 'report.md').read_text() if (lanes_l / 'report.md').is_file() else ''
        expect(f'case 23 land: a second land reuses the integration worktree, gates against both, and the report lists both, '
               f'got rc={l3.returncode} out={l3.stdout[-400:]!r} err={l3.stderr!r}',
               l3.returncode == 0 and '| t-0001-solo | T-0001 | merged |' in rep_ld and '| t-0003-solo | T-0003 | merged |' in rep_ld
               and sh(ld, 'rev-list', '--merges', '--count', integ).stdout.strip() == '2')
        def pruned(repo_):
            try:
                return [e['name'] for e in json.loads((repo_ / '.sdlc' / 'runtime' / 'prune.json').read_text())]
            except (OSError, ValueError):
                return []
        expect(f'case 23 land prune (T-0368): a merged solo is queued for pruning in the project, got {pruned(ld)}',
               pruned(ld) == ['T-0001-solo', 'T-0003-solo'] and 'prune: T-0003-solo' in l3.stdout + l3.stderr)
        make_branch(ld, 'worktree-T-0004-solo', {'f4.txt': 'four\n'}, 'T-0004: Ticket t4')
        tip_before = sh(ld, 'rev-parse', integ).stdout.strip()
        lr = verb(ld, 'land', 'worktree-T-0004-solo', *pin, '--gate', 'false')
        expect(f'case 23 land: a red gate reports red and resets the merge, got rc={lr.returncode} out={lr.stdout[-300:]!r}',
               lr.returncode == 1 and 'red: false rc=1' in lr.stdout and sh(ld, 'rev-parse', integ).stdout.strip() == tip_before
               and sh(ld, 'cat-file', '-e', f'{integ}:f4.txt').returncode != 0
               and re.search(r'^status: ready\b', sh(ld, 'show', f'{integ}:.sdlc/t4/handoff.md').stdout, re.M))
        expect(f'case 23 land prune (T-0368): a land that did not merge queues nothing (negative control), got {pruned(ld)}',
               'T-0004-solo' not in pruned(ld))
        lv = verb(ld, 'land', 'worktree-T-0004-solo', *pin, '--gate', 'echo "Ran 0 tests in 0.000s"')
        expect(f'case 23 land: a gate that ran no tests is refused, got rc={lv.returncode} out={lv.stdout[-300:]!r}',
               lv.returncode == 1 and 'gate vacuous' in lv.stdout and sh(ld, 'rev-parse', integ).stdout.strip() == tip_before)
        la = verb(ld, 'land', 'worktree-T-0004-solo', *pin, '--gate', 'echo "Ran 0 tests in 0.000s"', '--allow-empty-gate')
        expect(f'case 23 land: --allow-empty-gate merges it, got rc={la.returncode} out={la.stdout[-300:]!r}',
               la.returncode == 0 and '| t-0004-solo | T-0004 | merged |' in la.stdout)
        sh(ld, 'branch', 'worktree-T-0005-solo', 'main')  # a stub sub-agent that never committed
        tip_before = sh(ld, 'rev-parse', integ).stdout.strip()
        ln = verb(ld, 'land', 'worktree-T-0005-solo', *pin, '--gate', 'true')
        expect(f'case 23 land: a branch with no commits gives `no changes`, no merge, no close, got rc={ln.returncode} '
               f'out={ln.stdout[-300:]!r}', ln.returncode == 1 and '| t-0005-solo | T-0005 | no changes |' in ln.stdout
               and sh(ld, 'rev-parse', integ).stdout.strip() == tip_before
               and re.search(r'^status: ready\b', sh(ld, 'show', f'{integ}:.sdlc/t5/handoff.md').stdout, re.M))
        # host-style branch name worktree-agent-<id>: the lane comes from the agent_id in the dispatch record
        make_branch(ld, 'worktree-agent-a1b2c3', {'f6.txt': 'six\n', '.sdlc/t6/runs.jsonl':
                    json.dumps({'role': 'solo', 'agent_id': 'a1b2c3'}) + '\n'}, 'T-0006: Ticket t6')
        lh = verb(ld, 'land', 'worktree-agent-a1b2c3', *pin, '--gate', 'test -e f6.txt')
        expect(f'case 23 land host branch: a solo lane is found by agent_id, merged and closed, got rc={lh.returncode} '
               f'out={lh.stdout[-400:]!r} err={lh.stderr!r}', lh.returncode == 0 and 'T-0006 | merged |' in lh.stdout
               and '- Lane for `T-0006`: solo' in lh.stdout
               and re.search(r'^status: done\b', sh(ld, 'show', f'{integ}:.sdlc/t6/handoff.md').stdout, re.M))
        make_branch(ld, 'worktree-agent-zzz', {'fz.txt': 'z\n'}, 'unknown')
        lu = verb(ld, 'land', 'worktree-agent-zzz', *pin, '--gate', 'true')
        expect(f'case 23 land host branch: an unknown agent is refused without --ticket, got rc={lu.returncode} err={lu.stderr!r}',
               lu.returncode == 2 and 'cannot tell which ticket' in lu.stderr)
        # a real solo sub-agent writes no runs.jsonl line in its lane (T-0287 rerun): --ticket alone makes it a solo lane
        lz = verb(ld, 'land', 'worktree-agent-zzz', *pin, '--ticket', 'T-0007', '--gate', 'test -e fz.txt')
        expect(f'case 23 land host branch: no record, --ticket given: solo lane, merged and closed, got rc={lz.returncode} '
               f'out={lz.stdout[-400:]!r}', lz.returncode == 0 and '- Lane for `T-0007`: solo' in lz.stdout)
        # level L2: no verifier result, a failing one, then a passing one on the branch
        make_branch(ld, 'worktree-T-0002-solo', {'f2.txt': 'two\n'}, 'T-0002: Ticket t2')
        lm = verb(ld, 'land', 'worktree-T-0002-solo', *pin, '--gate', 'true')
        expect(f'case 23 land level L2: no verifier result is refused before any merge, got rc={lm.returncode} out={lm.stdout[-300:]!r}',
               lm.returncode == 1 and 'no verifier result' in lm.stdout and sh(ld, 'cat-file', '-e', f'{integ}:f2.txt').returncode != 0)
        vhead = '<!-- role=verifier level=L3 model=fable effort=high -->\n'
        for verdict, want, extra in (('fail', 'verifier fail', ()), ('pass', 'merged', ())):
            sh(ld, 'checkout', '-q', 'worktree-T-0002-solo')
            vpath = ld / '.sdlc' / 't2' / 'verifier-L3.md'
            vpath.write_text(vhead + f'## Verdict\n{verdict}\n', encoding='utf-8')
            sh(ld, 'add', '-A')
            sh(ld, 'commit', '-q', '-m', f'verifier {verdict}')
            sh(ld, 'checkout', '-q', 'main')
            lm = verb(ld, 'land', 'worktree-T-0002-solo', *pin, '--gate', 'true')
            expect(f'case 23 land level L2: a {verdict} verifier gives {want}, got rc={lm.returncode} out={lm.stdout[-300:]!r}',
                   want in lm.stdout and (lm.returncode == 0) == (want == 'merged'))
        expect('case 23 land level L2: the report names the L2 model',
               '- Lane for `T-0002`: solo (level L2: sonnet high)' in lm.stdout)
        # T-0439: a verifier result left uncommitted in the sub-agent worktree (the host's worktree, the record ignored by
        # git) is committed onto the lane by land, so it reaches the integration branch with no hand step
        lw = tmp / 'land-wt'
        sized_repo(lw, ['L2', 'L2'], {'.gitignore': gi + '.sdlc/*/verifier-L*.md\n'})
        lw_pin = ('--integration', 'fanout/w', '--lanes-dir', str(tmp / 'land-wt-lanes'), '--base', 'main')
        for k in (1, 2):
            wt_ = tmp / f'land-wt-agent{k}'
            sh(lw, 'worktree', 'add', '-q', '-b', f'worktree-agent-w{k}', str(wt_), 'main')
            (wt_ / f'w{k}.txt').write_text('w\n', encoding='utf-8')
            sh(wt_, 'add', '-A')
            sh(wt_, 'commit', '-q', '-m', f'T-000{k}: Ticket t{k}')
        (tmp / 'land-wt-agent1' / '.sdlc' / 't1' / 'verifier-L3.md').write_text(vhead + '## Verdict\npass\n', encoding='utf-8')
        (tmp / 'land-wt-agent1' / '.sdlc' / 't1' / 'runs.jsonl').write_text(
            json.dumps({'role': 'verifier', 'level': 'L3', 'model': 'fable', 'file': 'verifier-L3.md'}) + '\n', encoding='utf-8')
        lw1 = verb(lw, 'land', 'worktree-agent-w1', '--ticket', 'T-0001', *lw_pin, '--gate', 'test -e w1.txt')
        expect(f'case 23 land worktree record: an uncommitted verifier result in the lane worktree is carried in, got '
               f'rc={lw1.returncode} out={lw1.stdout[-400:]!r} err={lw1.stderr!r}', lw1.returncode == 0 and 'T-0001 | merged |' in lw1.stdout
               and sh(lw, 'cat-file', '-e', 'fanout/w:.sdlc/t1/verifier-L3.md').returncode == 0
               and sh(lw, 'cat-file', '-e', 'fanout/w:.sdlc/t1/runs.jsonl').returncode == 0)
        lw2 = verb(lw, 'land', 'worktree-agent-w2', '--ticket', 'T-0002', *lw_pin, '--gate', 'test -e w2.txt')
        expect(f'case 23 land worktree record: control, a worktree with no verifier result is still refused, got '
               f'rc={lw2.returncode} out={lw2.stdout[-300:]!r}', lw2.returncode == 1 and 'no verifier result' in lw2.stdout
               and sh(lw, 'cat-file', '-e', 'fanout/w:w2.txt').returncode != 0)
        # refusals, each exit 2 with nothing created
        sh(ld, 'branch', 'weird-branch', 'main')
        for label, args_, want in (('a branch that does not exist', ('no-such-branch',), 'not a local branch'),
                                   ('a branch that names no ticket', ('weird-branch',), '--ticket'),
                                   ('the integration branch itself', (integ, '--ticket', 'T-0001'), 'is the integration branch')):
            lo = verb(ld, 'land', *args_, *pin)
            expect(f'case 23 land refusal ({label}): exit 2 naming {want!r}, got rc={lo.returncode} err={lo.stderr!r}',
                   lo.returncode == 2 and want in lo.stderr and 'Traceback' not in lo.stderr)
        ls_ = verb(ld, 'land', 'weird-branch', '--ticket', 'T-0006', *pin, '--gate', 'true')
        expect(f'case 23 land: --ticket names a ticket on a branch with any name; with no commits it is `no changes`, '
               f'got rc={ls_.returncode} out={ls_.stdout[-200:]!r}', ls_.returncode == 1 and 'no changes' in ls_.stdout)
        lfresh = verb(ld, 'land', 'worktree-T-0006-solo', '--lanes-dir', str(tmp / 'nolanes'), '--integration', 'fanout/none')
        expect(f'case 23 land: an unknown solo branch refuses before creating the lanes dir, got rc={lfresh.returncode}',
               lfresh.returncode == 2 and not (tmp / 'nolanes').exists() and sh(ld, 'branch', '--list', 'fanout/none').stdout.strip() == '')

        # case 24 (T-0285): a --driver stub that commits nothing gives `no changes`; the stub path itself is unchanged
        nc = tmp / 'nochange'
        make_repo(nc, [('a', 'T-0001', 'ready')])
        pn = fanout(nc, 'alpha=T-0001', '--integration', 'fanout/nc', '--lanes-dir', str(tmp / 'nc-lanes'), '--driver', 'true',
                    '--gate', 'true')
        expect(f'case 24 stub that makes no change: outcome `no changes`, no merge, ticket still ready, got rc={pn.returncode} '
               f'out={pn.stdout[-300:]!r}', pn.returncode == 1 and '| alpha | T-0001 | no changes |' in pn.stdout
               and sh(nc, 'rev-list', '--merges', '--count', 'fanout/nc').stdout.strip() == '0')

        # case 25 (T-0339): a lane commit never stages *.log, .run.lock or *.running, keeps the rest
        ar = tmp / 'artifacts'
        sized_repo(ar, ['S'], {'.gitignore': gi})
        pa = fanout(ar, 'alpha=T-0001', '--integration', 'fanout/ar', '--lanes-dir', str(tmp / 'ar-lanes'), '--gate', 'true',
                    '--driver', 'echo k > keep.txt; echo l > verifier-L3.log; : > .run.lock; : > x.running; '
                                'mkdir -p .sdlc/t1; echo l > .sdlc/t1/v.log; echo a > .sdlc/t1/a.attempt.json')
        ls_ar = sh(ar, 'ls-tree', '-r', '--name-only', 'fanout/ar').stdout.split()
        expect(f'case 25 lane commit: artifacts excluded, keep.txt and attempt.json kept, got rc={pa.returncode} '
               f'out={pa.stdout[-300:]!r} tree={ls_ar}',
               'keep.txt' in ls_ar and '.sdlc/t1/a.attempt.json' in ls_ar
               and not [f for f in ls_ar if f.endswith(('.log', '.run.lock', '.running'))])

        # case 26 (T-0341): the printed prep commit command and the skill's verifier commit leave artifacts unstaged
        pr = tmp / 'prepcmd'
        sized_repo(pr, ['S'], {'.gitignore': gi})
        pp = verb(pr, 'prep', 'alpha=T-0001', '--lane', 'full', '--integration', 'fanout/pr', '--lanes-dir', str(tmp / 'pr-lanes'), '--stagger', '0')
        line = next((l for l in pp.stdout.splitlines() if l.strip().startswith('commit: git -C')), '')
        skill = (pathlib.Path(__file__).resolve().parent.parent / 'skills' / 'fanout' / 'SKILL.md').read_text()
        sk = re.search(r'`(git -C <worktree> add [^`]*)`', skill)
        for label, tmpl in (('prep', line.strip()[len('commit: '):]), ('skill', sk.group(1) if sk else '')):
            for flag, cmdtxt in (('new', tmpl), ('old', 'git -C <worktree> add -A && git -C <worktree> commit -m x')):
                lt = tmp / f'c26-{label}-{flag}'
                sh(tmp, 'clone', '-q', str(pr), str(lt))
                sh(lt, 'config', 'user.name', 't'); sh(lt, 'config', 'user.email', 't@example.invalid')
                (lt / 'k.txt').write_text('k'); (lt / 'v.log').write_text('l'); (lt / '.run.lock').write_text('')
                add = re.sub(r'git -C \S+', f'git -C {shlex.quote(str(lt))}', cmdtxt.split(' && ')[0])
                subprocess.run(add, shell=True, capture_output=True)
                staged = sh(lt, 'diff', '--cached', '--name-only').stdout.split()
                bad = [f for f in staged if f.endswith(('.log', '.run.lock'))]
                expect(f'case 26 {label}/{flag}: staged={staged}', 'k.txt' in staged and (bad if flag == 'old' else not bad))

        # case 27 (T-0374): the merge class gates `roll`. A verified lane based on an ancestor of main that touches no
        # path declared in .sdlc/config is rolling and lands on main (main only fast-forwards); a declared path, no
        # verifier result, or a stale base is integration and never reaches main.
        rl = tmp / 'roll'
        sized_repo(rl, ['L1', 'L2', 'L1', 'L1', 'L1'], {'.gitignore': gi, '.sdlc/config': '# hash-bound and generated paths\nhash_bound: gen  # generated\n'})
        main0 = sh(rl, 'rev-parse', 'main').stdout.strip()
        sh(rl, 'checkout', '-q', '-b', 'side', 'main')
        (rl / 'side.txt').write_text('side\n', encoding='utf-8')
        sh(rl, 'add', '-A')
        sh(rl, 'commit', '-q', '-m', 'unlanded side work')
        orphan = sh(rl, 'rev-parse', 'HEAD').stdout.strip()
        sh(rl, 'checkout', '-q', 'main')
        vpass = '<!-- role=verifier level=L2 model=opus effort=high -->\n## Verdict\npass\n'
        make_branch(rl, 'worktree-T-0001-solo', {'r1.txt': 'one\n', '.sdlc/t1/verifier-L2.md': vpass,
                                                  '.sdlc/t1/base-sha': main0 + '\n'}, 'T-0001: Ticket t1')
        make_branch(rl, 'worktree-T-0002-solo', {'gen/out.json': '{}\n', '.sdlc/t2/verifier-L2.md': vpass}, 'T-0002: Ticket t2')
        make_branch(rl, 'worktree-T-0003-solo', {'r3.txt': 'three\n'}, 'T-0003: Ticket t3')
        make_branch(rl, 'worktree-T-0004-solo', {'r4.txt': 'four\n', '.sdlc/t4/verifier-L2.md': vpass,
                                                  '.sdlc/t4/base-sha': orphan + '\n'}, 'T-0004: Ticket t4')
        make_branch(rl, 'worktree-T-0005-solo', {'r5.txt': 'five\n', '.sdlc/t5/verifier-L2.md': vpass}, 'T-0005: Ticket t5')
        rpin = ('--lanes-dir', str(tmp / 'roll-lanes'))
        r1 = verb(rl, 'roll', 'worktree-T-0001-solo', *rpin, '--gate', 'test -e r1.txt')
        main1 = sh(rl, 'rev-parse', 'main').stdout.strip()

        def rolling_gone():
            listed = sh(rl, 'worktree', 'list', '--porcelain').stdout
            return not (tmp / 'roll-lanes' / 'rolling').exists() and '/rolling\n' not in listed and not listed.rstrip().endswith('/rolling')
        gone_after_merge = rolling_gone()
        expect(f'case 27 roll: a verified lane on an ancestor of main touching no declared path is rolling and merged, '
               f'got rc={r1.returncode} out={r1.stdout[-500:]!r} err={r1.stderr[-300:]!r}',
               r1.returncode == 0 and 'T-0001 merged' in r1.stdout)
        expect('case 27 roll: main fast-forwarded to the merge and the close, the checkout followed, the ticket is done on main',
               main1 != main0 and sh(rl, 'merge-base', '--is-ancestor', main0, main1).returncode == 0
               and sh(rl, 'cat-file', '-e', 'main:r1.txt').returncode == 0 and (rl / 'r1.txt').is_file()
               and sh(rl, 'status', '--porcelain').stdout == ''
               and re.search(r'^status: done\b', sh(rl, 'show', 'main:.sdlc/t1/handoff.md').stdout, re.M)
               and {'Merge worktree-T-0001-solo: T-0001', 'close T-0001'} <= set(sh(rl, 'log', '--format=%s', 'main').stdout.splitlines()))
        for tid, want in (('T-0002', 'integration (hash-bound gen/out.json)'), ('T-0003', 'integration (unverified)'),
                          ('T-0004', f'integration (stale base {orphan[:7]})')):
            ro = verb(rl, 'roll', f'worktree-{tid}-solo', *rpin, '--gate', 'true')
            expect(f'case 27 roll: {tid} is {want} and never lands, got rc={ro.returncode} out={ro.stdout[-400:]!r} '
                   f'err={ro.stderr[-300:]!r}', ro.returncode == 1 and want in ro.stdout
                   and sh(rl, 'rev-parse', 'main').stdout.strip() == main1
                   and re.search(r'^status: ready\b', sh(rl, 'show', f'main:.sdlc/t{tid[-1]}/handoff.md').stdout, re.M))
            if tid == 'T-0002':
                expect(f'case 31 roll scratch: after a merged roll and after a refused roll ({tid}, exit 1) <lanes-dir>/rolling '
                       f'is absent and git worktree list names no rolling tree, got after merge {gone_after_merge}, after the '
                       f'refusal {rolling_gone()}: {sh(rl, "worktree", "list", "--porcelain").stdout!r}',
                       gone_after_merge and rolling_gone())
        (rl / 'r5.txt').write_text('a local file the fast-forward would overwrite\n', encoding='utf-8')
        r5 = verb(rl, 'roll', 'worktree-T-0005-solo', *rpin, '--gate', 'true')
        expect(f'case 27 roll: a fast-forward git refuses leaves main and the local file alone, got rc={r5.returncode} '
               f'out={r5.stdout[-400:]!r}', r5.returncode == 1 and 'main not advanced' in r5.stdout
               and sh(rl, 'rev-parse', 'main').stdout.strip() == main1 and (rl / 'r5.txt').read_text().startswith('a local'))
        (rl / 'r5.txt').unlink()
        r5 = verb(rl, 'roll', 'worktree-T-0005-solo', *rpin, '--gate', 'test -e r1.txt && test -e r5.txt')
        expect(f'case 27 roll: a lane cut before main moved still rolls (the merge is made, main fast-forwards), '
               f'got rc={r5.returncode} out={r5.stdout[-400:]!r} err={r5.stderr[-300:]!r}',
               r5.returncode == 0 and sh(rl, 'cat-file', '-e', 'main:r5.txt').returncode == 0
               and sh(rl, 'merge-base', '--is-ancestor', main1, 'main').returncode == 0)
        # negative control: with the hash_bound line gone, T-0002 is rolling, so the class came from .sdlc/config
        (rl / '.sdlc' / 'config').write_text('# nothing declared\n', encoding='utf-8')
        r2 = verb(rl, 'roll', 'worktree-T-0002-solo', *rpin, '--gate', 'true')
        expect(f'case 27 roll negative control: no declared path makes T-0002 rolling, got rc={r2.returncode} '
               f'out={r2.stdout[-300:]!r}', r2.returncode == 0 and sh(rl, 'cat-file', '-e', 'main:gen/out.json').returncode == 0)
        for label, args_, want in (('main itself', ('main', '--ticket', 'T-0003'), 'is main'),
                                   ('a branch that names no ticket', ('side',), '--ticket')):
            ro = verb(rl, 'roll', *args_, *rpin)
            expect(f'case 27 roll refusal ({label}): exit 2 naming {want!r}, got rc={ro.returncode} err={ro.stderr!r}',
                   ro.returncode == 2 and want in ro.stderr and 'Traceback' not in ro.stderr)

        # case 28 (T-0438, T-0452): settle brings the integration branch back and closes its tree through lanes.py (the
        # archive ref first), so the next prep starts at the current tip
        sv = tmp / 'settle'
        sized_repo(sv, ['L1', 'L1', 'L1'], {'.gitignore': gi})
        sv_lanes = tmp / 'settle-lanes'

        def integration_with(name, fname, lanes_dir=True):
            """An integration branch with one commit, its tree at <lanes dir>/<n>/integration beside merge.lock and logs/
            as fanout makes it, or (lanes_dir False) a plain worktree outside any lanes dir."""
            sh(sv, 'branch', name, 'main')
            wt_ = sv_lanes / name.replace('/', '-') / 'integration' if lanes_dir else tmp / 'settle-plain' / name.replace('/', '-')
            sh(sv, 'worktree', 'add', '-q', str(wt_), name)
            if lanes_dir:
                (wt_.parent / 'logs').mkdir(exist_ok=True)
                (wt_.parent / 'merge.lock').touch()
            (wt_ / fname).write_text('x\n', encoding='utf-8')
            sh(wt_, 'add', '-A')
            sh(wt_, 'commit', '-q', '-m', f'lane work {fname}')
            return wt_, sh(sv, 'rev-parse', name).stdout.strip()

        def archive_at(name, tip):
            ref = archived(sv, name)
            return bool(re.fullmatch(r'refs/archive/\d{4}-\d{2}-\d{2}/' + re.escape(name), ref)) and \
                sh(sv, 'rev-parse', f'{ref}^{{commit}}').stdout.strip() == tip
        wt_a, tip_a = integration_with('fanout/ff', 'a.txt')
        (wt_a / '.sdlc' / 'config').write_text('# copied, untracked\n', encoding='utf-8')  # land copies it; --force removes it
        st = verb(sv, 'settle', 'fanout/ff')
        expect(f'case 28 settle archive: a fast-forward integration branch is merged into main, refs/archive/<UTC date>/fanout/ff '
               f'is written at its tip, its tree (with an untracked .sdlc/config) is removed and its branch deleted, '
               f'got rc={st.returncode} out={st.stdout!r} err={st.stderr!r}',
               st.returncode == 0 and sh(sv, 'rev-parse', 'main').stdout.strip() == tip_a and not wt_a.exists()
               and sh(sv, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/ff').returncode != 0
               and archive_at('fanout/ff', tip_a) and 'closed integration (ancestor)' in st.stdout)
        wt_b, tip_b = integration_with('fanout/hand', 'b.txt')
        (sv / 'c.txt').write_text('c\n', encoding='utf-8')
        sh(sv, 'add', '-A')
        sh(sv, 'commit', '-q', '-m', 'main moved')
        sh(sv, 'merge', '-q', '--no-ff', '-m', 'merge by hand', 'fanout/hand')
        st = verb(sv, 'settle', 'fanout/hand')
        expect(f'case 28 settle archive: a branch the maintainer already merged with a non-ff merge is only retired (main '
               f'untouched) and archived at refs/archive/<UTC date>/fanout/hand, got rc={st.returncode} out={st.stdout!r} '
               f'err={st.stderr!r}',
               st.returncode == 0 and not wt_b.exists() and sh(sv, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/hand').returncode != 0
               and sh(sv, 'merge-base', '--is-ancestor', tip_b, 'main').returncode == 0 and archive_at('fanout/hand', tip_b))
        wt_c, tip_c = integration_with('fanout/div', 'd.txt')
        (sv / 'e.txt').write_text('e\n', encoding='utf-8')
        sh(sv, 'add', '-A')
        sh(sv, 'commit', '-q', '-m', 'main moved again')
        main_c = sh(sv, 'rev-parse', 'main').stdout.strip()
        st = verb(sv, 'settle', 'fanout/div')
        expect(f'case 28 settle negative control: a diverged integration branch is refused (exit 2) and left whole, '
               f'got rc={st.returncode} err={st.stderr!r}',
               st.returncode == 2 and 'not a fast-forward' in st.stderr and wt_c.exists()
               and sh(sv, 'rev-parse', 'fanout/div').stdout.strip() == tip_c and sh(sv, 'rev-parse', 'main').stdout.strip() == main_c
               and not archived(sv, 'fanout/div'))
        wt_o, tip_o = integration_with('fanout/plain', 'o.txt', lanes_dir=False)
        st = verb(sv, 'settle', 'fanout/plain')
        expect(f'case 28 settle archive negative control: a tree outside a lanes dir is not a plugin lane: it is kept with '
               f'`lane still open` and exit 1, its branch kept and nothing archived, got rc={st.returncode} out={st.stdout!r} '
               f'err={st.stderr!r}',
               st.returncode == 1 and f'lane still open: {wt_o}' in st.stdout and wt_o.exists()
               and sh(sv, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/plain').returncode == 0
               and not archived(sv, 'fanout/plain'))
        st = verb(sv, 'settle', 'fanout/none')
        expect(f'case 28 settle: an absent branch is nothing to settle (exit 0), got rc={st.returncode}', st.returncode == 0 and 'nothing to settle' in st.stdout)

        # 29. Lane lifecycle (T-0452): the run sweeps landed plugin lanes at its start (unless lane_sweep: off), opens
        # each lane through lanes.py with a port from lane_ports:, closes a lane whose every ticket merged (its archive
        # ref first), and keeps a stopped lane with its report line.
        lstub = tmp / 'lifecycle-stub.sh'
        lstub.write_text('#!/usr/bin/env bash\nset -eu\n'
                         'echo "${SDLC_LANE_PORT:-none}" >"$PORT_LOG/driver-$FANOUT_TICKET"\n'
                         '[ "$FANOUT_TICKET" != T-0002 ] || exit 3\n'
                         'echo "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"\n'
                         'printf \'## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n\' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"\n')
        lstub.chmod(0o755)

        def lifecycle_repo(name, extra_cfg=''):
            """A repo whose config sets lane_ports and lane_min_age_hours 0, holding a landed plugin lane T-0003-pre:
            opened with lanes.py open before the run, one commit, merged into main."""
            r_ = tmp / name
            make_repo(r_, [('a', 'T-0001', 'ready'), ('b', 'T-0002', 'ready'), ('c', 'T-0003', 'ready')],
                      {'.gitignore': '.worktrees/\n',
                       '.sdlc/config': 'lane_ports: 47400-47499\nlane_min_age_hours: 0\n' + extra_cfg})
            op = subprocess.run([sys.executable, str(SCRIPTS / 'lanes.py'), 'open', 'pre', '--ticket', 'T-0003', '--no-claim'],
                                cwd=str(r_), env=ENV, capture_output=True, text=True)
            pre_ = r_ / '.worktrees' / 'T-0003-pre'
            if pre_.is_dir():
                (pre_ / 'pre.txt').write_text('pre\n', encoding='utf-8')
                sh(pre_, 'add', 'pre.txt')
                sh(pre_, 'commit', '-q', '-m', 'pre work')
            mg = sh(r_, 'merge', '-q', '--no-ff', '-m', 'merge pre', 'lane/T-0003-pre')
            expect(f'case 29 lifecycle: fixture {name}: lanes.py open and the merge of the pre lane into main succeed, got '
                   f'open rc={op.returncode} {op.stdout!r} {op.stderr!r}, merge rc={mg.returncode} {mg.stderr!r}',
                   op.returncode == 0 and mg.returncode == 0 and pre_.is_dir())
            return r_, pre_

        lr, pre = lifecycle_repo('lifecycle')
        plog = tmp / 'lifecycle-ports'
        plog.mkdir()
        proc = fanout(lr, 'alpha=T-0001', 'beta=T-0002', '--integration', 'fanout/lc', '--driver', shlex.quote(str(lstub)),
                      '--gate', 'echo "${SDLC_LANE_PORT:-none}" >"$PORT_LOG/gate"', PORT_LOG=str(plog))
        ran = f'rc={proc.returncode} stdout={proc.stdout[-1500:]!r} stderr={proc.stderr[-500:]!r}'
        llanes = lr / '.worktrees' / 'fanout'
        rep = llanes / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        got = report_rows(llanes)
        merge_parents = sh(lr, 'log', '-1', '--format=%P', '--fixed-strings', '--grep', 'Merge fanout/lc-alpha: T-0001',
                           'fanout/lc').stdout.split()
        alpha_tip = merge_parents[1] if len(merge_parents) == 2 else ''
        aref = archived(lr, 'fanout/lc-alpha')
        expect(f'case 29 lifecycle: merged lane gone: alpha merged, its tree and refs/heads/fanout/lc-alpha are gone, '
               f'refs/archive/<UTC date>/fanout/lc-alpha ({aref!r}) resolves to its tip {alpha_tip!r}, and report.md says '
               f'- closed alpha (ancestor); got rows {got} report={text!r} {ran}',
               proc.returncode == 1 and got.get('T-0001') == 'merged' and not (llanes / 'alpha').exists()
               and sh(lr, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/lc-alpha').returncode != 0
               and re.fullmatch(r'refs/archive/\d{4}-\d{2}-\d{2}/fanout/lc-alpha', aref) and alpha_tip
               and sh(lr, 'rev-parse', f'{aref}^{{commit}}').stdout.strip() == alpha_tip
               and '- closed alpha (ancestor)' in text.splitlines() and '- closed alpha (ancestor)' in proc.stdout)
        beta = llanes / 'beta'
        expect(f'case 29 lifecycle: stopped lane kept: beta stopped (driver failed rc=3), its tree and branch remain, and '
               f'report.md has lane still open: {beta} (driver failed rc=3) and the integration line; got rows {got} '
               f'report={text!r} {ran}',
               got.get('T-0002') == 'driver failed rc=3' and beta.is_dir()
               and sh(lr, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/lc-beta').returncode == 0
               and f'- lane still open: {beta} (driver failed rc=3)' in text.splitlines()
               and f'- lane still open: {llanes / "integration"} (integration: stays until main contains fanout/lc)'
               in text.splitlines())

        def seen(name):
            f = plog / name
            return f.read_text().strip() if f.is_file() else ''
        brec = json.loads((beta / '.lane.json').read_text()) if (beta / '.lane.json').is_file() else {}
        bport = brec.get('port')
        ports = (seen('driver-T-0001'), seen('gate'), seen('driver-T-0002'))
        expect(f'case 29 lifecycle: SDLC_LANE_PORT: alpha driver and gate saw one port in 47400-47499 (printed with the '
               f'alpha worktree line), the beta driver saw the port in beta\'s lane record ({bport!r}), and the two differ; '
               f'got driver T-0001, gate, driver T-0002 = {ports}',
               isinstance(bport, int) and 47400 <= bport <= 47499 and ports[2] == str(bport)
               and ports[0].isdigit() and ports[0] == ports[1] and 47400 <= int(ports[0]) <= 47499 and ports[0] != ports[2]
               and f'(branch fanout/lc-alpha, port {ports[0]})' in proc.stdout)
        expect(f'case 29 lifecycle: sweep at start: the landed pre lane T-0003-pre is closed by the run start and logged as '
               f'lanes sweep: closed; got {ran}',
               'lanes sweep: closed T-0003-pre (ancestor)' in proc.stdout.splitlines() and not pre.exists()
               and sh(lr, 'rev-parse', '--verify', '-q', 'refs/heads/lane/T-0003-pre').returncode != 0
               and archived(lr, 'lane/T-0003-pre'))

        lo, pre_off = lifecycle_repo('lifecycle-off', 'lane_sweep: off\n')
        plog_off = tmp / 'lifecycle-ports-off'
        plog_off.mkdir()
        proc = fanout(lo, 'alpha=T-0001', '--integration', 'fanout/lo', '--driver', shlex.quote(str(lstub)), '--gate', 'true',
                      PORT_LOG=str(plog_off))
        expect(f'case 29 lifecycle: sweep off keeps: with lane_sweep: off the landed pre lane stays open and no lanes sweep '
               f'line prints, while the run itself merges; got rc={proc.returncode} stdout={proc.stdout[-1500:]!r} '
               f'stderr={proc.stderr[-500:]!r}',
               proc.returncode == 0 and pre_off.is_dir() and 'lanes sweep:' not in proc.stdout
               and sh(lo, 'rev-parse', '--verify', '-q', 'refs/heads/lane/T-0003-pre').returncode == 0)

        # case 30 (T-0452): prep writes the host lane record of a solo ticket; a land from a worktree the host named
        # .claude/worktrees/agent-<id> rebinds it to that leaf
        hr = tmp / 'host-record'
        sized_repo(hr, ['L1'], {'.gitignore': gi})
        hr_pin = ('--integration', 'fanout/h', '--lanes-dir', str(tmp / 'host-record-lanes'))
        hpp = verb(hr, 'prep', 'alpha=T-0001', *hr_pin, '--stagger', '0')
        prov = hr / '.worktrees' / 'host' / 'T-0001-solo.lane.json'
        prec = json.loads(prov.read_text()) if prov.is_file() else {}
        expect(f'case 30 host record: prep writes {prov} with kind host, ticket T-0001, branch worktree-T-0001-solo and into '
               f'fanout/h, and prints its path, got rc={hpp.returncode} rec={prec} out={hpp.stdout[-600:]!r} err={hpp.stderr!r}',
               hpp.returncode == 0 and prec.get('kind') == 'host' and prec.get('tickets') == ['T-0001']
               and prec.get('branch') == 'worktree-T-0001-solo' and prec.get('into') == 'fanout/h'
               and f'    host record: {prov}' in hpp.stdout.splitlines())
        agent = hr / '.claude' / 'worktrees' / 'agent-x'
        sh(hr, 'worktree', 'add', '-q', '-b', 'worktree-agent-x', str(agent), 'main')
        (agent / 'x.txt').write_text('x\n', encoding='utf-8')
        sh(agent, 'add', '-A')
        sh(agent, 'commit', '-q', '-m', 'T-0001: Ticket t1')
        hl = verb(hr, 'land', 'worktree-agent-x', '--ticket', 'T-0001', *hr_pin, '--base', 'main', '--gate', 'test -e x.txt')
        rebound = hr / '.worktrees' / 'host' / 'agent-x.lane.json'
        rrec = json.loads(rebound.read_text()) if rebound.is_file() else {}
        expect(f'case 30 host record: a land from .claude/worktrees/agent-x rebinds the record to agent-x.lane.json (kind '
               f'host, branch worktree-agent-x, ticket T-0001, the prep base) and removes T-0001-solo.lane.json; the host '
               f'tree stays, got rc={hl.returncode} rec={rrec} out={hl.stdout[-600:]!r} err={hl.stderr[-300:]!r}',
               hl.returncode == 0 and rrec.get('kind') == 'host' and rrec.get('lane') == 'agent-x'
               and rrec.get('branch') == 'worktree-agent-x' and rrec.get('tickets') == ['T-0001']
               and rrec.get('base_sha') == prec.get('base_sha') and not prov.exists() and agent.is_dir())

        # case 32 (T-0452): a full lane tree made with prep's printed lanes.py open line closes after its last ticket lands
        fl = tmp / 'full-lane'
        sized_repo(fl, ['L3', 'L3'], {'.gitignore': gi})
        fl_lanes = tmp / 'full-lane-lanes'
        fl_pin = ('--integration', 'fanout/f', '--lanes-dir', str(fl_lanes))
        fpp = verb(fl, 'prep', 'alpha=T-0001,T-0002', '--lane', 'full', *fl_pin, '--stagger', '0')
        tree_cmd = next((ln.strip()[len('tree: '):] for ln in fpp.stdout.splitlines() if ln.strip().startswith('tree: ')), '')
        fop = subprocess.run(['bash', '-c', tree_cmd], cwd=str(fl), env=ENV, capture_output=True, text=True) if tree_cmd else None
        ftree = fl_lanes / 'alpha'
        frec = json.loads((ftree / '.lane.json').read_text()) if (ftree / '.lane.json').is_file() else {}
        expect(f'case 32 full lane close: the printed tree line opens the lane through lanes.py (kind fanout, both tickets, '
               f'branch fanout/f-alpha), got {tree_cmd!r} rc={fop and fop.returncode} {fop and fop.stdout!r} '
               f'{fop and fop.stderr!r} rec={frec}',
               fop is not None and fop.returncode == 0 and frec.get('kind') == 'fanout'
               and frec.get('tickets') == ['T-0001', 'T-0002'] and frec.get('branch') == 'fanout/f-alpha')

        def full_commit(tid, slug_, fname):
            if not ftree.is_dir():
                return
            (ftree / fname).write_text(f'{tid}\n', encoding='utf-8')
            (ftree / '.sdlc' / slug_ / 'filer-L1.md').write_text('## Warnings\nNone\n\n## Follow-ups\nNone\n', encoding='utf-8')
            sh(ftree, 'add', '-A')
            sh(ftree, 'commit', '-q', '-m', f'{tid}: Ticket {slug_}')
        full_commit('T-0001', 't1', 'f1.txt')
        fl1 = verb(fl, 'land', 'fanout/f-alpha', '--ticket', 'T-0001', *fl_pin, '--base', 'main', '--gate', 'true')
        expect(f'case 32 full lane close control: after the first of its two tickets lands the tree and branch stay, got '
               f'rc={fl1.returncode} out={fl1.stdout[-600:]!r} err={fl1.stderr[-300:]!r}',
               fl1.returncode == 0 and ftree.is_dir()
               and sh(fl, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/f-alpha').returncode == 0
               and not archived(fl, 'fanout/f-alpha'))
        full_commit('T-0002', 't2', 'f2.txt')
        ftip = sh(fl, 'rev-parse', 'fanout/f-alpha').stdout.strip()
        fl2 = verb(fl, 'land', 'fanout/f-alpha', '--ticket', 'T-0002', *fl_pin, '--base', 'main', '--gate', 'true')
        faref = archived(fl, 'fanout/f-alpha')
        expect(f'case 32 full lane close: after its last ticket lands the tree is gone, refs/archive/<UTC date>/fanout/f-alpha '
               f'({faref!r}) is at its tip and the branch is deleted, got rc={fl2.returncode} out={fl2.stdout[-600:]!r} '
               f'err={fl2.stderr[-300:]!r}',
               fl2.returncode == 0 and not ftree.exists() and 'closed alpha (ancestor)' in fl2.stdout.splitlines()
               and sh(fl, 'rev-parse', '--verify', '-q', 'refs/heads/fanout/f-alpha').returncode != 0
               and faref and sh(fl, 'rev-parse', f'{faref}^{{commit}}').stdout.strip() == ftip)

    # case 33 (T-0455): the run-plan claim step sets status: claimed together with claimed_by
    def claim_rule_ok(text):
        m = re.search(r'(?m)^\s*- Claim it \((.*)$', text)
        return bool(m and 'status: claimed' in m.group(0).split('claimed_by', 1)[0] + m.group(0).split('claimed_by', 1)[-1][:60])
    rules = (PLUGIN / 'skills/run-plan/references/run-rules.md').read_text(encoding='utf-8')
    expect('case 33 run-plan claim step sets status: claimed beside claimed_by', claim_rule_ok(rules))
    expect('case 33 negative control: a claim step without status: claimed is rejected',
           not claim_rule_ok(rules.replace('status: claimed', 'status: ready')))

    if misses:
        print('fanout selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('fanout selftest: PASS')
    return 0


USAGE = ('usage: fanout.py run <spec>... [--root .sdlc] [--base REF] [--integration BRANCH] '
         '[--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run] '
         '[--lane auto|solo|full] [--max-lanes N] [--yes-many] [--stagger SECS] [--allow-overlap] [--allow-empty-gate] '
         '[--no-gate-lock] | '
         'fanout.py prep <spec>... [the run flags but --driver and --dry-run] | '
         'fanout.py land <branch> [--ticket T-NNNN] [--root .sdlc] [--base REF] [--integration BRANCH] [--lanes-dir DIR] '
         '[--gate CMD]... [--rewrite-refs] [--lane auto|solo|full] [--allow-empty-gate] [--no-gate-lock] | '
         'fanout.py roll <branch> [--ticket T-NNNN] [--root .sdlc] [--main BRANCH] [--lanes-dir DIR] [--gate CMD]... '
         '[--rewrite-refs] [--lane auto|solo|full] [--allow-empty-gate] [--no-gate-lock] | '
         'fanout.py settle <integration> | '
         'fanout.py selftest\n'
         '  each <spec> is <lane>=<id>[,<id>...] (a worktree and a driver per ticket) or '
         '<lane>@<branch>=<id>[,<id>...] (an external branch registered by an `external_branch: <branch>` '
         'line in <root>/config: no worktree, no driver)')


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] not in (['run'], ['prep'], ['land'], ['roll'], ['settle']):
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == 'settle':
        sp = argparse.ArgumentParser(prog='fanout.py settle', description='Fast-forward the current branch to a landed '
                                     'integration branch, then close its worktree through lanes.py: the archive ref '
                                     'first, then the tree and the branch (local only).')
        sp.add_argument('integration', help='the integration branch `prep` printed, for example fanout/2026-10-11')
        return cmd_settle(sp.parse_args(argv[1:]))
    if argv[0] == 'roll':
        rp = argparse.ArgumentParser(prog='fanout.py roll', description='Land one rolling lane on main at once (T-0374): '
                                     'verified, based on an ancestor of main, touching no hash_bound path in '
                                     '<root>/config. Main only fast-forwards; any other lane is `integration`.')
        rp.add_argument('branch', help='the finished branch, for example worktree-T-0001-solo')
        rp.add_argument('--ticket', metavar='T-NNNN', help='as for land')
        rp.add_argument('--root', default='.sdlc', help='ticket root, relative to the cwd (default .sdlc)')
        rp.add_argument('--main', metavar='BRANCH', help='the branch to land on (default: the main worktree\'s branch)')
        rp.add_argument('--lanes-dir', help='where the rolling scratch worktree and the logs go '
                        '(default <toplevel>/.worktrees/fanout)')
        rp.add_argument('--gate', action='append', metavar='CMD', help='run in the scratch worktree after the merge; '
                        'red resets the merge and main stays (repeatable, in order)')
        rp.add_argument('--rewrite-refs', action='store_true', help='as for run')
        rp.add_argument('--lane', choices=('auto', 'solo', 'full'), default='auto', help='as for land')
        rp.add_argument('--allow-empty-gate', action='store_true', help='as for run')
        rp.add_argument('--no-gate-lock', action='store_true', help='as for run')
        return cmd_roll(rp.parse_args(argv[1:]))
    if argv[0] == 'land':
        lp = argparse.ArgumentParser(prog='fanout.py land', description='Merge one finished sub-agent branch behind the '
                                     'locked merge and the gates, then close its ticket on the integration branch.')
        lp.add_argument('branch', help='the branch a sub-agent (or the parent, for a full ticket) committed on, '
                        'for example worktree-T-0001-solo')
        lp.add_argument('--ticket', metavar='T-NNNN', help='the ticket the branch delivers (else read from a '
                        'worktree-<id>-solo branch name)')
        lp.add_argument('--root', default='.sdlc', help='ticket root, relative to the cwd (default .sdlc)')
        lp.add_argument('--transcript', help='the solo sub-agent transcript (jsonl): prices the ticket\'s solo runs.jsonl row (T-0331)')
        lp.add_argument('--tokens', type=int, help='subagent_tokens from the notice, when there is no transcript')
        lp.add_argument('--base', help='commit for a new integration branch (default HEAD)')
        lp.add_argument('--integration', help='integration branch (default fanout/<YYYY-MM-DD>)')
        lp.add_argument('--lanes-dir', help='where the integration worktree, logs and report go '
                        '(default <toplevel>/.worktrees/fanout)')
        lp.add_argument('--gate', action='append', metavar='CMD', help='run in the integration worktree after the '
                        'merge; red resets the merge (repeatable, in order)')
        lp.add_argument('--rewrite-refs', action='store_true', help='as for run')
        lp.add_argument('--lane', choices=('auto', 'solo', 'full'), default='auto',
                        help='auto (default): a worktree-<id>-solo branch is a solo delivery, any other a full one')
        lp.add_argument('--allow-empty-gate', action='store_true', help='as for run')
        lp.add_argument('--no-gate-lock', action='store_true', help='as for run')
        return cmd_land(lp.parse_args(argv[1:]))
    ap = argparse.ArgumentParser(prog=f'fanout.py {argv[0]}', description=__doc__.split('\n')[0])
    ap.add_argument('lanes', nargs='+', metavar='<lane>[@<branch>]=<id>[,<id>...]',
                    help='a lane spec: <lane>=<id>[,<id>...] runs a worktree and a driver per ticket; '
                    '<lane>@<branch>=<id>[,<id>...] merges an outside agent\'s branch, registered by an '
                    '`external_branch: <branch>` line in <root>/config (else run refuses with exit 2), with no '
                    'worktree and no driver, and never writes that branch')
    ap.add_argument('--root', default='.sdlc', help='ticket root, relative to the cwd (default .sdlc)')
    ap.add_argument('--base', help='commit for a new integration branch (default HEAD)')
    ap.add_argument('--integration', help='integration branch (default fanout/<YYYY-MM-DD>)')
    ap.add_argument('--lanes-dir', help='where the worktrees, logs and report go '
                    '(default <toplevel>/.worktrees/fanout); inside the repo it must be gitignored '
                    '(add .worktrees/ or the dir to .gitignore) or run refuses with exit 2')
    ap.add_argument('--gate', action='append', metavar='CMD', help='run in the integration worktree after each merge; '
                    'red resets the merge (repeatable, in order)')
    if argv[0] == 'run':
        ap.add_argument('--driver', metavar='CMD', help='run per ticket in the lane worktree via bash -c '
                        '(default: a headless sdlc-lite conductor running /sdlc-lite:chain; on Claude it needs SDLC_CLAUDE_EXEC=1)')
    ap.add_argument('--rewrite-refs', action='store_true', help='opt-in, numbered mode only: when a ticket '
                    'closes, rewrite files outside the ticket folder that cite <rel>/NNNN-<slug> to '
                    '<rel>/.NNNN-<slug> (passed to tickets.py close). Without it such a close is refused')
    ap.add_argument('--lane', choices=('auto', 'solo', 'full'), default='auto',
                    help='auto (default): steps.py lane picks solo (ticket level L1 and L2) or the full chain per ticket; '
                    'solo or full forces it for every ticket')
    ap.add_argument('--max-lanes', type=int, default=MAX_LANES_DEFAULT, metavar='N',
                    help=f'most regular lanes in one run (default {MAX_LANES_DEFAULT}); above {MAX_LANES_HARD} needs --yes-many')
    ap.add_argument('--yes-many', action='store_true', help=f'confirm a --max-lanes above {MAX_LANES_HARD}')
    ap.add_argument('--stagger', type=float, default=STAGGER_DEFAULT, metavar='SECS',
                    help=f'seconds between lane starts (default {STAGGER_DEFAULT}; 0 for none)')
    ap.add_argument('--allow-overlap', action='store_true',
                    help='run tickets in different lanes whose planned scope overlaps (the merge-time wait serializes them)')
    ap.add_argument('--allow-empty-gate', action='store_true',
                    help='merge although a gate ran no tests (unittest "Ran 0 tests", pytest "no tests ran" or rc 5)')
    ap.add_argument('--no-gate-lock', action='store_true',
                    help='run each gate bare, not through gate_lock.py (as does SDLC_GATE_SLOTS=0)')
    if argv[0] == 'prep':  # prep never runs a driver and never creates anything, so it has neither flag
        ap.set_defaults(driver=None, dry_run=True)
        return cmd_prep(ap.parse_intermixed_args(argv[1:]))
    ap.add_argument('--dry-run', action='store_true', help='print the plan and create nothing')
    return cmd_run(ap.parse_intermixed_args(argv[1:]))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
