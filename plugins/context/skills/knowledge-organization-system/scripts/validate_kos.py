#!/usr/bin/env python3
"""Validate a KOS vocabulary file (a lightweight SKOS subset) and, optionally, the corpus it governs.

Usage: validate_kos.py VOCABULARY [--corpus PATH ...] [--strict]

Each finding is one line: SEVERITY RULE CONCEPT FIELD: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors,
2 when the vocabulary file cannot be read. Rule semantics: references/model.md.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

import yaml

TOP_FIELDS = ('title', 'schemes', 'concepts')
SCHEME_FIELDS = ('id', 'definition', 'scopeNote')
CONCEPT_FIELDS = ('id', 'prefLabel', 'altLabel', 'hiddenLabel', 'definition', 'scopeNote',
                  'broader', 'narrower', 'related', 'scheme', 'evidence', 'deprecated', 'replacedBy')
LIST_FIELDS = ('altLabel', 'hiddenLabel', 'broader', 'narrower', 'related', 'evidence')
TEXT_FIELDS = ('prefLabel', 'definition', 'scopeNote', 'scheme', 'replacedBy')
LINK_FIELDS = ('broader', 'narrower', 'related', 'replacedBy')

ERROR_RULES = ('schema', 'duplicate-preflabel', 'label-collision', 'missing-definition',
               'circular-definition', 'dangling-link', 'broader-cycle', 'unknown-scheme')
WARNING_RULES = ('stage-gate', 'unreferenced', 'retired-label-used')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}

STAGE2_MIN_CHILDREN = 3
SKIP_DIRS = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
MAX_FILE_BYTES = 2000000


class Finding(namedtuple('Finding', 'severity rule concept field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.concept} {self.field}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', RULE_ORDER[self.rule], self.concept, self.field, self.problem)


def normalize(label):
    """Compare labels case-insensitively with collapsed whitespace."""
    return ' '.join(str(label).casefold().split())


def restates_label(definition, label):
    text = normalize(definition).rstrip('.').strip()
    text = re.sub(r'^(a|an|the) ', '', text)
    return text == re.sub(r'^(a|an|the) ', '', normalize(label))


def load(path):
    """Parse a vocabulary file. Raises OSError (unreadable) or yaml.YAMLError (not YAML)."""
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def _schema(findings, concept, field, problem, fix):
    findings.append(Finding('ERROR', 'schema', concept, field, problem, fix))


def _read_schemes(data, findings):
    schemes = data.get('schemes')
    if not isinstance(schemes, list) or not schemes:
        _schema(findings, '-', 'schemes', 'no scheme list is declared.',
                'add `schemes:` with at least one `{id, definition}` entry.')
        return set()
    ids = set()
    for i, scheme in enumerate(schemes):
        sid = scheme.get('id') if isinstance(scheme, dict) else None
        if not isinstance(sid, str) or not sid.strip():
            _schema(findings, f'schemes[{i}]', 'id', 'scheme has no id.', 'give every scheme a non-empty `id`.')
            continue
        if sid in ids:
            _schema(findings, sid, 'id', f"scheme id '{sid}' is declared twice.", 'keep one declaration.')
        ids.add(sid)
        for field in sorted(set(scheme) - set(SCHEME_FIELDS)):
            _schema(findings, sid, field, f"unknown scheme field '{field}'.",
                    f"use only {', '.join(SCHEME_FIELDS)}.")
    return ids


def _read_concepts(data, findings):
    """Return {id: concept dict with every field present and list fields as lists of strings}."""
    raw = data.get('concepts')
    if not isinstance(raw, list):
        _schema(findings, '-', 'concepts', 'no concept list is declared.', 'add `concepts:` as a list (it may be empty).')
        return {}
    concepts = {}
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            _schema(findings, f'concepts[{i}]', '-', 'entry is not a mapping.', 'write each concept as a mapping of fields.')
            continue
        cid = item.get('id')
        if not isinstance(cid, str) or not cid.strip():
            _schema(findings, f'concepts[{i}]', 'id', 'concept has no id.', 'give it a stable, non-empty `id`.')
            continue
        if cid in concepts:
            _schema(findings, cid, 'id', f"id '{cid}' is used by two concepts.",
                    'give each concept its own id, or merge the two entries.')
            continue
        concept = {'id': cid}
        for field in sorted(set(item) - set(CONCEPT_FIELDS)):
            hint = ' (synonyms go in altLabel)' if field.casefold() in ('synonyms', 'aliases', 'alias') else ''
            _schema(findings, cid, field, f"unknown field '{field}'{hint}.",
                    'use only the fields listed in references/model.md.')
        for field in LIST_FIELDS:
            value = item.get(field)
            if value is None:
                value = []
            if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
                _schema(findings, cid, field, 'must be a list of non-empty strings.', f'write `{field}: [value, ...]`.')
                value = []
            concept[field] = value
        for field in TEXT_FIELDS:
            value = item.get(field)
            if value is not None and not isinstance(value, str):
                _schema(findings, cid, field, 'must be a string.', f'write `{field}` as text.')
                value = None
            concept[field] = value
        if not concept['prefLabel'] or not concept['prefLabel'].strip():
            _schema(findings, cid, 'prefLabel', 'concept has no prefLabel.', 'give it exactly one preferred label.')
            concept['prefLabel'] = None
        deprecated = item.get('deprecated', False)
        if not isinstance(deprecated, bool):
            _schema(findings, cid, 'deprecated', 'must be true or false.', 'write `deprecated: true` or remove it.')
            deprecated = False
        if deprecated and not concept['replacedBy']:
            _schema(findings, cid, 'replacedBy', 'deprecated concept has no replacement pointer.',
                    'add `replacedBy: <id>` naming the concept to use instead.')
        concept['deprecated'] = deprecated
        concepts[cid] = concept
    return concepts


def _check_definitions(concepts, schemes, findings):
    for cid, c in sorted(concepts.items()):
        definition = c['definition']
        if definition is None or not definition.strip():
            findings.append(Finding('ERROR', 'missing-definition', cid, 'definition',
                                    'definition is missing or empty.',
                                    'write one sentence saying what the concept means in this corpus.'))
        elif c['prefLabel'] and restates_label(definition, c['prefLabel']):
            findings.append(Finding('ERROR', 'circular-definition', cid, 'definition',
                                    f"definition only restates the prefLabel '{c['prefLabel']}'.",
                                    'define it in other words: what it is, and what distinguishes it.'))
        if c['scheme'] not in schemes:
            shown = c['scheme'] if c['scheme'] else '(none)'
            findings.append(Finding('ERROR', 'unknown-scheme', cid, 'scheme',
                                    f"scheme '{shown}' is not declared under schemes.",
                                    f"use one of: {', '.join(sorted(schemes)) or '(declare a scheme first)'}."))


def _check_labels(concepts, findings):
    """prefLabel unique per scheme; no label may equal another concept's prefLabel or altLabel in the scheme."""
    active = {cid: c for cid, c in concepts.items() if not c['deprecated']}
    owners = {}
    for cid, c in sorted(active.items()):
        if c['prefLabel']:
            owners.setdefault((c['scheme'], normalize(c['prefLabel'])), []).append((cid, 'prefLabel'))
        for label in c['altLabel']:
            owners.setdefault((c['scheme'], normalize(label)), []).append((cid, 'altLabel'))
    for (scheme, _), holders in sorted(owners.items()):
        prefs = [cid for cid, kind in holders if kind == 'prefLabel']
        for cid in prefs[1:]:
            findings.append(Finding('ERROR', 'duplicate-preflabel', cid, 'prefLabel',
                                    f"prefLabel '{active[cid]['prefLabel']}' is also the prefLabel of '{prefs[0]}' in scheme '{scheme}'.",
                                    "merge the two (deprecate one with replacedBy) or give one a distinct prefLabel."))
    seen = set()
    for cid, c in sorted(active.items()):
        for kind in ('altLabel', 'hiddenLabel'):
            for label in c[kind]:
                for other, other_kind in owners.get((c['scheme'], normalize(label)), []):
                    pair = (tuple(sorted((cid, other))), normalize(label))
                    if other == cid or pair in seen:
                        continue
                    seen.add(pair)
                    findings.append(Finding('ERROR', 'label-collision', cid, kind,
                                            f"label '{label}' is also the {other_kind} of '{other}' in scheme '{c['scheme']}'.",
                                            "keep the label on one concept only; if both mean the same thing, deprecate one with replacedBy."))


