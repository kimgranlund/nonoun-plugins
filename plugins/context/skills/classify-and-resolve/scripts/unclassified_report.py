#!/usr/bin/env python3
"""Group unclassified items from classify-and-resolve logs into candidate concepts for a KOS change proposal.

Usage: unclassified_report.py LOG [LOG ...] --pipeline FILE [--vocabulary FILE] [--min-items N] [--out FILE]

An item counts when its final label is unclassified and no Resolution corrected it. Items are
grouped first by rationale tags (#tag tokens in the classifier's rationale), then the rest by a
shared keyword from the payload and rationale; a group needs at least N items (default 3).
Grouping is greedy and deterministic: the largest group first, ties by name. No model, no
clustering. Corrections (misroutes) are listed as split, merge and rule evidence.
Writes Markdown to --out or stdout. Exit 0 on success, 1 when a log record is malformed or the
pipeline file is unusable, 2 when an input cannot be read.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from validate_pipeline import (UNCLASSIFIED, InputError, item_outcomes, load_pipelines, load_vocabulary,
                               normalize, read_log)

TAG = re.compile(r'#([a-z0-9][a-z0-9-]*)', re.I)
WORD = re.compile(r'[a-z0-9][a-z0-9-]*[a-z0-9]', re.I)
MIN_WORD = 4
STOPWORDS = set('''
about above after again against also because been before being below between both cannot could does doing
down during each from further have having here into itself just more most must need needs once only other
ought over same should since some such than that their theirs them then there these they this those through
under until very want wants were what when where which while with would your yours please thanks thank
hello issue ticket item fits class classified unclassified rationale request asks looks like nothing
'''.split())


def strings(value):
    """Every string inside a payload, in logged order."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key in value:
            yield from strings(value[key])
    elif isinstance(value, list):
        for entry in value:
            yield from strings(entry)


def features(entry):
    rationale = entry['final'].get('rationale') or ''
    tags = sorted({t.lower() for t in TAG.findall(rationale)})
    text = ' '.join(list(strings(entry['item']['payload'] if entry['item'] else None)) + [TAG.sub(' ', rationale)])
    words = sorted({w.lower() for w in WORD.findall(text) if len(w) >= MIN_WORD and w.lower() not in STOPWORDS})
    return tags, words


def greedy_groups(items, key, min_items, kind):
    """Assign items to the largest shared key first; returns (groups, items left over)."""
    left, groups = dict(items), []
    while True:
        counts = Counter(k for f in left.values() for k in f[key])
        best = sorted((k for k, n in counts.items() if n >= min_items), key=lambda k: (-counts[k], k))
        if not best:
            return groups, left
        members = sorted(i for i, f in left.items() if best[0] in f[key])
        groups.append({'name': best[0], 'kind': kind, 'items': members})
        for item_id in members:
            del left[item_id]


def example(entry):
    first = next(strings(entry['item']['payload']), '') if entry['item'] else ''
    return ' '.join(first.split())[:80]


def quote(text):
    return json.dumps(text, ensure_ascii=False)


