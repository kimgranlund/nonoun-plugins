#!/usr/bin/env python3
"""Run ticket lanes in parallel: one git worktree and one headless conductor per lane, each lane
merged into an integration branch under a lock, gated, and closed there. Main is never touched.
An external lane merges a registered branch an outside agent owns, with no worktree and no driver.

Usage: fanout.py run <spec>... [--root .sdlc] [--base REF] [--integration BRANCH]
                     [--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run]
                     [--lane auto|solo|full] [--max-lanes N] [--yes-many] [--stagger SECS] [--allow-overlap] [--allow-empty-gate]
       fanout.py selftest
  where each <spec> is <lane>=<id>[,<id>...] or <lane>@<branch>=<id>[,<id>...]

Solo first (the default driver). For each ticket, after the lane syncs, `steps.py lane <task dir>` decides
  the lane and appends its record to the task's skips.md (committed with the lane): `solo` (size S and M by
  default) starts the solo agent (agents/solo.md) from a typed brief at the tier's model and effort (Claude:
  `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo` at S Sonnet low, M Sonnet xhigh; Codex: `codex_exec.py solo
  L1|L2|L3`, honoring SDLC_BACKEND), both started through `solo_run.py` so each lane's solo session cost lands in
  the ticket's runs.jsonl and the budget and board meter it (T-0226); anything else (`full`, or `lean` after a plan) keeps the headless conductor
  running /sdlc-lite:chain. A solo ticket of size M or L then needs one independent batched verifier: a new
  task-dir verifier result with Verdict pass, from the solo itself or else one fanout runs once
  (`run.sh verifier L3 <task dir>/handoff.md`, never the solo's own family); a missing or non-pass verdict is
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
  match ^[a-z0-9]+(-[a-z0-9]+)*$ (not `integration` or `logs`, which name the lanes dir's own
  entries); each id is T-NNNN, resolves through tickets.load(tickets.ticket_dir(root)) to exactly one folder whose
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
  (then reuse it; --base is ignored); `git worktree add <lanes-dir>/integration <integration>`;
  per regular lane `git worktree add -b <lane branch> <lanes-dir>/<lane> <integration>` (an
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
       and BASH_DEFAULT_TIMEOUT_MS=BASH_MAX_TIMEOUT_MS=3600000 as bench.sh sets them. Default: a headless conductor (claude -p --agent sdlc-lite:conductor, Opus
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
    4. commit in the lane: `git add -A`, `git commit -m "<id>: <title>"`; nothing staged:
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
       is aborted: `merge conflict`); each --gate in order via bash -c, output to
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
  commit run only inside the lanes dir;
  nothing is pushed; the worktrees stay for inspection.

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
"""
import argparse, datetime, fcntl, json, os, pathlib, re, shlex, shutil, subprocess, sys, tempfile, threading, time, uuid

import tickets  # same scripts/ dir: the only front matter parser
import steps  # same scripts/ dir: next_action and section read step results
import order  # same scripts/ dir: newest result file of a role

SCRIPTS = pathlib.Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
LANE_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
RESERVED = ('integration', 'logs')
ENV = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
# No auto gc or maintenance while lanes write refs and objects concurrently.
GIT_CFG = ('-c', 'gc.auto=0', '-c', 'maintenance.auto=false')
TIMEOUT_MS = '3600000'
PROMPT = ('Run /sdlc-lite:chain {handoff} unattended. No person is present: never ask the user and '
          'never use AskUserQuestion; where a step would ask, take its recommended option and go on. '
          'In the file stage run the filer only and do not close the ticket (no tickets.py close), '
          'because /fanout closes it on the integration branch after the merge. '
          'Never commit, push, or publish: fanout.py commits this lane when you finish.')


