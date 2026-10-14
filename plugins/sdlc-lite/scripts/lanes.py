#!/usr/bin/env python3
"""lanes.py: the one home of the lane lifecycle. Open, close, sweep, list, check, port and archive a lane.

  lanes.py open <name> [--base REF] [--into REF] [--ticket ID]... [--kind fanout|integration|solo] [--title TEXT]
                [--root .sdlc] [--path DIR] [--branch NAME] [--no-claim] [--dry-run]
  lanes.py close <name|path> [--into REF] [--discard] [--dry-run]
  lanes.py sweep [--apply]                 a dry run by default; --apply closes every landed plugin lane
  lanes.py list [--all] [--stale [--fail]] [--json]
  lanes.py check [--warn]                  C1 placement, C2 ports, C3 record drift; --warn prints and exits 0
  lanes.py port [<path>]                   the port of the lane holding <path> (default the cwd); exit 1 if none
  lanes.py archive list [<branch>]
  lanes.py archive restore <date>/<branch>
  lanes.py selftest

Design: docs/specs/sdlc-lite/lane-lifecycle.md (section 17 wins over sections 1 to 16). Python API for callers:
open_lane, close_lane, sweep, list_lanes, still_open(root, ticket), landed, config, host_record. open_lane and close_lane
return a dict with rc, message, lane, path and branch; sweep returns (list of those dicts, rc). open_lane takes
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
  host lane        the Claude host, isolation:worktree .claude/worktrees/<name>            worktree-<name>       the integration branch     dispatch.py prune --done, else sweep
  runner tmp       run.sh, dispatch.py                 .worktrees/tmp/<role>-<pid>, detached none                none                       run.sh EXIT, remove_tmp, reap-tmp-worktrees.sh
  manual           a person                            anywhere                            any                   none                       the person; listed, never touched

  Names (17.1): kinds fanout and solo need --ticket; the slug is <name> lowercased with every run of characters
  outside [a-z0-9-] replaced by -, cut to 40 characters; a leading # is dropped from the ticket in the leaf.
  Integration uses <name> verbatim as its branch. Before open creates anything it runs git check-ref-format
  --branch, the clash test over refs/heads (a flat lane beside lane/x, and the reverse) and refuses a tree path that
  exists or is a lanes dir, so a refusal leaves no directory and no record. A legacy fanout lane's into is the branch
  of <lanes-dir>/integration, else main; the integration tree's into is lane_into:, else main. Main is the branch of
  the first git worktree list entry.

  Claim rule (8.1): a T-<digits> id is local when --root exists: open refuses `ticket <id> not claimed: set
  claimed_by: first` or `no ticket <id>`. Any other id prints `claim <id> in its tracker (assignee) before work; not
  checked here`. After a close by row 9, row 10 or pr merged, close prints `ticket still open: <id>` for each local
  ticket of the record whose status is neither done nor dropped.

Landed test. Every ref is named in full (refs/heads/<b>, refs/remotes/<r>/<b>), so a local pr/1 beside
refs/remotes/pr/1 is never ambiguous.
  1. into must resolve to a commit, else `cannot decide`. A remote-tracking into is fetched first; a failed fetch
     with a ref that still resolves goes on against the stale ref and says so.
  2. ancestor: git merge-base --is-ancestor refs/heads/<b> <into> exit 0.
  3. pr merged: gh pr list --state merged --head <b> --json headRefOid reports the tip sha (read only; skipped when
     gh or a remote is absent).
  4. content: m = git merge-base <into> refs/heads/<b>; git diff --no-renames --name-only m refs/heads/<b>; either
     command failing is `cannot decide`, never an empty list. Landed when every listed path has the same blob at
     the branch and at into, absent on both counting as equal.
  5. else not landed, naming the first path that differs.

Truth table for close and sweep; the first matching row wins.

  row        state                                                          outcome                                                    exit
  1          not a plugin lane                                              not a plugin lane: <path>                                  2
  2          neither tree nor branch exists                                 no lane <name>                                             1
  3          the branch is checked out in another worktree                  branch <b> checked out at <path>                           1
  4          an integration tree with an open lane whose into is its branch lanes still open into <b>: <names>                         1
  5          into does not resolve, or a git read fails                     cannot decide: <reason>                                    1
  6          tracked changes, or untracked files outside .sdlc/ and         uncommitted changes in <lane>: <first path>                1
             .lane.json, and no --discard
  locked     the tree is locked (git worktree list --porcelain)             locked: <reason>                                           1
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
  sweep is a dry run that prints `would close <lane> (<how>)`; --apply closes.

Close steps (rows 9, 10, pr merged, 12), in order, so a failure leaves a lane a rerun closes:
  1. Write an annotated tag object (git mktag, never a ref under refs/tags) whose message holds the branch
     description `<ticket> <title>`, the reason (ancestor, pr merged, content in <into>, discarded), into, the tip
     sha and the UTC time; point refs/archive/<UTC date>/<branch> at it with update-ref and a zero old value. If that
     fails, retry once with the leaf <branch>.<sha7>; a second failure stops the close with the branch intact.
  2. Copy the tree's untracked and ignored .sdlc/ files, and the ignored .sdlc/runtime/tasks/ records (minus *.log,
     *.running, *.run.lock), to <git common dir>/sdlc-lane-archive/<lane>/; a failed write stops the close here.
  3. git worktree remove --force <path>; a missing tree skips this step.
  4. git update-ref -d refs/heads/<b> <sha>: by full name, and only while the branch is at the sha the test read.
  5. git worktree prune; remove a host record; print `port <n> still listening (pid <p>)` when a listener holds
     the lane's port.
  Restore with `lanes.py archive restore <date>/<branch>` (git branch <branch> <ref>; refuses an existing branch).
  archive list reads tag and plain commit targets alike.

Record fields. .lane.json at the tree root, written by open, added to <git common dir>/info/exclude; a host record
<lanes root>/host/<name>.lane.json has the same fields.
  lane      the lane name (the tree leaf)          kind      fanout, integration or solo (host for a host record)
  branch    the lane branch                        base      the --base ref          base_sha  its sha at open
  into      the ref the landed test reads          tickets   the ticket ids          port      a port, or null
  opened    UTC time of open                       run_id    $SDLC_RUN_ID, or null   setup     ok, failed rc=<n>, or null
  open also writes branch.<b>.description as `<ticket> <title>` (cut to 120 characters).

Config (.sdlc/config of the main worktree; blank and # lines ignored):
  lanes_root: <path>        default .worktrees, relative to the main worktree's toplevel
  lane_into: <ref>          default none (main)
  lane_setup: <cmd>         run in a new tree; a failure records setup: failed rc=<n> and keeps the lane
  lane_ports: <lo>-<hi>     off when absent; open picks the lowest free port under a flock on <lanes root>/lanes.lock
  lane_stale_days: <n>      default 10        lane_min_age_hours: <n>  default 2
  lane_keep: <branch>...    sweep keeps these  lane_names:, lane_sweep:  read and returned only (fanout owns them)
"""
import argparse, contextlib, datetime, fcntl, io, json, os, pathlib, re, shutil, socket, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tickets  # same scripts/ dir: the only front matter parser

