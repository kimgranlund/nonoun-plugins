#!/usr/bin/env python3
"""Live probe for T-0181: a fresh Claude Code or Codex host waits for mail with one blocking
`messages.py wait` call instead of polling, then handles the message it returned.

Usage: probe.py <claude|codex> [--timeout SECONDS]
       probe.py selftest

The host starts first with a prompt that names one `messages.py wait --receiver <arm> --timeout 120
--interval 2` call. SEND_DELAY seconds after launch the probe sends one message to the arm through
the real CLI and starts a 2-second mailbox sampler. The verdict passes only when the host made one
wait call, made no poll (count, list, sleep, Monitor, BashOutput, TaskOutput, a backgrounded Bash,
or a Codex write_stdin or cell wait), the wait started before the send and returned the sent id, and
the message was read, replied to, and acked.

The plugin is this worktree's plugins/sdlc-lite. Every host process gets the environment without
CLAUDECODE, CLAUDE_PLUGIN_ROOT, CLAUDE_PLUGIN_DATA, CLAUDE_CODE_*, SDLC_*, BASH_DEFAULT_TIMEOUT_MS
and BASH_MAX_TIMEOUT_MS, so the Claude host runs with its default Bash limits. The throwaway project
is kept and its path printed; the host's raw stdout and stderr are saved next to it, as
host-stdout.jsonl and host-stderr.txt.

Output: key=value lines on stdout (arm, project, plugin, message, isolation, trace, state,
wait_calls and poll_calls, wait_returned, wait_before_send, stamps, result); progress notes on stderr.
Exit 0 pass, 1 fail, 2 setup error, 3 unverified (the host cannot run).

selftest runs offline (no model call): synthetic host events and rollout files, plus a real
messages.py send, read, reply, and ack. It prints `ok: <case>` per case, then `probe selftest: PASS`.
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

PLUGIN = Path(__file__).resolve().parents[3] / 'plugins' / 'sdlc-lite'
SCRIPTS = PLUGIN / 'scripts'

ARMS = ('claude', 'codex')
STATES = ('new', 'read', 'done')
SENDER = 'probe'
TOPIC = 'live-probe'
BODY = 'What is 2 + 3? Answer in one line.'
SEND_DELAY = 20
SAMPLE_EVERY = 2
PATH_TIMEOUT = 600
KILL_GRACE = 10
ROLLOUT_TRIES = 10
EXPIRED_OUTCOMES = ('expired', 'expired, no reply')
TS_RE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z')
TS_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'
ID_RE = re.compile(r'[0-9]{8}T[0-9]{12}Z-[a-z0-9]+(-[a-z0-9]+)*')
SUB_RE = re.compile(r'messages\.py["\']?\s+(?:--root\s+\S+\s+)?([a-z]+)')
SLEEP_RE = re.compile(r'(?<![\w.-])sleep(?![\w-])')
POLL_SUBCOMMANDS = ('count', 'list')
CLAUDE_POLL_TOOLS = ('Monitor', 'BashOutput', 'TaskOutput')
CODEX_POLL_FUNCTIONS = ('wait', 'write_stdin')
DROPPED_ENV = ('CLAUDECODE', 'CLAUDE_PLUGIN_ROOT', 'CLAUDE_PLUGIN_DATA',
               'BASH_DEFAULT_TIMEOUT_MS', 'BASH_MAX_TIMEOUT_MS')

PROMPT = (
    'Run this as one shell command and wait for it to finish: python3 {plugin}/scripts/messages.py wait '
    '--receiver {harness} --timeout 120 --interval 2. If your shell tool takes a timeout or a yield time, '
    'set it to at least 130000 milliseconds, so the call returns only when the command ends. When it '
    'prints a message id, handle that message as .sdlc/messages/AGENTS.md says: claim it with read, '
    'reply when follow_up_requested is true, then ack it. Then stop.')
CONTROL_PROMPT = 'Reply with exactly OK. Do not call tools.'


class SetupError(Exception):
    """Exit 2."""


class Unverified(Exception):
    """Exit 3. The message is the detail after `host cannot run: `."""


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
    """A copy of the environment without the host session, plugin root, sdlc runner, and Bash limit variables."""
    env = dict(os.environ if base is None else base)
    for key in list(env):
        if key in DROPPED_ENV or key.startswith('CLAUDE_CODE_') or key.startswith('SDLC_'):
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


def setup(env):
    """Make the throwaway project. Return (tmp, project), both real paths."""
    try:
        tmp = os.path.realpath(tempfile.mkdtemp(prefix='messages-wait-live-'))
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
    if not os.path.isfile(os.path.join(mailbox_of(project), 'AGENTS.md')):
        raise SetupError('tickets.py roadmap wrote no AGENTS.md in the mailbox')
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


def host_missing(host, env):
    """`host cannot run: ...` when <host> is not on the PATH of env, else None."""
    if shutil.which(host, path=env.get('PATH', os.defpath)) is None:
        return f'host cannot run: {host} is not on PATH'
    return None


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


def message_fields(mbox, mid):
    """The front matter of message <mid>, from its done/ copy when there is one."""
    fields = {}
    for state, _, path in locate(mbox, mid):
        if state == 'done' or not fields:
            fields = parse_message(path) or {}
    return fields


def oracle(mbox, mid, host, isolated):
    """The T-0179 path-only oracle. Return (stamps line, reasons). No reasons means pass."""
    found = locate(mbox, mid)
    where = [f'{s}/{r}/' for s, r, _ in found]
    fields = message_fields(mbox, mid)
    st, rt, at = (fields.get(k, '') for k in ('send_time', 'read_time', 'ack_time'))
    outcome = fields.get('outcome', '')
    reply = find_reply(mbox, mid)
    line = (f'send_time={st or "-"} read_time={rt or "-"} ack_time={at or "-"} '
            f'outcome={outcome or "-"} reply={reply or "none"}')
    if not isolated:
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


# ---------------------------------------------------------------- command classification

def classify(command):
    """(subcommands, sleeps) for one shell command string."""
    return SUB_RE.findall(command), len(SLEEP_RE.findall(command))


def first_field(output):
    """The first tab-separated field of the first line of a wait output, or `-` when it is not an id."""
    lines = (output or '').splitlines()
    field = lines[0].split('\t', 1)[0].strip() if lines else ''
    return field if ID_RE.fullmatch(field) else '-'


class Counts:
    """Shell commands seen, plus host-specific polls, for one host run."""

    def __init__(self):
        self.commands = []        # each shell command string, once per tool call or item
        self.tool_polls = 0       # Monitor, BashOutput, TaskOutput, backgrounded Bash
        self.wait_seen_at = None  # utc_now() at receipt of the first wait call's event
        self.wait_output = None   # that call's output, when seen

    def note_command(self, command, seen_at):
        self.commands.append(command)
        subs, _ = classify(command)
        if 'wait' in subs and self.wait_seen_at is None:
            self.wait_seen_at = seen_at
            return True
        return False

    def wait_calls(self):
        return sum(classify(c)[0].count('wait') for c in self.commands)

    def shell_polls(self):
        n = 0
        for c in self.commands:
            subs, sleeps = classify(c)
            n += sum(1 for s in subs if s in POLL_SUBCOMMANDS) + sleeps
        return n


# ---------------------------------------------------------------- host streams

class ClaudeTrace:
    """Reads Claude Code stream-json events."""

    def __init__(self):
        self.init, self.lines, self.ids = None, [], set()
        self.tool_calls = self.skill_calls = 0
        self.counts = Counts()
        self.wait_id = None
        self.thread_id = None

    def feed(self, ev):
        if ev.get('type') == 'system' and ev.get('subtype') == 'init':
            if self.init is None and not ev.get('parent_tool_use_id'):
                self.init = ev
            return
        content = (ev.get('message') or {}).get('content') or []
        content = content if isinstance(content, list) else []
        if ev.get('type') == 'user':
            for block in content:
                if (isinstance(block, dict) and block.get('type') == 'tool_result' and self.wait_id is not None
                        and block.get('tool_use_id') == self.wait_id and self.counts.wait_output is None):
                    self.counts.wait_output = result_text(block.get('content'))
            return
        if ev.get('type') != 'assistant':
            return
        seen_at = utc_now()
        in_sub = 'yes' if ev.get('parent_tool_use_id') else 'no'
        for block in content:
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
            background = name == 'Bash' and args.get('run_in_background') is True
            self.tool_calls += 1
            if name == 'Skill':
                self.skill_calls += 1
            if name in CLAUDE_POLL_TOOLS or background:
                self.counts.tool_polls += 1
            cmd = args.get('command') if name == 'Bash' else None
            if isinstance(cmd, str):
                if self.counts.note_command(cmd, seen_at):
                    self.wait_id = bid
            shown = (one_line(str(cmd)[:160]).rstrip() if cmd else '') or '-'
            self.lines.append(f'tool={name} sub={sub} in_subagent={in_sub} '
                              f'background={"yes" if background else "no"} cmd={shown}')

    def isolation(self):
        return claude_isolation(self.init, self.skill_calls)


def result_text(content):
    """A tool_result content, a string or a list of {type: text, text} blocks, as one string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return ''.join(str(b.get('text') or '') for b in content
                       if isinstance(b, dict) and b.get('type') == 'text')
    return ''


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
        self.thread_id, self.lines = None, []
        self.tool_items = set()
        self.first_seen = {}
        self.cmd_items = set()
        self.counts = Counts()
        self.wait_id = None

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
        if key not in self.first_seen:
            self.first_seen[key] = utc_now()
        if itype != 'command_execution':
            return
        if key not in self.cmd_items and item.get('command'):
            self.cmd_items.add(key)
            cmd = item['command']
            cmd = shlex.join(cmd) if isinstance(cmd, list) else str(cmd)
            if self.counts.note_command(cmd, self.first_seen[key]):
                self.wait_id = key
            self.lines.append(f'tool=shell cmd={one_line(cmd[:160]).rstrip() or "-"}')
        if (ev.get('type') == 'item.completed' and key == self.wait_id and self.wait_id is not None
                and self.counts.wait_output is None):
            self.counts.wait_output = str(item.get('aggregated_output') or '')

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