# Solo tiers (agents/solo.md): ticket size -> (Claude model, Claude effort, Codex level). The Codex agents are
# sdlc-solo-l1..l3 from adapters/codex/models.json. check.py guards that solo.md and these agree.
SOLO_TIERS = {'S': ('sonnet', 'low', 'L1'), 'M': ('sonnet', 'xhigh', 'L2'), 'L': ('opus', 'xhigh', 'L3')}
SOLO_VERIFIER = 'L3'  # a different family from every solo builder (Sonnet, Opus): the run.sh verifier L3
MAX_LANES_DEFAULT, MAX_LANES_HARD, STAGGER_DEFAULT = 4, 16, 20
# A test gate that ran nothing: unittest "Ran 0 tests", pytest "no tests ran" or exit code 5 (nothing collected).
VACUOUS_GATE = re.compile(r'\bRan 0 tests\b|\bno tests ran\b|\bcollected 0 items\b', re.M)
SOLO_PROMPT = ('Brief: deliver ticket {handoff} end to end in this session as the solo agent. Read the ticket and the '
               'files it names, make the smallest change that meets its done criterion, run every check command it '
               'names and rerun them all after a fix, and report files changed, each check with its outcome, and '
               'anything still open. For a size M or L ticket write the handoff\'s ## Acceptance criteria if it has '
               'none, then run the one batched independent verifier agents/solo.md names. No person is present: '
               'never ask the user and never use AskUserQuestion. Never commit, push, open a PR, or publish: '
               'fanout.py commits this lane when you finish and closes the ticket after the merge.')


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
    """The tier for a ticket size: S, M, or L (an XL or unknown size has no solo tier: None)."""
    return size if size in SOLO_TIERS else None


def solo_model_label(tier, backend=None):
    """`<model> <effort>` the solo agent runs at for a tier on the backend: the Claude tier from SOLO_TIERS, or the
    Codex model and effort of sdlc-solo-l1..l3 read from adapters/codex/models.json (never a hardcoded guess)."""
    backend = backend or os.environ.get('SDLC_BACKEND', 'claude')
    model, effort, level = SOLO_TIERS[tier]
    if backend == 'codex':
        try:
            model, effort = json.loads((PLUGIN / 'adapters' / 'codex' / 'models.json').read_text())['solo'][level]
        except (OSError, ValueError, KeyError):
            return f'codex {level} (model unreadable)'
    return f'{model} {effort}'


def gate_vacuous(rc, text, gate=''):
    """True when a gate's output shows it ran no tests (rc 0 or 5 only: any other failure is plain red)."""
    return rc in (0, 5) and bool(VACUOUS_GATE.search(text) or (rc == 5 and 'pytest' in gate))


def solo_command(handoff_rel, size, backend=None):
    """The shell command that starts the solo agent for one ticket at its size's tier, or raises Refuse.

    It starts through scripts/solo_run.py (T-0226), which runs `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`
    at the tier's model and effort (or codex_exec.py solo L1..L3) and appends one `role solo` record with the
    session's cost to the ticket's runs.jsonl, so budget.py and the board meter the lane. SDLC_SELFTEST_RAW_SOLO
    restores the raw unmetered command, which the selftest uses as its negative control."""
    backend = backend or os.environ.get('SDLC_BACKEND', 'claude')
    tier = solo_tier(size)
    if tier is None:
        raise Refuse(f'no solo tier for size {size!r}: want S, M, or L')
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
        '--backend', backend, '--brief', prompt))


def default_driver(handoff_rel, kind='full', size=None):
    if kind == 'solo':
        return solo_command(handoff_rel, size)
    backend = os.environ.get('SDLC_BACKEND', 'claude')
    if backend == 'codex':
        return ' '.join(shlex.quote(x) for x in (
            sys.executable, str(SCRIPTS / 'codex_exec.py'), 'conductor', 'L1',
            PROMPT.format(handoff=handoff_rel)))
    if backend != 'claude':
        raise Refuse('unknown SDLC_BACKEND: ' + backend)
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
        self.branch = self.dir = None
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
        tids = [x.strip() for x in ids.split(',') if x.strip()]
        if not eq or not tids or (at and not ext):
            errs.append(f'{spec!r}: want {SPEC_FORMS}')
            continue
        if not LANE_RE.fullmatch(name):
            errs.append(f'lane {name!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
        elif name in RESERVED:
            errs.append(f'lane {name!r} is reserved (the lanes dir holds {" and ".join(RESERVED)})')
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
                     f'files, so commit the .sdlc/ trail first')

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
            'allow_empty_gate': bool(getattr(a, 'allow_empty_gate', False))}


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
    return (f'delivered by the solo agent (tier {tier}); one independent batched verifier passed before the merge'
            if tier in ('M', 'L') else f'delivered by the solo agent (tier {tier}); the ticket\'s own checks and the fanout gates passed')


