#!/usr/bin/env python3
"""Read a project's sdlc run traces and report sdlc inefficiencies and bugs.

Usage:
  traces.py selftest [-k FAMILY]
  traces.py ingest <repo> [--lanes-dir DIR]... [--out DIR] [--bench-dir DIR] [--rerun-criteria]
                   [--load-series PATH]        prints the events.jsonl path
  traces.py detect [--repo REPO] [--out DIR]   runs the four detector families, prints notes and
                                               the findings.jsonl path
  traces.py clusters --max N [--repo REPO] [--out DIR]
                                               prints the top N cause clusters as JSON
  traces.py context <log> [--backend claude|codex] [--codex-home DIR]
                                               prints one JSON line: the paths one run read, or a
                                               status ('log absent', 'rollout absent'); run.sh
                                               stores it as loaded_context in runs.jsonl
detect and clusters resolve the out dir as ingest does (REPO defaults to `.`). None spawns a
claude or codex process.

Thin entry: the code lives in the traces/ package next to this file (a package dir wins over
this same-named module on sys.path, so `import traces` below loads the package).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import traces.cli  # noqa: E402  the traces/ package, not this file

if __name__ == '__main__':
    sys.exit(traces.cli.main(sys.argv[1:]))
