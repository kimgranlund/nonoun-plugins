"""Attempt reader: the <name>.attempt.json files of one handoff dir.

read(dir) returns (records, problems):
  records   one dict per *.attempt.json in dir, sorted by file name: the parsed object plus
            "path" (dir joined with the file name) and "marker" (True when a
            <role>-<level>.running file sits next to it);
  problems  the paths of files that did not parse as a JSON object, which are skipped.
"""
import json, os

from .. import table


def _marker(dir, rec, fname):
    role, level = rec.get('role'), rec.get('level')
    if not (isinstance(role, str) and role and isinstance(level, str) and level):
        n_role, n_level, _ = table.name_parts(rec.get('name') or fname[:-len('.attempt.json')])
        role, level = role if isinstance(role, str) and role else n_role, \
            level if isinstance(level, str) and level else n_level
    if not role or not level:
        return False
    return os.path.exists(os.path.join(dir, f'{role}-{level}.running'))


def read(dir):
    records, problems = [], []
    try:
        names = sorted(os.listdir(dir))
    except OSError:
        return records, problems
    for fname in names:
        if not fname.endswith('.attempt.json'):
            continue
        path = os.path.join(dir, fname)
        try:
            with open(path, encoding='utf-8') as f:
                rec = json.load(f)
        except (OSError, ValueError):
            rec = None
        if not isinstance(rec, dict):
            problems.append(path)
            continue
        rec['path'] = path
        rec['marker'] = _marker(dir, rec, fname)
        records.append(rec)
    return records, problems
