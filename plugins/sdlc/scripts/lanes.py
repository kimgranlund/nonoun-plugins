#!/usr/bin/env python3
"""lanes.py: the one home of the lane lifecycle. Open, close, finish, ready, sweep, list, check, port and archive a lane.

  lanes.py open <name> [--base REF] [--into REF] [--ticket ID]... [--tickets ID,ID] [--kind fanout|integration|solo] [--title TEXT]
                [--root .sdlc] [--path DIR] [--branch NAME] [--no-claim | --claim [--by AGENT]] [--dry-run]
  lanes.py close <name|path> [--into REF] [--discard] [--dry-run]
  lanes.py finish <name|path> [--backup REMOTE/REF] [--transcript JSONL] [--verifier-transcript JSONL]
                  [--solo-agent-id ID] [--verifier-agent-id ID] [--no-ticket]
                                           --no-ticket (T-0821): a lane with no local ticket commits, merges into a scratch
                                           tree at into, runs the land gate there, fast-forwards into and closes the lane;
                                           no record, verdict or ticket close; a hash_bound: path needs a pass verdict
                                           from --verifier-agent-id (its transcript's final message or the file it names)
  lanes.py ready [<name|path>] [--ticket ID] [--notify-cmd CMD]   pin the review sha, unlock, and tell the factory (default: the current lane)
  lanes.py sweep [--apply]                 a dry run by default; --apply closes every landed plugin lane
  lanes.py list [--all] [--stale [--fail]] [--json]
  lanes.py list --ready [--json]           one line per ready ref: ticket, lane, sha, path, and stale when the lane moved
  lanes.py list --overlap <path>...        `overlap <lane> <path>` per open plugin lane (not the current tree) whose diff
                                           from its base (committed, uncommitted, untracked) holds the path or a path under it
  lanes.py who [--json]                    `factory <session> <evidence>` per sign of an active factory session (T-0821):
                                           a live claude receiver naming a factory, a *.running marker a live process names,
                                           an open fanout or solo lane other than the current tree; else `none`; exit 0
  lanes.py check [--warn]                  C1 placement, C2 ports, C3 record drift; --warn prints and exits 0
  lanes.py port [<path>]                   the port of the lane holding <path> (default the cwd); exit 1 if none
  lanes.py archive list [<branch>]
  lanes.py archive restore <date>/<branch>
  lanes.py orphans                         read-only: snapshot refs and dangling commits whose work is on no local branch
  lanes.py selftest

Design: docs/specs/sdlc/lane-lifecycle.md (section 17 wins over sections 1 to 16). Python API for callers:
open_lane, close_lane, finish, sweep, list_lanes, still_open(root, ticket), landed, patch_landed, landed_and_gone, config, host_record. open_lane and close_lane
return a dict with rc, message, lane, path and branch; sweep returns (list of those dicts, rc); finish returns the exit code
and prints through its say= callable. open_lane takes
keyword-only path= (the tree; the leaf is its basename), branch= (used verbatim) and check_claim=False (skip the claim
rule for local ids; the ids are still recorded); the CLI spells them --path, --branch and --no-claim.
host_record(name, branch, into, tickets, base=None, cwd='.') writes <lanes root>/host/<name>.lane.json with every
record field (kind host), overwriting a record of that name, and returns it.

Kinds. A tree is a plugin lane when it has a .lane.json at its root, a host record <lanes root>/host/<name>.lane.json,
or a legacy fanout parent (its parent dir holds merge.lock and logs/). Every other tree is manual: list --all shows
it, and nothing here changes it. Old and new branch names are read alike; ownership never comes from a name.

  kind             made by                             path                                branch                into (target)              closed by
  fanout lane      lanes.py open --kind fanout         <lanes root>/<ticket>-<slug>        lane/<ticket>-<slug>  --into, else --base        close after its last ticket lands, or sweep
  integration      lanes.py open --kind integration    <lanes root>/<slug of name>         <name> (wave/<N>)     lane_into:, else main      sweep after the fast-forward
  rolling scratch  fanout.py roll                      <lanes-dir>/rolling, detached       none                  none                       roll itself, at its end
  solo worktree    lanes.py open --kind solo           <lanes root>/<ticket>-<slug>        lane/<ticket>-<slug>  lane_into:, else main      sweep
  host lane        the Claude host, isolation:worktree .claude/worktrees/<name> (host-owned) worktree-<name>     the integration branch     dispatch.py prune --done, else sweep
  runner tmp       run.sh, dispatch.py                 <lanes root>/tmp/<name>, detached   none                  none                       run.sh EXIT, remove_tmp, reap-tmp-worktrees.sh, wtroot sweep
  manual           a person                            anywhere                            any                   none                       the person; listed, never touched
  host-owned       Codex (~/.codex/worktrees/*) or Claude Code (.claude/worktrees/agent-*), wtroot.host_owned: sweep prints
                   `kept <path>: host-owned (<host>)` and never closes it, even with a host record; prune --done may (T-0564)

  Names (17.1): kinds fanout and solo need --ticket; the slug is <name> lowercased with every run of characters
  outside [a-z0-9-] replaced by -, cut to 40 characters; a leading # is dropped from the ticket in the leaf.
  Integration uses <name> verbatim as its branch. Before open creates anything it runs git check-ref-format
  --branch, the clash test over refs/heads (a flat lane beside lane/x, and the reverse) and refuses a tree path that
  exists or is a lanes dir, so a refusal leaves no directory and no record. A legacy fanout lane's into is the branch
  of <lanes-dir>/integration, else main; the integration tree's into is lane_into:, else main. Main is the branch of
  the first git worktree list entry.

  Claim rule (8.1): a T-<digits> id is local when --root exists: open refuses `ticket <id> not claimed: set
  claimed_by: first` or `no ticket <id>`. Any other id prints `claim <id> in its tracker (assignee) before work; not
  checked here`. With --claim [--by AGENT] (T-0800) the CLI open first runs tickets.py claim on each unclaimed local
  id in the main checkout and commits what it changed as `claim <ids>` (printed `claim: committed <sha> claim <ids>`;
  an id already claimed prints `claim: <id> already claimed`; a main tracking an upstream gets no commit, as T-0609,
  unless a `lane_landing: local` config line says the repo lands locally, T-0804); a
  failed claim stops before any lane is made. After a close by row 9, row 10 or pr merged, close prints `ticket still open: <id>` for each local
  ticket of the record whose status is neither done nor dropped, read in the tree owning ticket-close (wtroot.owner_tree:
  the integration tree holding the lane's into branch, else main; main for a ticket that tree lacks, T-0769).

  Ticket branch (T-0530): the CLI open writes `branch: <lane branch>` after each local ticket's `claimed_by:` (through
  tickets.record_branch, which regenerates the roadmap and router) and prints `ticket <id>: branch: <b>`; with it goes
  `worktree: <tree relative to the main checkout>` (T-0550, printed as `ticket <id>: worktree: <path>`; none for a
  tree outside the checkout); the Python open_lane does so only with record_branch=True. The same open then commits the
  paths those writes changed in main as `<ids>: record lane <leaf>` (T-0599, printed as `committed: <sha> <message>`),
  so main is clean and a fast-forward settle is not blocked. With no --root, an --into branch checked out in an
  integration tree (not the main checkout) takes both writes and the commit in that tree instead, printed as `recorded
  in <tree>`, and main does not move (T-0680); it writes and commits there under the merge.lock fanout.py land holds
  (<tree parent>/merge.lock beside a fanout integration tree, else the default lanes dir's, T-0725); a ticket missing from that tree's root falls back to main, printed as
  `recorded in the main checkout: <ids> not in <tree>/<root>`. An explicit --root records in the main checkout.
  A path already dirty before the open (staged or not) is never committed, compared by path: a ticket handoff left out this way prints `not committed: <path> (dirty before
  open); commit it yourself`. When main tracks an upstream (T-0609: the repo lands through it, as by PR) and no
  `lane_landing: local` line says it lands locally (T-0804), open writes and commits neither line, printing `not recorded: <main> tracks <upstream>, ...`, so main never gains a commit its
  landing path does not push; the claim is the refs/sdlc/claims ref (T-0588). Every close removes a record
  ticket's `branch:` line whose value is the lane branch, and its `worktree:` line with it, in main and in the integration
  tree holding the lane's into branch, where it commits `<ids>: clear lane record <leaf>` (T-0695, printed as `committed in
  <tree>: <sha> <message>`). A ticket that tree cleared stays byte-identical in main, which merging into brings the clear
  to; a clear in main for any other into than main is committed there the same way (T-0713), so a land leaves main clean.
  list rows carry ticket (the local ticket whose `branch:` is the row's branch, else the record's first local ticket,
  else null) and verdict (its newest verifier result: pass, fail, inherited, or null), so a
  manual worktree with verified, unmerged work shows its ticket.

Landed test. Every ref is named in full (refs/heads/<b>, refs/remotes/<r>/<b>), so a local pr/1 beside
refs/remotes/pr/1 is never ambiguous.
  1. into must resolve to a commit, else `cannot decide`. A remote-tracking into is fetched first; a failed fetch
     with a ref that still resolves goes on against the stale ref and says so.
  2. ancestor: git merge-base --is-ancestor refs/heads/<b> <into> exit 0.
  3. pr merged: gh pr list --state merged --head <b> --json headRefOid reports the tip sha (read only; skipped when
     gh or a remote is absent).
  3a. patch (tickets.py inventory only, landed(patch=True)): git cherry <into> <b> <merge base> prints no `+`
     line, so every branch commit has a patch-equivalent in into (patch_landed, shared with orphans).
  4. content: m = git merge-base <into> refs/heads/<b>; git diff --no-renames --name-only m refs/heads/<b>; either
     command failing is `cannot decide`, never an empty list. Landed when every listed path has the same blob at
     the branch and at into, absent on both counting as equal.
  5. else not landed, naming the first path that differs.

Truth table for close and sweep; the first matching row wins.

  row        state                                                          outcome                                                    exit
  host-owned sweep only, before row 1: wtroot.host_owned names the tree         kept <path>: host-owned (<host>)                           0
  1          not a plugin lane                                              not a plugin lane: <path>                                  2
  2          neither tree nor branch exists                                 no lane <name>                                             1
  3          the branch is checked out in another worktree                  branch <b> checked out at <path>                           1
  4          an integration tree with an open lane whose into is its branch lanes still open into <b>: <names>                         1
             (T-0743: a clean host-owned tree whose branch is an ancestor of <b> is not open; the close then prints
             `host-owned <path> landed in <b>; remove it yourself: git worktree remove <path>` and leaves the tree;
             T-0762: nor is a host record whose tree is gone and whose branch is an ancestor of <b>)
  5          into does not resolve, or a git read fails                     cannot decide: <reason>                                    1
  6          tracked changes, or untracked files outside .sdlc/, the        uncommitted changes in <lane>: <first path>                1
             work_root: dir when set, and .lane.json, and no --discard
  locked     the tree is locked (git worktree list --porcelain), except a   locked: <reason>                                           1
             plain close of a lock equal to the record's lock (open's own)
  7          sweep only: no commit since base_sha                           kept <lane>: no commits                                    0
  8          sweep only: a host lane queued in .sdlc/runtime/prune.json     kept <lane>: agent not pruned                              0
             less than 6 hours ago
  recent     sweep only: the tip is younger than lane_min_age_hours         kept <lane>: recent                                        0
  in use     sweep only: a ps line other than this script's names the path  kept <lane>: in use by pid <p>                             0
  9          landed by ancestry                                             closed <lane> (ancestor)                                   0
  pr merged  landed by a merged pull request whose head sha is the tip      closed <lane> (pr merged)                                  0
  10         landed by content                                              closed <lane> (content in <into>)                          0
  11         not landed, no --discard                                       not landed in <into>: first <path>; merge it or --discard  1
  12         close --discard on row 6, 7 or 11                              closed <lane> (discarded <sha>)                            0

  merging    sweep --apply only: a lane whose parent dir holds merge.lock   kept <lane>: merging (merge.lock held)              0
             while another process holds that flock (a land is merging)
  Rows 1 to 5 and locked refuse even with --discard. In sweep a refusing row prints `kept <lane>: <outcome>` and the
  sweep goes on; its exit is 0 unless a close step failed. Sweep keeps any branch in lane_keep:, acts only on plugin
  lanes, deletes no branch that has no lane, and never touches the main worktree or the current checkout. A bare
  sweep is a dry run that prints `would close <lane> (<how>)`; --apply closes. It then runs the wtroot.py crash sweep
  over <worktree root>/tmp (and the legacy tmp dirs) and the scratch dirs with lane_min_age_hours as the limit: `would remove
  <path>` or `removed <path>` for a dead owner past the limit, `unmarked: <path>` for a folder with no owner marker
  (never deleted; one line, `unmarked: <n> folders, first <path>` for several, and only for this repo's own tmp and scratch dirs,
  never a folder under another repo's scratch dir; T-0764); a live or recent owner is kept silently.

Close steps (rows 9, 10, pr merged, 12), in order, so a failure leaves a lane a rerun closes:
  1. Write an annotated tag object (git mktag, never a ref under refs/tags) whose message holds the branch
     description `<ticket> <title>`, the reason (ancestor, pr merged, content in <into>, discarded), into, the tip
     sha and the UTC time; point refs/archive/<UTC date>/<branch> at it with update-ref and a zero old value. If that
     fails, retry once with the leaf <branch>.<sha7>; a second failure stops the close with the branch intact.
  2. Unless discarded, carry each local ticket's records dir into the main checkout's runtime records dir, keeping a
     file there at least as new (T-0566), and print `records: <path>`. Then copy the tree's untracked and ignored
     .sdlc/ files (and the work_root: dir's untracked files when set), and the ignored .sdlc/runtime/tasks/ records (minus *.log,
     *.running, *.run.lock), to <git common dir>/sdlc-lane-archive/<lane>/; a failed write stops the close here.
  3. git worktree unlock <path> when the lane holds its own lock, then git worktree remove --force <path>; a missing
     tree skips this step.
  4. git update-ref -d refs/heads/<b> <sha>: by full name, and only while the branch is at the sha the test read.
  5. git worktree prune; remove a host record; print `port <n> still listening (pid <p>)` when a listener holds
     the lane's port.
  Restore with `lanes.py archive restore <date>/<branch>` (git branch <branch> <ref>; refuses an existing branch).
  archive list reads tag and plain commit targets alike.
  orphans (T-0580) lists each commit that holds work no local branch has: every ref outside refs/heads/ and
  refs/remotes/ that peels to a commit (refs/archive/*, refs/stash, ...) and every dangling commit from
  `git fsck --no-reflogs --connectivity-only` (never --lost-found). A candidate is listed when one of its commits
  is on no local branch (the default branch included) and git cherry finds no patch-equivalent commit there; one
  line each: `<sha> <ref|dangling> <subject> (<n> files)`, n the files the tip commit changes against its first parent. It changes
  nothing, deletes nothing, restores nothing, and exits 0.

Finish (T-0594): `finish <lane>` runs, from the main checkout, the whole end of a lane whose record names one local
ticket and whose into is the main checkout's branch, composing the existing commands. It prints one `<step>: ...` line
per step and stops at the first failure with `<step>: stopped: <why>; fix it, then rerun lanes.py finish <lane>: done
steps are skipped` (exit 1). Each step skips itself when its effect is already there, so a rerun goes on from the stop.
  1. record   dispatch.py record each *.dispatch.json in the ticket's records dir in the lane tree: a verifier whose
              attempt is still running (--verifier-transcript prices it), and the solo (--transcript prices its row
              once; it is idempotent); `nothing pending` when neither is due. --verifier-agent-id ID (--solo-agent-id
              for the solo, T-0800) finds subagents/agent-<ID>.jsonl under the Claude projects folder as dispatch.py
              record --agent-id does (a --transcript or --verifier-transcript names it instead), passes --agent-id,
              --tool-uses and --duration-ms read from it (cost_estimate.transcript_activity; tokens and the result come
              from the transcript inside record); for the verifier then dispatch.py prune --done <dispatch name>, printed
              `; pruned <name>` (the solo is queued later, by the land); no transcript found stops.
  2. verdict  the newest verifier result there must say pass; anything else (fail, none) stops before any commit or
              merge: finish never closes without a pass verdict.
  3. commit   a dirty lane tree is committed as `<id>: <title>` (logs and lock files left out); else `commit: clean`.
  4. land     fanout.py land <branch> --ticket <id> --integration finish/<lane> --lanes-dir <lanes root>/finish/<lane>
              --base <into> --rewrite-refs (--lane solo for a solo lane, --gate <land_gate:> when .sdlc/config sets it,
              default none): the merge with its conflict rules, the record carry, the gate and the ticket close stay
              fanout's. Skipped when the branch is already in into or in finish/<lane>.
  5. settle   fanout.py settle finish/<lane> (--forward --gate <land_gate:> with a gate): into fast-forwards and the
              integration tree closes; the per-lane lanes dir goes. Skipped when finish/<lane> does not exist. With no
              gate and into moved past finish/<lane> (a rerun after a stop), finish first merges into into it in its
              tree, the generated files resolved as a land does (fanout.merge_generated), and commits (T-0595).
  6. close    when the ticket in main is not done or dropped (a merge made by hand, a land stopped after its merge):
              carry the lane's records into main (carry_records), tickets.py close <slug> --rewrite-refs (the verdict
              gate), and commit what it changed as `close <id>`.
  7. lane     close_lane (landed by ancestry), then commit what that close wrote in main as `<id>: lane <lane> closed`,
              a tracked path in an ignored directory included; a failed commit stops (T-0595).
  8. backup   only with --backup REMOTE/REF: git push REMOTE refs/heads/<into>:REF (refs/heads/ added to a bare REF)
              in a detached background process (T-0800), printed `backup: pushing <into> to <remote> <ref> in the
              background; log <git common dir>/sdlc-backup.log`; finish does not wait, and the log ends `exit <code>`.
              A later finish whose log ends `exit <code>` nonzero prints `backup: previous push failed (exit N), see
              <log>` after its steps and exits 1 at least (T-0802).
              Without it nothing is pushed.
  A lane already gone with a landed archive ref prints `finish: <lane> is already finished (archive <ref>)` and exits 0,
  after the backup step when --backup is given.

Ready (T-0590): `ready [<lane>] [--ticket ID]`, run by the worker when its ticket is done, on any host. The ticket is
--ticket, else the record's first local ticket. It refuses (exit 1, nothing written) when the ticket's handoff (the lane
tree's copy, else the main checkout's) lists no item under ## Acceptance criteria, or when the lane's state has the tree
of base_sha (else the merge base with into): `no changes in <lane> since <sha>`. The state is HEAD plus every tracked and
untracked file git does not ignore (minus *.log, .run.lock, *.running), written through a copy of the index with
add -A and write-tree, never git stash. A state equal to HEAD pins HEAD; otherwise git commit-tree writes a snapshot
commit on HEAD (subject `sdlc ready snapshot: <id> in <lane>`, a `Lane-Base: <base sha>` trailer, printed as
`snapshot: ...`), and nothing in the tree or its index changes. Then:
  1. git update-ref refs/sdlc/ready/<id> <sha> (a rerun moves it) and print `ready: <ref> <sha>`.
  2. Clear the lane's own lock (the record's lock, as close does): `unlocked: <reason>`; a foreign lock is kept and
     printed as `still locked: <reason> (not the lock open set)`.
  3. messages.py send --receiver <factory> --sender <lane name as a mailbox name> --kind handoff --topic "ready <id>"
     --follow-up false with the body `<sha> <lane path>` and a line naming ticket, lane and branch. The receiver is the
     .sdlc/config factory: line, else factory. A receiver with no registered mailbox prints a `warning: not
     sent to <receiver>` line naming `lanes.py list --ready` and `messages.py register --name <receiver>` and exits 0
     (the ref is pinned and the lane unlocked, T-0610); that warning prints in full once per session (the session is
     CLAUDE_CODE_SESSION_ID, else the parent pid; marker files under <git common dir>/sdlc/ready-warned/), and later
     readies print `not sent: no <receiver> mailbox (warned once)` (T-0694); any other refused send prints `not sent to <receiver>: <why>;
     tell the factory yourself` and exits 1 with the ref kept.
  --notify-cmd CMD (T-0694): once the ref is pinned, run CMD through the shell in the main checkout with
  SDLC_READY_TICKET, SDLC_READY_SHA and SDLC_READY_PATH set; print `notified: CMD rc=<n>`. A non-zero rc prints a
  warning and the ready still exits 0. With it the missing-mailbox warning is not printed; a registered mailbox still
  gets the message.
list --ready reads refs/sdlc/ready/* and joins each to the lane whose record lists the ticket. A row is stale when the
lane's HEAD differs from the pinned HEAD (a snapshot's parent, else the sha) or its state's tree from the sha's tree,
or when no lane holds the ticket. dispatch.py prepare verifier reads the same ref: `Review sha: <sha>`, and Base sha
from the snapshot's Lane-Base: trailer (pin(), the Python API it shares). Every close deletes
refs/sdlc/ready/<id> for each local ticket of the record.

Open also adds /node_modules to <git common dir>/info/exclude (T-0773): .gitignore's node_modules/ does not match a symlink.

Record fields. .lane.json at the tree root, written by open, added to <git common dir>/info/exclude; a host record
<lanes root>/host/<name>.lane.json has the same fields.
  lane      the lane name (the tree leaf)          kind      fanout, integration or solo (host for a host record)
  branch    the lane branch                        base      the --base ref          base_sha  its sha at open
  into      the ref the landed test reads          tickets   the ticket ids          port      a port, or null
  opened    UTC time of open                       run_id    $SDLC_RUN_ID, or null   setup     ok, failed rc=<n> (<cmd>), or null
  lock      the reason open locked the tree with, or null
  open also writes branch.<b>.description as `<ticket> <title>` (cut to 120 characters).
  Lock (T-0589): the CLI open of a fanout or solo lane (the Python open_lane only with lock=True) runs git worktree lock
  --reason "<holder> <tickets>" and prints `locked: <reason>`; the holder is refs/sdlc/claims/<id> (T-0588), else the
  ticket's claimed_by:, its date dropped, else <host>:<session> from the environment. A locked lane is running: list
  shows `running (<reason>)` where it would show open or closable (`stale, locked` stays), and sweep keeps it. ready
  (T-0590) or a plain close of a landed lane clears that lock; close --discard refuses until `git worktree unlock`.

Config (.sdlc/config of the main worktree; blank and # lines ignored):
  lanes_root: <path>        default wtroot.py root: the sibling <main checkout parent>/<name>.worktrees (T-0563; legacy .claude/worktrees
                            in 0.23 and .worktrees before, both still read for one release), or a bare clone's <bare parent>/lanes
                            or a worktree_root: line (T-0561); a set path is relative to the main worktree's toplevel
  lane_into: <ref>          default none (main)
  lane_setup: <cmd>         run in a new tree; repeat the line for several commands, run in order, the first failure stops the rest;
                            open prints and records setup: ok or setup: failed rc=<n> (<cmd>) and keeps the lane (T-0692);
                            with package.json and no lane_setup: line, open prints a note instead (T-0773)
  lane_ports: <lo>-<hi>     off when absent; open picks the lowest free port under a flock on <lanes root>/lanes.lock
  lane_stale_days: <n>      default 10        lane_min_age_hours: <n>  default 2
  lane_keep: <branch>...    sweep keeps these  lane_names:, lane_sweep:  read and returned only (fanout owns them)
  plugin_min: <X.Y.Z>       open refuses (exit 2) when the running plugin ($SDLC_BACKEND's manifest) is older (T-0593)
  land_gate: <cmd>          the gate finish passes to fanout.py land and settle; default none
  factory: <name>         the mailbox receiver ready sends to; default factory (T-0590)
  lane_landing: local       finish lands into main locally although main tracks an upstream, so open commits the claim
                            and the record in main; default: a PR repo when main tracks an upstream (T-0609, T-0804)
"""
import argparse, contextlib, datetime, fcntl, io, json, os, pathlib, re, shutil, socket, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tickets  # same scripts/ dir: the only front matter parser
TICKETS = tickets  # open_lane's tickets= parameter shadows the module name
import order  # same scripts/ dir: newest-result ordering
import results  # same scripts/ dir: the verifier verdict
import wtroot  # same scripts/ dir: the worktree root, owner markers and the crash sweep (T-0550)
import plugin_min  # same scripts/ dir: the repo's minimum plugin version (T-0593)
import roots  # same scripts/ dir: the work-root record prefixes (T-0626)

Path = pathlib.Path
RECORD = '.lane.json'
LOCAL_SETTINGS = '.claude/settings.local.json'
NODE_MODULES = '/node_modules'  # T-0773, #81: .gitignore's `node_modules/` does not match a symlink; the lane exclude does
FIELDS = ('lane', 'kind', 'branch', 'base', 'base_sha', 'into', 'tickets', 'port', 'opened', 'run_id', 'setup', 'lock')
KINDS = ('fanout', 'integration', 'solo')
LOCAL_ID = re.compile(r'T-\d+')
PRUNE_REL = Path('.sdlc') / 'runtime' / 'prune.json'  # dispatch.py PRUNE_REL
PRUNE_TTL = 6 * 3600
NAMESPACES = ('lane/', 'wave/', 'release/')
CONFIG_KEYS = ('lanes_root', 'lane_into', 'lane_setup', 'lane_ports', 'lane_stale_days', 'lane_min_age_hours',
               'lane_keep', 'lane_names', 'lane_sweep', 'land_gate', 'factory', 'lane_landing')
READY_REFS = 'refs/sdlc/ready/'  # T-0590: dispatch.py READY_REFS
SNAPSHOT_SUBJECT = 'sdlc ready snapshot:'
SNAPSHOT_SKIP = (':(exclude,glob)**/*.log', ':(exclude,glob)**/.run.lock', ':(exclude,glob)**/*.running')


class LaneError(Exception):
    pass


# ---- git and small helpers --------------------------------------------------------------------------------

def git(cwd, *args, inp=None):
    return subprocess.run(['git', *args], cwd=str(cwd), capture_output=True, text=True, input=inp)


def out(cwd, *args):
    r = git(cwd, *args)
    return r.stdout.strip() if r.returncode == 0 else None


def run(cmd, cwd, timeout=30):
    try:
        return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def err(r):
    lines = (r.stderr or r.stdout or '').strip().splitlines()
    return lines[-1] if lines else f'exit {r.returncode}'


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def samepath(a, b):
    return os.path.realpath(str(a)) == os.path.realpath(str(b))


def plain_under(child, parent):
    child, parent = os.path.normpath(str(child)), os.path.normpath(str(parent))
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def under(child, parent):
    """True when child is parent or lies inside it, compared by real path (C1 as amended in 17.7)."""
    child, parent = os.path.realpath(str(child)), os.path.realpath(str(parent))  # REALPATH
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def slug(s):
    return re.sub(r'[^a-z0-9-]+', '-', s.lower())[:40]


def result(rc, message, lane=None, path=None, branch=None, **extra):
    d = dict(rc=rc, message=message, lane=lane, path=None if path is None else str(path), branch=branch)
    d.update(extra)
    return d


def read_json(p):
    try:
        d = json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


@contextlib.contextmanager
def flock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


# ---- config and repository context ------------------------------------------------------------------------

def config(toplevel):
    """The lane keys of <toplevel>/.sdlc/config with their defaults (see the docstring)."""
    top = Path(toplevel)
    vals, keep, setups = {}, [], []
    path = top / '.sdlc' / 'config'
    lines = path.read_text(encoding='utf-8').splitlines() if path.is_file() else []
    for line in lines:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = re.match(r'\s*(%s)\s*:\s*(.*?)\s*$' % '|'.join(CONFIG_KEYS), line)
        if not m:
            continue
        k, v = m.groups()
        if k == 'lane_keep':
            keep += [x for x in re.split(r'[\s,]+', v) if x]
        elif k == 'lane_setup':  # T-0692: every line counts, in order
            if v:
                setups.append(v)
        else:
            vals[k] = v
    ports = None
    m = re.fullmatch(r'(\d+)\s*-\s*(\d+)', vals.get('lane_ports', ''))
    if m and int(m.group(1)) <= int(m.group(2)):
        ports = (int(m.group(1)), int(m.group(2)))

    def num(k, d):
        try:
            return float(vals[k])
        except (KeyError, ValueError):
            return d
    # T-0561: no lanes_root line takes wtroot.py root (a worktree_root: line, else the sibling <parent>/<name>.worktrees
    # of the main checkout, T-0563, else a bare clone's <bare parent>/lanes), never a path under the current lane
    root = os.path.expanduser(vals.get('lanes_root') or str(wtroot.root(top) or wtroot.default_root(top)))
    return dict(lanes_root=Path(os.path.normpath(os.path.join(str(top), root))), lane_into=vals.get('lane_into') or None,
                lane_setup=setups, lane_ports=ports, lane_stale_days=num('lane_stale_days', 10),
                lane_min_age_hours=num('lane_min_age_hours', 2), lane_keep=keep, lane_names=vals.get('lane_names'),
                lane_sweep=vals.get('lane_sweep'), land_gate=vals.get('land_gate') or None, factory=vals.get('factory') or None,
                lane_landing=vals.get('lane_landing') or None)


def worktrees(cwd):
    r = git(cwd, 'worktree', 'list', '--porcelain')
    if r.returncode:
        raise LaneError(f'not a git repository: {cwd} ({err(r)})')
    res, cur = [], None
    for line in r.stdout.splitlines() + ['']:
        if line.startswith('worktree '):
            cur = dict(path=line[9:], head=None, branch=None, locked=None, bare=False)
        elif cur is None:
            continue
        elif line.startswith('HEAD '):
            cur['head'] = line[5:]
        elif line.startswith('branch '):
            b = line[7:]
            cur['branch'] = b[len('refs/heads/'):] if b.startswith('refs/heads/') else b
        elif line == 'bare':
            cur['bare'] = True
        elif line == 'locked' or line.startswith('locked '):
            cur['locked'] = line[7:]
        elif line == '':
            res.append(cur)
            cur = None
    return res


