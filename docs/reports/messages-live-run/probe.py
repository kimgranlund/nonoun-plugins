#!/usr/bin/env python3
"""Live probe for T-0179: a fresh Claude Code or Codex role handles a mailbox message from the entry files.

Usage: probe.py <claude|codex|claude-messenger|codex-messenger> [--defect] [--timeout SECONDS]
       probe.py selftest

Arms
  claude, codex                 path only: the host gets "Handle the message at <path>." and no skill.
  claude-messenger, codex-messenger
                                the host is told to spawn the messenger agent, which polls the mailbox.
  --defect (claude or codex)    overwrite the generated mailbox AGENTS.md files with defect-AGENTS.md
                                after the send, so a role that follows them fails the oracle.

The plugin is this worktree's plugins/sdlc-lite. Every host process gets the environment without
CLAUDECODE, CLAUDE_PLUGIN_ROOT, CLAUDE_PLUGIN_DATA, CLAUDE_CODE_* and SDLC_*. The throwaway project is
kept and its path printed; the host's raw stdout and stderr are saved next to it, as
host-stdout.jsonl and host-stderr.txt.

Output: key=value lines on stdout (arm, project, plugin, message, isolation, trace, state,
messenger_spawned, stamps, result); progress notes on stderr.
Exit 0 pass, 1 fail, 2 setup error, 3 unverified.

selftest runs offline (no model call) against the real messages.py CLI and prints `ok: <case>` per
case, then `probe selftest: PASS`.
"""
import argparse
import datetime
import glob
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = Path(__file__).resolve().parents[3] / 'plugins' / 'sdlc-lite'
SCRIPTS = PLUGIN / 'scripts'
DEFECT = HERE / 'defect-AGENTS.md'

ARMS = ('claude', 'codex', 'claude-messenger', 'codex-messenger')
HOST = {'claude': 'claude', 'codex': 'codex', 'claude-messenger': 'claude', 'codex-messenger': 'codex'}
MESSENGER_ARMS = ('claude-messenger', 'codex-messenger')
STATES = ('new', 'read', 'done')
SENDER = 'probe'
TOPIC = 'live-probe'
BODY = 'What is 2 + 3? Answer in one line.'
SEND_DELAY = 20
SAMPLE_EVERY = 2
PATH_TIMEOUT = 600
MESSENGER_TIMEOUT = 900
KILL_GRACE = 10
EXPIRED_OUTCOMES = ('expired', 'expired, no reply')
TS_RE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z')
TS_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'
CLAUDE_MESSENGER = 'sdlc-lite:messenger'
CODEX_MESSENGER = 'sdlc-messenger-l1'
DEFECT_FILES = ('AGENTS.md', 'new/AGENTS.md', 'read/AGENTS.md', 'done/AGENTS.md')
DEFECT_CAT = 'cat <path>'
DEFECT_MOVE = 'mkdir -p .sdlc/messages/done/<receiver> && mv <path> .sdlc/messages/done/<receiver>/'

CLAUDE_PARENT_PROMPT = (
    'This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. '
    'Spawn the sdlc-lite:messenger agent in the foreground, not in the background, with the prompt '
    '"harness: claude", and wait for its report; spawn it again until a report names a claimed message. '
    'Handle each claimed message as .sdlc/messages/AGENTS.md says: reply when follow_up_requested is true, '
    'then ack it. Then stop.')
CODEX_PARENT_PROMPT = (
    'This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. '
    'Spawn the sdlc-messenger-l1 agent with the prompt "harness: codex" and wait for its report; spawn it '
    'again until a report names a claimed message. Handle each claimed message as .sdlc/messages/AGENTS.md '
    'says: reply when follow_up_requested is true, then ack it. Then stop.')
CONTROL_PROMPT = 'Reply with exactly OK. Do not call tools.'


class SetupError(Exception):
    """Exit 2."""


class Unverified(Exception):
    """Exit 3."""


def emit(line):
    sys.stdout.write(line + '\n')
    sys.stdout.flush()


def note(text):
    sys.stderr.write('probe: ' + text + '\n')
    sys.stderr.flush()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(TS_FMT)


def one_line(text):
    """Escape line breaks and tabs so a value stays on one output line."""
    return text.replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')


# ---------------------------------------------------------------- environment and setup