def write_solo_skips(taskdir, tier):
    """The solo lane's skipped planner and filer under ## Skipped, written by steps.write_solo_skips (the one
    writer, shared with `steps.py lane` itself); called again here for the tier-sized reason and for an
    already-recorded lane. True when it wrote."""
    return steps.write_solo_skips(taskdir, tier)


def verifier_files(taskdir):
    """The task dir's verifier result file names now (the batched-verification baseline)."""
    try:
        return {f.name for f in pathlib.Path(taskdir).iterdir() if re.fullmatch(r'verifier-L\d+(-\d+)?\.md', f.name)}
    except OSError:
        return set()


def solo_verdict(taskdir, before):
    """'pass', 'fail', or None for the newest task-dir verifier result that is not in `before`."""
    new = [f for f in verifier_files(taskdir) if f not in before]
    if not new:
        return None
    newest = order.newest(pathlib.Path(taskdir), 'verifier')
    if newest is None or pathlib.Path(newest).name not in new:
        return None
    return steps.verdict_or_none(newest)


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
                shown = f'solo, tier {tier}: {solo_model_label(tier)}' if tier else kind
                out.append(f'    lane: {shown} ({why})')
    out += plan_overlap(ctx)
    if ctx['gates']:
        out += [f'gate {k}: {g}' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('gates: none given (merges will not be gated)')
    if ctx['driver']:
        out.append(f"driver: {ctx['driver']}")
    else:
        out.append(f"driver: solo first (--lane {ctx['lane_mode']}): steps.py lane picks solo or the full chain per ticket")
        out.append(f"  solo (size S and M): {solo_command('<handoff>', 'M')}")
        out.append(f"  full: {default_driver('<handoff>')}")
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
        git_out(cwd, 'worktree', 'add', '-q', str(ctx['integ_dir']), integration)
        worktrees.append(ctx['integ_dir'])
        print(f"worktree integration: {ctx['integ_dir']}", flush=True)
        regular = [lane for lane in ctx['lanes'] if not lane.external]
        for lane in regular:
            git_out(cwd, 'worktree', 'add', '-q', '-b', lane.branch, str(lane.dir), integration)
            worktrees.append(lane.dir)
            branches.append(lane.branch)
            print(f'worktree {lane.name}: {lane.dir} (branch {lane.branch})', flush=True)
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


def wip_commit(wt, tid, outcome):
    """Commit whatever a stopped ticket left in the lane worktree wt as `wip(<id>): <outcome>`.
    Runs git only in wt (never the integration worktree, main, or the stash). Returns the new
    short sha, or '' when the tree is clean or the add or commit fails; never raises."""
    try:
        dirty = git(wt, 'diff', '--quiet', 'HEAD').returncode != 0
        untracked = git(wt, 'ls-files', '--others', '--exclude-standard')
        if not dirty and not (untracked.returncode == 0 and untracked.stdout.strip()):
            return ''
        if git(wt, 'add', '-A').returncode:
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
    log = ctx['logs'] / f'{lane.name}-{t.id}.log'
    kind, why = lane_run(ctx, wt, t)
    tier = solo_tier(t.size) if kind == 'solo' else None
    if kind == 'solo' and tier is None:  # an XL or unsized ticket has no solo tier: the chain takes it
        kind, why = 'full', f'size {t.size or "unset"} has no solo tier'
    ctx['kinds'][t.id] = (kind, tier)
    env['FANOUT_LANE_KIND'] = kind
    say(ctx, lane, t.id, f'lane {kind}' + (f' tier {tier}' if tier else '') + f' ({why})')
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
    if kind == 'solo' and tier in ('M', 'L'):  # one independent batched verifier decides before any merge
        verdict = solo_verdict(taskdir, before)
        if verdict is None:  # the solo did not run it (Codex solo, say): fanout runs it once
            say(ctx, lane, t.id, f'verifier {SOLO_VERIFIER} started (the solo left no new verifier result)')
            vrc = run_logged(['bash', str(SCRIPTS / 'run.sh'), 'verifier', SOLO_VERIFIER,
                              str(taskdir / 'handoff.md')], str(wt), env,
                             ctx['logs'] / f'{lane.name}-{t.id}-verifier.log', ctx['run_id'])
            verdict = solo_verdict(taskdir, before) if not vrc else None
            if verdict is None:
                return (f'no verifier result (run.sh rc={vrc})' if vrc else 'no verifier result'), ''
        if verdict != 'pass':
            return f'verifier {verdict}', ''

    p = git(wt, 'add', '-A')
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
            rc = run_logged(['bash', '-c', gate], str(integ), dict(ENV, FANOUT_RUN_ID=ctx['run_id']),
                            ctx['logs'] / f'{stem}{n}.log', ctx['run_id'])
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
                return f'red: {gate} rc={rc}', cell
        if lane.dir is not None:  # an external lane has no lane dir: its ticket folder came in with the merge
            src, dst = lane.dir / trel / t.slug, integ / trel / t.slug
            if not any(dst.glob('filer-L*.md')) and src.is_dir():
                shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
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
    for lane in ctx['lanes']:
        for tid, _outcome, _commit in lane.results:
            if tid in ctx['kinds']:
                kind, tier = ctx['kinds'][tid]
                out.append(f'- Lane for `{tid}`: {kind}' + (f' (tier {tier}: {solo_model_label(tier)})' if tier else ''))
    out += ['', '| Lane | Ticket | Outcome | Commit |', '|---|---|---|---|']
    for lane in ctx['lanes']:
        for tid, outcome, commit in lane.results:
            out.append(f'| {lane.name} | {tid} | {cell(outcome)} | {commit or "-"} |')
    text = '\n'.join(out) + '\n'
    (ctx['lanes_dir'] / 'report.md').write_text(text, encoding='utf-8')
    return text


def cmd_run(a):
    try:
        ctx = preflight(a)
        if a.dry_run:
            print_plan(ctx)
            return 0
        # fanout mints its own id on every run; an inherited SDLC_ATTEMPT_ID belongs to a role attempt
        ctx['run_id'] = 'fanout-' + uuid.uuid4().hex[:12]
        if not ctx['allow_overlap']:
            pairs, _ = overlap_pairs(ctx)
            if pairs:
                la, ta, lb, tb, paths = pairs[0]
                raise Refuse(f"{ta.id} (lane {la.name}) and {tb.id} (lane {lb.name}) plan to change the same "
                             f"files ({', '.join(paths)}): run them in one lane, or pass --allow-overlap and let "
                             f"the merge-time wait serialize them")
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
    text = report(ctx)
    print()
    print(text, end='')
    results = [r for lane in ctx['lanes'] for r in lane.results]
    ok = bool(results) and all(outcome == 'merged' for _, outcome, _ in results)
    return 0 if ok else 1


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

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def sh(cwd, *args):
        return subprocess.run(['git', '-C', str(cwd), *args], env=ENV, capture_output=True, text=True)

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

    def fanout(cwd, *args):
        if not any(x == '--stagger' for x in args):
            args = (*args, '--stagger', '0')  # the default 20 s gap would slow every case
        return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', *args],
                              cwd=str(cwd), env=ENV, capture_output=True, text=True, timeout=300)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp).resolve()

        # 1. Two lanes, a stub driver, a gate that goes red on T-0003.
        repo, lanes = tmp / 'repo', tmp / 'lanes'
        make_repo(repo, [(s, f'T-000{i}', 'ready') for i, s in enumerate('abcde', 1)])
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
        saw = lanes / 'beta' / 'T-0004.saw'
        seen = saw.read_text().split() if saw.is_file() else []
        expect(f'T-0004.saw in beta lists T-0001.txt (synced before the ticket), got {seen}', 'T-0001.txt' in seen)
        board = subprocess.run([sys.executable, str(SCRIPTS / 'board.py'), '--lanes', '--root', str(repo / '.sdlc')],
                               env=ENV, capture_output=True, text=True)
        cells = {}
        for line in board.stdout.splitlines():
            c = [x.strip() for x in line.strip('|').split('|')]
            if line.startswith('| ') and len(c) == 3:
                cells[c[0]] = c[1]
        expect(f'board.py --lanes exits 0, got {board.returncode} stderr={board.stderr!r}', board.returncode == 0)
        expect(f'board.py --lanes lists alpha on fanout/test-alpha, got {cells}', cells.get('alpha') == 'fanout/test-alpha')
        expect(f'board.py --lanes lists beta on fanout/test-beta, got {cells}', cells.get('beta') == 'fanout/test-beta')

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
                            ('an unknown id', ('alpha=T-0009',)),
                            ('a done ticket', ('alpha=T-0002',))):
            # a no-op driver: if a refusal regresses, the run must never reach the default claude driver
            proc = fanout(rr, '--lanes-dir', str(rl), '--driver', 'exit 3', *args)
            expect(f'{label} exits 2 with a reason, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 2 and proc.stderr.strip() and 'Traceback' not in proc.stderr)
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
            subjects = sh(fr, 'log', '--format=%s', f'fanout/dd-{lane}').stdout.splitlines()
            expect(f'default lanes dir: fanout/dd-{lane} has a commit "{tid}: Ticket {slug}", got {subjects!r}',
                   f'{tid}: Ticket {slug}' in subjects)
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
        for name in ('alpha', 'beta', 'integration'):
            expect(f'default lanes dir: git worktree list shows {flanes / name}, got {wts!r}',
                   any(ln.split()[0] == str(flanes / name) for ln in wts.splitlines() if ln.strip()))

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
        subj = sh(cr, 'log', '-1', '--format=%s', 'fanout/dc-alpha').stdout.strip()
        expect(f'dirty-sync control: lane tip subject does not start with wip(, got {subj!r}',
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
        expect('external: no fanout/ext-alpha ref, while the regular fanout/ext-beta exists',
               sh(er, 'branch', '--list', 'fanout/ext-alpha').stdout.strip() == ''
               and sh(er, 'branch', '--list', 'fanout/ext-beta').stdout.strip() != '')
        expect('external: no <lanes-dir>/alpha dir, while <lanes-dir>/beta exists',
               not (el / 'alpha').exists() and (el / 'beta').is_dir())
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
        sizes = [('s1', 'T-0001', 'S'), ('m1', 'T-0002', 'M'), ('l1', 'T-0003', 'L'), ('s2', 'T-0004', 'S'),
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
        expect(f'case 15 lane: size S prints solo tier S (sonnet low), M tier M (sonnet xhigh), and L the full chain '
               f'(steps.py lane decides), got {proc.returncode} stdout={out!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'lane: solo, tier S: sonnet low' in out
               and 'lane: solo, tier M: sonnet xhigh' in out
               and re.search(r'T-0003 l1: .*\n    lane: full \(', out) and 'driver: solo first (--lane auto)' in out)
        expect('case 15 lane negative control: no solo line for the size L ticket',
               not re.search(r'T-0003 l1: .*\n    lane: solo', out))
        proc = fanout(sr, '--dry-run', '--lane', 'full', '--lanes-dir', str(sl), 'a=T-0001')
        expect(f'case 15 --lane full forces the chain for a size S ticket, got {proc.stdout!r}',
               proc.returncode == 0 and 'lane: full (--lane full)' in proc.stdout)
        for label, size in (('S', 'S'), ('M', 'M'), ('L', 'L')):
            cmd = solo_command('h.md', size, 'claude')
            expect(f'case 15 command: tier {label} starts through solo_run.py with --tier {label}, got {cmd}',
                   'solo_run.py' in cmd and ' run ' in cmd and f'--tier {label}' in cmd and '--backend claude' in cmd
                   and '--task-dir .' in cmd and 'sdlc-lite:conductor' not in cmd)
        saved_raw = os.environ.get('SDLC_SELFTEST_RAW_SOLO')
        os.environ['SDLC_SELFTEST_RAW_SOLO'] = '1'
        try:
            for label, size, want in (('S', 'S', ('--model sonnet', '--effort low')),
                                      ('M', 'M', ('--model sonnet', '--effort xhigh')),
                                      ('L', 'L', ('--model opus', '--effort xhigh'))):
                cmd = solo_command('h.md', size, 'claude')
                expect(f'case 15 raw fallback: tier {label} starts sdlc-lite:solo with {want}, got {cmd}',
                       '--agent sdlc-lite:solo' in cmd and all(w in cmd for w in want) and cmd.startswith('SDLC_ROLE=solo ')
                       and 'sdlc-lite:conductor' not in cmd and '--dangerously-skip-permissions' in cmd and 'solo_run.py' not in cmd)
        finally:
            if saved_raw is None: os.environ.pop('SDLC_SELFTEST_RAW_SOLO', None)
            else: os.environ['SDLC_SELFTEST_RAW_SOLO'] = saved_raw
        for size, level in (('S', 'L1'), ('M', 'L2'), ('L', 'L3')):
            cmd = solo_command('.sdlc/t/h/handoff.md', size, 'codex')
            expect(f'case 15 command: Codex tier {size} runs solo_run.py --backend codex --tier {size}, got {cmd}',
                   'solo_run.py' in cmd and '--backend codex' in cmd and f'--tier {size}' in cmd and '--task-dir .sdlc/t/h' in cmd)
        full = default_driver('h.md', 'full', 'M')
        expect(f'case 15 command negative control: the full driver starts the conductor, never solo, got {full}',
               'sdlc-lite:conductor' in full and 'sdlc-lite:solo' not in full)
        try:
            solo_command('h.md', 'XL', 'claude')
            expect('case 15: a size XL ticket has no solo tier (Refuse)', False)
        except Refuse:
            pass
        fake = {'kinds': {'T-1': ('solo', 'M'), 'T-2': ('solo', 'S'), 'T-3': ('full', None), 'T-4': ('driver', None)}}
        expect('case 15 close: a solo M ticket closes with a reason naming the verifier',
               'verifier passed' in (close_reason(fake, Ticket('T-1', 'x', 't')) or ''))
        expect('case 15 close: a solo S ticket closes with a reason naming the checks',
               'solo agent (tier S)' in (close_reason(fake, Ticket('T-2', 'x', 't')) or ''))
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
            for tid, lane in (('T-0001', 'x'), ('T-0002', 'y'), ('T-0003', 'z')):
                f = gl / lane / f'{tid}.start'
                ts.append(float(f.read_text()) if f.is_file() else 0.0)
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
        (shim / 'claude').write_text('#!/usr/bin/env bash\nset -eu\necho "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"\n')
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
        expect('case 16 write_solo_skips: writes once', write_solo_skips(tdir_, 'S') is True)
        expect('case 16 write_solo_skips: a second call is a no-op', write_solo_skips(tdir_, 'S') is False)
        (tdir_ / 'skips.md').write_text('# Skips\n', encoding='utf-8')
        expect('case 16 write_solo_skips negative control: no lane record writes nothing',
               write_solo_skips(tdir_, 'S') is False and 'skip:' not in (tdir_ / 'skips.md').read_text())

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
        for be, tier, want in (('claude', 'S', 'sonnet low'), ('claude', 'M', 'sonnet xhigh'), ('claude', 'L', 'opus xhigh'),
                               ('codex', 'S', 'gpt-6.1-sol low'), ('codex', 'M', 'gpt-6.1-sol high'),
                               ('codex', 'L', 'gpt-6.1-sol xhigh')):
            got = solo_model_label(tier, be)
            expect(f'case 19 model label: {be} tier {tier} is {want!r}, got {got!r}', got == want)
        expect('case 19 codex label is not the Claude model', 'sonnet' not in solo_model_label('S', 'codex'))
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

    if misses:
        print('fanout selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('fanout selftest: PASS')
    return 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] != ['run']:
        print('usage: fanout.py run <spec>... [--root .sdlc] [--base REF] [--integration BRANCH] '
              '[--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run] '
              '[--lane auto|solo|full] [--max-lanes N] [--yes-many] [--stagger SECS] [--allow-overlap] [--allow-empty-gate] | '
              'fanout.py selftest\n'
              '  each <spec> is <lane>=<id>[,<id>...] (a worktree and a driver per ticket) or '
              '<lane>@<branch>=<id>[,<id>...] (an external branch registered by an `external_branch: <branch>` '
              'line in <root>/config: no worktree, no driver)', file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(prog='fanout.py run', description=__doc__.split('\n')[0])
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
    ap.add_argument('--driver', metavar='CMD', help='run per ticket in the lane worktree via bash -c '
                    '(default: a headless sdlc-lite conductor running /sdlc-lite:chain)')
    ap.add_argument('--rewrite-refs', action='store_true', help='opt-in, numbered mode only: when a ticket '
                    'closes, rewrite files outside the ticket folder that cite <rel>/NNNN-<slug> to '
                    '<rel>/.NNNN-<slug> (passed to tickets.py close). Without it such a close is refused')
    ap.add_argument('--lane', choices=('auto', 'solo', 'full'), default='auto',
                    help='auto (default): steps.py lane picks solo (size S and M) or the full chain per ticket; '
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
    ap.add_argument('--dry-run', action='store_true', help='print the plan and create nothing')
    return cmd_run(ap.parse_intermixed_args(argv[1:]))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
