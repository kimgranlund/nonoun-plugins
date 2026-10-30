"""Findings: the detector output record, its stable id, the merged findings.jsonl, and clusters.

make(detector, family, severity, layer, cause_file, cause_rule, evidence, summary)
    returns one finding dict:
      id          first 12 hex of sha256 over the detector name plus the evidence entries, each
                  as its sorted (key, value) pairs, the entries themselves sorted, so the id
                  does not depend on dict or list order and does not change with the summary
      detector, family, summary
      severity    3 high, 2 medium, 1 low (the int or its name is accepted)
      layer       one of LAYERS
      cause_hint  {"file": a plugin-relative path or None, "rule": cause_rule}
      evidence    a list of {path, line} or {attempt_id} entries; extra keys are allowed
    A bad severity, layer, cause file, or evidence entry raises ValueError.
write(out, findings, now)
    merges into <out>/findings.jsonl (one JSON line per finding, sorted by id): an id already
    present keeps its first_seen and gets last_seen = now; a new id gets both = now; both get
    stale False; an id absent from this run is kept as it was with stale True. Returns the
    merged list.
clusters(out, max_n)
    groups the non-stale findings in <out>/findings.jsonl by cause_hint.file, ranks the groups
    by highest severity then finding count (then file, None last, for a stable order), keeps the
    first max_n, writes them to <out>/clusters.json, and returns them. A cluster is
    {"file", "severity" (the highest), "count", "ids"}.
"""
import hashlib, json, os

from . import store

FINDINGS, CLUSTERS = 'findings.jsonl', 'clusters.json'
SEVERITY = {'high': 3, 'medium': 2, 'low': 1}
LAYERS = ('sdlc', 'project', 'host', 'task-text', 'unknown')


def _severity(value):
    if isinstance(value, str) and value in SEVERITY:
        return SEVERITY[value]
    if isinstance(value, int) and not isinstance(value, bool) and value in SEVERITY.values():
        return value
    raise ValueError(f'severity must be 1..3 or one of {sorted(SEVERITY)}: {value!r}')


def _evidence(entries):
    if not isinstance(entries, (list, tuple)) or not entries:
        raise ValueError('evidence must be a non-empty list')
    out = []
    for e in entries:
        if not isinstance(e, dict):
            raise ValueError(f'evidence entry is not a dict: {e!r}')
        by_path = isinstance(e.get('path'), str) and e['path'] and 'line' in e
        by_attempt = isinstance(e.get('attempt_id'), str) and e['attempt_id']
        if not (by_path or by_attempt):
            raise ValueError(f'evidence entry needs {{path, line}} or {{attempt_id}}: {e!r}')
        out.append(dict(e))
    return out


def finding_id(detector, evidence):
    entries = sorted(json.dumps(sorted(e.items()), ensure_ascii=False, default=str)
                     for e in evidence)
    blob = json.dumps([detector, entries], ensure_ascii=False)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:12]


def make(detector, family, severity, layer, cause_file, cause_rule, evidence, summary):
    if not isinstance(detector, str) or not detector:
        raise ValueError('detector must be a non-empty string')
    if layer not in LAYERS:
        raise ValueError(f'layer must be one of {LAYERS}: {layer!r}')
    if cause_file is not None and (not isinstance(cause_file, str) or not cause_file
                                   or os.path.isabs(cause_file)):
        raise ValueError(f'cause_file must be a plugin-relative path or None: {cause_file!r}')
    ev = _evidence(evidence)
    return {'id': finding_id(detector, ev), 'detector': detector, 'family': family,
            'severity': _severity(severity), 'layer': layer,
            'cause_hint': {'file': cause_file, 'rule': cause_rule}, 'evidence': ev,
            'summary': summary}


def load(out):
    """The findings in <out>/findings.jsonl, in file order; a missing file or bad line is skipped."""
    rows = []
    try:
        with open(os.path.join(out, FINDINGS), encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError:
        return rows
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict) and isinstance(d.get('id'), str):
            rows.append(d)
    return rows


def write(out, findings, now):
    now = now.isoformat() if hasattr(now, 'isoformat') else str(now)
    old = {d['id']: d for d in load(out)}
    merged = {}
    for f in findings:
        d = dict(f)
        prev = old.get(d['id']) or merged.get(d['id'])
        d['first_seen'] = prev.get('first_seen', now) if prev else now
        d['last_seen'] = now
        d['stale'] = False
        merged[d['id']] = d
    for fid, d in old.items():
        if fid not in merged:
            merged[fid] = dict(d, stale=True)
    rows = [merged[k] for k in sorted(merged)]
    store._atomic_write(os.path.join(out, FINDINGS),
                        ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    return rows


def clusters(out, max_n):
    groups = {}
    for d in load(out):
        if d.get('stale'):
            continue
        hint = d.get('cause_hint') if isinstance(d.get('cause_hint'), dict) else {}
        groups.setdefault(hint.get('file'), []).append(d)
    result = []
    for file, rows in groups.items():
        result.append({'file': file, 'severity': max(int(r.get('severity') or 0) for r in rows),
                       'count': len(rows), 'ids': sorted(r['id'] for r in rows)})
    result.sort(key=lambda c: (-c['severity'], -c['count'], c['file'] is None, c['file'] or ''))
    result = result[:max(0, int(max_n))]
    store._atomic_write(os.path.join(out, CLUSTERS),
                        json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    return result
