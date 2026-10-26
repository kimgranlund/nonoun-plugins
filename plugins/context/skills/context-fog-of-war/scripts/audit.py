#!/usr/bin/env python3
"""Static contract audit of a harness's guidance surfaces (stdlib only).

Reads catalogs, schemas, skills, prompts, exemplars, checks, generated files and oracles as text or JSON.
It never executes, imports or fetches anything it reads. Every finding is a candidate for the agent's
semantic review, never a verdict. The rubric and each detector's blind spots: references/contract-audit.md.
"""
import argparse
import bisect
import hashlib
import json
import os
import re
import sys
from pathlib import Path

VERSION = '1.1.0'
PRUNE = {'.git', 'node_modules', 'dist', 'build', 'coverage', '.venv', 'venv', '__pycache__', '.next', '.cache', '.turbo', 'vendor', 'target'}
MAX_FILES, MAX_BYTES = 5000, 2 * 1024 * 1024
EVIDENCE_CAP = 50  # evidence lines kept per finding; metrics carry the full count
DISCOVERY = [
    ('schema', ['**/*.schema.json']),
    ('catalog', ['**/catalog*.json', '**/registry*.json']),
    ('skill', ['**/SKILL.md', '**/skills/**/*.md']),
    ('prompt', ['**/prompts/**/*.md', '**/*prompt*.md', '**/*persona*.md', '**/*system*.md']),
    ('guide', ['**/AGENTS.md', '**/CLAUDE.md']),
    ('exemplar', ['**/examples/**/*.json', '**/exemplars/**/*.json', '**/corpus/**/*.jsonl']),
    ('generated', ['**/*.gen.*', '**/*.generated.*']),
    ('oracle', ['**/evals/**/*.json', '**/scenarios/**/*', '**/*oracle*']),
]
PASCAL = r'\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b'
IDS = r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b'
NEG = re.compile(r"\b(?:never|not|no longer|don't|do not|dont|avoid|instead of|rather than|cannot|can't|must not|shouldn't|forbidden|excluded?)\b", re.I)
POS = re.compile(r'\b(?:must|should|always|use|uses|prefer|prefers|pick|choose|is one|are one|expects?|stays? (?:a|an|for)|reach for)\b', re.I)
NEGATED = re.compile(r"\b(?:no|not|never|without|non)\b[^,;:.]*", re.I)
NEG_KEY = re.compile(r'(?i)not|avoid|never|exclud|forbid|dont|deny|anti')
POS_KEY = re.compile(r'(?i)intent|^use|usewhen|when$|prefer|should|must|allow|^do$')
WORD = re.compile(r'[A-Za-z][a-z]{3,}')
STOP = set('''that this with from into when then than they them their there these those what which while where have has
had been being were will would could should must never always each only also just like such some many more most other
another same very your yours ours over under after before about above below again once here does done make makes made
used uses using want wants need needs keep keeps stay stays send sends show shows draw draws pick picks choose prefer
render renders expect expects reach list item items avoid instead rather cannot shouldn''t'''.split())
DETECTOR_FAMILY = {
    'cross-surface-conflict': ('Cross-surface conflict', 'b'),
    'undefined-reference': ('Cross-surface conflict', 'b'),
    'schema-mismatch': ('Repair or exemplar that fails its own schema', 'b'),
    'stale-generated': ('Stale generated artifact', 'b'),
    'index-only-rule': ('Index-only rule', 'b'),
    'modality-leak': ('Type named in modality-free text', 'b'),
    'generic-oracle': ('Oracle too generic', 'd'),
}
LIMITS = [
    'Findings are candidates from lexical heuristics; each needs semantic review before it becomes a ticket.',
    'Conflict precision: a ruling-out entry (a notFor reason or similar) that describes an adjacent situation pairs as a conflict by design; in the field run 0 of the 12 reviewed candidates (of 54, no topics) and 0 of 8 (with topics) held on the current tree, while 2 of 9 held on a pre-fix snapshot that had a real conflict, so declared topics cut the count, not the shape, and every pair must be reviewed before one is reported.',
    'Line-scoped analysis: a rule split across lines or built at run time is not read as one statement.',
    'Load modes (full, index-only, triggered) come from the mapping; a static read cannot observe them.',
    'No finding means no mechanical signal, not a coherent contract. Literal-reading hazards, narrow checks and coverage gaps are rubric-only.',
]

# ---------- files and globs ----------

def glob_re(pattern):
    out, i = '', 0
    while i < len(pattern):
        if pattern.startswith('**/', i): out += '(?:.*/)?'; i += 3
        elif pattern.startswith('**', i): out += '.*'; i += 2
        elif pattern[i] == '*': out += '[^/]*'; i += 1
        elif pattern[i] == '?': out += '[^/]'; i += 1
        else: out += re.escape(pattern[i]); i += 1
    return re.compile(out + r'\Z')

def literal_prefix(pattern):
    parts = []
    for part in pattern.split('/')[:-1]:
        if any(c in part for c in '*?['): break
        parts.append(part)
    return '/'.join(parts)

def mapping_globs(mapping):
    globs = [g for s in mapping.get('surfaces') or [] for g in s.get('paths') or []]
    globs += [s['path'] for s in (mapping.get('entities') or {}).get('fromJson') or []]
    globs += [g for s in mapping.get('schemas') or [] for i in s.get('instances') or [] for g in i.get('paths') or []]
    globs += [g for s in mapping.get('generated') or [] for g in (s.get('sources') or []) + [s.get('output', '')]]
    return globs