class Ctx:
    def __init__(self, cwd='.'):
        cwd = os.path.abspath(str(cwd))
        if not os.path.isdir(cwd):
            raise LaneError(f'no such directory: {cwd}')
        self.cwd = cwd
        self.refresh()
        first = self.wts[0]
        self.top = first['path'] if not first['bare'] else (out(cwd, 'rev-parse', '--show-toplevel') or first['path'])
        main = next((w for w in self.wts if not w['bare']), first)
        self.main = main['branch'] or main['head']
        self.cfg = config(self.top)
        self.root = self.cfg['lanes_root']
        cd = out(cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir') or out(cwd, 'rev-parse', '--git-common-dir')
        self.common = Path(os.path.normpath(os.path.join(cwd, cd or '.git')))
        cur = out(cwd, 'rev-parse', '--show-toplevel')
        self.current = os.path.realpath(cur) if cur else None
        self.fetched = {}

    def refresh(self):
        self.wts = worktrees(self.cwd)


def has_ref(top, ref):
    return git(top, 'rev-parse', '--verify', '-q', ref).returncode == 0


def landed_and_gone(top, path, branch, into, commit=None):
    """T-0762 and T-0777: True when the tree at path is gone and branch is a local ref that is an ancestor of the local
    branch into, so the lane landed and holds nothing open (evaluate's HOST-GONE rule; fanout.py's land report).
    T-0784: with the branch ref deleted too (settle prints `git branch -d` for it), a land journal's merge commit that
    is an ancestor of into says the same, as a second round's integration branch cut from main holds it."""
    if pathlib.Path(path).is_dir():
        return False
    if has_ref(top, f'refs/heads/{branch}'):
        return git(top, 'merge-base', '--is-ancestor', f'refs/heads/{branch}', f'refs/heads/{into}').returncode == 0
    return bool(commit) and has_ref(top, f'{commit}^{{commit}}') \
        and git(top, 'merge-base', '--is-ancestor', commit, f'refs/heads/{into}').returncode == 0


# ---- lane discovery and ownership -------------------------------------------------------------------------

def blank(path, exists, branch=None, head=None, locked=None):
    return dict(path=str(path), exists=exists, branch=branch, head=head, locked=locked, owner='', kind='manual',
                lane=os.path.basename(str(path)), into=None, base=None, base_sha=None, tickets=[], port=None,
                record=None, record_path=None, record_branch=None, setup=None, lock=None)


def apply_record(ctx, d, rec, host=False):
    d['record'] = rec
    d['kind'] = rec.get('kind') or ('host' if host else 'fanout')
    d['lane'] = rec.get('lane') or d['lane']
    d['record_branch'] = rec.get('branch')
    if rec.get('branch'):
        d['branch'] = rec['branch']
    d['into'] = rec.get('into') or ctx.cfg['lane_into'] or ctx.main
    for k in ('base', 'base_sha', 'port', 'setup', 'lock'):
        d[k] = rec.get(k)
    t = rec.get('tickets') or []
    d['tickets'] = [t] if isinstance(t, str) else list(t)


def lane_of(ctx, w):
    p = w['path']
    d = blank(p, os.path.isdir(p), w['branch'], w['head'], w['locked'])
    d['tree_branch'] = w['branch']
    rec = read_json(os.path.join(p, RECORD))
    hp = next((h / (os.path.basename(p) + '.lane.json') for h in host_dirs(ctx) if (h / (os.path.basename(p) + '.lane.json')).is_file()),
              ctx.root / 'host' / (os.path.basename(p) + '.lane.json'))
    hrec = read_json(hp) if hp.is_file() else None
    parent = os.path.dirname(p)
    if rec is not None:
        d.update(owner='record', record_path=os.path.join(p, RECORD))
        apply_record(ctx, d, rec)
    elif hrec is not None:
        d.update(owner='host', record_path=str(hp))
        apply_record(ctx, d, hrec, host=True)
        d['lane'] = hrec.get('lane') or os.path.basename(p)
    elif os.path.isfile(os.path.join(parent, 'merge.lock')) and os.path.isdir(os.path.join(parent, 'logs')):
        d['owner'] = 'legacy'
        base = os.path.basename(p)
        if base == 'integration':
            d['kind'] = 'integration'
            d['into'] = ctx.cfg['lane_into'] or ctx.main
        else:
            d['kind'] = 'rolling scratch' if (base == 'rolling' and not w['branch']) else 'fanout'
            integ = next((x for x in ctx.wts if samepath(x['path'], os.path.join(parent, 'integration'))), None)
            d['into'] = (integ and integ['branch']) or ctx.main
    elif any(plain_under(p, t) for t in tmp_dirs(ctx.top)):
        d['kind'] = 'runner tmp'
    return d


def tmp_dirs(top):
    """The runner tmp dirs: wtroot.py's tmp root (the sibling root's, T-0563, or under a worktree_root: line or a bare
    clone's root, T-0561), then the legacy <top>/.claude/worktrees/tmp and <top>/.worktrees/tmp read for one release."""
    return wtroot.tmp_roots(top) or [wtroot.default_root(top) / 'tmp']


def host_dirs(ctx):
    """Where host records live: <lanes root>/host, and the legacy <top>/.claude/worktrees/host and <top>/.worktrees/host
    read for one release (T-0563, T-0550)."""
    return [h for h in dict.fromkeys([ctx.root / 'host'] + [r / 'host' for r in wtroot.legacy_roots(ctx.top)]) if h.is_dir()]


def discover(ctx):
    """A lane dict for every worktree except the main one, plus host records whose tree is absent."""
    lanes, seen = [], set()
    for w in ctx.wts:
        if w['bare'] or samepath(w['path'], ctx.top):
            continue
        seen.add(os.path.realpath(w['path']))
        lanes.append(lane_of(ctx, w))
    for hp in sorted(hp for hd in host_dirs(ctx) for hp in hd.glob('*.lane.json')):
        name = hp.name[:-len('.lane.json')]
        tp = Path(ctx.top, *wtroot.CLAUDE, name)  # the host's own worktree dir, not the lanes root
        if os.path.realpath(str(tp)) in seen:
            continue
        seen.add(os.path.realpath(str(tp)))
        rec = read_json(hp)
        if rec is None:
            continue
        d = blank(tp, False)
        d.update(owner='host', record_path=str(hp), tree_branch=None)
        apply_record(ctx, d, rec, host=True)
        d['lane'] = rec.get('lane') or name
        lanes.append(d)
    return lanes


def find(ctx, lanes, target):
    """(lane, None) or (None, refusal result) for a close target, a name or a path."""
    if os.path.exists(target):
        for d in lanes:
            if samepath(d['path'], target):
                return d, None
        return None, result(2, f'not a plugin lane: {os.path.realpath(target)}', path=os.path.realpath(target), row='1')
    hits = [d for d in lanes if target in (d['lane'], os.path.basename(d['path']), d['branch'])]
    hits.sort(key=lambda d: not d['owner'])
    if hits:
        return hits[0], None
    return None, result(1, f'no lane {target}', lane=target, row='2')


# ---- the landed test --------------------------------------------------------------------------------------

def blob(cwd, ref, path):
    return out(cwd, 'rev-parse', '-q', '--verify', f'{ref}:{path}')


def has_remote(cwd):
    return bool(out(cwd, 'remote'))


def gh_json(cwd, args):
    if not shutil.which('gh') or not has_remote(cwd):
        return None
    r = run(['gh', *args], cwd, timeout=30)
    if r is None or r.returncode:
        return None
    try:
        data = json.loads(r.stdout or '[]')
    except ValueError:
        return None
    return data if isinstance(data, list) else None


def pr_merged(cwd, branch, tip):
    data = gh_json(cwd, ['pr', 'list', '--state', 'merged', '--head', branch, '--json', 'headRefOid'])
    return bool(data) and any(isinstance(x, dict) and x.get('headRefOid') == tip for x in data)


def patch_landed(top, into, ref):
    """The set of ref's commits (since its merge base with into) that git cherry finds no patch-equivalent of in
    into; empty means every commit landed by patch. None when git cherry fails."""
    mb = out(top, 'merge-base', into, ref)
    c = git(top, 'cherry', into, ref, *([mb] if mb else []))
    if c.returncode:
        return None
    return {l[2:].strip() for l in c.stdout.splitlines() if l.startswith('+ ')}


def landed(cwd, ref, into, branch=None, pr=True, patch=False):
    """('ancestor' | 'pr merged' | 'patch' | 'content' | 'not landed' | 'cannot decide', detail) for a full ref
    against into. 'patch' only with patch=True (tickets.py inventory); close and sweep never ask for it."""
    if git(cwd, 'rev-parse', '--verify', '-q', into + '^{commit}').returncode:
        return 'cannot decide', f'into {into} does not resolve'
    tip = out(cwd, 'rev-parse', '--verify', '-q', ref + '^{commit}')
    if not tip:
        return 'cannot decide', f'{ref} does not resolve'
    r = git(cwd, 'merge-base', '--is-ancestor', ref, into)
    if r.returncode == 0:
        return 'ancestor', ''
    if r.returncode != 1:
        return 'cannot decide', f'git merge-base --is-ancestor failed: {err(r)}'
    if pr and branch and pr_merged(cwd, branch, tip):
        return 'pr merged', ''
    if patch and patch_landed(cwd, into, ref) == set():
        return 'patch', ''
    m = git(cwd, 'merge-base', into, ref)
    mb = m.stdout.strip()
    d = git(cwd, 'diff', '--no-renames', '--name-only', '-z', mb, ref)  # NO-RENAMES
    if m.returncode or d.returncode: return 'cannot decide', f'no diff from the merge base of {ref} and {into}: {err(m) if m.returncode else err(d)}'  # DIFF-FAIL
    for p in [x for x in d.stdout.split('\0') if x]:
        a, b = blob(cwd, ref, p), blob(cwd, into, p)
        if a != b: return 'not landed', p  # ABSENT-EQUAL
    return 'content', ''


def resolve_into(ctx, into, fetch=True):
    """(full ref or sha, note); the ref is None when into does not resolve. A remote-tracking ref is fetched first."""
    top, note = ctx.top, ''
    remotes = (out(top, 'remote') or '').split()
    if into.startswith('refs/'):
        ref = into
    elif has_ref(top, f'refs/heads/{into}'):
        ref = f'refs/heads/{into}'
    elif into.split('/')[0] in remotes or has_ref(top, f'refs/remotes/{into}'):
        ref = f'refs/remotes/{into}'
    else:
        ref = into
    if fetch and ref.startswith('refs/remotes/') and ref.split('/')[2] in remotes:
        rem = ref.split('/')[2]
        if rem not in ctx.fetched:
            r = git(top, 'fetch', '-q', rem)
            ctx.fetched[rem] = r.returncode == 0
        if not ctx.fetched[rem]:
            note = f'fetch {rem} failed; testing against the stale ref'
    if git(top, 'rev-parse', '--verify', '-q', ref + '^{commit}').returncode:
        return None, note
    return ref, note


def trail_prefixes(path):
    """The repo-relative prefixes of the tree's work records: '.sdlc/', plus '<work_root>/' when its .sdlc/config
    sets one (T-0626). A config roots refuses keeps '.sdlc/' alone."""
    try:
        return roots.record_prefixes(path)
    except roots.Fail:
        return ('.sdlc/',)


def first_dirty(path):
    """(first dirty path or None, error or None): tracked changes, or untracked files outside .lane.json and the
    trail_prefixes (.sdlc/, and the work root when set)."""
    prefixes = trail_prefixes(path)
    r = git(path, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    if r.returncode:
        return None, f'git status failed in {path}: {err(r)}'
    parts = r.stdout.split('\0')
    i = 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        code, p = e[:2], e[3:]
        if code[0] in 'RC':
            i += 1
        if code == '??' and (p == RECORD or any(p == x.rstrip('/') or p.startswith(x) for x in prefixes)):
            continue
        return p, None
    return None, None


def prune_queued(ctx, name):
    try:
        data = json.loads((Path(ctx.top) / PRUNE_REL).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return False
    for e in data if isinstance(data, list) else []:
        if not isinstance(e, dict) or e.get('name') != name:
            continue
        try:
            at = datetime.datetime.fromisoformat(str(e.get('recorded_at', '')).replace('Z', '+00:00'))
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=datetime.timezone.utc)
        if (utcnow() - at).total_seconds() < PRUNE_TTL:
            return True
    return False


def in_use(path):
    r = run(['ps', '-axo', 'pid=,command='], '/', timeout=15)
    if r is None or r.returncode:
        return None
    variants = {str(path), os.path.realpath(str(path))}
    variants |= {v[len('/private'):] for v in list(variants) if v.startswith('/private/')}
    pat = re.compile('|'.join(re.escape(v) + r'(?=$|[/\s\'"])' for v in variants))
    me = os.getpid()
    for line in r.stdout.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) != me and pat.search(parts[1]):
            return int(parts[0])
    return None


def tip_age(top, ref):
    ct = out(top, 'log', '-1', '--format=%ct', ref)
    return time.time() - int(ct) if ct and ct.isdigit() else None


def evaluate(ctx, d, lanes, mode, discard=False, into=None, fetch=True, pr=True):
    """(row, outcome, rc, info) by the truth table; info carries how, sha and into when the row closes."""
    top, name = ctx.top, d['lane']
    if not d['owner']:
        return '1', f'not a plugin lane: {d["path"]}', 2, {}
    b = d['branch']
    hb = bool(b) and has_ref(top, f'refs/heads/{b}')
    if not d['exists'] and not hb:
        return '2', f'no lane {name}', 1, {}
    if b:
        for w in ctx.wts:
            if w['branch'] == b and not samepath(w['path'], d['path']):
                return '3', f'branch {b} checked out at {w["path"]}', 1, {}
    hosts = []  # T-0743: landed host-owned trees that do not hold the integration tree open, named in the close
    if d['kind'] == 'integration' and b:
        names = []
        for o in lanes:
            if o is d or not o['owner'] or o['kind'] == 'integration':
                continue
            oi = (o['into'] or '')
            oi = oi[len('refs/heads/'):] if oi.startswith('refs/heads/') else oi
            if oi == b and (o['exists'] or (o['branch'] and has_ref(top, f'refs/heads/{o["branch"]}'))):
                if o['exists'] and o['branch'] and wtroot.host_owned(o['path']) and has_ref(top, f'refs/heads/{o["branch"]}') \
                        and not git(top, 'merge-base', '--is-ancestor', f'refs/heads/{o["branch"]}', f'refs/heads/{b}').returncode \
                        and first_dirty(o['path']) == (None, None):  # dirty work has not landed
                    hosts.append(o['path'])
                    continue
                if not o['exists'] and o['owner'] == 'host' and o['branch'] \
                        and landed_and_gone(top, o['path'], o['branch'], b):  # HOST-GONE
                    continue  # T-0762: a host record whose tree is gone and whose branch landed holds nothing open
                names.append(o['lane'])
        if names:
            return '4', f'lanes still open into {b}: {", ".join(names)}', 1, {}
    if not b:
        return '5', f'cannot decide: no branch at {d["path"]}', 1, {}
    if not hb:
        return '5', f'cannot decide: branch {b} not found', 1, {}
    tip = out(top, 'rev-parse', '--verify', '-q', f'refs/heads/{b}')
    target = into or d['into'] or ctx.cfg['lane_into'] or ctx.main
    ref, note = resolve_into(ctx, target, fetch)
    if ref is None:
        return '5', f'cannot decide: into {target} does not resolve' + (f' ({note})' if note else ''), 1, {}
    dirty = None
    if d['exists']:
        dirty, e = first_dirty(d['path'])
        if e:
            return '5', f'cannot decide: {e}', 1, {}
    force = False
    if dirty and not discard: return '6', f'uncommitted changes in {name}: {dirty}', 1, {}  # DIRTY-CHECK
    if dirty:
        force = True
    own = mode == 'close' and not discard and d['lock'] and d['locked'] == d['lock']  # the lock this lane's open set
    if d['locked'] is not None and not own:
        return 'locked', f'locked: {d["locked"] or "no reason"}', 1, {}
    if mode == 'sweep':
        if d['base_sha']:
            n = out(top, 'rev-list', '--count', f'{d["base_sha"]}..refs/heads/{b}')
            if n == '0':
                return '7', 'no commits', 0, {}
        if d['owner'] == 'host' and prune_queued(ctx, name):
            return '8', 'agent not pruned', 0, {}
        age = tip_age(top, f'refs/heads/{b}')
        if age is not None and age < ctx.cfg['lane_min_age_hours'] * 3600:
            return 'recent', 'recent', 0, {}
        if d['exists']:
            pid = in_use(d['path'])
            if pid:
                return 'in use', f'in use by pid {pid}', 0, {}
    info = dict(sha=tip, into=target, note=note, hosts=hosts)
    if force:
        return '12', f'closed {name} (discarded {tip})', 0, dict(info, how='discarded')
    how, detail = landed(top, f'refs/heads/{b}', ref, branch=b, pr=pr)
    if how == 'ancestor':
        return '9', f'closed {name} (ancestor)', 0, dict(info, how=how)
    if how == 'pr merged':
        return 'pr merged', f'closed {name} (pr merged)', 0, dict(info, how=how)
    if how == 'content':
        return '10', f'closed {name} (content in {target})', 0, dict(info, how=how)
    if how == 'cannot decide':
        return '5', f'cannot decide: {detail}', 1, {}
    if discard:
        return '12', f'closed {name} (discarded {tip})', 0, dict(info, how='discarded')
    return '11', f'not landed in {target}: first {detail}; merge it or --discard', 1, {}


# ---- close ------------------------------------------------------------------------------------------------

def write_archive(ctx, b, sha, desc, reason, into):
    """(ref, None) after the archive tag and ref are written, or (None, error) with nothing deleted."""
    top = ctx.top
    now = utcnow()
    head = desc or '(no description)'  # DESC-COPY
    msg = (f'{head}\n\nbranch: {b}\nreason: {reason}\ninto: {into}\nsha: {sha}\n'
           f'time: {now.strftime("%Y-%m-%dT%H:%M:%SZ")}\n')
    ident = out(top, 'var', 'GIT_COMMITTER_IDENT') or f'lanes.py <lanes.py@localhost> {int(time.time())} +0000'
    body = f'object {sha}\ntype commit\ntag {b}\ntagger {ident}\n\n{msg}'
    r = git(top, 'mktag', inp=body)
    if r.returncode:
        r = git(top, 'hash-object', '-t', 'tag', '-w', '--stdin', inp=body)
    if r.returncode:
        return None, f'cannot write the archive tag for {b}: {err(r)}; branch {b} kept'
    tag = r.stdout.strip()
    zero = '0' * len(sha)
    ref = f'refs/archive/{now.strftime("%Y-%m-%d")}/{b}'
    r = git(top, 'update-ref', ref, tag, zero)  # ARCHIVE-ZERO
    if r.returncode:
        ref = f'{ref}.{sha[:7]}'
        r = git(top, 'update-ref', ref, tag, zero)
    if r.returncode: return None, f'cannot write {ref}: {err(r)}; branch {b} kept'  # ARCHIVE-STOP
    return ref, None


def copy_sdlc(path, dest):
    r = git(path, 'ls-files', '--others', '-z', '--', *(x.rstrip('/') for x in trail_prefixes(path)))
    if r.returncode:
        return f'git ls-files failed: {err(r)}'
    skip = ('.log', '.running', '.run.lock')
    rels = [x for x in r.stdout.split('\0')
            if x and not (x.startswith('.sdlc/runtime/tasks/') and x.endswith(skip))]
    try:
        for rel in rels:
            src, dst = Path(path) / rel, Path(dest) / rel
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
    except OSError as e:
        return str(e)
    return None


def runtime_records(task_dir):
    """The runtime records dir of a ticket folder, <nearest .sdlc>/runtime/tasks/<name without leading dots>, whatever
    order.records_dir's legacy rule says for it (order._base finds the base)."""
    p = os.path.abspath(os.fspath(task_dir))
    return Path(order._base(p)) / 'runtime' / 'tasks' / os.path.basename(p).lstrip('.')


def merge_runs(src, dst):
    """T-0775: append to the runs.jsonl dst each line of the runs.jsonl src that dst lacks, keeping every dst line; a
    line is present when dst holds its attempt_id (dst's row wins), else the same whole line. Returns True when dst
    changed."""
    def key(line):
        try:
            row = json.loads(line)
        except ValueError:
            row = None
        return ('a', row['attempt_id']) if isinstance(row, dict) and row.get('attempt_id') else ('l', line)
    d = Path(dst)
    have = d.read_text(encoding='utf-8') if d.is_file() else ''
    seen = {key(ln.strip()) for ln in have.splitlines() if ln.strip()}
    add = []
    for ln in Path(src).read_text(encoding='utf-8').splitlines():
        k = key(ln.strip())
        if ln.strip() and k not in seen:
            seen.add(k)
            add.append(ln.strip() + '\n')
    if not add:
        return False
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(have + ('\n' if have and not have.endswith('\n') else '') + ''.join(add), encoding='utf-8')
    return True


def copy_record(src, dst):
    """copytree's copy_function for a records dir: a runs.jsonl merges into dst (merge_runs), any other file overwrites."""
    if os.path.basename(src) == 'runs.jsonl':
        merge_runs(src, dst)
    else:
        shutil.copy2(src, dst)
    return dst


def copy_newer(src, dst):
    """Copy the files under records dir src into dst, without logs or lock files, keeping (never overwriting or
    deleting) a dst file at least as new as its source, except runs.jsonl, whose rows merge (merge_runs, T-0775).
    Returns the number of files copied."""
    n = 0
    for dirpath, _, files in os.walk(str(src)):
        for f in files:
            if f.endswith(('.log', '.running', '.run.lock')):
                continue
            s = Path(dirpath) / f
            d = Path(dst) / s.relative_to(src)
            if f == 'runs.jsonl':
                n += merge_runs(s, d)
                continue
            if d.exists() and d.stat().st_mtime >= s.stat().st_mtime:
                continue
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(s), str(d))
            n += 1
    return n


def carry_records(src_folder, dst_folder):
    """T-0566: carry ticket folder src_folder's records dir (order.records_dir) into dst_folder's runtime records dir
    (copy_newer), so a close in the main checkout finds the lane's verdict. Returns the dst records dir, or None when
    there is nothing to carry: no records dir, a legacy ticket whose records travel in the folder itself, or the same
    dir on both sides."""
    src = order.records_dir(src_folder)
    if not src.is_dir() or samepath(src, src_folder):
        return None
    dst = runtime_records(dst_folder)
    if samepath(src, dst):
        return None
    dst = order.records_dir(dst, create=True)
    copy_newer(src, dst)
    return dst


def owner_root(kind, tree):
    """<the checkout that owns kind for the lane or checkout tree>/.sdlc (wtroot.owner_tree, T-0752), else tree's."""
    return Path(wtroot.owner_tree(kind, None, tree) or tree) / '.sdlc'


def carry_lane_records(ctx, d):
    """Carry the records of each local ticket of lane d from the tree that owns them into the one that owns the lane
    close (carry_records; wtroot.owner_tree records and lane-close, T-0752), before the tree is removed. Returns the
    `records: <path>` lines."""
    lines = []
    lroot = owner_root('records', d['path'])
    mroot = owner_root('lane-close', ctx.top)
    if not lroot.is_dir():
        return lines
    try:
        ltdir = tickets.ticket_dir(lroot)
        mtdir = tickets.ticket_dir(mroot)  # T-0639: the main checkout's own ticket dir, docs/work under a work_root
        metas = tickets.load(ltdir)
    except tickets.Fail:
        return lines
    want = {str(t) for t in d['tickets'] if LOCAL_ID.fullmatch(str(t))}
    for slug, meta in metas:
        if meta.get('id') in want:
            dst = carry_records(ltdir / slug, mtdir / slug)
            if dst is not None:
                lines.append(f'records: {dst}')
    return lines


def port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', int(port)))
        return True
    except OSError:
        return False
    finally:
        s.close()


def port_line(port):
    if not port or port_free(port):
        return None
    pid = '?'
    if shutil.which('lsof'):
        r = run(['lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN', '-t'], '/', timeout=10)
        if r is not None and r.stdout.strip():
            pid = r.stdout.split()[0]
    return f'port {port} still listening (pid {pid})'


def local_tickets(top):
    rootp = Path(top) / '.sdlc'
    if not rootp.is_dir():
        return []
    try:
        return tickets.load(tickets.ticket_dir(rootp))
    except tickets.Fail:
        return []


def do_close(ctx, d, outcome, info, dry):
    top, name, b, sha, how, into = ctx.top, d['lane'], d['branch'], info['sha'], info['how'], info['into']
    pre = [info['note']] if info.get('note') else []
    if dry:
        return result(0, '\n'.join(pre + ['would close ' + outcome[len('closed '):]]), lane=name, path=d['path'], branch=b, row=how)
    desc = out(top, 'config', '--get', f'branch.{b}.description') or ''
    reason = {'content': f'content in {into}'}.get(how, how)
    ref, e = write_archive(ctx, b, sha, desc, reason, into)
    if e:
        return result(1, '\n'.join(pre + [e]), lane=name, path=d['path'], branch=b)
    carried = []
    # T-0752: the tree that owns the branch: and worktree: lines, read while the lane record still exists
    owner = wtroot.owner_tree('branch', None, d['path']) if d['exists'] else None
    closer = wtroot.owner_tree('ticket-close', None, d['path']) if d['exists'] else None  # T-0769, read at the end
    if d['exists']:
        if how != 'discarded':  # a discarded lane's verdict must not close the ticket in main
            try:
                carried = carry_lane_records(ctx, d)
            except OSError as e:
                return result(1, '\n'.join(pre + [f'cannot carry the records of {name} into the main checkout: {e}; '
                                                  f'archive ref {ref} kept, lane not closed']), lane=name, path=d['path'], branch=b)
        e = copy_sdlc(d['path'], ctx.common / 'sdlc-lane-archive' / name)
        if e:
            return result(1, '\n'.join(pre + [f'cannot archive the .sdlc files of {name}: {e}; archive ref {ref} kept, lane not closed']),
                          lane=name, path=d['path'], branch=b)
        if d['locked'] is not None:  # only the lane's own lock gets here (evaluate); a locked tree needs a second --force
            git(top, 'worktree', 'unlock', d['path'])
        r = git(top, 'worktree', 'remove', '--force', d['path'])
        if r.returncode:
            return result(1, '\n'.join(pre + [f'cannot remove {d["path"]}: {err(r)}']), lane=name, path=d['path'], branch=b)
    r = git(top, 'update-ref', '-d', f'refs/heads/{b}', sha)
    if r.returncode:
        return result(1, '\n'.join(pre + [f'branch {b} moved since the test; kept (archive ref {ref})']), lane=name, path=d['path'], branch=b)
    git(top, 'config', '--remove-section', f'branch.{b}')  # as git branch -D does: the description goes with the branch
    git(top, 'worktree', 'prune')
    if d['owner'] == 'host' and d['record_path']:
        with contextlib.suppress(OSError):
            os.unlink(d['record_path'])
    cleared, done = clear_integration_record(ctx, d, into, owner)
    # T-0713: a ticket the integration tree cleared stays byte-identical in main (merging into brings the clear); any
    # other clear in main is committed there when into is another branch, so a land never leaves main dirty
    mpre, mains = porcelain(top), []
    for t in d['tickets']:
        if LOCAL_ID.fullmatch(str(t)):
            if str(t) not in done:
                with contextlib.suppress(tickets.Fail, OSError):
                    if tickets.record_branch(Path(top) / '.sdlc', t, None, only=b):
                        mains.append(str(t))
            git(top, 'update-ref', '-d', READY_REFS + str(t))  # T-0590: the review pin goes with its lane
    if mains and short_branch(into) not in ('', 'HEAD', ctx.main):
        cleared += commit_clear(ctx, top, mpre, mains, d['lane'])
    lines = pre + [outcome] + carried + cleared
    lines += [f'host-owned {p} landed in {b}; remove it yourself: git worktree remove {p}' for p in info.get('hosts', [])]
    pl = port_line(d['port'])
    if pl:
        lines.append(pl)
    if how != 'discarded':
        metas = local_tickets(close_tree(ctx, closer, into)) + local_tickets(top)  # done in either tree counts (T-0769 verifier)
        for t in d['tickets']:
            st = [m.get('status') for _, m in metas if m.get('id') == t]
            if LOCAL_ID.fullmatch(str(t)) and st and not any(x in ('done', 'dropped') for x in st):
                lines.append(f'ticket still open: {t}')
    return result(0, '\n'.join(lines), lane=name, path=d['path'], branch=b, archive=ref, row=how)


def close_tree(ctx, closer, into):
    """T-0769 (#77): the tree `ticket still open` reads ticket status in: the one owning ticket-close (wtroot.owner_tree,
    resolved before the lane tree is removed), since fanout.py land closes the ticket on the integration branch and main
    still reads it open. A lane whose tree is already gone has no record for the helper to read, so closer None takes the
    worktree holding into; no such tree with a .sdlc takes the main checkout."""
    into = short_branch(into)
    wt = closer if closer is not None else next((Path(w['path']) for w in worktrees(ctx.top) if into and w['branch'] == into), None)
    return wt if wt is not None and (wt / '.sdlc').is_dir() else ctx.top


def clear_integration_record(ctx, d, into, owner=None):
    """T-0695: the lane's `branch:` and `worktree:` lines in owner, the tree that owns them (wtroot.owner_tree branch,
    T-0752; T-0680 wrote them there), cleared and committed in that tree. A lane whose tree is gone has no record for
    the helper to read, so owner None takes the worktree holding into. Returns (report lines, ids cleared); none when
    the owner is the main checkout or holds no record."""
    top, b = ctx.top, d['branch']
    into = short_branch(into)
    wt = owner if owner is not None else next((Path(w['path']) for w in worktrees(top) if into and w['branch'] == into), None)
    if wt is None or samepath(str(wt), str(top)) or not (wt / '.sdlc').is_dir():
        return [], []
    pre = porcelain(wt)
    cleared = []
    for t in d['tickets']:
        if LOCAL_ID.fullmatch(str(t)):
            with contextlib.suppress(tickets.Fail, OSError):
                if tickets.record_branch(wt / '.sdlc', t, None, only=b):
                    cleared.append(str(t))
    if not cleared:
        return [], []
    return commit_clear(ctx, wt, pre, cleared, d['lane']), cleared


def short_branch(into):
    into = into or ''
    return into[len('refs/heads/'):] if into.startswith('refs/heads/') else into


def commit_clear(ctx, wt, pre, cleared, lane):
    """Commit the cleared lane record of tickets cleared in tree wt as `<ids>: clear lane record <lane>`, leaving any
    path dirty before (pre) alone. Returns the report line."""
    msg = f'{", ".join(cleared)}: clear lane record {lane}'
    pre_paths = {l[3:].split(' -> ')[-1].strip('"') for l in pre}
    held = {l for l in porcelain(wt) if l[3:].split(' -> ')[-1].strip('"') in pre_paths}
    sha = commit_new(wt, pre | held, msg)
    where = 'main' if samepath(str(wt), str(ctx.top)) else os.path.relpath(os.path.realpath(str(wt)), os.path.realpath(str(ctx.top)))
    if sha:
        return [f'committed in {where}: {sha} {msg}']
    return [f'not committed in {where}: the cleared record is left in the tree; commit it yourself']


def close_lane(target, into=None, discard=False, dry_run=False, cwd='.'):
    ctx = Ctx(cwd)
    lanes = discover(ctx)
    d, refusal = find(ctx, lanes, str(target))
    if refusal:
        return refusal
    row, outcome, rc, info = evaluate(ctx, d, lanes, 'close', discard=discard, into=into)
    if rc:
        return result(rc, outcome, lane=d['lane'], path=d['path'], branch=d['branch'], row=row)
    return do_close(ctx, d, outcome, info, dry_run)


