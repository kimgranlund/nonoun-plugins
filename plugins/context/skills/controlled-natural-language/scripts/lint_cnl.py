#!/usr/bin/env python3
"""Lint governed prose against a CNL rule set and a KOS vocabulary.

Usage: lint_cnl.py RULES VOCABULARY [DOC_OR_FOLDER ...] [--strict]

Each finding is one line: SEVERITY RULE FILE:LINE: problem Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors,
2 when an input cannot be read. Rule semantics: references/patterns.md.
The vocabulary is read with the field names of knowledge-organization-system
(references/model.md there). Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

import yaml

TOP_FIELDS = ('version', 'bannedWords', 'docTypes', 'patterns')
DOCTYPE_FIELDS = ('id', 'description', 'paths', 'bannedWords')
BANNED_FIELDS = ('word', 'fix')
PATTERN_FIELDS = ('id', 'docType', 'template', 'slots', 'sources', 'deprecated', 'replacedBy')
SLOT_FIELDS = {'concept': ('type', 'concepts', 'scheme'), 'text': ('type', 'maxWords', 'pattern')}
FRONTMATTER_KEY = 'cnl'

ERROR_RULES = ('schema', 'unknown-concept', 'hidden-label', 'banned-word', 'unresolved-slot', 'no-pattern')
WARNING_RULES = ('alt-label', 'deprecated-pattern', 'no-source')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}

SKIP_DIRS = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
MAX_FILE_BYTES = 2000000
LINE_KEY = '__line__'
SLOT_RE = re.compile(r'\{(\w+)\}')
SENTENCE_END = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'(\[`])')
LIST_MARKER = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
ARTICLE = re.compile(r'^(?:the|a|an)\s+')


class Finding(namedtuple('Finding', 'severity rule path line problem fix')):
    def text(self):
        return f'{self.severity} {self.rule} {self.path}:{self.line}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', self.path, self.line, RULE_ORDER[self.rule], self.problem)


class LineLoader(yaml.SafeLoader):
    """SafeLoader that records each mapping's 1-based start line under LINE_KEY."""

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping[LINE_KEY] = node.start_mark.line + 1
        return mapping


def normalize(label):
    """Compare labels case-insensitively with collapsed whitespace, as the KOS validator does."""
    return ' '.join(str(label).casefold().split())


def term_pattern(label):
    """Whole-word, case-insensitive, trailing s or es: the KOS corpus-matching rule."""
    words = [re.escape(w) for w in str(label).split()]
    return re.compile(r'(?<!\w)' + r'\s+'.join(words) + r'(?:s|es)?(?!\w)', re.IGNORECASE)


# Vocabulary (read only; knowledge-organization-system owns its shape and validation)

class Vocabulary:
    def __init__(self, data):
        if not isinstance(data, dict) or not isinstance(data.get('concepts'), list):
            raise ValueError('not a KOS vocabulary (no `concepts` list)')
        self.schemes = {s.get('id') for s in data.get('schemes') or [] if isinstance(s, dict)}
        self.concepts = {c['id']: c for c in data['concepts'] if isinstance(c, dict) and isinstance(c.get('id'), str)}
        self.labels = {}  # normalized form -> [(concept id, kind)]
        self.retired = []  # (label, concept id, label to write instead)
        for cid, c in sorted(self.concepts.items()):
            pref, alts, hidden = c.get('prefLabel'), list(c.get('altLabel') or []), list(c.get('hiddenLabel') or [])
            if c.get('deprecated'):
                successor = self.concepts.get(c.get('replacedBy'), {}).get('prefLabel') or c.get('replacedBy') or '?'
                for label in ([pref] if pref else []) + alts + hidden:
                    self._add(label, cid, 'retired')
                    self.retired.append((label, cid, successor))
                continue
            self._add(cid, cid, 'id')
            if pref:
                self._add(pref, cid, 'prefLabel')
            for label in alts:
                self._add(label, cid, 'altLabel')
            for label in hidden:
                self._add(label, cid, 'retired')
                self.retired.append((label, cid, pref or cid))

    def _add(self, label, cid, kind):
        self.labels.setdefault(normalize(label), []).append((cid, kind))

    def resolve(self, value, allowed=None, scheme=None):
        """Return [(concept id, kind)] for a slot value, trying the article-free and singular forms."""
        text = ARTICLE.sub('', normalize(value))
        forms = [text] + ([text[:-1]] if text.endswith('s') else []) + ([text[:-2]] if text.endswith('es') else [])
        for form in forms:
            hits = [(cid, kind) for cid, kind in self.labels.get(form, [])
                    if (allowed is None or cid in allowed)
                    and (scheme is None or self.concepts[cid].get('scheme') == scheme)]
            if hits:
                return hits
        return []


