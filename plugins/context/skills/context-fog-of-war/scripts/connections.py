"""Conservative source routing candidates from recorded data, never repo contents."""
import json
import re


def excerpt(event, needle):
    text = event['evidence']['text']
    pos = text.find(needle)
    if pos < 0:
        return text[:240]
    return text[max(0, pos-80):pos+len(needle)+120]


def payload(event, output=False):
    if event.get('toolCalls'):
        return '\n'.join(t.get('output' if output else 'arguments', '') for t in event['toolCalls'])
    try:
        obj = json.loads(event['evidence']['text'])
        value = obj.get('output', '') if output else obj.get('arguments', obj.get('input', obj.get('content', '')))
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    except (ValueError, TypeError):
        return ''  # Opaque envelopes are not guessed.


def connect(data):
    """Idempotent deterministic pass; reviewed edges are preserved."""
    edges = [e for e in data.get('guidanceEdges', []) if not e['id'].startswith('auto-source-')]
    sources = {s['id']: s for s in data['sources']}
    seen = {}
    directives = {}
    emitted = set()
    for event in data['events']:
        # Only requests or assistant statements provide downstream signals.
        text = payload(event) if event['kind'] == 'call' or event['kind'] == 'message' and event['actor'] == 'assistant' else ''
        for sid, origin in list(seen.items()):
            source = sources[sid]
            path = source['path']
            # Require a whole path, never a shared basename like SKILL.md.
            match = re.search(r'(?<![\w./-])'+re.escape(path)+r'(?![\w./-])', text) if '/' in path else None
            kind, rule, prior, token = 'observed', 'path-reference', origin, path
            reason = 'A later step explicitly references this previously encountered path. This establishes a reference, not that the source caused the step.'
            if not match:
                item = next(((e,t) for e,t in directives.get(sid, []) if t in text), None)
                if not item:
                    continue
                prior, token = item
                kind, rule = 'inferred', 'literal-guidance'
                reason = 'A literal command/path in a single-source read reappears in a later step. This suggests guidance reuse, but does not establish causation or compliance.'
            # Both citations must contain the actual signal, not invented prose.
            if token not in event['evidence']['text']:
                continue
            key = (sid, event['id'])
            if key in emitted:
                continue
            emitted.add(key)
            edges.append({'id': 'auto-source-'+sid+'-'+event['id'], 'from': prior['id'], 'to': event['id'], 'kind': kind, 'sourceIds': [sid], 'explanation': 'Automatic '+rule+': '+reason+' Signal: '+token, 'evidence': [{'eventId': prior['id'], 'excerpt': excerpt(prior, token)}, {'eventId': event['id'], 'excerpt': excerpt(event, token)}]})
        for candidate in data.get('candidates', []):
            if candidate['eventId']==event['id'] and candidate['sourceId'] not in seen:seen[candidate['sourceId']]=event
        for exposure in event['exposures']:
            # Discovery can support a later reference, never a read/influence claim.
            if exposure['sourceId'] not in seen or exposure['state'] in ('read','partial'):
                seen[exposure['sourceId']] = event
        reads = {x['sourceId'] for x in event['exposures'] if x['state'] in ('read','partial')}
        if event['kind'] == 'result' and len(reads) == 1 and len(event.get('toolCalls', [])) <= 1:
            sid = next(iter(reads))
            # Multiple exposed sources make returned-text ownership ambiguous.
            if len({x['sourceId'] for x in event['exposures']}) == 1:
                for token in re.findall(r'`([^`\n]{5,160})`', payload(event, True)):
                    if '/' in token and token in event['evidence']['text']:
                        directives.setdefault(sid, []).append((event, token))
    data['guidanceEdges'] = edges
    note = 'Automatic source links detect exact path references and literal guidance reuse from unambiguous single-source reads. They do not establish causation; opaque, compound, paraphrased and unrecorded influences may remain unattributed.'
    if note not in data['coverage']['warnings']:
        data['coverage']['warnings'].append(note)
    return data


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    from fog import validate
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=validate(connect(validate(json.loads(a.data.read_text()))));a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
    print('Automatic source links:',sum(e['id'].startswith('auto-source-') for e in d['guidanceEdges']))