def sweep(apply=False, cwd='.'):
    """([result dict], rc): close every landed plugin lane (apply), or report what would close (dry run)."""
    ctx = Ctx(cwd)
    res, rc = [], 0
    lanes = discover(ctx)
    order = sorted(lanes, key=lambda x: x['kind'] == 'integration')
    for d0 in order:
        host = wtroot.host_owned(d0['path'])  # HOST-OWNED
        if host and d0['exists']:  # T-0564: a tree the host made for itself is never closed, record or not
            res.append(result(0, f"kept {d0['path']}: host-owned ({host})", lane=d0['lane'], path=d0['path'],
                              branch=d0['branch'], row='host-owned'))
            continue
        if not d0['owner'] or not d0['exists']:
            continue
        d = next((x for x in lanes if x['path'] == d0['path']), None)
        if d is None:
            continue
        name = d['lane']
        if ctx.current and samepath(d['path'], ctx.current):
            res.append(result(0, f'kept {name}: current checkout', lane=name, path=d['path'], branch=d['branch']))
            continue
        if d['branch'] and d['branch'] in ctx.cfg['lane_keep']:
            res.append(result(0, f'kept {name}: lane_keep', lane=name, path=d['path'], branch=d['branch']))
            continue
        row, outcome, r, info = evaluate(ctx, d, lanes, 'sweep')
        if r or not info:
            res.append(result(0, f'kept {name}: {outcome}', lane=name, path=d['path'], branch=d['branch'], row=row))
            continue
        mlock = os.path.join(os.path.dirname(d['path']), 'merge.lock')
        if apply and os.path.isfile(mlock):
            with open(mlock, 'a') as mf:  # a fanout lanes dir: close only while no land holds the merge lock
                try:
                    fcntl.flock(mf, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    res.append(result(0, f'kept {name}: merging (merge.lock held)', lane=name, path=d['path'],
                                      branch=d['branch'], row='merging'))
                    continue
                try:
                    x = do_close(ctx, d, outcome, info, dry=False)
                finally:
                    fcntl.flock(mf, fcntl.LOCK_UN)
        else:
            x = do_close(ctx, d, outcome, info, dry=not apply)
        res.append(x)
        if x['rc']:
            rc = 1
        elif apply:
            ctx.refresh()
            lanes = discover(ctx)
    # T-0550: the crash sweep of run folders (<root>/tmp, the scratch dir): a dead owner past lane_min_age_hours goes,
    # a live or recent one stays, an unmarked one is reported and never deleted
    # T-0764: an unmarked folder under another repo's scratch dir is that repo's to name; this repo's get one line
    unmarked = []
    for v, p in wtroot.sweep(ctx.top, hours=ctx.cfg['lane_min_age_hours'], apply=apply):
        if v in ('live', 'recent'):
            continue
        if v == 'unmarked':
            if wtroot.mine(p, ctx.top):  # SWEEP-MINE
                unmarked.append(p)
            continue
        res.append(result(1 if v == 'failed' else 0, wtroot.lines([(v, p)])[0], path=p, row='run folder'))
        rc = 1 if v == 'failed' else rc
    if unmarked:
        line = wtroot.lines([('unmarked', unmarked[0])])[0] if len(unmarked) == 1 \
            else f'unmarked: {len(unmarked)} folders, first {unmarked[0]}'
        res.append(result(0, line, path=unmarked[0], row='run folder'))
    if not apply:
        res.append(result(0, 'dry run; pass --apply to close'))
    return res, rc


# ---- finish (T-0594) --------------------------------------------------------------------------------------

def porcelain(cwd):
    r = git(cwd, 'status', '--porcelain', '--untracked-files=all')
    return set(r.stdout.splitlines()) if r.returncode == 0 else set()


def commit_new(top, pre, msg):
    """Stage the paths whose `git status --porcelain` line is new since pre (as fanout's close commit does) and commit
    them as msg. Returns the commit sha7, '' when nothing changed, or None when git refused."""
    paths = sorted({l[3:].split(' -> ')[-1].strip('"') for l in porcelain(top) - pre})
    if not paths:
        return ''
    r = git(top, 'add', '-A', '--', *paths)
    # T-0595: a tracked path in an ignored directory (the .sdlc/messages/ router files) is staged, and git exits 1 for it
    if r.returncode and 'ignored by one of your .gitignore' not in r.stderr:
        return None
    if git(top, 'commit', '-q', '-m', msg, '--', *paths).returncode:
        return None
    return out(top, 'rev-parse', '--short=7', 'HEAD')


def forward(top, integ, into, ldir):
    """T-0595: merge into into the diverged integ in its worktree, under <ldir>/merge.lock, the generated files resolved
    as a land does (fanout.merge_generated, T-0565), and commit it. Returns None, or why with the merge aborted."""
    import fanout  # same scripts/ dir; local because fanout imports lanes
    wt = next((Path(w['path']) for w in worktrees(top) if w['branch'] == integ), None)
    if wt is None:
        return f'no worktree has {integ} checked out; nothing merged'
    if out(wt, 'status', '--porcelain', '--untracked-files=no'):
        return f'{wt} has uncommitted tracked changes: commit or discard them first; nothing merged'
    sha = out(top, 'rev-parse', f'refs/heads/{into}')
    ldir.mkdir(parents=True, exist_ok=True)
    with fanout.MergeLock(ldir / 'merge.lock'):
        m = fanout.merge_generated(wt, sha, wt / '.sdlc')
        if m in (None, 'up to date'):
            c = git(wt, 'commit', '-q', '-m', f'finish: merge {into} {sha[:7]} into {integ}') if m is None else None
            if c is None or c.returncode == 0:
                return None
            why = f'the merge commit failed: {err(c)}'
        else:
            why = f'{m[0]}: {m[1]}'
        git(wt, 'merge', '--abort')
    return f'merging {into} {sha[:7]} into {integ} in {wt}: {why}; the merge is aborted'


def script_run(argv, cwd):
    """Run a sibling script with no time limit (a land runs the gates) and return the CompletedProcess."""
    return subprocess.run([sys.executable, *argv], cwd=str(cwd), capture_output=True, text=True, stdin=subprocess.DEVNULL)


def script_why(r):
    """The outcome of a fanout.py run that failed: its refusal on stderr, else its last `[<run>] [<lane>] <id> <event>`
    line, else its last output line."""
    errs = [l.strip() for l in (r.stderr or '').splitlines() if l.strip()]
    events = re.findall(r'(?m)^\[fanout-[0-9a-f]+\] \[[^\]]*\] \S+ (.*)$', r.stdout or '')
    if errs and (r.returncode == 2 or not events):
        return errs[-1]
    if events:
        return events[-1]
    lines = [l.strip() for l in (r.stdout or '').splitlines() if l.strip()]
    return lines[-1] if lines else f'exit {r.returncode}'


def finished(top, target):
    """The archive ref of a lane that finish (or any landed close) already removed, else None."""
    for e in archive_entries(top):
        b = e['branch']
        if (b == target or b.endswith('/' + target)) and not b.startswith('finish/') and e['reason'] != 'discarded':
            return e['ref']
    return None


def backup_log(top):
    return Path(top, out(top, 'rev-parse', '--git-common-dir') or '.git', 'sdlc-backup.log').resolve()


def failed_backup(top):
    """(exit code, log path) when the last background push ended nonzero (T-0802), else None: no log, a push still
    running (no `exit` line yet) and `exit 0` are all fine."""
    log = backup_log(top)
    try:
        last = log.read_text().rstrip().rsplit('\n', 1)[-1]
    except OSError:
        return None
    m = re.fullmatch(r'exit (\d+)', last)
    return (int(m.group(1)), log) if m and int(m.group(1)) else None


def push_backup(top, branch, backup, say):
    """The backup step: push refs/heads/<branch> to <remote>/<ref> only when backup names one, in a detached
    background process logging to <git common dir>/sdlc-backup.log (its last line `exit <code>` once the push ends), so
    finish never waits on the push (T-0800).
    Returns 1 when it stopped, else 0."""
    if not backup:
        say('backup: none (no --backup)')
        return 0
    remote, _, ref = backup.partition('/')
    dst = ref if ref.startswith('refs/') else f'refs/heads/{ref}'
    if not (remote and ref):
        say(f'backup: stopped: --backup {backup}: give <remote>/<ref>, as origin/backup-main; fix it, then rerun lanes.py '
            'finish: done steps are skipped')
        return 1
    log = backup_log(top)
    try:
        with open(log, 'w') as f:
            f.write(f'git push -q {remote} refs/heads/{branch}:{dst}\n')
            f.flush()
            # the last log line is `exit <code>` once the push ends
            subprocess.Popen(['sh', '-c', 'git push -q "$0" "$1"; echo "exit $?"', remote, f'refs/heads/{branch}:{dst}'],
                             cwd=str(top), stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        say(f'backup: stopped: {e}; fix it, then rerun lanes.py finish: done steps are skipped')
        return 1
    say(f'backup: pushing {branch} to {remote} {dst} in the background; log {log}')
    return 0


def agent_flags(agent_id, transcript):
    """(dispatch.py record flags, why) for one sub-agent (T-0800): with agent_id, its transcript found under the Claude
    projects folder (dispatch.find_subagent_transcript) unless transcript names it, plus --agent-id, --tool-uses and
    --duration-ms read from it; why is set when no transcript is found."""
    if not agent_id:
        return (['--transcript', transcript] if transcript else []), None
    import dispatch  # same scripts/ dir; local because dispatch imports lanes (and is heavy)
    import cost_estimate
    path = transcript or dispatch.find_subagent_transcript(agent_id)
    if not path:
        return [], f'no transcript agent-{agent_id}.jsonl under the Claude projects folder; pass its path'
    flags = ['--agent-id', agent_id, '--transcript', path]
    tools, ms = cost_estimate.transcript_activity(path) or (None, None)
    flags += ['--tool-uses', str(tools)] if tools is not None else []
    flags += ['--duration-ms', str(ms)] if ms is not None else []
    return flags, None


def finish(target, backup=None, transcript=None, verifier_transcript=None, cwd='.', say=print, solo_agent_id=None,
           verifier_agent_id=None, no_ticket=False):
    """Finish one lane end to end (see the docstring, finish); say prints each step's line. Returns the exit code, 1
    at least when the previous background backup push failed (T-0802): read before this run's own push rewrites the log."""
    prev = failed_backup(Ctx(cwd).top)
    rc = finish_steps(target, backup, transcript, verifier_transcript, cwd, say, solo_agent_id, verifier_agent_id, no_ticket)
    if prev:
        say(f'backup: previous push failed (exit {prev[0]}), see {prev[1]}')
    return rc or (1 if prev else 0)


def finish_steps(target, backup, transcript, verifier_transcript, cwd, say, solo_agent_id, verifier_agent_id, no_ticket=False):
    ctx = Ctx(cwd)
    top = ctx.top
    d, refusal = find(ctx, discover(ctx), str(target))
    if refusal:
        ref = finished(top, str(target))
        if not ref:
            say(refusal['message'])
            return refusal['rc']
        if push_backup(top, ctx.main, backup, say):  # a rerun after the lane step still owes the backup
            return 1
        say(f'finish: {target} is already finished (archive {ref})')
        return 0
    name = d['lane']

    def stop(step, why):
        say(f'{step}: stopped: {why}; fix it, then rerun lanes.py finish {name}: done steps are skipped')
        return 1

    if not d['owner']:
        say(f'not a plugin lane: {d["path"]}')
        return 2
    if not d['exists']:
        return stop('lane', f'no tree at {d["path"]}')
    tree, b, into = Path(d['path']), d['branch'], d['into']
    if ctx.current and samepath(tree, ctx.current):
        return stop('lane', f'run finish from the main checkout {top}, not from the lane it removes')
    if into != ctx.main:
        return stop('lane', f'the lane lands into {into}, not {ctx.main} (the branch of the main checkout {top})')
    ids = [str(t) for t in d['tickets'] if LOCAL_ID.fullmatch(str(t))]
    if no_ticket:
        if ids:
            return stop('lane', f'--no-ticket takes a lane with no local ticket; the record lists {", ".join(ids)}')
        return finish_ticketless(ctx, d, stop, say, backup, verifier_agent_id, verifier_transcript)
    if len(ids) != 1:
        return stop('lane', f'finish takes a lane with one local ticket; the record lists {ids or "none"}')
    tid = ids[0]
    try:
        ltdir = tickets.ticket_dir(tree / '.sdlc')
        slug, meta = next((s, m) for s, m in tickets.load(ltdir) if m.get('id') == tid)
    except (tickets.Fail, StopIteration):
        return stop('lane', f'no ticket {tid} under {tree / ".sdlc"}')
    folder, title = ltdir / slug, str(meta.get('title') or '')
    trel = ltdir.relative_to(tree)

    # 1. record: each pending verifier dispatch, then the solo (dispatch.py record prices its row once, T-0350)
    done = []
    rfolder = owner_root('records', tree).parent / folder.relative_to(tree)  # T-0752: the tree that owns the records
    rdir = order.records_dir(rfolder)
    for df in sorted(rdir.glob('*.dispatch.json')) if rdir.is_dir() else ():
        rec = read_json(df) or {}
        if rec.get('role') == 'verifier':
            att = read_json(rec.get('attempt_file') or '') or {}
            if att.get('status') not in ('running', 'limit-stopped'):
                continue
            aid, extra, why = verifier_agent_id, *agent_flags(verifier_agent_id, verifier_transcript)
        elif rec.get('role') == 'solo':
            aid, extra, why = solo_agent_id, *agent_flags(solo_agent_id, transcript)
        else:
            continue
        if why:
            return stop('record', f'{df.name}: {why}')
        r = script_run([str(HERE / 'dispatch.py'), 'record', *extra, str(df)], tree)
        if r.returncode:
            return stop('record', f'{df.name}: {script_why(r)}')
        done.append(f'{df.name} ({script_why(r)})')
        if aid and rec.get('role') == 'verifier' and rec.get('name'):  # T-0800: it leaves the prune queue (the stop is the factory's TaskStop); land queues the solo
            p = script_run([str(HERE / 'dispatch.py'), 'prune', '--root', top, '--done', rec['name']], top)
            if p.returncode:
                return stop('record', f'prune --done {rec["name"]}: {script_why(p)}')
            done[-1] += f'; pruned {rec["name"]}'
    say('record: ' + ('; '.join(done) or 'nothing pending'))

    # 2. verdict: the newest verifier result of the lane's records dir must pass, before anything is committed or merged
    newest = order.newest(str(rfolder), 'verifier')
    verdict = results.key_value(newest, 'verifier') if newest else None
    if verdict != 'pass':
        return stop('verdict', f'{verdict or "no verifier result"}' + (f' ({os.path.basename(newest)})' if newest else '') +
                    '; nothing merged')
    say(f'verdict: pass ({os.path.basename(newest)})')

    # 3. commit: the lane's uncommitted work as `<id>: <title>`
    if porcelain(tree):
        r = git(tree, 'add', '-A', '--', '.', ':(exclude,glob)**/*.log', ':(exclude,glob)**/.run.lock',
                ':(exclude,glob)**/*.running')
        if r.returncode or git(tree, 'commit', '-q', '-m', f'{tid}: {title}').returncode:
            return stop('commit', err(r) if r.returncode else 'git commit failed')
        say(f'commit: {out(tree, "rev-parse", "--short=7", "HEAD")} {tid}: {title}')
    else:
        say('commit: clean')

    # 4. land: fanout.py land into a per-lane integration branch (the merge, the generated-file handling, the record
    #    carry, the land_gate, the close), skipped when the branch is already in it or in main
    tip = out(top, 'rev-parse', '--verify', f'refs/heads/{b}^{{commit}}')
    if not tip:
        return stop('land', f'no branch {b}')
    integ = f'finish/{name}'
    ldir = ctx.root / 'finish' / name
    gate = ctx.cfg['land_gate']
    if git(top, 'merge-base', '--is-ancestor', tip, f'refs/heads/{into}').returncode == 0:
        say(f'land: skipped ({b} is in {into})')
    elif has_ref(top, f'refs/heads/{integ}') and git(top, 'merge-base', '--is-ancestor', tip, f'refs/heads/{integ}').returncode == 0:
        say(f'land: skipped ({b} is in {integ})')
    else:
        argv = [str(HERE / 'fanout.py'), 'land', b, '--ticket', tid, '--integration', integ, '--lanes-dir', str(ldir),
                '--base', f'refs/heads/{into}', '--rewrite-refs']
        argv += ['--lane', 'solo'] if d['kind'] == 'solo' else []
        argv += ['--gate', gate] if gate else []
        r = script_run(argv, top)
        if r.returncode:
            return stop('land', script_why(r))
        say(f'land: merged {b} into {integ}' + (f' (gate: {gate})' if gate else ' (no land_gate)'))

    # 5. settle: fast-forward main to the integration branch, then close its tree (fanout.py settle)
    if has_ref(top, f'refs/heads/{integ}'):
        # a rerun after into moved past the land: with no gate, settle cannot --forward, so finish merges into first
        if not gate and git(top, 'merge-base', '--is-ancestor', f'refs/heads/{into}', f'refs/heads/{integ}').returncode \
                and git(top, 'merge-base', '--is-ancestor', f'refs/heads/{integ}', f'refs/heads/{into}').returncode:
            why = forward(top, integ, into, ldir)
            if why:
                return stop('settle', why)
        argv = [str(HERE / 'fanout.py'), 'settle', integ] + (['--forward', '--gate', gate] if gate else [])
        r = script_run(argv, top)
        if r.returncode:
            return stop('settle', script_why(r))
        if ldir.is_dir() and not any(under(w['path'], ldir) for w in worktrees(top)):
            shutil.rmtree(str(ldir), ignore_errors=True)
        say(f'settle: {into} at {out(top, "rev-parse", "--short=7", "HEAD")}')
    else:
        say(f'settle: skipped (no {integ})')

    # 6. close: the ticket in main, when the land did not (a merge made by hand, or a land stopped after its merge)
    mtdir = Path(top) / trel
    m = next((m for _, m in tickets.load(mtdir) if m.get('id') == tid), None) if mtdir.is_dir() else None
    if m is not None and m.get('status') in ('done', 'dropped'):
        say(f'close: skipped ({tid} is {m["status"]} in {into})')
    else:
        try:
            carry_records(folder, mtdir / slug)
        except OSError as e:
            return stop('close', f'cannot carry the records of {tid} into {top}: {e}')
        pre = porcelain(top)
        r = script_run([str(HERE / 'tickets.py'), '--root', '.sdlc', 'close', slug, '--rewrite-refs'], top)
        if r.returncode:
            return stop('close', script_why(r))
        sha = commit_new(top, pre, f'close {tid}')
        if sha is None:
            return stop('close', f'{tid} closed but the close commit failed: commit it as `close {tid}`')
        say(f'close: {tid} done' + (f' ({sha} close {tid})' if sha else ''))

    # 7. lane: close_lane (landed by ancestry), then commit what its close wrote in main (the ticket's branch: line)
    pre = porcelain(top)
    r = close_lane(str(tree), cwd=top)
    if r['rc']:
        return stop('lane', r['message'].splitlines()[-1] if r['message'] else f'rc={r["rc"]}')
    sha = commit_new(top, pre, f'{tid}: lane {name} closed')
    if sha is None:
        return stop('lane', f'{name} closed but the commit failed: commit what it changed as `{tid}: lane {name} closed`')
    say('lane: ' + '; '.join(l for l in r['message'].splitlines() if l) + (f' ({sha} {tid}: lane {name} closed)' if sha else ''))

    # 8. backup: only with --backup, the one push, of main as it now stands
    if push_backup(top, into, backup, say):
        return 1
    say(f'finish: {name} done')
    return 0


def transcript_verdict(agent_id, transcript):
    """(verdict, why) of a verifier sub-agent (T-0821): its transcript's final message read as a verifier result, else
    the first existing file that message names; why is set when no transcript or no verdict is found."""
    import dispatch  # same scripts/ dir; local as in agent_flags
    import cost_estimate
    path = transcript or dispatch.find_subagent_transcript(agent_id)
    final = cost_estimate.transcript_final(path) if path else None
    if not final:
        return None, f'no final message in the transcript of agent {agent_id}; pass --verifier-transcript'
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as f:
        f.write(final[0])
    try:
        verdict = results.key_value(f.name, 'verifier')
    finally:
        os.unlink(f.name)
    for tok in re.findall(r'\S+\.md\b', final[0]) if verdict is None else ():
        if os.path.isfile(tok):
            verdict = results.key_value(tok, 'verifier')
            break
    return verdict, None if verdict else f'no verifier verdict in the final message of agent {agent_id}'


def finish_ticketless(ctx, d, stop, say, backup, verifier_agent_id, verifier_transcript):
    """finish --no-ticket (T-0821): a lane with no local ticket (a live session's lane) lands behind the land gate with
    no record, verdict or ticket close. A lane touching a hash_bound: path stops unless --verifier-agent-id names a
    verifier whose verdict is pass. Steps: commit, land (merge into a detached scratch tree at into, run the gate there),
    settle (fast-forward into), lane (close_lane), backup; a rerun skips the done steps."""
    import steps  # same scripts/ dir; local because steps is heavy
    top, tree, b, into, name = ctx.top, Path(d['path']), d['branch'], d['into'], d['lane']
    base = out(top, 'merge-base', f'refs/heads/{into}', f'refs/heads/{b}')
    if not base:
        return stop('lane', f'no merge base of {b} and {into}')
    try:
        hits = steps.declared_hits(str(tree), tickets.hash_bound_globs(Path(top) / '.sdlc'), base, untracked=True)
    except ValueError as e:
        return stop('verdict', f'cannot read the hash_bound paths: {e}')
    if hits:
        if not verifier_agent_id:
            return stop('verdict', f'the lane touches hash_bound paths {", ".join(hits)}; land it with a pass verdict '
                                   f'(--verifier-agent-id ID); nothing merged')
        verdict, why = transcript_verdict(verifier_agent_id, verifier_transcript)
        if verdict != 'pass':
            return stop('verdict', f'{why or verdict} (hash_bound paths {", ".join(hits)}); nothing merged')
        say(f'verdict: pass (agent {verifier_agent_id}, hash_bound paths {", ".join(hits)})')
    else:
        say('verdict: none needed (no ticket, no hash_bound path)')

    if porcelain(tree):
        r = git(tree, 'add', '-A', '--', '.', ':(exclude,glob)**/*.log', ':(exclude,glob)**/.run.lock',
                ':(exclude,glob)**/*.running')
        if r.returncode or git(tree, 'commit', '-q', '-m', f'lane {name}').returncode:
            return stop('commit', err(r) if r.returncode else 'git commit failed')
        say(f'commit: {out(tree, "rev-parse", "--short=7", "HEAD")} lane {name}')
    else:
        say('commit: clean')

    tip = out(top, 'rev-parse', '--verify', f'refs/heads/{b}^{{commit}}')
    gate = ctx.cfg['land_gate']
    if git(top, 'merge-base', '--is-ancestor', tip, f'refs/heads/{into}').returncode == 0:
        say(f'land: skipped ({b} is in {into})')
    else:
        scratch = ctx.root / 'finish' / name
        if scratch.exists():
            git(top, 'worktree', 'remove', '--force', str(scratch))
            shutil.rmtree(str(scratch), ignore_errors=True)
        scratch.parent.mkdir(parents=True, exist_ok=True)
        r = git(top, 'worktree', 'add', '-q', '--detach', str(scratch), f'refs/heads/{into}')
        if r.returncode:
            return stop('land', err(r))

        def drop():
            git(top, 'worktree', 'remove', '--force', str(scratch))
            shutil.rmtree(str(scratch), ignore_errors=True)

        r = git(scratch, 'merge', '--no-ff', '-q', '-m', f'Merge lane {name}', f'refs/heads/{b}')
        if r.returncode:
            drop()
            return stop('land', f'merging {b} into {into} failed: {err(r)}')
        if gate:
            cmd = ['bash', '-c', gate]
            try:
                slots = int(os.environ.get('SDLC_GATE_SLOTS') or 1)
            except ValueError:
                slots = 1
            if slots >= 1:
                cmd = [sys.executable, str(HERE / 'gate_lock.py'), 'run', '--nice', '--'] + cmd
            g = subprocess.run(cmd, cwd=str(scratch), capture_output=True, text=True)
            if g.returncode:
                drop()
                tail = (g.stdout + g.stderr).strip().splitlines()[-1:] or ['']
                return stop('land', f'land gate red (exit {g.returncode}): {tail[0]}; nothing merged')
        merged = out(scratch, 'rev-parse', 'HEAD')
        drop()
        r = git(top, 'merge', '--ff-only', '-q', merged)
        if r.returncode:
            return stop('settle', f'{into} cannot fast-forward to the gated merge {merged[:7]}: {err(r)}')
        say(f'land: merged {b} into {into}' + (f' (gate: {gate})' if gate else ' (no land_gate)'))
        say(f'settle: {into} at {out(top, "rev-parse", "--short=7", "HEAD")}')

    pre = porcelain(top)
    r = close_lane(str(tree), cwd=top)
    if r['rc']:
        return stop('lane', r['message'].splitlines()[-1] if r['message'] else f'rc={r["rc"]}')
    sha = commit_new(top, pre, f'lane {name} closed')
    if sha is None:
        return stop('lane', f'{name} closed but the commit failed: commit what it changed as `lane {name} closed`')
    say('lane: ' + '; '.join(l for l in r['message'].splitlines() if l) + (f' ({sha} lane {name} closed)' if sha else ''))
    if push_backup(top, into, backup, say):
        return 1
    say(f'finish: {name} done')
    return 0


# ---- open -------------------------------------------------------------------------------------------------

def claim(rootp, tid):
    """('local', title) | ('external', directive) | ('refuse', message) by the 8.1 claim rule."""
    if LOCAL_ID.fullmatch(tid) and rootp.is_dir():
        try:
            metas = tickets.load(tickets.ticket_dir(rootp))
        except tickets.Fail as e:
            return 'refuse', str(e)
        for _, meta in metas:
            if meta.get('id') == tid:
                cb = meta.get('claimed_by')
                if not (' '.join(cb) if isinstance(cb, list) else str(cb or '')).strip():
                    return 'refuse', f'ticket {tid} not claimed: set claimed_by: first'
                return 'local', str(meta.get('title') or '')
        return 'refuse', f'no ticket {tid}'
    return 'external', f'claim {tid} in its tracker (assignee) before work; not checked here'


def pr_upstream(ctx):
    """The upstream main tracks when the repo lands through it (T-0609, a PR repo), else None: no upstream, or a
    `lane_landing: local` config line (T-0804: finish lands into main locally, so open commits there)."""
    if ctx.cfg['lane_landing'] == 'local':
        return None
    return out(ctx.top, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', f'{ctx.main}@{{upstream}}')


def claim_tickets(ids, root='.sdlc', by=None, cwd='.'):
    """T-0800: open --claim: tickets.py claim each local ticket id in the main checkout and commit what the claims
    changed there as `claim <ids>`; a ticket already claimed keeps its holder. Not committed when main tracks an upstream
    (T-0609) and no `lane_landing: local` line says the repo lands locally (T-0804). Returns result(rc, message)."""
    ctx = Ctx(cwd)
    top, rootp, lines, done = ctx.top, Path(ctx.top, root), [], []
    pre = porcelain(top)
    for t in ids:
        if not LOCAL_ID.fullmatch(t):
            continue
        if claim(rootp, t)[0] == 'local':
            lines.append(f'claim: {t} already claimed')
            continue
        r = script_run([str(HERE / 'tickets.py'), '--root', root, 'claim', t] + (['--by', by] if by else []), top)
        if r.returncode:
            return result(1, '\n'.join(lines + [f'claim: stopped: {t}: {script_why(r)}; no lane opened']))
        done.append(t)
        lines.append(f'claim: {t} claimed')
    if done:
        msg = 'claim ' + ' '.join(done)
        upstream = pr_upstream(ctx)
        sha = None if upstream else commit_new(top, pre, msg)
        lines.append(f'claim: committed {sha} {msg}' if sha else
                     f'claim: not committed: {ctx.main} tracks {upstream}' if upstream else f'claim: not committed: commit it as `{msg}`')
    return result(0, '\n'.join(lines))


def name_refusal(ctx, branch, tree):
    top = ctx.top
    if git(top, 'check-ref-format', '--branch', branch).returncode:
        return f'not a valid branch name: {branch}'
    full = 'refs/heads/' + branch
    for r in (out(top, 'for-each-ref', '--format=%(refname)', 'refs/heads') or '').splitlines():
        if r == full:
            return f'branch {branch} exists'
        if full.startswith(r + '/'):
            return f'branch {branch} clashes with {r}: rename the flat branch {r[len("refs/heads/"):]} first'
        if r.startswith(full + '/'):
            return f'branch {branch} clashes with {r}: a flat {branch} cannot sit beside it; pick another name'
    if (tree / 'merge.lock').exists():
        return f'{tree} is a lanes dir'
    if tree.exists():
        return f'tree {tree} exists'
    return None


def pick_port(ctx, lanes):
    lo, hi = ctx.cfg['lane_ports']
    held = {int(d['port']) for d in lanes if d['owner'] and isinstance(d['port'], int)}
    for p in range(lo, hi + 1):
        if p not in held and port_free(p):
            return p
    return None


def add_exclude(common, entry=RECORD):
    path = Path(common) / 'info' / 'exclude'
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding='utf-8') if path.is_file() else ''
    if not any(l.strip() in (entry, '/' + entry) for l in text.splitlines()):
        path.write_text(text + ('' if not text or text.endswith('\n') else '\n') + entry + '\n', encoding='utf-8')


def write_record(tree, rec):
    (Path(tree) / RECORD).write_text(json.dumps({k: rec.get(k) for k in FIELDS}) + '\n', encoding='utf-8')


def ticket_title(rootp, tid):
    """The title of local ticket tid under rootp, or '' when it is not readable."""
    try:
        metas = tickets.load(tickets.ticket_dir(rootp))
    except (tickets.Fail, OSError):
        return ''
    return next((str(m.get('title') or '') for _, m in metas if m.get('id') == tid), '')


def lock_reason(rootp, ids):
    """`<holder> <ids>`: the holder is refs/sdlc/claims/<first local id> (T-0588), else that ticket's claimed_by:, with
    the trailing date dropped; else tickets.claim_by from the environment (<host>:<session>); else unknown."""
    holder = ''
    tid = next((t for t in ids if LOCAL_ID.fullmatch(t)), None)
    if tid:
        g = TICKETS.ref_git(rootp)
        holder = (TICKETS.ref_read(g, TICKETS.CLAIM_REFS + tid)[1] or '') if g else ''
        if not holder.strip() and rootp.is_dir():
            try:
                cb = next((m.get('claimed_by') for _, m in TICKETS.load(TICKETS.ticket_dir(rootp)) if m.get('id') == tid), '')
            except (TICKETS.Fail, OSError):
                cb = ''
            holder = ' '.join(cb) if isinstance(cb, list) else str(cb or '')
    holder = re.sub(r'\s+\d{4}-\d{2}-\d{2}$', '', ' '.join(holder.split())) or TICKETS.claim_by('', os.environ) or 'unknown'
    return ' '.join([holder] + list(ids))


def record_tree(ctx, tree, root, ids):
    """T-0680: (tree, note) for the lane record: the tree that owns the branch: line of lane tree (wtroot.owner_tree,
    T-0752: the worktree holding its into branch) when it is not the main checkout and its root holds every local
    ticket in ids, else the main checkout with note saying why (None when no other tree owns it)."""
    wt = wtroot.owner_tree('branch', None, tree)
    if wt is None or os.path.realpath(str(wt)) == os.path.realpath(str(ctx.top)):
        return ctx.top, None
    rel = os.path.relpath(os.path.realpath(str(wt)), os.path.realpath(str(ctx.top)))
    want = [t for t in ids if LOCAL_ID.fullmatch(t)]
    try:
        have = {m.get('id') for _, m in TICKETS.load(TICKETS.ticket_dir(wt / root))} if (wt / root).is_dir() else set()
    except TICKETS.Fail:
        have = set()
    missing = [t for t in want if t not in have]
    if missing:
        return ctx.top, f'recorded in the main checkout: {", ".join(missing)} not in {rel}/{root}'
    return wt, None


def integration_lock(top, tree):
    """T-0725: the fanout.MergeLock a land holds over the integration branch checked out in tree: <tree parent>/merge.lock
    for a fanout integration tree, else the default lanes dir's (fanout.resolve_lanes_dir); a null context where land
    refuses that dir."""
    import fanout  # same scripts/ dir; local because fanout imports lanes
    ldir = Path(tree).parent
    if not (ldir / 'merge.lock').is_file():
        top = Path(top).resolve()
        try:
            ldir = fanout.resolve_lanes_dir(argparse.Namespace(lanes_dir=None), top, top)
        except fanout.Refuse:
            return contextlib.nullcontext()
    ldir.mkdir(parents=True, exist_ok=True)
    return fanout.MergeLock(ldir / 'merge.lock')


def merge_tickets(single, csv):
    """T-0691: --ticket ids then the ids of each --tickets T-1,T-2, in order, duplicates dropped."""
    out = []
    for t in list(single or ()) + [x.strip() for c in (csv or ()) for x in c.split(',')]:  # TICKETS-CSV
        if t and t not in out:
            out.append(t)
    return out


def open_lane(name, base=None, into=None, tickets=(), kind='fanout', title=None, root='.sdlc', dry_run=False, cwd='.', *,
              path=None, branch=None, check_claim=True, record_branch=False, lock=False):
    ctx = Ctx(cwd)
    top = ctx.top
    ids = list(tickets or ())
    lines = []
    if kind not in KINDS:
        return result(2, f'unknown kind {kind}: use fanout, integration or solo')
    if kind in ('fanout', 'solo') and not ids:
        return result(1, f'kind {kind} needs --ticket: no ticket, no lane')
    refused = plugin_min.refusal(top)  # T-0593: before any claim, branch or tree
    if refused:
        return result(2, refused)
    explicit_root = root is not None  # T-0680: the CLI passes None when --root was not given
    root = root or '.sdlc'
    rootp = Path(cwd, root)
    titles = {}
    for t in ids:
        if not check_claim and LOCAL_ID.fullmatch(t) and rootp.is_dir():
            titles[t] = ticket_title(rootp, t)
            continue
        st, msg = claim(rootp, t)
        if st == 'refuse':
            return result(1, msg)
        if st == 'external':
            lines.append(msg)
        else:
            titles[t] = msg
    if kind == 'integration':
        b0, leaf = name, slug(name)
    else:
        leaf = f'{ids[0].lstrip("#")}-{slug(name)}'
        b0 = f'lane/{leaf}'
    branch = branch or b0
    if path:
        tree = Path(os.path.abspath(os.path.join(ctx.cwd, str(path))))
        leaf = tree.name
    else:
        tree = ctx.root / leaf
    refusal = name_refusal(ctx, branch, tree)  # NAME-FIRST
    if refusal:
        return result(1, '\n'.join(lines + [refusal]), lane=leaf, path=tree, branch=branch)
    base_ref = base or ctx.main
    base_sha = out(top, 'rev-parse', '--verify', '-q', base_ref + '^{commit}')
    if not base_sha:
        return result(1, '\n'.join(lines + [f'cannot resolve base {base_ref}']), lane=leaf, path=tree, branch=branch)
    into_ = into or (base if kind == 'fanout' and base else None) or ctx.cfg['lane_into'] or ctx.main
    tid = ids[0] if ids else ''
    ttl = titles.get(tid) or title or ''
    desc = ' '.join(x for x in (tid, ttl) if x)[:120]
    if dry_run:
        return result(0, '\n'.join(lines + [f'would open {leaf} at {tree} on {branch} from {base_ref} into {into_}']),
                      lane=leaf, path=tree, branch=branch)
    rec = dict(lane=leaf, kind=kind, branch=branch, base=base_ref, base_sha=base_sha, into=into_, tickets=ids, port=None,
               opened=utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), run_id=os.environ.get('SDLC_RUN_ID') or None, setup=None)
    ctx.root.mkdir(parents=True, exist_ok=True)
    with flock(ctx.root / 'lanes.lock'):
        if ctx.cfg['lane_ports']:
            rec['port'] = pick_port(ctx, discover(ctx))
            if rec['port'] is None:
                lo, hi = ctx.cfg['lane_ports']
                return result(1, '\n'.join(lines + [f'no free port in lane_ports {lo}-{hi}']), lane=leaf, path=tree, branch=branch)
        r = git(top, 'worktree', 'add', '-q', '-b', branch, str(tree), base_sha)
        if r.returncode:
            return result(1, '\n'.join(lines + [f'git worktree add failed: {err(r)}']), lane=leaf, path=tree, branch=branch)
        if lock and kind != 'integration':  # T-0589: a locked tree is a running lane; list and sweep read its owner
            reason = lock_reason(rootp, ids)
            r = git(top, 'worktree', 'lock', '--reason', reason, str(tree))
            if r.returncode:
                lock_line = f'not locked: {err(r)}'
            else:
                rec['lock'], lock_line = reason, f'locked: {reason}'
        write_record(tree, rec)
    add_exclude(ctx.common)
    add_exclude(ctx.common, NODE_MODULES)
    if git(top, 'check-ignore', '-q', LOCAL_SETTINGS).returncode:  # T-0724: host-personal, so a lane's `git add -A` never stages it
        add_exclude(ctx.common, LOCAL_SETTINGS)
    local = Path(top, '.claude', 'settings.local.json')  # gitignored, so a new worktree lacks it; copy only this file, never log it
    if local.is_file() and not Path(tree, '.claude', 'settings.local.json').exists():
        try:
            Path(tree, '.claude').mkdir(exist_ok=True)
            shutil.copy2(str(local), str(Path(tree, '.claude', 'settings.local.json')))
        except OSError as e:
            lines.append(f'settings.local.json not copied: {e.strerror or "error"}')
    if Path(top, '.codex', 'agents', '.sdlc-managed.json').is_file():  # T-0598: the generated agents are git-ignored, so a new tree lacks them
        r = subprocess.run([sys.executable, str(HERE / 'codex_roles.py'), 'install', str(tree)], capture_output=True, text=True)
        if r.returncode:
            lines.append(f'.codex/agents not installed: {(r.stderr or r.stdout).strip()}')
    if desc:
        git(top, 'config', f'branch.{branch}.description', desc)
    lines.append(f'opened {leaf} at {tree} (branch {branch}, into {into_})')
    if lock and kind != 'integration':
        lines.append(lock_line)
    # T-0609: a main tracking an upstream lands through it (a PR repo), so a record commit there would diverge from origin;
    # a `lane_landing: local` line says finish lands into main locally, so the record commits there (T-0804)
    upstream = pr_upstream(ctx)
    if upstream and record_branch and rootp.is_dir() and any(LOCAL_ID.fullmatch(t) for t in ids):
        lines.append(f'not recorded: {ctx.main} tracks {upstream}, so open writes no branch: or worktree: line in main')
        record_branch = False
    rtop, rrootp = top, rootp  # T-0680: an --into checked out in an integration tree takes the record there
    if record_branch and not explicit_root and rootp.is_dir() and any(LOCAL_ID.fullmatch(t) for t in ids):
        rtop, note = record_tree(ctx, tree, root, ids)
        rrootp = rtop / root if rtop != top else rootp
        if note:
            lines.append(note)
    with integration_lock(top, rtop) if rtop != top else contextlib.nullcontext():  # T-0725: never under a land
        pre = porcelain(rtop)
        written, handoffs = [], []
        for t in ids if record_branch and rrootp.is_dir() else ():
            if LOCAL_ID.fullmatch(t):
                try:
                    # relative to the main checkout: inside it, or under the sibling root (../<name>.worktrees/..., T-0563)
                    rel = os.path.relpath(os.path.realpath(str(tree)), os.path.realpath(str(top)))
                    if rel.startswith('..') and not plain_under(os.path.realpath(str(tree)), os.path.realpath(str(wtroot.default_root(top)))):
                        rel = None
                    slug_ = TICKETS.record_branch(rrootp, t, branch, worktree=rel)
                    if slug_:
                        written.append(t)
                        handoffs.append(os.path.relpath(os.path.realpath(str(TICKETS.layout_paths(rrootp).tickets / slug_ / 'handoff.md')),
                                                        os.path.realpath(str(rtop))))
                        lines.append(f'ticket {t}: branch: {branch}')
                        if rel:
                            lines.append(f'ticket {t}: worktree: {rel}')
                except (TICKETS.Fail, OSError) as e:
                    lines.append(f'ticket {t}: branch: not written: {e}')
        if written:  # T-0599: commit what the writes changed, or main stays dirty and a fast-forward settle refuses
            msg = f'{", ".join(written)}: record lane {leaf}'
            # compared by path: a staged edit turns `M ` into `MM`, a line commit_new would count as new
            pre_paths = {l[3:].split(' -> ')[-1].strip('"') for l in pre}
            held = {l for l in porcelain(rtop) if l[3:].split(' -> ')[-1].strip('"') in pre_paths}
            sha = commit_new(rtop, pre | held, msg)
            where = 'main' if rtop == top else os.path.relpath(os.path.realpath(str(rtop)), os.path.realpath(str(top)))
            if sha:
                lines.append(f'committed: {sha} {msg}')
                if rtop != top:
                    lines.append(f'recorded in {where}')
            elif sha is None:
                lines.append(f'not committed: commit the ticket changes in {where} as `{msg}`')
            for h in handoffs:
                if h in pre_paths:
                    lines.append(f'not committed: {h} (dirty before open); commit it yourself')
    if rec['port']:
        lines.append(f'port {rec["port"]}')
    if not ctx.cfg['lane_setup'] and Path(top, 'package.json').is_file():  # T-0773: a new tree has no node_modules
        lines.append('note: package.json but no lane_setup: in .sdlc/config; the new tree has no node_modules '
                     '(set lane_setup: to an install command; a node_modules symlink is no fix)')
    if ctx.cfg['lane_setup']:
        rec['setup'] = 'ok'
        for cmd in ctx.cfg['lane_setup']:  # T-0692: in order, the first failure stops the rest
            try:
                rc = subprocess.run(cmd, shell=True, cwd=str(tree)).returncode
            except OSError:
                rc = 127
            if rc:
                rec['setup'] = f'failed rc={rc} ({cmd})'
                break
        write_record(tree, rec)
        lines.append(f'setup: {rec["setup"]}')
    return result(0, '\n'.join(lines), lane=leaf, path=tree, branch=branch, port=rec['port'])


def host_record(name, branch, into, tickets, base=None, cwd='.'):
    """Write <lanes root>/host/<name>.lane.json (kind host, every FIELDS key), overwriting one of that name; return it."""
    ctx = Ctx(cwd)
    base_ref = base or ctx.main
    ids = [tickets] if isinstance(tickets, str) else list(tickets or ())
    rec = dict(lane=name, kind='host', branch=branch, base=base_ref,
               base_sha=out(ctx.top, 'rev-parse', '--verify', '-q', base_ref + '^{commit}'), into=into, tickets=ids,
               port=None, opened=utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), run_id=os.environ.get('SDLC_RUN_ID') or None,
               setup=None)
    hp = ctx.root / 'host' / f'{name}.lane.json'
    hp.parent.mkdir(parents=True, exist_ok=True)
    with flock(ctx.root / 'lanes.lock'):
        if ctx.cfg['lane_ports']:
            rec['port'] = pick_port(ctx, [d for d in discover(ctx) if not samepath(d['record_path'] or '', hp)])
        rec = {k: rec.get(k) for k in FIELDS}
        hp.write_text(json.dumps(rec) + '\n', encoding='utf-8')
    return rec