def rollout_polls(path):
    """Codex polls in a rollout: function_call wait or write_stdin lines, and write_stdin( in exec cells."""
    n = 0
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            payload = ev.get('payload') if isinstance(ev, dict) else None
            if not isinstance(payload, dict):
                continue
            if payload.get('type') == 'function_call' and payload.get('name') in CODEX_POLL_FUNCTIONS:
                n += 1
            elif payload.get('type') == 'custom_tool_call' and isinstance(payload.get('input'), str):
                n += payload['input'].count('write_stdin(')
    return n


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
    for _ in range(ROLLOUT_TRIES):
        path = find_rollout(home, trace.thread_id)
        if path:
            return count_mentions(path)
        time.sleep(1)
    raise Unverified(f'codex control call {label} left no rollout file for thread {trace.thread_id} '
                     f'under {home}/sessions')


def codex_isolation(project, env):
    """(isolated, line) from the two control calls."""
    ignored = codex_control(project, env, True)
    with_config = codex_control(project, env, False)
    ok = ignored == 0
    return ok, (f'isolation={"yes" if ok else "no"} ignore_config_sdlc_mentions={ignored} '
                f'with_config_sdlc_mentions={with_config}')


def host_command(arm, project):
    prompt = PROMPT.format(plugin=PLUGIN, harness=arm)
    if arm == 'claude':
        return ['claude', '-p', '--safe-mode', '--disable-slash-commands', '--dangerously-skip-permissions',
                '--model', 'sonnet', '--effort', 'low', '--output-format', 'stream-json', '--verbose',
                '--no-session-persistence', '--', prompt]
    return ['codex', 'exec', '--ignore-user-config', '--json', '--color', 'never', '-C', project,
            '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="medium"', '-c', 'approval_policy="never"',
            '--sandbox', 'workspace-write', prompt]


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