Path = pathlib.Path
RECORD = '.lane.json'
FIELDS = ('lane', 'kind', 'branch', 'base', 'base_sha', 'into', 'tickets', 'port', 'opened', 'run_id', 'setup')
KINDS = ('fanout', 'integration', 'solo')
LOCAL_ID = re.compile(r'T-\d+')
PRUNE_REL = Path('.sdlc') / 'runtime' / 'prune.json'  # dispatch.py PRUNE_REL
PRUNE_TTL = 6 * 3600
NAMESPACES = ('lane/', 'wave/', 'release/')
CONFIG_KEYS = ('lanes_root', 'lane_into', 'lane_setup', 'lane_ports', 'lane_stale_days', 'lane_min_age_hours',
               'lane_keep', 'lane_names', 'lane_sweep')


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
    vals, keep = {}, []
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
    root = os.path.expanduser(vals.get('lanes_root') or '.worktrees')
    return dict(lanes_root=Path(os.path.normpath(os.path.join(str(top), root))), lane_into=vals.get('lane_into') or None,
                lane_setup=vals.get('lane_setup') or None, lane_ports=ports, lane_stale_days=num('lane_stale_days', 10),
                lane_min_age_hours=num('lane_min_age_hours', 2), lane_keep=keep, lane_names=vals.get('lane_names'),
                lane_sweep=vals.get('lane_sweep'))


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