def _hierarchy(concepts):
    """Child to parent edges from broader, plus narrower read as its inverse."""
    parents = {cid: set() for cid in concepts}
    for cid, c in concepts.items():
        parents[cid].update(p for p in c['broader'] if p in concepts)
        for child in c['narrower']:
            if child in concepts:
                parents[child].add(cid)
    return parents


def _cycles(parents):
    reach = {}
    for start in sorted(parents):
        seen, stack = set(), list(parents[start])
        while stack:
            node = stack.pop()
            if node not in seen:
                seen.add(node)
                stack.extend(parents[node])
        reach[start] = seen
    groups, placed = [], set()
    for node in sorted(parents):
        if node in placed or node not in reach[node]:
            continue
        group = sorted(n for n in reach[node] if node in reach[n])
        placed.update(group)
        groups.append(group)
    return groups


def _check_links(concepts, findings):
    for cid, c in sorted(concepts.items()):
        for field in LINK_FIELDS:
            targets = c[field] if field != 'replacedBy' else [c[field]] if c[field] else []
            for target in targets:
                if target not in concepts:
                    findings.append(Finding('ERROR', 'dangling-link', cid, field,
                                            f"'{target}' is not a concept id.",
                                            'correct the id, add the concept with evidence, or remove the link.'))
    parents = _hierarchy(concepts)
    cyclic = set()
    for group in _cycles(parents):
        cyclic.update(group)
        findings.append(Finding('ERROR', 'broader-cycle', group[0], 'broader',
                                f"broader links loop through {', '.join(group)}.",
                                'remove the link that makes a concept its own ancestor.'))
    return parents, cyclic


