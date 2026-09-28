#!/usr/bin/env python3
"""Request/result transport for native in-session subagents; never launches a model CLI."""
import json
import os
from pathlib import Path
import signal
import sys
import time

import codex_roles


def wait_for_agent(role, level, prompt, model, effort, request_file, timeout):
    started = time.monotonic()
    request = Path(request_file).resolve()
    response = request.with_suffix('.response.json')
    if request.exists() or response.exists():
        raise ValueError('native exchange already exists: ' + str(request))
    agent = f'sdlc-{role}-{level.lower()}'
    default_model = codex_roles.models()[role][level][0]
    if role == 'verifier' and model != default_model:
        agent += '-alternate'
    context = '\n'.join(f'{key}={os.environ[key]}' for key in ('SDLC_BASE_SHA','SDLC_TMP_WORKTREES') if key in os.environ)
    message = 'Project working directory: ' + str(Path.cwd()) + '\nRun all project commands from that directory, even if your default cwd differs.\n' + prompt + '\n\nRunner context (use these exact values in commands when needed):\n' + context
    payload = dict(agent=agent, role=role, level=level, model=model, effort=effort,
                   prompt=message, response_path=str(response), status='waiting')
    temp = request.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, indent=2)+'\n');temp.replace(request)
    interrupted = [False]
    def interrupt(*_):
        interrupted[0] = True
    previous = {s: signal.signal(s, interrupt) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    report = ''; failed = True; usage = None
    try:
        while not interrupted[0] and time.monotonic()-started < timeout:
            if response.exists():
                data = json.loads(response.read_text())
                report = data.get('report', '')
                usage = data.get('usage')
                failed = data.get('is_error', False) or not isinstance(report, str) or not report.strip()
                break
            time.sleep(0.1)
        else:
            payload['error'] = 'cancelled' if interrupted[0] else 'native agent response timed out'
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        payload['error'] = 'invalid native response: ' + str(exc)
    finally:
        for sig, handler in previous.items():signal.signal(sig, handler)
    payload['status'] = 'failed' if failed else 'received'
    request.write_text(json.dumps(payload, indent=2)+'\n')
    print(json.dumps(dict(type='result', backend='codex', transport='subagent', is_error=bool(failed),
                         result=report if isinstance(report,str) else '', usage=usage,
                         duration_ms=round((time.monotonic()-started)*1000), num_turns=None, total_cost_usd=None)),flush=True)
    if payload.get('error'):print(payload['error'],file=sys.stderr)
    return 1 if failed else 0


def respond(request_path, report_path, failed=False):
    request = Path(request_path).resolve()
    payload = json.loads(request.read_text())
    if payload.get('status') != 'waiting':
        raise ValueError('native request is no longer waiting')
    # Do not trust an arbitrary destination embedded in JSON to select a write target.
    response = request.with_suffix('.response.json')
    if str(response) != payload['response_path'] or response.exists():
        raise ValueError('invalid or already answered native request')
    report = Path(report_path).read_text()
    if not report.strip():raise ValueError('empty agent report')
    temp = response.with_suffix('.tmp')
    temp.write_text(json.dumps(dict(report=report,is_error=failed))+'\n');temp.replace(response)
    print(response)


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('request');p.add_argument('report');p.add_argument('--failed',action='store_true')
    a=p.parse_args()
    try:respond(a.request,a.report,a.failed)
    except (OSError,ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(2)