def walk(root, prefixes=('',)):
    """Relative file paths under root, walking only the given folder prefixes (a mapping's literal glob prefixes)."""
    files, seen = [], set()
    for prefix in sorted(set(prefixes)):
        if any(prefix == s or prefix.startswith(s + '/') for s in seen if s) or '' in seen: continue
        seen.add(prefix); start = os.path.join(root, prefix) if prefix else root
        if os.path.isdir(start) and not os.path.islink(start): files += walk_dir(root, start)
        if len(files) > MAX_FILES: raise ValueError('More than %d files under the scanned folders; narrow the mapping globs' % MAX_FILES)
    return sorted(set(files))

def walk_dir(root, start):
    files = []
    for base, dirs, names in os.walk(start, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in PRUNE and not os.path.islink(os.path.join(base, d)))
        for name in sorted(names):
            path = os.path.join(base, name)
            if os.path.islink(path) or not os.path.isfile(path): continue
            files.append(Path(path).relative_to(root).as_posix())
            if len(files) > MAX_FILES: raise ValueError('More than %d files under the scanned folders; narrow the mapping globs' % MAX_FILES)
    return files

def match(files, patterns):
    regs = [glob_re(p) for p in patterns]
    return [f for f in files if any(r.match(f) for r in regs)]

def read_text(root, rel):
    path = Path(root) / rel
    if path.stat().st_size > MAX_BYTES: return None
    try: return path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError): return None

def pointer_all(value, ptr):
    """JSON Pointer with '*' matching every key or index; yields (pointer, value)."""
    if ptr in ('', None):
        yield '', value; return
    parts = [p.replace('~1', '/').replace('~0', '~') for p in ptr[1:].split('/')]
    def go(v, i, at):
        if i == len(parts):
            yield at, v; return
        key = parts[i]
        if key == '*':
            items = v.items() if isinstance(v, dict) else enumerate(v) if isinstance(v, list) else []
            for k, child in items: yield from go(child, i + 1, at + '/' + str(k))
        elif isinstance(v, dict) and key in v: yield from go(v[key], i + 1, at + '/' + key)
        elif isinstance(v, list) and key.isdigit() and int(key) < len(v): yield from go(v[int(key)], i + 1, at + '/' + key)
    yield from go(value, 0, '')

class Lines:
    def __init__(self, text):
        self.text = text; self.starts = [0] + [m.end() for m in re.finditer('\n', text)]; self.cursor = 0
    def line(self, offset): return bisect.bisect_right(self.starts, offset)
    def find(self, needle):
        """Line of the next occurrence of needle at or after the cursor (document order), else the cursor line."""
        if needle:
            at = self.text.find(needle, self.cursor)
            if at >= 0:
                self.cursor = at + 1; return self.line(at)
        return self.line(self.cursor)
    def excerpt(self, n): return self.text[self.starts[n - 1]:self.starts[n] if n < len(self.starts) else len(self.text)].strip()[:240]

# ---------- statements ----------

def frontmatter(text):
    if not text.startswith('---\n'): return 0
    end = text.find('\n---', 4)
    return text[:end].count('\n') + 2 if end > 0 else 0

def clauses(text):
    text = re.sub(r'\([^)]*\)', lambda m: m.group().replace(',', ' '), text)
    return [c for c in re.split(r'[;:.!?]|,|\bbut\b|\bwhile\b', text) if c.strip()]

def words(text, names):
    lowered = {n.lower() for n in names}
    text = re.sub(r'\b[A-Za-z]*[a-z][A-Z]\w*', ' ', text)  # camelCase and PascalCase tokens are names, not topic words
    return {w.lower() for w in WORD.findall(text) if w.lower() not in STOP and w.lower() not in lowered}

def stem_eq(a, b):
    if a == b: return True
    short, long_ = sorted((a, b), key=len)
    return len(short) >= 4 and long_.startswith(short) or len(os.path.commonprefix([a, b])) >= 5

def shares(ws, vs):
    return [w for w in ws if any(stem_eq(w, v) for v in vs)]

def json_strings(value, path=()):
    """Yield (string, ancestor keys) in document order."""
    if isinstance(value, dict):
        for k, v in value.items(): yield from json_strings(v, path + (str(k),))
    elif isinstance(value, list):
        for v in value: yield from json_strings(v, path)
    elif isinstance(value, str):
        yield value, path

