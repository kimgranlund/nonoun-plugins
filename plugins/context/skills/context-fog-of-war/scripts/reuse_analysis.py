#!/usr/bin/env python3
"""Reuse cited analysis on a rehydrated trace, remapping event IDs by original line."""
import argparse
import copy
import json
from pathlib import Path
from fog import validate
from connections import connect


def reuse(old, new):
    validate(old);validate(new)
    if old['session']['trace'] != new['session']['trace']:
        raise ValueError('Analysis reuse requires the same trace filename')
    by_line={e['evidence']['traceLine']:e for e in new['events']}
    mapping={e['id']:by_line[e['evidence']['traceLine']]['id'] for e in old['events'] if e['evidence']['traceLine'] in by_line}
    new_sources={s['path']:s['id'] for s in new['sources']}
    source_mapping={s['id']:new_sources[s['path']] for s in old['sources'] if s['path'] in new_sources}
    result=copy.deepcopy(new)
    for field in ('decisions','guidanceEdges','findings'):
        result[field]=copy.deepcopy(old.get(field,[]))
        for item in result[field]:
            try:
                for citation in item['evidence']:citation['eventId']=mapping[citation['eventId']]
                if field=='guidanceEdges':
                    item['from']=mapping[item['from']];item['to']=mapping[item['to']]
                    if 'sourceIds' in item:item['sourceIds']=[source_mapping[s] for s in item['sourceIds']]
            except KeyError as error:raise ValueError('Prior evidence event or source is outside the new trace') from error
    result['coverage']['warnings'].append('Decision analysis reused from a prior report with trace-line remapping and exact-citation validation. Exposures are reconstructed independently; prior annotations are not copied. Findings describe their original evidence window.')
    return validate(connect(result))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--from-report',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:
        result=reuse(json.loads(a.from_report.read_text()),json.loads(a.data.read_text()));a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    except (ValueError,OSError) as error:p.exit(1,f'Error: {error}\n')
    print(a.out)

if __name__=='__main__':main()