# ---------------------------------------------------------------- verdict

def measure(trace, env, tries=ROLLOUT_TRIES):
    """The four trace values as a dict, plus `missing`: a fail reason when Codex polls cannot be counted."""
    c = trace.counts
    polls = c.shell_polls() + c.tool_polls
    missing = None
    if isinstance(trace, CodexTrace):
        tid = trace.thread_id or '-'
        path = None
        home = codex_home(env)
        for i in range(tries):
            path = find_rollout(home, trace.thread_id) if trace.thread_id else None
            if path or i == tries - 1:
                break
            time.sleep(1)
        if path:
            polls += rollout_polls(path)
        else:
            missing = f'no rollout file for thread {tid}, so polls cannot be counted'
    return {'wait_calls': c.wait_calls(), 'poll_calls': polls,
            'wait_returned': first_field(c.wait_output) if c.wait_seen_at is not None else '-',
            'wait_seen_at': c.wait_seen_at, 'missing': missing}


def judge(mbox, mid, host, isolated, values, timed_out, timeout):
    """The verdict. Return (output lines, reasons). No reasons means pass.

    The lines are wait_calls and poll_calls, wait_returned, wait_before_send, and the stamps line.
    """
    send_time = message_fields(mbox, mid).get('send_time', '') if mid else ''
    seen_at = values['wait_seen_at']
    before = 'yes' if seen_at and send_time and seen_at < send_time else 'no'
    if mid:
        stamps, found = oracle(mbox, mid, host, isolated)
    else:
        stamps = 'send_time=- read_time=- ack_time=- outcome=- reply=none'
        found = ['the host exited before the message was sent']
    lines = [f'wait_calls={values["wait_calls"]} poll_calls={values["poll_calls"]}',
             f'wait_returned={values["wait_returned"]}',
             f'wait_before_send={before}',
             stamps]
    reasons = []
    if timed_out:
        reasons.append(f'timeout after {timeout} s')
    if values['wait_calls'] != 1:
        reasons.append(f'wait_calls={values["wait_calls"]}')
    if values['missing']:
        reasons.append(values['missing'])
    if values['poll_calls'] != 0:
        reasons.append(f'poll_calls={values["poll_calls"]}')
    if mid and values['wait_returned'] != mid:
        reasons.append(f'wait_returned={values["wait_returned"]}, not {mid}')
    if before != 'yes':
        reasons.append('wait_before_send=no')
    reasons.extend(found)
    return lines, reasons