def statements(rel, text, surface, vocab):
    """One statement per line of text, or per string value of JSON / JSONL. Each carries its entity mentions with polarity."""
    out, lines = [], Lines(text)
    index = surface.get('index') or {}
    fm = frontmatter(text) if rel.endswith('.md') else 0
    def add(n, body, is_index=False, ctx=None, ctx_pol=None, from_json=False):
        mentions = []
        directive = bool(NEG.search(body) or POS.search(body) or ctx_pol or surface.get('kind') == 'oracle')  # an oracle line asserts what it expects
        for c in clauses(body):
            pol = None if not directive else 'neg' if NEG.search(c) else 'pos' if not from_json or POS.search(c) else None
            mentions += [(m.group(), pol) for m in vocab.finditer(c)]
        if ctx: mentions.append((ctx, ctx_pol))
        # A ruling-out entry read from a JSON key describes its situation; its own negations ("no price") name features, not topics.
        topic = NEGATED.sub(' ', body) if from_json and ctx_pol == 'neg' else body
        out.append({'path': rel, 'line': n, 'text': body, 'topic': topic, 'index': is_index, 'directive': directive, 'mentions': mentions})
    if rel.endswith('.json') or rel.endswith('.jsonl'):
        docs = []
        if rel.endswith('.jsonl'):
            for n, raw in enumerate(text.splitlines(), 1):
                try: docs.append((json.loads(raw), n))
                except ValueError: pass
        else:
            try: docs.append((json.loads(text), None))
            except ValueError: docs = []
        if docs:
            for doc, fixed in docs:
                for s, path in json_strings(doc):
                    keys = [k for k in path if vocab and vocab.fullmatch(k)]
                    ctx = keys[-1] if keys else None
                    tail = path[path.index(ctx) + 1:] if ctx else path
                    pol = 'neg' if any(NEG_KEY.search(k) for k in tail) else 'pos' if any(POS_KEY.search(k) for k in tail) else None
                    n = fixed or lines.find(json.dumps(s, ensure_ascii=False)[1:-1][:60])
                    add(n, s, ctx=ctx if pol else None, ctx_pol=pol, from_json=True)
            return out
    pattern = re.compile(index['linePattern']) if index.get('linePattern') else None
    key = index.get('frontmatter')
    regions = [(re.compile(r['start']), re.compile(r['end'])) for r in surface.get('regions') or []]
    include, exclude = ([re.compile(r) for r in ([surface[k]] if isinstance(surface[k], str) else surface[k])] if surface.get(k) else None for k in ('include', 'exclude'))
    inside = None
    for n, body in enumerate(text.splitlines(), 1):
        if n <= fm:
            if key and re.match(r'\s*%s\s*:' % re.escape(key), body): add(n, body.split(':', 1)[1].strip(), True)
            continue
        if regions:
            if inside is not None and inside[1].search(body): inside = None
            if inside is None: inside = next((r for r in regions if r[0].search(body)), None)
            if inside is None: continue
        if include and not any(r.search(body) for r in include) or exclude and any(r.search(body) for r in exclude): continue
        if body.strip(): add(n, body, bool(pattern and pattern.search(body)))
    return out

# ---------- mapping and inventory ----------

def load_vocab(root, mapping, files):
    ent = mapping.get('entities') or {}
    names = set(ent.get('names') or [])
    for spec in ent.get('fromJson') or []:
        for rel in match(files, [spec['path']]):
            try: doc = json.loads(read_text(root, rel) or 'null')
            except ValueError: continue
            for _, v in pointer_all(doc, spec.get('pointer', '')):
                if spec.get('take', 'keys') == 'keys' and isinstance(v, dict): names.update(v)
                elif isinstance(v, str): names.add(v)
                elif isinstance(v, list): names.update(x for x in v if isinstance(x, str))
    names -= set(ent.get('ignore') or [])
    declared = sorted(names)
    if declared: regex = re.compile(r'\b(?:%s)\b' % '|'.join(re.escape(n) for n in sorted(declared, key=len, reverse=True)))
    else: regex = re.compile(ent['pattern'] if ent.get('pattern') else PASCAL)
    return declared, regex

def inventory(root, mapping, files):
    surfaces = []
    if mapping:
        for s in mapping.get('surfaces') or []:
            for rel in match(files, s.get('paths') or []):
                surfaces.append(dict(s, path=rel))
    else:
        for kind, globs in DISCOVERY:
            for rel in match(files, globs):
                if not any(x['path'] == rel for x in surfaces):
                    surfaces.append({'id': kind, 'kind': kind, 'path': rel, 'load': 'unknown'})
    return surfaces

# ---------- JSON Schema subset ----------

SUPPORTED = {'type', 'enum', 'const', 'required', 'properties', 'additionalProperties', 'items', 'minItems', 'maxItems',
             'minLength', 'maxLength', 'pattern', 'minimum', 'maximum', '$ref', 'allOf', 'anyOf', 'oneOf', 'not'}
ANNOTATION = {'title', 'description', 'default', 'examples', '$schema', '$id', '$defs', 'definitions', '$comment', 'format', 'deprecated', 'readOnly', 'writeOnly'}
TYPES = {'string': str, 'object': dict, 'array': list, 'boolean': bool, 'null': type(None)}

def is_type(v, t):
    if t == 'integer': return isinstance(v, int) and not isinstance(v, bool)
    if t == 'number': return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, TYPES.get(t, ()))

