#!/usr/bin/env python3
"""Own a handoff-directory lock and durable attempt record across either host backend."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

import readiness


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, data):
    temp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)


def lock(directory):
    handle = (directory / '.run.lock').open('a+')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise ValueError('A run still owns this handoff directory; wait or stop that owned run before retrying: ' + str(directory))
    return handle


def recover(directory):
    directory = Path(directory).resolve()
    with lock(directory):
        changed = []
        for path in directory.glob('*.attempt.json'):
            data = json.loads(path.read_text())
            if data['status'] == 'running':
                data.update(status='interrupted', finished_at=now(), recovery='Owner lock released without a terminal record. Inspect artifacts and working tree before a new attempt.')
                write(path, data)
                marker = directory / (data['role'] + '-' + data['level'] + '.running')
                if marker.parent != directory:
                    raise ValueError('invalid role in attempt record: ' + str(path))
                marker.unlink(missing_ok=True)
                changed.append(path.name)
        return changed


def run(role, level, handoff, backend, model, effort):
    directory = handoff.resolve().parent
    transport = os.environ.get('SDLC_CODEX_TRANSPORT', 'exec') if backend == 'codex' else 'exec'
    if transport not in ('exec', 'subagent'):
        raise ValueError('Unknown transport: ' + transport)
    check = readiness.inspect(Path.cwd(), backend, transport)
    if not check['ready']:
        raise ValueError('\n'.join(check['errors']))
    with lock(directory) as owner:
        stale = [p.name for p in directory.glob('*.attempt.json') if json.loads(p.read_text()).get('status') == 'running']
        if stale:
            raise ValueError('Interrupted attempt needs review; run run_lifecycle.py recover "' + str(directory) + '": ' + ', '.join(stale))
        stem = role + '-' + level
        name = stem
        n = 1
        while any(directory.glob(name + '.*')):
            n += 1
            name = stem + '-' + str(n)
        attempt = uuid.uuid4().hex
        reason = os.environ.get('SDLC_ROUTING_REASON', '').strip()
        data = dict(attempt_id=attempt, name=name, role=role, level=level, backend=backend,
                    transport=transport, model=model, effort=effort,
                    routing_reason=reason or 'Caller selected this role and level; no task-specific rationale supplied.',
                    reason_source='caller' if reason else 'fallback', status='running', started_at=now(),
                    project=str(Path.cwd()), handoff=str(handoff.resolve()), owner_pid=os.getpid())
        path = directory / (name + '.attempt.json')
        write(path, data)
        env = dict(os.environ, SDLC_ATTEMPT_ID=attempt, SDLC_ATTEMPT_NAME=name,
                   SDLC_ROUTING_REASON=data['routing_reason'], SDLC_LIFECYCLE_CHILD='1')
        process = None
        interrupted = []
        def stop(sig, _):
            interrupted.append(sig)
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        previous = {s: signal.signal(s, stop) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        rc = 1
        try:
            process = subprocess.Popen(['bash', str(readiness.ROOT/'scripts/run.sh'), role, level, str(handoff)],
                                       env=env, start_new_session=True, pass_fds=(owner.fileno(),))
            data['process_pid'] = process.pid
            write(path, data)
            deadline = None
            while process.poll() is None:
                if interrupted:
                    deadline = deadline or time.monotonic() + 5
                    if time.monotonic() >= deadline:
                        os.killpg(process.pid, signal.SIGKILL)
                time.sleep(.1)
            rc = 128 + interrupted[0] if interrupted else process.returncode
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            data.update(status='interrupted' if interrupted else ('completed' if rc == 0 else 'failed'), exit_code=rc, finished_at=now())
            write(path, data)
        return rc


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    r = sub.add_parser('run')
    for key in ('role', 'level', 'handoff', 'backend', 'model', 'effort'):
        r.add_argument(key)
    for command in ('status', 'recover'):
        sub.add_parser(command).add_argument('directory', type=Path)
    a = p.parse_args()
    if a.command == 'run':
        return run(a.role, a.level, Path(a.handoff), a.backend, a.model, a.effort)
    if a.command == 'recover':
        print(json.dumps(dict(recovered=recover(a.directory), next='Inspect artifacts and working tree, then rerun the original command as a new attempt. Never replay an old report.')))
    else:
        print(json.dumps([json.loads(p.read_text()) for p in sorted(a.directory.glob('*.attempt.json'))], indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