# Rules

def _schema(findings, path, line, problem, fix):
    findings.append(Finding('ERROR', 'schema', path, line, problem, fix))


def _unknown_keys(findings, path, item, allowed, where):
    for key in sorted(k for k in item if k != LINE_KEY and k not in allowed):
        _schema(findings, path, item[LINE_KEY], f"{where} has unknown key '{key}'.", f"use only {', '.join(allowed)}.")


def _banned(findings, path, raw, where):
    words = []
    if raw is None:
        return words
    if not isinstance(raw, list):
        _schema(findings, path, 1, f'{where} bannedWords is not a list.', 'write `bannedWords: [{word: ..., fix: ...}]`.')
        return words
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get('word'), str) or not item['word'].strip():
            line = item[LINE_KEY] if isinstance(item, dict) else 1
            _schema(findings, path, line, f'{where} has a banned word with no `word`.', 'write `{word: ..., fix: ...}`.')
            continue
        _unknown_keys(findings, path, item, BANNED_FIELDS, f"banned word '{item['word']}'")
        fix = item.get('fix') if isinstance(item.get('fix'), str) else 'rephrase without it.'
        words.append((item['word'], fix, term_pattern(item['word'])))
    return words


def _compile_template(template):
    """Return (regex, slot names) for a template such as 'When {trigger}, the {system} shall {response}.'"""
    parts, names, pos = [], [], 0
    for m in SLOT_RE.finditer(template):
        parts.append(r'\s+'.join(re.escape(w) for w in template[pos:m.start()].split(' ')))
        parts.append(f'(?P<{m.group(1)}>.+?)')
        names.append(m.group(1))
        pos = m.end()
    parts.append(r'\s+'.join(re.escape(w) for w in template[pos:].split(' ')))
    return re.compile(''.join(parts), re.IGNORECASE), names


def _read_slot(findings, path, pattern_id, name, slot, vocab):
    line = slot.get(LINE_KEY, 1) if isinstance(slot, dict) else 1
    kind = slot.get('type') if isinstance(slot, dict) else None
    if kind not in SLOT_FIELDS:
        _schema(findings, path, line, f"pattern '{pattern_id}' slot '{name}' has no valid type.",
                'set `type: concept` or `type: text`.')
        return None
    _unknown_keys(findings, path, slot, SLOT_FIELDS[kind], f"pattern '{pattern_id}' slot '{name}'")
    spec = {'type': kind, 'line': line}
    if kind == 'concept':
        allowed = slot.get('concepts')
        if allowed is not None and (not isinstance(allowed, list) or not all(isinstance(a, str) for a in allowed)):
            _schema(findings, path, line, f"slot '{name}' concepts is not a list of ids.", 'write `concepts: [id, ...]`.')
            allowed = None
        for cid in allowed or []:
            if cid not in vocab.concepts:
                findings.append(Finding('ERROR', 'unknown-concept', path, line,
                                        f"pattern '{pattern_id}' slot '{name}' names concept id '{cid}', which the vocabulary does not define.",
                                        'add the concept to vocabulary.yaml first (knowledge-organization-system), or correct the id.'))
        scheme = slot.get('scheme')
        if scheme is not None and scheme not in vocab.schemes:
            findings.append(Finding('ERROR', 'unknown-concept', path, line,
                                    f"pattern '{pattern_id}' slot '{name}' names scheme '{scheme}', which the vocabulary does not declare.",
                                    f"use one of: {', '.join(sorted(s for s in vocab.schemes if s)) or '(none declared)'}."))
        spec['concepts'] = set(allowed) if allowed is not None else None
        spec['scheme'] = scheme
    else:
        max_words = slot.get('maxWords')
        if max_words is not None and (not isinstance(max_words, int) or max_words < 1):
            _schema(findings, path, line, f"slot '{name}' maxWords is not a positive integer.", 'write `maxWords: 20`.')
            max_words = None
        regex = slot.get('pattern')
        if regex is not None:
            try:
                regex = re.compile(regex, re.IGNORECASE)
            except (re.error, TypeError) as exc:
                _schema(findings, path, line, f"slot '{name}' pattern is not a valid regex ({exc}).", 'correct the regex.')
                regex = None
        spec['maxWords'], spec['pattern'] = max_words, regex
    return spec