def validate(v, schema, rootdoc, at='', unsupported=None):
    """Errors for v against a JSON Schema subset; unknown keywords are collected, never failed."""
    if schema is True or schema is None: return []
    if schema is False: return ['%s: not allowed' % (at or '/')]
    errs = []
    for k in schema:
        if k not in SUPPORTED and k not in ANNOTATION and unsupported is not None: unsupported.add(k)
    if '$ref' in schema:
        ref = schema['$ref']
        target = next((t for _, t in pointer_all(rootdoc, ref[1:])), None) if ref.startswith('#') else None
        if target is None: unsupported is not None and unsupported.add('$ref ' + ref)
        else: errs += validate(v, target, rootdoc, at, unsupported)
    if 'type' in schema:
        ts = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(is_type(v, t) for t in ts): return errs + ['%s: expected %s' % (at or '/', '|'.join(ts))]
    if 'enum' in schema and v not in schema['enum']: errs.append('%s: %r not in enum' % (at or '/', v))
    if 'const' in schema and v != schema['const']: errs.append('%s: expected const %r' % (at or '/', schema['const']))
    if isinstance(v, dict):
        for r in schema.get('required') or []:
            if r not in v: errs.append('%s: missing required %r' % (at or '/', r))
        props = schema.get('properties') or {}
        for k, child in v.items():
            if k in props: errs += validate(child, props[k], rootdoc, at + '/' + k, unsupported)
            elif schema.get('additionalProperties') is False: errs.append('%s: unexpected property %r' % (at or '/', k))
            elif isinstance(schema.get('additionalProperties'), dict): errs += validate(child, schema['additionalProperties'], rootdoc, at + '/' + k, unsupported)
    if isinstance(v, list):
        if isinstance(schema.get('items'), dict):
            for i, child in enumerate(v): errs += validate(child, schema['items'], rootdoc, '%s/%d' % (at, i), unsupported)
        if len(v) < schema.get('minItems', 0): errs.append('%s: fewer than %d items' % (at or '/', schema['minItems']))
        if 'maxItems' in schema and len(v) > schema['maxItems']: errs.append('%s: more than %d items' % (at or '/', schema['maxItems']))
    if isinstance(v, str):
        if len(v) < schema.get('minLength', 0): errs.append('%s: shorter than %d' % (at or '/', schema['minLength']))
        if 'maxLength' in schema and len(v) > schema['maxLength']: errs.append('%s: longer than %d' % (at or '/', schema['maxLength']))
        if 'pattern' in schema and not re.search(schema['pattern'], v): errs.append('%s: does not match %s' % (at or '/', schema['pattern']))
    if is_type(v, 'number'):
        if 'minimum' in schema and v < schema['minimum']: errs.append('%s: below %s' % (at or '/', schema['minimum']))
        if 'maximum' in schema and v > schema['maximum']: errs.append('%s: above %s' % (at or '/', schema['maximum']))
    for sub in schema.get('allOf') or []: errs += validate(v, sub, rootdoc, at, unsupported)
    if 'anyOf' in schema and not any(not validate(v, s, rootdoc, at, unsupported) for s in schema['anyOf']): errs.append('%s: matches no anyOf branch' % (at or '/'))
    if 'oneOf' in schema and sum(not validate(v, s, rootdoc, at, unsupported) for s in schema['oneOf']) != 1: errs.append('%s: matches not exactly one oneOf branch' % (at or '/'))
    if 'not' in schema and not validate(v, schema['not'], rootdoc, at, unsupported): errs.append('%s: matches a not schema' % (at or '/'))
    return errs

def snippets(text, mode):
    """(line, parsed JSON) for fenced json blocks, or for every balanced {...} that parses as strict JSON."""
    lines, out = Lines(text), []
    if mode in ('fenced', 'both'):
        for m in re.finditer(r'```(?:json|jsonc)?[ \t]*\n(.*?)```', text, re.S):
            try: out.append((lines.line(m.start(1)), json.loads(m.group(1))))
            except ValueError: pass
    if mode in ('objects', 'both'):
        i = 0
        while True:
            i = text.find('{', i)
            if i < 0: break
            depth, j, quote = 0, i, None
            while j < len(text):
                ch = text[j]
                if quote:
                    if ch == '\\': j += 1
                    elif ch == quote: quote = None
                elif ch == '"': quote = ch
                elif ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: break
                j += 1
            try:
                doc = json.loads(text[i:j + 1])
                if isinstance(doc, dict) and doc and not any(line == lines.line(i) for line, _ in out): out.append((lines.line(i), doc))
                i = j + 1
            except ValueError: i += 1
    return out

# ---------- detectors ----------

def finding(ctx, detector, title, observation, evidence, entities=(), confidence='medium', metrics=None, cause=None):
    family, default_cause = DETECTOR_FAMILY[detector]
    cites = [{'path': p, 'line': n, 'excerpt': ctx['excerpt'](p, n)} for p, n in evidence]
    return {'detector': detector, 'family': family, 'causeClass': cause or default_cause, 'status': 'candidate', 'confidence': confidence,
            'title': title, 'observation': observation, 'evidence': cites, 'entities': sorted(set(entities)), 'metrics': metrics or {}}

def cov(state, eligible, reason=None, next_evidence=None):
    return {'state': state, 'eligible': eligible, 'reason': reason, 'nextEvidence': next_evidence}

def detect_conflict(ctx):
    """Same entity directed on one surface and ruled out on another, in statements that share a topic word."""
    topics = [t.lower() for t in ctx['mapping'].get('topics') or []]
    pos, neg = {}, {}
    for st in ctx['statements']:
        for name, pol in st['mentions']:
            if pol: (pos if pol == 'pos' else neg).setdefault(name, []).append(st)
    found, eligible = [], 0
    for name in sorted(set(pos) & set(neg)):
        best = {}
        for p in pos[name]:
            for n in neg[name]:
                if p['surface'] == n['surface'] or (p['scope'] and n['scope'] and not set(p['scope']) & set(n['scope'])): continue
                eligible += 1
                wp, wn = words(p['topic'], ctx['names']), words(n['topic'], ctx['names'])
                small, large = sorted((wp, wn), key=len)
                common = [t for t in topics if shares([t], wp) and shares([t], wn)] if topics else shares(small, large)
                ratio = len(set(shares(small, large))) / max(1, len(small))
                if not common or (not topics and (len(set(common)) < 2 or ratio < 0.3)): continue
                pair = tuple(sorted((p['surface'], n['surface'])))
                if pair not in best or ratio > best[pair][0]: best[pair] = (ratio, p, n, common)
        for ratio, p, n, common in best.values():
            found.append(finding(ctx, 'cross-surface-conflict', '%s: directed on %s, ruled out on %s' % (name, p['surface'], n['surface']),
                'One statement directs %s and another rules it out; shared topic words: %s (overlap %.2f). Same situation or not is a semantic call.' % (name, ', '.join(sorted(set(common))[:5]), ratio),
                [(p['path'], p['line']), (n['path'], n['line'])], [name], metrics={'overlap': round(ratio, 2)}))
    found.sort(key=lambda f: -f['metrics']['overlap'])
    return found, cov('assessed' if eligible else 'abstained', eligible, None if eligible else 'No entity has both a directing and a ruling-out statement on different surfaces.')