def clean_env(base=None):
    """A copy of the environment without the host session, plugin root, and sdlc runner variables."""
    env = dict(os.environ if base is None else base)
    for key in list(env):
        if (key in ('CLAUDECODE', 'CLAUDE_PLUGIN_ROOT', 'CLAUDE_PLUGIN_DATA')
                or key.startswith('CLAUDE_CODE_') or key.startswith('SDLC_')):
            del env[key]
    return env


def run_checked(cmd, cwd, env, what):
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise SetupError(f'{what}: {e}') from None
    if r.returncode != 0:
        raise SetupError(f'{what} exited {r.returncode}: {one_line(r.stderr.strip())[:300]}')
    return r.stdout


def setup(arm, env):
    """Make the throwaway project. Return (tmp, project), both real paths."""
    try:
        tmp = os.path.realpath(tempfile.mkdtemp(prefix='messages-live-'))
        project = os.path.join(tmp, 'project')
        os.mkdir(project)
    except OSError as e:
        raise SetupError(f'temp project: {e}') from None
    run_checked(['git', 'init', '-q'], project, env, 'git init')
    run_checked(['git', '-c', 'user.name=probe', '-c', 'user.email=probe@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', 'init'],
                project, env, 'git commit')
    run_checked(['python3', str(SCRIPTS / 'tickets.py'), '--root', '.sdlc', 'roadmap'], project, env,
                'tickets.py roadmap')
    mbox = mailbox_of(project)
    for rel in DEFECT_FILES:
        if not os.path.isfile(os.path.join(mbox, rel)):
            raise SetupError(f'tickets.py roadmap wrote no {rel} in the mailbox')
    if arm == 'codex-messenger':
        run_checked(['python3', str(SCRIPTS / 'codex_roles.py'), 'install', project], project, env,
                    'codex_roles.py install')
    return tmp, project


def mailbox_of(project):
    return os.path.join(project, '.sdlc', 'messages')


def send(project, host, env):
    """Send the probe message to <host> through the real CLI. Return its absolute path."""
    out = run_checked(['python3', str(SCRIPTS / 'messages.py'), 'send', '--receiver', host,
                       '--sender', SENDER, '--topic', TOPIC, '--follow-up', 'true', BODY],
                      project, env, 'messages.py send')
    path = out.strip()
    if not os.path.isfile(path):
        raise SetupError(f'messages.py send printed {path!r}, which is not a file')
    return path


def message_id(path):
    return os.path.basename(path)[:-3]


def apply_defect(mbox):
    """Overwrite each generated mailbox AGENTS.md with the bytes of defect-AGENTS.md."""
    try:
        data = DEFECT.read_bytes()
    except OSError as e:
        raise SetupError(f'defect fixture: {e}') from None
    for rel in DEFECT_FILES:
        path = os.path.join(mbox, rel)
        if not os.path.isfile(path):
            raise SetupError(f'no generated entry file {path}')
        with open(path, 'wb') as f:
            f.write(data)


# ---------------------------------------------------------------- mailbox reading (own parser)

def parse_message(path):
    """The front matter of a message file as a dict, read without messages.py. None when unreadable."""
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except OSError:
        return None
    if not data.startswith(b'---\n'):
        return None
    head, sep, _ = data[4:].partition(b'\n---\n')
    if not sep:
        return None
    fields = {}
    for line in head.decode('utf-8', 'replace').split('\n'):
        key, colon, value = line.partition(':')
        if colon:
            fields[key] = value[1:] if value.startswith(' ') else value
    return fields


def locate(mbox, mid):
    """Every (state, receiver, path) that holds message <mid>."""
    found = []
    for state in STATES:
        pattern = os.path.join(glob.escape(mbox), state, '*', glob.escape(mid) + '.md')
        for path in sorted(glob.glob(pattern)):
            found.append((state, os.path.basename(os.path.dirname(path)), path))
    return found


def find_reply(mbox, mid):
    """The id of a file in new/, read/ or done/ of the sender with the probe topic and re: <mid>, or None."""
    for state in STATES:
        for path in sorted(glob.glob(os.path.join(glob.escape(mbox), state, SENDER, '*.md'))):
            fields = parse_message(path)
            if fields and fields.get('topic') == TOPIC and fields.get('re') == mid:
                return message_id(path)
    return None