# ---- ready (T-0590) ---------------------------------------------------------------------------------------

def snapshot(path):
    """(HEAD sha, tree sha) of the tree at path as it stands: tracked and untracked files git does not ignore, minus logs
    and lock files, written through a copy of the index so the real index and the stash stack stay untouched. path may be
    any directory in the tree: the whole tree is read."""
    path = out(path, 'rev-parse', '--show-toplevel') or path
    head = out(path, 'rev-parse', '--verify', '-q', 'HEAD')
    idx = out(path, 'rev-parse', '--path-format=absolute', '--git-path', 'index')
    if not head or not idx:
        raise LaneError(f'cannot read HEAD or the index of {path}')
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, 'index')
        if os.path.isfile(idx):
            shutil.copy2(idx, tmp)
        env = dict(os.environ, GIT_INDEX_FILE=tmp)
        r = subprocess.run(['git', 'add', '-A', '--', '.', *SNAPSHOT_SKIP], cwd=str(path), capture_output=True, text=True, env=env)
        w = subprocess.run(['git', 'write-tree'], cwd=str(path), capture_output=True, text=True, env=env) if r.returncode == 0 else r
    if w.returncode:
        raise LaneError(f'cannot snapshot {path}: {err(w)}')
    return head, w.stdout.strip()


def ready_state(top, sha):
    """(head, tree) a ready sha pins: a snapshot commit pins its parent and its tree, any other commit itself."""
    subject = out(top, 'log', '-1', '--format=%s', sha) or ''
    head = out(top, 'rev-parse', '--verify', '-q', f'{sha}^1') if subject.startswith(SNAPSHOT_SUBJECT) else sha
    return head, out(top, 'rev-parse', '--verify', '-q', f'{sha}^{{tree}}')


def has_criteria(handoff):
    """True when the handoff lists at least one item under ## Acceptance criteria."""
    try:
        text = Path(handoff).read_text(encoding='utf-8')
    except OSError:
        return False
    inside = False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.rstrip() == '## Acceptance criteria'
        elif inside and re.match(r'\s*(?:[-*]|\d+[.)])\s+\S', line):
            return True
    return False


def pin(path, tid, name, base, state=None):
    """(sha, line or None): the commit that pins the tree at path, HEAD when its state equals HEAD, else a snapshot
    commit on HEAD (git commit-tree, nothing in the tree or index changes) whose message carries `Lane-Base: <base>`,
    which dispatch.py prepare verifier reads as Base sha. state is a snapshot(path) already taken."""
    head, tree = state or snapshot(path)
    if out(path, 'rev-parse', '--verify', '-q', 'HEAD^{tree}') == tree:
        return head, None
    msg = f'{SNAPSHOT_SUBJECT} {tid} in {name}\n\nUncommitted work at HEAD {head}.\n' + (f'\nLane-Base: {base}\n' if base else '')
    r = git(path, 'commit-tree', tree, '-p', head, '-m', msg)
    if r.returncode:
        raise LaneError(f'cannot write the snapshot commit: {err(r)}')
    sha = r.stdout.strip()
    return sha, f'snapshot: {sha[:12]} holds the uncommitted work on HEAD {head[:12]}'


def warned_before(ctx):
    """True when this session already saw the missing-mailbox warning; else records it. The session is
    CLAUDE_CODE_SESSION_ID when set, else the parent pid; the marker lives under the git common dir (T-0694)."""
    key = re.sub(r'[^A-Za-z0-9_.-]+', '-', os.environ.get('CLAUDE_CODE_SESSION_ID') or f'ppid-{os.getppid()}')
    marker = ctx.common / 'sdlc' / 'ready-warned' / key
    if marker.exists():
        return True
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(f'{utcnow().isoformat()}\n')
    except OSError:
        pass
    return False


def notify(cmd, cwd, tid, sha, path):
    """Run cmd through the shell in the main checkout with SDLC_READY_TICKET, SDLC_READY_SHA and SDLC_READY_PATH set;
    the lines to print (T-0694)."""
    env = dict(os.environ, SDLC_READY_TICKET=tid, SDLC_READY_SHA=sha, SDLC_READY_PATH=str(path))
    try:
        r = subprocess.run(cmd, shell=True, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return [f'warning: --notify-cmd did not run: {e}']
    lines = [f'notified: {cmd} rc={r.returncode}']
    if r.returncode:
        lines.append(f'warning: --notify-cmd exited {r.returncode}: {err(r)}')
    return lines


def ready(target=None, ticket=None, cwd='.', notify_cmd=None):
    """Pin refs/sdlc/ready/<ticket> at the lane's state, unlock the lane's own lock, and send the factory a ready
    message (see Ready in the docstring); notify_cmd runs after the pin. Returns a result dict."""
    ctx = Ctx(cwd)
    lanes = discover(ctx)
    if target is None:
        d = next((x for x in lanes if ctx.current and samepath(x['path'], ctx.current)), None)
        if d is None:
            return result(1, f'not in a lane: {ctx.cwd}; name the lane')
    else:
        d, refusal = find(ctx, lanes, str(target))
        if refusal:
            return refusal
    name, path = d['lane'], d['path']
    if not d['owner'] or not d['exists']:
        return result(1, f'not a plugin lane with a tree: {path}', lane=name, path=path, branch=d['branch'])
    tid = ticket or next((t for t in d['tickets'] if LOCAL_ID.fullmatch(str(t))), None)
    if not tid:
        return result(1, f'{name} has no local ticket: name it with --ticket', lane=name, path=path, branch=d['branch'])
    hits = ticket_handoffs(ctx, path, tid)
    if not any(has_criteria(h) for h in hits):
        where = hits[0] if hits else f'the {tid} handoff'
        return result(1, f'{tid} has no acceptance criteria: add them to {where} first', lane=name, path=path, branch=d['branch'])
    head, tree = snapshot(path)
    base = d['base_sha'] or out(path, 'merge-base', 'HEAD', d['into'] or ctx.main)
    if base and out(path, 'rev-parse', '--verify', '-q', f'{base}^{{tree}}') == tree:
        return result(1, f'no changes in {name} since {base[:12]}: nothing to review', lane=name, path=path, branch=d['branch'])
    try:
        sha, line = pin(path, tid, name, base, (head, tree))
    except LaneError as e:
        return result(1, str(e), lane=name, path=path, branch=d['branch'])
    lines = [line] if line else []
    ref = READY_REFS + tid
    r = git(path, 'update-ref', ref, sha)
    if r.returncode:
        return result(1, '\n'.join(lines + [f'cannot write {ref}: {err(r)}']), lane=name, path=path, branch=d['branch'])
    lines.append(f'ready: {ref} {sha}')
    if d['locked'] is not None and d['lock'] and d['locked'] == d['lock']:  # the lane's own lock, as close clears it
        r = git(ctx.top, 'worktree', 'unlock', path)
        lines.append(f'unlocked: {d["lock"]}' if r.returncode == 0 else f'not unlocked: {err(r)}')
    elif d['locked'] is not None:
        lines.append(f'still locked: {d["locked"] or "no reason"} (not the lock open set)')
    if notify_cmd:
        lines += notify(notify_cmd, ctx.top, tid, sha, path)
    receiver = ctx.cfg['factory'] or 'factory'
    sender = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:40].rstrip('-') or 'lane'
    body = f'{sha} {path}\nticket {tid}, lane {name}, branch {d["branch"] or "none"}: review this sha; lanes.py list --ready flags it stale once the lane moves'
    # beside tickets.py, the scripts dir this module imports from (a selftest mutant runs from a copy elsewhere)
    r = run([sys.executable, str(Path(tickets.__file__).resolve().parent / 'messages.py'), 'send', '--receiver', receiver, '--sender', sender, '--kind', 'handoff',
             '--topic', f'ready {tid}', '--follow-up', 'false', body], ctx.top)
    if r is not None and r.returncode and f'receiver {receiver} is not registered' in err(r):
        # the ref is pinned and the lane unlocked, so a missing mailbox is a warning, not a failure (T-0610); full
        # once per session, one short line after, none with --notify-cmd (T-0694)
        if notify_cmd:
            pass
        elif warned_before(ctx):
            lines.append(f'not sent: no {receiver} mailbox (warned once)')
        else:
            lines.append(f'warning: not sent to {receiver}: no {receiver} mailbox is registered; the ready ref is pinned, '
                         f'`lanes.py list --ready` shows it; to mail it, run `messages.py register --name {receiver} --harness claude|codex|human`')
        return result(0, '\n'.join(lines), lane=name, path=path, branch=d['branch'], sha=sha, ref=ref)
    if r is None or r.returncode:
        lines.append(f'not sent to {receiver}: {err(r) if r is not None else "messages.py did not run"}; tell the factory yourself')
        return result(1, '\n'.join(lines), lane=name, path=path, branch=d['branch'], sha=sha, ref=ref)
    lines.append(f'sent: ready {tid} to {receiver} ({r.stdout.strip()})')
    return result(0, '\n'.join(lines), lane=name, path=path, branch=d['branch'], sha=sha, ref=ref)


def ticket_handoffs(ctx, path, tid):
    """The handoff paths of local ticket tid, in the lane tree first, then the main checkout."""
    res = []
    for top in (path, ctx.top):
        rootp = Path(top) / '.sdlc'
        res += [tickets.ticket_dir(rootp) / s / 'handoff.md' for s, m in local_tickets(top) if m.get('id') == tid]
    return res


def ready_rows(cwd='.'):
    """One row per refs/sdlc/ready/<ticket>: ticket, lane, path, sha, and stale when the lane's HEAD or tree is no longer
    the pinned state (a lane that is gone is stale too)."""
    ctx = Ctx(cwd)
    lanes = discover(ctx)
    rows = []
    for line in (out(ctx.top, 'for-each-ref', '--format=%(refname) %(objectname)', READY_REFS) or '').splitlines():
        ref, sha = line.split()
        tid = ref[len(READY_REFS):]
        d = next((x for x in lanes if x['owner'] and x['exists'] and tid in x['tickets']), None)
        stale = True
        if d is not None:
            try:
                stale = snapshot(d['path']) != ready_state(ctx.top, sha)  # READY-STALE
            except LaneError:
                stale = True
        rows.append(dict(ticket=tid, lane=d['lane'] if d else None, path=d['path'] if d else None, sha=sha, ref=ref, stale=stale))
    return rows


# ---- list, still_open, check, port, archive ---------------------------------------------------------------

def lane_states(ctx, d):
    if not d['owner']:
        states = ['manual']
    else:
        primary = 'open'
        b = d['branch']
        if b and has_ref(ctx.top, f'refs/heads/{b}'):
            ref, _ = resolve_into(ctx, d['into'] or ctx.main, fetch=False)
            how = landed(ctx.top, f'refs/heads/{b}', ref, branch=b)[0] if ref else 'cannot decide'
            if how in ('ancestor', 'pr merged', 'content'):
                primary = 'closable'
            elif how == 'not landed':
                age = tip_age(ctx.top, f'refs/heads/{b}')
                if age is not None and age > ctx.cfg['lane_stale_days'] * 86400 and \
                        not gh_json(ctx.top, ['pr', 'list', '--state', 'open', '--head', b, '--json', 'number']):
                    primary = 'stale'
        states = [primary]
    if d['locked'] is not None:
        if states in (['open'], ['closable']):  # T-0589: a locked lane is running, never closable
            states = [f'running ({d["locked"] or "no reason"})']
        else:
            states.append('locked')
    if d['owner'] and d['branch'] and not d['branch'].startswith(NAMESPACES):
        states.append('legacy')
    return states


def ticket_verdict(top, metas, d):
    """(ticket id, verdict) for lane d: the local ticket whose `branch:` is the lane branch, else the record's first
    local ticket; verdict is the newest verifier result's (pass, fail, inherited) in its folder in the tree that owns
    the records (the lane while it exists, T-0752), else None."""
    b = d['branch']
    hit = next((m for _, m in metas if b and isinstance(m.get('branch'), str) and m['branch'].strip() == b), None)
    if hit is None:
        hit = next((m for t in d['tickets'] for _, m in metas if m.get('id') == t), None)
    if hit is None:
        return None, None
    slug = next(s for s, m in metas if m is hit)
    try:
        rootp = Path(wtroot.owner_tree('records', hit.get('id'), top) or top) / '.sdlc'  # T-0752
        newest = order.newest(str(tickets.ticket_dir(rootp) / slug), 'verifier')
    except (OSError, tickets.Fail):
        newest = None
    return hit.get('id'), (results.key_value(newest, 'verifier') if newest else None)


def list_lanes(all_=False, stale=False, cwd='.'):
    ctx = Ctx(cwd)
    rows = []
    metas = local_tickets(ctx.top)
    for d in discover(ctx):
        if not d['owner'] and not all_:
            continue
        st = lane_states(ctx, d)
        if stale and not ({'closable', 'stale'} & set(st)):
            continue
        desc = (out(ctx.top, 'config', '--get', f'branch.{d["branch"]}.description') or '') if d['branch'] else ''
        tid, verdict = ticket_verdict(ctx.top, metas, d)
        rows.append(dict(lane=d['lane'], path=d['path'], branch=d['branch'], kind=d['kind'], owner=d['owner'] or 'manual',
                         state=', '.join(st), states=st, description=desc, into=d['into'], tickets=d['tickets'],
                         port=d['port'], locked=d['locked'], exists=d['exists'], ticket=tid, verdict=verdict))
    return rows


def who(cwd='.'):
    """T-0821: the evidence of an active factory session in this repo, as dicts {session, evidence}, [] for none:
    a receiver in the main checkout's .sdlc/messages/receivers.json of harness claude whose name or reader names a
    factory and whose last_seen is within its expiry; a *.running marker under a .sdlc/runtime/tasks/ of the main
    checkout or a lane whose task dir a live process names (in_use); an open fanout or solo plugin lane other than the
    tree this runs in (a live session's own lane never counts as a factory)."""
    import messages  # same scripts/ dir; local because only who reads the mailbox
    ctx = Ctx(cwd)
    hits = []
    try:
        reg = messages.load_registry(os.path.join(ctx.top, '.sdlc', 'messages'))
    except messages.Refuse as e:
        reg = {}
        hits.append(dict(session='unknown', evidence=f'unreadable receivers registry: {e}'))
    now = utcnow()
    for name, e in sorted(reg.items()):
        if e['harness'] != 'claude' or e['reader'] == messages.NO_READER or 'factory' not in f'{name} {e["reader"]}':
            continue
        if (now - messages.parse_ts(e['last_seen'])).total_seconds() > messages.ttl_seconds(e['expiry']):
            continue
        hits.append(dict(session=name, evidence=f'receiver reader {e["reader"]} last seen {e["last_seen"]}'))
    lanes = discover(ctx)
    for tree in [ctx.top] + [d['path'] for d in lanes if d['exists']]:
        for m in sorted(Path(tree, '.sdlc', 'runtime', 'tasks').glob('*/*.running')):
            pid = in_use(m.parent)
            if pid:
                hits.append(dict(session=f'pid {pid}', evidence=f'running {m}'))
    for d in lanes:
        if d['owner'] and d['exists'] and d['kind'] in ('fanout', 'solo') and not (ctx.current and samepath(d['path'], ctx.current)):
            hits.append(dict(session=d['lane'], evidence=f'open {d["kind"]} lane {d["path"]}'))
    return hits


def lane_paths(ctx, d):
    """The paths lane d changed since its base (record base_sha, else the merge base with its into): committed on its
    branch, plus uncommitted and untracked in its tree; None when git cannot say."""
    b = d['branch']
    if not b or not has_ref(ctx.top, f'refs/heads/{b}'):
        return None
    base = d['base_sha'] or out(ctx.top, 'merge-base', f'refs/heads/{d["into"] or ctx.main}', f'refs/heads/{b}')
    if not base:
        return None
    r = git(ctx.top, 'diff', '--no-renames', '--name-only', base, f'refs/heads/{b}')
    if r.returncode:
        return None
    paths = set(r.stdout.splitlines())
    if d['exists']:
        for args in (('diff', '--no-renames', '--name-only', 'HEAD'), ('ls-files', '--others', '--exclude-standard')):
            r = git(d['path'], *args)
            paths |= set(r.stdout.splitlines()) if not r.returncode else set()
    return {p for p in paths if p}


def overlap(paths, cwd='.'):
    """T-0821: (lane, path) for each open plugin lane other than the current tree whose lane_paths hold a path, or a
    path under it when it names a directory; paths are relative to the repository root."""
    ctx = Ctx(cwd)
    want = [p.strip('/') for p in paths if p.strip('/')]
    rows = []
    for d in discover(ctx):
        if not d['owner'] or (ctx.current and samepath(d['path'], ctx.current)):
            continue
        changed = lane_paths(ctx, d) or set()
        rows += [(d['lane'], p) for p in want if any(c == p or c.startswith(p + '/') for c in changed)]
    return rows


def still_open(root, ticket):
    """The `lane still open: <path> (branch <b>, <reason>)` lines for every plugin lane whose record lists the
    ticket or whose host name is <ticket>-solo. Prints nothing."""
    try:
        ctx = Ctx(root)
    except LaneError:
        return []
    lanes = discover(ctx)
    res = []
    for d in lanes:
        if not d['owner']:
            continue
        if ticket not in d['tickets'] and not (d['owner'] == 'host' and d['lane'] == f'{ticket}-solo'):
            continue
        if not d['exists'] and not (d['branch'] and has_ref(ctx.top, f'refs/heads/{d["branch"]}')):
            continue
        row, outcome, rc, info = evaluate(ctx, d, lanes, 'close', fetch=False)
        reason = f'landed: {info["how"]}' if rc == 0 and info else outcome
        res.append(f'lane still open: {d["path"]} (branch {d["branch"] or "none"}, {reason})')
    return res


def check(warn=False, cwd='.'):
    """(findings, rc): C1 placement (17.7, by real path, plus a stray nested tree), C2 ports, C3 record drift."""
    ctx = Ctx(cwd)
    top = ctx.top
    lanes = discover(ctx)
    tops = [w['path'] for w in ctx.wts if not w['bare']]
    tmps, hostdir = tmp_dirs(top), Path(top, *wtroot.CLAUDE)
    found = []
    for d in lanes:
        if not d['exists'] or d['owner'] or any(under(d['path'], t) for t in tmps) or under(d['path'], hostdir):
            continue
        for t in tops:
            if not samepath(t, d['path']) and under(d['path'], t):
                found.append(f'C1: {os.path.basename(d["path"])} is nested in {t} and is not a plugin lane: {d["path"]}')
                break
    outside = not plain_under(ctx.root, top)
    for d in lanes:
        if d['owner'] != 'record' or not d['exists']:
            continue
        if not under(d['path'], ctx.root) and not wtroot.is_legacy(d['path'], top):  # legacy roots read for one release
            found.append(f'C1: {d["lane"]} lies outside the lanes root {ctx.root}: {d["path"]}')
            continue
        if outside:
            for t in tops:
                if not samepath(t, d['path']) and under(d['path'], t):
                    found.append(f'C1: {d["lane"]} lies under the checkout {t} while lanes_root is outside it: {d["path"]}')
                    break
    held = {}
    ports = ctx.cfg['lane_ports']
    for d in lanes:
        if d['owner'] and d['port'] is not None:
            held.setdefault(d['port'], []).append(d['lane'])
            if ports and not (isinstance(d['port'], int) and ports[0] <= d['port'] <= ports[1]):
                found.append(f'C2: {d["lane"]} holds port {d["port"]} outside lane_ports {ports[0]}-{ports[1]}')
    for p, names in sorted(held.items(), key=lambda x: str(x[0])):
        if len(names) > 1:
            found.append(f'C2: port {p} is held by {", ".join(names)}')
    for d in lanes:
        if d['owner'] in ('record', 'host') and d['exists'] and d['record_branch'] and d['record_branch'] != d.get('tree_branch'):
            found.append(f'C3: {d["lane"]} record says branch {d["record_branch"]}, the tree has {d.get("tree_branch") or "a detached HEAD"}: {d["path"]}')
    return found, (1 if found and not warn else 0)


def port_of(path=None):
    p = Path(os.path.abspath(path or os.getcwd()))
    for q in [p] + list(p.parents):
        rec = read_json(q / RECORD)
        if rec is not None:
            if isinstance(rec.get('port'), int):
                return rec['port'], f'{rec["port"]}'
            return None, f'no port for lane {rec.get("lane") or q.name}'
        if (q / RECORD).exists():
            return None, f'unreadable {q / RECORD}'
    return None, f'no lane holds {p}'


def archive_entries(top):
    rows = []
    for line in (out(top, 'for-each-ref', '--format=%(refname) %(objecttype) %(objectname)', 'refs/archive') or '').splitlines():
        refname, typ, obj = line.split(' ', 2)
        rest = refname[len('refs/archive/'):]
        date, _, leaf = rest.partition('/')
        e = dict(ref=refname, date=date, leaf=leaf, branch=leaf, sha=obj, reason='', title='')
        if typ == 'tag':
            e['sha'] = out(top, 'rev-parse', refname + '^{commit}') or obj
            body = out(top, 'cat-file', 'tag', obj) or ''
            msg = body.split('\n\n', 1)[1] if '\n\n' in body else ''
            mlines = msg.splitlines()
            e['title'] = mlines[0] if mlines else ''
            for l in mlines[1:]:
                k, _, v = l.partition(': ')
                if k in ('reason', 'branch') and v:
                    e[k] = v
        rows.append(e)
    return rows


def archive_list(branch=None, cwd='.'):
    ctx = Ctx(cwd)
    rows = archive_entries(ctx.top)
    if branch:
        rows = [e for e in rows if e['branch'] == branch or e['leaf'] == branch or e['leaf'].startswith(branch + '.')]
    return rows


def archive_restore(spec, cwd='.'):
    ctx = Ctx(cwd)
    ref = 'refs/archive/' + spec
    e = next((x for x in archive_entries(ctx.top) if x['ref'] == ref), None)
    if e is None:
        return 1, f'no archive ref {ref}'
    b = e['branch']
    if has_ref(ctx.top, f'refs/heads/{b}'):
        return 1, f'branch {b} exists: not restored'
    r = git(ctx.top, 'branch', b, ref + '^{commit}')
    if r.returncode:
        return 1, f'git branch {b} failed: {err(r)}'
    return 0, f'restored {b} at {e["sha"]}'


def orphans(cwd='.'):
    """[(sha, ref or 'dangling', subject, changed-file count)] for each snapshot ref or dangling commit whose work
    is on no local branch by reachability or patch (git cherry). Read-only."""
    top = Ctx(cwd).top
    branches = [l for l in (out(top, 'for-each-ref', '--format=%(refname)', 'refs/heads') or '').splitlines() if l]
    cands = []
    for line in (out(top, 'for-each-ref', '--format=%(refname)') or '').splitlines():
        if not line or line.startswith(('refs/heads/', 'refs/remotes/')):
            continue
        sha = out(top, 'rev-parse', '--verify', '-q', line + '^{commit}')
        if sha:
            cands.append((sha, line))
    r = git(top, 'fsck', '--no-reflogs', '--connectivity-only', '--no-progress')
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[:2] == ['dangling', 'commit']:
            cands.append((parts[2], 'dangling'))
    rows = []
    for sha, ref in cands:
        unique = None
        for b in branches:
            plus = patch_landed(top, b, sha) or set()
            unique = plus if unique is None else unique & plus
            if not unique:
                break
        if unique is None:  # no local branch at all: everything is unique
            unique = {sha}
        if not unique:
            continue
        subject = out(top, 'log', '-1', '--format=%s', sha) or ''
        files = [f for f in (out(top, 'diff-tree', '--no-commit-id', '-r', '--name-only', '--root', '-m', '--first-parent', sha) or '').splitlines() if f]
        rows.append((sha, ref, subject, len(files)))
    return rows


