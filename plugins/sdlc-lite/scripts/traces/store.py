"""Store: the traces out dir, its events.jsonl and aux.json, and the ingest cursor.

out_dir(repo, out=None)  `out` when given, else <cwd>/.sdlc/runtime/traces/<repo-key>/, where
                         repo-key is <basename of repo>-<first 8 hex of sha256 of its absolute
                         path>. Nothing is created here; the writers create the dir.
write_events(out, rows)  <out>/events.jsonl: one JSON line per row, keys in table.ROW_FIELDS
                         order, rows sorted by (task_dir, step or -1, attempt name) with
                         (superseded, attempt_id, sources) as tie-breaks, so an unchanged corpus
                         gives byte-identical output.
write_aux(out, aux)      <out>/aux.json (lanes, gates, git facts, tickets, baseline, repo).
load_cursor(out) / write_cursor(out, cursor)
                         <out>/cursor.json: {"version": 1, "keys": {source key: entry}}. A source
                         key is a handoff dir (its repo-relative path) or a lanes dir (its
                         absolute path); an entry holds the key's "fingerprint" and the "rows" it
                         produced (plus any extra fields the ingest keeps, such as "ticket").
fingerprint(dir, subdirs=())
                         sha256 over the sorted names, sizes, and mtime_ns of the plain files
                         directly in dir (and in each named subdir, as <subdir>/<name>); a
                         missing dir fingerprints as empty. Only stat is used, no file is opened.
reading(dir)             context manager: while it is active, every file under dir that the
                         process opens (seen through the "open" audit event) is recorded, and on
                         exit the count of distinct such paths that are files (a failed open of
                         a missing file is not a read) is added to READS.
READS                    source files actually opened by readers inside reading(); the ingest
                         resets it to 0 at the start of each run, so after a run it is that run's
                         count. The per-run readers outside any cursor key (git, tickets, bench)
                         are not counted.
"""
import contextlib, hashlib, json, os, sys

from . import table

READS = 0
EVENTS, AUX, CURSOR = 'events.jsonl', 'aux.json', 'cursor.json'
CURSOR_VERSION = 1

_ACTIVE = []  # stack of [prefix, set of opened paths]
_HOOKED = False


def repo_key(repo):
    path = os.path.abspath(repo)
    digest = hashlib.sha256(path.encode('utf-8')).hexdigest()[:8]
    return f'{os.path.basename(path.rstrip(os.sep)) or "root"}-{digest}'


def out_dir(repo, out=None):
    if out:
        return os.path.abspath(out)
    return os.path.join(os.getcwd(), '.sdlc', 'runtime', 'traces', repo_key(repo))


def _atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f'{path}.tmp-{os.getpid()}'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    os.replace(tmp, path)


def attempt_name(row):
    """<role>-<level>[-<k>] of a row, '' when role or level is unknown."""
    role, level, k = row.get('role'), row.get('level'), row.get('attempt_k')
    if not role or not level:
        return ''
    return f'{role}-{level}' + (f'-{k}' if isinstance(k, int) and k > 1 else '')


def _sort_key(row):
    step = row.get('step')
    return (str(row.get('task_dir') or ''), step if isinstance(step, int) else -1,
            attempt_name(row), bool(row.get('superseded')), str(row.get('attempt_id') or ''),
            json.dumps(row.get('sources'), sort_keys=True))


def event_line(row):
    return json.dumps({k: row.get(k) for k in table.ROW_FIELDS}, ensure_ascii=False)


def write_events(out, rows):
    path = os.path.join(out, EVENTS)
    _atomic_write(path, ''.join(event_line(r) + '\n' for r in sorted(rows, key=_sort_key)))
    return path


def write_aux(out, aux):
    path = os.path.join(out, AUX)
    _atomic_write(path, json.dumps(aux, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
    return path


def load_cursor(out):
    try:
        with open(os.path.join(out, CURSOR), encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get('version') != CURSOR_VERSION:
        return {}
    keys = data.get('keys')
    return keys if isinstance(keys, dict) else {}


def write_cursor(out, cursor):
    path = os.path.join(out, CURSOR)
    _atomic_write(path, json.dumps({'version': CURSOR_VERSION, 'keys': cursor}, sort_keys=True,
                                   ensure_ascii=False) + '\n')
    return path


def fingerprint(dir, subdirs=()):
    h = hashlib.sha256()
    entries = []
    for sub in ('',) + tuple(subdirs):
        base = os.path.join(dir, sub) if sub else dir
        try:
            it = list(os.scandir(base))
        except OSError:
            continue
        for e in it:
            try:
                if not e.is_file(follow_symlinks=False):
                    continue
                st = e.stat(follow_symlinks=False)
            except OSError:
                continue
            entries.append((f'{sub}/{e.name}' if sub else e.name, st.st_size, st.st_mtime_ns))
    for name, size, mtime in sorted(entries):
        h.update(f'{name}\0{size}\0{mtime}\n'.encode('utf-8', 'surrogateescape'))
    return h.hexdigest()


def _audit(event, args):
    if event != 'open' or not _ACTIVE or not args:
        return
    path = args[0]
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, str):
        return  # an fd
    path = os.path.abspath(path)
    for prefix, seen in _ACTIVE:
        if path.startswith(prefix):
            seen.add(path)


@contextlib.contextmanager
def reading(dir):
    global READS, _HOOKED
    if not _HOOKED:
        sys.addaudithook(_audit)
        _HOOKED = True
    entry = [os.path.join(os.path.abspath(dir), ''), set()]
    _ACTIVE.append(entry)
    try:
        yield entry[1]
    finally:
        _ACTIVE.remove(entry)
        # the audit event fires before the open; a path that is no file was never opened
        READS += sum(1 for p in entry[1] if os.path.isfile(p))