def oracle(mbox, mid, host, messenger, isolated, spawned=False, states=()):
    """Return (stamps line, reasons). No reasons means pass."""
    found = locate(mbox, mid)
    where = [f'{s}/{r}/' for s, r, _ in found]
    fields = {}
    for state, _, path in found:
        if state == 'done' or not fields:
            fields = parse_message(path) or {}
    st, rt, at = (fields.get(k, '') for k in ('send_time', 'read_time', 'ack_time'))
    outcome = fields.get('outcome', '')
    reply = find_reply(mbox, mid)
    line = (f'send_time={st or "-"} read_time={rt or "-"} ack_time={at or "-"} '
            f'outcome={outcome or "-"} reply={reply or "none"}')
    if not messenger and not isolated:
        return line, ['not isolated']
    reasons = []
    if where != [f'done/{host}/']:
        reasons.append(f'message is in {", ".join(where) or "no folder"}, not only done/{host}/')
    empty = [k for k, v in (('send_time', st), ('read_time', rt), ('ack_time', at)) if not v]
    if empty:
        reasons.append('empty ' + ', '.join(empty))
    elif not all(TS_RE.fullmatch(v) for v in (st, rt, at)):
        reasons.append('a stamp is not a timestamp')
    elif not st <= rt <= at:
        reasons.append('stamps are not send_time <= read_time <= ack_time')
    if outcome in EXPIRED_OUTCOMES:
        reasons.append(f'outcome is {outcome}')
    if reply is None:
        reasons.append(f'no reply with topic {TOPIC} and re {mid}')
    if messenger:
        if not spawned:
            reasons.append('messenger not spawned')
        if list(states) != list(STATES):
            reasons.append('state lines are ' + (', '.join(states) or 'none') + ', not new, read, done')
    return line, reasons


class Sampler(threading.Thread):
    """Checks the mailbox every SAMPLE_EVERY seconds and records the first time the message is in each state."""

    def __init__(self, mbox, mid):
        super().__init__(daemon=True)
        self.mbox, self.mid = mbox, mid
        self.seen = []
        self.lock = threading.Lock()
        self.halt = threading.Event()

    def sample(self):
        with self.lock:
            have = {s for s, _ in self.seen}
            for state in STATES:
                if state in have:
                    continue
                pattern = os.path.join(glob.escape(self.mbox), state, '*', glob.escape(self.mid) + '.md')
                if glob.glob(pattern):
                    self.seen.append((state, utc_now()))

    def run(self):
        while True:
            self.sample()
            if self.halt.wait(SAMPLE_EVERY):
                break

    def finish(self):
        self.halt.set()
        self.join()
        self.sample()
        return list(self.seen)


# ---------------------------------------------------------------- host streams

class ClaudeTrace:
    """Reads Claude Code stream-json events."""

    def __init__(self):
        self.init, self.lines, self.ids = None, [], set()
        self.tool_calls = self.skill_calls = 0
        self.spawned = False

    def feed(self, ev):
        if ev.get('type') == 'system' and ev.get('subtype') == 'init':
            if self.init is None and not ev.get('parent_tool_use_id'):
                self.init = ev
            return
        if ev.get('type') != 'assistant':
            return
        in_sub = 'yes' if ev.get('parent_tool_use_id') else 'no'
        content = (ev.get('message') or {}).get('content') or []
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict) or block.get('type') != 'tool_use':
                continue
            bid = block.get('id')
            if bid is not None:
                if bid in self.ids:
                    continue
                self.ids.add(bid)
            name = str(block.get('name') or '?')
            args = block.get('input') if isinstance(block.get('input'), dict) else {}
            sub = str(args.get('subagent_type') or '-')
            cmd = args.get('command') if name == 'Bash' else None
            cmd = (one_line(str(cmd)[:160]).rstrip() if cmd else '') or '-'
            self.tool_calls += 1
            if name == 'Skill':
                self.skill_calls += 1
            if name in ('Agent', 'Task') and sub == CLAUDE_MESSENGER:
                self.spawned = True
            self.lines.append(f'tool={name} sub={sub} in_subagent={in_sub} cmd={cmd}')

    def has_messenger(self):
        agents = (self.init or {}).get('agents')
        return isinstance(agents, list) and CLAUDE_MESSENGER in [agent_name(a) for a in agents]

    def isolation(self):
        return claude_isolation(self.init, self.skill_calls)


def agent_name(entry):
    if isinstance(entry, dict):
        return str(entry.get('name') or '')
    return str(entry)