# ---- CLI --------------------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(prog='lanes.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', metavar='{open,close,finish,ready,sweep,list,who,check,port,archive,orphans,selftest}')
    sub.required = True
    p = sub.add_parser('open')
    p.add_argument('name')
    p.add_argument('--base')
    p.add_argument('--into')
    p.add_argument('--ticket', action='append', default=[])
    p.add_argument('--tickets', action='append', default=[], metavar='ID,ID',
                   help='comma-separated ticket ids, merged after any --ticket in order, duplicates dropped (T-0691)')
    p.add_argument('--kind', choices=KINDS, default='fanout')
    p.add_argument('--title')
    p.add_argument('--root')
    p.add_argument('--path')
    p.add_argument('--branch')
    p.add_argument('--no-claim', action='store_true')
    p.add_argument('--claim', action='store_true', help='claim each local ticket (tickets.py claim) and commit the claim in main first (T-0800)')
    p.add_argument('--by', metavar='AGENT', help='with --claim: the claimant (default: tickets.py claim\'s, $SDLC_HOST or the host)')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('close')
    p.add_argument('target')
    p.add_argument('--into')
    p.add_argument('--discard', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('finish')
    p.add_argument('target')
    p.add_argument('--backup', metavar='REMOTE/REF')
    p.add_argument('--transcript', metavar='JSONL')
    p.add_argument('--verifier-transcript', metavar='JSONL')
    p.add_argument('--verifier-agent-id', metavar='ID', help='record the verifier from its sub-agent transcript and prune it (T-0800)')
    p.add_argument('--solo-agent-id', metavar='ID', help='record the solo from its sub-agent transcript and prune it (T-0800)')
    p.add_argument('--no-ticket', action='store_true', help='land a lane with no ticket behind the land gate, no verdict and no close (T-0821)')
    p = sub.add_parser('ready')
    p.add_argument('target', nargs='?')
    p.add_argument('--ticket')
    p.add_argument('--notify-cmd', metavar='CMD', help='shell command run in the main checkout after the pin, with SDLC_READY_TICKET, SDLC_READY_SHA, SDLC_READY_PATH')
    p = sub.add_parser('sweep')
    p.add_argument('--apply', action='store_true')
    p = sub.add_parser('list')
    p.add_argument('--all', action='store_true')
    p.add_argument('--ready', action='store_true')
    p.add_argument('--stale', action='store_true')
    p.add_argument('--fail', action='store_true')
    p.add_argument('--json', action='store_true')
    p.add_argument('--overlap', nargs='+', metavar='PATH', help='each open lane whose diff from its base touches a path (T-0821)')
    p = sub.add_parser('who')
    p.add_argument('--json', action='store_true')
    p = sub.add_parser('check')
    p.add_argument('--warn', action='store_true')
    p = sub.add_parser('port')
    p.add_argument('path', nargs='?')
    p = sub.add_parser('archive')
    asub = p.add_subparsers(dest='acmd', metavar='{list,restore}')
    asub.required = True
    q = asub.add_parser('list')
    q.add_argument('branch', nargs='?')
    q = asub.add_parser('restore')
    q.add_argument('spec', metavar='<date>/<branch>')
    sub.add_parser('orphans')
    sub.add_parser('selftest')
    a = ap.parse_args(argv)
    if a.cmd == 'open' and a.claim and (a.dry_run or a.no_claim):
        ap.error('--claim takes no --dry-run or --no-claim')
    if a.cmd == 'open' and a.by and not a.claim:
        ap.error('--by needs --claim')
    if a.cmd == 'list' and a.fail and not a.stale:
        ap.error('--fail needs --stale')
    if a.cmd == 'list' and a.ready and (a.all or a.stale):
        ap.error('--ready takes no --all or --stale')
    if a.cmd == 'list' and a.overlap and (a.all or a.stale or a.ready or a.json):
        ap.error('--overlap takes no --all, --stale, --ready or --json')
    if a.cmd == 'selftest':
        return selftest()
    try:
        if a.cmd == 'open':
            ids = merge_tickets(a.ticket, a.tickets)
            if a.claim:
                r = claim_tickets(ids, a.root or '.sdlc', a.by)
                print(r['message'])
                if r['rc']:
                    return r['rc']
            r = open_lane(a.name, base=a.base, into=a.into, tickets=ids, kind=a.kind, title=a.title, root=a.root,
                          dry_run=a.dry_run, path=a.path, branch=a.branch, check_claim=not a.no_claim,
                          record_branch=True, lock=True)
            print(r['message'])
            return r['rc']
        if a.cmd == 'close':
            r = close_lane(a.target, into=a.into, discard=a.discard, dry_run=a.dry_run)
            print(r['message'])
            return r['rc']
        if a.cmd == 'finish':
            return finish(a.target, backup=a.backup, transcript=a.transcript, verifier_transcript=a.verifier_transcript,
                          solo_agent_id=a.solo_agent_id, verifier_agent_id=a.verifier_agent_id, no_ticket=a.no_ticket)
        if a.cmd == 'ready':
            r = ready(a.target, ticket=a.ticket, notify_cmd=a.notify_cmd)
            print(r['message'])
            return r['rc']
        if a.cmd == 'who':
            hits = who()
            if a.json:
                print(json.dumps(dict(who='factory' if hits else 'none', hits=hits), indent=2))
            for h in hits if not a.json else ():
                print(f'factory {h["session"]} {h["evidence"]}')
            if not hits and not a.json:
                print('none')
            return 0
        if a.cmd == 'list' and a.overlap:
            for lane, path in overlap(a.overlap):
                print(f'overlap {lane} {path}')
            return 0
        if a.cmd == 'list' and a.ready:
            rows = ready_rows()
            if a.json:
                print(json.dumps(rows, indent=2))
            for r in rows if not a.json else ():
                print(f'{r["ticket"]}  {r["lane"] or "(no lane)"}  {r["sha"]}  {r["path"] or "-"}' + ('  stale' if r['stale'] else ''))
            return 0
        if a.cmd == 'sweep':
            res, rc = sweep(apply=a.apply)
            for r in res:
                print(r['message'])
            return rc
        if a.cmd == 'list':
            rows = list_lanes(all_=a.all, stale=a.stale)
            if a.json:
                print(json.dumps(rows, indent=2))
            else:
                for r in rows:
                    print(f'{r["state"]:<16} {r["lane"]}  {r["branch"] or "(detached)"}  {r["path"]}' +
                          (f'  {r["description"]}' if r['description'] else '') +
                          (f'  {r["ticket"]} verifier {r["verdict"] or "none"}' if r['ticket'] else ''))
            return 1 if (a.stale and a.fail and rows) else 0
        if a.cmd == 'check':
            found, rc = check(warn=a.warn)
            for f in found:
                print(f)
            if not found:
                print('check: ok')
            return rc
        if a.cmd == 'port':
            port, msg = port_of(a.path)
            print(msg, file=sys.stdout if port else sys.stderr)
            return 0 if port else 1
        if a.cmd == 'archive':
            if a.acmd == 'list':
                for e in archive_list(a.branch):
                    print(f'{e["date"]} {e["branch"]} {e["sha"]} {e["reason"] or "-"} {e["title"]}'.rstrip())
                return 0
            rc, msg = archive_restore(a.spec)
            print(msg)
            return rc
        if a.cmd == 'orphans':
            for sha, ref, subject, n in orphans():
                print(f'{sha} {ref} {subject} ({n} files)')
            return 0
    except LaneError as e:
        print(f'lanes.py: {e}', file=sys.stderr)
        return 1
    return 2


# ---- selftest ---------------------------------------------------------------------------------------------

class Fixture:
    """One throwaway repo with a local bare origin; all git runs with cwd inside it."""
    n = 0

    def __init__(self, base, script, label):
        Fixture.n += 1
        self.dir = Path(base) / f'{label}-{Fixture.n}'
        self.dir.mkdir(parents=True)
        self.script = script
        self.sh(['git', 'init', '-q', '--bare', 'origin.git'], self.dir)
        self.sh(['git', 'init', '-q', '-b', 'main', 'repo'], self.dir)
        self.top = Path(os.path.realpath(str(self.dir / 'repo')))
        self.commit('init', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/\n', 'README': 'r\n', 'old.txt': 'old\n',
                             'keep.txt': 'keep\n'})
        self.g('remote', 'add', 'origin', str(self.dir / 'origin.git'))
        self.g('push', '-q', 'origin', 'main')

    def sh(self, cmd, cwd, env=None):
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
        if r.returncode:
            raise LaneError(f'{" ".join(cmd)}: {r.stderr.strip()}')
        return r.stdout.strip()

    def g(self, *a, cwd=None, env=None):
        return self.sh(['git', *a], cwd or self.top, env)

    def ok(self, *a, cwd=None):
        return subprocess.run(['git', *a], cwd=str(cwd or self.top), capture_output=True, text=True).returncode == 0

    def write(self, files, cwd=None):
        for k, v in files.items():
            p = Path(cwd or self.top) / k
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(v)

    def commit(self, msg, files=None, cwd=None, days=3):
        if files:
            self.write(files, cwd)
            self.g('add', '--', *files, cwd=cwd)
        ts = f'@{int(time.time() - days * 86400)} +0000'
        env = dict(os.environ, GIT_AUTHOR_DATE=ts, GIT_COMMITTER_DATE=ts)
        self.g('commit', '-q', '--allow-empty', '-m', msg, cwd=cwd, env=env)

    def lanes(self, *a, cwd=None, env=None):
        e = dict(os.environ)
        e.update(env or {})
        r = subprocess.run([sys.executable, str(self.script), *a], cwd=str(cwd or self.top), capture_output=True,
                           text=True, env=e, timeout=300)
        return r.returncode, (r.stdout + r.stderr).strip()

    def tree(self, leaf):
        return wtroot.default_root(self.top) / leaf

    def open(self, name, ticket=None, *extra, keep_lock=False):
        """Open a lane with the CLI; unless keep_lock, unlock it as its worker's ready would (T-0589)."""
        args = ['open', name] + (['--ticket', ticket] if ticket else []) + list(extra)
        rc, o = self.lanes(*args)
        if rc:
            raise LaneError(f'open {name} failed: {o}')
        m = re.search(r'opened (\S+) at (.+?) \(branch (\S+),', o)
        if not keep_lock:
            self.ok('worktree', 'unlock', m.group(2))  # an unlocked tree (an integration lane) fails harmlessly
        return m.group(1), Path(m.group(2)), m.group(3)

    def work(self, tree, files=None, days=3):
        self.commit('work', files or {'f-%s.txt' % Path(tree).name: 'x\n'}, cwd=tree, days=days)

    def merge(self, branch, squash=False):
        if squash:
            self.g('merge', '--squash', '-q', f'refs/heads/{branch}')
            self.commit('squash')
        else:
            self.g('merge', '--no-ff', '-q', '-m', f'merge {branch}', f'refs/heads/{branch}')

    def archive_refs(self):
        return [l for l in self.g('for-each-ref', '--format=%(refname)', 'refs/archive').splitlines() if l]

    def ticket(self, num, title, claimed=False, status='ready'):
        cb = 'claimed_by: claude 2026-10-11\n' if claimed else ''
        self.write({f'.sdlc/{num:04d}-t/handoff.md': f'---\nid: T-{num}\ntitle: "{title}"\ntype: feature\nstatus: {status}\n'
                                                    f'size: L1\npriority: P2\ndepends: []\ncreated: 2026-10-11\n{cb}---\n\nbody\n'})


def today():
    return utcnow().strftime('%Y-%m-%d')


def case_row1(script, base):
    t = Fixture(base, script, 'row1')
    t.g('worktree', 'add', '-q', '-b', 'manual', str(t.dir / 'manual'))
    rc, o = t.lanes('close', str(t.dir / 'manual'))
    fails = [] if rc == 2 and 'not a plugin lane: ' in o else [f'row 1: want exit 2 and not a plugin lane, got {rc}: {o}']
    if not (t.dir / 'manual').is_dir() or not t.ok('rev-parse', '--verify', 'refs/heads/manual'):
        fails.append('row 1: the manual tree or branch changed')
    return fails


def case_row2(script, base):
    t = Fixture(base, script, 'row2')
    rc, o = t.lanes('close', 'nosuch')
    return [] if rc == 1 and o == 'no lane nosuch' else [f'row 2: got {rc}: {o}']


def case_row3(script, base):
    t = Fixture(base, script, 'row3')
    t.write({'.worktrees/host/h3.lane.json': json.dumps(dict(lane='h3', kind='host', branch='worktree-h3', into='main'))})
    t.g('worktree', 'add', '-q', '-b', 'worktree-h3', str(t.dir / 'other'))
    rc, o = t.lanes('close', 'h3')
    return [] if rc == 1 and o.startswith('branch worktree-h3 checked out at ') else [f'row 3: got {rc}: {o}']


def case_row4(script, base):
    t = Fixture(base, script, 'row4')
    t.open('wave/1', None, '--kind', 'integration')
    leaf, _, _ = t.open('a', 'T-4', '--base', 'wave/1')
    rc, o = t.lanes('close', 'wave/1')
    return [] if rc == 1 and o == f'lanes still open into wave/1: {leaf}' else [f'row 4: got {rc}: {o}']


def case_row5(script, base):
    t = Fixture(base, script, 'row5')
    leaf, tree, b = t.open('a', 'T-5')
    t.work(tree)
    fails = []
    rc, o = t.lanes('close', leaf, '--into', 'refs/remotes/origin/nope')
    if not (rc == 1 and o.startswith('cannot decide: ')):
        fails.append(f'row 5 (unresolvable into): got {rc}: {o}')
    tree_sha = subprocess.run(['git', 'mktree'], cwd=str(t.top), input='', capture_output=True, text=True).stdout.strip()
    c = t.g('commit-tree', tree_sha, '-m', 'orphan')
    t.g('update-ref', 'refs/heads/orphan', c)
    rc, o = t.lanes('close', leaf, '--into', 'orphan')
    if not (rc == 1 and o.startswith('cannot decide: ')):
        fails.append(f'row 5 (unrelated into, failed diff) closed or gave another outcome: {rc}: {o}')
    if not tree.is_dir() or not t.ok('rev-parse', '--verify', f'refs/heads/{b}'):
        fails.append('row 5: the lane was closed')
    return fails


def case_row6(script, base):
    t = Fixture(base, script, 'row6')
    leaf, tree, b = t.open('a', 'T-6')
    t.work(tree)
    t.merge(b)
    (tree / 'keep.txt').write_text('edited\n')
    rc, o = t.lanes('close', leaf)
    fails = [] if rc == 1 and o == f'uncommitted changes in {leaf}: keep.txt' else [f'row 6: dirty lane closed or other outcome: {rc}: {o}']
    if not tree.is_dir():
        fails.append('row 6: the dirty lane was closed')
    return fails


def case_row9(script, base):
    t = Fixture(base, script, 'row9')
    leaf, tree, b = t.open('a', 'T-9')
    t.work(tree)
    t.merge(b)
    t.write({'.sdlc/note.md': 'kept\n', '.sdlc/runtime/.gitignore': '*\n', '.sdlc/runtime/tasks/x/verifier-L1.md': 'kept\n', '.sdlc/runtime/tasks/x/run.log': 'noise\n'}, cwd=tree)
    rc, o = t.lanes('close', leaf)
    fails = [] if rc == 0 and o == f'closed {leaf} (ancestor)' else [f'row 9: got {rc}: {o}']
    if tree.exists() or t.ok('rev-parse', '--verify', f'refs/heads/{b}'):
        fails.append('row 9: the tree or branch is still there')
    if f'refs/archive/{today()}/{b}' not in t.archive_refs():
        fails.append(f'row 9: no archive ref, have {t.archive_refs()}')
    if not (t.top / '.git' / 'sdlc-lane-archive' / leaf / '.sdlc' / 'note.md').is_file():
        fails.append('row 9: the .sdlc file was not archived')
    if not (t.top / '.git' / 'sdlc-lane-archive' / leaf / '.sdlc' / 'runtime' / 'tasks' / 'x' / 'verifier-L1.md').is_file():
        fails.append('row 9: the runtime records were not archived')
    if (t.top / '.git' / 'sdlc-lane-archive' / leaf / '.sdlc' / 'runtime' / 'tasks' / 'x' / 'run.log').exists():
        fails.append('row 9: a runtime log was archived')
    if t.g('for-each-ref', 'refs/tags'):
        fails.append('row 9: a ref under refs/tags was created')
    return fails


def case_work_root(script, base):
    """T-0626: under `work_root: docs/work` an untracked ticket folder there is trail like .sdlc/, not dirt, and
    close archives it with the .sdlc files."""
    t = Fixture(base, script, 'workroot')
    leaf, tree, b = t.open('a', 'T-13')
    t.work(tree)
    t.merge(b)
    t.write({'.sdlc/config': 'work_root: docs/work\n', 'docs/work/0002-b/handoff.md': 'trail\n'}, cwd=tree)
    rc, o = t.lanes('close', leaf)
    fails = [] if rc == 0 and o == f'closed {leaf} (ancestor)' else [f'work root: got {rc}: {o}']
    if not (t.top / '.git' / 'sdlc-lane-archive' / leaf / 'docs' / 'work' / '0002-b' / 'handoff.md').is_file():
        fails.append('work root: the untracked docs/work ticket was not archived')
    return fails


def case_carry(script, base):
    """T-0566: close carries a lane ticket's runtime records into the main checkout, keeps a newer main file, and a
    discarded lane carries nothing."""
    t = Fixture(base, script, 'carry')
    fails = []
    for num, discard in ((8, False), (9, True)):
        t.ticket(num, f'T{num}', claimed=True, status='claimed')
        leaf, tree, b = t.open(f'c{num}', f'T-{num}')
        t.work(tree)
        if not discard:
            t.merge(b)
        key = f'.sdlc/runtime/tasks/{num:04d}-t'
        t.write({f'.sdlc/{num:04d}-t/handoff.md': (t.top / f'.sdlc/{num:04d}-t/handoff.md').read_text(),
                 '.sdlc/runtime/.gitignore': '*\n', f'{key}/verifier-L2.md': 'lane\n', f'{key}/runs.jsonl': 'lane\n'}, cwd=tree)
        t.write({f'{key}/runs.jsonl': 'main\n'})
        future = time.time() + 3600
        os.utime(t.top / key / 'runs.jsonl', (future, future))
        rc, o = t.lanes('close', leaf, *(['--discard'] if discard else []))
        carried = [ln[len('records: '):] for ln in o.splitlines() if ln.startswith('records: ')]
        got = (t.top / key / 'verifier-L2.md').is_file()
        if discard:
            if rc or carried or got:
                fails.append(f'carry: a discarded lane carried records: {rc}: {o}')
            continue
        if rc or len(carried) != 1 or not samepath(carried[0], t.top / key) or not got:
            fails.append(f'carry: the lane records did not reach the main checkout: {rc}: {o}')
        if (t.top / key / 'runs.jsonl').read_text() != 'main\nlane\n':
            fails.append('carry: a main runs.jsonl newer than the lane copy was overwritten or missed the lane row (T-0775)')
    return fails


def case_carry_work_root(script, base):
    """T-0639: under `work_root: docs/work` the ticket folder sits outside .sdlc, and close still carries its runtime
    records into the main checkout's records dir."""
    t = Fixture(base, script, 'carrywr')
    num = 8
    leaf, tree, b = t.open('c8', f'T-{num}')
    t.work(tree)
    t.merge(b)
    key = f'.sdlc/runtime/tasks/{num:04d}-t'
    t.write({'.sdlc/config': 'work_root: docs/work\n'})
    t.write({'.sdlc/config': 'work_root: docs/work\n', '.sdlc/runtime/.gitignore': '*\n', f'{key}/verifier-L2.md': 'lane\n',
             f'docs/work/{num:04d}-t/handoff.md': f'---\nid: T-{num}\ntitle: "T8"\ntype: feature\nstatus: claimed\nsize: L1\n'
                                                f'priority: P2\ndepends: []\ncreated: 2026-10-11\n---\n\nbody\n'}, cwd=tree)
    rc, o = t.lanes('close', leaf)
    carried = [ln[len('records: '):] for ln in o.splitlines() if ln.startswith('records: ')]
    if rc or len(carried) != 1 or not samepath(carried[0], t.top / key) or not (t.top / key / 'verifier-L2.md').is_file():
        return [f'carry work root: the lane records did not reach the main checkout: {rc}: {o}']
    return []


def stub_env(base, data):
    p = Path(base) / f'gh-{time.time_ns()}.json'
    p.write_text(json.dumps(data))
    return {'LANES_STUB_GH': str(p)}


def case_prmerged(script, base):
    t = Fixture(base, script, 'pr')
    leaf, tree, b = t.open('a', 'T-7')
    t.work(tree)
    tip = t.g('rev-parse', f'refs/heads/{b}')
    rc, o = t.lanes('close', leaf, env=stub_env(base, [{'headRefOid': tip}]))
    return [] if rc == 0 and o == f'closed {leaf} (pr merged)' and not tree.exists() else [f'row pr merged: got {rc}: {o}']


def case_row10(script, base):
    t = Fixture(base, script, 'row10')
    leaf, tree, b = t.open('a', 'T-10')
    t.work(tree)
    t.merge(b, squash=True)
    rc, o = t.lanes('close', leaf)
    return [] if rc == 0 and o == f'closed {leaf} (content in main)' and not tree.exists() else [f'row 10: got {rc}: {o}']


def case_row11(script, base):
    t = Fixture(base, script, 'row11')
    leaf, tree, b = t.open('a', 'T-11')
    t.work(tree, {'new.md': 'n\n'})
    rc, o = t.lanes('close', leaf)
    return [] if rc == 1 and o == f'not landed in main: first new.md; merge it or --discard' and tree.is_dir() else [f'row 11: got {rc}: {o}']


def case_rename(script, base):
    t = Fixture(base, script, 'rename')
    leaf, tree, b = t.open('a', 'T-12')
    t.g('mv', 'old.txt', 'new.txt', cwd=tree)
    t.commit('rename', cwd=tree)
    t.commit('copy', {'new.txt': 'old\n'})
    rc, o = t.lanes('close', leaf)
    return [] if rc == 1 and o.startswith('not landed in main: first old.txt') and tree.is_dir() else [f'rename case closed or other outcome: {rc}: {o}']


def case_deleted(script, base):
    t = Fixture(base, script, 'deleted')
    leaf, tree, b = t.open('a', 'T-13')
    t.g('rm', '-q', 'keep.txt', cwd=tree)
    t.commit('delete', cwd=tree)
    rc, o = t.lanes('close', leaf)
    return [] if rc == 1 and o.startswith('not landed in main: first keep.txt') and tree.is_dir() else [f'deleted-file case closed or other outcome: {rc}: {o}']


def case_row12(script, base):
    t = Fixture(base, script, 'row12')
    leaf, tree, b = t.open('a', 'T-14')
    t.work(tree)
    tip = t.g('rev-parse', f'refs/heads/{b}')
    rc, o = t.lanes('close', leaf, '--discard')
    fails = [] if rc == 0 and o == f'closed {leaf} (discarded {tip})' else [f'row 12: got {rc}: {o}']
    ref = f'refs/archive/{today()}/{b}'
    if ref not in t.archive_refs() or 'reason: discarded' not in t.g('cat-file', '-p', ref):
        fails.append('row 12: no archive tag with reason discarded')
    if t.ok('rev-parse', '--verify', f'refs/heads/{b}') or tree.exists():
        fails.append('row 12: the branch or tree is still there')
    return fails


def case_sweep(script, base):
    """Rows 7, 8, recent, in use and locked in sweep, and C5: only the landed lane goes."""
    t = Fixture(base, script, 'sweep')
    land = t.open('land', 'T-20')
    t.work(land[1])
    t.merge(land[2])
    empty = t.open('empty', 'T-21')
    host = t.top / '.claude' / 'worktrees' / 'h8'
    t.g('worktree', 'add', '-q', '-b', 'worktree-h8', str(host))
    t.write({'.worktrees/host/h8.lane.json': json.dumps(dict(lane='h8', kind='host', branch='worktree-h8', into='main'))})
    t.work(host)
    t.merge('worktree-h8')
    recent = t.open('recent', 'T-22')
    t.work(recent[1], days=0)
    t.merge(recent[2])
    inuse = t.open('inuse', 'T-23')
    t.work(inuse[1])
    t.merge(inuse[2])
    locked = t.open('locked', 'T-24')
    t.work(locked[1])
    t.merge(locked[2])
    t.g('worktree', 'lock', '--reason', 'run-x T-24', str(locked[1]))
    unl = t.open('unl', 'T-25')
    t.work(unl[1])
    dirty = t.open('dirty', 'T-26')
    t.work(dirty[1])
    t.merge(dirty[2])
    (dirty[1] / 'keep.txt').write_text('edited\n')
    t.g('worktree', 'add', '-q', '-b', 'manual2', str(t.dir / 'manual2'))
    t.write({'.sdlc/runtime/prune.json': json.dumps([dict(name='h8', recorded_at=utcnow().isoformat())])})
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)', str(inuse[1])])
    try:
        rc, dry = t.lanes('sweep')
        before = t.archive_refs() + ([] if land[1].is_dir() else ['the landed tree went in the dry run'])
        rc2, o = t.lanes('sweep', '--apply')
    finally:
        child.terminate()
        child.wait()
    fails = []
    if f'would close {land[0]} (ancestor)' not in dry or before:
        fails.append(f'sweep dry run changed something or did not report: {dry}')
    want = {'row 7': f'kept {empty[0]}: no commits', 'row 8': 'kept h8: agent not pruned',
            'row recent': f'kept {recent[0]}: recent', 'row in use': f'kept {inuse[0]}: in use by pid {child.pid}',
            'row locked': f'kept {locked[0]}: locked: run-x T-24', 'C5': f'closed {land[0]} (ancestor)'}
    for k, line in want.items():
        if line not in o.splitlines():
            fails.append(f'{k}: sweep printed no {line!r}: {o}')
    if f'kept {unl[0]}: not landed in main' not in o or f'kept {dirty[0]}: uncommitted changes in {dirty[0]}: keep.txt' not in o:
        fails.append(f'C5: the unlanded or dirty lane was not kept: {o}')
    gone = [x[0] for x in (land, empty, recent, inuse, locked, unl, dirty) if not x[1].exists()]
    if rc2 or gone != [land[0]] or not host.is_dir() or not (t.dir / 'manual2').is_dir() or len(t.archive_refs()) != 1:
        fails.append(f'C5: want only {land[0]} gone and one archive ref; gone {gone}, refs {t.archive_refs()}, rc {rc2}')
    rc, o = t.lanes('close', locked[0])
    if not (rc == 1 and o == 'locked: run-x T-24'):
        fails.append(f'row locked: close of a locked lane did not refuse: {rc}: {o}')
    return fails


def case_c1_nested(script, base):
    t = Fixture(base, script, 'c1')
    fails = []
    t.g('worktree', 'add', '-q', '-b', 'x', str(t.top / 'stray'))
    rc, o = t.lanes('check')
    if rc != 1 or 'stray' not in o:
        fails.append(f'C1: a stray nested tree passed: {rc}: {o}')
    t.g('worktree', 'remove', '--force', str(t.top / 'stray'))
    t.open('a', 'T-30')
    rc, o = t.lanes('check')
    if rc != 0:
        fails.append(f'C1: a lane from open failed check: {o}')
    t.g('worktree', 'add', '-q', '-b', 'lane/T-31-e', str(t.top / 'elsewhere' / 'T-31-e'))
    t.write({'elsewhere/T-31-e/.lane.json': json.dumps(dict(lane='T-31-e', kind='fanout', branch='lane/T-31-e', into='main'))})
    rc, o = t.lanes('check')
    if rc != 1 or 'T-31-e' not in o:
        fails.append(f'C1: a lane record outside the lanes root passed: {rc}: {o}')
    return fails


def case_c1_outside(script, base):
    t = Fixture(base, script, 'c1out')
    fails = []
    t.write({'.sdlc/config': 'lanes_root: ../outside\n'})
    leaf, tree, b = t.open('a', 'T-32', '--root', '.none')
    rc, o = t.lanes('check')
    if rc != 0 or not str(tree).startswith(str(t.dir / 'outside')):
        fails.append(f'C1: a lane under ../outside failed: {rc}: {o} ({tree})')
    t.g('worktree', 'add', '-q', '-b', 'lane/T-33-x', str(t.top / '.worktrees' / 'x'))
    t.write({'.worktrees/x/.lane.json': json.dumps(dict(lane='x', kind='fanout', branch='lane/T-33-x', into='main'))})
    rc, o = t.lanes('check')
    if rc != 1 or ' x ' not in o + ' ':
        fails.append(f'C1: a lane under the checkout passed with lanes_root outside: {rc}: {o}')
    t.g('worktree', 'remove', '--force', str(t.top / '.worktrees' / 'x'))
    moved = t.top / '.worktrees' / 'moved'
    os.rename(str(t.dir / 'outside'), str(moved))
    os.symlink(str(moved), str(t.dir / 'outside'))
    rc, o = t.lanes('check')
    if rc != 1 or leaf not in o:
        fails.append(f'C1 passed a symlinked path: a lane really under the checkout passed: {rc}: {o}')
    return fails


def case_c2(script, base):
    t = Fixture(base, script, 'c2')
    fails = []
    la, ta, ba = t.open('a', 'T-34')
    lb, tb, bb = t.open('b', 'T-35')
    for tr in (ta, tb):
        rec = json.loads((tr / RECORD).read_text())
        rec['port'] = 7400
        (tr / RECORD).write_text(json.dumps(rec))
    rc, o = t.lanes('check')
    if rc != 1 or 'port 7400' not in o:
        fails.append(f'C2: two records on one port passed: {rc}: {o}')
    t.work(ta)
    t.merge(ba)
    t.lanes('close', la)
    rc, o = t.lanes('check')
    if rc != 0:
        fails.append(f'C2: one record on 7400 after a close failed: {o}')
    t.write({'.sdlc/config': 'lane_ports: 7500-7510\n'})
    rc, o = t.lanes('check')
    if rc != 1 or 'outside lane_ports' not in o:
        fails.append(f'C2: a port outside lane_ports passed: {rc}: {o}')
    t.write({'.sdlc/config': 'lane_ports: 47600-47699\n'})
    rec = json.loads((tb / RECORD).read_text())
    rec['port'] = 47699
    (tb / RECORD).write_text(json.dumps(rec))
    l1 = t.open('p1', 'T-36', '--root', '.none')
    l2 = t.open('p2', 'T-37', '--root', '.none')
    ports = [json.loads((x[1] / RECORD).read_text())['port'] for x in (l1, l2)]
    rc1, o1 = t.lanes('port', str(l1[1]))
    rc2, o2 = t.lanes('port', cwd=l2[1])
    rc3, o3 = t.lanes('port', str(t.top))
    if None in ports or ports[0] == ports[1] or o1 != str(ports[0]) or o2 != str(ports[1]) or rc3 != 1:
        fails.append(f'C2: open picked ports {ports}; port printed {o1!r}, {o2!r}; outside a lane rc {rc3}')
    rc, o = t.lanes('check')
    if rc != 0:
        fails.append(f'C2: ports from open failed check: {o}')
    return fails


def case_c3(script, base):
    t = Fixture(base, script, 'c3')
    leaf, tree, b = t.open('a', 'T-38')
    rec = json.loads((tree / RECORD).read_text())
    rec['branch'] = 'lane/T-38-other'
    (tree / RECORD).write_text(json.dumps(rec))
    rc, o = t.lanes('check')
    return [] if rc == 1 and 'C3' in o and leaf in o else [f'C3: a record on another branch passed: {rc}: {o}']


def case_c4(script, base):
    t = Fixture(base, script, 'c4')
    s11 = t.open('s11', 'T-40')
    t.work(s11[1], days=11)
    s9 = t.open('s9', 'T-41')
    t.work(s9[1], days=9)
    cl = t.open('cl', 'T-42')
    t.work(cl[1], days=30)
    t.merge(cl[2])
    sl = t.open('sl', 'T-43')
    t.work(sl[1], days=11)
    t.g('worktree', 'lock', '--reason', f'agent pid {os.getpid()}', str(sl[1]))
    rc, o = t.lanes('list', '--stale', '--json')
    fails = []
    try:
        rows = {r['lane']: r['state'] for r in json.loads(o)}
    except ValueError:
        return [f'C4: list --stale --json is not JSON: {o}']
    want = {s11[0]: 'stale', cl[0]: 'closable', sl[0]: 'stale, locked'}
    if rc != 0 or rows != want:
        fails.append(f'C4: want {want}, got {rows} (rc {rc})')
    rc, o = t.lanes('list', '--stale', '--fail')
    if rc != 1:
        fails.append(f'C4: list --stale --fail exit {rc}')
    rc, o = t.lanes('sweep', '--apply')
    if not sl[1].is_dir() or f'kept {sl[0]}: locked: agent pid {os.getpid()}' not in o:
        fails.append(f'C4: sweep --apply did not keep the locked stale lane: {o}')
    return fails


def case_c9(script, base):
    t = Fixture(base, script, 'c9')
    fails = []
    t.g('branch', 'lane')
    rc, o = t.lanes('open', 'a', '--ticket', 'T-50')
    if rc != 1 or 'clashes with refs/heads/lane' not in o:
        fails.append(f'C9: lane/T-50-a beside lane was not refused: {rc}: {o}')
    if t.tree('T-50-a').exists():
        fails.append('C9: a refusal left a directory (lane/x beside lane)')
    t.g('branch', '-D', 'lane')
    t.g('branch', 'lane/x')
    rc, o = t.lanes('open', 'lane', '--kind', 'integration')
    if rc != 1 or 'clashes with refs/heads/lane/x' not in o:
        fails.append(f'C9: lane beside lane/x was not refused: {rc}: {o}')
    if t.tree('lane').exists():
        fails.append('C9: a refusal left a directory (lane beside lane/x)')
    rc, o = t.lanes('open', 'a')
    if rc != 1 or 'needs --ticket' not in o:
        fails.append(f'C9: a lane with no ticket was not refused: {rc}: {o}')
    if t.ok('rev-parse', '--verify', 'refs/heads/lane/T-50-a') or t.ok('rev-parse', '--verify', 'refs/heads/lane'):
        fails.append('C9: a refusal left a branch')
    rc, o = t.lanes('open', 'a', '--ticket', 'T-1')
    if rc != 0 or not (t.tree('T-1-a') / RECORD).is_file() or not t.ok('rev-parse', '--verify', 'refs/heads/lane/T-1-a'):
        fails.append(f'C9: lane/T-1-a did not open: {rc}: {o}')
    return fails


def case_tickets_csv(script, base):
    """T-0691: --tickets T-1,T-2 is two --ticket; mixed forms concatenate and drop duplicates."""
    t = Fixture(base, script, 'csv')
    t.ticket(1, 'First', claimed=True)
    t.ticket(2, 'Second', claimed=True)
    t.ticket(3, 'Third')
    fails = []
    rc, o = t.lanes('open', 'a', '--tickets', 'T-1,T-2', '--dry-run')
    rc2, o2 = t.lanes('open', 'a', '--ticket', 'T-1', '--ticket', 'T-2', '--dry-run')
    rc3, o3 = t.lanes('open', 'a', '--ticket', 'T-1', '--tickets', 'T-1,T-2', '--dry-run')
    if rc != 0 or (rc, o) != (rc2, o2) or (rc, o) != (rc3, o3):
        fails.append(f'tickets csv: --tickets differs from two --ticket: {(rc, o)} vs {(rc2, o2)} vs {(rc3, o3)}')
    rc, o = t.lanes('open', 'b', '--tickets', 'T-1,T-3')
    if rc != 1 or 'T-3' not in o or 'not claimed' not in o:
        fails.append(f'tickets csv: the second id of --tickets was not checked: {rc}: {o}')
    return fails


def case_plugin_min(script, base):
    """T-0593: a plugin_min: line above the running manifest refuses open with exit 2 naming both versions and the
    host's update command, leaving no tree and no branch; an equal version opens."""
    t = Fixture(base, script, 'pmin')
    fails = []
    have = json.loads((HERE.parent / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))['version']
    parts = have.split('.')
    need = '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])
    t.write({'.sdlc/0070-pmin/handoff.md': ticket_file('T-0070', claimed=True)})
    t.write({'.sdlc/config': f'plugin_min: {need}\n'})
    for host, cmd in (('claude', 'claude plugin update'), ('codex', 'codex plugin marketplace upgrade')):
        rc, o = t.lanes('open', 'a', '--ticket', 'T-0070', env={'SDLC_BACKEND': host})
        if rc != 2 or need not in o or have not in o or cmd not in o:
            fails.append(f'plugin_min {need} above {have} on {host}: want exit 2 naming both and {cmd}: {rc}: {o}')
    if t.tree('T-0070-a').exists() or t.ok('rev-parse', '--verify', 'refs/heads/lane/T-0070-a'):
        fails.append('plugin_min: a refusal left a tree or a branch')
    t.write({'.sdlc/config': f'plugin_min: {have}\n'})
    rc, o = t.lanes('open', 'a', '--ticket', 'T-0070', env={'SDLC_BACKEND': 'claude', 'CLAUDE_PLUGIN_ROOT': '',  # T-0596: no install
                                                           'SDLC_PLUGIN_CACHE': str(base / 'no-cache')})
    if rc != 0 or not (t.tree('T-0070-a') / RECORD).is_file():
        fails.append(f'plugin_min equal to {have}: open did not pass: {rc}: {o}')
    return fails


