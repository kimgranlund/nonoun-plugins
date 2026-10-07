"""Loaded-context reader (T-0252): the paths one role run read, from its raw log or Codex rollout.

read(log_path, backend=None, codex_home=None) returns one dict, never None, never raises:
  {'source': 'stream-json', 'paths': [...]}   Claude arm: the file_path of every Read tool_use block
                                              in assistant events of the stream-json log;
  {'source': 'rollout', 'paths': [...]}       Codex arm: the rollout named by the log's thread id;
                                              the files its shell commands read (cat, head, tail,
                                              sed, nl, less, more, bat) that exist, resolved
                                              against the command's workdir;
  {'status': 'log absent'}                    no file at log_path;
  {'status': 'log unreadable'}                the log could not be read;
  {'status': 'rollout absent'}                Codex arm: the log has no thread id, or no rollout
                                              file for it exists under <codex home>/sessions
                                              (`codex exec --ephemeral`, which codex_exec.py uses,
                                              writes none);
  {'status': 'rollout unreadable'}            the rollout exists but could not be read.
A record with a status has no paths key: an empty `paths` list means the run read nothing through
the recognized channels, and a missing log or rollout is never reported that way. Paths keep the
form the run used (a Read path as given, a shell path made absolute), first seen first, no
duplicates. Keys are in sorted order, so a record survives the ingest cursor's sorted-key JSON
round trip byte for byte. backend 'claude' or 'codex' picks the arm; None picks Codex when the log
holds a `codex_event` line, else Claude. codex_home defaults to $CODEX_HOME, else ~/.codex.
Not captured: entry files the host injects into a session (the stream-json log has no event for
them), a Claude Bash command that reads a file, and a Codex read by a command outside the list.
"""
import glob, json, os, shlex, re

SHELL_READERS = ('cat', 'head', 'tail', 'sed', 'nl', 'less', 'more', 'bat')
_SPLIT = re.compile(r'\|\||&&|[|;\n]')


def _events(path):
    """Parsed JSON objects of a JSONL file; lines that are not objects are skipped."""
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if isinstance(ev, dict):
                yield ev


def _uniq(paths):
    return list(dict.fromkeys(p for p in paths if isinstance(p, str) and p))


def _claude_paths(events):
    out = []
    for ev in events:
        msg = ev.get('message')
        content = msg.get('content') if isinstance(msg, dict) else None
        if ev.get('type') != 'assistant' or not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('name') == 'Read':
                inp = b.get('input')
                out.append(inp.get('file_path') if isinstance(inp, dict) else None)
    return out


def shell_reads(cmd, workdir):
    """Existing files named as arguments of a reader command in a shell command line."""
    out = []
    for seg in _SPLIT.split(cmd if isinstance(cmd, str) else ''):
        try:
            toks = shlex.split(seg)
        except ValueError:
            continue
        while toks and '=' in toks[0] and not toks[0].startswith('-'):
            toks = toks[1:]  # leading VAR=value
        if not toks or os.path.basename(toks[0]) not in SHELL_READERS:
            continue
        for t in toks[1:]:
            if t.startswith('-'):
                continue
            p = os.path.normpath(t if os.path.isabs(t) else os.path.join(workdir or '', t))
            if os.path.isfile(p):
                out.append(p)
    return out


def _call_command(payload):
    """(command string, workdir) of a Codex shell function_call or local_shell_call, else None."""
    if payload.get('type') == 'local_shell_call':
        action = payload.get('action')
        args = action if isinstance(action, dict) else {}
    elif payload.get('type') == 'function_call' and payload.get('name') in (
            'exec_command', 'shell', 'container.exec', 'shell_command'):
        try:
            args = json.loads(payload.get('arguments') or '{}')
        except ValueError:
            return None
    else:
        return None
    if not isinstance(args, dict):
        return None
    cmd = args.get('cmd', args.get('command'))
    if isinstance(cmd, list):
        cmd = cmd[-1] if len(cmd) > 2 and cmd[1] in ('-c', '-lc') else shlex.join(map(str, cmd))
    workdir = args.get('workdir') or args.get('working_directory') or ''
    return (cmd, workdir) if isinstance(cmd, str) else None


def _thread_id(events):
    for ev in events:
        inner = ev.get('event')
        if ev.get('type') == 'codex_event' and isinstance(inner, dict) \
                and inner.get('type') == 'thread.started' and inner.get('thread_id'):
            return str(inner['thread_id'])
    return None


def _rollout(thread_id, codex_home):
    home = codex_home or os.environ.get('CODEX_HOME') or os.path.expanduser('~/.codex')
    # The thread id is a UUID; refuse anything else so it cannot widen the glob.
    if not re.fullmatch(r'[0-9A-Za-z-]+', thread_id or ''):
        return None
    hits = sorted(glob.glob(os.path.join(glob.escape(home), 'sessions', '*', '*', '*',
                                         f'rollout-*{thread_id}.jsonl')))
    return hits[-1] if hits else None


def _codex_paths(events):
    out = []
    for ev in events:
        payload = ev.get('payload')
        got = _call_command(payload) if ev.get('type') == 'response_item' \
            and isinstance(payload, dict) else None
        if got:
            out.extend(shell_reads(*got))
    return out


def read(log_path, backend=None, codex_home=None):
    try:
        if not os.path.isfile(log_path):
            return {'status': 'log absent'}
        events = list(_events(log_path))
    except (OSError, TypeError):
        return {'status': 'log unreadable'}
    if backend is None:
        backend = 'codex' if any(e.get('type') == 'codex_event' for e in events) else 'claude'
    if backend != 'codex':
        return {'paths': _uniq(_claude_paths(events)), 'source': 'stream-json'}
    thread = _thread_id(events)
    rollout = _rollout(thread, codex_home) if thread else None
    if rollout is None:
        return {'status': 'rollout absent'}
    try:
        return {'paths': _uniq(_codex_paths(_events(rollout))), 'source': 'rollout'}
    except OSError:
        return {'status': 'rollout unreadable'}
