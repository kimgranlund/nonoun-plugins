"""Ticket reader: the ticket facts of one .sdlc root, through scripts/tickets.py.

read(root) returns one dict:
  by_slug   {slug: (id, status)} for every ticket folder tickets.load finds in
            tickets.ticket_dir(root) (root itself on tickets.Fail), closed
            .NNNN-<slug> folders included (a missing field reads as None);
  problems  tickets.problems(ts, tickets.config_numbered(root)), one line per problem;
  external  tickets.external_branches(root), the external_branch names in <root>/config;
  notes     True when the notes file exists: <root>/notes.md, or <root>/notes/notes.md with
            `layout: topics` (tickets.layout_paths(root).notes; <root>/notes.md on tickets.Fail).
"""
import os
from pathlib import Path

import tickets  # same scripts/ dir: there are no implicit relative imports, so this is not us


def read(root):
    root = Path(root)
    try:
        tdir = tickets.ticket_dir(root)
    except tickets.Fail:
        tdir = root
    try:
        notes = tickets.layout_paths(root).notes
    except tickets.Fail:
        notes = root / 'notes.md'
    ts = tickets.load(tdir)
    return {
        'by_slug': {slug: (m.get('id'), m.get('status')) for slug, m in ts},
        'problems': tickets.problems(ts, tickets.config_numbered(root), areas=tickets.config_areas(root)),
        'external': tickets.external_branches(root),
        'notes': os.path.isfile(notes),
    }