# ---- lane discovery and ownership -------------------------------------------------------------------------

def blank(path, exists, branch=None, head=None, locked=None):
    return dict(path=str(path), exists=exists, branch=branch, head=head, locked=locked, owner='', kind='manual',
                lane=os.path.basename(str(path)), into=None, base=None, base_sha=None, tickets=[], port=None,
                record=None, record_path=None, record_branch=None, setup=None)


def apply_record(ctx, d, rec, host=False):
    d['record'] = rec
    d['kind'] = rec.get('kind') or ('host' if host else 'fanout')
    d['lane'] = rec.get('lane') or d['lane']
    d['record_branch'] = rec.get('branch')
    if rec.get('branch'):
        d['branch'] = rec['branch']
    d['into'] = rec.get('into') or ctx.cfg['lane_into'] or ctx.main
    for k in ('base', 'base_sha', 'port', 'setup'):
        d[k] = rec.get(k)
    t = rec.get('tickets') or []
    d['tickets'] = [t] if isinstance(t, str) else list(t)


def lane_of(ctx, w):
    p = w['path']
    d = blank(p, os.path.isdir(p), w['branch'], w['head'], w['locked'])
    d['tree_branch'] = w['branch']
    rec = read_json(os.path.join(p, RECORD))
    hp = ctx.root / 'host' / (os.path.basename(p) + '.lane.json')
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
    elif plain_under(p, Path(ctx.top) / '.worktrees' / 'tmp'):
        d['kind'] = 'runner tmp'
    return d


def discover(ctx):
    """A lane dict for every worktree except the main one, plus host records whose tree is absent."""
    lanes, seen = [], set()
    for w in ctx.wts:
        if w['bare'] or samepath(w['path'], ctx.top):
            continue
        seen.add(os.path.realpath(w['path']))
        lanes.append(lane_of(ctx, w))
    hd = ctx.root / 'host'
    for hp in sorted(hd.glob('*.lane.json')) if hd.is_dir() else []:
        name = hp.name[:-len('.lane.json')]
        tp = Path(ctx.top) / '.claude' / 'worktrees' / name
        if os.path.realpath(str(tp)) in seen:
            continue
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


def landed(cwd, ref, into, branch=None, pr=True):
    """('ancestor' | 'pr merged' | 'content' | 'not landed' | 'cannot decide', detail) for a full ref against into."""
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


def first_dirty(path):
    """(first dirty path or None, error or None): tracked changes, or untracked files outside .sdlc/ and .lane.json."""
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
        if code == '??' and (p == RECORD or p == '.sdlc' or p.startswith('.sdlc/')):
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
    if d['kind'] == 'integration' and b:
        names = []
        for o in lanes:
            if o is d or not o['owner'] or o['kind'] == 'integration':
                continue
            oi = (o['into'] or '')
            oi = oi[len('refs/heads/'):] if oi.startswith('refs/heads/') else oi
            if oi == b and (o['exists'] or (o['branch'] and has_ref(top, f'refs/heads/{o["branch"]}'))):
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
    if d['locked'] is not None:
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
    info = dict(sha=tip, into=target, note=note)
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
    r = git(path, 'ls-files', '--others', '-z', '--', '.sdlc')
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
    if d['exists']:
        e = copy_sdlc(d['path'], ctx.common / 'sdlc-lane-archive' / name)
        if e:
            return result(1, '\n'.join(pre + [f'cannot archive the .sdlc files of {name}: {e}; archive ref {ref} kept, lane not closed']),
                          lane=name, path=d['path'], branch=b)
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
    lines = pre + [outcome]
    pl = port_line(d['port'])
    if pl:
        lines.append(pl)
    if how != 'discarded':
        metas = local_tickets(top)
        for t in d['tickets']:
            if LOCAL_ID.fullmatch(str(t)) and any(m.get('id') == t and m.get('status') not in ('done', 'dropped') for _, m in metas):
                lines.append(f'ticket still open: {t}')
    return result(0, '\n'.join(lines), lane=name, path=d['path'], branch=b, archive=ref, row=how)


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
    if not apply:
        res.append(result(0, 'dry run; pass --apply to close'))
    return res, rc


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