# ---------------------------------------------------------------- one arm

def run_arm(arm, timeout):
    host = arm
    timeout = timeout or PATH_TIMEOUT
    env = clean_env()
    emit(f'arm={arm}')
    try:
        tmp, project = setup(env)
    except SetupError as e:
        emit(f'result=fail reason=setup error: {e}')
        return 2
    emit(f'project={project}')
    emit(f'plugin={PLUGIN}')
    note(f'host stdout and stderr: {tmp}/host-stdout.jsonl and host-stderr.txt')
    missing = host_missing(host, env)
    if missing:
        emit(f'result=unverified reason={missing}')
        return 3
    mbox = mailbox_of(project)
    trace = ClaudeTrace() if host == 'claude' else CodexTrace()
    state = {'message': None, 'sampler': None}

    def do_send():
        path = send(project, host, env)
        state['message'] = path
        emit(f'message={path}')
        note(f'sent {path}')
        sampler = Sampler(mbox, message_id(path))
        sampler.start()
        state['sampler'] = sampler

    iso_ok, iso_line = None, None
    try:
        if host == 'codex':
            iso_ok, iso_line = codex_isolation(project, env)
        rc, timed_out = run_host(host_command(arm, project), project, env, tmp, timeout, trace.feed,
                                 delayed=(SEND_DELAY, do_send))
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
        emit(f'result=unverified reason=host cannot run: {e}')
        return 3

    seen = state['sampler'].finish() if state['sampler'] is not None else []
    if host == 'claude':
        iso_ok, iso_line = trace.isolation()
    emit(iso_line)
    for line in trace.lines:
        emit(line)
    for s, when in seen:
        emit(f'state={s} {when}')

    unverified = None
    if trace.tool_calls == 0 and timed_out:
        unverified = f'timeout after {timeout} s before any tool call'
    elif trace.tool_calls == 0 and rc != 0:
        unverified = f'{host} exited {rc} before any tool call'
    values = measure(trace, env, tries=1 if unverified else ROLLOUT_TRIES)
    message = state['message']
    lines, reasons = judge(mbox, message_id(message) if message else None, host, iso_ok, values,
                           timed_out, timeout)
    for line in lines:
        emit(line)
    if unverified:
        emit(f'result=unverified reason=host cannot run: {unverified}')
        return 3
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


def st_wait_cmd(host):
    return f'python3 "{SCRIPTS}/messages.py" wait --receiver {host} --timeout 120 --interval 2'


def st_bash(bid, command, background=False):
    args = {'command': command}
    if background:
        args['run_in_background'] = True
    return {'type': 'assistant', 'parent_tool_use_id': None, 'message': {'content': [
        {'type': 'tool_use', 'id': bid, 'name': 'Bash', 'input': args}]}}


def st_tool(bid, name, args):
    return {'type': 'assistant', 'parent_tool_use_id': None, 'message': {'content': [
        {'type': 'tool_use', 'id': bid, 'name': name, 'input': args}]}}


def st_result(bid, text, as_list=False):
    content = [{'type': 'text', 'text': text}] if as_list else text
    return {'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': bid, 'content': content}]}}


ST_INIT = {'type': 'system', 'subtype': 'init', 'skills': [], 'slash_commands': [],
           'agents': ['claude', 'Explore', 'general-purpose', 'Plan'], 'mcp_servers': []}


