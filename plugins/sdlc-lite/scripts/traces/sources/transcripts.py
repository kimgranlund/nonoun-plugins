"""Transcript reader: one role's stream-json .log.

read(log_path) returns one record:
  tool_calls   count of tool_use blocks in assistant events;
  bash_calls   list of (event timestamp, input.command) for Bash tool_use blocks;
  tool_errors  count of tool_result blocks with is_error true;
  denials      list of {hook_name, stderr} from system hook_response events with exit_code 2;
  rate_limits  count of rate_limit_event events;
  result       {total_cost_usd, duration_ms, num_turns} from the last result event, else None.
Lines that are not JSON objects are skipped. A missing or unreadable path returns every field
None and raises nothing.
"""
import json

FIELDS = ('tool_calls', 'bash_calls', 'tool_errors', 'denials', 'rate_limits', 'result')


def _blocks(ev):
    msg = ev.get('message')
    content = msg.get('content') if isinstance(msg, dict) else None
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def read(log_path):
    try:
        with open(log_path, encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
    except (OSError, TypeError):
        return dict.fromkeys(FIELDS)
    rec = {'tool_calls': 0, 'bash_calls': [], 'tool_errors': 0, 'denials': [],
           'rate_limits': 0, 'result': None}
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        kind = ev.get('type')
        if kind == 'assistant':
            for b in _blocks(ev):
                if b.get('type') != 'tool_use':
                    continue
                rec['tool_calls'] += 1
                if b.get('name') == 'Bash':
                    inp = b.get('input')
                    rec['bash_calls'].append(
                        (ev.get('timestamp'), inp.get('command') if isinstance(inp, dict) else None))
        elif kind == 'user':
            rec['tool_errors'] += sum(1 for b in _blocks(ev)
                                      if b.get('type') == 'tool_result' and b.get('is_error') is True)
        elif kind == 'system':
            if ev.get('subtype') == 'hook_response' and ev.get('exit_code') == 2:
                rec['denials'].append({'hook_name': ev.get('hook_name'), 'stderr': ev.get('stderr')})
        elif kind == 'rate_limit_event':
            rec['rate_limits'] += 1
        elif kind == 'result':
            rec['result'] = {k: ev.get(k) for k in ('total_cost_usd', 'duration_ms', 'num_turns')}
    return rec
