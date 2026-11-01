#!/usr/bin/env python3
"""Convert classify-and-resolve JSONL logs into an evaluation-system suite of production cases.

Usage: logs_to_cases.py LOG [LOG ...] --pipeline FILE [--suite-id ID] [--suite-version V]
                        [--holdout-percent N] [--out FILE]

An item becomes a case only when a human settled its class: a corrected_label on a Resolution
(the misroute signal) wins; otherwise the final label from a human cascade step (matched by
classifier_id), or a label a human resolver accepted. Items still unclassified are left to unclassified_report.py.
Each case: input = the logged Item payload, expected = the concept id, source = production,
added_because = the deciding log id, split = holdout when sha256(item id) mod 100 < N.
Writes YAML to --out or stdout; prints a one-line count to stderr. Exit 0 on success, 1 when a
log record is malformed or a pipeline file has errors, 2 when an input cannot be read.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import hashlib
import sys
from pathlib import Path

import yaml

from validate_pipeline import UNCLASSIFIED, InputError, item_outcomes, load_pipelines, read_log


def split_for(item_id, holdout_percent):
    bucket = int(hashlib.sha256(item_id.encode('utf-8')).hexdigest(), 16) % 100
    return 'holdout' if bucket < holdout_percent else 'dev'


def settled_label(entry, human_classifiers):
    """Return (label, deciding record) for one item, or (None, None) when no human settled it."""
    if entry['corrected'] is not None:
        return entry['corrected']['corrected_label'], entry['corrected']
    final = entry['final']
    if final is None:
        return None, None
    if final['classifier_id'] in human_classifiers:
        return final['label'], final
    accepted = [r for r in entry['resolutions'] if r['decided_by'] == 'human' and r['status'] != 'rejected']
    if accepted:
        return final['label'], accepted[-1]
    return None, None


def build_suite(pipeline, records, suite_id, suite_version, holdout_percent):
    pid = pipeline['id']
    # by classifier id, not step index: indices shift when a stage adds a step in front
    human_classifiers = {step.get('classifier_id') for step in pipeline.get('cascade') or []
                         if isinstance(step, dict) and step.get('kind') == 'human'}
    outcomes = item_outcomes([r for r in records if r['pipeline_id'] == pid])
    cases, skipped = [], {'unclassified': 0, 'no human decision': 0, 'no logged item': 0}
    for item_id in sorted(outcomes):
        entry = outcomes[item_id]
        label, decided = settled_label(entry, human_classifiers)
        if label is None:
            skipped['no human decision'] += 1
            continue
        if label == UNCLASSIFIED:
            skipped['unclassified'] += 1
            continue
        if entry['item'] is None:
            skipped['no logged item'] += 1
            continue
        cases.append({
            'id': f'case-{item_id}',
            'input': entry['item']['payload'],
            'expected': label,
            'tags': [label],
            'source': 'production',
            'added_because': decided['log_id'],
            'split': split_for(item_id, holdout_percent),
            'added_at': decided['at'][:10],
        })
    labels = sorted({c['expected'] for c in cases})
    suite = {
        'id': suite_id or f'{pid}-classification',
        'version': suite_version,
        'target': f'{pid} classification cascade',
        'target_spec': [f'The {pid} pipeline shall assign each item the class a human settled for it.'],
        'graders': [{'id': 'label-match', 'kind': 'exact', 'config': {'field': 'label'}}],
        'slices': labels,
        'cases': cases,
    }
    return suite, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('logs', nargs='+', metavar='LOG', help='JSONL log file(s)')
    parser.add_argument('--pipeline', required=True, help='the pipeline YAML that wrote the logs')
    parser.add_argument('--suite-id', help='suite id (default <pipeline id>-classification)')
    parser.add_argument('--suite-version', default=1, help='suite version (default 1); bump it when cases change')
    parser.add_argument('--holdout-percent', type=int, default=20, help='share of items in holdout (default 20)')
    parser.add_argument('--out', help='write the suite here instead of stdout')
    args = parser.parse_args(argv)
    if not 0 <= args.holdout_percent <= 100:
        parser.error('--holdout-percent must be between 0 and 100')
    version = int(args.suite_version) if str(args.suite_version).isdigit() else args.suite_version
    try:
        docs = load_pipelines(args.pipeline)
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
    suite, skipped = build_suite(docs[0], records, args.suite_id, version, args.holdout_percent)
    text = (f'# Generated by logs_to_cases.py from {", ".join(args.logs)}; edit cases only to retire them.\n'
            + yaml.safe_dump(suite, sort_keys=False, allow_unicode=True, width=120))
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    left_out = ', '.join(f'{n} {why}' for why, n in skipped.items() if n) or 'none'
    holdout = sum(c['split'] == 'holdout' for c in suite['cases'])
    print(f'{len(suite["cases"])} case(s), {holdout} in holdout; left out: {left_out}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