def load_rules(path, vocab, findings):
    """Return (doc types, patterns) from the rules file; problems go to findings."""
    try:
        data = yaml.load(Path(path).read_text(encoding='utf-8'), Loader=LineLoader)
    except yaml.YAMLError as exc:
        _schema(findings, path, 1, f"not valid YAML: {' '.join(str(exc).split())}.", 'fix the YAML syntax.')
        return {}, []
    if not isinstance(data, dict):
        _schema(findings, path, 1, 'the file is empty or not a mapping.', 'start from templates/rules.yaml.')
        return {}, []
    _unknown_keys(findings, path, data, TOP_FIELDS, 'the rules file')
    shared = _banned(findings, path, data.get('bannedWords'), 'the rules file')
    doc_types = {}
    for item in data.get('docTypes') or []:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            _schema(findings, path, item.get(LINE_KEY, 1) if isinstance(item, dict) else 1,
                    'a doc type has no id.', 'give every doc type an `id`.')
            continue
        did = item['id']
        if did in doc_types:
            _schema(findings, path, item[LINE_KEY], f"doc type '{did}' is declared twice.", 'keep one declaration.')
            continue
        _unknown_keys(findings, path, item, DOCTYPE_FIELDS, f"doc type '{did}'")
        paths = item.get('paths') or []
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            _schema(findings, path, item[LINE_KEY], f"doc type '{did}' paths is not a list of globs.", 'write `paths: ["docs/**/*.md"]`.')
            paths = []
        doc_types[did] = {'globs': [glob_regex(p) for p in paths],
                          'banned': shared + _banned(findings, path, item.get('bannedWords'), f"doc type '{did}'"),
                          'patterns': []}
    patterns, ids = [], set()
    raw_patterns = data.get('patterns') or []
    known_ids = {p.get('id') for p in raw_patterns if isinstance(p, dict)}
    for item in raw_patterns:
        line = item.get(LINE_KEY, 1) if isinstance(item, dict) else 1
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            _schema(findings, path, line, 'a pattern has no id.', 'give every pattern a stable `id`.')
            continue
        pid = item['id']
        if pid in ids:
            _schema(findings, path, line, f"pattern id '{pid}' is used twice.", 'give each pattern its own id.')
            continue
        ids.add(pid)
        _unknown_keys(findings, path, item, PATTERN_FIELDS, f"pattern '{pid}'")
        if item.get('docType') not in doc_types:
            _schema(findings, path, line, f"pattern '{pid}' names doc type '{item.get('docType')}', which is not declared.",
                    f"use one of: {', '.join(sorted(doc_types)) or '(declare a doc type first)'}.")
            continue
        template = item.get('template')
        if not isinstance(template, str) or not template.strip():
            _schema(findings, path, line, f"pattern '{pid}' has no template.", 'write `template: "The {system} shall {response}."`.')
            continue
        regex, names = _compile_template(' '.join(template.split()))
        raw_slots = item.get('slots') or {}
        raw_slots = {k: v for k, v in raw_slots.items() if k != LINE_KEY} if isinstance(raw_slots, dict) else {}
        if len(set(names)) != len(names) or set(names) != set(raw_slots):
            _schema(findings, path, line, f"pattern '{pid}' template slots {sorted(set(names))} do not match its declared slots {sorted(raw_slots)}.",
                    'declare each {slot} in the template once under `slots`, and nothing else.')
            continue
        slots = {name: _read_slot(findings, path, pid, name, raw_slots[name], vocab) for name in names}
        if None in slots.values():
            continue
        deprecated = item.get('deprecated', False) is True
        if deprecated and item.get('replacedBy') not in known_ids - {pid}:
            _schema(findings, path, line, f"deprecated pattern '{pid}' has no valid replacedBy.",
                    'set `replacedBy:` to the id of the pattern that replaces it.')
        sources = item.get('sources')
        if not isinstance(sources, list) or not [s for s in sources if isinstance(s, str) and s.strip()]:
            findings.append(Finding('WARNING', 'no-source', path, line,
                                    f"pattern '{pid}' records no source sentence.",
                                    'add `sources:` with the real sentence and path:line it was derived from, or remove the pattern.'))
        pattern = {'id': pid, 'template': ' '.join(template.split()), 'regex': regex, 'slots': slots,
                   'deprecated': deprecated, 'replacedBy': item.get('replacedBy')}
        doc_types[item['docType']]['patterns'].append(pattern)
        patterns.append(pattern)
    for dt in doc_types.values():  # active patterns are tried first, then retired ones
        dt['patterns'].sort(key=lambda p: p['deprecated'])
    return doc_types, patterns


