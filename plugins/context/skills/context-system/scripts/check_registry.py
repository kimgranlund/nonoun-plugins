#!/usr/bin/env python3
"""Check a generated registry against the manifests it indexes (JSON on both sides).

Usage: check_registry.py --registry REGISTRY --manifests GLOB [--manifests GLOB ...]
                         [--entries KEY] [--id-field id] [--keep FIELD,FIELD] [--path-field path]
                         [--id-pattern REGEX] [--root DIR] [--strict]

A manifest is the source of one item; the registry is an index generated from the manifests. The checks hold
the rules in references/manifests.md: one entry per manifest and no entry without one (closure both ways), no
duplicate or malformed ids, no lost routing fields (each --keep field a manifest sets reaches its entry with the
same value), entry paths that resolve, and a registry that says it is generated.

Each finding is one line: SEVERITY RULE ID FIELD: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors, 2 when an input cannot be read.
Standard library only; runs on Python 3.9.
"""
import argparse
import glob
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

ERROR_RULES = ('read', 'no-entries', 'duplicate-id', 'bad-id', 'missing-entry', 'orphan-entry', 'lost-field')
WARNING_RULES = ('stale-path', 'not-generated')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}
GENERATED_KEYS = ('generated', '$generated', 'generator', '$comment', '$description')


class Finding(namedtuple('Finding', 'severity rule item field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.item} {self.field}: {self.problem} Fix: {self.fix}'


def err(rule, item, field, problem, fix):
    return Finding('ERROR', rule, item, field, problem, fix)


def warn(rule, item, field, problem, fix):
    return Finding('WARNING', rule, item, field, problem, fix)


def find_entries(registry, key, id_field):
    """The registry's entries as {id: entry}: at KEY (dotted) when given, else the first list of objects with ids,
    or an object whose values are objects keyed by id."""
    node = registry
    if key:
        for part in key.split('.'):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        candidates = [node]
    else:
        candidates = [v for v in registry.values()] if isinstance(registry, dict) else [registry]
    for node in candidates:
        if isinstance(node, list) and node and all(isinstance(e, dict) and id_field in e for e in node):
            out = {}
            for e in node:
                out.setdefault(str(e[id_field]), []).append(e)
            return out
        if isinstance(node, dict) and node and all(isinstance(v, dict) for v in node.values()):
            return {str(v.get(id_field, k)): [v] for k, v in node.items()}
    return None


def check(manifests, registry, registry_path, args):
    """manifests: list of (path, data). Returns sorted findings."""
    f = []
    id_re = re.compile(args.id_pattern)
    keep = [k for k in (args.keep or '').split(',') if k]
    by_id = {}
    for path, data in manifests:
        mid = data.get(args.id_field) if isinstance(data, dict) else None
        if mid is None:
            f.append(err('bad-id', path, args.id_field, 'the manifest has no id.', f'give it a stable `{args.id_field}`.'))
            continue
        mid = str(mid)
        if not id_re.fullmatch(mid):
            f.append(err('bad-id', mid, args.id_field, f'id does not match {args.id_pattern}.', 'use a stable lowercase-hyphenated id; ids never change once published.'))
        if mid in by_id:
            f.append(err('duplicate-id', mid, args.id_field, f'declared by {by_id[mid][0]} and {path}.', 'give each item one manifest and one id.'))
            continue
        by_id[mid] = (path, data)
    entries = find_entries(registry, args.entries, args.id_field)
    if entries is None:
        f.append(err('no-entries', registry_path, args.entries or '-', 'no list of entries with ids was found.', 'pass --entries with the key that holds the entries.'))
        return sorted(f, key=order)
    if not any(k in registry for k in GENERATED_KEYS) if isinstance(registry, dict) else True:
        f.append(warn('not-generated', registry_path, '-', 'the registry does not say what generates it.', 'add a `generated` key naming the tool, and never hand-edit the file.'))
    for eid, es in entries.items():
        if len(es) > 1:
            f.append(err('duplicate-id', eid, args.id_field, f'{len(es)} registry entries share this id.', 'regenerate the registry from the manifests.'))
        if eid not in by_id:
            f.append(err('orphan-entry', eid, args.id_field, 'the registry lists an item no manifest declares.', 'remove it by regenerating, or restore its manifest.'))
            continue
        e, m = es[0], by_id[eid][1]
        for k in keep:
            if k in m and (k not in e or e[k] != m[k]):
                got = 'missing' if k not in e else json.dumps(e[k])
                f.append(err('lost-field', eid, k, f'the manifest says {json.dumps(m[k])}, the registry entry has {got}.', f'carry `{k}` into the registry projection; consumers route by it.'))
        p = e.get(args.path_field)
        if isinstance(p, str) and p and '://' not in p:
            base = Path(args.root) if args.root else Path(registry_path).parent
            if not (base / p).exists():
                f.append(warn('stale-path', eid, args.path_field, f'{p} does not exist under {base}.', 'regenerate the registry, or fix the path the generator writes.'))
    for mid in by_id:
        if mid not in entries:
            f.append(err('missing-entry', mid, args.id_field, f'{by_id[mid][0]} has no registry entry.', 'regenerate the registry; a manifest the index omits cannot be routed to.'))
    return sorted(f, key=order)


def order(x):
    return (0 if x.severity == 'ERROR' else 1, RULE_ORDER.get(x.rule, 99), str(x.item), x.field)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--registry', required=True)
    ap.add_argument('--manifests', action='append', required=True, help='glob of manifest files; repeatable')
    ap.add_argument('--entries', help='dotted key of the entries in the registry (default: the first list of objects with ids)')
    ap.add_argument('--id-field', default='id')
    ap.add_argument('--keep', help='comma-separated routing fields the registry must carry unchanged')
    ap.add_argument('--path-field', default='path')
    ap.add_argument('--id-pattern', default=r'[a-z][a-z0-9-]*')
    ap.add_argument('--root', help='directory entry paths are relative to (default: the registry file\'s folder)')
    ap.add_argument('--strict', action='store_true', help='warnings fail too')
    args = ap.parse_args(argv)
    try:
        registry = json.loads(Path(args.registry).read_text())
    except (OSError, ValueError) as exc:
        print(f'{args.registry}: cannot read: {exc}', file=sys.stderr)
        return 2
    paths = sorted({p for g in args.manifests for p in glob.glob(g, recursive=True)})
    if not paths:
        print(f"no manifest matches {', '.join(args.manifests)}", file=sys.stderr)
        return 2
    manifests = []
    for p in paths:
        try:
            manifests.append((p, json.loads(Path(p).read_text())))
        except (OSError, ValueError) as exc:
            print(f'{p}: cannot read: {exc}', file=sys.stderr)
            return 2
    findings = check(manifests, registry, args.registry, args)
    for x in findings:
        print(x.line())
    errors = sum(x.severity == 'ERROR' for x in findings)
    warnings = len(findings) - errors
    print(f'{args.registry}: {len(manifests)} manifest(s), {errors} error(s), {warnings} warning(s)')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
