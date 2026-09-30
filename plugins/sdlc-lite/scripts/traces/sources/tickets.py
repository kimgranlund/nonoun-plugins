"""Ticket reader: the ticket facts of one .sdlc root, through scripts/tickets.py.

read(root) returns one dict:
  by_slug   {slug: (id, status)} for every ticket folder tickets.load finds, closed
            .NNNN-<slug> folders included (a missing field reads as None);
  problems  tickets.problems(ts, tickets.config_numbered(root)), one line per problem;
  external  tickets.external_branches(root), the external_branch names in <root>/config;
  notes     True when <root>/notes.md exists.
"""
import os
from pathlib import Path

import tickets  # same scripts/ dir: there are no implicit relative imports, so this is not us


def read(root):
    root = Path(root)
    ts = tickets.load(root)
    return {
        'by_slug': {slug: (m.get('id'), m.get('status')) for slug, m in ts},
        'problems': tickets.problems(ts, tickets.config_numbered(root)),
        'external': tickets.external_branches(root),
        'notes': os.path.isfile(root / 'notes.md'),
    }
