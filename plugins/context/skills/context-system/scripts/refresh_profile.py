#!/usr/bin/env python3
"""Rewrite the sha256 of every artifact in a routing profile from the file it names.

Usage: refresh_profile.py --root CORPUS --profile PROFILE [--check]

A profile records the hash of each source so a changed source is noticed (validate.py reports `stale-hash`). After a
deliberate edit, run this to record the new bytes; a hash is never copied by hand. --check changes nothing and exits 1
when any hash is stale, naming the artifacts. Standard library only; runs on Python 3.9.
"""
import argparse
import json
import sys
from pathlib import Path

from validate import digest, local


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--profile', type=Path, required=True)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    try:
        profile = json.loads(args.profile.read_text(encoding='utf-8'))
        stale = []
        for artifact in profile['artifacts']:
            now = digest(local(args.root, artifact['location']).read_bytes())
            if artifact.get('sha256') != now:
                stale.append(artifact['id'])
                artifact['sha256'] = now
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'{args.profile}: cannot refresh: {exc}', file=sys.stderr)
        return 2
    if stale and not args.check:
        args.profile.write_text(json.dumps(profile, indent=2) + '\n', encoding='utf-8')
    print(f"{args.profile}: {len(stale)} stale hash(es){': ' + ', '.join(stale) if stale else ''}"
          f"{'' if args.check or not stale else '; rewritten'}")
    return 1 if stale and args.check else 0


if __name__ == '__main__':
    sys.exit(main())
