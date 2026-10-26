#!/usr/bin/env python3
"""Find project-local Codex sessions using filenames and first-record metadata only."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re


def discover(repo, sessions, session_id=None, exclude_id=None):
    repo = Path(repo).resolve()
    matches = []
    # Filename filtering avoids opening any other session when a thread ID is known.
    if session_id and not re.fullmatch(r'[A-Za-z0-9-]+', session_id):
        raise ValueError('Invalid session ID')
    for path in Path(sessions).rglob('*.jsonl'):
        if session_id and session_id not in path.name:
            continue
        try:
            with path.open() as stream:
                first = stream.readline(2 * 1024 * 1024)
            record = json.loads(first)
            meta = record.get('payload', {})
            if record.get('type') != 'session_meta' or not isinstance(meta, dict):
                continue
            identity = meta.get('id')
            if not identity or identity == exclude_id or session_id and identity != session_id:
                continue
            cwd = meta.get('cwd')
            if not isinstance(cwd, str) or not Path(cwd).is_absolute():
                continue
            location = Path(cwd).resolve()
            if location != repo and repo not in location.parents:
                continue
            stamp = meta.get('timestamp', record.get('timestamp', ''))
            moment = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
            if moment.tzinfo is None:
                moment = moment.replace(tzinfo=timezone.utc)
            matches.append({'id': identity, 'trace': str(path.resolve()), 'cwd': str(location), 'startedAt': stamp, '_time': moment.timestamp()})
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    matches.sort(key=lambda item: (-item['_time'], item['trace']))
    if not matches:
        raise ValueError('No matching local session metadata found for this project. Supply a trace path or the correct session directory.')
    if len(matches) > 1 and (session_id or matches[0]['_time'] == matches[1]['_time']):
        raise ValueError('Ambiguous session match: ' + ', '.join(item['trace'] for item in matches[:5]))
    chosen = dict(matches[0]); chosen.pop('_time')
    chosen['selection'] = 'exact session ID and project cwd' if session_id else 'latest session start in this project'
    chosen['matchingSessions'] = len(matches)
    return chosen


def discover_claude(repo, sessions, session_id=None, exclude_id=None):
    """Scan only the selected project's JSONL envelopes; never return message bodies."""
    from claude import records
    repo=Path(repo).resolve()
    if session_id and not re.fullmatch(r'[A-Za-z0-9-]+',session_id): raise ValueError('Invalid session ID')
    folder=Path(sessions)/str(repo).replace('/','-')
    matches=[]
    for path in folder.glob((session_id or '*')+'.jsonl'):
        if path.is_symlink() or path.stem==exclude_id:continue
        stamps=[];identity=None;cwds=set()
        for _,r in records(path):
            if not r:continue
            if r.get('sessionId'):identity=r['sessionId']
            if isinstance(r.get('cwd'),str):cwds.add(os.path.normpath(r['cwd']))
            if r.get('type') in ('user','assistant') and isinstance(r.get('timestamp'),str):
                try:
                    t=datetime.fromisoformat(r['timestamp'].replace('Z','+00:00'))
                    if t.tzinfo is None:t=t.replace(tzinfo=timezone.utc)
                    stamps.append((t.timestamp(),r['timestamp']))
                except ValueError:pass
        if identity!=path.stem or (session_id and identity!=session_id) or str(repo) not in cwds or not stamps:continue
        moment,stamp=max(stamps)
        matches.append(dict(id=identity,trace=str(path.resolve()),cwd=str(repo),lastMessageAt=stamp,_time=moment,host='claude'))
    matches.sort(key=lambda x:(-x['_time'],x['trace']))
    if not matches:raise ValueError('No Claude session matches this project and identity; provide --trace or --session-id.')
    if len(matches)>1 and (session_id or matches[0]['_time']==matches[1]['_time']):raise ValueError('Ambiguous Claude session timestamp; provide --session-id.')
    chosen=dict(matches[0]);chosen.pop('_time');chosen.update(matchingSessions=len(matches),selection='exact identity' if session_id else 'latest user/assistant timestamp in project')
    return chosen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--sessions', type=Path); parser.add_argument('--host',choices=['codex','claude'],default='codex'); parser.add_argument('--trace',type=Path)
    parser.add_argument('--session-id', help='Known current or explicitly requested thread ID')
    parser.add_argument('--current', action='store_true', help='Use CODEX_THREAD_ID; fail if unavailable rather than guessing')
    parser.add_argument('--exclude-id', help='Exclude the current thread when requesting the previous session')
    args = parser.parse_args()
    try:
        identity = args.session_id
        if args.trace:
            if not args.trace.is_file(): raise ValueError('Trace not found')
            print(json.dumps({'trace':str(args.trace.resolve()),'selection':'explicit trace','host':args.host},indent=2)); return
        if args.current and not identity and args.host=='claude': raise ValueError('Claude current identity unavailable; supply --trace or --session-id, never substitute latest.')
        if args.current and not identity:
            identity = os.environ.get('CODEX_THREAD_ID')
            if not identity:
                raise ValueError('Current thread ID unavailable. Pass --session-id from chat context; do not substitute a different session.')
        if not args.repo.is_dir(): raise ValueError('Repository directory does not exist')
        sessions=args.sessions or (Path.home()/'.claude/projects' if args.host=='claude' else Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'sessions')
        print(json.dumps((discover_claude if args.host=='claude' else discover)(args.repo, sessions, identity, args.exclude_id), indent=2))
    except ValueError as error:
        parser.exit(1, f'Error: {error}\n')

if __name__ == '__main__': main()