def case_codex_agents(script, base):
    """T-0598: a lane opened in a repo onboarded with codex_roles.py install gets the generated .codex/agents too (they
    are git-ignored, so a new tree never has them), and install --check passes there; a repo never onboarded gets none."""
    roles = HERE / 'codex_roles.py'
    fails = []
    t = Fixture(base, script, 'cxag')
    t.write({'.sdlc/0071-cxag/handoff.md': ticket_file('T-0071', claimed=True)})
    t.sh([sys.executable, str(roles), 'install', str(t.top)], t.top)
    leaf, tree, b = t.open('a', 'T-0071')
    r = subprocess.run([sys.executable, str(roles), 'install', '--check', str(tree)], capture_output=True, text=True)
    if r.returncode:
        fails.append(f'onboarded repo: install --check in the new lane exit {r.returncode}: {(r.stdout + r.stderr).strip()}')
    u = Fixture(base, script, 'cxno')
    u.write({'.sdlc/0072-cxno/handoff.md': ticket_file('T-0072', claimed=True)})
    leaf, tree, b = u.open('a', 'T-0072')
    if (tree / '.codex').exists():
        fails.append('repo never onboarded: the lane got a .codex directory')
    return fails


def case_c10(script, base):
    t = Fixture(base, script, 'c10')
    fails = []
    leaf, tree, b = t.open('a', 'T-60')
    t.work(tree)
    t.merge(b)
    tip = t.g('rev-parse', f'refs/heads/{b}')
    t.lanes('close', leaf)
    rc, o = t.lanes('archive', 'list', b)
    if rc or f'{today()} {b} {tip} ancestor T-60' not in o:
        fails.append(f'C10: archive list did not show the close: {o}')
    rc, o = t.lanes('archive', 'restore', f'{today()}/{b}')
    if rc or t.g('rev-parse', f'refs/heads/{b}') != tip:
        fails.append(f'C10: archive restore did not return the tip: {rc}: {o}')
    rc, o = t.lanes('archive', 'restore', f'{today()}/{b}')
    if rc != 1 or 'exists' not in o:
        fails.append(f'C10: archive restore over an existing branch did not refuse: {rc}: {o}')
    t.g('update-ref', 'refs/archive/2026-01-01/old-commit-ref', tip)
    rc, o = t.lanes('archive', 'list')
    if '2026-01-01 old-commit-ref ' + tip not in o:
        fails.append(f'C10: archive list did not read a plain commit ref: {o}')
    return fails


def case_archive_twice(script, base):
    t = Fixture(base, script, 'twice')
    for i in (1, 2):
        leaf, tree, b = t.open('z', 'T-61')
        t.work(tree, {f'z{i}.txt': f'{i}\n'})
        t.merge(b)
        rc, o = t.lanes('close', leaf)
        if rc:
            return [f'C10: close {i} of one name failed: {o}']
    refs = [r for r in t.archive_refs() if '/lane/T-61-z' in r]
    return [] if len(refs) == 2 else [f'C10: two closes of one name on one date left one ref or another count: {refs}']


def case_archive_clash(script, base):
    t = Fixture(base, script, 'clash')
    leaf, tree, b = t.open('c', 'T-62')
    t.work(tree)
    t.merge(b)
    t.g('update-ref', f'refs/archive/{today()}/lane', t.g('rev-parse', 'HEAD'))
    rc, o = t.lanes('close', leaf)
    fails = []
    if not t.ok('rev-parse', '--verify', f'refs/heads/{b}'):
        fails.append(f'C10: a failed archive write still let the branch be deleted: {rc}: {o}')
    if rc != 1 or not tree.is_dir() or 'cannot write' not in o:
        fails.append(f'C10: a forced ref directory clash did not stop the close: {rc}: {o}')
    return fails


def case_orphans(script, base):
    """T-0580: a dangling commit holding a unique change is listed; a snapshot ref whose change reached main by
    squash is not; orphans writes no ref and no lost-found."""
    t = Fixture(base, script, 'orphans')
    leaf, tree, b = t.open('s', 'T-63')
    t.work(tree, {'landed.txt': 'landed\n'})
    t.merge(b, squash=True)
    rc, o = t.lanes('close', leaf)
    if rc:
        return [f'orphans: the squash-landed lane did not close: {o}']
    snap = [r for r in t.archive_refs() if r.endswith('/' + b)]
    snap_sha = t.g('rev-parse', snap[0] + '^{commit}') if snap else ''
    t.write({'unique.txt': 'only here\n'})
    t.g('add', 'unique.txt')
    tree_sha = t.g('write-tree')
    t.g('reset', '-q')
    (t.top / 'unique.txt').unlink()
    dangling = t.g('commit-tree', tree_sha, '-p', 'HEAD', '-m', 'stranded work')
    refs_before = t.g('for-each-ref')
    rc, o = t.lanes('orphans')
    fails = []
    if rc != 0 or f'{dangling} dangling stranded work (1 files)' not in o.splitlines():
        fails.append(f'orphans: the dangling commit with a unique change is not listed: {rc}: {o}')
    if not snap_sha or snap_sha in o:
        fails.append(f'orphans: the snapshot ref whose change is on main is listed (or missing: {snap}): {o}')
    if t.g('for-each-ref') != refs_before or (t.top / '.git' / 'lost-found').exists():
        fails.append('orphans: the repo changed')
    return fails


def case_c13(script, base):
    t = Fixture(base, script, 'c13')
    leaf, tree, b = t.open('a', 'T-70', '--title', 'Make the thing')
    fails = []
    if t.g('config', '--get', f'branch.{b}.description') != 'T-70 Make the thing':
        fails.append('C13: the branch description is not <ticket> <title>')
    t.work(tree)
    t.merge(b)
    t.lanes('close', leaf)
    ref = f'refs/archive/{today()}/{b}'
    msg = t.g('cat-file', '-p', ref) if ref in t.archive_refs() else ''
    if 'T-70 Make the thing' not in msg:
        fails.append(f'C13: the archive tag message lacks the description: {msg!r}')
    return fails


def case_claim_unclaimed(script, base):
    t = Fixture(base, script, 'claim')
    t.ticket(1, 'First')
    fails = []
    rc, o = t.lanes('open', 'a', '--ticket', 'T-1')
    if rc != 1 or o != 'ticket T-1 not claimed: set claimed_by: first':
        fails.append(f'claim unclaimed: got {rc}: {o}')
    rc, o = t.lanes('open', 'b', '--ticket', 'T-99')
    if rc != 1 or o != 'no ticket T-99':
        fails.append(f'claim unclaimed: an unknown local id got {rc}: {o}')
    if t.tree('T-1-a').exists() or t.ok('rev-parse', '--verify', 'refs/heads/lane/T-1-a'):
        fails.append('claim unclaimed: a refusal created something')
    return fails


def case_claim_external(script, base):
    t = Fixture(base, script, 'ext')
    fails = []
    rc, o = t.lanes('open', 'a', '--ticket', '#123')
    if rc or 'claim #123 in its tracker (assignee) before work; not checked here' not in o or \
            not t.ok('rev-parse', '--verify', 'refs/heads/lane/123-a'):
        fails.append(f'claim external: got {rc}: {o}')
    rc, o = t.lanes('open', 'b', '--ticket', 'T-7')
    if rc or 'claim T-7 in its tracker' not in o:
        fails.append(f'claim external: a T- id with no --root got {rc}: {o}')
    return fails


def case_claim_still_open(script, base):
    t = Fixture(base, script, 'still')
    t.ticket(2, 'Second', claimed=True, status='claimed')
    fails = []
    leaf, tree, b = t.open('a', 'T-2')
    if t.g('config', '--get', f'branch.{b}.description') != 'T-2 Second':
        fails.append('claim still open: the description does not carry the local title')
    t.work(tree)
    t.merge(b)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        lines = still_open(str(t.top / '.sdlc'), 'T-2')
    if buf.getvalue() or lines != [f'lane still open: {tree} (branch {b}, landed: ancestor)']:
        fails.append(f'still_open: got {lines} and printed {buf.getvalue()!r}')
    rc, o = t.lanes('close', leaf)
    if rc or o.splitlines() != [f'closed {leaf} (ancestor)', 'ticket still open: T-2']:
        fails.append(f'claim still open: got {rc}: {o}')
    return fails


def ticket_file(tid, branch=None, claimed=False):
    cb = 'claimed_by: claude 2026-10-11\n' if claimed else ''
    br = f'branch: {branch}\n' if branch else ''
    return (f'---\nid: {tid}\ntitle: "Ticket {tid}"\ntype: feature\nstatus: {"claimed" if claimed else "ready"}\n'
            f'size: L1\npriority: P2\ndepends: []\ncreated: 2026-10-11\n{cb}{br}---\n\nbody\n')


def case_branch_list(script, base):
    """T-0530: a manual worktree joins its ticket by `branch:`, with the newest verifier verdict; no line, no join."""
    fails = []
    for with_line in (True, False):
        t = Fixture(base, script, 'brlist')
        t.write({'.sdlc/0520-fix/handoff.md': ticket_file('T-0520', 'fix-0520' if with_line else None),
                 '.sdlc/0520-fix/verifier-L2.md': '# verifier\n\n## Verdict\n\npass\n'})
        t.g('worktree', 'add', '-q', '-b', 'fix-0520', str(t.top / '.worktrees' / 'fix-0520'))
        rc, o = t.lanes('list', '--all', '--json')
        try:
            rows = [r for r in json.loads(o) if r['branch'] == 'fix-0520']
        except ValueError:
            rows = []
        got = [(r['owner'], r.get('ticket'), r.get('verdict')) for r in rows]
        want = [('manual', 'T-0520', 'pass')] if with_line else [('manual', None, None)]
        if rc or got != want:
            fails.append(f'branch list ({"with" if with_line else "without"} branch:): want {want}, got {rc}: {got} {o[:300]}')
    return fails


def case_branch_record(script, base):
    """T-0530: open --kind solo --ticket writes `branch: lane/...` on the ticket, close removes it."""
    t = Fixture(base, script, 'brrec')
    h = t.top / '.sdlc' / '0001-one' / 'handoff.md'
    t.write({'.sdlc/0001-one/handoff.md': ticket_file('T-0001', claimed=True)})
    fails = []
    leaf, tree, b = t.open('one', 'T-0001', '--kind', 'solo')
    text = h.read_text()
    if b != 'lane/T-0001-one' or 'claimed_by: claude 2026-10-11\nbranch: lane/T-0001-one\n' not in text:
        fails.append(f'branch record: open did not write branch: {b} after claimed_by: {text!r}')
    if 'branch: lane/T-0001-one\nworktree: ../repo.worktrees/T-0001-one\n' not in text:
        fails.append(f'branch record: open did not write worktree: ../repo.worktrees/T-0001-one after branch: (T-0550, T-0563): {text!r}')
    t.work(tree)
    t.merge(b)
    rc, o = t.lanes('close', leaf)
    if rc or 'branch:' in h.read_text() or 'worktree:' in h.read_text():
        fails.append(f'branch record: close did not remove branch: and worktree: {rc}: {o} {h.read_text()!r}')
    # T-0550: a fanout lane writes both lines too, and its close removes both
    h2 = t.top / '.sdlc' / '0002-two' / 'handoff.md'
    t.write({'.sdlc/0002-two/handoff.md': ticket_file('T-0002', claimed=True)})
    leaf2, tree2, b2 = t.open('two', 'T-0002', '--kind', 'fanout')
    text = h2.read_text()
    if f'branch: {b2}\nworktree: ../repo.worktrees/{leaf2}\n' not in text:
        fails.append(f'branch record: a fanout lane did not write branch: and worktree: {text!r}')
    t.work(tree2)
    t.merge(b2)
    rc, o = t.lanes('close', leaf2)
    if rc or 'branch:' in h2.read_text() or 'worktree:' in h2.read_text():
        fails.append(f'branch record: a fanout close did not remove branch: and worktree: {rc}: {o} {h2.read_text()!r}')
    return fails


def case_open_commits_record(script, base):
    """T-0599: open commits the ticket's branch:/worktree: lines (and the roadmap and router they regenerate) in main, so
    main is clean and a fast-forward settle is not blocked; paths that were already dirty are left alone."""
    t = Fixture(base, script, 'opencommit')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/0001-one/handoff.md': ticket_file('T-0001', claimed=True)})
    t.write({'keep.txt': 'dirty\n'})  # an unrelated tracked change that open must not sweep in
    head0 = t.g('rev-parse', 'HEAD')
    leaf, tree, b = t.open('one', 'T-0001', '--kind', 'solo')
    fails = []
    dirty = [l for l in t.g('status', '--porcelain', '--untracked-files=all').splitlines() if l.strip() != 'M keep.txt']
    if dirty:
        fails.append(f'open commit: main is dirty after open: {dirty}')
    if t.g('rev-parse', 'HEAD') == head0 or f'branch: {b}\nworktree:' not in t.g('show', 'HEAD:.sdlc/0001-one/handoff.md'):
        fails.append('open commit: HEAD does not hold the branch: and worktree: lines')
    if 'keep.txt' in t.g('show', '--name-only', '--format=', 'HEAD').splitlines():
        fails.append('open commit: the unrelated dirty keep.txt was committed')
    t.work(tree)
    return fails


def case_open_dirty_ticket(script, base):
    """T-0599: a ticket handoff already dirty before open (here a staged edit) is not swept into the record commit."""
    t = Fixture(base, script, 'opendirty')
    h = '.sdlc/0001-one/handoff.md'
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n', h: ticket_file('T-0001', claimed=True)})
    t.write({h: ticket_file('T-0001', claimed=True).replace('body\n', 'body\nSTAGED EDIT\n')})
    t.g('add', '--', h)
    rc, o = t.lanes('open', 'one', '--ticket', 'T-0001', '--kind', 'solo')
    fails = []
    if rc:
        return [f'open dirty ticket: open failed: {rc}: {o}']
    if 'STAGED EDIT' in t.g('show', f'HEAD:{h}'):
        fails.append('open dirty ticket: the staged edit was committed by the record commit')
    if f'not committed: {h} (dirty before open); commit it yourself' not in o:
        fails.append(f'open dirty ticket: no not-committed line for the dirty handoff: {o}')
    if 'STAGED EDIT' not in t.g('diff', '--cached', '--', h):
        fails.append('open dirty ticket: the staged edit is no longer staged')
    return fails


def case_open_into_integration(script, base):
    """T-0680: open --into a branch checked out in an integration tree commits the lane record there, not on main; a
    ticket missing from that tree falls back to main and says why."""
    t = Fixture(base, script, 'openinto')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/0001-one/handoff.md': ticket_file('T-0001', claimed=True)})
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    head0, ihead0 = t.g('rev-parse', 'HEAD'), t.g('rev-parse', ib)
    rc, o = t.lanes('open', 'one', '--ticket', 'T-0001', '--kind', 'solo', '--into', ib)
    if rc:
        return [f'open into integration: open failed: {rc}: {o}']
    fails = []
    if t.g('rev-parse', 'HEAD') != head0:
        fails.append(f'open into integration: main moved: {t.g("log", "--oneline", f"{head0}..HEAD")}')
    if t.g('log', '--format=%s', f'{ihead0}..{ib}') != 'T-0001: record lane T-0001-one':
        fails.append(f'open into integration: {ib} lacks the record commit: {t.g("log", "--oneline", f"{ihead0}..{ib}")!r}')
    if 'branch: lane/T-0001-one\nworktree:' not in t.g('show', f'{ib}:.sdlc/0001-one/handoff.md'):
        fails.append('open into integration: the integration tip lacks the branch: and worktree: lines')
    if t.g('status', '--porcelain', cwd=integ) or t.g('status', '--porcelain'):
        fails.append('open into integration: a tree is dirty after open')
    if f'recorded in {os.path.relpath(integ, t.top)}' not in o:
        fails.append(f'open into integration: no recorded in line: {o}')
    # filed on main after the integration branch forked: the record falls back to main
    t.commit('file T-0002', {'.sdlc/0002-two/handoff.md': ticket_file('T-0002', claimed=True)})
    head1 = t.g('rev-parse', 'HEAD')
    rc, o = t.lanes('open', 'two', '--ticket', 'T-0002', '--kind', 'solo', '--into', ib)
    if rc or 'recorded in the main checkout: T-0002 not in' not in o or t.g('rev-parse', 'HEAD') == head1:
        fails.append(f'open into integration: a ticket missing there did not fall back to main: {rc}: {o}')
    return fails


def case_open_into_mergelock(script, base):
    """T-0725: open --into an integration tree waits for the merge.lock fanout.py land holds (the default lanes dir's),
    so the record commit never lands while a land's gates or auto-reset run; once released it commits."""
    t = Fixture(base, script, 'openlock')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/0001-one/handoff.md': ticket_file('T-0001', claimed=True)})
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    ihead0 = t.g('rev-parse', ib)
    ldir = wtroot.default_root(t.top) / 'fanout'
    ldir.mkdir(parents=True, exist_ok=True)
    fails = []
    with open(ldir / 'merge.lock', 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            p = subprocess.Popen([sys.executable, str(script), 'open', 'one', '--ticket', 'T-0001', '--kind', 'solo',
                                  '--into', ib], cwd=str(t.top), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            try:
                p.wait(timeout=6)
                fails.append(f'open into mergelock: open finished while merge.lock was held: {p.returncode}: {p.stdout.read()}')
            except subprocess.TimeoutExpired:
                pass
            if t.g('rev-parse', ib) != ihead0:
                fails.append(f'open into mergelock: {ib} moved while merge.lock was held')
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    o, _ = p.communicate(timeout=300)
    if p.returncode or t.g('log', '--format=%s', f'{ihead0}..{ib}') != 'T-0001: record lane T-0001-one':
        fails.append(f'open into mergelock: once released want the record committed in {ib}: {p.returncode}: {o}')
    return fails


def case_close_integration_record(script, base):
    """T-0695: close clears the branch: and worktree: lines in the integration tree that open wrote them in (T-0680), and
    commits that there; main does not move."""
    t = Fixture(base, script, 'closeinto')
    h = '.sdlc/0001-one/handoff.md'
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n', h: ticket_file('T-0001', claimed=True)})
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    leaf, tree, b = t.open('one', 'T-0001', '--kind', 'solo', '--into', ib)
    t.work(tree)
    t.g('merge', '--no-ff', '-q', '-m', f'merge {b}', f'refs/heads/{b}', cwd=integ)
    head0, ihead0 = t.g('rev-parse', 'HEAD'), t.g('rev-parse', ib)
    rc, o = t.lanes('close', leaf)
    if rc:
        return [f'close integration record: close failed: {rc}: {o}']
    fails = []
    text = (integ / h).read_text()
    if 'branch:' in text or 'worktree:' in text:
        fails.append(f'close integration record: the integration ticket still holds branch: or worktree: {text!r}')
    if t.g('rev-parse', 'HEAD') != head0:
        fails.append(f'close integration record: main moved: {t.g("log", "--oneline", f"{head0}..HEAD")}')
    if t.g('log', '--format=%s', f'{ihead0}..{ib}') != 'T-0001: clear lane record ' + leaf:
        fails.append(f'close integration record: {ib} lacks the clear commit: {t.g("log", "--oneline", f"{ihead0}..{ib}")!r}')
    if t.g('status', '--porcelain', cwd=integ):
        fails.append('close integration record: the integration tree is dirty after close')
    return fails


def case_close_done_in_integration(script, base):
    """T-0769 (#77): a ticket closed on the integration branch (status done there, still claimed in main) is not
    reported `ticket still open` by the close that lands its lane; a ticket still open in the integration tree is."""
    t = Fixture(base, script, 'closedone')
    h, h2 = '.sdlc/0001-one/handoff.md', '.sdlc/0002-two/handoff.md'
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n', h: ticket_file('T-0001', claimed=True),
                             h2: ticket_file('T-0002', claimed=True)})
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    leaf, tree, b = t.open('one', 'T-0001', '--kind', 'solo', '--into', ib)
    leaf2, tree2, b2 = t.open('two', 'T-0002', '--kind', 'solo', '--into', ib)
    for tr, br in ((tree, b), (tree2, b2)):
        t.work(tr)
        t.g('merge', '--no-ff', '-q', '-m', f'merge {br}', f'refs/heads/{br}', cwd=integ)
    t.commit('close T-0001', {h: (integ / h).read_text().replace('status: claimed', 'status: done')}, cwd=integ)
    if 'status: claimed' not in (t.top / h).read_text():
        return ['close done in integration: main already reads the ticket as done']
    fails = []
    rc, o = t.lanes('close', leaf)
    if rc or 'ticket still open: T-0001' in o.splitlines():
        fails.append(f'close done in integration: T-0001 is done in {ib} but close reported it open: {rc}: {o}')
    rc, o = t.lanes('close', leaf2)
    if rc or 'ticket still open: T-0002' not in o.splitlines():
        fails.append(f'close done in integration: T-0002 is open in {ib} but close did not say so: {rc}: {o}')
    return fails


def case_open_upstream(script, base):
    """T-0609: in a main that tracks an upstream (a repo landing by PR), open commits nothing on main and leaves it
    clean, so main stays fast-forwardable to origin."""
    t = Fixture(base, script, 'openupstream')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/0001-one/handoff.md': ticket_file('T-0001', claimed=True)})
    t.g('push', '-q', '-u', 'origin', 'main')
    rc, o = t.lanes('open', 'one', '--ticket', 'T-0001', '--kind', 'solo')
    if rc:
        return [f'open upstream: open failed: {rc}: {o}']
    fails = []
    ahead = t.g('rev-list', 'origin/main..main')
    if ahead:
        fails.append(f'open upstream: main has commits origin lacks: {ahead.split()}')
    dirty = t.g('status', '--porcelain')
    if dirty:
        fails.append(f'open upstream: main is dirty after open: {dirty!r}')
    if 'not recorded: main tracks origin/main' not in o:
        fails.append(f'open upstream: no not recorded line: {o}')
    return fails


def case_open_local_finish(script, base):
    """T-0609: a main with no upstream (a repo landing locally) keeps the T-0599 record commit, so main is clean after
    open with no commit of its own, and finish lands and closes."""
    t = Fixture(base, script, 'openlocal')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/0001-fin/handoff.md': ticket_file('T-0001', claimed=True)})
    leaf, tree, b = t.open('fin', 'T-0001', '--kind', 'solo')
    fails = []
    if t.g('status', '--porcelain'):
        fails.append(f'open local: main is dirty after open: {t.g("status", "--porcelain")!r}')
    if f'branch: {b}' not in t.g('show', 'HEAD:.sdlc/0001-fin/handoff.md'):
        fails.append('open local: main HEAD does not hold the branch: line')
    t.work(tree, {'fin.txt': 'work\n'})
    rd = order.records_dir(tree / '.sdlc' / '0001-fin', create=True)
    (rd / 'verifier-L2.md').write_text(FIN_VERDICT.format('pass'))
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    if rc or f'finish: {leaf} done' not in o:
        fails.append(f'open local: finish wants exit 0 and done, got {rc}: {o}')
    if finish_state(t, b, leaf) != ('done', False, False, False):
        fails.append(f'open local: want (done, no tree, no branch, no finish branch), got {finish_state(t, b, leaf)}')
    if t.g('status', '--porcelain'):
        fails.append(f'open local: main is left dirty after finish: {t.g("status", "--porcelain")!r}')
    return fails


def case_pr_ref(script, base):
    t = Fixture(base, script, 'prref')
    leaf, tree, b = t.open('pr/1', None, '--kind', 'integration')
    t.work(tree)
    t.merge(b)
    t.g('update-ref', 'refs/remotes/pr/1', t.g('rev-parse', 'HEAD'))
    rc, o = t.lanes('close', 'pr/1')
    fails = [] if rc == 0 and o == f'closed {leaf} (ancestor)' else [f'case pr ref: got {rc}: {o}']
    if t.ok('rev-parse', '--verify', 'refs/heads/pr/1') or not t.ok('rev-parse', '--verify', 'refs/remotes/pr/1'):
        fails.append('case pr ref: want only the local branch gone')
    return fails


def case_bare_root(script, base):
    """T-0561: in a bare clone (lanes beside the bare dir) the default lanes root and the runner tmp dir sit outside the lane."""
    t = Fixture(base, script, 'bare')
    fails = []
    kit = t.dir / 'kit'
    t.sh(['git', 'clone', '-q', '--bare', str(t.top), str(kit / '.bare')], t.dir)
    lane = Path(os.path.realpath(str(kit))) / 'lanes' / 'a'
    t.sh(['git', 'worktree', 'add', '-q', '--detach', str(lane), 'HEAD'], kit / '.bare')
    ctx = Ctx(lane)
    if ctx.root != lane.parent or plain_under(ctx.root, lane):
        fails.append(f'bare: the default lanes root from a lane is {ctx.root}, want {lane.parent}')
    if not any(samepath(d, lane.parent / 'tmp') for d in tmp_dirs(ctx.top)):
        fails.append(f'bare: the runner tmp dirs {tmp_dirs(ctx.top)} miss {lane.parent / "tmp"}')
    return fails


def case_sibling_root(script, base):
    """T-0563: a normal repo's default lanes root is the sibling <parent>/<name>.worktrees, outside the main checkout,
    from the main checkout and from a lane alike; a lane opens there; .claude/worktrees is read as legacy."""
    t = Fixture(base, script, 'sib')
    t.ticket(7, 'Seven', claimed=True)
    sib = Path(os.path.realpath(str(t.dir))) / 'repo.worktrees'
    fails = []
    ctx = Ctx(t.top)
    if ctx.root != sib or plain_under(ctx.root, t.top):
        fails.append(f'sibling: the default lanes root is {ctx.root}, want {sib} outside {t.top}')
    leaf, tree, _ = t.open('a', 'T-7')
    if not samepath(tree.parent, sib):
        fails.append(f'sibling: open made {tree}, want it directly under {sib}')
    elif Ctx(tree).root != sib:
        fails.append(f'sibling: the lanes root from the lane is {Ctx(tree).root}, want {sib}')
    if not any(samepath(d, sib / 'tmp') for d in tmp_dirs(t.top)) or \
            not any(samepath(d, t.top / '.claude' / 'worktrees' / 'tmp') for d in tmp_dirs(t.top)):
        fails.append(f'sibling: the runner tmp dirs {tmp_dirs(t.top)} miss {sib / "tmp"} or the legacy .claude/worktrees/tmp')
    old = t.top / '.claude' / 'worktrees' / 'h9'
    t.g('worktree', 'add', '-q', '-b', 'worktree-h9', str(old))
    t.write({'.claude/worktrees/host/h9.lane.json': json.dumps(dict(lane='h9', kind='host', branch='worktree-h9', into='main'))})  # legacy
    d = next((x for x in discover(Ctx(t.top)) if x['lane'] == 'h9'), None)
    if not d or d['owner'] != 'host':
        fails.append(f'sibling: a legacy host record under .claude/worktrees/host was not read: {d}')
    rc, o = t.lanes('check')
    if 'C1' in o:
        fails.append(f'sibling: check flags a lane under the sibling root or a legacy one: {rc}: {o}')
    return fails


def case_open_path(script, base):
    t = Fixture(base, script, 'opath')
    t.ticket(5, 'Five')
    tree = t.top / '.worktrees' / 'fan' / 'alpha'
    args = ('open', 'alpha', '--ticket', 'T-5', '--path', str(tree), '--branch', 'wave1-alpha')
    fails = []
    rc, o = t.lanes(*args)
    if rc != 1 or o != 'ticket T-5 not claimed: set claimed_by: first' or tree.exists() or t.ok('rev-parse', '--verify', 'refs/heads/wave1-alpha'):
        fails.append(f'open path: without --no-claim want the claim refusal and nothing made, got {rc}: {o}')
    rc, o = t.lanes(*args, '--no-claim')
    rec = read_json(tree / RECORD) or {}
    if rc or f'opened alpha at {tree} (branch wave1-alpha, into main)' not in o:
        fails.append(f'open path: --no-claim did not open at the path: {rc}: {o}')
    if (rec.get('lane'), rec.get('branch'), rec.get('kind'), rec.get('tickets')) != ('alpha', 'wave1-alpha', 'fanout', ['T-5']) or \
            t.g('rev-parse', '--abbrev-ref', 'HEAD', cwd=tree) != 'wave1-alpha':
        fails.append(f'open path: want the tree on wave1-alpha with its record, got {rec}')
    if t.g('config', '--get', 'branch.wave1-alpha.description') != 'T-5 Five':
        fails.append('open path: the description lacks the ticket title')
    return fails


def case_local_settings(script, base):
    t = Fixture(base, script, 'lset')
    t.ticket(6, 'Six', claimed=True)
    t.write({'.claude/settings.local.json': '{"permissions": {"allow": ["Bash(ls:*)"]}}\n', '.claude/other.json': 'x\n'})
    fails = []
    leaf, wt, _ = t.open('a', 'T-6')
    f, o = wt.joinpath('.claude', 'settings.local.json'), wt.joinpath('.claude', 'other.json')
    if not f.is_file() or f.read_bytes() != t.top.joinpath('.claude', 'settings.local.json').read_bytes():
        fails.append('local settings: want the ignored settings file in the lane, byte for byte')
    if o.exists():
        fails.append('local settings: another ignored file was copied')
    return fails


def case_local_settings_unignored(script, base):
    """T-0724: in a repo that does not ignore .claude/settings.local.json, a lane's `git add -A` never stages it."""
    t = Fixture(base, script, 'lsetx')
    t.commit('unignore', {'.gitignore': '.worktrees/\n.sdlc/\n'})
    t.ticket(6, 'Six', claimed=True)
    t.write({'.claude/settings.local.json': '{"permissions": {"allow": ["Bash(ls:*)"]}}\n'})
    fails = []
    leaf, wt, _ = t.open('a', 'T-6')
    if not wt.joinpath('.claude', 'settings.local.json').is_file():
        fails.append('local settings unignored: want the settings file copied into the lane')
    t.write({'new.txt': 'n\n'}, cwd=wt)
    t.g('add', '-A', cwd=wt)
    staged = t.g('diff', '--cached', '--name-only', cwd=wt).splitlines()
    if staged != ['new.txt']:
        fails.append(f'local settings unignored: git add -A in the lane want only new.txt staged, got {staged}')
    return fails


def case_lane_setup(script, base):
    """T-0692: two lane_setup: lines both run in order in the new tree; a failing first line records failed and skips the second."""
    t = Fixture(base, script, 'lsetup')
    t.ticket(7, 'Seven', claimed=True)
    t.write({'.sdlc/config': 'lane_setup: echo one >> marker.txt\nlane_setup: echo two >> marker.txt\n'})
    fails = []
    leaf, wt, _ = t.open('a', 'T-7')
    marker = wt / 'marker.txt'
    got = marker.read_text().split() if marker.is_file() else None
    rec = read_json(wt / RECORD) or {}
    if got != ['one', 'two'] or rec.get('setup') != 'ok':
        fails.append(f'lane_setup: two lines want marker [one, two] and setup ok, got {got} and {rec.get("setup")!r}')
    rc, o = t.lanes('open', 'b', '--ticket', 'T-7', '--root', '.none')
    if rc or 'setup: ok' not in o.splitlines():
        fails.append(f'lane_setup: a successful open want a setup: ok line, got {rc}: {o}')
    t.write({'.sdlc/config': 'lane_setup: echo first >> marker.txt; exit 3\nlane_setup: echo second >> marker.txt\n'})
    rc, o = t.lanes('open', 'c', '--ticket', 'T-7', '--root', '.none')
    m = re.search(r'opened (\S+) at (.+?) \(branch', o)
    wc = Path(m.group(2)) if m else None
    got = wc.joinpath('marker.txt').read_text().split() if wc and wc.joinpath('marker.txt').is_file() else None
    rec = read_json(wc / RECORD) if wc else {}
    want = 'failed rc=3 (echo first >> marker.txt; exit 3)'
    if rc or got != ['first'] or (rec or {}).get('setup') != want or f'setup: {want}' not in o.splitlines():
        fails.append(f'lane_setup: a failing first line want marker [first], the lane kept and {want!r}, got {rc} {got} {(rec or {}).get("setup")!r}: {o}')
    return fails