def claude_isolation(init, skill_calls):
    """(isolated, line) from the init event and the number of Skill tool calls."""
    init = init or {}
    counts = {}
    for key in ('skills', 'slash_commands'):
        value = init.get(key)
        counts[key] = len(value) if isinstance(value, list) else None
    agents = init.get('agents')
    counts['sdlc_agents'] = (sum(1 for a in agents if agent_name(a).startswith('sdlc-lite:'))
                             if isinstance(agents, list) else None)
    ok = all(v == 0 for v in counts.values()) and skill_calls == 0
    shown = {k: '?' if v is None else v for k, v in counts.items()}
    line = (f'isolation={"yes" if ok else "no"} skills={shown["skills"]} '
            f'slash_commands={shown["slash_commands"]} sdlc_agents={shown["sdlc_agents"]} '
            f'skill_calls={skill_calls}')
    return ok, line


class CodexTrace:
    """Reads codex exec --json events."""

    def __init__(self):
        self.thread_id, self.lines, self.done = None, [], set()
        self.tool_items = set()
        self.spawned = False

    def feed(self, ev):
        if ev.get('type') == 'thread.started' and self.thread_id is None:
            self.thread_id = ev.get('thread_id')
        item = ev.get('item')
        if not isinstance(item, dict):
            return
        itype = str(item.get('type') or '?')
        if itype in ('agent_message', 'reasoning'):
            return
        iid = item.get('id')
        key = iid if iid is not None else json.dumps(item, sort_keys=True)
        self.tool_items.add(key)
        if itype == 'command_execution' and (key, 'cmd') not in self.done and item.get('command'):
            self.done.add((key, 'cmd'))
            cmd = item['command']
            cmd = shlex.join(cmd) if isinstance(cmd, list) else str(cmd)
            self.lines.append(f'tool=shell cmd={one_line(cmd[:160]).rstrip() or "-"}')
        if (key, 'sub') not in self.done and CODEX_MESSENGER in json.dumps(item):
            self.done.add((key, 'sub'))
            self.spawned = True
            self.lines.append(f'tool={itype} sub={CODEX_MESSENGER}')

    @property
    def tool_calls(self):
        return len(self.tool_items)


def codex_home(env):
    return env.get('CODEX_HOME') or os.path.join(os.path.expanduser('~'), '.codex')


def find_rollout(home, thread_id):
    pattern = os.path.join(glob.escape(home), 'sessions', '**', f'rollout-*{glob.escape(thread_id)}*.jsonl')
    hits = sorted(glob.glob(pattern, recursive=True))
    return hits[0] if hits else None