def detect_undefined(ctx):
    """A name shaped like an entity, used in a directive on a non-authority surface, that no authority surface defines."""
    if not ctx['declared'] or not any(s.get('authority') for s in ctx['surfaces']):
        return [], cov('abstained', 0, 'No declared entity vocabulary or no authority surface.', 'Mark the catalog surface "authority": true and declare entities.fromJson.')
    ref = re.compile((ctx['mapping'].get('entities') or {}).get('referencePattern') or PASCAL)
    known, ignore = set(ctx['declared']), set((ctx['mapping'].get('entities') or {}).get('ignore') or [])
    hits, eligible = {}, 0
    for st in ctx['statements']:
        if st['authority'] or not st['directive']: continue
        for m in ref.finditer(st['text']):
            eligible += 1
            if m.group() not in known and m.group() not in ignore: hits.setdefault(m.group(), []).append(st)
    found = [finding(ctx, 'undefined-reference', '%s is named in guidance but defined on no authority surface' % name,
                     '%d directive statement(s) name %s; the authority surfaces define %d entities and not this one.' % (len(sts), name, len(known)),
                     [(s['path'], s['line']) for s in sts[:3]], [name], metrics={'statements': len(sts)}) for name, sts in sorted(hits.items())]
    return found, cov('assessed', eligible)

def detect_schema(ctx):
    specs = ctx['mapping'].get('schemas') or []
    if not specs: return [], cov('abstained', 0, 'No schemas declared in the mapping.', 'Add schemas[] with a schema path and the instances (exemplars, repair snippets) it governs.')
    found, eligible, unsupported = [], 0, set()
    for spec in specs:
        schema_path, _, frag = spec['schema'].partition('#')
        try: rootdoc = json.loads(read_text(ctx['root'], schema_path) or 'null')
        except (OSError, ValueError): rootdoc = None
        schema = next((v for _, v in pointer_all(rootdoc, frag)), None) if rootdoc is not None else None
        if schema is None:
            ctx['issues'].append('schema %s not found or not JSON' % spec['schema']); continue
        for inst in spec.get('instances') or []:
            for rel in match(ctx['files'], inst.get('paths') or []):
                text = read_text(ctx['root'], rel)
                if text is None: continue
                docs = []
                if rel.endswith('.jsonl') or rel.endswith('.json'):
                    for n, raw in (enumerate(text.splitlines(), 1) if rel.endswith('.jsonl') else [(None, text)]):
                        try: docs.append((n, json.loads(raw)))
                        except ValueError: pass
                else: docs = snippets(text, inst.get('snippets', 'both'))
                lines = Lines(text)
                for n, doc in docs:
                    for at, item in pointer_all(doc, inst.get('pointer', '')):
                        line = n or lines.find(json.dumps(next((s for s, _ in json_strings(item)), ''), ensure_ascii=False)[1:-1][:60])
                        where = inst.get('where') or {}
                        if any(next((v for _, v in pointer_all(item, k)), None) != want for k, want in where.items()): continue
                        eligible += 1
                        errs = validate(item, schema, rootdoc, '', unsupported)
                        if not errs: continue
                        label = spec.get('id') or schema_path
                        found.append(finding(ctx, 'schema-mismatch', '%s instance fails %s' % (rel, label),
                            'Instance %s fails the schema it teaches or repairs toward: %s' % (at or '/', '; '.join(errs[:4])),
                            [(rel, line)], [v for k, v in where.items() if isinstance(v, str)], metrics={'errors': len(errs)}, cause=inst.get('causeClass')))
    if unsupported: ctx['issues'].append('schema keywords not checked (abstained): ' + ', '.join(sorted(unsupported)))
    return found, cov('assessed' if eligible else 'abstained', eligible, None if eligible else 'No instance matched the declared paths, pointer and where filter.')

def unescape(text):
    text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
    return re.sub(r'\\(.)', lambda m: {'n': '\n', 't': '\t'}.get(m.group(1), m.group(1)), text)