def add_exclude(common):
    path = Path(common) / 'info' / 'exclude'
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding='utf-8') if path.is_file() else ''
    if not any(l.strip() in (RECORD, '/' + RECORD) for l in text.splitlines()):
        path.write_text(text + ('' if not text or text.endswith('\n') else '\n') + RECORD + '\n', encoding='utf-8')


def write_record(tree, rec):
    (Path(tree) / RECORD).write_text(json.dumps({k: rec.get(k) for k in FIELDS}) + '\n', encoding='utf-8')


def ticket_title(rootp, tid):
    """The title of local ticket tid under rootp, or '' when it is not readable."""
    try:
        metas = tickets.load(tickets.ticket_dir(rootp))
    except (tickets.Fail, OSError):
        return ''
    return next((str(m.get('title') or '') for _, m in metas if m.get('id') == tid), '')


def open_lane(name, base=None, into=None, tickets=(), kind='fanout', title=None, root='.sdlc', dry_run=False, cwd='.', *,
              path=None, branch=None, check_claim=True):
    ctx = Ctx(cwd)
    top = ctx.top
    ids = list(tickets or ())
    lines = []
    if kind not in KINDS:
        return result(2, f'unknown kind {kind}: use fanout, integration or solo')
    if kind in ('fanout', 'solo') and not ids:
        return result(1, f'kind {kind} needs --ticket: no ticket, no lane')
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
        write_record(tree, rec)
    add_exclude(ctx.common)
    local = Path(top, '.claude', 'settings.local.json')  # gitignored, so a new worktree lacks it; copy only this file, never log it
    if local.is_file() and not Path(tree, '.claude', 'settings.local.json').exists():
        try:
            Path(tree, '.claude').mkdir(exist_ok=True)
            shutil.copy2(str(local), str(Path(tree, '.claude', 'settings.local.json')))
        except OSError as e:
            lines.append(f'settings.local.json not copied: {e.strerror or "error"}')
    if desc:
        git(top, 'config', f'branch.{branch}.description', desc)
    lines.append(f'opened {leaf} at {tree} (branch {branch}, into {into_})')
    if rec['port']:
        lines.append(f'port {rec["port"]}')
    if ctx.cfg['lane_setup']:
        try:
            s = subprocess.run(ctx.cfg['lane_setup'], shell=True, cwd=str(tree))
            rec['setup'] = 'ok' if s.returncode == 0 else f'failed rc={s.returncode}'
        except OSError as e:
            rec['setup'] = f'failed rc=127 ({e})'
        write_record(tree, rec)
        if rec['setup'] != 'ok':
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
        if states == ['open']:
            states = ['locked']
        else:
            states.append('locked')
    if d['owner'] and d['branch'] and not d['branch'].startswith(NAMESPACES):
        states.append('legacy')
    return states


def list_lanes(all_=False, stale=False, cwd='.'):
    ctx = Ctx(cwd)
    rows = []
    for d in discover(ctx):
        if not d['owner'] and not all_:
            continue
        st = lane_states(ctx, d)
        if stale and not ({'closable', 'stale'} & set(st)):
            continue
        desc = (out(ctx.top, 'config', '--get', f'branch.{d["branch"]}.description') or '') if d['branch'] else ''
        rows.append(dict(lane=d['lane'], path=d['path'], branch=d['branch'], kind=d['kind'], owner=d['owner'] or 'manual',
                         state=', '.join(st), states=st, description=desc, into=d['into'], tickets=d['tickets'],
                         port=d['port'], locked=d['locked'], exists=d['exists']))
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
    tmp, hostdir = Path(top) / '.worktrees' / 'tmp', Path(top) / '.claude' / 'worktrees'
    found = []
    for d in lanes:
        if not d['exists'] or d['owner'] or under(d['path'], tmp) or under(d['path'], hostdir):
            continue
        for t in tops:
            if not samepath(t, d['path']) and under(d['path'], t):
                found.append(f'C1: {os.path.basename(d["path"])} is nested in {t} and is not a plugin lane: {d["path"]}')
                break
    outside = not plain_under(ctx.root, top)
    for d in lanes:
        if d['owner'] != 'record' or not d['exists']:
            continue
        if not under(d['path'], ctx.root):
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