def st_item(kind, iid, command, output=None):
    item = {'id': iid, 'type': 'command_execution', 'command': command,
            'status': 'completed' if kind == 'item.completed' else 'in_progress'}
    if output is not None:
        item['aggregated_output'] = output
        item['exit_code'] = 0
    return {'type': kind, 'item': item}


def st_handle_claude(mid):
    return [st_bash('h1', f'python3 "{SCRIPTS}/messages.py" read {mid} --receiver claude'),
            st_bash('h2', f'python3 "{SCRIPTS}/messages.py" reply {mid} "5"'),
            st_bash('h3', f'python3 "{SCRIPTS}/messages.py" ack {mid} --outcome "answered 5"')]


def st_handle_codex(mid):
    out = []
    for n, sub in enumerate((f'read {mid} --receiver codex', f'reply {mid} "5"', f'ack {mid} --outcome "answered 5"')):
        cmd = f'/bin/zsh -lc \'python3 "{SCRIPTS}/messages.py" {sub}\''
        out += [st_item('item.started', f'item_h{n}', cmd), st_item('item.completed', f'item_h{n}', cmd, 'ok\n')]
    return out


def st_rollout(home, tid, extra=()):
    """Write a rollout for thread tid: one exec cell that runs the wait through tools.exec_command only."""
    day = os.path.join(home, 'sessions', '2026', '10', '01')
    os.makedirs(day, exist_ok=True)
    cell = ('text(await tools.exec_command({cmd:"python3 messages.py wait --receiver codex --timeout 120 '
            '--interval 2","yield_time_ms":130000}));\n')
    lines = [{'type': 'session_meta', 'payload': {'id': tid}},
             {'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'name': 'exec', 'input': cell,
                                                   'call_id': 'call_1'}}]
    lines += list(extra)
    with open(os.path.join(day, f'rollout-2026-10-01T00-00-00-{tid}.jsonl'), 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(json.dumps(line) + '\n')


def st_run(project, env, host, before, after, home=None, rollout_extra=None):
    """Feed before, send a real message, feed after(mid, path), handle it through the CLI, and judge."""
    trace = ClaudeTrace() if host == 'claude' else CodexTrace()
    for ev in before:
        trace.feed(ev)
    path = send(project, host, env)
    mid = message_id(path)
    for ev in after(mid, path):
        trace.feed(ev)
    st_cli(project, env, 'read', mid, '--receiver', host)
    st_cli(project, env, 'reply', mid, '5')
    st_cli(project, env, 'ack', mid, '--outcome', 'answered 5')
    run_env = dict(env)
    if host == 'codex':
        run_env['CODEX_HOME'] = home
        st_rollout(home, trace.thread_id, rollout_extra or ())
        isolated = True
    else:
        isolated, _ = trace.isolation()
    values = measure(trace, run_env, tries=1)
    lines, reasons = judge(mailbox_of(project), mid, host, isolated, values, False, PATH_TIMEOUT)
    return mid, lines, reasons


def st_fail(reasons, want):
    st_check(reasons, 'expected fail, got pass')
    st_check(any(r.startswith(want) for r in reasons), f'expected a reason {want!r}, got {reasons}')


def selftest():
    env = clean_env()
    tmp = None
    case = 'setup'
    try:
        tmp, project = setup(env)
        home = os.path.join(tmp, 'codex-home')
        wait_c = st_wait_cmd('claude')
        wait_x = f'/bin/zsh -lc \'{st_wait_cmd("codex")}\''

        def claude_ok(mid, path):
            return [st_result('w1', f'{mid}\t{path}\n', as_list=True)] + st_handle_claude(mid)

        def codex_ok(mid, path):
            return [st_item('item.completed', 'item_w', wait_x, f'{mid}\t{path}\n')] + st_handle_codex(mid)

        codex_before = [{'type': 'thread.started', 'thread_id': '01a0f695-0000-7000-8000-0000000000c1'},
                        st_item('item.started', 'item_w', wait_x)]

        case = 'pass: one wait call returned the id, then read, reply, ack'
        mid, lines, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('w1', wait_c)], claude_ok)
        st_check(not reasons, f'expected pass, got {reasons}')
        st_check(lines[:3] == ['wait_calls=1 poll_calls=0', f'wait_returned={mid}', 'wait_before_send=yes'],
                 f'lines {lines}')
        print(f'ok: {case}')

        case = 'pass: a Codex wait call with no poll in the rollout'
        mid, lines, reasons = st_run(project, env, 'codex', codex_before, codex_ok, home=home)
        st_check(not reasons, f'expected pass, got {reasons}')
        st_check(lines[:3] == ['wait_calls=1 poll_calls=0', f'wait_returned={mid}', 'wait_before_send=yes'],
                 f'lines {lines}')
        print(f'ok: {case}')

        case = 'fail: two wait calls'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('w1', wait_c), st_bash('w2', wait_c)],
                               claude_ok)
        st_fail(reasons, 'wait_calls=2')
        print(f'ok: {case}')

        case = 'fail: a count call'
        count = f'python3 "{SCRIPTS}/messages.py" count --receiver claude'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('c1', count), st_bash('w1', wait_c)],
                               claude_ok)
        st_fail(reasons, 'poll_calls=1')
        print(f'ok: {case}')

        case = 'fail: a Monitor call'
        monitor = st_tool('m1', 'Monitor', {'command': 'until test -n "$(ls .sdlc/messages/new/claude)"; do :; done'})
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('w1', wait_c), monitor], claude_ok)
        st_fail(reasons, 'poll_calls=1')
        print(f'ok: {case}')

        case = 'fail: a backgrounded wait call'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('w1', wait_c, background=True)],
                               lambda mid, path: [st_result('w1', 'Command running in background with ID: b1')]
                               + st_handle_claude(mid))
        st_fail(reasons, 'poll_calls=1')
        print(f'ok: {case}')

        case = 'fail: no wait call'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT], lambda mid, path: st_handle_claude(mid))
        st_fail(reasons, 'wait_calls=0')
        print(f'ok: {case}')

        case = 'fail: the wait started after the send'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT],
                               lambda mid, path: [st_bash('w1', wait_c)] + claude_ok(mid, path))
        st_fail(reasons, 'wait_before_send=no')
        st_check(not any(r.startswith(('wait_calls=', 'poll_calls=', 'wait_returned=')) for r in reasons),
                 f'expected only the late wait, got {reasons}')
        print(f'ok: {case}')

        case = 'fail: the wait returned another id'
        other = '20260101T000000000000Z-other-topic'
        _, _, reasons = st_run(project, env, 'claude', [ST_INIT, st_bash('w1', wait_c)],
                               lambda mid, path: [st_result('w1', f'{other}\t/x/{other}.md\n')]
                               + st_handle_claude(mid))
        st_fail(reasons, f'wait_returned={other}')
        print(f'ok: {case}')

        case = 'fail: a Codex write_stdin poll'
        cell = ('text(await tools.exec_command({cmd:"python3 messages.py wait --receiver codex",'
                '"yield_time_ms":1000}));\ntext(await tools.write_stdin({session_id:1,chars:""}));\n')
        poll = {'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'name': 'exec', 'input': cell,
                                                     'call_id': 'call_2'}}
        codex_before[0]['thread_id'] = '01a0f695-0000-7000-8000-0000000000c2'
        _, _, reasons = st_run(project, env, 'codex', codex_before, codex_ok, home=home, rollout_extra=[poll])
        st_fail(reasons, 'poll_calls=1')
        print(f'ok: {case}')

        case = 'fail: a Codex cell wait'
        cell_wait = {'type': 'response_item', 'payload': {'type': 'function_call', 'name': 'wait',
                                                          'arguments': '{"cell_id":"1"}', 'call_id': 'call_3'}}
        codex_before[0]['thread_id'] = '01a0f695-0000-7000-8000-0000000000c3'
        _, _, reasons = st_run(project, env, 'codex', codex_before, codex_ok, home=home, rollout_extra=[cell_wait])
        st_fail(reasons, 'poll_calls=1')
        print(f'ok: {case}')

        case = 'unverified: a host not on PATH says host cannot run'
        empty = os.path.join(tmp, 'empty-path')
        os.mkdir(empty)
        reasons = [host_missing(h, dict(env, PATH=empty)) for h in ARMS]
        st_check(all(r and r.startswith('host cannot run: ') for r in reasons), f'reasons {reasons}')
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
    p = argparse.ArgumentParser(prog='probe.py', description='Messages wait live probe (T-0181).')
    p.add_argument('arm', choices=ARMS + ('selftest',))
    p.add_argument('--timeout', type=int, metavar='SECONDS')
    a = p.parse_args(argv)
    if a.arm == 'selftest':
        if a.timeout is not None:
            p.error('selftest takes no options')
        return selftest()
    if a.timeout is not None and a.timeout <= 0:
        p.error('--timeout must be a positive number of seconds')
    return run_arm(a.arm, a.timeout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
