#!/usr/bin/env python3
"""Run a predefined SDLC Lite role in Codex, emitting the runner's normalized result event."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time

import codex_roles


def run(role, level, prompt, model=None, effort=None, request_file=None):
    root = codex_roles.ROOT
    definition = codex_roles.loads(root / 'adapters/codex/agents' / f'sdlc-{role}-{level.lower()}.toml')
    model = model or definition['model']
    effort = effort or definition['model_reasoning_effort']
    instructions = definition['developer_instructions'].replace(codex_roles.TOKEN, str(root))
    timeout = int(os.environ.get('SDLC_CODEX_TIMEOUT_SECONDS', '3600'))
    if timeout <= 0:
        raise ValueError('SDLC_CODEX_TIMEOUT_SECONDS must be positive')
    transport = os.environ.get('SDLC_CODEX_TRANSPORT', 'exec')
    if transport not in ('exec', 'subagent'):
        raise ValueError('unknown SDLC_CODEX_TRANSPORT: ' + transport)
    if transport == 'subagent':
        if not request_file and role in ('conductor', 'solo'):
            import uuid
            exchange_dir = Path.cwd() / '.sdlc'
            exchange_dir.mkdir(exist_ok=True)
            request_file = str(exchange_dir / ('native-' + role + '-' + uuid.uuid4().hex + '.request.json'))
        if not request_file:raise ValueError('subagent transport requires --request-file')
        from codex_exchange import wait_for_agent
        return wait_for_agent(role, level, prompt, model, effort, request_file, timeout)
    env = dict(os.environ, SDLC_BACKEND='codex', SDLC_HEADLESS='1', SDLC_ROLE=role)
    if role == 'conductor':
        # Setup happens in the launcher's context, before the conductor enters its sandbox.
        codex_roles.install(Path.cwd())
        env['SDLC_CODEX_TRANSPORT'] = 'subagent'
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='sdlc-codex-') as tmp:
        final = Path(tmp) / 'final.md'
        command = ['codex', 'exec', '--ephemeral', '--json', '--color', 'never',
                   '--model', model, '-c', 'model_reasoning_effort=' + json.dumps(effort),
                   '-c', 'developer_instructions=' + json.dumps(instructions, ensure_ascii=False),
                   '-c', 'agents.enabled=' + ('true' if role == 'conductor' else 'false'), '-c', 'approval_policy="never"',
                   '--sandbox', definition['sandbox_mode'], '--output-last-message', str(final), '-']
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=None, text=True, env=env, start_new_session=True)
        def stop(*_):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        old_handlers = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
        expired = threading.Event()
        def expire():
            expired.set()
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
        timer = threading.Timer(timeout, expire)
        timer.start()
        usage = None
        failed = False
        turns = 0
        try:
            process.stdin.write(prompt)
            process.stdin.close()
            for line in process.stdout:
                try:
                    event = json.loads(line)
                except ValueError:
                    event = {'text': line.rstrip()}
                # Retain raw Codex events without confusing the shared result selector.
                print(json.dumps({'type': 'codex_event', 'event': event}), flush=True)
                if event.get('type') in ('turn.failed', 'error'):
                    failed = True
                if event.get('type') == 'turn.completed':
                    turns += 1
                    usage = event.get('usage')
            rc = process.wait()
        finally:
            timer.cancel()
            if process.poll() is None:
                stop()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
        text = final.read_text() if final.exists() else ''
        failed = failed or rc != 0 or expired.is_set() or not text.strip()
        print(json.dumps({'type': 'result', 'backend': 'codex', 'is_error': failed,
                          'result': text, 'total_cost_usd': None,
                          'duration_ms': round((time.monotonic() - started) * 1000),
                          'num_turns': turns, 'usage': usage}), flush=True)
        if expired.is_set():
            print('Codex role timed out', file=sys.stderr)
        return 1 if failed else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('role'); p.add_argument('level'); p.add_argument('prompt')
    p.add_argument('--model'); p.add_argument('--effort'); p.add_argument('--request-file')
    args = p.parse_args()
    return run(args.role, args.level, args.prompt, args.model, args.effort, args.request_file)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print('Codex execution failed: ' + str(exc), file=sys.stderr)
        sys.exit(2)