# ---- CLI --------------------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(prog='lanes.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', metavar='{open,close,sweep,list,check,port,archive,selftest}')
    sub.required = True
    p = sub.add_parser('open')
    p.add_argument('name')
    p.add_argument('--base')
    p.add_argument('--into')
    p.add_argument('--ticket', action='append', default=[])
    p.add_argument('--kind', choices=KINDS, default='fanout')
    p.add_argument('--title')
    p.add_argument('--root', default='.sdlc')
    p.add_argument('--path')
    p.add_argument('--branch')
    p.add_argument('--no-claim', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('close')
    p.add_argument('target')
    p.add_argument('--into')
    p.add_argument('--discard', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('sweep')
    p.add_argument('--apply', action='store_true')
    p = sub.add_parser('list')
    p.add_argument('--all', action='store_true')
    p.add_argument('--stale', action='store_true')
    p.add_argument('--fail', action='store_true')
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
    sub.add_parser('selftest')
    a = ap.parse_args(argv)
    if a.cmd == 'list' and a.fail and not a.stale:
        ap.error('--fail needs --stale')
    if a.cmd == 'selftest':
        return selftest()
    try:
        if a.cmd == 'open':
            r = open_lane(a.name, base=a.base, into=a.into, tickets=a.ticket, kind=a.kind, title=a.title, root=a.root,
                          dry_run=a.dry_run, path=a.path, branch=a.branch, check_claim=not a.no_claim)
            print(r['message'])
            return r['rc']
        if a.cmd == 'close':
            r = close_lane(a.target, into=a.into, discard=a.discard, dry_run=a.dry_run)
            print(r['message'])
            return r['rc']
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
                          (f'  {r["description"]}' if r['description'] else ''))
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
        return self.top / '.worktrees' / leaf

    def open(self, name, ticket=None, *extra):
        args = ['open', name] + (['--ticket', ticket] if ticket else []) + list(extra)
        rc, o = self.lanes(*args)
        if rc:
            raise LaneError(f'open {name} failed: {o}')
        m = re.search(r'opened (\S+) at (.+?) \(branch (\S+),', o)
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
    hp = t.top / '.worktrees' / 'host' / 'h1.lane.json'
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
    ('REALPATH', 'child, parent = os.path.realpath(str(child)), os.path.realpath(str(parent))' + '  # REALPATH',
     'child, parent = os.path.normpath(str(child)), os.path.normpath(str(parent))' + '  # REALPATH', case_c1_outside,
     'passed a symlinked path', 'C1 passes a symlinked path'),
)


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
        os.environ.update(GIT_CONFIG_GLOBAL=str(base / 'gitconfig'), GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='lanes selftest',
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
        need('row pr merged', case_prmerged(script, base), 'a merged PR whose head is the tip closes')
        need('row 10', case_row10(script, base), 'a git merge --squash closes by content')
        need('row 11', case_row11(script, base) + case_rename(script, base) + case_deleted(script, base),
             'a change, a rename and a deletion the target lacks refuse')
        need('row 12', case_row12(script, base), 'close --discard closes with an archive tag')
        print('ok: C6: every truth table row gives its outcome')
        need('C1', case_c1_nested(script, base) + case_c1_outside(script, base),
             'a stray nested tree, a record outside the lanes root and a lane really under the checkout fail')
        need('C2', case_c2(script, base), 'two records on one port and a port outside lane_ports fail; open picks distinct ports')
        need('C3', case_c3(script, base), 'a record on another branch fails')
        need('C4', case_c4(script, base), 'stale at 11 days, not at 9, closable when landed, stale, locked kept by sweep')
        need('C9', case_c9(script, base), 'clashing names and a missing ticket refuse with nothing left; lane/T-1-a opens')
        need('C10', case_c10(script, base) + case_archive_twice(script, base) + case_archive_clash(script, base),
             'restore returns the tip, two closes leave two refs, a failed write keeps the branch')
        need('C13', case_c13(script, base), 'the description is set at open and copied into the archive tag')
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
        need('host record', case_host_record(script, base), 'every field written under the lanes.lock port pick, and discover reads it')
        need('sweep merge.lock', case_sweep_mergelock(script, base),
             'a held merge.lock keeps a landed lane as merging; once released sweep closes it')
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