def embedded_forms(line):
    js = json.dumps(line)[1:-1]
    return {line, js, json.dumps(line, ensure_ascii=False)[1:-1], line.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${'), line.replace("'", "\\'")}

def detect_generated(ctx):
    specs = ctx['mapping'].get('generated') or []
    if not specs: return [], cov('abstained', 0, 'No generated outputs declared.', 'Add generated[] with each output and the sources its generator reads.')
    found, eligible = [], 0
    for spec in specs:
        out_path = Path(ctx['root']) / spec['output']
        if not out_path.is_file():
            ctx['issues'].append('declared generated output %s is missing' % spec['output']); continue
        sources = match(ctx['files'], spec.get('sources') or [])
        if not sources:
            ctx['issues'].append('no source matched for %s' % spec['output']); continue
        eligible += 1
        out_text = read_text(ctx['root'], spec['output']) or ''
        out_text += '\n' + unescape(out_text)
        if spec.get('mtime', True):
            newer = [s for s in sources if (Path(ctx['root']) / s).stat().st_mtime > out_path.stat().st_mtime]
            if newer:
                found.append(finding(ctx, 'stale-generated', '%s is older than %d of its sources' % (spec['output'], len(newer)),
                    'File times say the output predates %s. A checkout resets times, so confirm with the generator\'s own check.' % ', '.join(newer[:3]),
                    [(newer[0], 1), (spec['output'], 1)], confidence='low', metrics={'newerSources': len(newer)}))
        if spec.get('embedded'):
            minimum = spec.get('minLength', 24)
            for src in sources:
                text = read_text(ctx['root'], src) or ''
                fm = frontmatter(text) if spec.get('skipFrontmatter') and src.endswith('.md') else 0
                lines = [(n, l.strip()) for n, l in enumerate(text.splitlines(), 1) if n > fm and len(l.strip()) >= minimum]
                missing = [(n, l) for n, l in lines if not any(f in out_text for f in embedded_forms(l))]
                if missing:
                    found.append(finding(ctx, 'stale-generated', '%s diverges from %s' % (spec['output'], src),
                        '%d of %d source lines (length >= %d) are absent from the output in raw, JSON-escaped or template-escaped form.' % (len(missing), len(lines), minimum),
                        [(src, n) for n, _ in missing[:3]], metrics={'missingLines': len(missing), 'checkedLines': len(lines)}))
    return found, cov('assessed' if eligible else 'abstained', eligible)

def detect_index_only(ctx):
    """A rule stated only in the body of an index-only surface: the model sees its one-line index entry, not the rule."""
    framed = [s for s in ctx['statements'] if s['load'] == 'full' or s['index']]
    bodies = [s for s in ctx['statements'] if s['load'] == 'index-only' and not s['index'] and s['directive']]
    if not any(s['load'] == 'index-only' for s in ctx['surfaces']) or not any(s.get('load') == 'full' for s in ctx['surfaces']):
        return [], cov('abstained', 0, 'The mapping marks no surface index-only, or none full.', 'Set load: full | index-only per surface from a trace of what was framed.')
    per_file, eligible = {}, 0
    for st in bodies:
        ents = {n for n, _ in st['mentions']}
        ws = words(st['text'], ctx['names'])
        if not ents and len(ws) < 3: continue
        eligible += 1
        def covers(f):
            fe = {n for n, _ in f['mentions']}
            return ents <= fe and len(shares(ws, words(f['text'], ctx['names']))) * 2 >= len(ws)
        if not any(covers(f) for f in framed): per_file.setdefault(st['path'], []).append(st)
    found = [finding(ctx, 'index-only-rule', '%d rule(s) live only in the body of index-only %s' % (len(sts), path),
                     'No full-load statement or index entry carries these rules (all their entities and half their topic words), so a turn that frames only the index line never sees them.',
                     [(s['path'], s['line']) for s in sts[:EVIDENCE_CAP]], [n for s in sts for n, _ in s['mentions']], metrics={'rules': len(sts)})
             for path, sts in sorted(per_file.items())]
    return found, cov('assessed', eligible)

def detect_modality(ctx):
    free = [s for s in ctx['statements'] if s['modalityFree']]
    if not any(s.get('modalityFree') for s in ctx['surfaces']) or not ctx['declared']:
        return [], cov('abstained', 0, 'No surface is marked modalityFree, or no entity vocabulary is declared.', 'Mark persona or task text that must stay modality-free with "modalityFree": true.')
    per_file = {}
    for st in free:
        if st['mentions']: per_file.setdefault(st['path'], []).append(st)
    found = [finding(ctx, 'modality-leak', '%s names %d catalog type(s) in modality-free text' % (path, len({n for s in sts for n, _ in s['mentions']})),
                     'Text that should say what the user needs names how to render it; it can override catalog selection.' + (' Evidence: first %d of %d lines.' % (EVIDENCE_CAP, len(sts)) if len(sts) > EVIDENCE_CAP else ''),
                     [(s['path'], s['line']) for s in sts[:EVIDENCE_CAP]], [n for s in sts for n, _ in s['mentions']], metrics={'statements': len(sts), 'evidenceShown': min(len(sts), EVIDENCE_CAP)})
             for path, sts in sorted(per_file.items())]
    return found, cov('assessed', len(free))

def detect_generic_oracle(ctx):
    oracles = [s for s in ctx['statements'] if s['kind'] == 'oracle']
    if not oracles or not ctx['declared']:
        return [], cov('abstained', 0, 'No oracle surface, or no entity vocabulary.', 'Declare scenario and eval files as kind "oracle".')
    family = {n: [m for m in ctx['declared'] if m != n and m.endswith(n)] for n in ctx['declared'] if len(n) >= 3}
    found, seen, eligible = [], set(), 0
    for st in oracles:
        for m in (ctx['vocab'].finditer(st['text'])):
            name = m.group(); eligible += 1
            if len(family.get(name, [])) >= 2 and (st['path'], name) not in seen:
                seen.add((st['path'], name))
                found.append(finding(ctx, 'generic-oracle', '%s expects %s, which %d more specific types also satisfy' % (st['path'], name, len(family[name])),
                    'An oracle on a base type passes on any of %s; check that it pins the intended one.' % ', '.join(family[name]),
                    [(st['path'], st['line'])], [name]))
    return found, cov('assessed', eligible)

DETECTORS = {
    'cross-surface-conflict': detect_conflict,
    'undefined-reference': detect_undefined,
    'schema-mismatch': detect_schema,
    'stale-generated': detect_generated,
    'index-only-rule': detect_index_only,
    'modality-leak': detect_modality,
    'generic-oracle': detect_generic_oracle,
}

# ---------- scan ----------

def scan(root, mapping=None, mapping_path=None):
    root = str(Path(root).resolve())
    if mapping is not None and mapping.get('version') != 1: raise ValueError('Mapping requires version 1')
    mapping = mapping or {}
    files = walk(root, [literal_prefix(g) for g in mapping_globs(mapping)] if mapping else ('',))
    surfaces = inventory(root, mapping or None, files)
    declared, vocab = load_vocab(root, mapping, files)
    id_re = re.compile(mapping.get('ids') or IDS)
    texts, all_statements, issues, index = {}, [], [], {'entities': {}, 'ids': {}}
    for s in surfaces:
        text = read_text(root, s['path'])
        if text is None:
            issues.append('%s skipped (binary, unreadable or over %d bytes)' % (s['path'], MAX_BYTES)); continue
        texts[s['path']] = Lines(text)
        s['lines'] = text.count('\n') + 1; s['sha256'] = hashlib.sha256(text.encode()).hexdigest()
        lines = s['statementLines'] = []
        for st in statements(s['path'], text, s, vocab):
            lines.append(st['line'])
            scope = s.get('scope') or []
            st.update(surface=s['id'], kind=s.get('kind'), load=s.get('load', 'unknown'), authority=bool(s.get('authority')), modalityFree=bool(s.get('modalityFree')),
                      scope=[scope] if isinstance(scope, str) else scope)
            all_statements.append(st)
            for name, _ in st['mentions']: index['entities'].setdefault(name, []).append([st['path'], st['line']])
            for m in id_re.finditer(st['text']): index['ids'].setdefault(m.group(), []).append([st['path'], st['line']])
    for s in surfaces:
        if 'statementLines' not in s: continue
        if s['path'].endswith('.md'):
            # Frontmatter (a skill's description, its routing text) reaches the model even when it is not the declared index line.
            body = texts[s['path']].text.splitlines()[:frontmatter(texts[s['path']].text)]
            s['statementLines'] += [n for n, line in enumerate(body, 1) if line.strip() not in ('', '---')]
        s['statementLines'] = sorted(set(s['statementLines']))
    # Only a mapping with producer guidance (prompt, persona, skill or guide files found) owes repair and tool surfaces;
    # a catalog-only or corpus-only audit does not. "noSurface": {"repair": "why", "tool": "why"} records a deliberate absence.
    kinds, absent = {s.get('kind') for s in surfaces}, (mapping or {}).get('noSurface') or {}
    if mapping and kinds & {'prompt', 'persona', 'skill', 'guide'}:
        if not kinds & {'check', 'repair'} and not absent.get('repair'):
            issues.append('mapping declares no repair surface (kind "check" or "repair" with a matched file): the producer\'s validator and repair text reach the model; declare them, or set noSurface.repair to the reason there are none')
        if 'tool' not in kinds and not absent.get('tool'):
            issues.append('mapping declares no tool surface (kind "tool" with a matched file): tool names, descriptions and input schemas reach the model; declare them, or set noSurface.tool to the reason there are none')
    for table in index.values():
        for k in table: table[k] = [list(x) for x in dict.fromkeys(tuple(x) for x in table[k])][:50]
    def excerpt(path, n):
        if path not in texts:
            t = read_text(root, path)
            texts[path] = Lines(t or '')
        return texts[path].excerpt(n) if n else ''
    ctx = {'root': root, 'mapping': mapping, 'files': files, 'surfaces': surfaces, 'statements': all_statements, 'declared': declared,
           'names': set(declared) or {n for n, _ in (m for st in all_statements for m in st['mentions'])}, 'vocab': vocab, 'issues': issues, 'excerpt': excerpt}
    findings, coverage = [], []
    for name, fn in DETECTORS.items():
        got, c = fn(ctx)
        findings += got; coverage.append(dict(c, detector=name, findings=len(got)))
    for i, f in enumerate(findings, 1): f['id'] = 'audit-%d' % i
    return {'auditVersion': VERSION, 'root': root,
            'mapping': {'path': mapping_path, 'sha256': hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest()} if mapping else None,
            'inventory': [{k: s.get(k) for k in ('id', 'kind', 'path', 'load', 'authority', 'modalityFree', 'lines', 'sha256', 'statementLines')} for s in surfaces],
            'vocabulary': {'declared': declared, 'pattern': None if declared else vocab.pattern, 'ids': id_re.pattern},
            'index': index, 'coverage': coverage, 'findings': findings, 'issues': issues, 'limits': LIMITS}

def summary(report, limit=25):
    out = ['contract audit %s: %d surfaces, %d findings (candidates)' % (report['root'], len(report['inventory']), len(report['findings']))]
    for c in report['coverage']:
        out.append('  %-24s %-9s eligible=%-5s findings=%s%s' % (c['detector'], c['state'], c['eligible'], c['findings'], ('  ' + c['reason']) if c['reason'] else ''))
    for f in report['findings'][:limit]:
        ev = f['evidence'][0] if f['evidence'] else {'path': '?', 'line': 0}
        out.append('%s [%s, cause %s] %s  %s:%s' % (f['id'], f['detector'], f['causeClass'], f['title'], ev['path'], ev['line']))
    if len(report['findings']) > limit: out.append('... %d more in the JSON report' % (len(report['findings']) - limit))
    for issue in report['issues']: out.append('issue: ' + issue)
    for limit in report.get('limits') or []: out.append('limit: ' + limit)
    return '\n'.join(out)

# ---------- link ----------

def strings_of(value):
    if isinstance(value, str): yield value
    elif isinstance(value, dict):
        for v in value.values(): yield from strings_of(v)
    elif isinstance(value, list):
        for v in value: yield from strings_of(v)

def finding_text(data, fid):
    pools = [data.get('findings') or [], (data.get('diagnostics') or {}).get('findings') or []]
    for f in (f for pool in pools for f in pool):
        if f.get('id') == fid: return '\n'.join(strings_of(f))
    raise ValueError('Finding %s not in the session data' % fid)

def link(report, text):
    """Contract surfaces whose entities, ids or exact phrases appear in a trace finding's text."""
    declared = report['vocabulary']['declared']
    vocab = re.compile(r'\b(?:%s)\b' % '|'.join(re.escape(n) for n in sorted(declared, key=len, reverse=True))) if declared else re.compile(report['vocabulary']['pattern'])
    ents = sorted({m.group() for m in vocab.finditer(text)} & set(report['index']['entities']))
    ids = sorted({m.group() for m in re.finditer(report['vocabulary']['ids'], text)} & set(report['index']['ids']))
    hits = {}
    for kind, names in (('entity', ents), ('id', ids)):
        for name in names:
            for path, line in report['index']['entities' if kind == 'entity' else 'ids'][name]:
                hits.setdefault(path, {'path': path, 'matched': set(), 'lines': set()})
                hits[path]['matched'].add(name); hits[path]['lines'].add(line)
    toks = re.findall(r"[\w'-]+", text)
    shingles = {' '.join(toks[i:i + 5]).lower() for i in range(len(toks) - 4)}
    for s in report['inventory']:
        path = Path(report['root']) / s['path']
        if not shingles or not path.is_file(): continue
        # Only the mapped statements (after regions, include and exclude); a report older than statementLines falls back to every line.
        keep = set(s['statementLines']) if 'statementLines' in s else None
        for n, line in enumerate((read_text(report['root'], s['path']) or '').splitlines(), 1):
            if keep is not None and n not in keep: continue
            lt = ' '.join(re.findall(r"[\w'-]+", line)).lower()
            if any(sh in lt for sh in shingles):
                hits.setdefault(s['path'], {'path': s['path'], 'matched': set(), 'lines': set()})
                hits[s['path']]['matched'].add('phrase'); hits[s['path']]['lines'].add(n)
    surface_of = {s['path']: s for s in report['inventory']}
    rows = sorted(({'path': h['path'], 'surface': surface_of.get(h['path'], {}).get('id'), 'kind': surface_of.get(h['path'], {}).get('kind'),
                    'matched': sorted(h['matched']), 'lines': sorted(h['lines'])[:20]} for h in hits.values()), key=lambda r: (-len(r['matched']), r['path']))
    related = [f['id'] for f in report['findings'] if set(f['entities']) & set(ents) or any(e['path'] in hits for e in f['evidence'])]
    return {'query': {'entities': ents, 'ids': ids}, 'surfaces': rows, 'auditFindings': related}

# ---------- CLI ----------

def main(argv=None):
    p = argparse.ArgumentParser(description='Static contract audit of guidance surfaces (catalogs, schemas, skills, prompts, checks, corpus, oracles). Read-only; findings are candidates.')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan', help='inventory surfaces and run the mechanical detectors')
    s.add_argument('--root', required=True, help='project or corpus folder (read-only)')
    s.add_argument('--mapping', help='mapping JSON (surfaces, entities, schemas, generated, topics); without it, discovery globs inventory surfaces and most detectors abstain')
    s.add_argument('--out', required=True, help='report JSON path (outside the audited root)')
    s.add_argument('--text', help='also write the text summary here')
    l = sub.add_parser('link', help='list contract surfaces a trace finding touches')
    l.add_argument('--report', required=True, help='report JSON from scan')
    g = l.add_mutually_exclusive_group(required=True)
    g.add_argument('--excerpt', help='a trace finding excerpt or title')
    g.add_argument('--finding', help='a finding id in --data')
    l.add_argument('--data', help='v2 session.json holding --finding')
    l.add_argument('--json', action='store_true', help='print JSON instead of a table')
    a = p.parse_args(argv)
    if a.cmd == 'scan':
        out = Path(a.out).resolve(); root = Path(a.root).resolve()
        if root == out.parent or root in out.parents: p.error('--out must be outside --root (the audit is read-only)')
        mapping = json.loads(Path(a.mapping).read_text()) if a.mapping else None
        report = scan(root, mapping, str(Path(a.mapping).resolve()) if a.mapping else None)
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, indent=1))
        text = summary(report)
        if a.text: Path(a.text).write_text(text + '\n')
        print(text); return 0
    report = json.loads(Path(a.report).read_text())
    if a.finding:
        if not a.data: p.error('--finding needs --data')
        text = finding_text(json.loads(Path(a.data).read_text()), a.finding)
    else: text = a.excerpt
    result = link(report, text)
    if a.json: print(json.dumps(result, indent=1)); return 0
    print('entities: %s; ids: %s' % (', '.join(result['query']['entities']) or 'none', ', '.join(result['query']['ids']) or 'none'))
    for r in result['surfaces']: print('%s (%s, %s) matched %s at lines %s' % (r['path'], r['surface'], r['kind'], ', '.join(r['matched']), ', '.join(map(str, r['lines']))))
    if result['auditFindings']: print('audit findings on these entities or files: ' + ', '.join(result['auditFindings']))
    if not result['surfaces']: print('no contract surface matched; the finding may name nothing the mapping inventories')
    return 0

if __name__ == '__main__':
    sys.exit(main())