def case_node_modules(script, base):
    """T-0773 (#81): .gitignore's `node_modules/` does not match a symlink, so a lane's commit and close must leave a
    node_modules symlink alone; open warns when package.json exists and lane_setup: is unset, and is quiet when it is set."""
    t, leaf, tree, b = finish_fixture(script, base, 'nodemod', gate='test -e fin2.txt')
    t.commit('ignore node_modules', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\nnode_modules/\n'})
    (tree / 'node_modules').symlink_to(t.top)  # added by hand to the lane, as in the report
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    fails = [] if rc == 0 else [f'node_modules: finish want exit 0, got {rc}: {o}']
    if t.ok('cat-file', '-e', 'main:node_modules') or not t.ok('cat-file', '-e', 'main:fin2.txt'):
        fails.append('node_modules: want main with the committed fin2.txt and no node_modules symlink')
    t2 = Fixture(base, script, 'nodemod-open')
    t2.ticket(7, 'Seven', claimed=True)
    t2.commit('pkg', {'package.json': '{}\n'})
    rc, o = t2.lanes('open', 'a', '--ticket', 'T-7', '--root', '.none')
    if rc or 'note: package.json but no lane_setup:' not in o:
        fails.append(f'node_modules: open with package.json and no lane_setup want the note, got {rc}: {o}')
    t2.write({'.sdlc/config': 'lane_setup: true\n'})
    rc, o = t2.lanes('open', 'b', '--ticket', 'T-7', '--root', '.none')
    if rc or 'no lane_setup' in o:
        fails.append(f'node_modules: open with lane_setup set want no note, got {rc}: {o}')
    return fails


def case_host_record(script, base):
    t = Fixture(base, script, 'hostrec')
    t.write({'.sdlc/config': 'lane_ports: 47110-47130\n'})
    fails = []
    os.environ['SDLC_RUN_ID'] = 'run-h1'
    try:
        host_record('h1', 'worktree-h1', 'wave/1', ['T-9'], cwd=str(t.top))
        rec = host_record('h1', 'worktree-h1', 'wave/2', ['T-9'], cwd=str(t.top))
    finally:
        os.environ.pop('SDLC_RUN_ID', None)
    hp = wtroot.default_root(t.top) / 'host' / 'h1.lane.json'
    disk = read_json(hp) or {}
    want = dict(lane='h1', kind='host', branch='worktree-h1', base='main', base_sha=t.g('rev-parse', 'main'), into='wave/2',
                tickets=['T-9'], run_id='run-h1', setup=None)
    if set(disk) != set(FIELDS) or disk != rec or any(disk.get(k) != v for k, v in want.items()) or \
            not isinstance(disk.get('port'), int) or not disk.get('opened'):
        fails.append(f'host record: want every field with kind host and the second into, got {disk}')
    d = next((x for x in discover(Ctx(t.top)) if x['lane'] == 'h1'), None)
    if not d or d['owner'] != 'host' or d['kind'] != 'host' or d['branch'] != 'worktree-h1' or d['into'] != 'wave/2':
        fails.append(f'host record: discover did not read it: {d}')
    return fails


def case_host_owned(script, base):
    """T-0564: a Codex tree under ~/.codex/worktrees and a host-owned .claude/worktrees/agent-x tree, both landed (agent-x
    with a host record, which sweep closed before), are named host-owned and never closed by sweep."""
    t = Fixture(base, script, 'hostown')
    home = Path(os.path.realpath(str(t.dir))) / 'home'
    codex = home / '.codex' / 'worktrees' / 'ab12' / 'repo'
    agent = t.top / '.claude' / 'worktrees' / 'agent-x'
    for tree, br in ((codex, 'codex-x'), (agent, 'worktree-agent-x')):
        t.g('worktree', 'add', '-q', '-b', br, str(tree))
        t.work(tree)
        t.merge(br)
    t.write({str(t.tree('host') / 'agent-x.lane.json'): json.dumps(dict(lane='agent-x', kind='host', branch='worktree-agent-x',
                                                                       into='main'))})
    rc, dry = t.lanes('sweep', env={'HOME': str(home)})
    rc2, o = t.lanes('sweep', '--apply', env={'HOME': str(home)})
    fails = []
    for tree, host in ((codex, 'Codex'), (agent, 'Claude Code')):
        line = f'kept {tree}: host-owned ({host})'
        if line not in dry.splitlines() or line not in o.splitlines():
            fails.append(f'host-owned tree listed without its host-owned line {line!r}: {dry} || {o}')
    if 'agent-x (' in dry + o or not codex.is_dir() or not agent.is_dir() or rc or rc2:
        fails.append(f'host-owned tree listed for removal or removed: rc {rc}/{rc2}: {dry} || {o}')
    return fails


def case_host_landed_integration(script, base):
    """T-0743 (GitHub #71): a host-owned .claude/worktrees/agent-x tree with a host record into the integration branch, its
    branch merged there, does not hold the integration tree open: close removes the integration tree, keeps agent-x and
    prints the git worktree remove line for it. An unmerged agent-y, or agent-x with a modified file, still holds it open."""
    t = Fixture(base, script, 'hostinteg')
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    agents = {}
    for leaf in ('agent-x', 'agent-y'):
        tree = t.top / '.claude' / 'worktrees' / leaf
        t.g('worktree', 'add', '-q', '-b', f'worktree-{leaf}', str(tree), ib)
        t.work(tree)
        t.write({str(t.tree('host') / f'{leaf}.lane.json'): json.dumps(dict(lane=leaf, kind='host', branch=f'worktree-{leaf}',
                                                                          into=ib))})
        agents[leaf] = tree
    t.g('merge', '--no-ff', '-q', '-m', 'merge agent-x', 'refs/heads/worktree-agent-x', cwd=integ)
    rc, o = t.lanes('close', ib, '--into', 'main')
    fails = [] if rc == 1 and o == f'lanes still open into {ib}: agent-y' else [f'host landed: want agent-y alone open, got {rc}: {o}']
    t.g('worktree', 'remove', '--force', str(agents['agent-y']))
    t.g('branch', '-D', 'worktree-agent-y')
    t.g('merge', '-q', '--ff-only', f'refs/heads/{ib}')
    dirty = agents['agent-x'] / 'f-agent-x.txt'
    dirty.write_text('changed\n')
    rc, o = t.lanes('close', ib, '--into', 'main')
    if rc != 1 or o != f'lanes still open into {ib}: agent-x' or not integ.is_dir():
        fails.append(f'host landed: a merged agent-x with a modified file must hold it open, got {rc}: {o}')
    dirty.write_text('x\n')
    rc, o = t.lanes('close', ib, '--into', 'main')
    line = f'host-owned {agents["agent-x"]} landed in {ib}; remove it yourself: git worktree remove {agents["agent-x"]}'
    if rc or line not in o.splitlines() or integ.exists():
        fails.append(f'host landed: want the integration tree closed and {line!r}, got {rc}: {o}')
    if not agents['agent-x'].is_dir():
        fails.append('host landed: the host-owned agent-x tree was removed')
    return fails


def case_host_removed_integration(script, base):
    """T-0762: a host record whose .claude/worktrees/agent-z tree was removed after its branch landed does not hold the
    integration tree open: close removes the integration tree and prints the remove line for the landed agent-x tree
    still present, and none for agent-z."""
    t = Fixture(base, script, 'hostgone')
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    agents = {}
    for leaf in ('agent-x', 'agent-z'):
        tree = t.top / '.claude' / 'worktrees' / leaf
        t.g('worktree', 'add', '-q', '-b', f'worktree-{leaf}', str(tree), ib)
        t.work(tree)
        t.write({str(t.tree('host') / f'{leaf}.lane.json'): json.dumps(dict(lane=leaf, kind='host', branch=f'worktree-{leaf}',
                                                                          into=ib))})
        t.g('merge', '--no-ff', '-q', '-m', f'merge {leaf}', f'refs/heads/worktree-{leaf}', cwd=integ)
        agents[leaf] = tree
    t.g('worktree', 'remove', '--force', str(agents['agent-z']))
    t.g('merge', '-q', '--ff-only', f'refs/heads/{ib}')
    rc, o = t.lanes('close', ib, '--into', 'main')
    line = f'host-owned {agents["agent-x"]} landed in {ib}; remove it yourself: git worktree remove {agents["agent-x"]}'
    if rc or line not in o.splitlines() or 'agent-z' in o or integ.exists():
        return [f'host removed: want the integration tree closed, {line!r} and no agent-z line, got {rc}: {o}']
    return []


def case_host_removed_unmerged(script, base):
    """T-0762 verifier control: a host record whose tree was removed but whose branch is NOT an ancestor of the
    integration branch still holds the integration tree open (unmerged work is never orphaned)."""
    t = Fixture(base, script, 'hostgoneun')
    _, integ, ib = t.open('wave/1', None, '--kind', 'integration')
    tree = t.top / '.claude' / 'worktrees' / 'agent-z'
    t.g('worktree', 'add', '-q', '-b', 'worktree-agent-z', str(tree), ib)
    t.work(tree)
    t.write({str(t.tree('host') / 'agent-z.lane.json'): json.dumps(dict(lane='agent-z', kind='host',
                                                                       branch='worktree-agent-z', into=ib))})
    t.g('worktree', 'remove', '--force', str(tree))
    rc, o = t.lanes('close', ib, '--into', 'main')
    if rc != 1 or o != f'lanes still open into {ib}: agent-z' or not integ.is_dir():
        return [f'host removed unmerged: want agent-z alone holding the integration tree open, got {rc}: {o}']
    return []


def case_sweep_other_repo(script, base):
    """T-0764: the sweep run from repo A names an unmarked scratch folder of A (one line for several) and none of repo B's;
    B's folder is kept."""
    t = Fixture(base, script, 'sweepother')
    tmpd = Path(base) / 'sweepother-tmp'
    shutil.rmtree(tmpd, ignore_errors=True)  # a mutant run reuses base
    mine = tmpd / 'sdlc' / wtroot.repo_key(t.top)
    theirs = tmpd / 'sdlc' / 'other-deadbeef'
    for d in (mine / 'probe-a', theirs / 'probe-b', theirs / 'probe-c'):
        d.mkdir(parents=True)
    env = {'TMPDIR': str(tmpd)}
    fails = []
    for args in (('sweep',), ('sweep', '--apply')):
        rc, o = t.lanes(*args, env=env)
        got = [x for x in o.splitlines() if 'unmarked' in x]
        if rc or got != [f'unmarked: {mine / "probe-a"}']:
            fails.append(f'sweep other repo {args}: want one unmarked line for this repo only, got {rc}: {o}')
    (mine / 'probe-d').mkdir()
    rc, o = t.lanes('sweep', env=env)
    got = [x for x in o.splitlines() if 'unmarked' in x]
    if rc or len(got) != 1 or not got[0].startswith('unmarked: 2 folders, first ') or 'other-deadbeef' in o:
        fails.append(f'sweep other repo: want one summary line for two folders, got {rc}: {o}')
    if not all(d.is_dir() for d in (theirs / 'probe-b', theirs / 'probe-c', mine / 'probe-a')):
        fails.append('sweep other repo: an unmarked folder was deleted')
    return fails


def case_lock(script, base):
    """T-0589: open locks the tree with its owner (the claim ref holder, else claimed_by) and the ticket; list shows the
    lane with no commits as running, not closable; sweep --apply keeps it; close --discard refuses it; a plain close
    unlocks and closes it; an explicit unlock lets close --discard close a dirty lane."""
    t = Fixture(base, script, 'lock')
    t.ticket(77, 'owned lane', claimed=True)
    t.ticket(78, 'unlocked by hand', claimed=True)
    blob = subprocess.run(['git', 'hash-object', '-w', '--stdin'], cwd=str(t.top), input='codex:s1 2026-10-15\n',
                          capture_output=True, text=True).stdout.strip()
    t.g('update-ref', 'refs/sdlc/claims/T-77', blob)
    own = t.open('own', 'T-77', keep_lock=True)
    dis = t.open('dis', 'T-78', keep_lock=True)
    fails = []
    wl = t.g('worktree', 'list', '--porcelain')
    for tree, reason in ((own[1], 'codex:s1 T-77'), (dis[1], 'claude T-78')):
        if f'worktree {tree}\n' not in wl + '\n' or f'locked {reason}' not in wl:
            fails.append(f'lock: open did not lock {tree.name} with {reason!r}: {wl}')
    rc, o = t.lanes('list', '--json')
    try:
        rows = {r['lane']: r for r in json.loads(o)}
    except ValueError:
        return fails + [f'lock: list --json is not JSON: {o}']
    r = rows.get(own[0]) or {}
    if r.get('state') != 'running (codex:s1 T-77)' or 'closable' in (r.get('states') or []):
        fails.append(f'lock: want {own[0]} running (codex:s1 T-77), not closable; got {r.get("state")!r}')
    rc, o = t.lanes('sweep', '--apply')
    if rc or f'kept {own[0]}: locked: codex:s1 T-77' not in o.splitlines() or not own[1].is_dir():
        fails.append(f'lock: sweep --apply did not keep the locked lane: {rc}: {o}')
    rc, o = t.lanes('close', own[0], '--discard')
    if rc != 1 or o != 'locked: codex:s1 T-77' or not own[1].is_dir():
        fails.append(f'lock: close --discard of a locked lane did not refuse: {rc}: {o}')
    rc, o = t.lanes('close', own[0])
    if rc or f'closed {own[0]} (ancestor)' not in o.splitlines() or own[1].exists() or str(own[1]) in t.g('worktree', 'list'):
        fails.append(f'lock: close did not unlock and close the lane it locked: {rc}: {o}')
    (dis[1] / 'keep.txt').write_text('edited\n')
    t.g('worktree', 'unlock', str(dis[1]))
    rc, o = t.lanes('close', dis[0], '--discard')
    if rc or f'closed {dis[0]} (discarded' not in o or dis[1].exists():
        fails.append(f'lock: close --discard after an explicit unlock did not close: {rc}: {o}')
    return fails


def case_ready(script, base):
    """T-0590: ready refuses an unchanged lane and a ticket with no criteria; on uncommitted work it pins a snapshot
    commit holding it (index and stash untouched), unlocks the lane and mails the factory; list --ready shows the
    row, stale once the lane is edited; close deletes the ref."""
    t = Fixture(base, script, 'ready')
    crit = '\n## Acceptance criteria\n1. `true` exits 0.\n'
    t.ticket(90, 'ready lane', claimed=True)
    t.ticket(91, 'no criteria', claimed=True)
    hp = t.top / '.sdlc' / '0090-t' / 'handoff.md'
    hp.write_text(hp.read_text() + crit)
    reg = subprocess.run([sys.executable, str(HERE / 'messages.py'), 'register', '--name', 'factory', '--harness', 'claude'],
                         cwd=str(t.top), capture_output=True, text=True)
    if reg.returncode:
        return [f'ready: cannot register the factory: {reg.stderr}']
    lane, tree, _ = t.open('rdy', 'T-90', keep_lock=True)
    bare, btree, _ = t.open('bare', 'T-91', keep_lock=True)
    fails, ref = [], 'refs/sdlc/ready/T-90'
    inbox = t.top / '.sdlc' / 'messages' / 'new' / 'factory'
    rc, o = t.lanes('ready', lane)
    if rc != 1 or f'no changes in {lane} since' not in o or t.ok('rev-parse', '--verify', '-q', ref) or list(inbox.glob('*.md')):
        fails.append(f'ready: an unchanged lane did not refuse with nothing written: {rc}: {o}')
    (btree / 'keep.txt').write_text('bare\n')
    rc, o = t.lanes('ready', bare)
    if rc != 1 or 'T-91 has no acceptance criteria' not in o or t.ok('rev-parse', '--verify', '-q', 'refs/sdlc/ready/T-91'):
        fails.append(f'ready: a ticket with no acceptance criteria did not refuse: {rc}: {o}')
    (tree / 'keep.txt').write_text('edited\n')
    (tree / 'new.txt').write_text('new\n')
    status = t.g('status', '--porcelain', cwd=tree)
    rc, o = t.lanes('ready', cwd=tree)
    sha = t.g('rev-parse', '--verify', '-q', ref) if t.ok('rev-parse', '--verify', '-q', ref) else ''
    if rc or not sha or f'ready: {ref} {sha}' not in o.splitlines():
        return fails + [f'ready: ready on uncommitted work did not pin {ref}: {rc}: {o}']
    if t.g('show', f'{sha}:new.txt') != 'new' or t.g('show', f'{sha}:keep.txt') != 'edited' \
            or t.g('rev-parse', f'{sha}^1') != t.g('rev-parse', 'HEAD', cwd=tree) \
            or f'Lane-Base: {t.g("rev-parse", "main")}' not in t.g('log', '-1', '--format=%B', sha):
        fails.append(f'ready: the ready sha {sha} is not a snapshot commit of the uncommitted work on the lane HEAD naming its base')
    if t.g('status', '--porcelain', cwd=tree) != status or t.g('stash', 'list'):
        fails.append('ready: the lane index or the stash stack changed')
    if any(b.startswith(f'worktree {tree}\n') and '\nlocked' in b for b in t.g('worktree', 'list', '--porcelain').split('\n\n')):
        fails.append(f'ready: the lane is still locked: {o}')
    msgs = list(inbox.glob('*.md'))
    text = msgs[0].read_text() if len(msgs) == 1 else ''
    if 'topic: ready T-90' not in text or 'kind: handoff' not in text or f'{sha} {tree}' not in text:
        fails.append(f'ready: want one handoff message `ready T-90` carrying the sha and lane path, got {len(msgs)}: {text}')
    rc, o = t.lanes('list', '--ready')
    want = f'T-90  {lane}  {sha}  {tree}'
    if rc or o.splitlines() != [want]:
        fails.append(f'ready: list --ready want {want!r}, got {rc}: {o}')
    (tree / 'new.txt').write_text('changed after ready\n')
    rc, o = t.lanes('list', '--ready')
    if rc or o.splitlines() != [want + '  stale']:
        fails.append(f'ready: an edit after ready did not show stale: {rc}: {o}')
    rc, o = t.lanes('close', lane, '--discard')
    if rc or t.ok('rev-parse', '--verify', '-q', ref):
        fails.append(f'ready: close did not delete {ref}: {rc}: {o}')
    return fails


def case_ready_unregistered(script, base):
    """T-0610: in a repo whose factory mailbox is not registered, ready on uncommitted work pins the ref, unlocks the
    lane, prints a warning naming `lanes.py list --ready` and `messages.py register --name factory`, and exits 0."""
    t = Fixture(base, script, 'readyun')
    t.ticket(92, 'unregistered', claimed=True)
    hp = t.top / '.sdlc' / '0092-t' / 'handoff.md'
    hp.write_text(hp.read_text() + '\n## Acceptance criteria\n1. `true` exits 0.\n')
    lane, tree, _ = t.open('unreg', 'T-92', keep_lock=True)
    (tree / 'keep.txt').write_text('edited\n')
    ref = 'refs/sdlc/ready/T-92'
    rc, o = t.lanes('ready', cwd=tree)
    sha = t.g('rev-parse', '--verify', '-q', ref) if t.ok('rev-parse', '--verify', '-q', ref) else ''
    fails = []
    if rc or not sha or f'ready: {ref} {sha}' not in o.splitlines():
        fails.append(f'ready: with no factory registered ready did not exit 0 with {ref} pinned: {rc}: {o}')
    if 'not sent to factory' not in o or 'lanes.py list --ready' not in o or 'messages.py register --name factory' not in o:
        fails.append(f'ready: the unregistered-factory warning does not name list --ready and the register step: {o}')
    if any(b.startswith(f'worktree {tree}\n') and '\nlocked' in b for b in t.g('worktree', 'list', '--porcelain').split('\n\n')):
        fails.append(f'ready: the lane is still locked: {o}')
    if list((t.top / '.sdlc' / 'messages' / 'new' / 'factory').glob('*.md')):
        fails.append('ready: a message reached an unregistered factory')
    return fails


def case_ready_once(script, base):
    """T-0694: with no factory mailbox, two readies in one session print the full warning once and then
    `not sent: no factory mailbox (warned once)`; a new session warns in full again; --notify-cmd runs in the main
    checkout with the ticket, sha and lane path in its environment, prints `notified:`, replaces the warning, and a
    failing command is a warning that leaves the exit code 0."""
    t = Fixture(base, script, 'readyonce')
    t.ticket(93, 'warn once', claimed=True)
    hp = t.top / '.sdlc' / '0093-t' / 'handoff.md'
    hp.write_text(hp.read_text() + '\n## Acceptance criteria\n1. `true` exits 0.\n')
    lane, tree, _ = t.open('once', 'T-93', keep_lock=True)
    (tree / 'keep.txt').write_text('edited\n')
    sess = {'CLAUDE_CODE_SESSION_ID': 'once-a'}
    full, short = 'warning: not sent to factory', 'not sent: no factory mailbox (warned once)'
    fails = []
    rc1, o1 = t.lanes('ready', cwd=tree, env=sess)
    (tree / 'keep.txt').write_text('edited again\n')
    rc2, o2 = t.lanes('ready', cwd=tree, env=sess)
    if rc1 or rc2 or full not in o1 or short in o1 or full in o2 or short not in o2.splitlines():
        fails.append(f'ready once: want the full warning then the short line in one session, got {rc1}: {o1} / {rc2}: {o2}')
    rc3, o3 = t.lanes('ready', cwd=tree, env={'CLAUDE_CODE_SESSION_ID': 'once-b'})
    if rc3 or full not in o3:
        fails.append(f'ready once: a new session did not warn in full: {rc3}: {o3}')
    mark = t.dir / 'notified.txt'
    cmd = f'echo "$SDLC_READY_TICKET $SDLC_READY_SHA $SDLC_READY_PATH $(pwd -P)" > {mark}'
    rc4, o4 = t.lanes('ready', '--notify-cmd', cmd, cwd=tree, env={'CLAUDE_CODE_SESSION_ID': 'once-c'})
    sha = t.g('rev-parse', '--verify', '-q', 'refs/sdlc/ready/T-93')
    want = f'T-93 {sha} {os.path.realpath(tree)} {os.path.realpath(t.top)}'
    if rc4 or f'notified: {cmd} rc=0' not in o4 or full in o4 or short in o4 or not mark.exists() \
            or mark.read_text().strip() != want:
        fails.append(f'ready once: --notify-cmd want {want!r} written and no mailbox warning, got {rc4}: {o4}')
    rc5, o5 = t.lanes('ready', '--notify-cmd', 'exit 3', cwd=tree, env={'CLAUDE_CODE_SESSION_ID': 'once-d'})
    if rc5 or 'notified: exit 3 rc=3' not in o5 or 'warning: --notify-cmd exited 3' not in o5:
        fails.append(f'ready once: a failing --notify-cmd did not warn with exit 0: {rc5}: {o5}')
    return fails


def case_sweep_mergelock(script, base):
    t = Fixture(base, script, 'mlock')
    lanes_dir = t.top / '.worktrees' / 'fanout'
    (lanes_dir / 'logs').mkdir(parents=True)
    mlock = lanes_dir / 'merge.lock'
    mlock.write_text('')
    tree = lanes_dir / 'a'
    t.g('worktree', 'add', '-q', '-b', 'wave1-a', str(tree))
    t.work(tree)
    t.merge('wave1-a')
    fails = []
    with open(mlock, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            rc, o = t.lanes('sweep', '--apply')
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    if rc or 'kept a: merging (merge.lock held)' not in o.splitlines() or not tree.is_dir():
        fails.append(f'sweep merge.lock: with the lock held want the lane kept as merging, got {rc}: {o}')
    rc, o = t.lanes('sweep', '--apply')
    if rc or 'closed a (ancestor)' not in o.splitlines() or tree.exists():
        fails.append(f'sweep merge.lock: once released want the lane closed, got {rc}: {o}')
    return fails


# markers the mutant copies edit; each is joined so the selftest's own text does not contain the marked line
MUTANTS = (
    ('HOST-OWNED', "host = wtroot.host_owned(d0['path'])" + '  # HOST-OWNED', 'host = None  # HOST-OWNED', case_host_owned,
     'host-owned tree listed', 'without the host-owned test sweep lists a Codex or agent-x tree'),
    ('NO-RENAMES', "d = git(cwd, 'diff', '--no-renames', '--name-only', '-z', mb, ref)" + '  # NO-RENAMES',
     "d = git(cwd, 'diff', '--name-only', '-z', mb, ref)" + '  # NO-RENAMES', case_rename, 'rename case closed',
     'the rename case closes without --no-renames'),
    ('DIFF-FAIL', "if m.returncode or d.returncode: " + "return 'cannot decide'", "if False: return 'cannot decide'", case_row5,
     'failed diff', 'a failed diff read as empty closes the row 5 case'),
    ('DIRTY-CHECK', "if dirty and not discard: " + "return '6'", "if False: return '6'", case_row6, 'dirty lane closed',
     'row 6 closes without the dirty check'),
    ('ABSENT-EQUAL', 'if a != b: return ' + "'not landed', p", 'if a and b and a != b: return ' + "'not landed', p",
     case_deleted, 'deleted-file case closed', 'the deleted-file case of row 11 closes'),
    ('ARCHIVE-ZERO', "r = git(top, 'update-ref', ref, tag, zero)" + '  # ARCHIVE-ZERO',
     "r = git(top, 'update-ref', ref, tag)" + '  # ARCHIVE-ZERO', case_archive_twice, 'left one ref',
     'two closes of one name on one date leave one ref'),
    ('ARCHIVE-STOP', "if r.returncode: return None, " + "f'cannot write {ref}", "if False: return None, f'cannot write {ref}",
     case_archive_clash, 'branch be deleted', 'a forced ref directory clash deletes the branch'),
    ('NAME-FIRST', 'refusal = name_refusal(ctx, branch, tree)' + '  # NAME-FIRST',
     'tree.mkdir(parents=True, exist_ok=True); refusal = name_refusal(ctx, branch, tree)' + '  # NAME-FIRST', case_c9,
     'left a directory', 'a C9 refusal leaves a directory'),
    ('DESC-COPY', "head = desc or '(no description)'" + '  # DESC-COPY', "head = '(no description)'" + '  # DESC-COPY',
     case_c13, 'lacks the description', 'the C13 tag message lacks the description'),
    ('READY-STALE', "stale = snapshot(d['path']) != ready_state(ctx.top, sha)" + '  # READY-STALE',
     'stale = False  # READY-STALE', case_ready, 'did not show stale', 'list --ready shows no stale row after an edit'),
    ('REALPATH', 'child, parent = os.path.realpath(str(child)), os.path.realpath(str(parent))' + '  # REALPATH',
     'child, parent = os.path.normpath(str(child)), os.path.normpath(str(parent))' + '  # REALPATH', case_c1_outside,
     'passed a symlinked path', 'C1 passes a symlinked path'),
    ('TICKETS-CSV', "+ [x.strip() for c in (csv or ()) for x in c.split(',')]:" + '  # TICKETS-CSV', ':' + '  # TICKETS-CSV',
     case_tickets_csv, 'tickets csv', '--tickets adds no ticket to the open'),
    ('HOST-GONE', "and landed_and_gone(top, o['path'], o['branch'], b):"
     + '  # HOST-GONE', 'and True:  # HOST-GONE', case_host_removed_unmerged, 'host removed unmerged',
     'without the ancestor test a removed host tree with unmerged work no longer holds the integration tree open'),
    ('SWEEP-MINE', 'if wtroot.mine(p, ctx.top):' + '  # SWEEP-MINE', 'if True:  # SWEEP-MINE', case_sweep_other_repo,
     'sweep other repo', "without the own-repo test the sweep names another repo's unmarked folders"),
)


FIN_ENV = {'SDLC_GATE_SLOTS': '0'}  # the land gate runs bare: no machine-wide gate queue in a selftest
FIN_VERDICT = '<!-- role=verifier level=L2 model=opus effort=high -->\n## Verdict\n{}\n\n## Evidence\nran\n'


def finish_fixture(script, base, label, verdict='pass', gate=None):
    """A repo tracking .sdlc/ (not .sdlc/runtime/) with claimed ticket T-0001 (size L2) and a solo lane on it: one
    commit, one uncommitted file and a verifier result with the given verdict in the lane's records dir."""
    t = Fixture(base, script, label)
    files = {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
             '.sdlc/0001-fin/handoff.md': '---\nid: T-0001\ntitle: "Finish me"\ntype: feature\nstatus: claimed\nsize: L2\n'
                                          'priority: P2\ndepends: []\ncreated: 2026-10-15\nclaimed_by: claude 2026-10-15\n---\n\n'
                                          '## Goal\nfinish\n\n## Acceptance criteria\n1. fin.txt exists\n'}
    if gate:
        files['.sdlc/config'] = f'land_gate: {gate}\n'
    t.commit('track .sdlc', files)
    leaf, tree, b = t.open('fin', 'T-0001', '--kind', 'solo')
    t.g('add', '-A')
    t.commit('claim T-0001')  # open wrote branch: and worktree: into the ticket in main
    t.work(tree, {'fin.txt': 'work\n'})
    t.write({'fin2.txt': 'more\n'}, cwd=tree)
    if verdict:  # None: no result yet (a case prepares its own verifier dispatch)
        rd = order.records_dir(tree / '.sdlc' / '0001-fin', create=True)
        (rd / 'verifier-L2.md').write_text(FIN_VERDICT.format(verdict))
    return t, leaf, tree, b


def finish_state(t, b, leaf):
    """(ticket status in main, lane tree exists, lane branch exists, finish branch exists)."""
    meta = next((m for _, m in tickets.load(t.top / '.sdlc') if m.get('id') == 'T-0001'), {})
    return (meta.get('status'), t.tree(leaf).exists(), t.ok('rev-parse', '--verify', '-q', f'refs/heads/{b}'),
            t.ok('rev-parse', '--verify', '-q', f'refs/heads/finish/{leaf}'))


def origin_has(t, ref):
    return subprocess.run(['git', '--git-dir', str(t.dir / 'origin.git'), 'rev-parse', '--verify', '-q', ref],
                          capture_output=True, text=True).stdout.strip()


def case_finish_pass(script, base):
    t, leaf, tree, b = finish_fixture(script, base, 'finish-pass', gate='test -e fin2.txt')
    rc, o = t.lanes('finish', leaf, '--backup', 'origin/backup-main', env=FIN_ENV)
    fails = [] if rc == 0 else [f'finish pass: want exit 0, got {rc}: {o}']
    for want in ('record: nothing pending', 'verdict: pass (verifier-L2.md)', 'commit: ', 'land: merged ', '(gate: test -e fin2.txt)',
                 'settle: main at ', 'close: skipped (T-0001 is done in main)', 'backup: pushing main to origin refs/heads/backup-main in the background',
                 f'lane: closed {leaf} (ancestor)', f'finish: {leaf} done'):
        if want not in o:
            fails.append(f'finish pass: no {want!r} line: {o}')
    if finish_state(t, b, leaf) != ('done', False, False, False):
        fails.append(f'finish pass: want (done, no tree, no branch, no finish branch), got {finish_state(t, b, leaf)}')
    if not (t.ok('cat-file', '-e', 'main:fin.txt') and t.ok('cat-file', '-e', 'main:fin2.txt')):
        fails.append('finish pass: main lacks the lane work (fin.txt and the committed fin2.txt)')
    if wait_origin(t, 'refs/heads/backup-main') != t.g('rev-parse', 'main'):
        fails.append('finish pass: --backup did not push main to origin backup-main')
    if t.g('status', '--porcelain'):
        fails.append(f'finish pass: main is left dirty: {t.g("status", "--porcelain")}')
    rc2, o2 = t.lanes('finish', leaf, env=FIN_ENV)
    if rc2 or 'already finished' not in o2:
        fails.append(f'finish pass: a rerun after the finish wants exit 0 and already finished, got {rc2}: {o2}')
    return fails


def case_finish_resume(script, base):
    t, leaf, tree, b = finish_fixture(script, base, 'finish-resume')
    t.commit('rest', {'fin2.txt': 'more\n'}, cwd=tree)
    tip = t.g('rev-parse', f'refs/heads/{b}')
    t.merge(b)  # the simulated stop: the lane is merged into main, the ticket is not closed, the lane is not removed
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    fails = [] if rc == 0 else [f'finish resume: want exit 0, got {rc}: {o}']
    for want in ('commit: clean', f'land: skipped ({b} is in main)', f'settle: skipped (no finish/{leaf})', 'close: T-0001 done',
                 'backup: none (no --backup)', f'lane: closed {leaf} (ancestor)'):
        if want not in o:
            fails.append(f'finish resume: no {want!r} line: {o}')
    merges = [l for l in t.g('log', '--merges', '--format=%P', 'main').splitlines() if tip in l.split()[1:]]
    if len(merges) != 1:
        fails.append(f'finish resume: want one merge of the lane tip in main, got {len(merges)}')
    if finish_state(t, b, leaf) != ('done', False, False, False):
        fails.append(f'finish resume: want (done, no tree, no branch, no finish branch), got {finish_state(t, b, leaf)}')
    if origin_has(t, 'refs/heads/backup-main'):
        fails.append('finish resume: pushed with no --backup')
    return fails


def case_finish_fail(script, base):
    t, leaf, tree, b = finish_fixture(script, base, 'finish-fail', verdict='fail')
    main0, tip0 = t.g('rev-parse', 'main'), t.g('rev-parse', f'refs/heads/{b}')
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    fails = [] if rc == 1 and 'verdict: stopped: fail (verifier-L2.md); nothing merged' in o else \
        [f'finish fail: want exit 1 and verdict: stopped: fail, got {rc}: {o}']
    if any(f'{s}:' in o for s in ('commit', 'land', 'settle', 'close', 'backup')):
        fails.append(f'finish fail: a step after the verdict ran: {o}')
    if (t.g('rev-parse', 'main'), t.g('rev-parse', f'refs/heads/{b}')) != (main0, tip0):
        fails.append('finish fail: main or the lane branch moved')
    if finish_state(t, b, leaf) != ('claimed', True, True, False) or not (tree / 'fin2.txt').is_file():
        fails.append(f'finish fail: want the ticket claimed and the lane whole, got {finish_state(t, b, leaf)}')
    return fails


def case_finish_ignored(script, base):
    """T-0595: the lane close rewrites a tracked file in an ignored directory (as the live .sdlc/messages/ is); git add
    stages it and exits 1, and finish still commits it, leaving main clean."""
    t, leaf, tree, b = finish_fixture(script, base, 'finish-ignored')
    with (t.top / '.git' / 'info' / 'exclude').open('a') as f:
        f.write('.sdlc/0001-fin/\n')  # the ticket's handoff is tracked, its directory ignored
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    fails = [] if rc == 0 and 'close: skipped (T-0001 is done in main)' in o and f'{leaf} closed)' in o else \
        [f'finish ignored: want exit 0, close skipped and the lane close committed, got {rc}: {o}']
    if t.g('status', '--porcelain'):
        fails.append(f'finish ignored: main is left dirty: {t.g("status", "--porcelain")}')
    return fails


def case_finish_moved(script, base):
    """T-0595: land merged into finish/<lane>, then main moved (a new ticket, so the roadmap conflicts) before settle;
    a finish with no land_gate merges main into finish/<lane> and settles."""
    t, leaf, tree, b = finish_fixture(script, base, 'finish-moved')
    t.commit('rest', {'fin2.txt': 'more\n'}, cwd=tree)
    r = subprocess.run([sys.executable, str(HERE / 'fanout.py'), 'land', b, '--ticket', 'T-0001', '--integration',
                        f'finish/{leaf}', '--lanes-dir', str(t.tree(leaf).parent / 'finish' / leaf), '--base', 'refs/heads/main',
                        '--rewrite-refs', '--lane', 'solo'], cwd=str(t.top), capture_output=True, text=True,
                       env=dict(os.environ, **FIN_ENV))
    if r.returncode:
        return [f'finish moved: fixture land failed: {r.stdout} {r.stderr}']
    t.write({'.sdlc/0002-t/handoff.md': '---\nid: T-0002\ntitle: "Moved on"\ntype: feature\nstatus: ready\nsize: L1\n'
                                        'priority: P2\ndepends: []\ncreated: 2026-10-15\n---\n\nbody\n'})
    t.sh([sys.executable, str(HERE / 'tickets.py'), '--root', '.sdlc', 'roadmap'], t.top)
    t.g('add', '-A')
    t.commit('file T-2')
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    fails = [] if rc == 0 and f'finish: {leaf} done' in o else [f'finish moved: want exit 0 and done, got {rc}: {o}']
    if finish_state(t, b, leaf) != ('done', False, False, False):
        fails.append(f'finish moved: want (done, no tree, no branch, no finish branch), got {finish_state(t, b, leaf)}')
    if not (t.ok('cat-file', '-e', 'main:fin2.txt') and t.ok('cat-file', '-e', 'main:.sdlc/0002-t/handoff.md')):
        fails.append('finish moved: main lacks the lane work or the ticket filed after the land')
    if t.g('status', '--porcelain'):
        fails.append(f'finish moved: main is left dirty: {t.g("status", "--porcelain")}')
    return fails


def case_open_claim(script, base):
    """T-0800: open --claim on a proposed ticket claims it, commits the claim in main and opens the lane in one call."""
    t = Fixture(base, script, 'openclaim')
    h = '.sdlc/0001-one/handoff.md'
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             h: ticket_file('T-0001').replace('status: ready', 'status: proposed')})
    rc, o = t.lanes('open', 'one', '--ticket', 'T-0001', '--kind', 'solo', '--claim', '--by', 'tester')
    if rc:
        return [f'open claim: want exit 0, got {rc}: {o}']
    fails = []
    meta = next((m for _, m in tickets.load(t.top / '.sdlc') if m.get('id') == 'T-0001'), {})
    if meta.get('status') != 'claimed' or not str(meta.get('claimed_by') or '').startswith('tester'):
        fails.append(f'open claim: want status claimed by tester, got {meta.get("status")} {meta.get("claimed_by")}')
    if 'claim T-0001' not in t.g('log', '--format=%s', 'main').splitlines():
        fails.append('open claim: no `claim T-0001` commit in main')
    if 'status: claimed' not in t.g('show', f'main:{h}'):
        fails.append('open claim: main does not hold the claim in a commit')
    if not re.search(r'opened (\S+) at (.+?) \(branch ', o) or not t.tree('T-0001-one').is_dir():
        fails.append(f'open claim: the lane is not open: {o}')
    if t.g('status', '--porcelain'):
        fails.append(f'open claim: main is dirty: {t.g("status", "--porcelain")!r}')
    return fails


