"""Result reader: the <role>-L<n>(-<k>).md result files of one handoff dir.

read(dir) returns (records, problems):
  records   one dict per result file in dir, sorted by file name, with name (no .md), path, role,
            level, model and effort (from a first-line <!-- role=... model=... effort=... -->
            header, else None), status (builder), verdict (verifier), plan_defect, swap,
            next_note, and changes (the code-span texts under the Changes section);
  problems  the paths of result files that could not be read, which are skipped.
Every section is read through steps.section and every classification through steps.py's own
helpers, so this reader classifies exactly as `steps.py next` does.
"""
import os, re

import order  # same scripts/ dir: RESULT is the one <role>-L<n>(-<k>).md name rule
import steps

from .. import table

HEADER_RE = re.compile(r'^\s*<!--(.*?)-->')
KV_RE = re.compile(r'(\w+)=(\S+)')


def _header(path):
    with open(path, encoding='utf-8') as f:
        first = f.readline()
    m = HEADER_RE.match(first)
    if not m:
        return None, None
    kv = dict(KV_RE.findall(m.group(1)))
    return kv.get('model'), kv.get('effort')


def _first_line(path, heading):
    body = steps.section(path, heading) or []
    return next((line.strip() for line in body if line.strip()), None)


def _changes(path):
    out = []
    for line in steps.section(path, 'Changes') or []:
        for m in steps.SPAN_RE.finditer(line):
            out.append(m.group(2).strip())
    return out


def read(dir):
    records, problems = [], []
    try:
        names = sorted(os.listdir(dir))
    except OSError:
        return records, problems
    for fname in names:
        if not order.RESULT.match(fname):
            continue
        path = os.path.join(dir, fname)
        role, level, _ = table.name_parts(fname)
        try:
            model, effort = _header(path)
            rec = {
                'name': fname[:-len('.md')], 'path': path, 'role': role, 'level': level,
                'model': model, 'effort': effort,
                'status': steps.build_status_or_none(path) if role == 'builder' else None,
                'verdict': steps.verdict_or_none(path) if role == 'verifier' else None,
                'plan_defect': steps.is_plan_defect(path),
                'swap': steps.swap_pair(path) is not None,
                'next_note': _first_line(path, 'For the next attempt' if role == 'verifier'
                                         else 'Notes'),
                'changes': _changes(path),
            }
        except (OSError, UnicodeDecodeError):
            problems.append(path)
            continue
        records.append(rec)
    return records, problems