def glob_regex(glob):
    """Translate a path glob (** spans folders, * and ? stay inside one) to a regex."""
    out, i = [], 0
    while i < len(glob):
        if glob.startswith('**/', i):
            out.append('(?:.*/)?')
            i += 3
        elif glob.startswith('**', i):
            out.append('.*')
            i += 2
        elif glob[i] == '*':
            out.append('[^/]*')
            i += 1
        elif glob[i] == '?':
            out.append('[^/]')
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile(''.join(out) + r'\Z')


# Documents

def split_frontmatter(lines):
    """Return (front matter mapping, index of the first body line)."""
    if not lines or lines[0].strip() != '---':
        return {}, 0
    for i in range(1, len(lines)):
        if lines[i].strip() in ('---', '...'):
            try:
                data = yaml.safe_load('\n'.join(lines[1:i]))
            except yaml.YAMLError:
                data = None
            return (data if isinstance(data, dict) else {}), i + 1
    return {}, 0


def mask_code(text):
    """Blank inline code spans (same length) so quoted code is not checked as prose."""
    return re.sub(r'`[^`]*`', lambda m: ' ' * len(m.group(0)), text)


def units(lines, start):
    """Yield (kind, text, line numbers per character) for the governed body.

    kind is 'paragraph' for paragraphs and list items (checked against patterns) and
    'line' for headings, table rows and quotes (checked for words only). Code fences,
    inline code and HTML comments are skipped.
    """
    para, fence, comment = None, None, False

    def flush():
        if para and para[0].strip():
            return [('paragraph', para[0], para[1])]
        return []

    for n in range(start, len(lines)):
        raw, lineno = lines[n], n + 1
        stripped = raw.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        if stripped.startswith('```') or stripped.startswith('~~~'):
            yield from flush()
            para, fence = None, stripped[:3]
            continue
        if comment or '<!--' in raw:
            text, comment = _strip_comments(raw, comment)
            raw, stripped = text, text.strip()
        if not stripped:
            yield from flush()
            para = None
            continue
        if stripped.startswith(('#', '|', '>')):
            yield from flush()
            para = None
            yield ('line', raw, [lineno] * len(raw))
            continue
        marker = LIST_MARKER.match(raw)
        if marker:
            yield from flush()
            body = raw[marker.end():]
            para = [body, [lineno] * len(body)]
            continue
        if para is None:
            para = [stripped, [lineno] * len(stripped)]
        else:
            para[0] += ' ' + stripped
            para[1] += [lineno] * (len(stripped) + 1)
    yield from flush()


def _strip_comments(text, inside):
    out, i = [], 0
    while i < len(text):
        if inside:
            end = text.find('-->', i)
            if end < 0:
                return ''.join(out), True
            i, inside = end + 3, False
        else:
            begin = text.find('<!--', i)
            if begin < 0:
                out.append(text[i:])
                break
            out.append(text[i:begin])
            i, inside = begin + 4, True
    return ''.join(out), inside


