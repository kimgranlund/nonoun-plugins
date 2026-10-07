"""Run-row reader: the runs.jsonl of one handoff dir.

read(dir) returns (records, skipped):
  records  one dict per good JSON object line of <dir>/runs.jsonl, in file order, read through
           order.records(dir): the kept FIELDS (lists default to [], the rest to None) plus
           "index" (the line index) and "path" (dir joined with runs.jsonl);
  skipped  the count of lines that are not JSON objects (order.records drops them silently).
A missing runs.jsonl gives ([], 0).
"""
import os

import order  # same scripts/ dir: the one runs.jsonl line reader

FIELDS = ('ts', 'role', 'level', 'model', 'effort', 'file', 'attempt_id', 'backend', 'cost_usd', 'cost_estimated',
          'duration_ms', 'turns', 'stray_worktrees', 'stray_branches', 'routing_reason',
          'loaded_context')
LISTS = ('stray_worktrees', 'stray_branches')


def read(dir):
    path = os.path.join(dir, 'runs.jsonl')
    try:
        with open(path, encoding='utf-8') as f:
            total = len(f.read().splitlines())
    except OSError:
        return [], 0
    records = []
    for i, rec in order.records(dir):
        out = {k: rec.get(k) for k in FIELDS}
        for k in LISTS:
            if out[k] is None:
                out[k] = []
        out['index'] = i
        out['path'] = path
        records.append(out)
    return records, total - len(records)