def _check_stage_gates(concepts, schemes, parents, cyclic, findings):
    children = {}
    for child, ps in parents.items():
        for p in ps:
            children.setdefault(p, set()).add(child)
    for parent, kids in sorted(children.items()):
        if parent in cyclic or len(kids) >= STAGE2_MIN_CHILDREN:
            continue
        findings.append(Finding('WARNING', 'stage-gate', parent, 'narrower',
                                f"only {len(kids)} concept(s) ({', '.join(sorted(kids))}) share this parent; Stage 2 needs at least {STAGE2_MIN_CHILDREN}.",
                                'drop these broader/narrower links until three evidenced concepts share the parent.'))
    if len(schemes) > 1:
        by_label = {}
        for c in concepts.values():
            if c['deprecated']:
                continue
            for label in ([c['prefLabel']] if c['prefLabel'] else []) + c['altLabel']:
                by_label.setdefault(normalize(label), set()).add(c['scheme'])
        if not any(len(s) > 1 for s in by_label.values()):
            findings.append(Finding('WARNING', 'stage-gate', '-', 'schemes',
                                    f'{len(schemes)} schemes are declared but no label is used in two of them; Stage 3 needs one label with two meanings.',
                                    'merge back into one scheme until two domains use one label differently.'))


def inferred_stage(concepts, schemes, parents):
    if len(schemes) > 1:
        return 3
    if any(parents.values()):
        return 2
    if any(c['altLabel'] or c['hiddenLabel'] or c['deprecated'] for c in concepts.values()):
        return 1
    return 0


def term_pattern(label):
    words = [re.escape(w) for w in str(label).split()]
    return re.compile(r'(?<!\w)' + r'\s+'.join(words) + r'(?:s|es)?(?!\w)', re.IGNORECASE)


def corpus_files(paths, exclude):
    """Yield (display path, text) for readable text files under the corpus paths, sorted."""
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(
            p for p in root.rglob('*')
            if p.is_file() and not any(part in SKIP_DIRS or part.startswith('.') for part in p.relative_to(root).parts))
        for path in files:
            if path.resolve() in exclude or path.stat().st_size > MAX_FILE_BYTES:
                continue
            try:
                yield str(path), path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue


def _check_corpus(concepts, corpus, exclude, findings):
    texts = list(corpus_files(corpus, exclude))
    for cid, c in sorted(concepts.items()):
        if c['deprecated']:
            continue
        terms = [cid] + ([c['prefLabel']] if c['prefLabel'] else []) + c['altLabel']
        patterns = [term_pattern(t) for t in terms]
        if not any(p.search(text) for _, text in texts for p in patterns):
            findings.append(Finding('WARNING', 'unreferenced', cid, 'prefLabel',
                                    f"no corpus file uses its id, prefLabel or altLabel ({', '.join(str(p) for p in corpus)}).",
                                    'deprecate it with replacedBy, drop it if it was never used, or record where it is used.'))
    reported = set()  # a label retired on two concepts is reported once per line
    for cid, c in sorted(concepts.items()):
        if c['deprecated']:
            successor = concepts.get(c['replacedBy'], {}).get('prefLabel') or c['replacedBy']
            retired = [('prefLabel', l) for l in ([c['prefLabel']] if c['prefLabel'] else [])]
            retired += [('altLabel', l) for l in c['altLabel']] + [('hiddenLabel', l) for l in c['hiddenLabel']]
        else:
            successor = c['prefLabel']
            retired = [('hiddenLabel', l) for l in c['hiddenLabel']]
        for field, label in retired:
            pattern = term_pattern(label)
            for name, text in texts:
                for n, line in enumerate(text.splitlines(), 1):
                    if pattern.search(line) and (normalize(label), name, n) not in reported:
                        reported.add((normalize(label), name, n))
                        findings.append(Finding('WARNING', 'retired-label-used', cid, field,
                                                f"retired label '{label}' appears at {name}:{n}.",
                                                f"write '{successor}' instead."))


def validate(data, corpus=(), vocabulary_path=None):
    """Return (sorted findings, inferred stage) for a parsed vocabulary."""
    findings = []
    if not isinstance(data, dict):
        _schema(findings, '-', '-', 'the file is empty or not a mapping.',
                'start from templates/vocabulary.yaml (top-level `schemes` and `concepts`).')
        return findings, 0
    for field in sorted(set(data) - set(TOP_FIELDS)):
        _schema(findings, '-', field, f"unknown top-level field '{field}'.", f"use only {', '.join(TOP_FIELDS)}.")
    schemes = _read_schemes(data, findings)
    concepts = _read_concepts(data, findings)
    _check_definitions(concepts, schemes, findings)
    _check_labels(concepts, findings)
    parents, cyclic = _check_links(concepts, findings)
    _check_stage_gates(concepts, schemes, parents, cyclic, findings)
    if corpus:
        exclude = {Path(vocabulary_path).resolve()} if vocabulary_path else set()
        _check_corpus(concepts, corpus, exclude, findings)
    return sorted(findings, key=Finding.key), inferred_stage(concepts, schemes, parents)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('vocabulary', help='the vocabulary YAML file')
    parser.add_argument('--corpus', action='append', default=[], metavar='PATH',
                        help='file or folder the vocabulary governs; enables corpus warnings (repeatable)')
    parser.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = parser.parse_args(argv)
    try:
        data = load(args.vocabulary)
    except OSError as exc:
        print(f'{args.vocabulary}: cannot read: {exc.strerror or exc}', file=sys.stderr)
        return 2
    except yaml.YAMLError as exc:
        problem = ' '.join(str(exc).split())
        findings, stage = [Finding('ERROR', 'schema', '-', '-', f'not valid YAML: {problem}.', 'fix the YAML syntax.')], 0
    else:
        missing = [p for p in args.corpus if not Path(p).exists()]
        if missing:
            print(f"corpus path not found: {', '.join(missing)}", file=sys.stderr)
            return 2
        findings, stage = validate(data, args.corpus, args.vocabulary)
    errors = sum(f.severity == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    for finding in findings:
        print(finding.line())
    print(f'{args.vocabulary}: {errors} error(s), {warnings} warning(s), inferred stage {stage}')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