def sentences(text, linemap):
    """Split a paragraph into (sentence, start line)."""
    pos = 0
    for m in list(SENTENCE_END.finditer(text)) + [None]:
        end = m.start() if m else len(text)
        chunk = text[pos:end]
        if chunk.strip():
            offset = pos + len(chunk) - len(chunk.lstrip())
            yield ' '.join(chunk.split()), linemap[min(offset, len(linemap) - 1)]
        pos = m.end() if m else end


def doc_type_of(path, front, doc_types, rules_dir):
    declared = front.get(FRONTMATTER_KEY)
    if declared is not None:
        return str(declared)
    candidates = {Path(path).as_posix()}
    for base in (Path.cwd(), rules_dir):
        try:
            candidates.add(Path(path).resolve().relative_to(base.resolve()).as_posix())
        except ValueError:
            pass
    for did, dt in sorted(doc_types.items()):
        if any(g.match(c) for g in dt['globs'] for c in candidates):
            return did
    return None


def check_slots(pattern, match, vocab):
    """Return (unresolved [(slot, value)], text failures [str], altLabel uses [(value, concept id)])."""
    unresolved, failures, alts = [], [], []
    for name, spec in pattern['slots'].items():
        value = match.group(name).strip()
        if spec['type'] == 'concept':
            hits = vocab.resolve(value, spec['concepts'], spec['scheme'])
            if not hits:
                unresolved.append((name, value))
            elif all(kind == 'altLabel' for _, kind in hits):
                alts.append((value, hits[0][0]))
        else:
            if spec['maxWords'] and len(value.split()) > spec['maxWords']:
                failures.append(f"slot '{name}' has {len(value.split())} words, limit {spec['maxWords']}")
            if spec['pattern'] and not spec['pattern'].fullmatch(value):
                failures.append(f"slot '{name}' value '{value}' does not match {spec['pattern'].pattern}")
    return unresolved, failures, alts


def check_sentence(path, line, sentence, doc_type, vocab, findings):
    templates = {p['id']: f'"{p["template"]}"' for p in doc_type['patterns']}
    near = []  # patterns whose shape matched but whose slots failed
    for pattern in doc_type['patterns']:
        match = pattern['regex'].fullmatch(sentence)
        if not match:
            continue
        unresolved, failures, alts = check_slots(pattern, match, vocab)
        if not unresolved and not failures:
            for value, cid in alts:
                findings.append(Finding('WARNING', 'alt-label', path, line,
                                        f"slot value '{value}' is an altLabel of concept '{cid}'; pattern '{pattern['id']}' expects the prefLabel.",
                                        f"write '{vocab.concepts[cid].get('prefLabel')}'."))
            if pattern['deprecated']:
                findings.append(Finding('WARNING', 'deprecated-pattern', path, line,
                                        f"sentence matches only retired pattern '{pattern['id']}'.",
                                        f"rewrite it to pattern '{pattern['replacedBy']}' ({templates.get(pattern['replacedBy'], '?')}); delete the retired pattern once no governed doc uses it."))
            return
        near.append((pattern, unresolved, failures))
    concept_only = [n for n in near if n[1] and not n[2]]
    if concept_only:
        pattern, unresolved, _ = concept_only[0]
        for name, value in unresolved:
            findings.append(Finding('ERROR', 'unresolved-slot', path, line,
                                    f"slot '{name}' of pattern '{pattern['id']}' holds '{value}', which resolves to no vocabulary concept.",
                                    'use a concept id, prefLabel or altLabel from vocabulary.yaml; if the term is new, add it there first (knowledge-organization-system).'))
        return
    active = [f'"{p["template"]}"' for p in doc_type['patterns'] if not p['deprecated']]
    reason = ''
    if near:
        pattern, unresolved, failures = near[0]
        problems = failures + [f"slot '{name}' value '{value}' resolves to no concept" for name, value in unresolved]
        reason = f" ({'; '.join(problems)} in pattern '{pattern['id']}')"
    findings.append(Finding('ERROR', 'no-pattern', path, line,
                            f"sentence matches no pattern{reason}: \"{sentence}\"",
                            f"rewrite it to one of {' | '.join(active) or '(no active pattern)'}, or add a pattern once this shape recurs 3 times (Stage 2)."))