def case_open_claim_upstream(script, base):
    """T-0804: with main tracking an upstream, open --claim commits the claim (and the record) only when .sdlc/config
    says `lane_landing: local`; a PR repo (no line) commits nothing on main, as T-0609."""
    fails = []
    for local in (True, False):
        t = Fixture(base, script, 'openclaimup')
        h = '.sdlc/0001-one/handoff.md'
        files = {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                 h: ticket_file('T-0001').replace('status: ready', 'status: proposed')}
        if local:
            files['.sdlc/config'] = 'lane_landing: local\n'
        t.commit('track .sdlc', files)
        t.g('push', '-q', '-u', 'origin', 'main')
        rc, o = t.lanes('open', 'one', '--ticket', 'T-0001', '--kind', 'solo', '--claim', '--by', 'tester')
        m = re.search(r'opened (\S+) at (.+?) \(branch ', o)
        if rc or not m:
            fails.append(f'open claim upstream (local={local}): want exit 0 and an open lane, got {rc}: {o}')
            continue
        claimed = 'claim T-0001' in t.g('log', '--format=%s', 'main').splitlines()
        if local:
            if not claimed:
                fails.append(f'open claim upstream: lane_landing local: no `claim T-0001` commit in main: {o}')
            if 'status: claimed' not in Path(m.group(2), h).read_text():
                fails.append('open claim upstream: lane_landing local: the lane copy is not claimed')
            if t.g('status', '--porcelain'):
                fails.append(f'open claim upstream: lane_landing local: main is dirty: {t.g("status", "--porcelain")!r}')
        else:
            if claimed or t.g('rev-list', 'origin/main..main'):
                fails.append(f'open claim upstream: PR repo: main gained commits origin lacks: {o}')
            if 'claim: not committed: main tracks origin/main' not in o:
                fails.append(f'open claim upstream: PR repo: no not committed line: {o}')
    return fails


def agent_transcript(base, agent_id, text, tools=2, secs=90):
    """A fixture sub-agent transcript under <base>/projects/-p/s/subagents (the SDLC_CLAUDE_PROJECTS layout): tools
    tool_use blocks, usage on each message, secs seconds from the first line to the last, text as the final message."""
    d = base / 'projects' / '-p' / 's' / 'subagents'
    d.mkdir(parents=True, exist_ok=True)
    t0 = datetime.datetime(2026, 10, 28, 12, 0, 0)
    ts = lambda s: (t0 + datetime.timedelta(seconds=s)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    use = {'input_tokens': 10, 'output_tokens': 20, 'cache_read_input_tokens': 100, 'cache_creation_input_tokens': 5}
    lines = [dict(type='user', timestamp=ts(0), message=dict(role='user', content='go'))]
    for i in range(tools):
        lines.append(dict(type='assistant', timestamp=ts(1 + i), message=dict(
            id=f'm{i}', role='assistant', model='claude-sonnet-5-5', usage=use,
            content=[dict(type='tool_use', id=f'tu{i}', name='Bash', input={'command': 'true'})])))
    lines.append(dict(type='assistant', timestamp=ts(secs), message=dict(
        id='mz', role='assistant', model='claude-sonnet-5-5', usage=use, stop_reason='end_turn',
        content=[dict(type='text', text=text)])))
    p = d / f'agent-{agent_id}.jsonl'
    p.write_text(''.join(json.dumps(l) + '\n' for l in lines))
    return p


def case_finish_agent_id(script, base):
    """T-0800: finish --verifier-agent-id finds the verifier transcript, records the result with tokens, tool uses and
    duration from it, drops the verifier from the prune queue, then lands."""
    t, leaf, tree, b = finish_fixture(script, base, 'finish-agent', verdict=None)
    env = dict(FIN_ENV, SDLC_CLAUDE_PROJECTS=str(base / 'projects'), SDLC_DISPATCH_PARENT_PID=str(os.getpid()))
    r = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', 'verifier', 'L2', '.sdlc/0001-fin/handoff.md',
                        '--solo-model', 'sonnet'], cwd=str(tree), capture_output=True, text=True, env=dict(os.environ, **env))
    try:
        got = json.loads(r.stdout)
    except ValueError:
        return [f'finish agent: fixture prepare failed: {r.returncode} {r.stdout} {r.stderr}']
    agent_transcript(base, 'ag-ver', '## Verdict\npass\n\n## Evidence\nran\n')
    sh = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prune', '--root', str(t.top), '--add', got['name']],
                        cwd=str(t.top), capture_output=True, text=True, env=dict(os.environ, **env))
    if sh.returncode:
        return [f'finish agent: fixture prune --add failed: {sh.stdout} {sh.stderr}']
    rc, o = t.lanes('finish', leaf, '--verifier-agent-id', 'ag-ver', env=env)
    fails = [] if rc == 0 and f'finish: {leaf} done' in o else [f'finish agent: want exit 0 and done, got {rc}: {o}']
    for want in ('record: ', f'pruned {got["name"]}', 'verdict: pass', 'land: merged '):
        if want not in o:
            fails.append(f'finish agent: no {want!r} in: {o}')
    rows = []
    for f in (t.top / '.sdlc').rglob('runs.jsonl'):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    v = next((x for x in rows if x.get('role') == 'verifier'), None)
    if not v:
        fails.append(f'finish agent: no verifier row in main runs.jsonl: {rows}')
    else:
        u = v.get('usage') or {}
        if (v.get('agent_id'), u.get('tool_uses'), v.get('duration_ms'), u.get('input_tokens')) != ('ag-ver', 2, 90000, 30):
            fails.append(f'finish agent: want agent ag-ver, 2 tool uses, 90000 ms and 30 input tokens, got {v}')
    queue = t.top / '.sdlc' / 'runtime' / 'prune.json'
    if queue.is_file() and got['name'] in queue.read_text():
        fails.append(f'finish agent: {got["name"]} is still in the prune queue')
    if finish_state(t, b, leaf) != ('done', False, False, False):
        fails.append(f'finish agent: want (done, no tree, no branch, no finish branch), got {finish_state(t, b, leaf)}')
    return fails


def wait_origin(t, ref, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        sha = origin_has(t, ref)
        if sha:
            return sha
        time.sleep(0.2)
    return ''


def case_finish_backup_bg(script, base):
    """T-0800: finish --backup starts the push in a detached process and returns while it still runs, printing the log
    path; a pre-push hook holds the push until the case releases it."""
    t, leaf, tree, b = finish_fixture(script, base, 'finish-bg')
    gate = t.dir / 'release-push'
    hook = t.top / '.git' / 'hooks' / 'pre-push'
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(f'#!/bin/sh\ni=0\nwhile [ ! -e "{gate}" ] && [ $i -lt 600 ]; do sleep 0.1; i=$((i+1)); done\nexit 0\n')
    hook.chmod(0o755)
    rc, o = t.lanes('finish', leaf, '--backup', 'origin/backup-main', env=FIN_ENV)
    fails = [] if rc == 0 and f'finish: {leaf} done' in o else [f'finish bg: want exit 0 and done, got {rc}: {o}']
    if origin_has(t, 'refs/heads/backup-main'):
        fails.append('finish bg: the push completed before finish returned')
    m = re.search(r'^backup: pushing main to origin refs/heads/backup-main in the background; log (\S+)$', o, re.M)
    if not m:
        fails.append(f'finish bg: no background backup line with a log path: {o}')
    gate.write_text('')
    if wait_origin(t, 'refs/heads/backup-main') != t.g('rev-parse', 'main'):
        fails.append('finish bg: the background push never landed main on origin backup-main')
    elif m and not Path(m.group(1)).is_file():
        fails.append(f'finish bg: the log {m.group(1)} does not exist')
    return fails


def case_finish_backup_failed(script, base):
    """T-0802: a background push that exits 1 leaves `exit 1` in the log; the next finish prints `backup: previous push
    failed` and exits nonzero after its work."""
    t, leaf, tree, b = finish_fixture(script, base, 'finish-bgfail')
    hook = t.top / '.git' / 'hooks' / 'pre-push'
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text('#!/bin/sh\nexit 1\n')
    hook.chmod(0o755)
    rc, o = t.lanes('finish', leaf, '--backup', 'origin/backup-main', env=FIN_ENV)
    fails = [] if rc == 0 and 'previous push failed' not in o else [f'finish bgfail: want exit 0 and no failure line on the first finish, got {rc}: {o}']
    m = re.search(r'^backup: pushing main to origin refs/heads/backup-main in the background; log (\S+)$', o, re.M)
    if not m:
        return fails + [f'finish bgfail: no background backup line with a log path: {o}']
    end = time.time() + 60
    while time.time() < end and not Path(m.group(1)).read_text().rstrip().endswith('exit 1'):
        time.sleep(0.2)
    rc, o = t.lanes('finish', leaf, env=FIN_ENV)
    if rc == 0 or f'backup: previous push failed (exit 1), see {m.group(1)}' not in o:
        fails.append(f'finish bgfail: want a nonzero exit and `backup: previous push failed (exit 1), see {m.group(1)}`, got {rc}: {o}')
    if f'finish: {leaf} is already finished' not in o:
        fails.append(f'finish bgfail: the second finish did not report the lane finished: {o}')
    return fails


def case_who(script, base):
    """T-0821: who is none with no factory evidence (a codex receiver and a reader-less one do not count), then factory
    with a live claude receiver whose reader is a factory session."""
    t = Fixture(base, script, 'who')
    now = utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    entry = dict(harness='codex', repo='repo', reader='repo-codex-factory', last_seen=now, expiry='7d')
    reg = {'repo-codex-factory': entry, 'repo-claude-factory': dict(entry, harness='claude', reader='none')}
    t.write({'.sdlc/messages/receivers.json': json.dumps({'receivers': reg})})
    fails = []
    rc, o = t.lanes('who')
    if rc or o != 'none':
        fails.append(f'who: want exit 0 and none, got {rc}: {o}')
    reg['repo-claude-factory'] = dict(entry, harness='claude', reader='factory-session-1')
    t.write({'.sdlc/messages/receivers.json': json.dumps({'receivers': reg})})
    rc, o = t.lanes('who')
    if rc or not o.startswith('factory repo-claude-factory '):
        fails.append(f'who: want exit 0 and factory repo-claude-factory, got {rc}: {o}')
    rc, o = t.lanes('who', '--json')
    try:
        got = json.loads(o)
    except ValueError:
        got = None
    if rc or not got or got.get('who') != 'factory':
        fails.append(f'who --json: want who factory, got {rc}: {o}')
    return fails


def case_overlap(script, base):
    """T-0821: list --overlap names a lane whose diff from its base touches the path (committed or uncommitted), and
    not a lane that does not."""
    t = Fixture(base, script, 'overlap')
    la, ta, _ = t.open('a', 'T-1')
    lb, tb, _ = t.open('b', 'T-2')
    t.work(ta, {'src/a.txt': 'a\n'})
    t.work(tb, {'b.txt': 'b\n'})
    (tb / 'keep.txt').write_text('edited\n')
    fails = []
    rc, o = t.lanes('list', '--overlap', 'src/a.txt', 'keep.txt', 'README')
    want = {f'overlap {la} src/a.txt', f'overlap {lb} keep.txt'}
    if rc or set(o.splitlines()) != want:
        fails.append(f'overlap: want exit 0 and {sorted(want)}, got {rc}: {o}')
    rc, o = t.lanes('list', '--overlap', 'src')
    if rc or o != f'overlap {la} src':
        fails.append(f'overlap: a directory names the lane touching a path under it, got {rc}: {o}')
    return fails


def case_finish_no_ticket(script, base):
    """T-0821: finish --no-ticket lands a ticketless lane through the land gate and closes it; a lane touching a
    hash_bound: path is refused with nothing merged; a lane with a local ticket refuses --no-ticket."""
    t = Fixture(base, script, 'fin-noticket')
    t.commit('track .sdlc', {'.gitignore': '.worktrees/\n.claude/\n.sdlc/runtime/\n',
                             '.sdlc/config': 'land_gate: test -e live.txt\nhash_bound: gen/*\n'})
    leaf, tree, b = t.open('live', None, '--kind', 'integration')
    t.work(tree, {'live.txt': 'live\n'})
    t.write({'live2.txt': 'more\n'}, cwd=tree)
    fails = []
    rc, o = t.lanes('finish', leaf, '--no-ticket', env=FIN_ENV)
    if rc or f'finish: {leaf} done' not in o or '(gate: test -e live.txt)' not in o:
        fails.append(f'finish --no-ticket: want exit 0, the gate and done, got {rc}: {o}')
    if not (t.ok('cat-file', '-e', 'main:live.txt') and t.ok('cat-file', '-e', 'main:live2.txt')):
        fails.append('finish --no-ticket: main lacks the lane work')
    if tree.exists() or t.ok('rev-parse', '--verify', '-q', f'refs/heads/{b}'):
        fails.append('finish --no-ticket: the lane tree or branch is left')
    if t.g('status', '--porcelain'):
        fails.append(f'finish --no-ticket: main is dirty: {t.g("status", "--porcelain")!r}')
    leaf, tree, b = t.open('gen', None, '--kind', 'integration')
    t.work(tree, {'gen/x.json': '{}\n', 'live.txt': 'again\n'})
    head = t.g('rev-parse', 'main')
    rc, o = t.lanes('finish', leaf, '--no-ticket', env=FIN_ENV)
    if rc != 1 or 'hash_bound' not in o or 'gen/x.json' not in o:
        fails.append(f'finish --no-ticket hash_bound: want exit 1 naming gen/x.json, got {rc}: {o}')
    if t.g('rev-parse', 'main') != head or not tree.is_dir():
        fails.append('finish --no-ticket hash_bound: main moved or the lane was closed')
    t.commit('ticket', {'.sdlc/0003-t/handoff.md': ticket_file('T-0003', claimed=True)})
    leaf, tree, b = t.open('tk', 'T-0003', '--kind', 'solo')
    rc, o = t.lanes('finish', leaf, '--no-ticket', env=FIN_ENV)
    if rc != 1 or 'T-0003' not in o:
        fails.append(f'finish --no-ticket on a ticket lane: want exit 1 naming T-0003, got {rc}: {o}')
    return fails


def selftest():
    script = Path(__file__).resolve()
    src = script.read_text()
    saved = dict(os.environ)
    with tempfile.TemporaryDirectory() as t:
        base = Path(os.path.realpath(t))
        (base / 'bin').mkdir()
        gh = base / 'bin' / 'gh'
        gh.write_text('#!/bin/sh\nif [ -n "$LANES_STUB_GH" ] && [ -f "$LANES_STUB_GH" ]; then cat "$LANES_STUB_GH"; else echo "[]"; fi\n')
        gh.chmod(0o755)
        (base / 'gitconfig').write_text('')
        for k in list(os.environ):
            if k.startswith('GIT_') or k in ('SDLC_RUN_ID', 'LANES_STUB_GH'):
                del os.environ[k]
        ts = f'@{int(time.time() - 3 * 86400)} +0000'
        os.environ.update(GIT_CONFIG_GLOBAL=str(base / 'gitconfig'), GIT_CONFIG_NOSYSTEM='1', XDG_CONFIG_HOME=str(base / 'xdg'), GIT_AUTHOR_NAME='lanes selftest',
                          GIT_AUTHOR_EMAIL='lanes@selftest', GIT_COMMITTER_NAME='lanes selftest', GIT_COMMITTER_EMAIL='lanes@selftest',
                          GIT_AUTHOR_DATE=ts, GIT_COMMITTER_DATE=ts, PATH=f'{base / "bin"}{os.pathsep}{os.environ.get("PATH", "")}',
                          PYTHONPATH=os.pathsep.join(x for x in (str(HERE), os.environ.get('PYTHONPATH')) if x))
        old_cwd = os.getcwd()
        try:
            sentinel = base / 'sentinel'
            sentinel.mkdir()
            for c in (['init', '-q', '-b', 'main'], ['commit', '-q', '--allow-empty', '-m', 'sentinel']):
                r = git(sentinel, *c)
                if r.returncode:
                    print(f'FAIL: isolation: cannot make the sentinel repo: {err(r)}')
                    return 1
            os.chdir(str(sentinel))  # a cwd-relative leak in any case lands here, never in the real repository
            before = sentinel_state(sentinel)
            run_selftest(script, src, base)
            fails = []
            d = state_diff(before, sentinel_state(sentinel))
            if d:
                fails.append(d)
            git(sentinel, 'update-ref', 'refs/heads/leak', 'HEAD')
            if not state_diff(before, sentinel_state(sentinel)):
                fails.append('a planted refs/heads/leak was not caught')
            git(sentinel, 'update-ref', '-d', 'refs/heads/leak')
            git(sentinel, 'worktree', 'add', '-q', '--detach', str(base / 'planted-wt'))
            if not state_diff(before, sentinel_state(sentinel)):
                fails.append('a planted worktree was not caught')
            if fails:
                print('FAIL: isolation: ' + ' | '.join(fails))
                return 1
            print('ok: isolation: the sentinel repo is unchanged; a planted ref and a planted worktree are both caught')
            print('ok: lanes.py selftest')
            return 0
        finally:
            os.chdir(old_cwd)
            os.environ.clear()
            os.environ.update(saved)


def sentinel_state(repo):
    return [git(repo, 'worktree', 'list', '--porcelain').stdout, git(repo, 'for-each-ref').stdout]


def state_diff(a, b):
    """'' when the two snapshots match, else the changed lines marked - and +."""
    la, lb = (set(''.join(x).splitlines()) for x in (a, b))
    return '; '.join([f'-{l}' for l in sorted(la - lb)] + [f'+{l}' for l in sorted(lb - la)])


def run_selftest(script, src, base):
    def need(label, fails, okline):
        if fails:
            print(f'FAIL: {label}: ' + ' | '.join(fails))
            sys.exit(1)
        print(f'ok: {label}: {okline}')

    try:
        rows = (('row 1', case_row1, 'a manual tree refuses with exit 2'), ('row 2', case_row2, 'no lane <name>'),
                ('row 3', case_row3, 'a branch checked out in another worktree refuses'),
                ('row 4', case_row4, 'an integration tree with an open lane refuses'),
                ('row 5', case_row5, 'an unresolvable target and a failed diff both say cannot decide'),
                ('row 6', case_row6, 'a dirty landed lane refuses'))
        for label, case, line in rows:
            need(label, case(script, base), line)
        sw = case_sweep(script, base)
        for k, line in (('row 7', 'sweep keeps an empty lane'), ('row 8', 'sweep keeps a host lane queued for prune'),
                        ('row recent', 'sweep keeps a lane with a young tip'), ('row in use', 'sweep keeps a lane a process names'),
                        ('row locked', 'sweep keeps and close refuses a locked lane')):
            need(k, [f for f in sw if f.startswith(k + ':')], line)
        need('C5', [f for f in sw if f.startswith('C5') or f.startswith('sweep')], 'sweep closes only the landed lane and writes one archive ref')
        need('row 9', case_row9(script, base), 'a --no-ff merge closes by ancestry, archive ref and .sdlc copy written')
        need('work root', case_work_root(script, base),
             'under work_root: docs/work an untracked docs/work/0002-b/ is not dirt and is archived on close')
        need('row pr merged', case_prmerged(script, base), 'a merged PR whose head is the tip closes')
        need('row 10', case_row10(script, base), 'a git merge --squash closes by content')
        need('row 11', case_row11(script, base) + case_rename(script, base) + case_deleted(script, base),
             'a change, a rename and a deletion the target lacks refuse')
        need('row 12', case_row12(script, base), 'close --discard closes with an archive tag')
        need('carry', case_carry(script, base), 'close carries lane records into main, keeps a newer file, a discard carries none')
        need('carry work root', case_carry_work_root(script, base),
             'under work_root: docs/work close carries the lane records of a docs/work ticket into main')
        print('ok: C6: every truth table row gives its outcome')
        need('C1', case_c1_nested(script, base) + case_c1_outside(script, base),
             'a stray nested tree, a record outside the lanes root and a lane really under the checkout fail')
        need('C2', case_c2(script, base), 'two records on one port and a port outside lane_ports fail; open picks distinct ports')
        need('C3', case_c3(script, base), 'a record on another branch fails')
        need('bare root', case_bare_root(script, base), 'a bare clone lane gets <bare parent>/lanes and its tmp dir, outside the lane')
        need('C4', case_c4(script, base), 'stale at 11 days, not at 9, closable when landed, stale, locked kept by sweep')
        need('C9', case_c9(script, base), 'clashing names and a missing ticket refuse with nothing left; lane/T-1-a opens')
        need('tickets csv', case_tickets_csv(script, base),
             '--tickets T-1,T-2 equals two --ticket, mixed forms drop duplicates, and the second id is claim-checked (T-0691)')
        need('plugin_min', case_plugin_min(script, base),
             'plugin_min above the manifest refuses open with exit 2 and the host command, nothing left; equal opens')
        need('lane_setup', case_lane_setup(script, base),
             'two lane_setup: lines run in order; a failing first line records failed with its command and skips the second (T-0692)')
        need('node_modules', case_node_modules(script, base),
             'a node_modules symlink in a lane is never committed and finish closes clean; open warns on package.json without lane_setup (T-0773)')
        need('codex agents', case_codex_agents(script, base),
             'a lane in an onboarded repo gets current .codex/agents; a repo never onboarded gets none')
        need('C10', case_c10(script, base) + case_archive_twice(script, base) + case_archive_clash(script, base),
             'restore returns the tip, two closes leave two refs, a failed write keeps the branch')
        need('orphans', case_orphans(script, base),
             'a dangling commit with a unique change is listed, a squash-landed snapshot ref is not, nothing written')
        need('C13', case_c13(script, base), 'the description is set at open and copied into the archive tag')
        need('branch list', case_branch_list(script, base),
             'list --all joins a manual worktree to its ticket by branch: with verdict pass; no branch:, no ticket')
        need('branch record', case_branch_record(script, base), 'open --kind solo --ticket writes branch:, close removes it')
        need('open commits record', case_open_commits_record(script, base),
             'open commits the ticket branch: and worktree: lines in main and leaves other dirty paths alone (T-0599)')
        need('open dirty ticket', case_open_dirty_ticket(script, base),
             'a staged edit to the ticket handoff before open is not committed and is named in a not committed line (T-0599)')
        need('open into integration', case_open_into_integration(script, base),
             'open --into an integration tree commits the record there and main does not move (T-0680)')
        need('open into mergelock', case_open_into_mergelock(script, base),
             'open --into an integration tree waits for the merge.lock land holds before it commits the record (T-0725)')
        need('close integration record', case_close_integration_record(script, base),
             'close clears branch: and worktree: in the integration tree that holds the record and commits it there (T-0695)')
        need('close done in integration', case_close_done_in_integration(script, base),
             'a ticket done on the integration branch is not reported still open after its lane closes; one open there is (T-0769)')
        need('open upstream', case_open_upstream(script, base),
             'a main tracking an upstream gets no record commit and stays clean and level with origin (T-0609)')
        need('open local finish', case_open_local_finish(script, base),
             'a main with no upstream gets the record commit, stays clean, and finish lands and closes (T-0609)')
        need('claim unclaimed', case_claim_unclaimed(script, base), 'an unclaimed or unknown local ticket refuses')
        need('claim external', case_claim_external(script, base), 'an external id prints the directive and opens')
        cs = case_claim_still_open(script, base)
        need('still_open', [f for f in cs if f.startswith('still_open')], 'the lane still open line, nothing printed')
        need('claim still open', [f for f in cs if not f.startswith('still_open')], 'close prints ticket still open')
        need('case pr ref', case_pr_ref(script, base), 'a local pr/1 beside refs/remotes/pr/1: only the local branch goes')
        need('open path', case_open_path(script, base),
             '--path, --branch and --no-claim open an unclaimed ticket there with a record; without --no-claim it refuses')
        need('local settings', case_local_settings(script, base),
             'an ignored .claude/settings.local.json is copied into the lane and no other ignored file'),
        need('local settings unignored', case_local_settings_unignored(script, base),
             'a repo that does not ignore .claude/settings.local.json: git add -A in a lane never stages it (T-0724)')
        need('sibling root', case_sibling_root(script, base), 'the default lanes root is <parent>/<name>.worktrees, outside the main checkout (T-0563)')
        need('host record', case_host_record(script, base), 'every field written under the lanes.lock port pick, and discover reads it')
        need('host-owned', case_host_owned(script, base),
             'a landed Codex tree and a landed agent-x tree with a host record are kept as host-owned (T-0564)')
        need('host landed', case_host_landed_integration(script, base),
             'a landed host-owned agent-x tree does not hold the integration tree open; close prints its cleanup line (T-0743)')
        need('host removed', case_host_removed_integration(script, base),
             'a landed host record whose tree was removed does not hold the integration tree open; the present tree gets its line (T-0762)')
        need('host removed unmerged', case_host_removed_unmerged(script, base),
             'a removed host tree whose branch is not an ancestor of the integration branch holds the integration tree open (T-0762)')
        need('sweep other repo', case_sweep_other_repo(script, base),
             "the sweep names no unmarked folder under another repo's scratch dir and one line for this repo's (T-0764)")
        need('lock', case_lock(script, base),
             'open locks the lane with its owner; list shows it running, sweep keeps it, close --discard refuses, '
             'close unlocks and closes it, and an explicit unlock lets --discard close')
        need('ready', case_ready(script, base),
             'an unchanged lane and a ticket with no criteria refuse; uncommitted work pins a snapshot ref, unlocks and '
             'mails the factory; list --ready shows it, stale after an edit; close deletes the ref')
        need('ready unregistered', case_ready_unregistered(script, base),
             'with no factory registered ready pins the ref, unlocks, warns naming list --ready and the register step, and exits 0')
        need('ready once', case_ready_once(script, base),
             'with no factory mailbox the warning prints in full once per session; --notify-cmd runs with the ticket, sha '
             'and lane path, replaces the warning, and a failing command still exits 0')
        need('sweep merge.lock', case_sweep_mergelock(script, base),
             'a held merge.lock keeps a landed lane as merging; once released sweep closes it')
        need('finish pass', case_finish_pass(script, base),
             'a pass verdict commits, lands through the gate, settles, closes, backs up and removes the lane; a rerun is done')
        need('finish resume', case_finish_resume(script, base),
             'after a stop between merge and close a rerun closes and removes the lane with no second merge')
        need('finish fail', case_finish_fail(script, base), 'a fail verdict stops before any commit or merge')
        need('finish ignored', case_finish_ignored(script, base),
             'a skipped close still commits the lane close, an ignored tracked path included, and main is clean')
        need('finish moved', case_finish_moved(script, base),
             'main moved between land and settle: a rerun merges main into finish/<lane> and settles')
        need('open claim', case_open_claim(script, base), 'open --claim claims a proposed ticket, commits the claim and opens the lane (T-0800)')
        need('open claim upstream', case_open_claim_upstream(script, base),
             'with main tracking an upstream, lane_landing: local commits the claim; a PR repo commits nothing (T-0804)')
        need('finish agent id', case_finish_agent_id(script, base),
             'finish --verifier-agent-id records tokens, tool uses and duration from the transcript, prunes, then lands (T-0800)')
        need('finish backup bg', case_finish_backup_bg(script, base),
             'finish --backup returns while the push still runs and prints the background log path (T-0800)')
        need('finish backup failed', case_finish_backup_failed(script, base),
             'a failed background push is reported by the next finish: a previous-push-failed line and a nonzero exit (T-0802)')
        need('who', case_who(script, base), 'none with no live claude factory receiver, factory with one (T-0821)')
        need('overlap', case_overlap(script, base),
             'list --overlap names each lane touching a path, committed or uncommitted, and not one that does not (T-0821)')
        need('finish no ticket', case_finish_no_ticket(script, base),
             'finish --no-ticket lands a ticketless lane behind the gate, refuses a hash_bound path and a ticket lane (T-0821)')
        for marker, line, repl, case, tell, why in MUTANTS:
            if src.count(line) != 1:
                need(f'mutant {marker}', [f'the marked line is in the script {src.count(line)} times, want 1'], '')
            mdir = base / f'mutant-{marker}'
            mdir.mkdir()
            mutant = mdir / 'lanes.py'
            mutant.write_text(src.replace(line, repl))
            got = case(mutant, base)
            need(f'mutant {marker}', [] if any(tell in g for g in got) else [f'the mutant must fail its case with {tell!r}, got {got}'],
                 why)
    except LaneError as e:
        print(f'FAIL: fixture: {e}')
        sys.exit(1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