def count_mentions(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read().count('sdlc-lite')


def codex_control(project, env, ignore):
    """One control call. Return the sdlc-lite mention count in its rollout file."""
    label = 'with --ignore-user-config' if ignore else 'without --ignore-user-config'
    cmd = (['codex', 'exec'] + (['--ignore-user-config'] if ignore else [])
           + ['--json', '--color', 'never', '--sandbox', 'read-only', '-C', project, '-m', 'gpt-6-luna',
              '-c', 'model_reasoning_effort="low"', CONTROL_PROMPT])
    note(f'codex control call {label}')
    try:
        r = subprocess.run(cmd, cwd=project, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, timeout=300, start_new_session=True)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Unverified(f'codex control call {label} failed: {e}') from None
    if r.returncode != 0:
        raise Unverified(f'codex control call {label} exited {r.returncode}')
    trace = CodexTrace()
    for raw in r.stdout.splitlines():
        try:
            ev = json.loads(raw)
        except ValueError:
            continue
        if isinstance(ev, dict):
            trace.feed(ev)
    if not trace.thread_id:
        raise Unverified(f'codex control call {label} printed no thread.started event')
    home = codex_home(env)
    for _ in range(10):
        path = find_rollout(home, trace.thread_id)
        if path:
            return count_mentions(path)
        time.sleep(1)
    raise Unverified(f'no rollout file for thread {trace.thread_id} under {home}/sessions')


def codex_isolation(project, env):
    """(isolated, line) from the two control calls."""
    ignored = codex_control(project, env, True)
    with_config = codex_control(project, env, False)
    ok = ignored == 0
    return ok, (f'isolation={"yes" if ok else "no"} ignore_config_sdlc_mentions={ignored} '
                f'with_config_sdlc_mentions={with_config}')


def host_command(arm, project, message):
    if arm == 'claude':
        return ['claude', '-p', '--safe-mode', '--disable-slash-commands', '--dangerously-skip-permissions',
                '--model', 'sonnet', '--effort', 'medium', '--output-format', 'stream-json', '--verbose',
                '--no-session-persistence', '--', f'Handle the message at {message}.']
    if arm == 'codex':
        return ['codex', 'exec', '--ignore-user-config', '--json', '--color', 'never', '-C', project,
                '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="medium"', '-c', 'approval_policy="never"',
                '--sandbox', 'workspace-write', f'Handle the message at {message}.']
    if arm == 'claude-messenger':
        return ['claude', '-p', '--plugin-dir', str(PLUGIN), '--dangerously-skip-permissions',
                '--model', 'sonnet', '--effort', 'medium', '--output-format', 'stream-json', '--verbose',
                '--no-session-persistence', '--', CLAUDE_PARENT_PROMPT]
    return ['codex', 'exec', '--json', '--color', 'never', '-C', project, '-m', 'gpt-6.1-sol',
            '-c', 'model_reasoning_effort="medium"', '-c', 'agents.enabled=true', '-c', 'approval_policy="never"',
            '--sandbox', 'workspace-write', CODEX_PARENT_PROMPT]


def kill_group(proc):
    """SIGTERM the host's own process group, then SIGKILL whatever is left after KILL_GRACE seconds."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    try:
        proc.wait(KILL_GRACE)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_host(cmd, project, env, tmp, timeout, feed, delayed=None):
    """Run the host, feed each JSON event to feed(ev). Return (exit code, timed out).

    delayed is (seconds, action): action runs that long after launch unless the host exited first.
    An exception from action kills the host and is re-raised here.
    """
    out_log = open(os.path.join(tmp, 'host-stdout.jsonl'), 'w', encoding='utf-8')
    err_log = open(os.path.join(tmp, 'host-stderr.txt'), 'w', encoding='utf-8')
    try:
        proc = subprocess.Popen(cmd, cwd=project, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=err_log, text=True, encoding='utf-8', errors='replace',
                                start_new_session=True)
    except OSError as e:
        out_log.close()
        err_log.close()
        raise Unverified(f'{cmd[0]} could not start: {e}') from None
    note(f'launched {cmd[0]} (pid {proc.pid}), timeout {timeout} s')
    timed_out, exited, failure = threading.Event(), threading.Event(), []

    def on_timeout():
        timed_out.set()
        note(f'timeout after {timeout} s, killing the host process group')
        kill_group(proc)

    def on_delay():
        if exited.wait(delayed[0]):
            return
        try:
            delayed[1]()
        except Exception as e:  # recorded and re-raised by the main thread
            failure.append(e)
            kill_group(proc)

    timer = threading.Timer(timeout, on_timeout)
    timer.daemon = True
    timer.start()
    helper = None
    if delayed is not None:
        helper = threading.Thread(target=on_delay, daemon=True)
        helper.start()
    try:
        for raw in proc.stdout:
            out_log.write(raw)
            out_log.flush()
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            if isinstance(ev, dict):
                feed(ev)
        rc = proc.wait()
    except BaseException:
        kill_group(proc)
        raise
    finally:
        timer.cancel()
        exited.set()
        out_log.close()
        err_log.close()
    if helper is not None:
        helper.join()
    try:
        os.killpg(proc.pid, signal.SIGTERM)  # leftovers in the host's own group only
    except (ProcessLookupError, PermissionError):
        pass
    note(f'{cmd[0]} exited {rc}')
    if failure:
        raise failure[0]
    return rc, timed_out.is_set()


# ---------------------------------------------------------------- one arm

def run_arm(arm, defect, timeout):
    host = HOST[arm]
    messenger = arm in MESSENGER_ARMS
    timeout = timeout or (MESSENGER_TIMEOUT if messenger else PATH_TIMEOUT)
    env = clean_env()
    emit(f'arm={arm}' + (' defect=yes' if defect else ''))
    try:
        tmp, project = setup(arm, env)
    except SetupError as e:
        emit(f'result=fail reason=setup error: {e}')
        return 2
    emit(f'project={project}')
    emit(f'plugin={PLUGIN}')
    note(f'host stdout and stderr: {tmp}/host-stdout.jsonl and host-stderr.txt')
    if shutil.which(host) is None:
        emit(f'result=unverified reason={host} is not on PATH')
        return 3
    mbox = mailbox_of(project)
    trace = ClaudeTrace() if host == 'claude' else CodexTrace()
    state = {'message': None, 'sampler': None}

    def do_send():
        path = send(project, host, env)
        state['message'] = path
        emit(f'message={path}')
        note(f'sent {path}')
        if defect:
            apply_defect(mbox)
            note('overwrote the mailbox AGENTS.md files with defect-AGENTS.md')
        sampler = Sampler(mbox, message_id(path))
        sampler.start()
        state['sampler'] = sampler

    iso_ok, iso_line = None, None
    try:
        if messenger:
            cmd = host_command(arm, project, None)
            rc, timed_out = run_host(cmd, project, env, tmp, timeout, trace.feed, delayed=(SEND_DELAY, do_send))
        else:
            do_send()
            if host == 'codex':
                iso_ok, iso_line = codex_isolation(project, env)
            cmd = host_command(arm, project, state['message'])
            rc, timed_out = run_host(cmd, project, env, tmp, timeout, trace.feed)
    except SetupError as e:
        if state['sampler'] is not None:
            state['sampler'].finish()
        emit(f'result=fail reason=setup error: {e}')
        return 2
    except Unverified as e:
        if state['sampler'] is not None:
            state['sampler'].finish()
        if iso_line:
            emit(iso_line)
        emit(f'result=unverified reason={e}')
        return 3

    seen = state['sampler'].finish() if state['sampler'] is not None else []
    if host == 'claude' and not messenger:
        iso_ok, iso_line = trace.isolation()
    if iso_line:
        emit(iso_line)
    for line in trace.lines:
        emit(line)
    for s, when in seen:
        emit(f'state={s} {when}')
    if messenger:
        emit(f'messenger_spawned={"yes" if trace.spawned else "no"}')

    message = state['message']
    reasons = []
    if message is not None:
        stamps, reasons = oracle(mbox, message_id(message), host, messenger, iso_ok,
                                 spawned=trace.spawned, states=[s for s, _ in seen])
        emit(stamps)
    else:
        reasons = ['the host exited before the message was sent']

    unverified = None
    if trace.tool_calls == 0 and timed_out:
        unverified = f'timeout after {timeout} s before any tool call'
    elif trace.tool_calls == 0 and rc != 0:
        unverified = f'{host} exited {rc} before any tool call'
    elif arm == 'claude-messenger' and not trace.has_messenger():
        unverified = f'init lacks {CLAUDE_MESSENGER}'
    elif arm == 'codex-messenger' and not trace.spawned:
        unverified = 'no native subagent spawn observed'
    if unverified:
        emit(f'result=unverified reason={unverified}')
        return 3
    if timed_out:
        reasons.insert(0, f'timeout after {timeout} s')
    if reasons:
        emit('result=fail reason=' + '; '.join(reasons))
        return 1
    emit('result=pass')
    return 0


# ---------------------------------------------------------------- selftest

def st_check(cond, reason):
    if not cond:
        raise AssertionError(reason)


def st_cli(project, env, *args):
    return run_checked(['python3', str(SCRIPTS / 'messages.py')] + list(args), project, env,
                       'messages.py ' + args[0])


def selftest():
    env = clean_env()
    tmp = None
    case = 'setup'
    try:
        tmp, project = setup('claude', env)
        mbox = mailbox_of(project)

        case = 'a: read, reply, ack gives pass'
        path = send(project, 'claude', env)
        mid = message_id(path)
        st_cli(project, env, 'read', path, '--receiver', 'claude')
        st_cli(project, env, 'reply', mid, '5')
        st_cli(project, env, 'ack', mid, '--outcome', 'answered 5')
        line, reasons = oracle(mbox, mid, 'claude', False, True)
        st_check(not reasons, f'expected pass, got {reasons}')
        st_check('reply=none' not in line and 'read_time=-' not in line, f'stamps line {line}')
        print(f'ok: {case}')

        case = 'b: read only gives fail'
        path = send(project, 'claude', env)
        mid = message_id(path)
        st_cli(project, env, 'read', path, '--receiver', 'claude')
        _, reasons = oracle(mbox, mid, 'claude', False, True)
        st_check(reasons, 'expected fail, got pass')
        st_check(any('read/claude/' in r for r in reasons), f'expected a folder miss, got {reasons}')
        print(f'ok: {case}')

        case = 'c: the defect flow gives fail'
        path = send(project, 'claude', env)
        mid = message_id(path)
        apply_defect(mbox)
        fixture = DEFECT.read_text(encoding='utf-8')
        for rel in DEFECT_FILES:
            with open(os.path.join(mbox, rel), encoding='utf-8') as f:
                st_check(f.read() == fixture, f'{rel} does not hold the defect fixture')
        for command in (DEFECT_CAT, DEFECT_MOVE):
            st_check(command in fixture, f'the fixture lacks {command!r}')
            shell = command.replace('<path>', shlex.quote(path)).replace('<receiver>', 'claude')
            r = subprocess.run(['sh', '-c', shell], cwd=project, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            st_check(r.returncode == 0, f'{shell!r} exited {r.returncode}')
        st_check([f'{s}/{r}' for s, r, _ in locate(mbox, mid)] == ['done/claude'], 'the defect flow did not move it')
        _, reasons = oracle(mbox, mid, 'claude', False, True)
        st_check(reasons, 'expected fail, got pass')
        st_check(any('read_time' in r for r in reasons), f'expected empty stamps, got {reasons}')
        print(f'ok: {case}')

        case = 'd: the Claude isolation parser gives no, then yes'
        verdicts = []
        for skills in (['sdlc-lite:chain'], []):
            trace = ClaudeTrace()
            trace.feed({'type': 'system', 'subtype': 'init', 'skills': skills, 'slash_commands': [],
                        'agents': ['claude', 'Explore', 'general-purpose', 'Plan'], 'mcp_servers': []})
            trace.feed({'type': 'assistant', 'parent_tool_use_id': None, 'message': {'content': [
                {'type': 'tool_use', 'id': 't1', 'name': 'Bash', 'input': {'command': 'ls'}}]}})
            verdicts.append(trace.isolation())
        st_check([ok for ok, _ in verdicts] == [False, True], f'verdicts {verdicts}')
        st_check(verdicts[1][1] == 'isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0',
                 f'line {verdicts[1][1]!r}')
        st_check(verdicts[0][1].startswith('isolation=no skills=1 '), f'line {verdicts[0][1]!r}')
        print(f'ok: {case}')

        case = 'e: the Codex rollout counter gives 0 and 2'
        home = os.path.join(tmp, 'codex-home')
        day = os.path.join(home, 'sessions', '2026', '10', '01')
        os.makedirs(day)
        ids = ('01a0f695-0000-7000-8000-00000000000a', '01a0f695-0000-7000-8000-00000000000b')
        bodies = ('{"type":"session_meta","payload":{"instructions":"none"}}\n',
                  '{"type":"session_meta","payload":{"skills":["sdlc-lite:chain"]}}\n'
                  '{"type":"response_item","payload":{"text":"plugin sdlc-lite enabled"}}\n')
        for tid, text in zip(ids, bodies):
            with open(os.path.join(day, f'rollout-2026-10-01T00-00-00-{tid}.jsonl'), 'w') as f:
                f.write(text)
        with open(os.path.join(day, 'rollout-2026-10-01T00-00-01-decoy.jsonl'), 'w') as f:
            f.write('sdlc-lite sdlc-lite sdlc-lite\n')
        counts = [count_mentions(find_rollout(home, tid)) for tid in ids]
        st_check(counts == [0, 2], f'counts {counts}')
        st_check(find_rollout(home, 'no-such-thread') is None, 'found a rollout for an unknown thread')
        print(f'ok: {case}')
    except (AssertionError, SetupError, OSError) as e:
        print(f'probe selftest: FAIL: {case}: {e}')
        return 1
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
    print('probe selftest: PASS')
    return 0


def main(argv):
    p = argparse.ArgumentParser(prog='probe.py', description='Messages live probe (T-0179).')
    p.add_argument('arm', choices=ARMS + ('selftest',))
    p.add_argument('--defect', action='store_true', help='inject the wrong mailbox AGENTS.md (claude or codex only)')
    p.add_argument('--timeout', type=int, metavar='SECONDS')
    a = p.parse_args(argv)
    if a.arm == 'selftest':
        if a.defect or a.timeout is not None:
            p.error('selftest takes no options')
        return selftest()
    if a.defect and a.arm not in ('claude', 'codex'):
        p.error('--defect is accepted only with claude or codex')
    if a.timeout is not None and a.timeout <= 0:
        p.error('--timeout must be a positive number of seconds')
    return run_arm(a.arm, a.defect, a.timeout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