def render(pipeline, logs, outcomes, min_items, vocab):
    pid, scheme = pipeline['id'], pipeline.get('scheme')
    candidates, corrections = {}, []
    for item_id in sorted(outcomes):
        entry = outcomes[item_id]
        if entry['final'] is None:
            continue
        if entry['corrected'] is not None:
            corrections.append((entry['final']['label'], entry['corrected']['corrected_label'], item_id,
                                entry['corrected']['log_id']))
        elif entry['final']['label'] == UNCLASSIFIED:
            tags, words = features(entry)
            candidates[item_id] = {'tags': tags, 'words': words}
    tag_groups, left = greedy_groups(candidates, 'tags', min_items, 'rationale tag')
    word_groups, left = greedy_groups(left, 'words', min_items, 'shared keyword')
    groups = tag_groups + word_groups
    known = {}
    if vocab is not None:
        for cid, concept in vocab['concepts'].items():
            for label in [cid, concept.get('prefLabel', '')] + list(concept.get('altLabel') or []):
                known[normalize(str(label).replace('-', ' '))] = cid

    total = sum(1 for e in outcomes.values() if e['final'] is not None)
    lines = [f'# Unclassified report: {pid} v{pipeline.get("version")}', '',
             f'Scheme `{scheme}`. Logs: {", ".join(logs)}. {total} classified item(s); '
             f'{len(candidates)} still unclassified; {len(corrections)} corrected. '
             f'A candidate needs at least {min_items} items.', '', '## Candidate concepts', '']
    if not groups:
        lines += ['None: no rationale tag or keyword is shared by enough unclassified items.', '']
    for n, group in enumerate(groups, 1):
        members = group['items']
        cid = group['name'].lower()
        label = cid.replace('-', ' ')
        evidence = [f'{i} ({outcomes[i]["final"]["log_id"]})' for i in members]
        words = Counter(w for i in members for w in candidates[i]['words'])
        top = sorted(words, key=lambda w: (-words[w], w))[:5]
        lines += [f'### {n}. `{cid}` ({len(members)} items, {group["kind"]} `{group["name"]}`)', '',
                  f'- Evidence: {", ".join(evidence)}',
                  f'- Shared keywords: {", ".join(f"{w} ({words[w]})" for w in top)}',
                  f'- Examples: {"; ".join(quote(example(outcomes[i])) for i in members[:3])}']
        if normalize(label) in known:
            lines += [f'- Matches the existing concept `{known[normalize(label)]}`: a definition or rule gap, '
                      'not a new class. Fix the definition or the rule before adding anything.', '']
            continue
        lines += ['', 'Proposed `knowledge-organization-system` change (write the definition before adding it):', '',
                  '```yaml', f'  - id: {cid}', f'    prefLabel: {label}',
                  '    definition: Replace with what these items have in common, in words other than the label.',
                  f'    scheme: {scheme}',
                  f'    evidence: [{", ".join(outcomes[i]["final"]["log_id"] for i in members)}]',
                  '```', '']
    lines += ['## Corrections', '']
    if corrections:
        pairs = {}
        for source, target, item_id, log_id in corrections:
            pairs.setdefault((source, target), []).append(f'{item_id} ({log_id})')
        lines += ['| From | To | Items |', '|---|---|---|']
        lines += [f'| {s} | {t} | {", ".join(ids)} |' for (s, t), ids in sorted(pairs.items())]
        lines += ['', 'A pair that repeats is evidence for a rule or definition fix, a split or a merge '
                      '(references/growth.md, taxonomy feedback loop).', '']
    else:
        lines += ['None recorded.', '']
    lines += ['## Ungrouped', '']
    if left:
        for item_id in sorted(left):
            tags = ' '.join(f'#{t}' for t in left[item_id]['tags']) or 'no tags'
            lines.append(f'- {item_id} ({outcomes[item_id]["final"]["log_id"]}): {tags}; '
                         f'{quote(example(outcomes[item_id]))}')
    else:
        lines.append('None.')
    return '\n'.join(lines) + '\n', len(groups)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('logs', nargs='+', metavar='LOG', help='JSONL log file(s)')
    parser.add_argument('--pipeline', required=True, help='the pipeline YAML that wrote the logs')
    parser.add_argument('--vocabulary', help='KOS vocabulary, to flag candidates that match an existing concept')
    parser.add_argument('--min-items', type=int, default=3, help='items a candidate needs (default 3)')
    parser.add_argument('--out', help='write the Markdown here instead of stdout')
    args = parser.parse_args(argv)
    if args.min_items < 1:
        parser.error('--min-items must be at least 1')
    try:
        docs = load_pipelines(args.pipeline)
        vocab = load_vocabulary(args.vocabulary) if args.vocabulary else None
        records, problems = read_log(args.logs)
    except (InputError, OSError, yaml.YAMLError) as exc:
        print(exc, file=sys.stderr)
        return 2
    if len(docs) != 1 or not isinstance(docs[0], dict) or not isinstance(docs[0].get('id'), str):
        print(f'{args.pipeline}: expected one pipeline document with an id; run validate_pipeline.py.', file=sys.stderr)
        return 1
    if problems:
        for where, message in problems:
            print(f'ERROR schema log:{where} record: {message}.', file=sys.stderr)
        return 1
    outcomes = item_outcomes([r for r in records if r['pipeline_id'] == docs[0]['id']])
    text, count = render(docs[0], args.logs, outcomes, args.min_items, vocab)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    print(f'{count} candidate concept(s)', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