def check_words(path, text, linemap, doc_type, vocab, findings, seen):
    masked = mask_code(text)
    for label, cid, use in vocab.retired:
        for m in term_pattern(label).finditer(masked):
            line = linemap[m.start()]
            if ('hidden-label', line, normalize(label)) not in seen:
                seen.add(('hidden-label', line, normalize(label)))
                findings.append(Finding('ERROR', 'hidden-label', path, line,
                                        f"'{m.group(0)}' is a retired label of concept '{cid}'.",
                                        f"write '{use}'."))
    for word, fix, regex in doc_type['banned']:
        for m in regex.finditer(masked):
            line = linemap[m.start()]
            if ('banned-word', line, normalize(word)) not in seen:
                seen.add(('banned-word', line, normalize(word)))
                findings.append(Finding('ERROR', 'banned-word', path, line, f"banned word '{m.group(0)}'.", fix))


def lint_doc(path, text, doc_types, vocab, rules_dir, findings):
    """Return True when the doc is governed by a doc type."""
    lines = text.splitlines()
    front, start = split_frontmatter(lines)
    did = doc_type_of(path, front, doc_types, rules_dir)
    if did is None:
        return False
    if did not in doc_types:
        _schema(findings, path, 1, f"front matter names doc type '{did}', which the rules do not declare.",
                f"use one of: {', '.join(sorted(doc_types)) or '(none declared)'}.")
        return True
    doc_type, seen = doc_types[did], set()
    for kind, body, linemap in units(lines, start):
        check_words(path, body, linemap, doc_type, vocab, findings, seen)
        if kind == 'paragraph':
            for sentence, line in sentences(body, linemap):
                check_sentence(path, line, sentence, doc_type, vocab, findings)
    return True


def doc_files(paths):
    """Yield (display path, text) for readable text files under the given paths, sorted."""
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(
            p for p in root.rglob('*')
            if p.is_file() and not any(part in SKIP_DIRS or part.startswith('.') for part in p.relative_to(root).parts))
        for path in files:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            try:
                yield str(path), path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue


def lint(rules_path, vocab, docs):
    """Return (sorted findings, governed doc count, ungoverned file count)."""
    findings = []
    doc_types, _ = load_rules(rules_path, vocab, findings)
    governed = ungoverned = 0
    for path, text in doc_files(docs):
        if lint_doc(path, text, doc_types, vocab, Path(rules_path).parent, findings):
            governed += 1
        else:
            ungoverned += 1
    return sorted(set(findings), key=Finding.key), governed, ungoverned


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('rules', help='the CNL rules YAML file')
    parser.add_argument('vocabulary', help='the KOS vocabulary YAML file (knowledge-organization-system)')
    parser.add_argument('docs', nargs='*', metavar='DOC', help='governed docs or folders; none checks the rules alone')
    parser.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = parser.parse_args(argv)
    for path in [args.rules, args.vocabulary] + args.docs:
        if not Path(path).exists():
            print(f'{path}: not found', file=sys.stderr)
            return 2
    try:
        vocab = Vocabulary(yaml.safe_load(Path(args.vocabulary).read_text(encoding='utf-8')))
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f'{args.vocabulary}: cannot read vocabulary: {" ".join(str(exc).split())}. '
              'Check it with knowledge-organization-system/scripts/validate_kos.py.', file=sys.stderr)
        return 2
    findings, governed, ungoverned = lint(args.rules, vocab, args.docs)
    errors = sum(f.severity == 'ERROR' for f in findings)
    for finding in findings:
        print(finding.text())
    print(f'{args.rules}: {errors} error(s), {len(findings) - errors} warning(s), '
          f'{governed} governed doc(s), {ungoverned} ungoverned file(s)')
    return 1 if errors or (args.strict and len(findings) > errors) else 0


if __name__ == '__main__':
    sys.exit(main())
