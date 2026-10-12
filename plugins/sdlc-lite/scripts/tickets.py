#!/usr/bin/env python3
"""Tickets are .sdlc/<slug>/handoff.md (or .sdlc/tickets/<slug>/handoff.md) files that open with front matter.
See skills/handoff-format; the tickets/ form applies when .sdlc/config has a `ticket_root: tickets` line.
This script is the only writer of the roadmap: .sdlc/roadmap.md, or .sdlc/tickets/roadmap.md with `layout: topics`.

Usage: tickets.py [--root DIR] {new <type> <slug> ["title"] [--numbered] | close <slug> [--force] [--reason TEXT] [--ack-warnings TEXT] [--dry-run] [--skip N[,N...]] [--ticket N] [--expect DIGEST] [--rewrite-refs | --keep-refs] [--numbered] | roadmap [--numbered] | check [--numbered] | archive [--dry-run] [--rewrite-refs] [--force] [--numbered] | number [--dry-run] | migrate-layout [--dry-run] [--rewrite-refs] | migrate-size [--apply] | selftest}
  --root    dir holding roadmap.md, config, notes.md, _templates and the ticket dirs (default: .sdlc in the cwd,
            like board.py). With a `ticket_root: tickets` line in <root>/config the ticket dirs live in
            <root>/tickets (the ticket root) instead; roadmap.md, config, notes.md and _templates stay at <root>
            and roadmap rows link tickets/<slug>/handoff.md. With `layout: topics` too (see config), roadmap.md
            moves to <root>/tickets/roadmap.md (rows link <slug>/handoff.md) and notes.md to <root>/notes/notes.md;
            layout_paths(root) resolves all of these, and every notes.md path below means that file
  new       copy <root>/_templates/<type>.md (else <plugin>/skills/ticket/templates/<type>.md),
            stamp the next id, today's date and the title, then regenerate the roadmap.
            Numbered mode (--numbered, or a `ticket_folders: numbered` line in <root>/config) names
            the folder NNNN-<slug> after the stamped id; the slug is given bare. On success,
            new --numbered persists the mode by adding that line to <root>/config if it is absent
  close     after /file: read the task's newest filer-L*.md, refuse while its Warnings are open
            (unless --force), file at most one Follow-ups bullet as a proposed idea ticket with
            from: <id>, append the rest to <root>/notes.md, set the ticket done, then regenerate the
            roadmap. Each bullet starts with a tag, `fix-now:`, `decide:` or `note:` (case as written,
            optional spaces after the colon); an untagged bullet counts as decide. Title, slug, duplicate
            check and ticket context use the text after the tag; the digest covers the full bullet.
            close --ticket N files only item N (1-based) as a ticket; it refuses, writing nothing, when N
            is out of range, in --skip, a fix-now: or note: item (only a decide: item can become a
            ticket), a duplicate (already tracked by T-NNNN), with --reason, and, outside --dry-run,
            without --expect. Without --ticket close files no ticket; there is no way to file two.
            Every item that is not the --ticket item, not skipped and not a duplicate is appended to
            <root>/notes.md after every refusal check: the file is created with a `# Notes` heading and
            a line saying close appends follow-ups that did not become tickets, then each close adds
            `## <id>: <title> (<YYYY-MM-DD>)` and one `- <tag>: <text>` line per item (untagged as
            `- decide: <text>`). notes.md holds no folder paths, and nothing is appended when no item
            goes there. The output names the one ticket (or none) and the count appended to notes.md.
            Numbered mode (as for new) names the follow-up folder NNNN-<slug> after its new id. On
            success, close --numbered persists the mode in <root>/config, as new --numbered does.
            In numbered mode, closing a NNNN-<slug> folder renames it to .NNNN-<slug> (after the
            handoff and follow-ups are written, before the roadmap) so ls and Finder hide it; the
            output adds `; moved to .<slug>` and each follow-up's context names the new folder.
            A plain slug folder never moves. close refuses, writing nothing, when .<slug> already
            exists, and names the dot folder (`already closed`) when only .<slug> holds the ticket.
            close --dry-run adds a `rename <slug> -> .<slug>` line.
            Before that rename, close runs `git grep --untracked -lF <rel>/<slug>` from the git toplevel
            (<rel> is the ticket root relative to it) on every close path, leaving out the ticket's own
            folder and <root>/roadmap.md. It keeps files with a literal <rel>/<slug> (ending at `/`, the end
            of a token, or punctuation, never running on into a longer folder name) or a path token that
            resolves to the folder: toplevel-relative, relative to the citing file's directory, or
            absolute. Only matched tokens are rewritten, keeping their form; no case folding, symlink
            resolution, ~ expansion or self-reference handling. A hit refuses, writing nothing, naming each file and
            suggesting --rewrite-refs or --force. close --rewrite-refs rewrites <rel>/<slug> to
            <rel>/.<slug> in each file with the rename, adding `; rewrote refs in <files>` to the
            output; --dry-run --rewrite-refs lists one `rewrite <file>` line per file before the
            `expect` line. --force closes and leaves them. --keep-refs also leaves them, without
            overriding open warnings: the ticket's ## Closed section lists the stale citations, the
            output says `left refs`, and --dry-run lists one `keep <file>` line per file. It does not
            combine with --rewrite-refs. Outside git there is no scan.
            With no filer-L*.md here, close refuses and, when another git worktree's same-relative
            <slug>/ holds one (glob only, never read), names each such folder: commit or copy it into
            this tree, then rerun close.
            A follow-up whose normalized title (lowercase, words only) or slug base (no -N suffix, no
            NNNN- prefix) equals any other ticket's, any status, is a duplicate: close skips it and
            names it in the output, writing it nowhere. Follow-ups in the same filer are not checked
            against each other. close --dry-run applies the same refusals, then lists each Follow-ups
            bullet as `<i>. <tag>: <title>` with a mark: ` [<slug>] ticket` (the --ticket item), ` note`
            (bound for notes.md), ` [<slug>] skip (--skip)` or ` [<slug>] duplicate of T-NNNN (<slug>)`,
            then one `open T-NNNN <title> [<slug>]` line per other proposed, ready or blocked
            ticket in id order, then one `open T-NNNN <title> [<slug>] (worktree <name>)` line, in id
            order, per proposed, ready or blocked ticket found only in another git worktree's
            same-relative root (<name> is that worktree's basename; a ticket whose id exists locally
            is decided by the local copy), and writes nothing (no notes.md either); --dry-run --ticket N
            needs no --expect. close --skip N[,N...] drops the named 1-based indices from that listing:
            neither ticket nor notes.md; an index out of range refuses and writes nothing. The dry run's
            last line is `expect <digest>`, a digest of the full ordered Follow-ups bullets; --skip and
            --ticket need --expect <digest> from that line and refuse without it. close --expect DIGEST refuses, writing nothing, when the current Follow-ups
            no longer match (the list changed since the dry run, so the indices may point at other
            items). Plain close without --skip or --ticket needs no token. --dry-run, --skip, --expect
            and --ticket refuse together with --reason
  archive   numbered mode only: rename every existing done or dropped NNNN-<slug> folder to
            .NNNN-<slug>, then regenerate the roadmap. Refuses, writing nothing, outside numbered
            mode, on a bad ticket, or when any target .NNNN-<slug> exists. Before any write it runs
            close's reference scan (git grep --untracked from the git toplevel, also matching paths
            relative to the citing file, with the same limits) for each folder it
            would rename and refuses, writing nothing, naming each cited <rel>/NNNN-<slug> and each
            citing file; a file inside one archived folder that cites another counts. --rewrite-refs
            rewrites each cite to <rel>/.NNNN-<slug> before the renames; --force archives and leaves
            them. Outside git there is no scan. --dry-run prints one `<name> -> .<name>` line per
            folder, then with --rewrite-refs one `rewrite <file>` line per citing file, and writes
            nothing; without either flag it refuses the same way. --numbered persists the mode
            close --reason TEXT is for a ticket whose work other tickets did: it skips the filer
            (no filer needed, warnings and follow-ups ignored), sets the ticket done, appends a
            ## Closed section with today's date and TEXT, and files no follow-ups
            close --ack-warnings TEXT closes while the filer's Warnings are open, for warnings that no
            longer apply: follow-ups, duplicates, --dry-run, --skip/--expect and the numbered rename work
            as for a plain close, and the handoff gains a ## Closed section with today's date,
            `warnings acknowledged: TEXT`, and the Warnings text quoted line by line (`> `). It refuses,
            writing nothing, with --force, with --reason, with empty TEXT, or when Warnings is None
            On every path (plain, --reason, --ack-warnings, --dry-run) close refuses, writing nothing, when
            the ticket's skips.md records lane solo, lean, fix, or full but lacks a result or a ## Skipped entry
            for a role the full chain would have run, as check does; no skips.md or no lane record is exempt
  roadmap   regenerate the roadmap (<root>/roadmap.md, or <root>/tickets/roadmap.md with `layout: topics`) in dependency order (refuses on any ticket problem, including,
            in numbered mode (as for new), the NNNN-<slug> prefix/id rule)
  check     validate every ticket; fail if roadmap.md is missing or stale, then on each router problem (see
            Router below). With `layout: topics` it also fails each entry directly under <root> other than
            AGENTS.md, CLAUDE.md, config, layout.md, board.md, tickets, work, notes, messages, evals, proposals,
            supervisor, runtime, dogfood, a _-prefixed name or a .-prefixed one (a closed-ticket .NNNN-<slug> is
            a stray: it belongs in tickets/), as `<name>: stray entry at the root`; only check runs this, so a
            loose file never blocks new or close. In the flat layout with no explicit `layout: flat` line it
            prints, last, `warning: <root> uses the flat layout; tickets.py migrate-layout moves it to topic
            folders (...)` (exit stays 0). Numbered mode (as for new)
            also fails a NNNN-<slug> folder whose id is not T-NNNN. Outside numbered mode, when every
            ticket folder has an NNNN- prefix, prints a warning (exit stays 0) that the config line is missing.
            Inside a git work tree it also prints `warning: external_branch <b> is not a local branch` (exit
            stays 0) for each registered branch with no refs/heads/<b>
            It also prints `warning: <slug>/handoff.md:<n>: closed ticket still holds <type> template
            placeholder text: '<line>'` (exit stays 0) for each done or dropped ticket whose handoff holds a
            prompt line of its type's template as a whole line (the template's default statements, a bare
            `- Label:` line and headings never count): newest id first, at most 5 lines, then one
            `<N> more closed tickets hold template placeholder text` line
            Last, it fails each done ticket whose skips.md records lane solo, lean, fix, or full (the last
            `- lane:` line under ## Lane) but has neither the result nor a ## Skipped entry (format:
            skills/handoff-format) for a missing planner, verifier step <n> or filer result (a solo ticket has
            no steps, so it needs entries for planner and filer; a full ticket needs the results); no skips.md or
            no lane record (tickets closed before the guard) is exempt
  number    convert a plain-slug root: rename each ticket folder <slug> to NNNN-<slug> after its id, rewrite
            every cite of <rel>/<slug> (as close's scan finds them, plus files inside the folder) to
            <rel>/NNNN-<slug>, persist `ticket_folders: numbered`, regenerate the roadmap. Refuses, writing
            nothing, on a bad ticket, a non T-NNNN id, or an existing target. --dry-run lists the renames
            and rewrites. Follow with archive --rewrite-refs to hide done and dropped folders
  migrate-layout  move a flat root to the topics layout: each ticket folder directly under <root> (load's rule,
            or a .NNNN-<slug> name) to tickets/<name>, each other dir not in check's allowed list and not _ or .
            prefixed to work/<name>, roadmap.md to tickets/roadmap.md and notes.md to notes/notes.md (Path.rename,
            never git mv); then add `ticket_root: tickets` and `layout: topics` to config (dropping other layout
            lines), regenerate the roadmap, routers and mailbox entries, and append check's output. Refuses, writing
            nothing, on a bad config line, outside git, on any uncommitted change (untracked files included), on a
            bad ticket or malformed router block, on a loose file at the root (not roadmap.md or notes.md), or on an
            existing target. Cites: files that cite a moved path (outside_refs per moved name, plus files under the
            moved paths holding ../) are rewritten by migrate_text so each path token resolves after the moves to
            the same file (a token inside an onboard managed block never changes; a file-relative token in a
            moved file is re-expressed from its new dir). Without --rewrite-refs a citing file refuses, named;
            with it each prints `rewrite <file>`. A file under docs/reports/ is a dated record: printed `keep
            <file> (dated record under docs/reports/)`, never rewritten. --dry-run prints the `move <src> -> <dst>`,
            rewrite, keep and `config <line>` lines and writes nothing. With nothing to move and both config lines
            present it prints `nothing to migrate` and check's output. Afterwards run onboard.py setup to refresh
            the root AGENTS.md block
  migrate-size  rewrite each alias `size:` (SIZE_ALIASES, read as L1 to L4) to its level in the front matter of
            every ticket handoff.md (closed .NNNN-<slug> folders too) and every <root>/_templates/*.md, printing
            `<path>: size <old> -> <new>` per file. A dry run unless --apply; --apply writes and regenerates the
            roadmap. A ticket's size is its level: L1 small, L2 medium, L3 large, L4 extra large, L5 reserved
  config   <root>/config may also hold `external_branch: <branch>` lines, one branch per line (blank lines, #
            comment lines and a trailing # comment are ignored; a repeated name counts once), each registering a
            branch an outside agent owns that no worktree here checks out. new and close read the ticket folders
            committed at <branch>:<rel> from git objects (no checkout) and stamp every new ticket and follow-up
            id above their max; check warns for a registered name with no local branch. Outside git the lines
            change nothing.
            `hash_bound: <glob> [<glob>...]` lines (same comment rules) declare the hash-bound and generated paths of
            the fanout merge class (hash_bound_globs); tickets.py itself never acts on them.
            A `ticket_root: tickets` line (same comment rules) puts the ticket dirs in <root>/tickets for new, close,
            roadmap, check, archive and number; `tickets` is the only supported value, and any other value refuses
            every command, writing nothing. Without the line the ticket dirs are <root>/<slug> as before. With it,
            a ticket folder (handoff.md with front matter, under load's folder rule) left directly under <root> is
            a stray, `outside the ticket root`: check fails it and new, close, roadmap, archive and number refuse,
            writing nothing, until it moves to tickets/<slug>. A plain task (no front matter) is never a stray. The
            reference scan in close, archive and number then names <rel>/<slug> with <rel> the ticket root
            (.sdlc/tickets) and leaves out the roadmap file. Ids across worktrees and external branches, the
            no-filer hint and close --dry-run's worktree lines read each other tree's or branch's ticket root,
            resolved by its own config
            A `layout: <flat|topics>` line (same comment rules) picks the folder layout, resolved by
            layout_paths(root) into (layout, tickets, roadmap, notes, work). No line or `layout: flat` keeps the
            paths above. `layout: topics` needs `ticket_root: tickets` too (other trees, branches, board.py and
            traces read only ticket_root) and gives tickets <root>/tickets, roadmap <root>/tickets/roadmap.md,
            notes <root>/notes/notes.md, and work <root>/work for task folders with no ticket. Any other value,
            both values, or topics without ticket_root: tickets refuses every command, writing nothing. Other
            trees' ticket roots never read this line
  selftest  build fixtures in a temp dir and prove every check failure fires

Ids across git worktrees: new and close stamp each id above the max across the same-relative ticket root
(<worktree>/<root relative to its toplevel>) in every `git worktree list` tree, so parallel worktrees never
reuse an id. Ids committed on a registered external_branch are read from git objects and counted too. Each
other worktree's and each registered branch's ticket root is resolved by that tree's or branch's own config
(`ticket_root: tickets` there means its <root>/tickets; an unsupported value there falls back to its <root>).
Outside git, or when git fails, the local root decides alone. A worktree with no such dir yet is skipped, and
malformed tickets in another tree or branch are ignored there. An unregistered branch not checked out in any
worktree stays unseen; check catches a clash after merge (duplicate id, naming both folders).

Router: write_roadmap also keeps a managed router block current, so an agent reads one short file and opens only
the tickets in the stage it needs. The managed files are <root>/AGENTS.md (the router: stage counts, one line
per proposed, ready, claimed, paused or blocked ticket as `  - <id> <title> (<folder>)`, plus `, claimed by <value>`
when the ticket's front matter has a non-empty `claimed_by:` and then `, paused: <reason>` for a paused ticket's
`paused_reason:`, the ticket fields, and the create, claim and close procedures) and
<root>/CLAUDE.md, and with `ticket_root: tickets` also <root>/tickets/AGENTS.md (the same procedures) and
<root>/tickets/CLAUDE.md, and with `layout: topics` also work/AGENTS.md, work/CLAUDE.md, notes/AGENTS.md and
notes/CLAUDE.md (short entry blocks); the topics router opens with a topic-folder paragraph and both procedures
send notes to `<R>/notes/notes.md`. Every command that regenerates the roadmap (new, close, roadmap, archive, number)
regenerates them. The block uses onboard.py's managed-block format and helpers (wrap_block, find_block,
digest, has_import, _replace_region, _append_region; same scripts/ dir, standard library only): a missing
AGENTS.md is created as the block alone, a file with no block gets it appended, a file with a block gets it
replaced, and every byte outside the markers is kept. A CLAUDE.md that lacks an `@AGENTS.md` import line gets
one appended (a missing one is created as that line). Paths in the text are relative to the git toplevel
(else root's parent) in posix form, so the text is the same on every machine. new, close (--dry-run
included), roadmap, archive and number refuse, writing nothing, while a managed AGENTS.md holds a malformed
block. new and close follow-ups stamp `router: <ticket dir>/AGENTS.md  # how to claim and close this ticket` as
the last front matter line. `router` is never validated. Status is set by hand: `status: claimed` needs a
non-empty `claimed_by:` and `status: paused` a non-empty `paused_reason:`; on any other status neither field is
validated, so a `claimed_by:` on a ready ticket stays valid. An optional `area:` is the ticket's domain and must
be one of the `areas: a, b, c` names in <root>/config (config_areas); it is never a lane or branch name. When some
ticket has an area, the roadmap gains an Area column after Type; a paused Status cell reads
`<glyph> paused (<paused_reason>)`. No migration: an absent `area` is valid and every existing status stays valid.
check fails, after the ticket problems and the stale-roadmap check, with one line per cause:
`<label>: router block missing`, `router block stale`, `router block malformed: <reason>`, or
`no @AGENTS.md import`, where <label> is AGENTS.md, CLAUDE.md, tickets/AGENTS.md, tickets/CLAUDE.md, or under
topics work/ or notes/ AGENTS.md or CLAUDE.md. With
no ticket and no <root>/AGENTS.md, check passes.
write_roadmap also writes the mailbox entry files under <root>/messages/ through messages.write_entries, creating
the folder: .gitignore, AGENTS.md, CLAUDE.md, and AGENTS.md and CLAUDE.md in each of new/, read/, done/. The
router's Mailbox line links messages/AGENTS.md. check does not validate the entry files: they are git-ignored
local state that a fresh clone lacks.

Depends entries take three forms. T-NNNN names a ticket that must exist. file:<path> names a file relative
to the git toplevel of the ticket root (else the root's parent dir); the path is non-empty, not absolute, and
has no .. segment. It never orders tickets and a missing file is not an error. cap:<name> (name matches
[A-Za-z0-9][A-Za-z0-9._-]*) names a capability that some ticket, any status, lists in its optional
`provides: [<name>, ...]` front matter; it orders the ticket after every provider, so check also finds cycles
through capabilities. Any other entry fails check. In the roadmap a file: entry reads `(unmet)` until the file
exists and a cap: entry until a done ticket provides it. The roadmap goes stale when a named file appears or a
provider closes, so rerun `roadmap` then.

A handoff with no front matter is not a ticket and is skipped. Dirs starting with _ or . are skipped,
except a closed-ticket folder .NNNN-<slug>: it is a ticket in every mode and command (ids, depends, from,
roadmap), and check fails it unless its status is done or dropped (rename it without the dot to reopen).
Build progress is not tracked here: /board derives it from each task's step artifacts.
"""
import argparse
import collections
import datetime
import hashlib
import heapq
import os
import pathlib
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

import onboard  # same scripts/ dir: the managed-block format and helpers the router block reuses
import order as run_order

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ('id', 'title', 'type', 'status', 'size', 'priority', 'depends', 'created')
ENUMS = {
    'type': ('feature', 'bug', 'chore', 'spike', 'idea'),
    'status': ('proposed', 'ready', 'claimed', 'paused', 'blocked', 'done', 'dropped'),
    'size': ('L1', 'L2', 'L3', 'L4', 'L5'),
    'priority': ('P1', 'P2', 'P3'),
}
# A ticket's size is its level, L1 (small) to L4 (extra large); L5 is reserved. The 0.21.x values are read
# aliases (deprecated): parse() maps them to the level, and every tickets.py write of a front matter
# (new, close, migrate-size) stores the level. ALIAS_OK: the retired-vocabulary guard in check.py allows this line.
SIZE_ALIASES = {'S': 'L1', 'M': 'L2', 'L': 'L3', 'XL': 'L4'}  # ALIAS_OK
SIZE_COMMENT = '# L1 | L2 | L3 | L4 (L5 reserved)'
GLYPH = {'proposed': '⏳', 'ready': '🔵', 'claimed': '🟡', 'paused': '⏸️', 'blocked': '🔴', 'done': '🟢',
         'dropped': '⚪'}
ID_RE = re.compile(r'T-\d{4}')
CAP_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')  # a capability name, fullmatch (cap:<name>, provides)
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
SLUG_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
PREFIX_RE = re.compile(r'\d{4}-')
DOT_RE = re.compile(r'\.\d{4}-[a-z0-9]+(-[a-z0-9]+)*')  # a closed-ticket folder: .NNNN-<slug>, fullmatch
CONFIG_RE = re.compile(r'\s*ticket_folders\s*:\s*numbered\s*(?:#.*)?')
EXTERNAL_RE = re.compile(r'\s*external_branch\s*:\s*(\S+)\s*(?:#.*)?')
HASH_BOUND_RE = re.compile(r'\s*hash_bound\s*:\s*([^#]*?)\s*(?:#.*)?')  # T-0374: one or more globs per line
TICKET_ROOT_RE = re.compile(r'\s*ticket_root\s*:\s*(\S+)\s*(?:#.*)?')
LAYOUT_RE = re.compile(r'\s*layout\s*:\s*(\S+)\s*(?:#.*)?')
AREAS_RE = re.compile(r'\s*areas\s*:\s*([^#]*?)\s*(?:#.*)?')

HEADER = """# Roadmap

GENERATED by `tickets.py roadmap` from ticket front matter. Do not edit by hand: change the ticket's `handoff.md` front matter and regenerate.
New ticket: `/ticket new <feature|bug|chore|spike|idea> <slug> "title"`. Build progress per ticket: `/board`.
"""


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


# ---------- parsing ----------

def parse_value(v):
    v = v.strip()
    if v.startswith('"'):
        m = re.match(r'"([^"]*)"\s*(?:#.*)?$', v) or re.match(r'"(.*)"$', v)
        return m.group(1) if m else v
    v = re.sub(r'(^|\s+)#.*$', '', v).strip()
    if v.startswith('[') and v.endswith(']'):
        return [x.strip().strip('"') for x in v[1:-1].split(',') if x.strip()]
    return v


def parse(text):
    """Front matter dict, or None when the text has no front matter block."""
    text = text.replace('\r\n', '\n')
    m = re.match(r'---\n(.*?)^---[ \t]*$', text, re.S | re.M)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith('#') or ':' not in line:
            continue
        k, v = line.split(':', 1)
        meta[k.strip()] = parse_value(v)
    if isinstance(meta.get('size'), str):
        meta['size'] = size_level(meta['size'])
    return meta


def size_level(v):
    """The level for a size value: an alias (SIZE_ALIASES) maps to L1 to L4, anything else is returned as is."""
    return SIZE_ALIASES.get(v, v)


def normalize_size_text(text):
    """(text, old, new): the front matter's `size:` line rewritten from an alias to its level, with the
    template's alias comment replaced; old and new are None when nothing changed. Only the front matter block
    is touched."""
    fm = re.match(r'---\r?\n.*?^---[ \t]*\r?$', text, re.S | re.M)
    if not fm:
        return text, None, None
    head = fm.group(0)
    m = re.search(r'^([ \t]*size[ \t]*:[ \t]*)([^\s#]+)([ \t]*)(#[^\r\n]*)?', head, re.M)
    if not m or m.group(2) not in SIZE_ALIASES:
        return text, None, None
    old, new = m.group(2), SIZE_ALIASES[m.group(2)]
    comment = m.group(4)
    if comment is not None and re.fullmatch(r'#\s*S\s*\|\s*M\s*\|\s*L\s*\|\s*XL\s*', comment.strip()):  # ALIAS_OK
        comment = SIZE_COMMENT
    if comment is None:
        line = m.group(1) + new + m.group(3)
    else:  # keep the comment's column where the shorter alias left room
        line = m.group(1) + new + ' ' * max(1, len(old) + len(m.group(3)) - len(new)) + comment
    head = head[:m.start()] + line + head[m.end():]
    return head + text[fm.end():], old, new


def load(root):
    """[(slug, meta)] for every <root>/<dir>/handoff.md with front matter, sorted by slug.
    Dirs starting with _ or . are skipped, except a closed-ticket folder .NNNN-<slug> (DOT_RE)."""
    if not root.is_dir():
        return []
    out = []
    for d in sorted(p for p in root.iterdir()
                    if p.is_dir() and (not p.name.startswith(('_', '.')) or DOT_RE.fullmatch(p.name))):
        h = d / 'handoff.md'
        if h.is_file():
            meta = parse(h.read_text(encoding='utf-8'))
            if meta is not None:
                out.append((d.name, meta))
    return out


def config_numbered(root):
    """True when <root>/config has a `ticket_folders: numbered` line. A missing file or any other
    content means plain slug folders; blank and # comment lines are ignored."""
    path = root / 'config'
    if not path.is_file():
        return False
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if CONFIG_RE.fullmatch(line):
            return True
    return False


def config_areas(root):
    """The allowed ticket areas: the comma-separated names on every `areas: a, b, c` line of <root>/config, in
    order, each stripped, empty names dropped. A missing file or no such line gives []. Blank and # comment lines
    are ignored. An area is a ticket's domain (the `area:` front matter value), never a lane or branch name:
    lanes stay `lane/<ticket>-<slug>`."""
    path = root / 'config'
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        mo = AREAS_RE.fullmatch(line)
        if mo:
            out += [a.strip() for a in mo.group(1).split(',') if a.strip() and a.strip() not in out]
    return out


def ensure_numbered_config(root):
    """Persist numbered mode: append `ticket_folders: numbered` to <root>/config (created if missing)
    unless config_numbered(root) already holds. Adds a newline first if the file lacks a trailing one."""
    if config_numbered(root):
        return
    path = root / 'config'
    old = path.read_text(encoding='utf-8') if path.is_file() else ''
    if old and not old.endswith('\n'):
        old += '\n'
    path.write_text(old + 'ticket_folders: numbered\n', encoding='utf-8')


def ensure_topics_config(root, write=True):
    """Persist the topics layout in <root>/config (created if missing): append `ticket_root: tickets` when no
    ticket_root line exists, and unless every layout line already says topics, drop every `layout:` line and append
    `layout: topics`. Every other line stays byte-identical. Returns the lines added; write=False only computes
    them (for --dry-run)."""
    path = root / 'config'
    old = path.read_text(encoding='utf-8') if path.is_file() else ''
    lines = old.splitlines(keepends=True)

    def live(line, rx):
        return line.strip() and not line.lstrip().startswith('#') and rx.fullmatch(line.rstrip('\r\n'))

    added = []
    if not any(live(x, TICKET_ROOT_RE) for x in lines):
        added.append('ticket_root: tickets')
    found = layout_lines(root)
    if not found or any(v != 'topics' for v, _ in found):
        lines = [x for x in lines if not live(x, LAYOUT_RE)]
        added.append('layout: topics')
    if added and write:
        new = ''.join(lines)
        if new and not new.endswith('\n'):
            new += '\n'
        path.write_text(new + ''.join(x + '\n' for x in added), encoding='utf-8')
    return added


def external_branches(root):
    """The branch names registered by `external_branch: <branch>` lines in <root>/config, in file order,
    deduplicated; blank and # comment lines are ignored, as in config_numbered. [] when the file is missing."""
    path = root / 'config'
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = EXTERNAL_RE.fullmatch(line)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def hash_bound_globs(root):
    """The hash-bound and generated paths a repo declares for the merge class (T-0374): the globs on every
    `hash_bound: <glob> [<glob>...]` line in <root>/config, in file order, deduplicated; blank and # comment lines and a
    trailing # comment are ignored, as for external_branch. [] when the file or the line is missing. Each glob is a git
    :(glob) pathspec relative to the repository root (docs/references/sdlc-internals.md, fanout merge class)."""
    path = root / 'config'
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = HASH_BOUND_RE.fullmatch(line)
        for g in (m.group(1).split() if m else []):
            if g not in out:
                out.append(g)
    return out


def ticket_dir(root):
    """The dir holding the ticket folders: <root>/tickets when <root>/config has a `ticket_root: tickets` line,
    else root. Blank and # comment lines are ignored and a missing file is no line, as in config_numbered. Any
    other ticket_root value raises Fail before anything is read or written: the only supported value is
    `tickets`. config and _templates stay at <root> either way; roadmap.md and notes.md stay at <root> in the flat
    layout and move under the topics layout (see layout_paths, which calls this, never the reverse). This function
    never reads the `layout` line, so a bad one in another tree never breaks that tree's resolution here."""
    path = root / 'config'
    if not path.is_file():
        return root
    values = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = TICKET_ROOT_RE.fullmatch(line)
        if m:
            values.append(m.group(1))
    if not values:
        return root
    for v in values:
        if v != 'tickets':
            raise Fail(f'{path}: ticket_root: {v} is not supported; the only supported value is '
                       f'ticket_root: tickets; nothing written')
    return root / 'tickets'


LayoutPaths = collections.namedtuple('LayoutPaths', 'layout tickets roadmap notes work')


def layout_lines(root):
    """[(value, line)] for each `layout: <value>` line in <root>/config, in file order (line stripped). Blank
    and # comment lines are ignored and a missing file is no line, as in ticket_dir."""
    path = root / 'config'
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = LAYOUT_RE.fullmatch(line)
        if m:
            out.append((m.group(1), line.strip()))
    return out


def layout_paths(root):
    """LayoutPaths(layout, tickets, roadmap, notes, work) from <root>/config's `layout:` line. No line, or only
    `layout: flat` lines: ('flat', ticket_dir(root), <root>/roadmap.md, <root>/notes.md, <root>). `layout: topics`:
    ('topics', <root>/tickets, <root>/tickets/roadmap.md, <root>/notes/notes.md, <root>/work), and it needs a
    `ticket_root: tickets` line too, since other worktrees, external branches, board.py and traces resolve the
    ticket root from ticket_root alone. Any other value, both values in one file, or topics without
    ticket_root: tickets raises Fail before anything is read or written, as ticket_dir does."""
    path = root / 'config'
    found = layout_lines(root)
    for v, line in found:
        if v not in ('flat', 'topics'):
            raise Fail(f'{path}: {line} is not supported; the supported values are layout: flat and layout: topics; '
                       f'nothing written')
    for v, line in found:
        if v != found[0][0]:
            raise Fail(f'{path}: {line} conflicts with {found[0][1]}; keep one layout value; nothing written')
    tdir = ticket_dir(root)
    if found and found[0][0] == 'topics':
        if tdir == root:
            raise Fail(f'{path}: layout: topics needs a ticket_root: tickets line too (other worktrees, branches, '
                       f'board.py and traces find the ticket root from ticket_root alone); add ticket_root: tickets; '
                       f'nothing written')
        return LayoutPaths('topics', tdir, tdir / 'roadmap.md', root / 'notes' / 'notes.md', root / 'work')
    return LayoutPaths('flat', tdir, root / 'roadmap.md', root / 'notes.md', root)


def strays(root):
    """One problem line per ticket folder left directly under <root> while <root>/config sets
    `ticket_root: tickets`: a dir other than tickets that load()'s folder rule takes (not _ or . prefixed, except
    a closed-ticket .NNNN-<slug>) whose handoff.md has front matter. A plain task (no front matter) is never a
    stray. [] when the ticket root is <root> itself."""
    if ticket_dir(root) == root:
        return []
    return [f'{name}: ticket folder outside the ticket root; {root}/config sets ticket_root: tickets, so move it '
            f'to tickets/{name}' for name, _ in load(root) if name != 'tickets']


ROOT_ALLOWED = ('AGENTS.md', 'CLAUDE.md', 'config', 'layout.md', 'board.md', 'tickets', 'work', 'notes', 'messages',
                'evals', 'proposals', 'supervisor', 'runtime', 'dogfood')


def root_strays(root):
    """For check only, never roadmap, so a loose file never blocks new or close. Under `layout: topics`, one line per
    entry directly under <root> that is not allowed: ROOT_ALLOWED, any _-prefixed name, and any .-prefixed name
    except a closed-ticket .NNNN-<slug> (it belongs in tickets/). Names strays(root) already reports are skipped.
    [] under the flat layout or when <root> does not exist."""
    if layout_paths(root).layout != 'topics' or not root.is_dir():
        return []
    reported = {name for name, _ in load(root)}
    return [f'{p.name}: stray entry at the root; {root}/config sets layout: topics, so move it into tickets/, work/, '
            f'or notes/' for p in sorted(root.iterdir())
            if p.name not in ROOT_ALLOWED and p.name not in reported and not p.name.startswith('_')
            and not (p.name.startswith('.') and not DOT_RE.fullmatch(p.name))]


GIT_ENV_DROP = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')


def worktree_roots(root):
    """The ticket roots of worktree_pairs(root), in the same order."""
    return [r for _, r in worktree_pairs(root)]


def worktree_pairs(root):
    """(worktree dir, ticket root) pairs. The same-relative ticket root in every other git worktree of root's repo: <worktree>/<rel>, where rel is
    root relative to its worktree's toplevel. Only existing dirs; the current root is left out. [] when git is
    missing, a git call fails, or root is outside the toplevel (not in git: the local root decides alone).
    GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE are dropped so an outer git context cannot redirect the lookup."""
    try:
        here = root.resolve()
        anchor = here
        while not anchor.is_dir() and anchor != anchor.parent:
            anchor = anchor.parent
        env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

        def git(*args):
            p = subprocess.run(['git', '-C', str(anchor), *args], env=env, capture_output=True, text=True)
            if p.returncode:
                raise ValueError(p.stderr.strip())
            return p.stdout

        top = pathlib.Path(git('rev-parse', '--show-toplevel').strip())
        rel = here.relative_to(top.resolve())
        out = []
        for line in git('worktree', 'list', '--porcelain').splitlines():
            if not line.startswith('worktree '):
                continue
            other = (pathlib.Path(line[len('worktree '):]) / rel).resolve()
            if other != here and other.is_dir():
                out.append((pathlib.Path(line[len('worktree '):]), other))
        return out
    except (OSError, ValueError):
        return []


def other_ticket_dirs(root):
    """(worktree dir, ticket dir) pairs in worktree_pairs(root) order: each other tree's ticket dir is
    ticket_dir(<that tree's root>), resolved by that tree's own <root>/config. When that config cannot be read or
    holds an unsupported ticket_root value, the pair keeps that tree's root: another tree's problems never fail
    this one. Callers pass the .sdlc root, never a ticket dir."""
    out = []
    for wdir, r in worktree_pairs(root):
        try:
            out.append((wdir, ticket_dir(r)))
        except (Fail, OSError, UnicodeDecodeError):
            out.append((wdir, r))
    return out


def branch_tickets(root, branch):
    """[(slug, meta)] for the ticket folders committed at <branch>:<rel>, read from git objects with no checkout
    (rel is root relative to its worktree's toplevel, as in worktree_pairs). The branch's own config decides the
    ticket root: when the <branch>:<rel>/config blob (read with `git cat-file -p`; a missing blob is no line)
    holds `ticket_root: tickets` under ticket_dir's rule, the folders are listed at <branch>:<rel>/tickets;
    without the line, or with an unsupported value, at <branch>:<rel>. Slugs stay folder names. Folders follow load()'s rule (names
    starting with _ or . are skipped, except a closed-ticket folder .NNNN-<slug>); each <dir>/handoff.md blob is
    read through one `git cat-file --batch` process, and only those with front matter count, sorted by dir name.
    [] when git is missing, a git call fails, the branch does not exist, or root is outside the toplevel. A
    handoff that is missing, not a blob, undecodable or malformed is skipped, never raised. GIT_DIR,
    GIT_WORK_TREE and GIT_INDEX_FILE are dropped so an outer git context cannot redirect the lookup."""
    try:
        if not branch or branch.startswith('-'):
            return []
        here = root.resolve()
        anchor = here
        while not anchor.is_dir() and anchor != anchor.parent:
            anchor = anchor.parent
        env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

        def git(cwd, *args, data=None):
            p = subprocess.run(['git', '-C', str(cwd), *args], env=env, input=data, capture_output=True)
            if p.returncode:
                raise ValueError(p.stderr.decode('utf-8', 'replace').strip())
            return p.stdout

        top = pathlib.Path(git(anchor, 'rev-parse', '--show-toplevel').decode('utf-8').strip()).resolve()
        rel = here.relative_to(top).as_posix()
        try:
            cfg = git(top, 'cat-file', '-p', f'{branch}:config' if rel == '.' else f'{branch}:{rel}/config')
        except ValueError:
            cfg = b''  # no config blob on the branch: no line
        values = []
        for line in cfg.decode('utf-8', 'replace').splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            m = TICKET_ROOT_RE.fullmatch(line)
            if m:
                values.append(m.group(1))
        if values and all(v == 'tickets' for v in values):
            rel = 'tickets' if rel == '.' else f'{rel}/tickets'
        prefix = f'{branch}:' if rel == '.' else f'{branch}:{rel}/'
        dirs = []
        for entry in git(top, 'ls-tree', '-z', branch if rel == '.' else f'{branch}:{rel}').split(b'\0'):
            head, sep, raw = entry.partition(b'\t')
            if not sep or head.split(b' ')[1:2] != [b'tree']:
                continue
            try:
                name = raw.decode('utf-8')
            except UnicodeDecodeError:
                continue
            if '\n' not in name and (not name.startswith(('_', '.')) or DOT_RE.fullmatch(name)):
                dirs.append(name)
        if not dirs:
            return []
        data = git(top, 'cat-file', '--batch',
                   data=''.join(f'{prefix}{d}/handoff.md\n' for d in dirs).encode('utf-8'))
        out, pos = [], 0
        for d in dirs:
            end = data.index(b'\n', pos)
            parts = data[pos:end].split(b' ')
            pos = end + 1
            if len(parts) != 3 or not parts[2].isdigit():
                continue  # `<name> missing` (or ambiguous): no content follows
            size = int(parts[2])
            blob, pos = data[pos:pos + size], pos + size + 1
            if parts[1] != b'blob':
                continue
            try:
                meta = parse(blob.decode('utf-8'))
            except (ValueError, TypeError):
                continue
            if meta is not None:
                out.append((d, meta))
        return sorted(out, key=lambda t: t[0])
    except (OSError, ValueError, IndexError):
        return []


def unknown_branches(root, names):
    """The names with no local branch (`git rev-parse -q --verify refs/heads/<b>^{commit}` fails), in order.
    [] when root is not inside a git work tree or git is missing: outside git nothing is checked."""
    if not names:
        return []
    try:
        anchor = root.resolve()
        while not anchor.is_dir() and anchor != anchor.parent:
            anchor = anchor.parent
        env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

        def git(*args):
            return subprocess.run(['git', '-C', str(anchor), *args], env=env, capture_output=True, text=True)

        p = git('rev-parse', '--is-inside-work-tree')
        if p.returncode or p.stdout.strip() != 'true':
            return []
        return [b for b in names if git('rev-parse', '-q', '--verify', f'refs/heads/{b}^{{commit}}').returncode]
    except OSError:
        return []


def literal_re(old):
    """The literal folder path old, matched only where it starts a path token (start of text or after a TOKEN_RE
    delimiter: whitespace, a quote, a backtick, a paren, or an angle or square bracket), so a path into another
    tree (other/<rel>/<slug>, /elsewhere/<rel>/<slug>, ../other/<rel>/<slug>) is not the literal, and only when
    no folder-name character follows it, so <rel>/<slug> ends at `/`, the end of a token, or punctuation and
    never runs on into a longer folder name. A URL or prefixed form (https://host/<rel>/<slug>,
    key=<rel>/<slug>) is therefore not the literal either."""
    return re.compile(r'(?<![^\s\'"`()<>\[\]])' + re.escape(old) + r'(?![A-Za-z0-9_-])')


def outside_refs(root, slug, own=False, roadmap=None):
    """(toplevel, old, new, files) for a numbered close of root/slug. old is <rel>/<slug> and new <rel>/.<slug>,
    where rel is root relative to its git toplevel. One `git grep --untracked -I -lF <slug>` from the toplevel
    finds candidate files; each is kept only when it holds a reference: the literal old (the original
    rule), counted only where it starts a path token (start of text or after a TOKEN_RE delimiter, so
    other/.sdlc/0001-a and /elsewhere/.sdlc/0001-a are not it) and ending at `/`, the end of a token, or
    punctuation, never running on into a longer folder name (.sdlc/0001-a never matches inside .sdlc/0001-ab;
    literal_re), or a path token that ref_tokens resolves to the folder (relative to the citing file, toplevel-relative
    or absolute, for example ../<slug>/filer-L1.md or ./<slug>/handoff.md). A bare <slug> word and a path that
    resolves elsewhere are not references. files are the toplevel-relative paths (sorted), leaving out every
    file under the ticket's own folder and <root>/roadmap.md (the folder moves with the ticket; close
    regenerates the roadmap). (None, '', '', []) when git is missing, a git call fails, or root is outside the
    toplevel, the same rule as worktree_pairs. GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE are dropped so an outer
    git context cannot redirect the scan. own=True (number) keeps files under the ticket's own folder too, since
    a literal <rel>/<slug> cite there goes stale when the folder is renamed. roadmap is the roadmap path to leave
    out, default <root>/roadmap.md; with `ticket_root: tickets` callers pass the ticket dir as root and
    roadmap=<root>/roadmap.md, whose tickets/<slug>/handoff.md link would otherwise count as a cite."""
    try:
        here = root.resolve()
        anchor = here
        while not anchor.is_dir() and anchor != anchor.parent:
            anchor = anchor.parent
        env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
        p = subprocess.run(['git', '-C', str(anchor), 'rev-parse', '--show-toplevel'], env=env,
                           capture_output=True, text=True)
        if p.returncode:
            raise ValueError(p.stderr.strip())
        top = pathlib.Path(p.stdout.strip()).resolve()
        rel = here.relative_to(top)
        old, new = (rel / slug).as_posix(), (rel / ('.' + slug)).as_posix()
        p = subprocess.run(['git', '-C', str(top), 'grep', '--untracked', '-I', '-l', '-z', '--full-name',
                            '-F', '-e', slug], env=env, capture_output=True, text=True)
        if p.returncode not in (0, 1):
            raise ValueError(p.stderr.strip())
        hits = p.stdout
        if rel.parts:  # the ticket root is often gitignored: scan it with ignore rules off so its citations count too
            q = subprocess.run(['git', '-C', str(top), 'grep', '--untracked', '--no-exclude-standard', '-I', '-l', '-z',
                                '--full-name', '-F', '-e', slug, '--', rel.as_posix()], env=env,
                               capture_output=True, text=True)
            if q.returncode not in (0, 1):
                raise ValueError(q.stderr.strip())
            hits += q.stdout
        if roadmap is None:
            skip = (rel / 'roadmap.md').as_posix()
        else:
            skip = (roadmap.parent.resolve() / roadmap.name).relative_to(top).as_posix()
        lit = literal_re(old)
        files = []
        for f in sorted({f for f in hits.split('\0') if f and f != skip and (own or not f.startswith(old + '/'))}):
            try:
                text = (top / f).read_bytes().decode('utf-8', 'surrogateescape')
            except OSError:
                files.append(f)  # unreadable: keep it, so the scan refuses instead of passing silently
                continue
            if lit.search(text) or ref_tokens(text, top, f, old):
                files.append(f)
        return top, old, new, files
    except (OSError, ValueError):
        return None, '', '', []


# A path-like token: a maximal run with no whitespace, quotes, backticks, parens, or angle or square brackets.
TOKEN_RE = re.compile(r"[^\s'\"`()<>\[\]]+")


def ref_tokens(text, top, f, old, dest=None):
    """[(start, end, rewritten)] for each path token in text (read from toplevel-relative file f under top) that
    names the folder top/old: a token holding a '/' whose component <slug> (old's last part) is a whole path
    component, where the path up to that component lands on top/old, and the whole token (trailing .,;:!?
    stripped) lands on top/old or under it, joined to f's own directory, as a toplevel-relative path, or as an
    absolute path (also after resolving symlinks). rewritten is the token with only that component turned into
    .<slug>; every other byte is kept. Lexical: the folder need not exist, so it works after the rename."""
    slug = old.rsplit('/', 1)[-1]
    dest = dest or '.' + slug
    target = os.path.normpath(str(top / old))
    fdir = os.path.dirname(os.path.normpath(str(top / f)))
    bases = [fdir, str(top)]

    def lands(path, exact):
        cands = [os.path.normpath(os.path.join(b, path)) for b in bases]
        if path.startswith('/'):
            cands.append(os.path.realpath(path))
        return any(c == target or (not exact and c.startswith(target + '/')) for c in cands)

    out = []
    for m in TOKEN_RE.finditer(text):
        tok = m.group().rstrip('.,;:!?')
        if '/' not in tok or slug not in tok.split('/'):
            continue
        parts = tok.split('/')
        for i, part in enumerate(parts):
            if part == slug and lands('/'.join(parts[:i + 1]) or '/', True) and lands(tok, False):
                parts[i] = dest
                out.append((m.start(), m.start() + len(tok), '/'.join(parts)))
                break
    return out


def rewrite_files(top, files, old, new):
    """In each toplevel-relative file under top, replace old (<rel>/<slug>) with new (<rel>/.<slug>) as bytes
    wherever the literal starts a path token (start of text or after a TOKEN_RE delimiter, never inside
    other/<rel>/<slug>) and ends at `/`, the end of a token, or punctuation (literal_re; never inside a longer
    folder name such as <rel>/<slug>b), then turn the <slug> component of each path token that ref_tokens resolves to the folder into .<slug>,
    keeping the token's form (relative, ./, absolute); all other bytes stay. Tokens resolve against each file's
    current location, so archive runs this before any rename."""
    lit = literal_re(old)
    for f in files:
        path = top / f
        text = lit.sub(lambda m: new, path.read_bytes().decode('utf-8', 'surrogateescape'))
        for start, end, tok in reversed(ref_tokens(text, top, f, old, new.rsplit('/', 1)[-1])):
            text = text[:start] + tok + text[end:]
        path.write_bytes(text.encode('utf-8', 'surrogateescape'))


def migrate_text(text, top, f, moves):
    """text (read from toplevel-relative file f under top, f's path before the moves) with each path token rewritten
    so it resolves after the moves to the file it resolved to before. moves: [(src, dst)] toplevel-relative posix
    paths. Tokens are TOKEN_RE runs holding a '/' (trailing .,;:!? stripped); a token on a line of the managed block
    onboard.find_block reports never changes. A token names a src by ref_tokens' rule; its form comes from the first
    base the prefix lands on src from: absolute (starts with /), file-relative (f's dir), toplevel-relative. A
    file-relative token in a file that moves becomes os.path.relpath from f's new dir to the moved target; any other
    named token gets only the matched component replaced by dst relative to src's parent. In a file that moves, a
    file-relative token naming no src that resolves from f's old dir to an existing path is re-expressed the same
    way. A trailing / and a leading ./ (when the new form does not start with ../) are kept."""
    top = str(top)
    S = [(os.path.normpath(os.path.join(top, s)), os.path.normpath(os.path.join(top, d))) for s, d in moves]

    def post(p):
        for s, d in S:
            if p == s or p.startswith(s + '/'):
                return d + p[len(s):]
        return p

    fpath = os.path.normpath(os.path.join(top, f))
    fdir = os.path.dirname(fpath)
    moving = post(fpath) != fpath
    newdir = os.path.dirname(post(fpath))

    def rel_form(tok, target):
        new = os.path.relpath(post(target), newdir)
        if tok.endswith('/') and not new.endswith('/'):
            new += '/'
        if tok.startswith('./') and not new.startswith('../'):
            new = './' + new
        return new

    frozen = None
    fb = onboard.find_block(text)
    if fb.status == 'block':
        lines = onboard._split_keep(text)
        frozen = (sum(len(x) for x in lines[:fb.block.start]), sum(len(x) for x in lines[:fb.block.end + 1]))
    out = []
    for m in TOKEN_RE.finditer(text):
        tok = m.group().rstrip('.,;:!?')
        if '/' not in tok or (frozen and frozen[0] <= m.start() < frozen[1]):
            continue
        parts = tok.split('/')
        new = None
        for (s, d), (src, dst) in zip(S, moves):
            name = s.rsplit('/', 1)[-1]
            if name not in parts:
                continue
            bases = [] if tok.startswith('/') else [('file', fdir), ('top', top)]
            for i, part in enumerate(parts):
                if part != name:
                    continue
                prefix = '/'.join(parts[:i + 1]) or '/'
                form = None
                if tok.startswith('/'):
                    if s in (os.path.normpath(prefix), os.path.realpath(prefix)):
                        whole = [os.path.normpath(tok), os.path.realpath(tok)]
                        if any(w == s or w.startswith(s + '/') for w in whole):
                            form = 'abs'
                else:
                    for kind, b in bases:
                        if os.path.normpath(os.path.join(b, prefix)) == s:
                            w = os.path.normpath(os.path.join(b, tok))
                            if w == s or w.startswith(s + '/'):
                                form = kind
                            break
                if form is None:
                    continue
                if form == 'file' and moving:
                    new = rel_form(tok, os.path.normpath(os.path.join(fdir, tok)))
                else:
                    parts = parts[:i] + [posixpath.relpath(dst, posixpath.dirname(src) or '.')] + parts[i + 1:]
                    new = '/'.join(parts)
                break
            if new is not None:
                break
        if new is None and moving and not tok.startswith('/'):
            target = os.path.normpath(os.path.join(fdir, tok))
            if os.path.exists(target):
                new = rel_form(tok, target)
        if new is not None and new != tok:
            out.append((m.start(), m.start() + len(tok), new))
    for start, end, new in reversed(out):
        text = text[:start] + new + text[end:]
    return text


def id_floor(root):
    """The highest ticket number in every other worktree's ticket dir (other_ticket_dirs, each resolved by that
    tree's own config) and in every branch registered by an `external_branch: <branch>` line in <root>/config
    (branch_tickets, read from git objects at the branch's ticket root), else 0. Malformed tickets and unreadable files there are ignored: another
    tree's or branch's problems never fail this one."""
    floor = 0
    found = []
    for _, r in other_ticket_dirs(root):
        try:
            found.append(load(r))
        except (OSError, UnicodeDecodeError):
            continue
    for b in external_branches(root):
        found.append(branch_tickets(root, b))
    for ts in found:
        for _, m in ts:
            i = m.get('id')
            if isinstance(i, str) and ID_RE.fullmatch(i):
                floor = max(floor, int(i[2:]))
    return floor


def folder_name(slug, tid, numbered):
    """The ticket's directory name: NNNN-<slug> from id T-NNNN in numbered mode, else the bare slug."""
    return f'{tid[2:]}-{slug}' if numbered else slug


def deps_of(m):
    d = m.get('depends', [])
    return d if isinstance(d, list) else []


def dep_kind(d):
    """'id' (T-NNNN), 'file' (file:<relative path, no ..>), 'cap' (cap:<name>), or None when malformed."""
    if not isinstance(d, str):
        return None
    if ID_RE.fullmatch(d):
        return 'id'
    if d.startswith('file:'):
        p = d[len('file:'):]
        return 'file' if p and not p.startswith('/') and '..' not in p.split('/') else None
    if d.startswith('cap:'):
        return 'cap' if CAP_RE.fullmatch(d[len('cap:'):]) else None
    return None


def provides_of(m):
    """The valid capability names m lists in `provides`; [] when absent or not a list."""
    p = m.get('provides', [])
    return [x for x in p if isinstance(x, str) and CAP_RE.fullmatch(x)] if isinstance(p, list) else []


def providers(ts):
    """{capability name: [id of every ticket, any status, that provides it]}. Tickets without a string id are left out."""
    out = {}
    for _, m in ts:
        i = m.get('id')
        if isinstance(i, str):
            for name in provides_of(m):
                out.setdefault(name, []).append(i)
    return out


def edges_of(m, prov):
    """The ids m waits on: its T-NNNN entries plus every provider of each cap: entry. file: entries add none."""
    out = set()
    for d in deps_of(m):
        k = dep_kind(d)
        if k == 'id':
            out.add(d)
        elif k == 'cap':
            out.update(prov.get(d[len('cap:'):], ()))
    return out


# ---------- validation ----------

def order(ts):
    """Kahn's algorithm, ties by id ascending. Returns (ordered [(slug, meta)], {stuck id: its deps}, by_id).
    Stuck ids sit on or behind a dependency cycle. A cap:<name> entry is an edge to every ticket that provides
    <name>; a file: entry is never an edge.
    Only tickets with a string id are placed; dangling depends are ignored here (problems() reports them)."""
    by_id = {}
    for slug, m in ts:
        i = m.get('id')
        if isinstance(i, str) and i not in by_id:
            by_id[i] = (slug, m)
    prov = providers(ts)
    need = {i: {d for d in edges_of(m, prov) if d in by_id} for i, (_, m) in by_id.items()}
    users = {i: set() for i in by_id}
    for i, ds in need.items():
        for d in ds:
            users[d].add(i)
    left = {i: len(ds) for i, ds in need.items()}
    ready = [i for i, n in left.items() if n == 0]
    heapq.heapify(ready)
    out = []
    while ready:
        i = heapq.heappop(ready)
        out.append(by_id[i])
        for u in users[i]:
            left[u] -= 1
            if left[u] == 0:
                heapq.heappush(ready, u)
    placed = {m['id'] for _, m in out}
    return out, {i: need[i] for i in by_id if i not in placed}, by_id


def cycles(ts):
    """Each dependency cycle once, as a list of ids ending where it started."""
    _, stuck, _ = order(ts)
    seen, found = set(), []
    for start in sorted(stuck):
        if start in seen:
            continue
        path, pos, i = [], {}, start
        # every stuck id has a dep that is also stuck, so this walk always ends in a cycle
        while i not in pos and i not in seen:
            pos[i] = len(path)
            path.append(i)
            i = min(d for d in stuck[i] if d in stuck)
        seen.update(path)
        if i in pos:
            found.append(path[pos[i]:] + [i])
    return found


def problems(ts, numbered=False, areas=None):
    """One line per problem, each naming the ticket slug.
    numbered also fails a NNNN-<slug> (or .NNNN-<slug>) folder whose id is not T-NNNN; plain slugs are never
    prefix-checked. In any mode, a .NNNN-<slug> folder fails unless its status is done or dropped.
    status: claimed needs a non-empty string claimed_by, and status: paused a non-empty string paused_reason;
    on any other status neither field is validated. areas is config_areas(root): an `area:` must be a non-empty
    string in it, and with areas == [] any `area:` fails naming the config line to add. areas=None (a caller
    with no root) skips the area check. An absent `area:` is always valid; an area is never a lane name."""
    errs, ids = [], {}
    for slug, m in ts:
        if DOT_RE.fullmatch(slug) and m.get('status') not in ('done', 'dropped'):
            errs.append(f'{slug}: closed ticket folder (dot prefix) has status {m.get("status")!r}; want done or '
                        f'dropped (rename it to {slug[1:]} to reopen)')
        name = slug.lstrip('.')
        if numbered and PREFIX_RE.match(name) and isinstance(m.get('id'), str):
            nnnn = name[:4]
            if m['id'] != f'T-{nnnn}':
                errs.append(f'{slug}: folder prefix {nnnn}- does not match id {m["id"]!r} (want T-{nnnn})')
        gone = [k for k in REQUIRED if k not in m]
        if gone:
            errs.append(f'{slug}: missing {", ".join(gone)}')
        for k, allowed in ENUMS.items():
            if k in m and m[k] not in allowed:
                errs.append(f'{slug}: {k}={m[k]!r} not in {"|".join(allowed)}')
        if 'id' in m:
            i = m['id']
            if not isinstance(i, str) or not ID_RE.fullmatch(i) or i == 'T-0000':
                errs.append(f'{slug}: id {i!r} is not T-NNNN (T-0000 is the template placeholder)')
            elif i in ids:
                errs.append(f'{slug}: duplicate id {i}, also used by {ids[i]}')
            else:
                ids[i] = slug
        if 'created' in m and not (isinstance(m['created'], str) and DATE_RE.fullmatch(m['created'])):
            errs.append(f'{slug}: created {m["created"]!r} is not YYYY-MM-DD')
        if 'depends' in m and not isinstance(m['depends'], list):
            errs.append(f'{slug}: depends {m["depends"]!r} is not a list like [T-0002]')
        if 'provides' in m:
            if not isinstance(m['provides'], list):
                errs.append(f"{slug}: provides '{m['provides']}' is not a list like [name]")
            else:
                for x in m['provides']:
                    if not (isinstance(x, str) and CAP_RE.fullmatch(x)):
                        errs.append(f"{slug}: provides item '{x}' is not a name like [A-Za-z0-9][A-Za-z0-9._-]*")
        if 'from' in m and not isinstance(m['from'], str):
            errs.append(f'{slug}: from {m["from"]!r} is not a single ticket id')
        for st, field in (('claimed', 'claimed_by'), ('paused', 'paused_reason')):
            v = m.get(field)
            if m.get('status') == st and not (isinstance(v, str) and v.strip()):
                errs.append(f'{slug}: status {st} needs a non-empty {field}: line in its front matter')
        if 'area' in m and areas is not None:
            a = m['area']
            if not areas:
                errs.append(f'{slug}: area {a!r} but no areas are configured; add `areas: <name>, ...` to '
                            f'<root>/config')
            elif not (isinstance(a, str) and a.strip() in areas):
                errs.append(f'{slug}: area {a!r} not in the config areas {", ".join(areas)}')
    prov = providers(ts)
    for slug, m in ts:
        for dep in deps_of(m):
            k = dep_kind(dep)
            if k is None:
                errs.append(f"{slug}: depends entry '{dep}' is not T-NNNN, file:<path> or cap:<name>")
            elif k == 'id' and dep not in ids:
                errs.append(f'{slug}: depends on {dep}, which no ticket has')
            elif k == 'cap' and dep[len('cap:'):] not in prov:
                errs.append(f'{slug}: depends on {dep}, which no ticket provides')
        f = m.get('from')
        if isinstance(f, str) and f not in ids:
            errs.append(f'{slug}: from {f}, which no ticket has')
    for cyc in cycles(ts):
        errs.append(f'{ids.get(cyc[0], cyc[0])}: dependency cycle {" -> ".join(cyc)}')
    return errs


# ---------- roadmap ----------

def skip_section(text, heading):
    """Lines of the `## <heading>` section (from that exact line to the next `## ` line), or None if absent."""
    out = None
    for ln in text.splitlines():
        if out is None:
            if ln.rstrip() == f'## {heading}':
                out = []
        elif ln.startswith('## '):
            break
        else:
            out.append(ln)
    return out


def skip_missing(d, covered=()):
    """(lane, [missing roles]) for ticket dir d's skips.md, or None when exempt: no skips.md, no ## Lane
    section, no `- lane:` line in it, or a last lane other than solo, lean, fix, or full. The full chain's planner,
    verifier per live step-<digits>/ and filer each need a counting `- skip: <role>; ...` entry under
    ## Skipped when their result is missing (format: skills/handoff-format, Layout). covered names roles to
    count as skipped (close passes ('verifier',) for a docs-only diff, T-0429)."""
    f = d / 'skips.md'
    if not f.is_file():
        return None
    text = f.read_text(encoding='utf-8')
    lanes = [ln[len('- lane: '):].split(';', 1)[0].strip()
             for ln in (skip_section(text, 'Lane') or []) if ln.startswith('- lane: ')]
    if not lanes or lanes[-1] not in ('solo', 'lean', 'fix', 'full'):
        return None
    cover = {}
    for ln in skip_section(text, 'Skipped') or []:
        if not ln.startswith('- skip: '):
            continue
        parts = ln[len('- skip: '):].split(';')
        kv = {}
        for part in parts[1:]:
            if ':' in part:
                k, v = part.split(':', 1)
                kv[k.strip()] = v.strip()
        if kv.get('reason') and kv.get('decided'):
            cover.setdefault(parts[0].strip(), set()).add(kv.get('step', ''))
    missing = []
    if not run_order.ordered(d, 'planner') and 'planner' not in cover:
        missing.append('planner')
    steps = sorted(int(p.name[5:]) for p in d.iterdir() if p.is_dir() and re.fullmatch(r'step-\d+', p.name))
    for n in steps:
        if 'verifier' not in covered and not run_order.ordered(d / f'step-{n}', 'verifier') and not (
                cover.get('verifier', set()) & {str(n), 'all'}):
            missing.append(f'verifier step {n}')
    if not run_order.ordered(d, 'filer') and 'filer' not in cover:
        missing.append('filer')
    return (lanes[-1], missing) if missing else None


def recorded_base(d):
    """The commit a ticket's build started from: the first line of <d>/base-sha, else of the lowest live step-<n>/base-sha;
    None when no role recorded one."""
    steps = sorted((int(p.name[5:]), p) for p in d.iterdir() if p.is_dir() and re.fullmatch(r'step-\d+', p.name))
    for f in [d / 'base-sha'] + [p / 'base-sha' for _, p in steps]:
        try:
            first = (f.read_text(encoding='utf-8').splitlines() or [''])[0].strip()
        except OSError:
            continue
        if first:
            return first
    return None


def docs_waiver(d):
    """The recorded base when the ticket's diff against it is docs, records and reports only and its checks are green
    (verify_scope.scope), so close needs no verifier result; None otherwise, also with no recorded base or no git
    (T-0429). A `verifier: L1`..`L3` line in the handoff keeps the verifier."""
    import verify_scope  # local like steps: only close needs it
    base = recorded_base(d)
    top = verify_scope.toplevel(str(d))
    if not base or not top:
        return None
    try:
        ok, _ = verify_scope.scope(top, base, str(d / 'handoff.md'))
    except ValueError:
        return None
    return base if ok else None


def add_skip_line(f, line):
    """Append one `- skip:` line to the end of the ## Skipped section of skips.md f, adding the section when it is absent."""
    lines = f.read_text(encoding='utf-8').splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.rstrip() == '## Skipped'), None)
    if start is None:
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        lines += ['\n', '## Skipped\n', line + '\n']
    else:
        pos = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('## ')), len(lines))
        while pos > start + 1 and not lines[pos - 1].strip():
            pos -= 1
        if not lines[pos - 1].endswith('\n'):
            lines[pos - 1] += '\n'
        lines.insert(pos, line + '\n')
    f.write_text(''.join(lines), encoding='utf-8')


def skip_line(folder, got):
    return f'{folder}: skips.md records lane {got[0]} but has no ## Skipped entry for {", ".join(got[1])}'


def skip_problems(td, ts):
    """One line per done ticket whose skips.md records lane solo, lean, fix, or full but has neither the result nor a ## Skipped entry for a
    role the full chain would have run (skip_missing). Only check and close use it, not problems()."""
    out = []
    for folder, m in ts:
        if m.get('status') == 'done':
            got = skip_missing(td / folder)
            if got:
                out.append(skip_line(folder, got))
    return out


# A template line that is real default content, not a prompt to the author: a closed ticket may keep it.
PLACEHOLDER_KEEP = frozenset({
    'the bug is fixed and a test that failed before the fix passes after it',
    'the failing test lands before or with the fix, never after',
    'a decision or a recommendation with cited evidence, written back into this file',
    'timebox. no production code lands from a spike',
})
PLACEHOLDER_SHOWN = 5  # warning lines printed per check, newest ticket first; the rest are counted in one line
LABEL_ONLY_RE = re.compile(r'(?:[-*]|\d+[.)])?[ \t]*[^:]{1,40}:')  # fullmatch: a bare `- Do:` label


def prompt_text(line):
    """The comparable form of one body line: no list marker, no trailing period, lower case. '' for a blank,
    a heading, or a bare `- Label:` line (a label is structure, not a prompt)."""
    line = line.strip()
    if not line or line.startswith('#') or LABEL_ONLY_RE.fullmatch(line):
        return ''
    m = BULLET_RE.fullmatch(line)
    return (m.group(1) if m else line).strip().rstrip('.').strip().lower()


def body_lines(text):
    """[(line number, line)] after the front matter block; every line when there is none."""
    lines = text.replace('\r\n', '\n').split('\n')
    start = 0
    if lines and lines[0] == '---':
        for i in range(1, len(lines)):
            if re.fullmatch(r'---[ \t]*', lines[i]):
                start = i + 1
                break
    return [(i + 1, lines[i]) for i in range(start, len(lines))]


def placeholder_problems(root, td, ts):
    """One warning line per done or dropped ticket whose handoff.md still holds a prompt line copied verbatim
    from the template of its type (<root>/_templates first, as `new` reads it): the first such line, with its
    line number. Warnings only: check prints them and still passes. Newest ticket (highest id) first,
    at most PLACEHOLDER_SHOWN lines, then one line counting the rest: old closed tickets are history, the
    recent ones are the ones to fix."""
    prompts, out = {}, []
    for slug, m in sorted(ts, key=lambda t: str(t[1].get('id', '')), reverse=True):
        if m.get('status') not in ('done', 'dropped'):
            continue
        kind = m.get('type')
        if kind not in prompts:
            try:
                prompts[kind] = {t for _, l in body_lines(template(root, kind).read_text(encoding='utf-8'))
                                 for t in [prompt_text(l)] if t and t not in PLACEHOLDER_KEEP}
            except (Fail, OSError):
                prompts[kind] = set()
        try:
            text = (td / slug / 'handoff.md').read_text(encoding='utf-8')
        except OSError:
            continue
        for n, line in body_lines(text):
            if prompt_text(line) in prompts[kind] and prompt_text(line):
                out.append(f'warning: {slug}/handoff.md:{n}: closed ticket still holds {kind} template placeholder '
                           f'text: {line.strip()[:60]!r}')
                break
    if len(out) > PLACEHOLDER_SHOWN:
        out[PLACEHOLDER_SHOWN:] = [f'warning: {len(out) - PLACEHOLDER_SHOWN} more closed tickets hold template '
                                   f'placeholder text ({PLACEHOLDER_SHOWN} shown, newest first)']
    return out


def unfilled_line(root, text):
    """(line number, line) of the first template prompt line an open handoff still holds, or None. Same rule as
    placeholder_problems (a prompt line of the handoff's type template, copied verbatim), plus one stricter
    case: a line under `## Goal` that is the template's own Goal text, even when PLACEHOLDER_KEEP lets a closed
    ticket keep it. None when the text has no front matter type or no template for it (a plain task handoff)."""
    m = re.match(r'---\n(.*?)\n---[ \t]*(?:\n|$)', text.replace('\r\n', '\n'), re.S)
    kind = None
    for line in (m.group(1).split('\n') if m else []):
        k = re.fullmatch(r'type:[ \t]*([A-Za-z0-9_-]+)[ \t]*(?:#.*)?', line)
        if k:
            kind = k.group(1)
    if not kind:
        return None
    try:
        tmpl = body_lines(template(root, kind).read_text(encoding='utf-8'))
    except (Fail, OSError):
        return None
    prompts = {t for _, l in tmpl for t in [prompt_text(l)] if t and t not in PLACEHOLDER_KEEP}
    goal, in_goal = set(), False
    for _, l in tmpl:
        if l.startswith('#'):
            in_goal = l.strip().lower() == '## goal'
        elif in_goal and prompt_text(l):
            goal.add(prompt_text(l))
    in_goal = False
    for n, line in body_lines(text):
        if line.startswith('#'):
            in_goal = line.strip().lower() == '## goal'
        t = prompt_text(line)
        if t and (t in prompts or in_goal and t in goal):
            return n, line


def file_base(root):
    """The dir file:<path> entries resolve against: the git toplevel of root, else root's parent directory
    (git missing or failing, or root outside git). GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE are dropped."""
    anchor = root.resolve()
    while not anchor.is_dir() and anchor != anchor.parent:
        anchor = anchor.parent
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
    try:
        p = subprocess.run(['git', '-C', str(anchor), 'rev-parse', '--show-toplevel'], env=env,
                           capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            return pathlib.Path(p.stdout.strip())
    except OSError:
        pass
    return root.resolve().parent


def render_dep(d, met_caps, base):
    """One Depends on entry: T-NNNN as is; file:/cap: as is when met, else with ' (unmet)'; '|' escaped."""
    k = dep_kind(d)
    if k == 'file' and not (base() / d[len('file:'):]).exists():
        d += ' (unmet)'
    elif k == 'cap' and d[len('cap:'):] not in met_caps:
        d += ' (unmet)'
    return d.replace('|', '\\|')


def area_of(m):
    """A ticket's non-empty string area, stripped, else ''."""
    a = m.get('area')
    return a.strip() if isinstance(a, str) else ''


def render(ts, root):
    """The roadmap text. An Area column after Type appears only when some ticket has a non-empty area, so a
    root with no area renders byte for byte as before. A paused Status cell carries its paused_reason."""
    with_area = any(area_of(m) for _, m in ts)
    if with_area:
        rows = ['| ID | Ticket | Title | Type | Area | Size | Pri | Depends on | Status |',
                '|---|---|---|---|---|---|---|---|---|']
    else:
        rows = ['| ID | Ticket | Title | Type | Size | Pri | Depends on | Status |',
                '|---|---|---|---|---|---|---|---|']
    ordered, _, _ = order(ts)
    met_caps = {name for _, m in ts if m.get('status') == 'done' for name in provides_of(m)}
    cache = []

    def base():
        if not cache:
            cache.append(file_base(root))
        return cache[0]
    lp = layout_paths(root)
    prefix = '' if lp.tickets == lp.roadmap.parent else 'tickets/'
    for slug, m in ordered:
        deps = ', '.join(render_dep(d, met_caps, base) for d in m['depends']) or 'none'
        title = m['title'].replace('|', '\\|')
        status = f"{GLYPH[m['status']]} {m['status']}"
        if m['status'] == 'paused' and isinstance(m.get('paused_reason'), str):
            status += f" ({m['paused_reason'].strip()})".replace('|', '\\|')
        area = ' ' + area_of(m).replace('|', '\\|') + ' |' if with_area else ''
        rows.append(f"| {m['id']} | [{slug}]({prefix}{slug}/handoff.md) | {title} | {m['type']} |{area} {m['size']} | "
                    f"{m['priority']} | {deps} | {status} |")
    return HEADER + '\n' + '\n'.join(rows) + '\n'


def write_roadmap(root, ts):
    path = layout_paths(root).roadmap
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render(ts, root).encode('utf-8'))
    write_router(root, ts)
    import messages  # same scripts/ dir; local so board, fanout and traces, which import tickets to parse, skip it
    messages.write_entries(os.path.join(root, 'messages'))
    return path


def stale(root, ts):
    path = layout_paths(root).roadmap
    if not path.exists():
        return bool(ts)
    return path.read_bytes() != render(ts, root).encode('utf-8')


# ---------- router ----------

ROUTER_PLUGIN_LINE = ('- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: '
                      '`${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` '
                      'skill.\n')

ROUTER_PROCEDURES = """\
## Procedures

Create a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root <R> new <feature|bug|chore|spike|idea> <slug> "<title>"`. \
Never pick an id by hand: `new` stamps the next id above every worktree's.
2. Fill in the body sections of the new `handoff.md`.

Ticket fields:
status: proposed | ready | claimed | paused | blocked | done | dropped
- `area:` is optional: the ticket's domain, one of the `areas:` names in `<R>/config`. It is never a lane or \
branch name.
- `paused_reason:` is the one-line reason a `status: paused` ticket waits; `status: claimed` needs `claimed_by:`.

Claim a ticket:
1. Open its `handoff.md`. A `claimed_by:` front matter line means another agent holds it: pick another ticket or \
ask the user.
2. Set `status: claimed` and add `claimed_by: <claude|codex> <YYYY-MM-DD>` to the front matter, then run \
`python3 <plugin-root>/scripts/tickets.py --root <R> roadmap`.
3. Start the work through `run.sh`, which puts it in progress: \
`<plugin-root>/scripts/run.sh planner <level> <T>/<folder>/handoff.md`, or `/sdlc-lite:chain <T>/<folder>`. \
Progress shows on `/board`.
4. Release: remove the `claimed_by:` line and set `status: ready`. Pause: set `status: paused` and add a one-line \
`paused_reason:`. Rerun `roadmap` after either.

Close a ticket:
1. Run the filer (`/file`): `<plugin-root>/scripts/run.sh filer L1 <T>/<folder>/handoff.md`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root <R> close <folder> --dry-run`. It lists each follow-up as \
`<i>. <tag>: <title>` and ends with `expect <digest>`.
3. Run `python3 <plugin-root>/scripts/tickets.py --root <R> close <folder>`. To file the one `decide:` follow-up \
worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to \
`notes.md`; `fix-now:` items are finished before the close.
4. Work already done by another ticket: \
`python3 <plugin-root>/scripts/tickets.py --root <R> close <folder> --reason "<why>"`.
"""

ROUTER_TEMPLATE = """\
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` \
(also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front \
matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are \
history: open one only when asked.

<ticket folders line>
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
""" + ROUTER_PLUGIN_LINE + """
## Stages

<stage lines>

""" + ROUTER_PROCEDURES

TICKETS_TEMPLATE = """\
# Tickets

One folder per ticket: `<slug>/` or `NNNN-<slug>/` while open, `.NNNN-<slug>/` once closed. Stage counts and the \
open tickets are in `../AGENTS.md`. `tickets.py roadmap` generates this block: do not edit inside it.

""" + ROUTER_PLUGIN_LINE + '\n' + ROUTER_PROCEDURES

ROUTER_FLAT_INTRO = """\
This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` \
(also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front \
matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are \
history: open one only when asked.
"""

ROUTER_TOPICS_INTRO = """\
This folder holds SDLC Lite records in topic folders: `tickets/` (ticket folders and `tickets/roadmap.md`), `work/` \
(task folders with no ticket), `notes/` (`notes/notes.md`), and `messages/`, beside `config` and `_templates/`. \
`tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's \
`handoff.md` front matter and rerun `roadmap`. `tickets/roadmap.md` lists every ticket in dependency order. Closed \
`.NNNN-*` folders are history: open one only when asked.
"""

WORK_TEMPLATE = """\
# Work

One folder per task with no ticket: release records, verification handoffs, dogfood runs. Ticket folders are in \
`../tickets/`. `tickets.py roadmap` generates this block: do not edit inside it.
"""

NOTES_TEMPLATE = """\
# Notes

`notes.md` holds the follow-ups `tickets.py close` appends: `note:` items and the `decide:` items not filed as \
tickets. It names no folder paths. `tickets.py roadmap` generates this block: do not edit inside it.
"""

ROUTER_HERE = '- Ticket folders: next to this file.'
ROUTER_TICKETS = '- Ticket folders: `tickets/`; the same procedures are in `tickets/AGENTS.md`.'
ACTIVE = ('proposed', 'ready', 'claimed', 'paused', 'blocked')


def router_paths(root):
    """(R, T): root and its ticket dir relative to file_base(root), in posix form (`.sdlc`, and `.sdlc` or
    `.sdlc/tickets` for the usual root), so the router text holds no absolute path."""
    here, base = root.resolve(), file_base(root).resolve()
    try:
        rel = here.relative_to(base).as_posix()
    except ValueError:
        rel = pathlib.Path(os.path.relpath(here, base)).as_posix()
    if ticket_dir(root) == root:
        return rel, rel
    return rel, (pathlib.PurePosixPath(rel) / 'tickets').as_posix()


def router_files(root):
    """[(label, path, kind)] for the managed router files: AGENTS.md and CLAUDE.md at <root>, with
    `ticket_root: tickets` also tickets/AGENTS.md and tickets/CLAUDE.md, and with `layout: topics` also
    work/AGENTS.md, work/CLAUDE.md, notes/AGENTS.md and notes/CLAUDE.md. kind is 'agents' or 'claude'."""
    out = [('AGENTS.md', root / 'AGENTS.md', 'agents'), ('CLAUDE.md', root / 'CLAUDE.md', 'claude')]
    if ticket_dir(root) != root:
        out += [('tickets/AGENTS.md', root / 'tickets' / 'AGENTS.md', 'agents'),
                ('tickets/CLAUDE.md', root / 'tickets' / 'CLAUDE.md', 'claude')]
    if layout_paths(root).layout == 'topics':
        for d in ('work', 'notes'):
            out += [(f'{d}/AGENTS.md', root / d / 'AGENTS.md', 'agents'),
                    (f'{d}/CLAUDE.md', root / d / 'CLAUDE.md', 'claude')]
    return out


def stage_lines(ts):
    """One `- <stage>: <count>` line per status in ENUMS order; under each ACTIVE status (proposed, ready,
    claimed, paused, blocked) one `  - <id> <title> (<folder>)` line per ticket in id order, with
    `, claimed by <value>` for a non-empty string claimed_by, then `, paused: <reason>` for a paused ticket's
    non-empty string paused_reason. The folder is the bare folder name, never a path."""
    out = []
    for st in ENUMS['status']:
        group = sorted(((m.get('id') if isinstance(m.get('id'), str) else '', slug, m)
                        for slug, m in ts if m.get('status') == st), key=lambda e: (e[0], e[1]))
        out.append(f'- {st}: {len(group)}')
        if st in ACTIVE:
            for tid, slug, m in group:
                title = m.get('title') if isinstance(m.get('title'), str) else ''
                line = f'  - {tid} {title} ({slug})'
                c = m.get('claimed_by')
                if isinstance(c, str) and c.strip():
                    line += f', claimed by {c.strip()}'
                r = m.get('paused_reason')
                if st == 'paused' and isinstance(r, str) and r.strip():
                    line += f', paused: {r.strip()}'
                out.append(line)
    return out


def router_bodies(root, ts):
    """{label: block text} for every managed AGENTS.md: the router at <root> and, with `ticket_root: tickets`,
    the tickets/AGENTS.md block. Text between the markers, ending with a newline. Under `layout: topics` the
    router's first paragraph is ROUTER_TOPICS_INTRO, both procedures send notes to `<R>/notes/notes.md`, and
    work/AGENTS.md and notes/AGENTS.md get WORK_TEMPLATE and NOTES_TEMPLATE; the flat text is unchanged."""
    r, t = router_paths(root)
    nested = ticket_dir(root) != root
    topics = layout_paths(root).layout == 'topics'
    body = (ROUTER_TEMPLATE.replace('<ticket folders line>', ROUTER_TICKETS if nested else ROUTER_HERE)
            .replace('<stage lines>', '\n'.join(stage_lines(ts))))
    tickets_body = TICKETS_TEMPLATE
    if topics:
        body = body.replace(ROUTER_FLAT_INTRO, ROUTER_TOPICS_INTRO, 1)
        body, tickets_body = (b.replace('go to `notes.md`', 'go to `<R>/notes/notes.md`') for b in (body, tickets_body))
    out = {'AGENTS.md': body.replace('<R>', r).replace('<T>', t)}
    if nested:
        out['tickets/AGENTS.md'] = tickets_body.replace('<R>', r).replace('<T>', t)
    if topics:
        out['work/AGENTS.md'] = WORK_TEMPLATE
        out['notes/AGENTS.md'] = NOTES_TEMPLATE
    return out


def read_text(path):
    return path.read_bytes().decode('utf-8', 'surrogateescape')


def router_preflight(root):
    """Refuse, before any write, while a managed AGENTS.md holds a malformed block."""
    errs = []
    for label, path, kind in router_files(root):
        if kind == 'agents' and path.is_file():
            f = onboard.find_block(read_text(path))
            if f.status == 'malformed':
                errs.append(f'{label}: router block malformed: {f.reason}; fix its markers by hand, then rerun; '
                            f'nothing written')
    if errs:
        raise Fail('\n'.join(errs))


def write_router(root, ts):
    """Write or refresh every managed router file (router_files) from ts, the tickets of the ticket dir. An
    AGENTS.md: missing is created as the wrapped block alone; no block gets it appended (_append_region); a
    block gets it replaced (_replace_region); a malformed one is left alone (the preflight refuses first). A
    CLAUDE.md: missing becomes `@AGENTS.md`; without the import the line is appended; else untouched."""
    bodies = router_bodies(root, ts)
    for label, path, kind in router_files(root):
        path.parent.mkdir(parents=True, exist_ok=True)
        old = read_text(path) if path.is_file() else None
        if kind == 'agents':
            region = onboard.wrap_block(bodies[label])
            if old is None:
                new = region
            else:
                f = onboard.find_block(old)
                if f.status == 'malformed':
                    continue
                new = (onboard._replace_region(old, f.block, region) if f.status == 'block'
                       else onboard._append_region(old, region))
        elif old is None:
            new = '@AGENTS.md\n'
        elif onboard.has_import(old):
            continue
        else:
            new = old + ('' if not old or old.endswith('\n') else '\n') + '@AGENTS.md\n'
        if new != old:
            path.write_bytes(new.encode('utf-8', 'surrogateescape'))


def router_problems(root, ts):
    """One line per router problem, for check: a managed AGENTS.md whose file or block is missing, whose block
    is stale (text, digest or version differs from onboard.wrap_block of the expected body) or malformed, and a
    managed CLAUDE.md with no @AGENTS.md import. [] when ts is empty and <root>/AGENTS.md does not exist."""
    if not ts and not (root / 'AGENTS.md').exists():
        return []
    bodies = router_bodies(root, ts)
    run_it = f'run tickets.py --root {root} roadmap'
    out = []
    for label, path, kind in router_files(root):
        text = read_text(path) if path.is_file() else None
        if kind == 'claude':
            if text is None or not onboard.has_import(text):
                out.append(f'{label}: no @AGENTS.md import; {run_it}')
            continue
        f = onboard.find_block(text) if text is not None else None
        if f is None or f.status == 'none':
            out.append(f'{label}: router block missing; {run_it}')
        elif f.status == 'malformed':
            out.append(f'{label}: router block malformed: {f.reason}; fix its markers by hand, then {run_it}')
        else:
            body = bodies[label]
            if (f.block.text != body or f.block.digest != onboard.digest(body)
                    or f.block.version != onboard.TEMPLATE_VERSION):
                out.append(f'{label}: router block stale; {run_it}')
    return out


# ---------- commands ----------

def template_types(root):
    dirs = [root / '_templates', PLUGIN / 'skills' / 'ticket' / 'templates']
    return sorted({p.stem for d in dirs if d.is_dir() for p in d.glob('*.md')})


def template(root, kind):
    for d in (root / '_templates', PLUGIN / 'skills' / 'ticket' / 'templates'):
        p = d / f'{kind}.md'
        if p.is_file():
            return p
    raise Fail(f'no template for type {kind!r}; available types: {", ".join(template_types(root))}')


def stamp(root, ts, kind, slug, title='', origin=None, context=None, numbered=False, floor=0):
    """Text and meta of a new ticket, validated against ts (which must already be clean). Writes nothing.
    The new id is one above the max of ts's ids and floor (id_floor: the max in every other git worktree).
    origin adds `from: <id>` right after the created: line; context replaces the body of ## Context.
    numbered checks for and validates under the folder name folder_name(slug, <new id>, True). The template
    comes from <root>; the exists check is under ticket_dir(root)."""
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    tpl = template(root, kind)
    nums = [int(m['id'][2:]) for _, m in ts]
    tid = f'T-{max(nums + [floor]) + 1:04d}'
    name = folder_name(slug, tid, numbered)
    d = ticket_dir(root) / name
    if d.exists() or any(s == name for s, _ in ts):
        raise Fail(f'{name}: {d} already exists; nothing written')
    text = tpl.read_text(encoding='utf-8')
    text = text.replace('id: T-0000', f'id: {tid}', 1)
    text = text.replace('created: YYYY-MM-DD', f'created: {datetime.date.today().isoformat()}', 1)
    if title:
        clean = ' '.join(title.replace('"', "'").split())
        text = text.replace('title: ""', f'title: "{clean}"', 1)
    if origin:
        text, n = re.subn(r'^(created:.*)$', lambda m: f'{m.group(1)}\nfrom: {origin}', text, count=1, flags=re.M)
        if not n:
            raise Fail(f'{tpl}: template has no created: line to put from: after; nothing written')
    if context is not None:
        m = re.search(r'^## Context[ \t]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
        if not m:
            raise Fail(f'{tpl}: template has no ## Context section; nothing written')
        gap = '\n\n' if m.end(1) < len(text) else '\n'
        text = text[:m.start(1)] + context.strip('\n') + gap + text[m.end(1):]
    fm = re.match(r'---\r?\n.*?^(---[ \t]*\r?$)', text, re.S | re.M)
    if fm:
        t = router_paths(root)[1]
        text = (text[:fm.start(1)] + f'router: {t}/AGENTS.md  # how to claim and close this ticket\n'
                + text[fm.start(1):])
    text = normalize_size_text(text)[0]  # an older consumer template's alias size is stored as its level
    meta = parse(text)
    if meta is None:
        raise Fail(f'{tpl}: template has no front matter; nothing written')
    if numbered and meta.get('id') != tid:
        raise Fail(f'{tpl}: template has no id: T-0000 line to stamp, so the folder cannot be numbered; '
                   f'nothing written')
    errs = problems(ts + [(name, meta)], numbered, areas=config_areas(root))
    if errs:
        raise Fail('\n'.join(errs + [f'{tpl}: template gives a bad ticket; nothing written']))
    return text, meta


def cmd_new(root, kind, slug, title='', origin=None, context=None, numbered=False):
    td = layout_paths(root).tickets
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    if numbered and PREFIX_RE.match(slug):
        raise Fail(f'slug {slug!r} already starts with NNNN-: numbered mode adds the prefix itself, so this '
                   f'would double it; pass the bare slug {slug[5:]!r}; nothing written')
    template(root, kind)
    if not numbered and (td / slug).exists():
        raise Fail(f'{slug}: {td / slug} already exists; nothing written')
    ts = load(td)
    errs = problems(ts, numbered, areas=config_areas(root)) + strays(root)
    if errs:
        raise Fail('\n'.join(errs + ['refusing to add a ticket: fix the problems above first']))
    router_preflight(root)
    text, meta = stamp(root, ts, kind, slug, title, origin, context, numbered, floor=id_floor(root))
    d = td / folder_name(slug, meta['id'], numbered)
    d.mkdir(parents=True)
    path = d / 'handoff.md'
    path.write_text(text, encoding='utf-8')
    if flag:
        ensure_numbered_config(root)
    write_roadmap(root, load(td))
    return str(path)


def section(text, heading):
    """Body of `## <heading>` up to the next `## ` heading or EOF, stripped; None if the heading is absent."""
    text = text.replace('\r\n', '\n')
    m = re.search(rf'^## {re.escape(heading)}[ \t]*(?:\n|\Z)(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1).strip() if m else None


BULLET_RE = re.compile(r'(?:[-*]|\d+[.)])[ \t]+(.*)')


def bullets(body):
    """Top-level list items (marker at column 0). Every later non-blank line joins the current item,
    so no text after the first bullet is dropped. Text before the first bullet is a lead-in."""
    items = []
    for line in body.splitlines():
        m = BULLET_RE.fullmatch(line.rstrip())
        if m:
            items.append([m.group(1).strip()])
        elif items and line.strip():
            items[-1].append(line.strip())
    return [' '.join(x for x in parts if x) for parts in items if any(parts)]


def is_none(text):
    # "None" or "None." optionally followed by an explanation ("None. All steps passed."), never "None of ..."
    return re.match(r'none(\.(\s|$)|$)', text.strip(), re.I) is not None


def follow_up_title(plain):
    """A <= 70 char title for a follow-up bullet's cleaned text, never cut mid-word."""
    if len(plain) <= 70:
        return plain
    m = re.search(r'[.!?] ', plain)
    if m and m.start() == 0:
        return follow_up_title(plain[m.end():])
    if m and m.start() <= 70:
        return plain[:m.start()]
    cut = plain.rfind(' ', 0, 68)
    if cut == -1:
        return plain[:67] + '...'
    return plain[:cut].rstrip(' ,;:.-') + '...'


def norm_title(s):
    """Lowercase words only, for the follow-up duplicate check: 'Fix #12' -> 'fix 12'."""
    return ' '.join(re.findall(r'[a-z0-9]+', s.lower()))


def strip_prefix(name):
    """name without its NNNN- prefix(es) and a closed folder's dot: '0002-beta' and '.0002-beta' -> 'beta'."""
    if DOT_RE.fullmatch(name):
        name = name[1:]
    while PREFIX_RE.match(name):
        name = name[5:]
    return name


def follow_digest(items):
    """The token that ties --skip indices to the exact Follow-ups list a dry run showed: a short sha256 of
    the full ordered bullet texts (items is bullets(follow), or [] for None), so reordering, adding,
    removing, or rewording any item changes it."""
    return hashlib.sha256('\n'.join(items).encode('utf-8')).hexdigest()[:12]


def parse_skip(text):
    """--skip N[,N...] as a list of ints; a token that is not an integer is a refusal, not a traceback."""
    out = []
    for tok in text.split(','):
        try:
            out.append(int(tok.strip()))
        except ValueError:
            raise Fail(f'--skip {text!r}: {tok.strip()!r} is not an integer; give 1-based indices like '
                       f'--skip 2,3; nothing written') from None
    return out


TAG_RE = re.compile(r'(fix-now|decide|note):[ \t]*')


def follow_tag(item):
    """(tag, text) of a Follow-ups bullet: a leading `fix-now:`, `decide:` or `note:` (case as written) is the
    tag and the rest is the text; an untagged bullet counts as decide, so legacy filer output stays closable."""
    m = TAG_RE.match(item)
    return (m.group(1), item[m.end():]) if m else ('decide', item)


def append_notes(root, pid, title, entries):
    """Append one `## <id>: <title> (<date>)` block with a `- <tag>: <text>` line per entry to layout_paths(root).notes
    (<root>/notes.md, or <root>/notes/notes.md under `layout: topics`), creating its folder and the file with a
    heading first. Never a folder path, so the numbered reference scan never hits it."""
    p = layout_paths(root).notes
    p.parent.mkdir(parents=True, exist_ok=True)
    old = p.read_text(encoding='utf-8') if p.is_file() else (
        '# Notes\n\n`tickets.py close` appends follow-ups that did not become tickets.\n')
    if not old.endswith('\n'):
        old += '\n'
    block = f'\n## {pid}: {title} ({datetime.date.today().isoformat()})\n\n' + ''.join(
        f'- {tag}: {text}\n' for tag, text in entries)
    p.write_text(old + block, encoding='utf-8')


def lane_report(root, pid):
    """The `lane still open: <path> (branch <b>, <reason>)` lines (lanes.still_open) for a ticket just closed, each
    behind a newline, one per plugin lane that lists it (T-0453). Report only: a failure adds nothing and never changes the exit code."""
    try:
        import lanes  # local like steps: only close reads lanes
        lines = lanes.still_open(pathlib.Path(root), pid)
    except Exception:  # noqa: BLE001 - lanes is advisory here
        return ''
    return ''.join('\n' + ln for ln in lines)


def cmd_close(root, slug, force=False, numbered=False, reason=None, dry_run=False, skip=None, expect=None,
              ack_warnings=None, rewrite_refs=False, ticket=None, keep_refs=False):
    """Read the newest filer-L*.md: refuse on open warnings, file at most one follow-up (the --ticket item) as
    a proposed idea ticket with from: <id>, append every other follow-up that is not skipped or a duplicate to
    <root>/notes.md, set the ticket done, regenerate the roadmap. Every refusal writes nothing.
    Each Follow-ups bullet has a tag (follow_tag): fix-now, decide or note; untagged counts as decide. Title,
    slug, duplicate check and ticket context use the text after the tag; the digest covers the full bullets.
    ticket: the one 1-based index to file; it must be a decide item, in range, not skipped, not a duplicate,
    and (unless dry_run) comes with expect. Without it, close files no ticket.
    numbered (or <root>/config) names the follow-up folder NNNN-<slug> after its new id.
    On success, --numbered persists `ticket_folders: numbered` in <root>/config, as new does.
    reason (not None) skips the filer: set done, append a ## Closed section, file no follow-ups.
    A follow-up matching any other ticket (ts, never the one being closed) by normalized title or slug base is skipped as a duplicate.
    skip: 1-based Follow-ups indices not to file. dry_run: same refusals, list the plan, write nothing.
    The dry run ends with `expect <digest>` (follow_digest). expect: that digest; required with skip (unless
    dry_run), and any mismatch with the current Follow-ups refuses, so stale indices are never applied.
    Numbered mode archives a NNNN-<slug> folder: after writing, rename it to .NNNN-<slug>, then the roadmap.
    With no filer here, the refusal names every other worktree's same-relative <slug>/ holding a filer-L*.md
    (glob only, never read), so work filed in a lane worktree can be committed or copied in.
    ack_warnings (not None): pass the open-warnings gate with a recorded reason instead of force; the write
    appends a ## Closed section with the date, `warnings acknowledged: <why>` and the Warnings quoted with `> `.
    It refuses with force, with reason, when empty, and when the filer's Warnings is None.
    Before archiving, outside_refs lists files outside the folder that reference it, as the literal <rel>/<slug>
    (ending at `/`, the end of a token, or punctuation, never running on into a longer folder name) or as a path token resolving to it relative to the citing file, from the toplevel, or absolute: with hits,
    close refuses unless rewrite_refs (rewrite_files turns each reference into the .<slug> form, keeping its
    relative or absolute form, with the rename; the dry run lists `rewrite <file>`) or force (close and leave
    them). keep_refs leaves them too without force, and records the stale citations in a ## Closed section.
    Plain slug folders never move, so never scan.
    A criterion still held (steps.open_items: a verifier reported it unmet-dependency or deferred and no later result
    passed it) refuses every close, --reason and --force included; nothing is written (T-0408).
    After a successful close, one `lane still open: <path> (branch <b>, <reason>)` line per plugin lane that lists the
    ticket (lanes.still_open) follows the result line; the exit code is unchanged (T-0453)."""
    if keep_refs and rewrite_refs:
        raise Fail(f'{slug}: --keep-refs leaves citations as they are and --rewrite-refs rewrites them, so they '
                   f'do not combine; use one; nothing written')
    if ack_warnings is not None and force:
        raise Fail(f'{slug}: --ack-warnings records why open warnings no longer apply, so it does not combine '
                   f'with --force; use one; nothing written')
    if ack_warnings is not None and reason is not None:
        raise Fail(f'{slug}: --ack-warnings closes through the filer and --reason skips it, so they do not '
                   f'combine; use one; nothing written')
    if ack_warnings is not None and not ack_warnings.strip():
        raise Fail(f'{slug}: empty --ack-warnings; give the reason the open warnings no longer apply; '
                   f'nothing written')
    if reason is not None and (dry_run or skip is not None or expect is not None or ticket is not None):
        raise Fail(f'{slug}: --reason files no follow-ups, so it does not combine with --dry-run, --skip, '
                   f'--expect or --ticket; '
                   f'nothing written')
    td = layout_paths(root).tickets
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    d = td / slug
    h = d / 'handoff.md'
    dot = td / ('.' + slug)
    archive = bool(numbered and PREFIX_RE.match(slug))
    final = dot.name if archive else slug
    if not h.is_file() and (dot / 'handoff.md').is_file():
        raise Fail(f'{slug}: already closed (folder {dot.name}); nothing written')
    raw = h.read_bytes().decode('utf-8') if h.is_file() else None
    meta = parse(raw) if raw is not None else None
    if meta is None:
        raise Fail(f'{h}: missing or has no front matter, so it is not a ticket; nothing written')
    if archive and dot.exists():
        raise Fail(f'{slug}: close would rename it to {dot.name}, but {dot} already exists; nothing written')
    ts = load(td)
    errs = problems(ts, numbered, areas=config_areas(root)) + strays(root)
    if errs:
        raise Fail('\n'.join(errs + ['refusing to close: fix the problems above first']))
    router_preflight(root)
    pid = meta['id']
    if meta['status'] == 'done':
        raise Fail(f'{slug}: {pid} is already closed (status: done); a second close would file duplicate '
                   f'follow-ups; nothing written')
    import steps  # local like messages: only close needs the verifier's held criteria (T-0408)
    held = steps.open_items(d, root)
    if held:
        raise Fail(f'{slug}: criteria still held: '
                   + ', '.join(f"{i['ref']} {i['state']} {i['who']}" for i in held)
                   + '; settle them in the owner stage; nothing written')
    got = skip_missing(d)
    docs_base = docs_waiver(d) if got and any(m.startswith('verifier') for m in got[1]) else None
    if docs_base:  # T-0429: a docs, records and reports only diff closes on its own checks; the guard below still counts planner and filer
        got = skip_missing(d, covered=('verifier',))

    def note_docs_waiver():
        if docs_base:
            add_skip_line(d / 'skips.md', f'- skip: verifier; step: all; reason: docs-only diff against {docs_base[:12]} '
                                          f'(verify_scope.py); decided: tickets.py close')
    if got:
        raise Fail(f'{skip_line(slug, got)}; add one "- skip: <role>; step: <n or all>; reason: <why>; '
                   f'decided: <who>" line per role under ## Skipped in {d / "skips.md"}; nothing written')
    top, old_ref, new_ref, refs = (outside_refs(td, slug, roadmap=layout_paths(root).roadmap) if archive
                                   else (None, '', '', []))
    if refs and not rewrite_refs and not force and not keep_refs:
        via_force = (f' or --keep-refs (close, leave them and record them in the close note)'
                     + ('' if ack_warnings is not None else ' or --force (close anyway, leaving them)'))
        raise Fail(f'{slug}: close renames it to {dot.name}, but these files outside it reference {old_ref}:\n'
                   + ''.join(f'  {f}\n' for f in refs)
                   + f'rerun with --rewrite-refs (rewrite them to {new_ref}){via_force}; nothing written')
    rewrite = refs if rewrite_refs else []

    kept = (f'{datetime.date.today().isoformat()}: kept stale refs to {old_ref} in: ' + ', '.join(refs)
            if keep_refs and refs else '')

    def rewrite_now():
        rewrite_files(top, rewrite, old_ref, new_ref)
        if rewrite:
            return f'; rewrote refs in {", ".join(rewrite)}'
        return f'; left refs to {old_ref} in {", ".join(refs)}' if refs else ''
    fm = re.match(r'---\r?\n.*?^---[ \t]*\r?$', raw, re.S | re.M)
    head, n = re.subn(r'^([ \t]*status[ \t]*:[ \t]*)[^\s#]+', r'\g<1>done', raw[:fm.end()], count=1, flags=re.M)
    head = normalize_size_text(head)[0]
    if reason is not None:
        why = reason.strip()
        if not why:
            raise Fail(f'{slug}: empty --reason; give the reason the ticket is closed; nothing written')
        if not n:
            raise Fail(f'{h}: no status: line in front matter; nothing written')
        body = raw[fm.end():]
        if body and not body.endswith('\n'):
            body += '\n'
        body += f'\n## Closed\n\n{datetime.date.today().isoformat()}: {why}\n'
        if kept:
            body += f'\n{kept}\n'
        note_docs_waiver()
        h.write_bytes((head + body).encode('utf-8'))
        if archive:
            d.rename(dot)
        rewrote = rewrite_now()
        write_roadmap(root, load(td))
        if flag:
            ensure_numbered_config(root)
        moved = f'; moved to {dot.name}' if archive else ''
        return f'{pid} done (closed by reason: {why}); no follow-ups filed{moved}{rewrote}' + lane_report(root, pid)
    filers = [pathlib.Path(p) for p in run_order.ordered(d, 'filer')]
    if not filers:
        held = []
        for _, r in other_ticket_dirs(root):
            try:
                if any((r / d.name).glob('filer-L*.md')):
                    held.append(str(r / d.name))
            except OSError:
                pass
        hint = (f'; a filer record exists in {", ".join(held)}; commit or copy it into this tree, then rerun close'
                if held else '')
        raise Fail(f'{slug}: no filer-L*.md in {d}; run /file on the task first{hint}; nothing written')
    filer = filers[-1]
    text = filer.read_text(encoding='utf-8')
    warnings, follow = section(text, 'Warnings'), section(text, 'Follow-ups')
    if warnings is None or follow is None:
        raise Fail(f'{filer}: missing a ## Warnings or ## Follow-ups section; nothing written')
    if ack_warnings is not None and is_none(warnings):
        raise Fail(f'{slug}: no open warnings to acknowledge in {filer.name}; rerun without --ack-warnings; '
                   f'nothing written')
    if not is_none(warnings) and not force and ack_warnings is None:
        raise Fail(f'{slug}: filer warnings are open, not closing (rerun with --ack-warnings "<why>" to record '
                   f'why they no longer apply, or --force to override):\n{warnings}')
    items = [] if is_none(follow) else bullets(follow)
    if not is_none(follow) and not items:
        raise Fail(f'{filer}: Follow-ups is prose with no top-level bullet (-, *, 1.), so its items cannot be '
                   f'filed; rewrite it as a list or "None"; nothing written:\n{follow}')
    digest = follow_digest(items)
    if skip is not None and not dry_run and expect is None:
        raise Fail(f'{slug}: --skip needs --expect <digest> from the dry run that listed the indices '
                   f'(run close --dry-run first); nothing written')
    if ticket is not None and not dry_run and expect is None:
        raise Fail(f'{slug}: --ticket needs --expect <digest> from the dry run that listed the indices '
                   f'(run close --dry-run first); nothing written')
    if expect is not None and expect.strip() != digest:
        raise Fail(f'{slug}: --expect {expect} does not match the current Follow-ups in {filer.name} '
                   f'(digest {digest}); the list changed since the dry run, so the --skip indices may point '
                   f'at other items; rerun close --dry-run; nothing written')
    skipped = sorted(set(skip or ()))
    for i in skipped:
        if not 1 <= i <= len(items):
            raise Fail(f'{slug}: --skip {i} is out of range: Follow-ups has {len(items)} item(s)'
                       + (f', so indices run 1 to {len(items)}' if items else '') + '; nothing written')

    if ticket is not None:
        if not 1 <= ticket <= len(items):
            raise Fail(f'{slug}: --ticket {ticket} is out of range: Follow-ups has {len(items)} item(s)'
                       + (f', so indices run 1 to {len(items)}' if items else '') + '; nothing written')
        if ticket in skipped:
            raise Fail(f'{slug}: --ticket {ticket} is also in --skip; pick one; nothing written')
        tag = follow_tag(items[ticket - 1])[0]
        if tag != 'decide':
            raise Fail(f'{slug}: --ticket {ticket} is a {tag}: item; only a decide: item can become a ticket; '
                       f'nothing written')

    # the other tickets to check each follow-up against (never the one being closed):
    # (normalized title, folder without NNNN-, id, folder)
    known = [(norm_title(m['title']) if isinstance(m.get('title'), str) else '', strip_prefix(x), m['id'], x)
             for x, m in ts if m.get('id') != pid and x != slug]
    # ids stay above every other worktree's max
    floor = id_floor(root)
    # plan everything first, so a refusal in the middle writes nothing
    planned, notes, lines, dups = [], [], [], []
    for i, item in enumerate(items, 1):
        tag, text = follow_tag(item)
        no_emphasis = re.sub(r'(?<!\w)_{1,2}(\S.*?\S|\S)_{1,2}(?!\w)', r'\1', text)
        plain = ' '.join(re.sub(r'[`*\[\]()]', '', no_emphasis).split())
        title = follow_up_title(plain)
        base = '-'.join(re.findall(r'[a-z0-9]+', plain.lower())[:5]) or 'follow-up'
        if numbered:
            base = strip_prefix(base) or 'follow-up'
        if i in skipped:
            lines.append(f'{i}. {tag}: {title} [{base}] skip (--skip)')
            continue
        key, nt = strip_prefix(base), norm_title(title)
        dup = next(((kid, kname) for kt, kbase, kid, kname in known if (nt and kt == nt) or kbase == key), None)
        if dup:
            if i == ticket:
                raise Fail(f'{slug}: --ticket {ticket} ({title}) is already tracked by {dup[0]} ({dup[1]}); '
                           f'nothing written')
            mark = f'duplicate of {dup[0]} ({dup[1]})'
            dups.append(f'{title} ({mark})')
            lines.append(f'{i}. {tag}: {title} [{base}] {mark}')
            continue
        if i != ticket:
            notes.append((tag, text))
            lines.append(f'{i}. {tag}: {title} note')
            continue
        tid = f'T-{max(max((int(x["id"][2:]) for _, x in ts), default=0), floor) + 1:04d}'
        s, k = base, 2
        while (td / (name := folder_name(s, tid, numbered))).exists() or any(x == name for x, _ in ts):
            s, k = f'{base}-{k}', k + 1
        ctx = f'Follow-up from {pid} ({final}/{filer.name}):\n\n{text}'
        t, _ = stamp(root, ts, 'idea', s, title, origin=pid, context=ctx, numbered=numbered, floor=floor)
        planned.append((name, t))
        lines.append(f'{i}. {tag}: {title} [{name}] ticket')
    if not n:
        raise Fail(f'{h}: no status: line in front matter; nothing written')
    if dry_run:
        opens = [f'open {m["id"]} {m.get("title", "")} [{x}]'
                 for x, m in sorted(ts, key=lambda e: e[1]['id'])
                 if m.get('status') in ACTIVE and m['id'] != pid]
        local_ids = {m.get('id') for _, m in ts}
        seen = {}
        for wdir, r in other_ticket_dirs(root):
            try:
                ots = load(r)
            except (OSError, UnicodeDecodeError):
                continue
            for x, m in ots:
                i = m.get('id')
                if (not isinstance(i, str) or not ID_RE.fullmatch(i) or i in local_ids or i == pid or i in seen
                        or m.get('status') not in ACTIVE):
                    continue
                seen[i] = f'open {i} {m.get("title", "")} [{x}] (worktree {wdir.name})'
        other_opens = [seen[i] for i in sorted(seen)]
        return '\n'.join([f'{pid} dry run: {len(items)} proposed follow-up(s); nothing written'] + lines + opens
                         + other_opens
                         + ([f'rename {slug} -> {dot.name}'] if archive else [])
                         + ([f'ack warnings: {ack_warnings.strip()}'] if ack_warnings is not None else [])
                         + [f'rewrite {f}' for f in rewrite]
                         + ([f'keep {f}' for f in refs] if keep_refs else [])
                         + [f'expect {digest}'])

    note_docs_waiver()
    for s, t in planned:
        (td / s).mkdir()
        (td / s / 'handoff.md').write_text(t, encoding='utf-8')
    if notes:
        append_notes(root, pid, meta.get('title') or slug, notes)
    body = raw[fm.end():]
    if ack_warnings is not None:
        if body and not body.endswith('\n'):
            body += '\n'
        quoted = '\n'.join(f'> {ln}' if ln.strip() else '>' for ln in warnings.splitlines())
        body += (f'\n## Closed\n\n{datetime.date.today().isoformat()}: warnings acknowledged: '
                 f'{ack_warnings.strip()}\n\n{quoted}\n')
    if kept:
        if body and not body.endswith('\n'):
            body += '\n'
        body += (f'\n{kept}\n' if '\n## Closed\n' in body else f'\n## Closed\n\n{kept}\n')
    h.write_bytes((head + body).encode('utf-8'))
    if archive:
        d.rename(dot)
    rewrote = rewrite_now()
    write_roadmap(root, load(td))
    if flag:
        ensure_numbered_config(root)
    out = (f'{pid} done; follow-up ticket: ' + (', '.join(s for s, _ in planned) or 'none')
           + f'; {len(notes)} follow-up(s) appended to notes.md')
    if dups:
        out += '; skipped duplicate(s): ' + ', '.join(dups)
    if skipped:
        out += '; skipped by --skip: ' + ', '.join(map(str, skipped))
    if archive:
        out += f'; moved to {dot.name}'
    if ack_warnings is not None:
        out += f'; warnings acknowledged: {ack_warnings.strip()}'
    return out + rewrote + lane_report(root, pid)


def cmd_roadmap(root, numbered=False):
    td = layout_paths(root).tickets
    numbered = numbered or config_numbered(root)
    ts = load(td)
    errs = problems(ts, numbered, areas=config_areas(root)) + strays(root)
    if errs:
        raise Fail('\n'.join(errs + ['roadmap not written: fix the problems above first']))
    router_preflight(root)
    root.mkdir(parents=True, exist_ok=True)
    return f'wrote {write_roadmap(root, ts)}'


def cmd_check(root, numbered=False):
    td = layout_paths(root).tickets
    numbered = numbered or config_numbered(root)
    ts = load(td)
    errs = problems(ts, numbered, areas=config_areas(root)) + strays(root) + root_strays(root)
    if errs:
        raise Fail('\n'.join(errs))
    if stale(root, ts):
        raise Fail(f'roadmap.md: stale or missing, run tickets.py --root {root} roadmap')
    errs = router_problems(root, ts)
    if errs:
        raise Fail('\n'.join(errs))
    errs = skip_problems(td, ts)
    if errs:
        raise Fail('\n'.join(errs))
    out = [f'ok: {len(ts)} tickets, roadmap current']
    out += placeholder_problems(root, td, ts)
    if not numbered and ts and all(PREFIX_RE.match(slug) or DOT_RE.fullmatch(slug) for slug, _ in ts):
        out.append(f"warning: every ticket folder has an NNNN- prefix but {root}/config lacks "
                   f"'ticket_folders: numbered'; add that line (or run new/close --numbered once) to enforce it")
    out += [f'warning: external_branch {b} is not a local branch'
            for b in unknown_branches(root, external_branches(root))]
    if layout_paths(root).layout == 'flat' and not layout_lines(root):
        out.append(f"warning: {root} uses the flat layout; tickets.py migrate-layout moves it to topic folders "
                   f"(add 'layout: flat' to {root}/config to keep it and silence this)")
    return '\n'.join(out)


def cmd_archive(root, numbered=False, dry_run=False, rewrite_refs=False, force=False):
    td = layout_paths(root).tickets
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not numbered:
        raise Fail(f'archive renames NNNN-<slug> folders and needs numbered mode (--numbered or '
                   f'ticket_folders: numbered in {root}/config); nothing written')
    ts = load(td)
    errs = problems(ts, numbered, areas=config_areas(root)) + strays(root)
    if errs:
        raise Fail('\n'.join(errs + ['nothing written: fix the problems above first']))
    router_preflight(root)
    names = [name for name, m in ts if PREFIX_RE.match(name) and not name.startswith('.')
             and m.get('status') in ('done', 'dropped')]
    taken = [f'.{n}' for n in names if (td / f'.{n}').exists()]
    if taken:
        raise Fail(f'archive: {", ".join(taken)} already exist(s); nothing written')
    hits = [(name, top, old, new, files) for name in names
            for top, old, new, files in [outside_refs(td, name, roadmap=layout_paths(root).roadmap)] if files]
    if hits and not rewrite_refs and not force:
        raise Fail('archive would rename these folders, but other files reference them:\n'
                   + ''.join(f'{old}:\n' + ''.join(f'  {f}\n' for f in files) for _, _, old, _, files in hits)
                   + 'rerun with --rewrite-refs (rewrite them to the dot form) or --force (archive anyway, '
                     'leaving them); nothing written')
    rewrite = sorted({f for *_, files in hits for f in files}) if rewrite_refs else []
    if dry_run:
        if not names:
            return 'nothing to archive'
        return '\n'.join([f'{n} -> .{n}' for n in names] + [f'rewrite {f}' for f in rewrite])
    if not names:
        return 'nothing to archive'
    if rewrite_refs:
        for _, top, old, new, files in hits:
            rewrite_files(top, files, old, new)
    for n in names:
        (td / n).rename(td / f'.{n}')
    write_roadmap(root, load(td))
    if flag:
        ensure_numbered_config(root)
    rewrote = f'; rewrote refs in {", ".join(rewrite)}' if rewrite else ''
    return f'archived {len(names)} folder(s): ' + ', '.join(f'{n} -> .{n}' for n in names) + rewrote


def cmd_migrate_size(root, apply=False):
    """Rewrite every ticket's alias `size:` (SIZE_ALIASES) to its level (L1 to L4) in the front matter of each
    <ticket root>/<dir>/handoff.md (closed .NNNN-<slug> folders too) and each <root>/_templates/*.md. A dry run
    (the default) lists `<path>: size <old> -> <new>` and writes nothing; apply writes them and regenerates the
    roadmap. Only the size line (and the template's alias comment on it) changes."""
    td = layout_paths(root).tickets
    files = [td / slug / 'handoff.md' for slug, _ in load(td)]
    tpl = pathlib.Path(root) / '_templates'
    if tpl.is_dir():
        files += sorted(tpl.glob('*.md'))
    lines, changed = [], []
    for f in files:
        raw = f.read_bytes().decode('utf-8', 'surrogateescape')
        new, old, lvl = normalize_size_text(raw)
        if old is None:
            continue
        rel = f.relative_to(root) if f.is_relative_to(root) else f
        lines.append(f'{rel.as_posix()}: size {old} -> {lvl}')
        changed.append((f, new))
    if not changed:
        return 'migrate-size: every size is already a level (L1 to L5); nothing to do'
    if not apply:
        return '\n'.join(lines + [f'migrate-size: dry run, {len(changed)} file(s) would change; rerun with --apply'])
    for f, new in changed:
        f.write_bytes(new.encode('utf-8', 'surrogateescape'))
    if td.is_dir():
        write_roadmap(root, load(td))
    return '\n'.join(lines + [f'migrate-size: rewrote {len(changed)} file(s)'])


def cmd_number(root, dry_run=False):
    """Convert a plain-slug ticket root to numbered mode: rename each <slug> ticket folder to NNNN-<slug> after
    its own id, rewrite every cite of <rel>/<slug> (the literal, or a path token that resolves to the folder,
    including files inside the folder itself) to <rel>/NNNN-<slug>, persist `ticket_folders: numbered`, and
    regenerate the roadmap. Refuses, writing nothing, on a bad ticket, a ticket whose id is not T-NNNN, or an
    existing target folder. Done and dropped folders get NNNN- too; `archive --rewrite-refs` hides them after.
    With `ticket_root: tickets` the folders are under <root>/tickets; config and roadmap.md stay at <root>."""
    td = layout_paths(root).tickets
    ts = load(td)
    errs = problems(ts, areas=config_areas(root)) + strays(root)
    if errs:
        raise Fail('\n'.join(errs + ['nothing written: fix the problems above first']))
    router_preflight(root)
    plain = [(n, m) for n, m in ts if not n.startswith('.') and not PREFIX_RE.match(n)]
    bad = [n for n, m in plain if not re.fullmatch(r'T-\d{4}', str(m.get('id', '')))]
    if bad:
        raise Fail(f'number: no T-NNNN id in {", ".join(bad)}; nothing written')
    moves = [(n, folder_name(n, m['id'], True)) for n, m in plain]
    taken = [new for _, new in moves if (td / new).exists() or (td / f'.{new}').exists()]
    if taken:
        raise Fail(f'number: {", ".join(taken)} already exist(s); nothing written')
    hits = []
    for n, new in moves:
        top, old, _, files = outside_refs(td, n, own=True, roadmap=layout_paths(root).roadmap)
        if files:
            hits.append((n, new, top, old, old.rsplit('/', 1)[0] + '/' + new if '/' in old else new, files))
    rewrite = sorted({f for *_, files in hits for f in files})
    if dry_run:
        if not moves:
            return 'nothing to number'
        return '\n'.join([f'{n} -> {new}' for n, new in moves] + [f'rewrite {f}' for f in rewrite])
    for n, new, top, old, dest, files in hits:
        rewrite_files(top, files, old, dest)
    for n, new in moves:
        (td / n).rename(td / new)
    ensure_numbered_config(root)
    write_roadmap(root, load(td))
    if not moves:
        return 'nothing to number; numbered mode on'
    rewrote = f'; rewrote refs in {len(rewrite)} file(s)' if rewrite else ''
    return (f'numbered {len(moves)} folder(s){rewrote}; run `archive --rewrite-refs` to hide done and dropped '
            'ones')


def cmd_migrate_layout(root, dry_run=False, rewrite_refs=False):
    """Move a flat root to the topics layout: ticket folders directly under <root> (load's rule, or a .NNNN-<slug>
    name) to tickets/<name>, every other non-allowed dir to work/<name>, roadmap.md to tickets/roadmap.md and
    notes.md to notes/notes.md; rewrite the files that cite a moved path (migrate_text) with --rewrite-refs, else
    refuse naming them; files under docs/reports/ are dated records and stay; then set `ticket_root: tickets` and
    `layout: topics` in config, regenerate the roadmap, routers and mailbox entries, and run check. Refuses, writing
    nothing, on a bad config, outside git, on a dirty work tree, on a bad ticket or malformed router block, on a
    loose file at the root, or when a move target exists. --dry-run prints the move, rewrite, keep and config lines
    and writes nothing."""
    lp = layout_paths(root)
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
    here = root.resolve()
    anchor = here
    while not anchor.is_dir() and anchor != anchor.parent:
        anchor = anchor.parent
    try:
        p = subprocess.run(['git', '-C', str(anchor), 'rev-parse', '--show-toplevel'], env=env,
                           capture_output=True, text=True)
        top = pathlib.Path(p.stdout.strip()).resolve() if p.returncode == 0 else None
        rel = here.relative_to(top) if top else None
    except (OSError, ValueError):
        top = None
    if top is None:
        raise Fail(f'migrate-layout: {root} is not inside a git work tree; the cite scan needs git to find the files '
                   f'that cite the moved paths; nothing written')
    p = subprocess.run(['git', '-C', str(top), 'status', '--porcelain'], env=env, capture_output=True, text=True)
    if p.returncode:
        raise Fail(f'migrate-layout: git status failed: {p.stderr.strip()}; nothing written')
    dirty = p.stdout.splitlines()
    if dirty:
        raise Fail('migrate-layout: the work tree has uncommitted changes; commit or stash them first:\n'
                   + ''.join(f'  {x}\n' for x in dirty[:10]) + ('  ...\n' if len(dirty) > 10 else '')
                   + 'nothing written')
    td = lp.tickets
    at_root = [(n, m) for n, m in load(root) if n not in ROOT_ALLOWED]
    ts = sorted((load(td) if td != root else []) + at_root)
    errs = problems(ts, config_numbered(root), areas=config_areas(root))
    if errs:
        raise Fail('\n'.join(errs + ['nothing written: fix the problems above first']))
    router_preflight(root)
    entries = sorted(root.iterdir()) if root.is_dir() else []
    loose = [e.name for e in entries if not e.is_dir() and e.name not in ROOT_ALLOWED
             and not e.name.startswith(('_', '.')) and e.name not in ('roadmap.md', 'notes.md')]
    if loose:
        raise Fail('migrate-layout: these files at the root have no topic folder; move each into tickets/, work/ or '
                   'notes/ (or remove it), commit, and rerun:\n' + ''.join(f'  {n}\n' for n in loose)
                   + 'nothing written')
    tickets = {n for n, _ in at_root}
    moves = []
    for e in entries:
        n = e.name
        if e.is_dir() and (n in tickets or DOT_RE.fullmatch(n)):
            moves.append((n, f'tickets/{n}'))
        elif e.is_dir() and n not in ROOT_ALLOWED and not n.startswith(('_', '.')):
            moves.append((n, f'work/{n}'))
        elif n == 'roadmap.md' and e.is_file():
            moves.append((n, 'tickets/roadmap.md'))
        elif n == 'notes.md' and e.is_file():
            moves.append((n, 'notes/notes.md'))
    taken = [dst for _, dst in moves if (root / dst).exists() or (root / dst).is_symlink()]
    if taken:
        raise Fail(f'migrate-layout: {", ".join(taken)} already exist(s); nothing written')
    config = ensure_topics_config(root, write=False)
    if not moves and not config:
        return 'nothing to migrate\n' + cmd_check(root)
    tmoves = [((rel / s).as_posix(), (rel / d).as_posix()) for s, d in moves]
    old_roadmap = (rel / 'roadmap.md').as_posix()
    cands = set()
    for s, _ in moves:
        t, _, _, files = outside_refs(root, s, own=True, roadmap=root / 'roadmap.md')
        if t is None:
            raise Fail('migrate-layout: cite scan failed (git grep); nothing written')
        cands.update(files)
    if moves:
        p = subprocess.run(['git', '-C', str(top), 'grep', '--untracked', '--no-exclude-standard', '-I', '-l', '-z',
                            '--full-name', '-F', '-e', '../', '--', *(s for s, _ in tmoves)], env=env,
                           capture_output=True, text=True)
        if p.returncode not in (0, 1):
            raise Fail(f'migrate-layout: cite scan failed (git grep): {p.stderr.strip()}; nothing written')
        cands.update(f for f in p.stdout.split('\0') if f)
    cands.discard(old_roadmap)
    rewrites, keeps, unreadable = {}, [], []
    for f in sorted(cands):
        try:
            text = (top / f).read_bytes().decode('utf-8', 'surrogateescape')
        except OSError:
            unreadable.append(f)
            continue
        new = migrate_text(text, top, f, tmoves)
        if new == text:
            continue
        if f.startswith('docs/reports/'):
            keeps.append(f)
        else:
            rewrites[f] = new
    if unreadable:
        raise Fail('migrate-layout: cannot read these files to scan them for cites:\n'
                   + ''.join(f'  {f}\n' for f in unreadable) + 'nothing written')
    if rewrites and not rewrite_refs:
        raise Fail('migrate-layout would move these paths, but other files cite them:\n'
                   + ''.join(f'  {f}\n' for f in sorted(rewrites))
                   + 'rerun with --rewrite-refs (rewrite them to the new paths); nothing written')
    lines = ([f'move {s} -> {d}' for s, d in moves]
             + [f'rewrite {f}' if f in rewrites else f'keep {f} (dated record under docs/reports/)'
                for f in sorted(list(rewrites) + keeps)]
             + [f'config {x}' for x in config])
    if dry_run:
        return '\n'.join(lines)
    for f, new in rewrites.items():
        (top / f).write_bytes(new.encode('utf-8', 'surrogateescape'))
    for s, d in moves:
        (root / d).parent.mkdir(parents=True, exist_ok=True)
        (root / s).rename(root / d)
    ensure_topics_config(root)
    write_roadmap(root, load(layout_paths(root).tickets))
    try:
        checked = cmd_check(root)
    except Fail as e:
        raise Fail(f'migrated, but check failed:\n{e}')
    return '\n'.join(lines + [checked])


def run(root, cmd, args=(), **kw):
    """(exit code, stdout, stderr). The CLI and the selftest both go through here.
    kw goes to new, close, roadmap, check and archive (numbered=)."""
    try:
        if cmd == 'new':
            return 0, cmd_new(root, *args, **kw), ''
        if cmd == 'close':
            return 0, cmd_close(root, *args, **kw), ''
        if cmd == 'roadmap':
            return 0, cmd_roadmap(root, **kw), ''
        if cmd == 'check':
            return 0, cmd_check(root, **kw), ''
        if cmd == 'archive':
            return 0, cmd_archive(root, **kw), ''
        if cmd == 'number':
            return 0, cmd_number(root, **kw), ''
        if cmd == 'migrate-layout':
            return 0, cmd_migrate_layout(root, **kw), ''
        if cmd == 'migrate-size':
            return 0, cmd_migrate_size(root, **kw), ''
        raise Fail(f'unknown command {cmd!r}')
    except Fail as e:
        return 1, '', str(e)


# ---------- selftest ----------

def selftest():
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def edit(root, slug, pattern, repl):
        h = root / slug / 'handoff.md'
        old = h.read_text(encoding='utf-8')
        new = re.sub(pattern, repl, old, count=1, flags=re.M)
        if new == old:
            raise AssertionError(f'selftest mutation did not apply: {slug} {pattern!r}')
        h.write_text(new, encoding='utf-8')

    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp) / 'base' / '.sdlc'
        rc_a, out_a, err_a = run(base, 'new', ('feature', 'alpha', 'Alpha | one'))
        rc_b, out_b, err_b = run(base, 'new', ('bug', 'beta', 'Fix #12'))
        expect(f'new alpha: rc={rc_a} {err_a}', rc_a == 0 and out_a.endswith('alpha/handoff.md'))
        expect(f'new beta: rc={rc_b} {err_b}', rc_b == 0)
        ids = {s: m.get('id') for s, m in load(base)}
        expect(f'ids T-0001 then T-0002, got {ids}', ids == {'alpha': 'T-0001', 'beta': 'T-0002'})
        expect('quoted title keeps "#"', dict(load(base)).get('beta', {}).get('title') == 'Fix #12')
        edit(base, 'alpha', r'^depends:.*$', 'depends: [T-0002]')
        rc, _, err = run(base, 'check')
        expect(f'edited depends makes roadmap stale: rc={rc} {err}', rc == 1 and 'stale' in err)
        run(base, 'roadmap')
        first = (base / 'roadmap.md').read_bytes()
        run(base, 'roadmap')
        expect('roadmap is byte-stable across runs', (base / 'roadmap.md').read_bytes() == first)
        rm = first.decode('utf-8')
        expect('T-0002 row before T-0001 row', 0 <= rm.find('| T-0002 |') < rm.find('| T-0001 |'))
        expect('"|" in title escaped', 'Alpha \\| one' in rm)
        rc, out, err = run(base, 'check')
        expect(f'clean base passes check: rc={rc} {err}',
               rc == 0 and out.splitlines()[0] == 'ok: 2 tickets, roadmap current'
               and out.splitlines()[1:] == [f"warning: {base} uses the flat layout; tickets.py migrate-layout moves it "
                                            f"to topic folders (add 'layout: flat' to {base}/config to keep it and "
                                            f"silence this)"])

        before = (base / 'alpha' / 'handoff.md').read_bytes()
        rc, _, err = run(base, 'new', ('idea', 'alpha'))
        expect('new on an existing slug refuses and writes nothing',
               rc == 1 and (base / 'alpha' / 'handoff.md').read_bytes() == before)
        rc, _, err = run(base, 'new', ('epic', 'gamma'))
        expect(f'new with an unknown type lists the types: {err}',
               rc == 1 and all(t in err for t in ENUMS['type']) and not (base / 'gamma').exists())
        rc, _, err = run(base, 'new', ('idea', 'Bad_Slug'))
        expect('new with a bad slug refuses', rc == 1 and not (base / 'Bad_Slug').exists())

        n = [0]

        def case(mutate):
            n[0] += 1
            root = pathlib.Path(tmp) / f'case{n[0]}' / '.sdlc'
            shutil.copytree(base, root)
            mutate(root)
            return root

        # negative control: a handoff with no front matter is not a ticket and not an error
        def plain(root):
            (root / 'plain').mkdir()
            (root / 'plain' / 'handoff.md').write_text('## Goal\nNo front matter here.\n', encoding='utf-8')
        rc, out, err = run(case(plain), 'check')
        expect(f'handoff without front matter still passes: rc={rc} {err}', rc == 0 and 'ok: 2 tickets' in out)

        def hand_edit(root):
            with (root / 'roadmap.md').open('a', encoding='utf-8') as f:
                f.write('hand edit\n')

        mutations = [
            ('bad type', lambda r: edit(r, 'alpha', r'^type:.*$', 'type: epic'), "type='epic'"),
            ('bad status', lambda r: edit(r, 'alpha', r'^status:.*$', 'status: wip'), "status='wip'"),
            ('bad size', lambda r: edit(r, 'alpha', r'^size:.*$', 'size: XXL'), "size='XXL'"),
            ('bad priority', lambda r: edit(r, 'alpha', r'^priority:.*$', 'priority: P0'), "priority='P0'"),
            ('missing field', lambda r: edit(r, 'alpha', r'^size:.*\n', ''), 'alpha: missing size'),
            ('partial front matter is one finding', lambda r: (r / 'alpha' / 'handoff.md').write_text(
                '---\nstatus: done\n---\n\n## Goal\nx\n', encoding='utf-8'),
             'alpha: missing id, title, type, size, priority, depends, created'),
            ('bad id', lambda r: edit(r, 'alpha', r'^id:.*$', 'id: T-12'), "alpha: id 'T-12' is not T-NNNN"),
            ('bad created', lambda r: edit(r, 'alpha', r'^created:.*$', 'created: 2026-9-1'),
             "alpha: created '2026-9-1' is not YYYY-MM-DD"),
            ('duplicate id', lambda r: edit(r, 'beta', r'^id:.*$', 'id: T-0001'),
             'beta: duplicate id T-0001, also used by alpha'),
            ('dangling depends', lambda r: edit(r, 'alpha', r'^depends:.*$', 'depends: [T-0099]'),
             'alpha: depends on T-0099'),
            ('dangling from', lambda r: edit(r, 'alpha', r'^created:(.*)$', r'created:\1\nfrom: T-0099'),
             'alpha: from T-0099'),
            ('cycle', lambda r: edit(r, 'beta', r'^depends:.*$', 'depends: [T-0001]'), 'cycle T-0001 -> T-0002 -> T-0001'),
            ('self-cycle', lambda r: edit(r, 'alpha', r'^depends:.*$', 'depends: [T-0001]'), 'cycle T-0001 -> T-0001'),
            ('stale roadmap', hand_edit, 'stale'),
        ]
        for label, mutate, want in mutations:
            rc, _, err = run(case(mutate), 'check')
            expect(f'{label}: check did not fail with {want!r} (rc={rc}, stderr={err!r})', rc == 1 and want in err)
        rc, _, err = run(case(mutations[0][1]), 'roadmap')
        expect('roadmap refuses on a bad ticket', rc == 1 and "type='epic'" in err)
        rc, _, err = run(case(mutations[0][1]), 'new', ('idea', 'delta'))
        expect('new refuses on a bad ticket', rc == 1 and "type='epic'" in err)

        # ---- file: and cap: depends entries; base: alpha T-0001 depends [T-0002], beta T-0002 depends [] ----
        def steps(*fs):
            def put(r):
                for f in fs:
                    f(r)
            return put

        def deps(slug, value):
            return lambda r: edit(r, slug, r'^depends:.*$', f'depends: [{value}]')

        def provides(slug, value):
            return lambda r: edit(r, slug, r'^created:(.*)$', rf'created:\1\nprovides: {value}')

        def status(slug, value):
            return lambda r: edit(r, slug, r'^status:.*$', f'status: {value}')

        def row(root, tid):
            rm = (root / 'roadmap.md').read_text(encoding='utf-8')
            return next((ln for ln in rm.splitlines() if ln.startswith(f'| {tid} |')), ''), rm

        root = case(steps(deps('alpha', 'cap:widget'), provides('beta', '[widget]'), status('beta', 'done')))
        rc_r, _, err_r = run(root, 'roadmap')
        rc, _, err = run(root, 'check')
        a, rm = row(root, 'T-0001')
        expect(f'cap: edge orders after its provider: rc={rc_r}/{rc} {err_r!r} {err!r} {rm!r}',
               rc_r == 0 and rc == 0 and '| cap:widget |' in a and 0 <= rm.find('| T-0002 |') < rm.find('| T-0001 |'))
        root = case(steps(deps('alpha', 'cap:widget'), provides('beta', '[widget]')))
        rc, _, err = run(root, 'roadmap')
        a, rm = row(root, 'T-0001')
        expect(f'cap: provided by an open ticket renders (unmet) and still orders: rc={rc} {err!r} {a!r}',
               rc == 0 and '| cap:widget (unmet) |' in a and 0 <= rm.find('| T-0002 |') < rm.find('| T-0001 |'))

        root = case(deps('alpha', 'file:src/present.txt'))
        (root.parent / 'src').mkdir()
        (root.parent / 'src' / 'present.txt').write_text('x\n', encoding='utf-8')
        rc_r, _, err_r = run(root, 'roadmap')
        rc, _, err = run(root, 'check')
        a, rm = row(root, 'T-0001')
        expect(f'file: entry that exists does not block: rc={rc_r}/{rc} {err_r!r} {err!r} {rm!r}',
               rc_r == 0 and rc == 0 and '| file:src/present.txt |' in a
               and 0 <= rm.find('| T-0001 |') < rm.find('| T-0002 |'))
        (root.parent / 'src' / 'present.txt').unlink()
        rc, _, err = run(root, 'check')
        expect(f'file: entry whose file vanished makes the roadmap stale: rc={rc} {err!r}', rc == 1 and 'stale' in err)
        root = case(deps('alpha', 'file:missing.txt, file:a|b'))
        rc_r, _, err_r = run(root, 'roadmap')
        rc, _, err = run(root, 'check')
        a, _ = row(root, 'T-0001')
        expect(f'file: entry that is missing renders (unmet) and passes check: rc={rc_r}/{rc} {err_r!r} {err!r} {a!r}',
               rc_r == 0 and rc == 0 and '| file:missing.txt (unmet), file:a\\|b (unmet) |' in a)

        for bad in ('bogus', 'file:/etc/hosts', 'file:../up.txt', 'file:src/../x', 'file:', 'cap:', 'cap:-x', 'T-12'):
            rc, _, err = run(case(deps('alpha', bad)), 'check')
            want = f"alpha: depends entry '{bad}' is not T-NNNN, file:<path> or cap:<name>"
            expect(f'malformed depends entry fails check: {bad!r} rc={rc} {err!r}', rc == 1 and want in err)
        rc, _, err = run(case(deps('alpha', 'cap:nobody')), 'check')
        expect(f'unprovided cap: fails check: rc={rc} {err!r}',
               rc == 1 and 'alpha: depends on cap:nobody, which no ticket provides' in err)
        rc, _, err = run(case(steps(deps('alpha', 'cap:widget'), deps('beta', 'T-0001'), provides('beta', '[widget]'))),
                         'check')
        expect(f'cap: cycle through a provider fails check: rc={rc} {err!r}',
               rc == 1 and 'dependency cycle T-0001 -> T-0002 -> T-0001' in err)
        rc, _, err = run(case(provides('beta', 'widget')), 'check')
        expect(f'non-list provides fails check: rc={rc} {err!r}',
               rc == 1 and "beta: provides 'widget' is not a list like [name]" in err)
        rc, _, err = run(case(provides('beta', '[-bad]')), 'check')
        expect(f'bad provides item fails check: rc={rc} {err!r}', rc == 1 and "beta: provides item '-bad'" in err)
        if shutil.which('git'):
            root = pathlib.Path(tmp) / 'gitcase' / 'proj' / '.sdlc'
            shutil.copytree(base, root)
            deps('alpha', 'file:src/top.txt')(root)
            genv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
            subprocess.run(['git', '-C', str(root.parent.parent), 'init', '-q'], env=genv, capture_output=True)
            (root.parent.parent / 'src').mkdir()
            (root.parent.parent / 'src' / 'top.txt').write_text('x\n', encoding='utf-8')
            rc, _, err = run(root, 'roadmap')
            a, _ = row(root, 'T-0001')
            expect(f'file: resolves against the git toplevel, not the root parent: rc={rc} {err!r} {a!r}',
                   rc == 0 and '| file:src/top.txt |' in a)

        def snap(root):
            return {p.relative_to(root): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}

        # ---- numbered folders: base holds T-0001 and T-0002, so the next id is T-0003 ----
        def tree(root):
            return sorted(p.name for p in root.iterdir())

        def config(text):
            def put(root):
                (root / 'config').write_text(text, encoding='utf-8')
            return put

        def both(*fs):
            def put(root):
                for f in fs:
                    f(root)
            return put

        def numbered_ok(label, root, rc, out, err, slug):
            ids = dict(load(root))
            got = ids.get(f'0003-{slug}', {}).get('id')
            expect(f'{label}: folder 0003-{slug} with id T-0003, rc={rc} out={out!r} err={err!r} '
                   f'tree={tree(root)} id={got!r}',
                   rc == 0 and out.endswith(f'0003-{slug}/handoff.md') and got == 'T-0003'
                   and not (root / slug).exists() and run(root, 'check')[0] == 0
                   and run(root, 'check', numbered=True)[0] == 0)

        root = case(lambda r: None)
        rc, out, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        numbered_ok('new --numbered', root, rc, out, err, 'gamma')

        # new --numbered persists `ticket_folders: numbered` in <root>/config, so plain check enforces it
        expect(f'new --numbered writes config with the numbered line: tree={tree(root)}',
               (root / 'config').is_file() and config_numbered(root))
        (root / '0003-gamma').rename(root / '0009-gamma')
        run(root, 'roadmap')
        rc, _, err = run(root, 'check')
        expect(f'after new --numbered, plain check fails a renamed 0009-gamma: rc={rc} {err!r}',
               rc == 1 and "0009-gamma: folder prefix 0009- does not match id 'T-0003'" in err)
        root = case(config('# keep me\nother: x\n'))
        rc, _, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        text = (root / 'config').read_text(encoding='utf-8') if (root / 'config').is_file() else ''
        expect(f'new --numbered keeps existing config lines and adds the numbered line once: {text!r}',
               rc == 0 and text.startswith('# keep me\nother: x\n')
               and len([ln for ln in text.splitlines() if CONFIG_RE.fullmatch(ln)]) == 1)
        for label, mutate in (('twice', lambda r: None), ('line present', config('ticket_folders: numbered\n'))):
            root = case(mutate)
            run(root, 'new', ('feature', 'gamma'), numbered=True)
            if label == 'twice':
                run(root, 'new', ('feature', 'delta'), numbered=True)
            text = (root / 'config').read_text(encoding='utf-8') if (root / 'config').is_file() else ''
            expect(f'new --numbered ({label}) leaves one ticket_folders: numbered line: {text!r}',
                   len([ln for ln in text.splitlines() if CONFIG_RE.fullmatch(ln)]) == 1)
        root = case(lambda r: None)
        rc, _, err = run(root, 'new', ('feature', 'gamma'))
        expect(f'plain new writes no config: rc={rc} tree={tree(root)}', rc == 0 and not (root / 'config').exists())

        root = case(config('# tickets\n\nticket_folders: numbered\n'))
        rc, out, err = run(root, 'new', ('feature', 'gamma'))
        numbered_ok('new with config ticket_folders: numbered', root, rc, out, err, 'gamma')

        # a slug already carrying NNNN- in numbered mode: refuses, names the double prefix, writes nothing
        for label, mutate, kw in (('flag', lambda r: None, {'numbered': True}),
                                  ('config', config('ticket_folders: numbered\n'), {})):
            root = case(mutate)
            before = snap(root)
            rc, _, err = run(root, 'new', ('feature', '0007-gamma'), **kw)
            expect(f'new 0007-gamma in numbered mode ({label}) refuses on the double prefix: rc={rc} {err!r}',
                   rc == 1 and 'double' in err and snap(root) == before)

        # an existing numbered folder with the final name refuses and writes nothing
        root = case(lambda r: (r / '0003-gamma').mkdir())
        before = snap(root)
        rc, _, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        expect(f'new --numbered onto an existing 0003-gamma refuses: rc={rc} {err!r}',
               rc == 1 and '0003-gamma' in err and snap(root) == before)

        # negative control: plain mode (no flag; config absent, or config saying anything else) is a bare slug
        for label, mutate in (('no config', lambda r: None),
                              ('other config', config('# ticket_folders: numbered\nticket_folders: plain\n'))):
            root = case(mutate)
            rc, out, err = run(root, 'new', ('feature', 'gamma'))
            expect(f'plain mode ({label}) new gives bare folder gamma: rc={rc} out={out!r} err={err!r} '
                   f'tree={tree(root)}',
                   rc == 0 and out.endswith('/gamma/handoff.md') and dict(load(root)).get('gamma', {}).get('id')
                   == 'T-0003' and not any(PREFIX_RE.match(n) for n in tree(root)))
        root = case(lambda r: None)
        rc, out, err = run(root, 'new', ('feature', '0007-gamma'))
        expect(f'plain mode still takes a digit-led slug as-is: rc={rc} {err!r}',
               rc == 0 and (root / '0007-gamma' / 'handoff.md').is_file())
        rc, _, err = run(root, 'check')
        rc_n, _, err_n = run(root, 'check', numbered=True)
        expect(f'digit-led plain slug: plain check passes, check --numbered names it: rc={rc} {err!r} '
               f'rc_n={rc_n} {err_n!r}', rc == 0 and rc_n == 1 and '0007-gamma' in err_n)

        # ---- NNNN-/id rule: numbered mode only; a rename makes the roadmap stale, so regenerate it ----
        def renamed(to):
            def put(root):
                (root / 'alpha').rename(root / to)
                run(root, 'roadmap')
            return put

        mismatch = "0005-alpha: folder prefix 0005- does not match id 'T-0001'"
        for label, mutate, kw in (('flag', renamed('0005-alpha'), {'numbered': True}),
                                  ('config', both(renamed('0005-alpha'), config('ticket_folders: numbered\n')), {})):
            rc, _, err = run(case(mutate), 'check', **kw)
            expect(f'prefix mismatch ({label}): rc={rc} {err!r}', rc == 1 and mismatch in err)
        rc, out, err = run(case(renamed('0005-alpha')), 'check')
        expect(f'prefix mismatch is not checked in plain mode: rc={rc} {out!r} {err!r}',
               rc == 0 and out.splitlines()[0] == 'ok: 2 tickets, roadmap current' and len(out.splitlines()) == 2
               and 'migrate-layout' in out and 'prefix' not in err)
        rc, _, err = run(case(renamed('0001-alpha')), 'check', numbered=True)
        expect(f'matching 0001-alpha passes check --numbered: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(case(lambda r: None), 'check', numbered=True)
        expect(f'plain slugs get no prefix error in numbered mode: rc={rc} {err!r}', rc == 0)

        # check warns (exit 0) when every folder is NNNN- but <root>/config lacks the numbered line
        def renamed_beta(root):
            (root / 'beta').rename(root / '0002-beta')
            run(root, 'roadmap')
        all_numbered = both(renamed('0001-alpha'), renamed_beta)
        rc, out, err = run(case(all_numbered), 'check')
        expect(f'all-numbered folders, no config: check warns and exits 0: rc={rc} {out!r} {err!r}',
               rc == 0 and out.startswith('ok: 2 tickets') and 'warning' in out and "ticket_folders: numbered" in out)
        for label, mutate in (('with config', both(all_numbered, config('ticket_folders: numbered\n'))),
                              ('plain slugs', lambda r: None),
                              ('mixed', renamed('0001-alpha'))):
            rc, out, err = run(case(mutate), 'check')
            expect(f'no numbered-config warning ({label}): rc={rc} {out!r} {err!r}',
                   rc == 0 and 'ticket_folders: numbered' not in out + err)
        rc, out, err = run(pathlib.Path(tmp) / 'empty-warn' / '.sdlc', 'check')
        expect(f'no numbered-config warning (empty root): rc={rc} {out!r}',
               rc == 0 and 'ticket_folders: numbered' not in out + err)
        # roadmap follows the same rule: numbered mode refuses on a mismatch and writes nothing
        for label, mutate, kw in (('flag', renamed('0005-alpha'), {'numbered': True}),
                                  ('config', both(renamed('0005-alpha'), config('ticket_folders: numbered\n')), {})):
            root = case(mutate)
            before = snap(root)
            rc, _, err = run(root, 'roadmap', **kw)
            expect(f'roadmap refuses on a prefix mismatch ({label}) and writes nothing: rc={rc} {err!r}',
                   rc == 1 and mismatch in err and 'roadmap not written' in err and snap(root) == before)
        rc, out, err = run(case(renamed('0005-alpha')), 'roadmap')
        expect(f'plain roadmap ignores a prefix mismatch: rc={rc} {out!r} {err!r}', rc == 0 and 'prefix' not in err)
        rc, _, err = run(case(renamed('0001-alpha')), 'roadmap', numbered=True)
        expect(f'matching 0001-alpha passes roadmap --numbered: rc={rc} {err!r}', rc == 0)
        root = case(both(renamed('0005-alpha'), config('ticket_folders: numbered\n')))
        before = snap(root)
        for cmd, args in (('new', ('feature', 'gamma')), ('close', ('beta',))):
            rc, _, err = run(root, cmd, args)
            expect(f'numbered {cmd} refuses on an existing prefix mismatch and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '0005-alpha: folder prefix' in err and 'fix the problems above first' in err
                   and snap(root) == before)
        root = case(renamed('0005-alpha'))
        rc, _, err = run(root, 'new', ('feature', 'gamma'))
        expect(f'plain new ignores an existing prefix mismatch: rc={rc} {err!r}',
               rc == 0 and (root / 'gamma' / 'handoff.md').is_file())

        # ---- close: each case in its own copy of base; alpha (T-0001) is the ticket being closed ----
        def filer(name, warnings, follow, mtime=None, slug='alpha'):
            def put(root):
                p = root / slug / name
                p.write_text(f'## Warnings\n{warnings}\n\n## PR title\nx\n\n## Follow-ups\n{follow}\n', encoding='utf-8')
                if mtime is not None:
                    os.utime(p, (mtime, mtime))
            return put

        def fresh(root, before):
            return {s: m for s, m in load(root) if s not in before}

        def status(root, slug='alpha'):
            return dict(load(root)).get(slug, {}).get('status')

        def close_one(root, i, slug='alpha', force=False, **kw):
            """The capped path: a dry run for the digest, then close --ticket i --expect <digest>."""
            rc, out, _ = run(root, 'close', (slug, force), dry_run=True, **kw)
            token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else 'none'
            return run(root, 'close', (slug, force), ticket=i, expect=token, **kw)

        def notes(root):
            p = root / 'notes.md'
            return p.read_text(encoding='utf-8') if p.is_file() else None

        notes_head = '# Notes\n\n`tickets.py close` appends follow-ups that did not become tickets.\n'
        today = datetime.date.today().isoformat()

        long_item = ('Split the runner into a preflight module and an exec module so the Fable swap can be '
                     'tested on its own')
        short_first_sentence_item = ('Optional id and status columns in board.py. T-0001 listed this as '
                                      'optional, and the plan left it out of scope.')
        underscore_item = '`follow_up_title` in tickets.py returns a mangled title with underscores stripped'
        good = filer('filer-L1.md', 'None', f'- Quote the `--root` flag in the docs\n'
                     f'- {long_item[:60]}\n  {long_item[60:]}\n'
                     f'- {short_first_sentence_item}\n'
                     f'- {underscore_item}')

        def with_body_status(root):
            with (root / 'alpha' / 'handoff.md').open('a', encoding='utf-8') as f:
                f.write('\nstatus: this body line is not front matter\n')

        # (a) Warnings None, four untagged bullets (so each counts as decide; one has a backtick, one is over
        # 70 chars wrapped onto a continuation line): close --ticket i files only item i and appends the other
        # three to notes.md as `- decide: <text>`; across i = 1..4 every title is checked
        made, ctx = {}, ''
        for i in range(1, 5):
            root = case(both(good, with_body_status))
            before_h = (root / 'alpha' / 'handoff.md').read_bytes()
            rc, out, err = close_one(root, i)
            one = fresh(root, {'alpha', 'beta'})
            nt = notes(root) or ''
            expect(f'(a) close --ticket {i}: one ticket, three notes: rc={rc} out={out!r} err={err!r} '
                   f'made={sorted(one)} notes={nt!r}',
                   rc == 0 and len(one) == 1
                   and out == f'T-0001 done; follow-up ticket: {next(iter(one), "")}; 3 follow-up(s) appended to notes.md'
                   and nt.startswith(notes_head) and nt.count('\n- decide: ') == 3)
            made.update(one)
            ctx += ''.join((root / s / 'handoff.md').read_text(encoding='utf-8') for s in one)
            if i == 1:
                expect('(a) parent done, rest byte-identical, body status line untouched',
                       (root / 'alpha' / 'handoff.md').read_bytes()
                       == before_h.replace(b'status: proposed', b'status: done', 1)
                       and b'status: this body line is not front matter' in before_h)
                rc, out, err = run(root, 'check')
                expect(f'(a) check passes after close: rc={rc} {err}', rc == 0 and 'ok: 3 tickets' in out)
        expect(f'(a) four idea/proposed tickets from T-0001, one per close, got {made}', len(made) == 4 and all(
            m.get('type') == 'idea' and m.get('status') == 'proposed' and m.get('from') == 'T-0001'
            for m in made.values()))
        titles = sorted(m.get('title', '') for m in made.values())
        expect(f'(a) titles clean and <= 70 chars: {titles}',
               all(len(t) <= 70 and '`' not in t for t in titles) and 'Quote the --root flag in the docs' in titles)
        expect(f'(a) short-first-sentence bullet title is the sentence without its final period: {titles}',
               'Optional id and status columns in board.py' in titles)
        expect(f'(a) underscore inside a word survives cleanup (not mangled to followuptitle): {titles}',
               any('follow_up_title' in t for t in titles) and not any('followuptitle' in t for t in titles))
        empty_first_sentence_title = follow_up_title('. ' + 'x' * 80)
        expect(f'(a) empty first sentence falls through to whole-word cut: {empty_first_sentence_title!r}',
               bool(empty_first_sentence_title) and not empty_first_sentence_title.startswith('.'))
        long_title = next((t for t in titles if t.endswith('...')), None)
        expect(f'(a) long_item title ends with ...: {titles}', long_title is not None)
        prefix = (long_title or '')[:-3]
        expect(f'(a) long_item title is a whole-word prefix of long_item, no trailing space/punct before ...: '
               f'{long_title!r}',
               long_item.startswith(prefix) and len(long_item) > len(prefix)
               and long_item[len(prefix)] == ' ' and prefix == prefix.rstrip()
               and (not prefix or prefix[-1] not in ',;:.-'))
        expect('(a) context names the source and keeps the joined continuation line',
               'Follow-up from T-0001 (alpha/filer-L1.md):' in ctx and long_item in ctx)
        # (a) plain close of the same filer: no ticket, all four bullets in notes.md under one dated block
        root = case(good)
        rc, out, err = run(root, 'close', ('alpha',))
        nt = notes(root) or ''
        expect(f'(a) plain close files no ticket and appends all four: rc={rc} out={out!r} err={err!r} notes={nt!r}',
               rc == 0 and not fresh(root, {'alpha', 'beta'}) and status(root) == 'done'
               and out == 'T-0001 done; follow-up ticket: none; 4 follow-up(s) appended to notes.md'
               and nt.startswith(notes_head + f'\n## T-0001: Alpha | one ({today})\n\n- decide: Quote the `--root`')
               and nt.count('\n- decide: ') == 4 and long_item in nt and run(root, 'check')[0] == 0)

        # (b) Warnings open, no --force: refuses and writes nothing
        warned = filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch')
        root = case(warned)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(b) open warnings refuse, name --force and the warning: rc={rc} {err!r}',
               rc == 1 and '--force' in err and 'step-2 verifier fail' in err)
        expect('(b) refusal wrote nothing (handoff, ticket count, roadmap)', snap(root) == before
               and len(load(root)) == 2 and status(root) == 'proposed')
        expect(f'(b) refusal names --ack-warnings before --force: {err!r}',
               '--ack-warnings "<why>"' in err and err.find('--ack-warnings') < err.find('--force'))

        # (c) the same with --force closes: plain files no ticket and notes the item; --ticket 1 files it
        root = case(warned)
        rc, out, err = run(root, 'close', ('alpha', True))
        expect(f'(c) --force closes: rc={rc} {err!r}', rc == 0 and status(root) == 'done'
               and not fresh(root, {'alpha', 'beta'}) and '- decide: Add retry to fetch\n' in (notes(root) or ''))
        root = case(warned)
        rc, out, err = close_one(root, 1, force=True)
        expect(f'(c) --force --ticket 1 files the one follow-up: rc={rc} {out!r} {err!r}', rc == 0
               and status(root) == 'done' and sorted(fresh(root, {'alpha', 'beta'})) == ['add-retry-to-fetch']
               and notes(root) is None)

        # (d) Follow-ups None: no tickets, parent done
        root = case(filer('filer-L1.md', 'None.', 'None'))
        rc, out, err = run(root, 'close', ('alpha',))
        expect(f'(d) follow-ups None: rc={rc} {out!r} {err!r}', rc == 0 and '0 follow-up' in out
               and not fresh(root, {'alpha', 'beta'}) and status(root) == 'done' and run(root, 'check')[0] == 0)

        # (e) no filer file: refuses, names /file
        root = case(lambda r: None)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(e) no filer file refuses: rc={rc} {err!r}', rc == 1 and '/file' in err and snap(root) == before)

        # (f) prose follow-ups with no bullet: refuses, writes nothing
        root = case(filer('filer-L1.md', 'None', 'We should add retry to fetch and document the flag.'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(f) prose follow-ups refuse: rc={rc} {err!r}', rc == 1 and snap(root) == before)

        # (g) a second close on a done ticket: refuses, no duplicate tickets
        root = case(good)
        run(root, 'close', ('alpha',))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha', True))
        expect(f'(g) second close refuses: rc={rc} {err!r}', rc == 1 and 'already closed' in err and snap(root) == before)

        # (h) the newest filer file is picked by recorded run order in runs.jsonl, never by file time
        def runs(*names):
            def put(root):
                (root / 'alpha' / 'runs.jsonl').write_text(''.join(
                    f'{{"role": "filer", "level": "{n[6:8]}", "file": "{n}"}}\n' for n in names), encoding='utf-8')
            return put

        bad = 'step-1 verifier fail'
        root = case(both(both(filer('filer-L2.md', bad, 'None', mtime=1_000_000),
                              filer('filer-L1.md', 'None', 'None', mtime=1_000_000)),
                         runs('filer-L2.md', 'filer-L1.md')))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) equal mtimes: runs.jsonl picks the lower-named filer recorded last: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done')
        root = case(both(both(filer('filer-L2.md', bad, 'None', mtime=2_000_000),
                              filer('filer-L1.md', 'None', 'None', mtime=1_000_000)),
                         runs('filer-L2.md', 'filer-L1.md')))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) inverse mtimes: runs.jsonl still decides: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        # no records: name (level) order, filer-L2.md beats a newer filer-L1.md
        root = case(both(filer('filer-L1.md', bad, 'None', mtime=2_000_000),
                         filer('filer-L2.md', 'None', 'None', mtime=1_000_000)))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) no runs.jsonl: name order decides, not mtime: rc={rc} {err!r}', rc == 0 and status(root) == 'done')

        # (i) numbered close: each follow-up folder is NNNN-<slug> with its own id; alpha keeps its name
        numbered_follow = filer('filer-L1.md', 'None', '- Add retry to fetch\n- Add retry to fetch\n'
                                '- 0042 fix the parser')
        for label, mutate, kw in (('flag', numbered_follow, {'numbered': True}),
                                  ('config', both(numbered_follow, config('ticket_folders: numbered\n')), {})):
            root = case(mutate)
            rc, out, err = close_one(root, 3, **kw)
            made = fresh(root, {'alpha', 'beta'})
            ok = all(re.match(r'\d{4}-', s) and s[:4] == m.get('id', '')[2:] for s, m in made.items())
            expect(f'(i) numbered close --ticket 3 ({label}): rc={rc} {err!r} made={sorted(made)}',
                   rc == 0 and len(made) == 1 and ok and status(root) == 'done'
                   and sorted(made) == ['0003-fix-the-parser'] and run(root, 'check')[0] == 0
                   and (notes(root) or '').count('- decide: Add retry to fetch\n') == 2)
        # (i) a clash on the final numbered name appends -2
        root = case(both(filer('filer-L1.md', 'None', '- Add retry to fetch'),
                         lambda r: (r / '0003-add-retry-to-fetch').mkdir()))
        rc, out, err = close_one(root, 1, numbered=True)
        expect(f'(i) numbered clash appends -2: rc={rc} {err!r} {out!r}',
               rc == 0 and (root / '0003-add-retry-to-fetch-2' / 'handoff.md').is_file())
        # (i) negative control: no flag, no config -> bare-slug follow-ups
        root = case(numbered_follow)
        rc, out, err = close_one(root, 3)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(i) plain close keeps bare slugs: rc={rc} {sorted(made)}',
               rc == 0 and sorted(made) == ['0042-fix-the-parser'])
        expect(f'(i) plain close writes no config: tree={tree(root)}', not (root / 'config').exists())
        # (j) close --numbered persists `ticket_folders: numbered`, like new --numbered; a refusal writes none
        root = case(numbered_follow)
        rc, out, err = run(root, 'close', ('alpha',), numbered=True)
        expect(f'(j) close --numbered writes config with the numbered line: rc={rc} {err!r} tree={tree(root)}',
               rc == 0 and (root / 'config').is_file() and config_numbered(root))
        root = case(filer('filer-L1.md', 'step-1 verifier fail', '- Add retry to fetch'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), numbered=True)
        expect(f'(j) refused close --numbered writes no config: rc={rc} {err!r}',
               rc == 1 and not (root / 'config').exists() and snap(root) == before)

        # (k) --reason closes with no filer file: done, a ## Closed section, check passes
        root = case(lambda r: None)
        rc, out, err = run(root, 'close', ('alpha',), reason='done by T-0002')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(k) --reason closes without a filer: rc={rc} {err!r} {out!r}',
               rc == 0 and status(root) == 'done' and 'reason' in out
               and text.rstrip().endswith(f'## Closed\n\n{datetime.date.today().isoformat()}: done by T-0002')
               and run(root, 'check')[0] == 0)
        # (k2) T-0453: a close prints one `lane still open` line per plugin lane that lists the ticket; the exit code is unchanged
        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the (k2) lane-report cases')
        else:
            import lanes
            lenv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
            lenv.update(GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')

            def lgit(cwd, *args):
                p = subprocess.run(['git', '-C', str(cwd), *args], env=lenv, capture_output=True, text=True)
                if p.returncode:
                    raise AssertionError(f'selftest git fixture failed: git {" ".join(args)}: {p.stderr.strip()}')

            def lane_repo(claim=True):
                root = case(lambda r: None)
                if claim:
                    edit(root, 'alpha', r'^status:.*$', 'status: claimed\nclaimed_by: codex 2026-10-11')
                (root.parent / '.gitignore').write_text('.sdlc/\n.worktrees/\n', encoding='utf-8')
                lgit(root.parent, 'init', '-q', '-b', 'main')
                lgit(root.parent, 'add', '-A')
                lgit(root.parent, 'commit', '-q', '-m', 'init')
                return root

            saved_env = {k: os.environ.get(k) for k in lenv if k.startswith('GIT_')}
            os.environ.update({k: v for k, v in lenv.items() if k.startswith('GIT_AUTHOR') or k.startswith('GIT_COMMITTER')})
            try:
                root = lane_repo()
                opened = lanes.open_lane('alpha', tickets=['T-0001'], cwd=root.parent)
                rc, out, err = run(root, 'close', ('alpha',), reason='done by lane')
                rows = [ln for ln in out.splitlines() if ln.startswith('lane still open: ')]
                expect(f'(k2) a close prints one lane still open line for the lane that lists the ticket: rc={rc} {err!r} {out!r} {opened["message"]!r}',
                       opened['rc'] == 0 and rc == 0 and status(root) == 'done' and len(rows) == 1
                       and str(opened['path']) in rows[0] and '(branch lane/T-0001-alpha, ' in rows[0])
                # negative control: a ticket no lane lists reports nothing
                root = lane_repo()
                lanes.open_lane('alpha', tickets=['T-0001'], cwd=root.parent)
                rc, out, err = run(root, 'close', ('beta',), reason='unrelated')
                expect(f'(k2) closing a ticket no lane lists prints no lane line: rc={rc} {err!r} {out!r}',
                       rc == 0 and 'lane still open' not in out)
                # not a git repo: the close still succeeds and prints no lane line
                root = case(lambda r: None)
                rc, out, err = run(root, 'close', ('alpha',), reason='no repo')
                expect(f'(k2) a root outside any repo closes with no lane line: rc={rc} {err!r} {out!r}',
                       rc == 0 and 'lane still open' not in out)
            finally:
                for k in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL'):
                    if saved_env.get(k) is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = saved_env[k]
        # (l) --reason ignores a filer with open warnings and follow-ups
        root = case(filer('filer-L1.md', 'step-1 verifier fail', '- Add retry to fetch'))
        rc, out, err = run(root, 'close', ('alpha',), reason='superseded')
        expect(f'(l) --reason ignores the filer: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done' and not fresh(root, {'alpha', 'beta'}))
        # (m) an empty or whitespace-only reason refuses and writes nothing
        for why in ('', '   '):
            root = case(lambda r: None)
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), reason=why)
            expect(f'(m) empty --reason {why!r} refuses: rc={rc} {err!r}', rc == 1 and snap(root) == before)
        # (n) --reason on a done ticket still refuses
        root = case(lambda r: None)
        run(root, 'close', ('alpha',), reason='first')
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), reason='second')
        expect(f'(n) --reason on done refuses: rc={rc} {err!r}',
               rc == 1 and 'already closed' in err and snap(root) == before)
        # (o) --force with --reason closes; --numbered with --reason persists the config
        root = case(lambda r: None)
        rc, _, err = run(root, 'close', ('alpha', True), reason='x')
        expect(f'(o) --force --reason closes: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        root = case(lambda r: None)
        rc, _, err = run(root, 'close', ('alpha',), numbered=True, reason='x')
        expect(f'(o) --numbered --reason persists config: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done' and config_numbered(root))

        # (held) T-0408: a criterion the verifier holds (deferred or unmet-dependency) keeps the ticket open
        V_HEAD = '<!-- role=verifier level=L2 model=opus effort=high -->\n'
        V_HELD = (V_HEAD + '## Verdict\nfail\n\n## Criteria\n- #1 ships it: deferred integration. Evidence: not yet\n\n'
                  '## For the next attempt\ndeferred: integration\n')
        V_SETTLE = (V_HEAD + '## Verdict\npass\n\n## Criteria\n- #1 ships it: pass. Evidence: green\n\n'
                    '## For the next attempt\nNone\n\n## Settles\n- ticket#1\n')

        def held_case(clause='[owner: integration]', settled=False):
            def mutate(r):
                with (r / 'alpha' / 'handoff.md').open('a', encoding='utf-8') as f:
                    f.write(f'\n## Acceptance criteria\n- [ ] ships it {clause}\n')
                (r / 'alpha' / 'verifier-L2.md').write_text(V_HELD, encoding='utf-8')
                names = ['verifier-L2.md']
                if settled:
                    (r / 'alpha' / 'verifier-L2-2.md').write_text(V_SETTLE, encoding='utf-8')
                    names.append('verifier-L2-2.md')
                (r / 'alpha' / 'runs.jsonl').write_text(''.join(f'{{"file": "{n}"}}\n' for n in names), encoding='utf-8')
            return mutate
        for label, kw, args in (('--reason', {'reason': 'done elsewhere'}, ('alpha',)),
                                ('--force --reason', {'reason': 'done elsewhere'}, ('alpha', True)),
                                ('the filer path', {}, ('alpha',))):
            root = case(held_case())
            before = snap(root)
            rc, _, err = run(root, 'close', args, **kw)
            expect(f'(held) close via {label} refuses a held criterion and writes nothing: rc={rc} {err!r}',
                   rc == 1 and 'criteria still held: ticket#1 deferred integration' in err
                   and 'nothing written' in err and snap(root) == before and status(root) != 'done')
        root = case(held_case(settled=True))
        rc, _, err = run(root, 'close', ('alpha',), reason='done elsewhere')
        expect(f'(held) control: the same ticket after a settling result closes: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done')
        root = case(held_case(clause=''))
        rc, _, err = run(root, 'close', ('alpha',), reason='done elsewhere')
        expect(f'(held) control: a held line on a criterion with no clause does not block close: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done')

        # (p) --dry-run lists every bullet with its index and duplicate mark, and writes nothing
        three = '- Add retry to fetch\n- Quote the docs\n- Split the runner'
        root = case(filer('filer-L1.md', 'None', '- Add retry to fetch\n- Fix #12\n- Quote the docs'))
        before = snap(root)
        rc, out, err = run(root, 'close', ('alpha',), numbered=True, dry_run=True)
        lines = out.splitlines()
        expect(f'(p) dry run lists 1 to 3, marks Fix #12 as a duplicate of beta, writes nothing: rc={rc} '
               f'out={out!r} err={err!r} tree={tree(root)}',
               rc == 0 and snap(root) == before and status(root) == 'proposed'
               and lines[:1] == ['T-0001 dry run: 3 proposed follow-up(s); nothing written']
               and [ln.split('.', 1)[0] for ln in lines[1:-1] if not ln.startswith('open ')] == ['1', '2', '3']
               and lines[-1] == 'expect ' + follow_digest(['Add retry to fetch', 'Fix #12', 'Quote the docs'])
               and lines[2].startswith('2. decide: Fix #12 ') and lines[2].endswith('duplicate of T-0002 (beta)')
               and 'duplicate' not in lines[1] + lines[3]
               and lines[1] == '1. decide: Add retry to fetch note' and lines[3] == '3. decide: Quote the docs note')
        # (p2) open tickets listed: an open ticket with its full title; not done/dropped, not the closed one
        def open_mix(r):
            filer('filer-L1.md', 'None', '- Add retry to fetch')(r)
            cmd_new(r, 'bug', 'gone', 'Gone bug')
            edit(r, 'gone', r'^status:.*$', 'status: dropped')
        root = case(open_mix)
        rc, out, err = run(root, 'close', ('alpha',), dry_run=True)
        opens = [ln for ln in out.splitlines() if ln.startswith('open ')]
        beta = next(m for x, m in load(root) if x == 'beta')
        expect(f'(p2) open tickets listed: beta with full title, not dropped gone, not alpha: rc={rc} {out!r} {err!r}',
               rc == 0 and opens == [f'open T-0002 {beta["title"]} [beta]']
               and out.splitlines()[-1].startswith('expect '))
        root = case(filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), dry_run=True)
        expect(f'(p) dry run with open warnings and no --force refuses: rc={rc} {err!r}',
               rc == 1 and '--force' in err and snap(root) == before)

        # (q) --skip drops an item entirely: --skip 2 --ticket 1 files bullet 1 and notes only bullet 3
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, err = run(root, 'close', ('alpha',), skip=[2], ticket=1, expect=follow_digest(bullets(three)))
        made = fresh(root, {'alpha', 'beta'})
        nt = notes(root) or ''
        expect(f'(q) --skip 2 --ticket 1 files bullet 1, notes bullet 3: rc={rc} out={out!r} err={err!r} '
               f'made={sorted(made)} notes={nt!r}',
               rc == 0 and status(root) == 'done' and len(made) == 1
               and [m.get('title') for m in made.values()] == ['Add retry to fetch']
               and [m.get('id') for m in made.values()] == ['T-0003']
               and '- decide: Split the runner\n' in nt and 'Quote the docs' not in nt
               and 'skipped by --skip: 2' in out)

        # (r) --skip out of range refuses, names the index and the count, writes nothing
        for bad, follow in ((4, three), (0, three), (1, 'None')):
            root = case(filer('filer-L1.md', 'None', follow))
            before = snap(root)
            for dry in (True, False):
                token = None if dry else follow_digest([] if follow == 'None' else bullets(follow))
                rc, _, err = run(root, 'close', ('alpha',), skip=[bad], dry_run=dry, expect=token)
                count = 0 if follow == 'None' else 3
                expect(f'(r) --skip {bad} (dry_run={dry}) with {count} bullet(s) refuses: rc={rc} {err!r}',
                       rc == 1 and f'--skip {bad} ' in err and f'has {count} item' in err and snap(root) == before)
        try:
            parse_skip('2,x')
            bad_token = None
        except Fail as e:
            bad_token = str(e)
        expect(f'(r) a non-integer --skip token is a refusal: {bad_token!r}',
               bad_token is not None and "'x'" in bad_token and parse_skip('3, 1') == [3, 1])

        # (s) a plain close skips duplicates of existing tickets (by title, by slug base) and names them
        dup_follow = filer('filer-L1.md', 'None', '- Fix #12\n- Beta\n- Add retry to fetch')
        root = case(dup_follow)
        rc, out, err = close_one(root, 3)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(s) duplicates of beta skipped on close: rc={rc} out={out!r} err={err!r} made={sorted(made)}',
               rc == 0 and sorted(made) == ['add-retry-to-fetch'] and 'skipped duplicate(s)' in out
               and out.count('T-0002 (beta)') == 2 and run(root, 'check')[0] == 0
               and notes(root) is None and '0 follow-up(s) appended to notes.md' in out)
        root = case(dup_follow)
        rc, out, err = run(root, 'close', ('alpha',))
        nt = notes(root) or ''
        expect(f'(s) plain close notes only the non-duplicate: rc={rc} out={out!r} notes={nt!r}',
               rc == 0 and not fresh(root, {'alpha', 'beta'}) and out.count('T-0002 (beta)') == 2
               and nt.endswith('\n- decide: Add retry to fetch\n') and 'Fix #12' not in nt and 'Beta' not in nt)

        # (s2) the ticket being closed is not a duplicate target: follow-ups that start with its own
        # title ("Alpha | one" -> "alpha one") are filed, and colliding slugs take a -2 suffix
        root = case(filer('filer-L1.md', 'None', '- Alpha one\n- Alpha one.'))
        rc, out, err = run(root, 'close', ('alpha',), dry_run=True)
        expect(f'(s2) dry run marks no bullet a duplicate of the closing ticket: rc={rc} out={out!r} err={err!r}',
               rc == 0 and 'duplicate' not in out and '1. decide: Alpha one ' in out
               and '2. decide: Alpha one. ' in out)
        rc, out, err = close_one(root, 2)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(s2) close --ticket 2 files it, notes the other: rc={rc} out={out!r} err={err!r} '
               f'made={sorted(made)}',
               rc == 0 and sorted(made) == ['alpha-one'] and 'duplicate' not in out
               and (notes(root) or '').endswith('\n- decide: Alpha one\n') and run(root, 'check')[0] == 0)
        # a folder already holding the slug (not a ticket) makes the one follow-up take -2
        root = case(both(filer('filer-L1.md', 'None', '- Alpha one'), lambda r: (r / 'alpha-one').mkdir()))
        rc, out, err = close_one(root, 1)
        expect(f'(s2) a taken slug appends -2: rc={rc} out={out!r} err={err!r}',
               rc == 0 and sorted(fresh(root, {'alpha', 'beta'})) == ['alpha-one-2'])

        # (t) --reason does not combine with --dry-run or --skip
        for kw in ({'dry_run': True}, {'skip': [1]}, {'expect': 'x'}, {'ticket': 1}):
            root = case(filer('filer-L1.md', 'None', three))
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), reason='superseded', **kw)
            expect(f'(t) --reason with {kw} refuses and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '--reason' in err and snap(root) == before)

        # (v) --skip is tied to the dry run's list: a changed Follow-ups list refuses, unchanged closes.
        # (v4) a plain close with no --skip and no --expect needs no token; case (s) covers it too.
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        old = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        filer('filer-L1.md', 'None', '- Quote the docs\n- Add retry to fetch\n- Split the runner')(root)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2], expect=old)
        expect(f'(v1) a reordered Follow-ups list refuses stale --skip indices: rc={rc} {err!r}',
               rc == 1 and 'does not match' in err and 'filer-L1.md' in err and err.endswith('nothing written')
               and snap(root) == before and status(root) == 'proposed')
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        rc, out, err = run(root, 'close', ('alpha',), skip=[2], ticket=3, expect=token)
        expect(f'(v2) an unchanged list closes with --skip --ticket --expect: rc={rc} {out!r} {err!r}',
               rc == 0 and status(root) == 'done' and sorted(fresh(root, {'alpha', 'beta'})) == ['split-the-runner']
               and (notes(root) or '').endswith('\n- decide: Add retry to fetch\n'))
        # (v2) --ticket is tied to the dry run's list too: a reordered list refuses a stale --expect
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        old = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        filer('filer-L1.md', 'None', '- Quote the docs\n- Add retry to fetch\n- Split the runner')(root)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), ticket=1, expect=old)
        expect(f'(v2) a reordered Follow-ups list refuses a stale --ticket: rc={rc} {err!r}',
               rc == 1 and 'does not match' in err and snap(root) == before and notes(root) is None)
        root = case(filer('filer-L1.md', 'None', three))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2])
        expect(f'(v3) --skip without --expect refuses: rc={rc} {err!r}',
               rc == 1 and '--expect' in err and 'nothing written' in err and snap(root) == before)
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, err = run(root, 'close', ('alpha',))
        expect(f'(v4) plain close needs no token: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        tail = ' and a retry budget that callers can tune per request without touching the runner at all'
        long3 = f'- Add retry to fetch{tail}\n- Quote the docs\n- Split the runner'
        root = case(filer('filer-L1.md', 'None', long3))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        old = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        filer('filer-L1.md', 'None', long3.replace('at all', 'ever'))(root)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2], expect=old)
        expect(f'(v5) rewording past the title cut refuses: rc={rc} {err!r}',
               rc == 1 and 'does not match' in err and snap(root) == before)

        # (cap) each Follow-ups bullet carries a tag (fix-now:, decide:, note:; untagged = decide); close files at
        # most one ticket, the decide: item named by --ticket N, and appends every other item to <root>/notes.md
        two = filer('filer-L1.md', 'None', '- decide: Add retry to fetch\n- decide: Split the runner')
        root = case(two)
        rc, out, err = close_one(root, 1)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(cap) two decide: items, --ticket 1 files one ticket and notes item 2: rc={rc} out={out!r} '
               f'err={err!r} made={made} notes={notes(root)!r}',
               rc == 0 and list(made) == ['add-retry-to-fetch'] and made['add-retry-to-fetch'].get('title')
               == 'Add retry to fetch' and made['add-retry-to-fetch'].get('from') == 'T-0001'
               and notes(root) == notes_head + f'\n## T-0001: Alpha | one ({today})\n\n- decide: Split the runner\n'
               and out == 'T-0001 done; follow-up ticket: add-retry-to-fetch; 1 follow-up(s) appended to notes.md'
               and status(root) == 'done' and run(root, 'check')[0] == 0)
        h = root / 'add-retry-to-fetch' / 'handoff.md'
        ctx = h.read_text(encoding='utf-8') if h.is_file() else ''
        expect(f'(cap) the ticket context holds the text after the tag, not the tag: {ctx!r}',
               'alpha/filer-L1.md):\n\nAdd retry to fetch' in ctx and 'decide:' not in ctx)
        # (cap) a second close elsewhere appends its own dated block under the one heading
        filer('filer-L1.md', 'None', '- note: Beta also saw it', slug='beta')(root)
        rc, out, err = run(root, 'close', ('beta',))
        nt = notes(root) or ''
        expect(f'(cap) a second close appends a block, heading once: rc={rc} {err!r} notes={nt!r}',
               rc == 0 and nt.count('# Notes') == 1 and nt.endswith(
                   f'- decide: Split the runner\n\n## T-0002: Fix #12 ({today})\n\n- note: Beta also saw it\n'))
        # (cap) plain close files zero tickets and appends all, untagged written as decide:
        mixed = filer('filer-L1.md', 'None', '- decide: Add retry to fetch\n- fix-now: Quote the docs\n'
                      '- note:Split the runner\n- Untagged legacy item')
        root = case(mixed)
        rc, out, err = run(root, 'close', ('alpha',))
        expect(f'(cap) plain close files zero tickets and appends all four: rc={rc} out={out!r} err={err!r} '
               f'notes={notes(root)!r}',
               rc == 0 and not fresh(root, {'alpha', 'beta'}) and status(root) == 'done'
               and out == 'T-0001 done; follow-up ticket: none; 4 follow-up(s) appended to notes.md'
               and (notes(root) or '').endswith('\n\n- decide: Add retry to fetch\n- fix-now: Quote the docs\n'
                                                '- note: Split the runner\n- decide: Untagged legacy item\n')
               and not any((root / x).exists() for x in ('add-retry-to-fetch', 'quote-the-docs',
                                                         'split-the-runner', 'untagged-legacy-item')))
        # (cap) note: items never appear as folders, with or without --ticket elsewhere
        root = case(filer('filer-L1.md', 'None', '- note: Add retry to fetch\n- decide: Split the runner\n'
                          '- note: Quote the docs'))
        rc, out, err = close_one(root, 2)
        expect(f'(cap) note: items never become folders: rc={rc} {out!r} {err!r} tree={tree(root)}',
               rc == 0 and sorted(fresh(root, {'alpha', 'beta'})) == ['split-the-runner']
               and not (root / 'add-retry-to-fetch').exists() and not (root / 'quote-the-docs').exists()
               and (notes(root) or '').endswith('\n- note: Add retry to fetch\n- note: Quote the docs\n'))
        # (cap) refusals: each writes nothing (no notes.md, status unchanged, tree snapshot equal)
        for label, follow, kw, want in (
                ('--ticket on a note: item', '- decide: Add retry to fetch\n- note: Split the runner',
                 {'ticket': 2}, 'is a note: item; only a decide: item can become a ticket'),
                ('--ticket on a fix-now: item', '- decide: Add retry to fetch\n- fix-now: Split the runner',
                 {'ticket': 2}, 'is a fix-now: item; only a decide: item can become a ticket'),
                ('--ticket on a duplicate', '- decide: Fix #12\n- decide: Add retry to fetch',
                 {'ticket': 1}, 'already tracked by T-0002'),
                ('--ticket without --expect', '- decide: Add retry to fetch', {'ticket': 1, 'expect': None},
                 '--ticket needs --expect'),
                ('--ticket inside --skip', '- decide: Add retry to fetch\n- decide: Split the runner',
                 {'ticket': 1, 'skip': [1]}, 'also in --skip'),
                ('--ticket with --reason', '- decide: Add retry to fetch', {'ticket': 1, 'reason': 'x',
                                                                            'expect': None},
                 '--reason files no follow-ups'),
                ('--ticket out of range', '- decide: Add retry to fetch', {'ticket': 2}, '--ticket 2 is out of range'),
                ('--ticket 0', '- decide: Add retry to fetch', {'ticket': 0}, '--ticket 0 is out of range'),
                ('dry run --ticket on a note: item', '- note: Add retry to fetch',
                 {'ticket': 1, 'dry_run': True, 'expect': None}, 'is a note: item')):
            root = case(filer('filer-L1.md', 'None', follow))
            kw = {'expect': follow_digest(bullets(follow)), **kw}
            before = snap(root)
            rc, out, err = run(root, 'close', ('alpha',), **kw)
            expect(f'(cap) {label} refuses and writes nothing: rc={rc} out={out!r} err={err!r}',
                   rc == 1 and want in err and err.endswith('nothing written') and notes(root) is None
                   and status(root) == 'proposed' and snap(root) == before)
        # (cap) an untagged item counts as decide: and takes --ticket; its title and slug are the whole text
        root = case(filer('filer-L1.md', 'None', '- Add retry to fetch\n- note: keep'))
        rc, out, err = close_one(root, 1)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(cap) an untagged item takes --ticket as decide: rc={rc} {out!r} {err!r} made={made}',
               rc == 0 and list(made) == ['add-retry-to-fetch']
               and made['add-retry-to-fetch'].get('title') == 'Add retry to fetch'
               and (notes(root) or '').endswith('\n- note: keep\n'))
        # (cap) numbered mode names the one folder NNNN-<slug>; notes.md holds no folder path
        root = case(two)
        rc, out, err = close_one(root, 2, numbered=True)
        made = fresh(root, {'alpha', 'beta'})
        nt = notes(root) or ''
        expect(f'(cap) numbered mode names the one folder 0003-split-the-runner: rc={rc} {out!r} {err!r} '
               f'made={made} notes={nt!r}',
               rc == 0 and {x: m.get('id') for x, m in made.items()} == {'0003-split-the-runner': 'T-0003'}
               and nt.endswith('\n- decide: Add retry to fetch\n') and '/' not in nt
               and run(root, 'check')[0] == 0)
        # (cap) a dry run writes no notes.md and carries the ticket/note marks; the tag leads each line
        root = case(filer('filer-L1.md', 'None', '- decide:   Add retry to fetch\n- note: Split the runner\n'
                          '- decide: Quote the docs\n- fix-now: Fix #12'))
        before = snap(root)
        rc, out, err = run(root, 'close', ('alpha',), dry_run=True, ticket=3)
        ol = out.splitlines()
        expect(f'(cap) a dry run with --ticket 3 marks ticket and note, writes nothing: rc={rc} out={out!r} '
               f'err={err!r}',
               rc == 0 and snap(root) == before and notes(root) is None
               and ol[0] == 'T-0001 dry run: 4 proposed follow-up(s); nothing written'
               and ol[1:5] == ['1. decide: Add retry to fetch note', '2. note: Split the runner note',
                               '3. decide: Quote the docs [quote-the-docs] ticket',
                               '4. fix-now: Fix #12 [fix-12] duplicate of T-0002 (beta)']
               and ol[-1] == 'expect ' + follow_digest(['decide:   Add retry to fetch', 'note: Split the runner',
                                                        'decide: Quote the docs', 'fix-now: Fix #12']))
        # (cap) the digest covers the full bullet, tag included: retagging an item changes it
        expect('(cap) the digest changes when only a tag changes',
               follow_digest(['decide: A']) != follow_digest(['note: A']) != follow_digest(['A']))

        # (u) numbered close archives a NNNN-<slug> folder as .NNNN-<slug>; every command still sees it
        def numbered_x(root):
            rc, _, err = run(root, 'new', ('feature', 'x'), numbered=True)  # 0003-x, T-0003; persists config
            if rc:
                raise AssertionError(f'selftest fixture 0003-x not made: {err}')

        def x_filer(follow):
            return filer('filer-L1.md', 'None', follow, slug='0003-x')

        root = case(both(numbered_x, x_filer('- Add retry to fetch')))
        rc, out, err = close_one(root, 1, slug='0003-x')
        made = fresh(root, {'alpha', 'beta', '.0003-x'})
        ctx = ''.join((root / s / 'handoff.md').read_text(encoding='utf-8') for s in made)
        expect(f'(u) numbered close with a filer renames 0003-x to .0003-x: rc={rc} out={out!r} err={err!r} '
               f'tree={tree(root)}',
               rc == 0 and out.endswith('; moved to .0003-x') and not (root / '0003-x').exists()
               and (root / '.0003-x' / 'filer-L1.md').is_file() and status(root, '.0003-x') == 'done'
               and sorted(made) == ['0004-add-retry-to-fetch']
               and 'Follow-up from T-0003 (.0003-x/filer-L1.md):' in ctx and run(root, 'check')[0] == 0)
        rm = (root / 'roadmap.md').read_text(encoding='utf-8')
        expect(f'(u) roadmap lists .0003-x: {rm!r}', '| T-0003 | [.0003-x](.0003-x/handoff.md) |' in rm)
        before = snap(root)
        for kw in ({}, {'reason': 'again'}, {'dry_run': True}):
            rc, _, err = run(root, 'close', ('0003-x',), **kw)
            expect(f'(u) closing again by the old name {kw} refuses with already closed: rc={rc} {err!r}',
                   rc == 1 and 'already closed (folder .0003-x)' in err and snap(root) == before)
        edit(root, 'beta', r'^depends:.*$', 'depends: [T-0003]')
        run(root, 'roadmap')
        rc, out, err = run(root, 'check')
        expect(f'(u) depends: [T-0003] on the dot folder resolves: rc={rc} {out!r} {err!r}',
               rc == 0 and 'ok: 4 tickets' in out)

        root = case(numbered_x)
        rc, out, err = run(root, 'close', ('0003-x',), reason='done elsewhere')
        text = (root / '.0003-x' / 'handoff.md').read_text(encoding='utf-8') if (root / '.0003-x').is_dir() else ''
        expect(f'(u) numbered --reason close renames: rc={rc} out={out!r} err={err!r} tree={tree(root)}',
               rc == 0 and out.endswith('; moved to .0003-x') and not (root / '0003-x').exists()
               and '## Closed' in text and status(root, '.0003-x') == 'done' and run(root, 'check')[0] == 0)
        rc, out, err = run(root, 'new', ('feature', 'y'), numbered=True)
        got = dict(load(root)).get('0004-y', {}).get('id')
        expect(f'(u) next new --numbered after a dot folder gets T-0004: rc={rc} {out!r} {err!r} id={got!r}',
               rc == 0 and got == 'T-0004')
        count = len(load(root))
        (root / '.hidden').mkdir()
        (root / '.hidden' / 'handoff.md').write_bytes((root / 'beta' / 'handoff.md').read_bytes())
        (root / '.board-state.json').write_text('{}', encoding='utf-8')
        rc, out, err = run(root, 'check')
        expect(f'(u) .hidden/handoff.md and .board-state.json are not tickets: rc={rc} {out!r} {err!r}',
               len(load(root)) == count == 4 and rc == 0 and out.startswith('ok: 4 tickets'))
        edit(root, '.0003-x', r'^status:.*$', 'status: ready')
        for label in ('numbered by config', 'plain mode'):
            if label == 'plain mode':
                (root / 'config').unlink()
            rc, _, err = run(root, 'check')
            expect(f'(u) check ({label}) fails a dot folder with status ready: rc={rc} {err!r}',
                   rc == 1 and '.0003-x: closed ticket folder' in err and 'done or dropped' in err)
        edit(root, '.0003-x', r'^status:.*$', 'status: dropped')
        run(root, 'roadmap')
        rc, out, err = run(root, 'check', numbered=True)
        expect(f'(u) a dropped dot folder passes: rc={rc} {out!r} {err!r}', rc == 0)

        # (u) the rename target already exists: refuses on every close path and writes nothing
        for kw in ({}, {'reason': 'x'}, {'dry_run': True}):
            root = case(both(numbered_x, x_filer('- Add retry to fetch'), lambda r: (r / '.0003-x').mkdir()))
            before = snap(root)
            rc, _, err = run(root, 'close', ('0003-x',), **kw)
            expect(f'(u) close {kw} onto an existing .0003-x refuses: rc={rc} {err!r}',
                   rc == 1 and '.0003-x' in err and 'nothing written' in err and snap(root) == before
                   and (root / '0003-x' / 'handoff.md').is_file())

        # (u) the dry run shows the rename line and writes nothing
        root = case(both(numbered_x, x_filer('- Add retry to fetch')))
        before = snap(root)
        rc, out, err = run(root, 'close', ('0003-x',), dry_run=True)
        expect(f'(u) dry run shows the rename and writes nothing: rc={rc} {out!r} {err!r}',
               rc == 0 and 'rename 0003-x -> .0003-x' in out.splitlines() and snap(root) == before
               and not (root / '.0003-x').exists())

        # (u) numbered: a .NNNN- folder still gets the prefix/id rule; a dot folder counts as prefixed
        def closed_as(to):
            def put(root):
                edit(root, 'alpha', r'^status:.*$', 'status: done')
                (root / 'alpha').rename(root / to)
                run(root, 'roadmap')
            return put
        rc, _, err = run(case(closed_as('.0005-alpha')), 'check', numbered=True)
        expect(f'(u) .0005-alpha with id T-0001 fails check --numbered: rc={rc} {err!r}',
               rc == 1 and ".0005-alpha: folder prefix 0005- does not match id 'T-0001'" in err)
        rc, out, err = run(case(both(closed_as('.0001-alpha'), renamed_beta)), 'check')
        expect(f'(u) .0001-alpha plus 0002-beta, no config: the numbered-config warning fires: rc={rc} {out!r}',
               rc == 0 and 'warning' in out)
        expect("(u) strip_prefix drops a closed folder's dot", strip_prefix('.0002-beta') == 'beta')

        # (u) numbered close refuses on files outside the folder that reference it; --rewrite-refs rewrites them
        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the (u) outside-reference cases')
        else:
            renv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

            def rgit(cwd, *args):
                p = subprocess.run(['git', '-C', str(cwd), *args], env=renv, capture_output=True, text=True)
                if p.returncode:
                    raise AssertionError(f'selftest git fixture failed: git {" ".join(args)}: {p.stderr.strip()}')

            def ref_repo(*fs, commit=True, where='docs/spec.md', text='see .sdlc/0003-x/handoff.md\n'):
                root = case(both(numbered_x, x_filer('None'), *fs))
                rgit(root.parent, 'init', '-q')
                spec = root.parent / where
                spec.parent.mkdir(parents=True, exist_ok=True)
                spec.write_text(text, encoding='utf-8')
                if commit:
                    rgit(root.parent, 'add', '-A')
                    rgit(root.parent, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                         'commit', '--no-verify', '-qm', 'x')
                return root, spec

            def whole(root):
                return {p.relative_to(root.parent): p.read_bytes() for p in sorted(root.parent.rglob('*'))
                        if p.is_file() and '.git' not in p.relative_to(root.parent).parts}

            for label, commit, kw in (('committed', True, {}), ('untracked', False, {}),
                                      ('--reason', True, {'reason': 'done elsewhere'}),
                                      ('--dry-run', True, {'dry_run': True})):
                root, spec = ref_repo(commit=commit)
                before = whole(root)
                rc, out, err = run(root, 'close', ('0003-x',), **kw)
                expect(f'(u) refs: a {label} outside reference refuses, names docs/spec.md, writes nothing: rc={rc} '
                       f'{out!r} {err!r}',
                       rc == 1 and 'docs/spec.md' in err and '--rewrite-refs' in err and '--force' in err
                       and 'nothing written' in err and whole(root) == before and (root / '0003-x').is_dir())

            root, spec = ref_repo()
            rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
            got = spec.read_text(encoding='utf-8')
            expect(f'(u) refs: --rewrite-refs rewrites and closes: rc={rc} {out!r} {err!r} spec={got!r}',
                   rc == 0 and out.endswith('; moved to .0003-x; rewrote refs in docs/spec.md')
                   and got == 'see .sdlc/.0003-x/handoff.md\n' and status(root, '.0003-x') == 'done'
                   and run(root, 'check')[0] == 0)

            root, spec = ref_repo()
            rc, out, err = run(root, 'close', ('0003-x',), reason='done elsewhere', rewrite_refs=True)
            expect(f'(u) refs: --reason --rewrite-refs rewrites and closes: rc={rc} {out!r} {err!r}',
                   rc == 0 and out.endswith('; rewrote refs in docs/spec.md') and (root / '.0003-x').is_dir()
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/.0003-x/handoff.md\n')

            root, spec = ref_repo()
            before = whole(root)
            rc, out, err = run(root, 'close', ('0003-x',), dry_run=True, rewrite_refs=True)
            ol = out.splitlines()
            expect(f'(u) refs: --dry-run --rewrite-refs lists the file before expect, writes nothing: rc={rc} '
                   f'{out!r} {err!r}',
                   rc == 0 and len(ol) >= 2 and ol[-2] == 'rewrite docs/spec.md' and ol[-1].startswith('expect ')
                   and whole(root) == before)

            root, spec = ref_repo()
            rc, out, err = run(root, 'close', ('0003-x',), force=True)
            expect(f'(u) refs: --force closes and leaves the reference: rc={rc} {out!r} {err!r}',
                   rc == 0 and (root / '.0003-x').is_dir() and 'rewrote' not in out
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/0003-x/handoff.md\n')
            expect(f'(u) refs: --force prints the files it left citing the folder: {out!r}',
                   out.endswith('; left refs to .sdlc/0003-x in docs/spec.md'))

            # T-0348: --keep-refs closes, leaves the citation, lists it in the close note; no flag still refuses
            root, spec = ref_repo()
            rc, out, err = run(root, 'close', ('0003-x',))
            expect(f'(u) keep-refs: no flag still refuses: rc={rc} {err!r}',
                   rc == 1 and '--keep-refs' in err and (root / '0003-x').is_dir())
            rc, out, err = run(root, 'close', ('0003-x',), keep_refs=True, rewrite_refs=True)
            expect(f'(u) keep-refs: does not combine with --rewrite-refs: rc={rc} {err!r}',
                   rc == 1 and 'nothing written' in err and (root / '0003-x').is_dir())
            rc, out, err = run(root, 'close', ('0003-x',), keep_refs=True, dry_run=True)
            expect(f'(u) keep-refs: dry run lists keep docs/spec.md: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'keep docs/spec.md' in out.splitlines() and (root / '0003-x').is_dir())
            rc, out, err = run(root, 'close', ('0003-x',), keep_refs=True)
            note = (root / '.0003-x' / 'handoff.md').read_text(encoding='utf-8')
            expect(f'(u) keep-refs: closes, leaves the cite, close note lists docs/spec.md: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'kept refs' not in err and out.endswith('; left refs to .sdlc/0003-x in docs/spec.md')
                   and '## Closed' in note and 'kept stale refs to .sdlc/0003-x in: docs/spec.md' in note
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/0003-x/handoff.md\n'
                   and status(root, '.0003-x') == 'done')

            # T-0262: a citation under a gitignored ticket root is seen, refused, named, and rewritable
            def ignored_ref():
                root, spec = ref_repo(commit=False, where='.sdlc/index.md')
                (root.parent / '.gitignore').write_text('.sdlc/\n', encoding='utf-8')
                return root, spec

            root, spec = ignored_ref()
            before = whole(root)
            rc, out, err = run(root, 'close', ('0003-x',))
            expect(f'(u) refs: a citation in a gitignored .sdlc refuses and names .sdlc/index.md: rc={rc} {err!r}',
                   rc == 1 and '.sdlc/index.md' in err and '--rewrite-refs' in err and whole(root) == before)
            root, spec = ignored_ref()
            rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
            expect(f'(u) refs: --rewrite-refs rewrites the gitignored .sdlc citation: rc={rc} {out!r} {err!r}',
                   rc == 0 and out.endswith('; rewrote refs in .sdlc/index.md')
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/.0003-x/handoff.md\n')

            # negative controls: a reference only inside the ticket's own folder (or the roadmap) closes
            root, spec = ref_repo(where='.sdlc/0003-x/notes.md')
            with (root / 'roadmap.md').open('a', encoding='utf-8') as f:
                f.write('.sdlc/0003-x/handoff.md\n')
            rc, out, err = run(root, 'close', ('0003-x',))
            expect(f'(u) refs: a reference only inside the own folder closes: rc={rc} {out!r} {err!r}',
                   rc == 0 and (root / '.0003-x' / 'notes.md').is_file() and 'rewrote' not in out)

            # plain mode never scans: the folder does not move, so a reference stays valid
            root = case(filer('filer-L1.md', 'None', 'None'))
            rgit(root.parent, 'init', '-q')
            (root.parent / 'spec.md').write_text('see .sdlc/alpha/handoff.md\n', encoding='utf-8')
            rc, out, err = run(root, 'close', ('alpha',))
            expect(f'(u) refs: plain mode never refuses on a reference: rc={rc} {out!r} {err!r}',
                   rc == 0 and status(root) == 'done' and (root / 'alpha').is_dir())

            # a reference written relative to the citing file, or as an absolute path, is found and rewritten too
            def abs_ref(root):
                return f'see {root}/0003-x/handoff.md\n'

            for label, where, text, want in (
                    ('../ from another ticket folder', '.sdlc/alpha/notes.md', 'see ../0003-x/filer-L1.md\n',
                     lambda root: 'see ../.0003-x/filer-L1.md\n'),
                    ('./ from the ticket root', '.sdlc/index.md', '[x](./0003-x/handoff.md)\n',
                     lambda root: '[x](./.0003-x/handoff.md)\n'),
                    ('absolute', 'docs/spec.md', None, lambda root: f'see {root}/.0003-x/handoff.md\n')):
                def fixture():
                    root, spec = ref_repo(where=where, text=text or '')
                    if text is None:
                        spec.write_text(abs_ref(root), encoding='utf-8')
                    return root, spec

                root, spec = fixture()
                before = whole(root)
                rc, out, err = run(root, 'close', ('0003-x',))
                expect(f'(u) refs: a {label} reference refuses, names {where}, writes nothing: rc={rc} '
                       f'{out!r} {err!r}',
                       rc == 1 and where in err and '--rewrite-refs' in err and 'nothing written' in err
                       and whole(root) == before and (root / '0003-x').is_dir())
                root, spec = fixture()
                before = whole(root)
                rc, out, err = run(root, 'close', ('0003-x',), dry_run=True, rewrite_refs=True)
                expect(f'(u) refs: --dry-run --rewrite-refs lists a {label} reference, writes nothing: rc={rc} '
                       f'{out!r} {err!r}',
                       rc == 0 and f'rewrite {where}' in out.splitlines() and whole(root) == before)
                root, spec = fixture()
                rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
                got = spec.read_text(encoding='utf-8')
                expect(f'(u) refs: --rewrite-refs rewrites a {label} reference in its own form: rc={rc} {out!r} '
                       f'{err!r} got={got!r}',
                       rc == 0 and out.endswith(f'; rewrote refs in {where}') and got == want(root)
                       and (root / '.0003-x').is_dir() and run(root, 'check')[0] == 0)

            # negative controls: a bare word and a path resolving elsewhere are not references
            for where, text in (('docs/spec.md', 'see 0003-x and other/0003-x/handoff.md and ../0003-x/\n'),
                                ('.sdlc/index.md', 'see 0003-x and other/0003-x/handoff.md\n')):
                root, spec = ref_repo(where=where, text=text)
                rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
                expect(f'(u) refs: {text.strip()!r} in {where} is not a reference: rc={rc} {out!r} {err!r}',
                       rc == 0 and 'rewrote' not in out and (root / '.0003-x').is_dir()
                       and spec.read_bytes() == text.encode('utf-8'))

            # a path into another tree that only contains .sdlc/0003-x is not a reference: the literal must
            # start a path token
            for text in ('see other/.sdlc/0003-x/handoff.md\n', 'see /elsewhere/repo/.sdlc/0003-x/handoff.md\n',
                         'see ../other/.sdlc/0003-x/handoff.md\n'):
                root, spec = ref_repo(text=text)
                rc, out, err = run(root, 'close', ('0003-x',))
                expect(f'(u) refs: other-tree path {text.strip()!r} does not block close: rc={rc} {out!r} {err!r}',
                       rc == 0 and 'rewrote' not in out and (root / '.0003-x').is_dir()
                       and spec.read_bytes() == text.encode('utf-8'))
                root, spec = ref_repo(text=text)
                rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
                expect(f'(u) refs: --rewrite-refs leaves other-tree path {text.strip()!r}: rc={rc} {out!r} {err!r}',
                       rc == 0 and 'rewrote' not in out and (root / '.0003-x').is_dir()
                       and spec.read_bytes() == text.encode('utf-8'))
            root, spec = ref_repo(text='see other/.sdlc/0003-x/a.md and .sdlc/0003-x/b.md\n')
            rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
            got = spec.read_text(encoding='utf-8')
            expect(f'(u) refs: --rewrite-refs rewrites only the real cite, not other/.sdlc/0003-x: rc={rc} {out!r} '
                   f'got={got!r}',
                   rc == 0 and out.endswith('; rewrote refs in docs/spec.md')
                   and got == 'see other/.sdlc/0003-x/a.md and .sdlc/.0003-x/b.md\n')

            # a literal that runs on into a longer folder name (0003-xy) is not a reference to 0003-x
            text = 'see .sdlc/0003-xy/handoff.md\n'
            root, spec = ref_repo(text=text)
            rc, out, err = run(root, 'close', ('0003-x',))
            expect(f'(u) refs: a cite of only the prefix sibling .sdlc/0003-xy does not block: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'rewrote' not in out and (root / '.0003-x').is_dir()
                   and spec.read_bytes() == text.encode('utf-8'))
            root, spec = ref_repo(text='see .sdlc/0003-x/a.md and .sdlc/0003-xy/b.md\n')
            rc, out, err = run(root, 'close', ('0003-x',), rewrite_refs=True)
            got = spec.read_text(encoding='utf-8')
            expect(f'(u) refs: --rewrite-refs rewrites only the 0003-x cite, not 0003-xy: rc={rc} {out!r} got={got!r}',
                   rc == 0 and got == 'see .sdlc/.0003-x/a.md and .sdlc/0003-xy/b.md\n')
            # the same through outside_refs and rewrite_files with both 0001-a and 0001-ab folders present
            d = pathlib.Path(tempfile.mkdtemp())
            (d / '.sdlc' / '0001-a').mkdir(parents=True)
            (d / '.sdlc' / '0001-ab').mkdir()
            (d / 'only.md').write_text('see .sdlc/0001-ab/handoff.md\n', encoding='utf-8')
            (d / 'both.md').write_text('see .sdlc/0001-a/x.md and .sdlc/0001-ab/y.md\n', encoding='utf-8')
            rgit(d, 'init', '-q')
            top, old, new, fs = outside_refs(d / '.sdlc', '0001-a')
            rewrite_files(top, fs, old, new)
            expect(f'(u) refs: outside_refs skips a cite of only .sdlc/0001-ab and rewrite_files leaves it: {fs!r}',
                   fs == ['both.md'] and (d / 'only.md').read_text(encoding='utf-8') == 'see .sdlc/0001-ab/handoff.md\n'
                   and (d / 'both.md').read_text(encoding='utf-8')
                   == 'see .sdlc/.0001-a/x.md and .sdlc/0001-ab/y.md\n')
            shutil.rmtree(d, ignore_errors=True)

        # (u) negative controls: plain mode, and a plain slug in numbered mode, never rename
        for label, mutate in (('plain mode', lambda r: None),
                              ('numbered, plain slug', config('ticket_folders: numbered\n'))):
            for kw in ({'reason': 'x'}, {}):
                root = case(both(mutate, filer('filer-L1.md', 'None', 'None')))
                rc, out, err = run(root, 'close', ('alpha',), **kw)
                expect(f'(u) {label} close {kw} does not rename alpha: rc={rc} {out!r} {err!r} tree={tree(root)}',
                       rc == 0 and status(root) == 'done' and not (root / '.alpha').exists()
                       and (root / 'alpha' / 'handoff.md').is_file() and 'moved' not in out)

        # (w) --ack-warnings closes past open warnings with a recorded reason; warned: 'step-2 verifier fail'
        today = datetime.date.today().isoformat()
        # (w1) ack close: done, the follow-up filed, a ## Closed section quoting the warning, check passes
        root = case(warned)
        rc, out, err = close_one(root, 1, ack_warnings='committed later')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(w1) --ack-warnings closes with open warnings: rc={rc} out={out!r} err={err!r} text={text!r}',
               rc == 0 and status(root) == 'done' and len(fresh(root, {'alpha', 'beta'})) == 1
               and out.endswith('; warnings acknowledged: committed later')
               and text.rstrip().endswith(f'## Closed\n\n{today}: warnings acknowledged: committed later\n\n'
                                          f'> step-2 verifier fail')
               and run(root, 'check')[0] == 0)
        # (w2) a multi-line Warnings section is quoted line by line, verbatim after `> `
        root = case(filer('filer-L1.md', '- step-2 verifier fail\n- nothing committed yet', '- Add retry to fetch'))
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='fixed on main')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(w2) multi-line warnings quoted line by line: rc={rc} {err!r} text={text!r}',
               rc == 0 and text.rstrip().endswith(f'{today}: warnings acknowledged: fixed on main\n\n'
                                                  f'> - step-2 verifier fail\n> - nothing committed yet'))
        # (w3) --ack-warnings with --force, (w4) with --reason, (w5) empty or whitespace: refuse, write nothing
        for label, args, kw, want in (('w3', ('alpha', True), {'ack_warnings': 'x'}, '--force'),
                                      ('w4', ('alpha',), {'ack_warnings': 'x', 'reason': 'y'}, '--reason'),
                                      ('w5', ('alpha',), {'ack_warnings': ''}, 'empty --ack-warnings'),
                                      ('w5', ('alpha',), {'ack_warnings': '   '}, 'empty --ack-warnings')):
            root = case(warned)
            before = snap(root)
            rc, _, err = run(root, 'close', args, **kw)
            expect(f'({label}) --ack-warnings {args} {kw} refuses and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '--ack-warnings' in err and want in err and err.endswith('nothing written')
                   and snap(root) == before and status(root) == 'proposed')
        # (w6) with Warnings None there is nothing to acknowledge: refuses, plain and dry run
        for kw in ({}, {'dry_run': True}):
            root = case(filer('filer-L1.md', 'None', '- Add retry to fetch'))
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), ack_warnings='x', **kw)
            expect(f'(w6) --ack-warnings with no open warnings refuses {kw}: rc={rc} {err!r}',
                   rc == 1 and 'rerun without --ack-warnings' in err and snap(root) == before)
        # (w7) dry run with --ack-warnings on open warnings lists the plan, ends with expect, writes nothing
        root = case(warned)
        before = snap(root)
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='committed later', dry_run=True)
        lines = out.splitlines()
        expect(f'(w7) --ack-warnings dry run: rc={rc} out={out!r} err={err!r}',
               rc == 0 and lines[-1] == 'expect ' + follow_digest(['Add retry to fetch'])
               and 'ack warnings: committed later' in lines and snap(root) == before)
        # (w8) --ack-warnings with --skip/--expect files only the unskipped follow-ups
        root = case(filer('filer-L1.md', 'step-2 verifier fail', three))
        rc, out, _ = run(root, 'close', ('alpha',), ack_warnings='ok', dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='ok', skip=[2], ticket=1, expect=token)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(w8) --ack-warnings --skip 2 --ticket 1 files 1, notes 3: rc={rc} out={out!r} err={err!r} '
               f'made={sorted(made)}',
               rc == 0 and status(root) == 'done'
               and sorted(m.get('title') for m in made.values()) == ['Add retry to fetch']
               and (notes(root) or '').endswith('\n- decide: Split the runner\n')
               and 'skipped by --skip: 2' in out and 'warnings acknowledged: ok' in out)
        # (w9) numbered: an ack close renames 0003-x to .0003-x and the moved handoff holds ## Closed
        root = case(both(numbered_x, filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch',
                                           slug='0003-x')))
        rc, out, err = run(root, 'close', ('0003-x',), numbered=True, ack_warnings='committed later')
        text = (root / '.0003-x' / 'handoff.md').read_text(encoding='utf-8') if (root / '.0003-x').is_dir() else ''
        expect(f'(w9) numbered ack close renames and keeps ## Closed: rc={rc} out={out!r} err={err!r} '
               f'tree={tree(root)}',
               rc == 0 and '; moved to .0003-x' in out and not (root / '0003-x').exists()
               and status(root, '.0003-x') == 'done' and '## Closed' in text
               and 'warnings acknowledged: committed later' in text and '> step-2 verifier fail' in text
               and run(root, 'check')[0] == 0)

        # archive: done and dropped NNNN- folders move to .NNNN-, a ready one stays
        def arch_base(root):
            for slug, st in (('alpha', 'done'), ('beta', 'dropped')):
                edit(root, slug, r'^status:.*$', f'status: {st}')
            (root / 'alpha').rename(root / '0001-alpha')
            (root / 'beta').rename(root / '0002-beta')
            run(root, 'new', ('feature', 'gamma'), numbered=True)
            run(root, 'roadmap')
        root = case(arch_base)
        before = snap(root)
        rc, out, err = run(root, 'archive', dry_run=True)
        expect(f'archive dry run lists renames and writes nothing: rc={rc} {out!r} {err!r}',
               rc == 0 and out.splitlines() == ['0001-alpha -> .0001-alpha', '0002-beta -> .0002-beta']
               and snap(root) == before)
        rc, out, err = run(root, 'archive')
        expect(f'archive moves done and dropped, keeps ready: rc={rc} {out!r} {err!r} tree={tree(root)}',
               rc == 0 and 'archived 2 folder(s)' in out and (root / '.0001-alpha').is_dir()
               and (root / '.0002-beta').is_dir() and (root / '0003-gamma').is_dir()
               and not (root / '0001-alpha').exists() and not (root / '0002-beta').exists())
        rc, out, err = run(root, 'check')
        expect(f'check passes after archive: rc={rc} {out!r} {err!r}', rc == 0)
        rc, out, err = run(root, 'archive')
        expect(f'second archive reports nothing to archive: rc={rc} {out!r}', rc == 0 and out == 'nothing to archive')
        root = case(both(arch_base, lambda r: (r / '.0002-beta').mkdir()))
        before = snap(root)
        rc, out, err = run(root, 'archive')
        expect(f'archive collision refuses and writes nothing: rc={rc} {err!r}',
               rc == 1 and '.0002-beta' in err and snap(root) == before and (root / '0001-alpha').is_dir())
        root = case(lambda r: edit(r, 'alpha', r'^status:.*$', 'status: done'))
        run(root, 'roadmap')
        before = snap(root)
        rc, out, err = run(root, 'archive')
        expect(f'archive in plain mode refuses and writes nothing: rc={rc} {err!r}',
               rc == 1 and 'numbered mode' in err and snap(root) == before and (root / 'alpha').is_dir())

        # archive runs close's reference scan: a cite refuses; --rewrite-refs rewrites it; --force leaves it
        def arch_ref(where='docs/spec.md', text='see .sdlc/0001-alpha/handoff.md\n', git=True):
            root = case(arch_base)
            spec = root.parent / where
            spec.parent.mkdir(parents=True, exist_ok=True)
            spec.write_text(text, encoding='utf-8')
            if git:
                rgit(root.parent, 'init', '-q')
                rgit(root.parent, 'add', '-A')
                rgit(root.parent, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                     'commit', '--no-verify', '-qm', 'x')
            return root, spec

        # number converts a plain root; the refusals write nothing
        if shutil.which('git') is not None:
            root, spec = arch_ref(text='see .sdlc/alpha/handoff.md and ../.sdlc/beta\n')
            for slug, new in (('0001-alpha', 'alpha'), ('0002-beta', 'beta')):
                (root / slug).rename(root / new)
            (root / 'config').unlink()
            (root / 'alpha' / 'note.md').write_text('in .sdlc/alpha/step-1\n', encoding='utf-8')
            before = whole(root)
            rc, out, err = run(root, 'number', dry_run=True)
            expect(f'number dry run lists and writes nothing: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'alpha -> 0001-alpha' in out and 'rewrite docs/spec.md' in out
                   and whole(root) == before)
            rc, out, err = run(root, 'number')
            expect(f'number renames, rewrites, persists mode: rc={rc} {out!r} {err!r} tree={tree(root)}',
                   rc == 0 and (root / '0001-alpha').is_dir() and (root / '0002-beta').is_dir()
                   and (root / '0003-gamma').is_dir() and config_numbered(root)
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/0001-alpha/handoff.md and ../.sdlc/0002-beta\n'
                   and (root / '0001-alpha' / 'note.md').read_text(encoding='utf-8') == 'in .sdlc/0001-alpha/step-1\n'
                   and run(root, 'check')[0] == 0)
            root = case(both(arch_base, lambda r: ((r / '0001-alpha').rename(r / 'alpha'),
                                                   (r / '0001-alpha').mkdir())))
            before = snap(root)
            rc, out, err = run(root, 'number')
            expect(f'number collision refuses and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '0001-alpha' in err and snap(root) == before and (root / 'alpha').is_dir())

        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the archive reference cases')
        else:
            for label, kw in (('committed', {}), ('--dry-run', {'dry_run': True})):
                root, spec = arch_ref()
                before = whole(root)
                rc, out, err = run(root, 'archive', **kw)
                expect(f'archive refs: a {label} reference refuses, names docs/spec.md, writes nothing: rc={rc} '
                       f'{out!r} {err!r}',
                       rc == 1 and 'docs/spec.md' in err and '.sdlc/0001-alpha' in err and '--rewrite-refs' in err
                       and '--force' in err and err.endswith('nothing written') and whole(root) == before
                       and (root / '0001-alpha').is_dir())

            root, spec = arch_ref()
            rc, out, err = run(root, 'archive', rewrite_refs=True)
            expect(f'archive refs: --rewrite-refs rewrites and renames: rc={rc} {out!r} {err!r}',
                   rc == 0 and out.endswith('; rewrote refs in docs/spec.md') and (root / '.0001-alpha').is_dir()
                   and (root / '.0002-beta').is_dir()
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/.0001-alpha/handoff.md\n'
                   and run(root, 'check')[0] == 0)

            root, spec = arch_ref()
            rc, out, err = run(root, 'archive', force=True)
            expect(f'archive refs: --force renames and leaves the reference: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'rewrote' not in out and (root / '.0001-alpha').is_dir()
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/0001-alpha/handoff.md\n')

            root, spec = arch_ref()
            before = whole(root)
            rc, out, err = run(root, 'archive', dry_run=True, rewrite_refs=True)
            expect(f'archive refs: --dry-run --rewrite-refs lists renames then the file, writes nothing: rc={rc} '
                   f'{out!r} {err!r}',
                   rc == 0 and out.splitlines() == ['0001-alpha -> .0001-alpha', '0002-beta -> .0002-beta',
                                                    'rewrite docs/spec.md']
                   and whole(root) == before)

            root, spec = arch_ref()
            before = whole(root)
            rc, out, err = run(root, 'archive', dry_run=True, force=True)
            expect(f'archive refs: --dry-run --force lists only the renames, writes nothing: rc={rc} {out!r} {err!r}',
                   rc == 0 and out.splitlines() == ['0001-alpha -> .0001-alpha', '0002-beta -> .0002-beta']
                   and whole(root) == before)

            # a file in one archived folder citing another archived folder is rewritten before both renames
            root, spec = arch_ref(where='.sdlc/0001-alpha/notes.md', text='see .sdlc/0002-beta/handoff.md\n')
            before = whole(root)
            rc, out, err = run(root, 'archive')
            expect(f'archive refs: a cite between two archived folders refuses: rc={rc} {err!r}',
                   rc == 1 and '.sdlc/0001-alpha/notes.md' in err and whole(root) == before)
            rc, out, err = run(root, 'archive', rewrite_refs=True)
            got = (root / '.0001-alpha' / 'notes.md').read_text(encoding='utf-8')
            expect(f'archive refs: --rewrite-refs rewrites a cite between two archived folders: rc={rc} {out!r} '
                   f'{err!r} notes={got!r}',
                   rc == 0 and got == 'see .sdlc/.0002-beta/handoff.md\n' and (root / '.0002-beta').is_dir()
                   and out.endswith('; rewrote refs in .sdlc/0001-alpha/notes.md'))

            # archive finds and rewrites references written relative to the citing file, or absolute
            renames = ['0001-alpha -> .0001-alpha', '0002-beta -> .0002-beta']
            for label, where, text, want in (
                    ('../ from another ticket folder', '.sdlc/0003-gamma/notes.md',
                     'see ../0001-alpha/filer-L1.md\n', lambda root: 'see ../.0001-alpha/filer-L1.md\n'),
                    ('./ from the ticket root', '.sdlc/index.md', '[a](./0001-alpha/handoff.md)\n',
                     lambda root: '[a](./.0001-alpha/handoff.md)\n'),
                    ('absolute', 'docs/spec.md', None, lambda root: f'see {root}/.0001-alpha/handoff.md\n')):
                def afixture():
                    root, spec = arch_ref(where=where, text=text or '')
                    if text is None:
                        spec.write_text(f'see {root}/0001-alpha/handoff.md\n', encoding='utf-8')
                    return root, spec

                root, spec = afixture()
                before = whole(root)
                rc, out, err = run(root, 'archive')
                expect(f'archive refs: a {label} reference refuses, names {where}, writes nothing: rc={rc} '
                       f'{out!r} {err!r}',
                       rc == 1 and where in err and err.endswith('nothing written') and whole(root) == before
                       and (root / '0001-alpha').is_dir())
                root, spec = afixture()
                before = whole(root)
                rc, out, err = run(root, 'archive', dry_run=True, rewrite_refs=True)
                expect(f'archive refs: --dry-run --rewrite-refs lists a {label} reference, writes nothing: '
                       f'rc={rc} {out!r} {err!r}',
                       rc == 0 and out.splitlines() == renames + [f'rewrite {where}'] and whole(root) == before)
                root, spec = afixture()
                rc, out, err = run(root, 'archive', rewrite_refs=True)
                got = spec.read_text(encoding='utf-8')
                expect(f'archive refs: --rewrite-refs rewrites a {label} reference in its own form: rc={rc} '
                       f'{out!r} {err!r} got={got!r}',
                       rc == 0 and out.endswith(f'; rewrote refs in {where}') and got == want(root)
                       and (root / '.0001-alpha').is_dir() and run(root, 'check')[0] == 0)

            # negative controls: a bare word and a path resolving elsewhere do not block the archive
            text = 'see 0001-alpha and other/0001-alpha/handoff.md and ../0001-alpha/\n'
            root, spec = arch_ref(text=text)
            rc, out, err = run(root, 'archive', rewrite_refs=True)
            expect(f'archive refs: a bare word and paths resolving elsewhere are not references: rc={rc} {out!r} '
                   f'{err!r}',
                   rc == 0 and 'rewrote' not in out and (root / '.0001-alpha').is_dir()
                   and spec.read_bytes() == text.encode('utf-8'))

            # a path into another tree that only contains .sdlc/0001-alpha does not block the archive
            text = ('see other/.sdlc/0001-alpha/handoff.md and /elsewhere/repo/.sdlc/0001-alpha/handoff.md '
                    'and ../other/.sdlc/0001-alpha/handoff.md\n')
            for kw in ({}, {'rewrite_refs': True}):
                root, spec = arch_ref(text=text)
                rc, out, err = run(root, 'archive', **kw)
                expect(f'archive refs: other-tree paths are not references {kw}: rc={rc} {out!r} {err!r}',
                       rc == 0 and 'rewrote' not in out and (root / '.0001-alpha').is_dir()
                       and spec.read_bytes() == text.encode('utf-8'))
            root, spec = arch_ref(text='see other/.sdlc/0001-alpha/a.md and .sdlc/0001-alpha/b.md\n')
            rc, out, err = run(root, 'archive', rewrite_refs=True)
            got = spec.read_text(encoding='utf-8')
            expect(f'archive refs: --rewrite-refs rewrites only the real cite, not other/.sdlc/0001-alpha: rc={rc} '
                   f'{out!r} got={got!r}',
                   rc == 0 and out.endswith('; rewrote refs in docs/spec.md')
                   and got == 'see other/.sdlc/0001-alpha/a.md and .sdlc/.0001-alpha/b.md\n')

            # a literal that runs on into a longer folder name (0001-alphax) is left alone by archive
            text = 'see .sdlc/0001-alpha/a.md and .sdlc/0001-alphax/b.md\n'
            root, spec = arch_ref(text=text)
            rc, out, err = run(root, 'archive', rewrite_refs=True)
            got = spec.read_text(encoding='utf-8')
            expect(f'archive refs: --rewrite-refs rewrites only the 0001-alpha cite, not 0001-alphax: rc={rc} '
                   f'{out!r} got={got!r}',
                   rc == 0 and got == 'see .sdlc/.0001-alpha/a.md and .sdlc/0001-alphax/b.md\n')
            root, spec = arch_ref(text='see .sdlc/0001-alphax/b.md\n')
            rc, out, err = run(root, 'archive')
            expect(f'archive refs: a cite of only .sdlc/0001-alphax does not block: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'rewrote' not in out
                   and spec.read_text(encoding='utf-8') == 'see .sdlc/0001-alphax/b.md\n')

        # outside git there is no scan: a citing file does not block the archive and is left alone
        root, spec = arch_ref(git=False)
        rc, out, err = run(root, 'archive')
        expect(f'archive refs: outside git a reference does not block: rc={rc} {out!r} {err!r}',
               rc == 0 and (root / '.0001-alpha').is_dir()
               and spec.read_text(encoding='utf-8') == 'see .sdlc/0001-alpha/handoff.md\n')

        # ---- worktrees: new and close stamp ids above the max across every git worktree's same-relative root ----
        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the worktree id cases')
        else:
            genv = {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')}

            def git(cwd, *args):
                p = subprocess.run(['git', '-C', str(cwd), *args], env=genv, capture_output=True, text=True)
                if p.returncode:
                    raise AssertionError(f'selftest git fixture failed: git {" ".join(args)}: {p.stderr.strip()}')

            def tid(root, slug):
                return dict(load(root)).get(slug, {}).get('id')

            wtmp = pathlib.Path(tmp) / 'worktrees'
            wtmp.mkdir()
            main_dir, nosdlc_dir = wtmp / 'main', wtmp / 'nosdlc'
            m_root, w_root, n_root = main_dir / '.sdlc', wtmp / 'wt' / '.sdlc', nosdlc_dir / '.sdlc'
            git(wtmp, 'init', '-q', 'main')
            rc, _, err = run(m_root, 'new', ('feature', 'alpha'))
            expect(f'worktree: first id in a fresh repo is T-0001: rc={rc} {err!r}', rc == 0 and tid(m_root, 'alpha')
                   == 'T-0001')
            git(main_dir, 'add', '-A')
            git(main_dir, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                'commit', '--no-verify', '-qam', 'alpha')
            git(main_dir, 'worktree', 'add', '-q', '../wt', '-b', 'wt')
            git(main_dir, 'worktree', 'add', '-q', '../nosdlc', '-b', 'nosdlc')
            shutil.rmtree(n_root)  # a worktree with no .sdlc dir yet: skipped, never an error
            rc_b, _, err_b = run(m_root, 'new', ('feature', 'beta'))
            rc_g, _, err_g = run(w_root, 'new', ('feature', 'gamma'))
            expect(f'worktree: beta in main is T-0002, then gamma in wt is T-0003 (not T-0002): rc={rc_b},{rc_g} '
                   f'{err_b!r} {err_g!r} beta={tid(m_root, "beta")!r} gamma={tid(w_root, "gamma")!r}',
                   rc_b == 0 and rc_g == 0 and err_b == err_g == '' and tid(m_root, 'beta') == 'T-0002'
                   and tid(w_root, 'gamma') == 'T-0003')
            # plain close in wt: main's delta (T-0004) sits above wt's max (T-0003), so the follow-up is T-0005
            rc, _, err = run(m_root, 'new', ('feature', 'delta'))
            expect(f'worktree: delta in main counts wt gamma, so it is T-0004: rc={rc} {err!r} '
                   f'got={tid(m_root, "delta")!r}', rc == 0 and tid(m_root, 'delta') == 'T-0004')
            filer('filer-L1.md', 'None', '- Add retry to fetch', slug='gamma')(w_root)
            rc, out, err = close_one(w_root, 1, slug='gamma')
            made = fresh(w_root, {'alpha', 'gamma'})
            expect(f'worktree: plain close in wt stamps its follow-up above main T-0004, as T-0005: rc={rc} {out!r} '
                   f'{err!r} made={made}',
                   rc == 0 and [m.get('id') for m in made.values()] == ['T-0005'] and run(w_root, 'check')[0] == 0)
            # numbered close in wt: main's epsilon (T-0006) sits above wt's max (T-0005); folder 0007- matches T-0007
            rc, _, err = run(m_root, 'new', ('feature', 'epsilon'))
            expect(f'worktree: epsilon in main is T-0006: rc={rc} {err!r} got={tid(m_root, "epsilon")!r}',
                   rc == 0 and tid(m_root, 'epsilon') == 'T-0006')
            filer('filer-L1.md', 'None', '- Quote the docs', slug='alpha')(w_root)
            rc, out, err = close_one(w_root, 1, numbered=True)
            made = fresh(w_root, {'alpha', 'gamma', 'add-retry-to-fetch'})
            expect(f'worktree: numbered close in wt names the follow-up 0007-quote-the-docs with id T-0007: rc={rc} '
                   f'{out!r} {err!r} made={made}',
                   rc == 0 and {s: m.get('id') for s, m in made.items()} == {'0007-quote-the-docs': 'T-0007'}
                   and run(w_root, 'check')[0] == 0)
            # the worktree with no .sdlc yet: new there creates the root and still counts every other tree
            rc, _, err = run(n_root, 'new', ('feature', 'zeta'))
            expect(f'worktree: first ticket in a worktree with no .sdlc yet is T-0008: rc={rc} {err!r} '
                   f'got={tid(n_root, "zeta")!r}', rc == 0 and err == '' and tid(n_root, 'zeta') == 'T-0008')
            # close in main with the filer record only in wt (alpha, filed there above): refuse, name wt's folder
            before = snap(m_root)
            rc, _, err = run(m_root, 'close', ('alpha',))
            expect(f'worktree: close in main names the wt folder holding the filer record, writes nothing: rc={rc} '
                   f'{err!r}', rc == 1 and snap(m_root) == before and str((w_root / 'alpha').resolve()) in err
                   and '/file' in err and 'nothing written' in err)
            # close --dry-run lists open tickets found only in another worktree, after the local ones
            d_dir = wtmp / 'dr'
            d_root, dw_root = d_dir / '.sdlc', wtmp / 'wtdr' / '.sdlc'
            git(wtmp, 'init', '-q', 'dr')
            for sl in ('alpha', 'beta', 'delta'):
                run(d_root, 'new', ('feature', sl, sl.title()))
            git(d_dir, 'add', '-A')
            git(d_dir, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                'commit', '--no-verify', '-qm', 'x')
            git(d_dir, 'worktree', 'add', '-q', '../wtdr', '-b', 'wtdr')
            run(dw_root, 'new', ('feature', 'gamma', 'Gamma'))
            bh = d_root / 'beta' / 'handoff.md'
            bh.write_text(re.sub(r'(?m)^status: \w+', 'status: done', bh.read_text()), encoding='utf-8')
            filer('filer-L1.md', 'None', 'None', slug='alpha')(d_root)
            before = snap(d_root), snap(dw_root)
            rc, out, err = run(d_root, 'close', ('alpha',), dry_run=True)
            ol = out.strip().splitlines()
            expect(f'worktree dry-run: other-worktree gamma listed once as (worktree wtdr), local delta once, '
                   f'locally done beta absent, digest unchanged, nothing written: rc={rc} {out!r} {err!r}',
                   rc == 0 and ol[1:] == ['open T-0003 Delta [delta]', 'open T-0004 Gamma [gamma] (worktree wtdr)',
                                          'expect e3b0c44298fc']
                   and (snap(d_root), snap(dw_root)) == before)
            # with follow-ups present, the digest still covers only the ordered follow-ups, not the open lines
            filer('filer-L1.md', 'None', '- A\n- B', slug='delta')(d_root)
            before = snap(d_root), snap(dw_root)
            rc, out, err = run(d_root, 'close', ('delta',), dry_run=True)
            ol = out.strip().splitlines()
            expect(f'worktree dry-run with follow-ups: gamma listed as (worktree wtdr), digest covers only the '
                   f'follow-ups, nothing written: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'open T-0004 Gamma [gamma] (worktree wtdr)' in ol
                   and ol[1:3] == ['1. decide: A note', '2. decide: B note']
                   and ol[-1] == 'expect ' + follow_digest(['A', 'B'])
                   and (snap(d_root), snap(dw_root)) == before)

            # ---- external_branch: ids committed on a registered branch count, read from git objects ----
            def commit(cwd, msg):
                git(cwd, 'add', '-A')
                git(cwd, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                    'commit', '--no-verify', '-qm', msg)

            # (i) config parsing: order kept, duplicates once, comments and blanks skipped, numbered still holds
            cfg = wtmp / 'cfg'
            cfg.mkdir()
            (cfg / 'config').write_text('# external_branch: hidden\nticket_folders: numbered\n\n'
                                        'external_branch: codex/x\n   \nexternal_branch: ext # note\n'
                                        'external_branch: codex/x\n', encoding='utf-8')
            got = external_branches(cfg)
            expect(f'external: config yields the two names in order, numbered still holds: {got!r}',
                   got == ['codex/x', 'ext'] and config_numbered(cfg))
            expect('external: a missing config yields []', external_branches(wtmp / 'nocfg') == [])
            # T-0374: hash_bound lines are one glob list (several per line, order kept, duplicates once, comments skipped)
            (cfg / 'config').write_text('# hash_bound: hidden\nexternal_branch: ext\nhash_bound: gen  # generated\n'
                                        '  hash_bound: a/** b/*.json\nhash_bound: gen\nhash_bound:   # none\n', encoding='utf-8')
            got = hash_bound_globs(cfg)
            expect(f'hash_bound: config yields the three globs in order, external_branch untouched: {got!r}',
                   got == ['gen', 'a/**', 'b/*.json'] and external_branches(cfg) == ['ext'])
            expect('hash_bound: a missing config yields []', hash_bound_globs(wtmp / 'nocfg') == [])

            # (ii) branch_tickets reads a branch checked out nowhere, by load()'s folder rule
            e_dir = wtmp / 'ext'
            e_root = e_dir / '.sdlc'
            git(wtmp, 'init', '-q', '-b', 'main', 'ext')
            (e_dir / 'README').write_text('x\n', encoding='utf-8')
            commit(e_dir, 'readme')
            git(e_dir, 'checkout', '-q', '-b', 'ext')
            fm = ('---\nid: {}\ntitle: "t"\ntype: chore\nstatus: {}\nsize: S\npriority: P2\ndepends: []\n'
                  'created: 2026-01-01\n---\n')
            for d, text in (('0002-b', fm.format('T-0002', 'ready')), ('.0003-c', fm.format('T-0003', 'done')),
                            ('_templates', fm.format('T-0009', 'ready')), ('plain', '## Goal\n')):
                (e_root / d).mkdir(parents=True)
                (e_root / d / 'handoff.md').write_text(text, encoding='utf-8')
            commit(e_dir, 'ext tickets')
            git(e_dir, 'checkout', '-q', 'main')
            got = [(sl, m.get('id'), m.get('status')) for sl, m in branch_tickets(e_root, 'ext')]
            expect(f'external: branch_tickets reads exactly the two tickets on ext, from git objects: {got!r}',
                   got == [('.0003-c', 'T-0003', 'done'), ('0002-b', 'T-0002', 'ready')] and not e_root.exists())
            expect('external: branch_tickets on a missing branch is []', branch_tickets(e_root, 'nosuch') == [])
            expect('external: branch_tickets outside git is []',
                   branch_tickets(pathlib.Path(tmp) / 'noext' / '.sdlc', 'ext') == [])

            # (iii) case (b): T-0002 committed only on ext; registered, new and close mint above it
            b_dir = wtmp / 'extb'
            b_root = b_dir / '.sdlc'
            git(wtmp, 'init', '-q', '-b', 'main', 'extb')
            run(b_root, 'new', ('feature', 'a'))
            commit(b_dir, 'a')
            git(b_dir, 'checkout', '-q', '-b', 'ext')
            rc, _, err = run(b_root, 'new', ('feature', 'b'))
            expect(f'external: fixture b on ext is T-0002: rc={rc} {err!r}', rc == 0 and tid(b_root, 'b') == 'T-0002')
            commit(b_dir, 'b')
            git(b_dir, 'checkout', '-q', 'main')
            filer('filer-L1.md', 'None', '- Add retry to fetch', slug='a')(b_root)
            copies = {}
            for name in ('close', 'bare', 'bare-close'):
                shutil.copytree(b_dir, wtmp / f'extb-{name}', symlinks=True)
                copies[name] = wtmp / f'extb-{name}' / '.sdlc'
            for r in (b_root, copies['close']):
                (r / 'config').write_text('external_branch: ext\n', encoding='utf-8')
            rc, _, err = run(b_root, 'new', ('feature', 'z'))
            expect(f'external: registered, new in main mints T-0003 above ext T-0002: rc={rc} {err!r} '
                   f'got={tid(b_root, "z")!r}', rc == 0 and err == '' and tid(b_root, 'z') == 'T-0003')
            rc, out, err = close_one(copies['close'], 1, slug='a')
            made = fresh(copies['close'], {'a'})
            expect(f'external: registered, close --ticket 1 --expect mints its follow-up above ext T-0002, as '
                   f'T-0003: rc={rc} {out!r} {err!r} made={made}',
                   rc == 0 and [m.get('id') for m in made.values()] == ['T-0003'])
            rc, _, err = run(copies['bare'], 'new', ('feature', 'z'))
            expect(f'external: negative control, unregistered, new mints the colliding T-0002: rc={rc} {err!r}',
                   rc == 0 and tid(copies['bare'], 'z') == 'T-0002')
            rc, out, err = close_one(copies['bare-close'], 1, slug='a')
            made = fresh(copies['bare-close'], {'a'})
            expect(f'external: negative control, unregistered, the close follow-up collides as T-0002: rc={rc} '
                   f'{out!r} {err!r} made={made}', rc == 0 and [m.get('id') for m in made.values()] == ['T-0002'])
            rc, out, err = run(b_root, 'check')
            expect(f'external: check with a registered local branch has no external warning: rc={rc} {out!r}',
                   rc == 0 and 'external_branch' not in out)

            # (iv) a registered name with no local branch: check warns, exit 0; new is unaffected
            n_dir = wtmp / 'extn'
            nn_root = n_dir / '.sdlc'
            git(wtmp, 'init', '-q', 'extn')
            nn_root.mkdir()
            (nn_root / 'config').write_text('external_branch: nosuch\n', encoding='utf-8')
            rc, out, err = run(nn_root, 'check')
            expect(f'external: check warns on a registered branch that is not local, exit 0: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'warning: external_branch nosuch is not a local branch' in out.splitlines())
            rc, _, err = run(nn_root, 'new', ('feature', 'q'))
            expect(f'external: new with an unknown registered branch mints T-0001, empty stderr: rc={rc} {err!r} '
                   f'got={tid(nn_root, "q")!r}', rc == 0 and err == '' and tid(nn_root, 'q') == 'T-0001')
            loose = pathlib.Path(tmp) / 'extloose' / '.sdlc'
            loose.mkdir(parents=True)
            (loose / 'config').write_text('external_branch: nosuch\n', encoding='utf-8')
            rc, out, err = run(loose, 'check')
            expect(f'external: outside git check gives no external warning: rc={rc} {out!r}',
                   rc == 0 and 'external_branch' not in out)

            # (v) ticket_root across trees: each other worktree's and each registered branch's ticket root is
            # resolved by that tree's or branch's own config. main is the default layout; the worktree's
            # .sdlc/config says ticket_root: tickets, so its tickets live under .sdlc/tickets/
            r_dir = wtmp / 'trw'
            r_root, rw_root = r_dir / '.sdlc', wtmp / 'trw-wt' / '.sdlc'
            git(wtmp, 'init', '-q', '-b', 'main', 'trw')
            run(r_root, 'new', ('feature', 'alpha', 'Alpha'))
            commit(r_dir, 'alpha')
            git(r_dir, 'worktree', 'add', '-q', '../trw-wt', '-b', 'trw-wt')
            (rw_root / 'tickets').mkdir()
            (rw_root / 'alpha').rename(rw_root / 'tickets' / 'alpha')
            (rw_root / 'config').write_text('ticket_root: tickets\n', encoding='utf-8')
            rc_b, _, err_b = run(rw_root, 'new', ('feature', 'beta', 'Beta'))
            rc_g, _, err_g = run(r_root, 'new', ('feature', 'gamma', 'Gamma'))
            rc_d, _, err_d = run(rw_root, 'new', ('feature', 'delta', 'Delta'))
            got = (tid(rw_root / 'tickets', 'beta'), tid(r_root, 'gamma'), tid(rw_root / 'tickets', 'delta'))
            pairs = [(w.resolve(), t) for w, t in other_ticket_dirs(r_root)]
            expect(f'ticket_root worktree: new in either tree mints above the other tree\'s max (beta T-0002 in the '
                   f'worktree tickets/, gamma T-0003 in main, delta T-0004 in the worktree): rc={rc_b},{rc_g},{rc_d} '
                   f'{err_b!r} {err_g!r} {err_d!r} got={got!r} pairs={pairs!r}',
                   rc_b == rc_g == rc_d == 0 and got == ('T-0002', 'T-0003', 'T-0004')
                   and pairs == [((wtmp / 'trw-wt').resolve(), (rw_root / 'tickets').resolve())])
            # the no-filer refusal in main names the worktree's tickets/<slug> folder holding the filer record
            (rw_root / 'tickets' / 'alpha' / 'filer-L1.md').write_text(
                '## Warnings\nNone\n\n## Follow-ups\nNone\n', encoding='utf-8')
            before = snap(r_root)
            rc, _, err = run(r_root, 'close', ('alpha',))
            expect(f'ticket_root worktree: close in main names <worktree>/.sdlc/tickets/alpha, writes nothing: '
                   f'rc={rc} {err!r}', rc == 1 and snap(r_root) == before
                   and str((rw_root / 'tickets' / 'alpha').resolve()) in err and 'nothing written' in err)
            # close --dry-run in main lists the open tickets found only in the worktree's tickets/
            filer('filer-L1.md', 'None', 'None', slug='alpha')(r_root)
            before = snap(r_root), snap(rw_root)
            rc, out, err = run(r_root, 'close', ('alpha',), dry_run=True)
            ol = out.strip().splitlines()
            expect(f'ticket_root worktree: close --dry-run in main lists beta and delta as (worktree trw-wt), '
                   f'nothing written: rc={rc} {out!r} {err!r}',
                   rc == 0 and ol[1:] == ['open T-0003 Gamma [gamma]', 'open T-0002 Beta [beta] (worktree trw-wt)',
                                          'open T-0004 Delta [delta] (worktree trw-wt)', 'expect e3b0c44298fc']
                   and (snap(r_root), snap(rw_root)) == before)
            # an external branch whose committed config says ticket_root: tickets is counted by new on main
            x_dir = wtmp / 'trx'
            x_root = x_dir / '.sdlc'
            git(wtmp, 'init', '-q', '-b', 'main', 'trx')
            run(x_root, 'new', ('feature', 'alpha'))
            commit(x_dir, 'alpha')
            git(x_dir, 'checkout', '-q', '-b', 'ext')
            (x_root / 'tickets').mkdir()
            (x_root / 'alpha').rename(x_root / 'tickets' / 'alpha')
            (x_root / 'config').write_text('ticket_root: tickets\n', encoding='utf-8')
            rc, _, err = run(x_root, 'new', ('feature', 'beta'))
            expect(f'ticket_root external: fixture beta on ext is T-0002 under tickets/: rc={rc} {err!r}',
                   rc == 0 and tid(x_root / 'tickets', 'beta') == 'T-0002')
            commit(x_dir, 'beta')
            git(x_dir, 'checkout', '-q', 'main')
            shutil.copytree(x_dir, wtmp / 'trx-bare', symlinks=True)
            xb_root = wtmp / 'trx-bare' / '.sdlc'
            got = [(sl, m.get('id')) for sl, m in branch_tickets(x_root, 'ext')]
            expect(f'ticket_root external: branch_tickets reads <branch>:.sdlc/tickets, folder names kept: {got!r}',
                   got == [('alpha', 'T-0001'), ('beta', 'T-0002')])
            (x_root / 'config').write_text('external_branch: ext\n', encoding='utf-8')
            rc, _, err = run(x_root, 'new', ('feature', 'gamma'))
            expect(f'ticket_root external: registered, new on main mints T-0003 above ext tickets/beta T-0002: '
                   f'rc={rc} {err!r} got={tid(x_root, "gamma")!r}',
                   rc == 0 and err == '' and tid(x_root, 'gamma') == 'T-0003')
            rc, _, err = run(xb_root, 'new', ('feature', 'gamma'))
            expect(f'ticket_root external: negative control, no external_branch line, new mints the colliding '
                   f'T-0002: rc={rc} {err!r} got={tid(xb_root, "gamma")!r}',
                   rc == 0 and tid(xb_root, 'gamma') == 'T-0002')

        # outside git (no worktrees to consult) the local root decides: the first id is T-0001
        solo = pathlib.Path(tmp) / 'solo' / '.sdlc'
        rc, _, err = run(solo, 'new', ('feature', 'solo'))
        expect(f'outside git the first id is T-0001, no stderr: rc={rc} {err!r} got={dict(load(solo)).get("solo")}',
               rc == 0 and err == '' and dict(load(solo)).get('solo', {}).get('id') == 'T-0001')

        # outside git, close --dry-run lists only local open tickets, with no worktree lines
        run(solo, 'new', ('feature', 'solo2', 'Solo2'))
        filer('filer-L1.md', 'None', 'None', slug='solo')(solo)
        rc, out, err = run(solo, 'close', ('solo',), dry_run=True)
        expect(f'outside git the worktree dry-run output is local only: rc={rc} {out!r} {err!r}',
               rc == 0 and out.strip().splitlines() == ['T-0001 dry run: 0 proposed follow-up(s); nothing written',
                                                        'open T-0002 Solo2 [solo2]', 'expect e3b0c44298fc'])

        empty = pathlib.Path(tmp) / 'empty' / '.sdlc'
        rc, out, _ = run(empty, 'check')
        expect('zero tickets and no roadmap passes', rc == 0 and out.startswith('ok: 0 tickets'))

        # ---- ticket_root: tickets: ticket folders live in <root>/tickets; roadmap, config, notes, _templates stay ----
        def tr_root(name, extra=''):
            r = pathlib.Path(tmp) / name / '.sdlc'
            r.mkdir(parents=True)
            (r / 'config').write_text('ticket_root: tickets\n' + extra, encoding='utf-8')
            return r

        def tr_text(path):
            return path.read_text(encoding='utf-8') if path.is_file() else ''

        def tr_filer(root, folder, follow):
            (root / 'tickets' / folder / 'filer-L1.md').write_text(
                f'## Warnings\nNone\n\n## Follow-ups\n{follow}\n', encoding='utf-8')

        tr = tr_root('tr-new')
        rc, out, err = run(tr, 'new', ('feature', 'alpha', 'Alpha'))
        rm = tr_text(tr / 'roadmap.md')
        expect(f'ticket_root: new lands in tickets/alpha and the roadmap links tickets/alpha/handoff.md: rc={rc} '
               f'{out!r} {err!r} {rm!r}',
               rc == 0 and ticket_dir(tr) == tr / 'tickets' and (tr / 'tickets' / 'alpha' / 'handoff.md').is_file()
               and not (tr / 'alpha').exists() and '| [alpha](tickets/alpha/handoff.md) |' in rm
               and not (tr / 'tickets' / 'roadmap.md').exists() and run(tr, 'check')[0] == 0)
        (tr / 'task-x').mkdir()
        (tr / 'task-x' / 'handoff.md').write_text('## Goal\nNo front matter here.\n', encoding='utf-8')
        rc, out, err = run(tr, 'check')
        expect(f'ticket_root: a plain task at <root> is not a stray: rc={rc} {out!r} {err!r}',
               rc == 0 and out.startswith('ok: 1 tickets'))

        tr = tr_root('tr-close')
        run(tr, 'new', ('feature', 'alpha', 'Alpha'))
        tr_filer(tr, 'alpha', '- note: Keep this\n- decide: Add a gizmo')
        rc, out, _ = run(tr, 'close', ('alpha',), dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else 'none'
        rc, out, err = run(tr, 'close', ('alpha',), ticket=2, expect=token)
        got = dict(load(tr / 'tickets'))
        expect(f'ticket_root: plain close sets done, files the follow-up in tickets/ and notes at <root>: rc={rc} '
               f'{out!r} {err!r} tickets={sorted(got)}',
               rc == 0 and got.get('alpha', {}).get('status') == 'done'
               and (tr / 'tickets' / 'add-a-gizmo' / 'handoff.md').is_file() and not (tr / 'add-a-gizmo').exists()
               and 'note: Keep this' in tr_text(tr / 'notes.md') and not (tr / 'tickets' / 'notes.md').exists()
               and run(tr, 'check')[0] == 0)

        tr = tr_root('tr-nclose', 'ticket_folders: numbered\n')
        run(tr, 'new', ('feature', 'alpha', 'Alpha'))
        tr_filer(tr, '0001-alpha', 'None')
        rc, out, err = run(tr, 'close', ('0001-alpha',))
        expect(f'ticket_root: numbered close renames to tickets/.0001-alpha: rc={rc} {out!r} {err!r}',
               rc == 0 and (tr / 'tickets' / '.0001-alpha' / 'handoff.md').is_file()
               and not (tr / 'tickets' / '0001-alpha').exists() and not (tr / '.0001-alpha').exists()
               and '(tickets/.0001-alpha/handoff.md)' in tr_text(tr / 'roadmap.md') and run(tr, 'check')[0] == 0)

        if shutil.which('git'):
            tr = tr_root('tr-git', 'ticket_folders: numbered\n')
            tenv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
            subprocess.run(['git', '-C', str(tr.parent), 'init', '-q'], env=tenv, capture_output=True)
            run(tr, 'new', ('feature', 'alpha', 'Alpha'))
            tr_filer(tr, '0001-alpha', 'None')
            spec = tr.parent / 'spec.md'
            spec.write_text('see .sdlc/tickets/0001-alpha/handoff.md\n', encoding='utf-8')
            rc, _, err = run(tr, 'close', ('0001-alpha',))
            expect(f'ticket_root: a cite of .sdlc/tickets/0001-alpha refuses close, naming spec.md and never the '
                   f'roadmap: rc={rc} {err!r}',
                   rc == 1 and 'spec.md' in err and 'roadmap.md' not in err and '.sdlc/tickets/0001-alpha' in err
                   and (tr / 'tickets' / '0001-alpha').is_dir())
            rc, out, err = run(tr, 'close', ('0001-alpha',), rewrite_refs=True)
            expect(f'ticket_root: close --rewrite-refs rewrites the cite to .sdlc/tickets/.0001-alpha: rc={rc} '
                   f'{out!r} {err!r} {tr_text(spec)!r}',
                   rc == 0 and tr_text(spec) == 'see .sdlc/tickets/.0001-alpha/handoff.md\n'
                   and (tr / 'tickets' / '.0001-alpha').is_dir())

        tr = tr_root('tr-num')
        run(tr, 'new', ('feature', 'alpha', 'Alpha'))
        run(tr, 'close', ('alpha',), reason='done elsewhere')
        rc, out, err = run(tr, 'number')
        expect(f'ticket_root: number renames tickets/alpha to tickets/0001-alpha, config stays at <root>: rc={rc} '
               f'{out!r} {err!r}',
               rc == 0 and (tr / 'tickets' / '0001-alpha').is_dir() and not (tr / 'tickets' / 'alpha').exists()
               and not (tr / '0001-alpha').exists() and config_numbered(tr)
               and not (tr / 'tickets' / 'config').exists())
        rc, out, err = run(tr, 'archive')
        expect(f'ticket_root: archive renames to tickets/.0001-alpha: rc={rc} {out!r} {err!r}',
               rc == 0 and (tr / 'tickets' / '.0001-alpha').is_dir() and not (tr / '.0001-alpha').exists()
               and '(tickets/.0001-alpha/handoff.md)' in tr_text(tr / 'roadmap.md') and run(tr, 'check')[0] == 0)

        bad = pathlib.Path(tmp) / 'tr-bad' / '.sdlc'
        bad.mkdir(parents=True)
        (bad / 'config').write_text('ticket_root: work\n', encoding='utf-8')
        rc, _, err = run(bad, 'new', ('feature', 'alpha'))
        expect(f'ticket_root: an unsupported value refuses new, writing nothing: rc={rc} {err!r} '
               f'tree={tree(bad)}', rc == 1 and 'ticket_root: tickets' in err and tree(bad) == ['config'])
        rc, _, err = run(bad, 'check')
        expect(f'ticket_root: an unsupported value fails check: rc={rc} {err!r}',
               rc == 1 and 'ticket_root: work' in err)

        st = pathlib.Path(tmp) / 'tr-stray' / '.sdlc'
        run(st, 'new', ('feature', 'alpha', 'Alpha'))
        (st / 'config').write_text('ticket_root: tickets\n', encoding='utf-8')
        rc, _, err = run(st, 'check')
        expect(f'ticket_root: a ticket folder left at <root> fails check as a stray: rc={rc} {err!r}',
               rc == 1 and 'alpha: ticket folder outside the ticket root' in err and 'tickets/alpha' in err)
        before = snap(st)
        rc, _, err = run(st, 'new', ('feature', 'beta'))
        expect(f'ticket_root: a stray refuses new, writing nothing: rc={rc} {err!r}',
               rc == 1 and 'outside the ticket root' in err and snap(st) == before
               and not (st / 'tickets').exists())

        # negative control: no ticket_root line (no config, or other lines only) keeps <root>/<slug>
        for label, cfg in (('no config', None), ('other lines', '# ticket_root: tickets\nticket_folders: plain\n')):
            nc = pathlib.Path(tmp) / f'tr-none-{label.replace(" ", "-")}' / '.sdlc'
            if cfg is not None:
                nc.mkdir(parents=True)
                (nc / 'config').write_text(cfg, encoding='utf-8')
            rc, out, err = run(nc, 'new', ('feature', 'alpha', 'Alpha'))
            expect(f'ticket_root absent ({label}): new lands in <root>/alpha with link alpha/handoff.md: rc={rc} '
                   f'{out!r} {err!r}',
                   rc == 0 and ticket_dir(nc) == nc and (nc / 'alpha' / 'handoff.md').is_file()
                   and not (nc / 'tickets').exists() and '| [alpha](alpha/handoff.md) |' in tr_text(nc / 'roadmap.md')
                   and run(nc, 'check')[0] == 0)

        # ---- router: <root>/AGENTS.md holds a managed block with stage counts, open tickets and procedures ----
        def block_of(path):
            f = onboard.find_block(tr_text(path))
            return f.block.text if f.status == 'block' else ''

        def stage_text(root):
            b = block_of(root / 'AGENTS.md')
            return b[b.index('## Stages\n\n') + len('## Stages\n\n'):b.index('\n\n## Procedures')] if b else ''

        def router_line(path):
            return next((ln for ln in tr_text(path).splitlines() if ln.startswith('router: ')), '')

        def check_err(root):
            rc, out, err = run(root, 'check')
            return rc, err

        # regeneration: new, a status edit plus roadmap, and close each rewrite the counts and lines
        rl = pathlib.Path(tmp) / 'rt-life' / '.sdlc'
        rc, _, err = run(rl, 'new', ('feature', 'alpha', 'Alpha'))
        st = stage_text(rl)
        expect(f'router: new writes proposed 1 and the ticket line: rc={rc} {err!r} {st!r}',
               rc == 0 and st == '- proposed: 1\n  - T-0001 Alpha (alpha)\n- ready: 0\n- claimed: 0\n- paused: 0\n'
                                 '- blocked: 0\n- done: 0\n- dropped: 0' and tr_text(rl / 'CLAUDE.md') == '@AGENTS.md\n'
               and run(rl, 'check')[0] == 0)
        edit(rl, 'alpha', r'^status:.*$', 'status: ready')
        rc_c, _ = check_err(rl)
        run(rl, 'roadmap')
        st = stage_text(rl)
        expect(f'router: a status edit plus roadmap moves the line to ready: rc_check={rc_c} {st!r}',
               rc_c == 1 and st == '- proposed: 0\n- ready: 1\n  - T-0001 Alpha (alpha)\n- claimed: 0\n- paused: 0\n'
                                    '- blocked: 0\n- done: 0\n- dropped: 0' and run(rl, 'check')[0] == 0)
        filer('filer-L1.md', 'None', '- decide: Add retry to fetch')(rl)
        rc, out, err = close_one(rl, 1)
        st = stage_text(rl)
        expect(f'router: close raises done, drops the line, and the follow-up adds a proposed line: rc={rc} {out!r} '
               f'{err!r} {st!r}',
               rc == 0 and st == '- proposed: 1\n  - T-0002 Add retry to fetch (add-retry-to-fetch)\n- ready: 0\n'
                                 '- claimed: 0\n- paused: 0\n- blocked: 0\n- done: 1\n- dropped: 0'
               and run(rl, 'check')[0] == 0)
        expect(f'router: new and follow-up tickets carry the router line: '
               f'{router_line(rl / "alpha" / "handoff.md")!r} {router_line(rl / "add-retry-to-fetch" / "handoff.md")!r}',
               router_line(rl / 'alpha' / 'handoff.md') == router_line(rl / 'add-retry-to-fetch' / 'handoff.md')
               == 'router: .sdlc/AGENTS.md  # how to claim and close this ticket'
               and dict(load(rl)).get('alpha', {}).get('router') == '.sdlc/AGENTS.md')
        b = block_of(rl / 'AGENTS.md')
        expect(f'router: procedures name .sdlc paths and no absolute path: {b!r}',
               '--root .sdlc new <feature|bug|chore|spike|idea>' in b
               and '<plugin-root>/scripts/run.sh filer L1 .sdlc/<folder>/handoff.md' in b
               and '${CLAUDE_PLUGIN_ROOT}' in b and str(tmp) not in b and ROUTER_HERE in b)

        # contents with tickets in every status, closed dot folders included
        r5 = pathlib.Path(tmp) / 'rt-five' / '.sdlc'
        for sl in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'):
            run(r5, 'new', ('feature', sl, sl.upper()), numbered=True)
        for sl, s in (('0002-b', 'ready'), ('0003-c', 'blocked'), ('0004-d', 'done'), ('0005-e', 'dropped'),
                      ('0007-g', 'claimed\nclaimed_by: codex 2026-10-11'),
                      ('0008-h', 'paused\npaused_reason: waiting on vendor')):
            edit(r5, sl, r'^status:.*$', f'status: {s}')
        run(r5, 'roadmap')
        rc_a, out_a, err_a = run(r5, 'archive')
        rc_f, out_f, err_f = run(r5, 'close', ('0006-f',), reason='done elsewhere')
        st = stage_text(r5)
        expect(f'router: every status, dot folders counted under their status, done and dropped count only: '
               f'rc={rc_a},{rc_f} {err_a!r} {err_f!r} tree={tree(r5)} {st!r}',
               rc_a == rc_f == 0 and (r5 / '.0004-d').is_dir() and (r5 / '.0006-f').is_dir()
               and st == '- proposed: 1\n  - T-0001 A (0001-a)\n- ready: 1\n  - T-0002 B (0002-b)\n- claimed: 1\n'
                         '  - T-0007 G (0007-g), claimed by codex 2026-10-11\n- paused: 1\n'
                         '  - T-0008 H (0008-h), paused: waiting on vendor\n- blocked: 1\n'
                         '  - T-0003 C (0003-c)\n- done: 2\n- dropped: 1' and run(r5, 'check')[0] == 0)
        # claimed_by shows on an active line; while only the router is stale, check names AGENTS.md, not roadmap.md
        edit(r5, '0002-b', r'^created:(.*)$', r'created:\1\nclaimed_by: claude 2026-09-30')
        rc, err = check_err(r5)
        expect(f'router: claimed_by added, roadmap current: check names AGENTS.md stale, not roadmap.md: rc={rc} '
               f'{err!r}',
               rc == 1 and 'AGENTS.md: router block stale' in err and 'roadmap.md' not in err)
        run(r5, 'roadmap')
        expect(f'router: claimed_by shows on the active line: {stage_text(r5)!r}',
               '  - T-0002 B (0002-b), claimed by claude 2026-09-30\n' in stage_text(r5) and run(r5, 'check')[0] == 0)

        # area, claimed and paused: validation runs one way; the Area column shows only when an area exists
        ra = pathlib.Path(tmp) / 'rt-area' / '.sdlc'
        run(ra, 'new', ('feature', 'alpha', 'Alpha'))
        rm = tr_text(ra / 'roadmap.md')
        expect(f'area: no area anywhere keeps the header without an Area column: {rm!r}',
               '| ID | Ticket | Title | Type | Size | Pri | Depends on | Status |\n' in rm and '| Area |' not in rm)
        edit(ra, 'alpha', r'^status:.*$', 'status: ready\nclaimed_by: claude 2026-10-11')
        run(ra, 'roadmap')
        rc, err = check_err(ra)
        expect(f'claimed_by on a ready ticket stays valid: rc={rc} {err!r}', rc == 0)
        edit(ra, 'alpha', r'^created:(.*)$', r'created:\1\narea: ui-kit')
        rc, err = check_err(ra)
        expect(f'area: an area with no areas: line fails naming the config line to add: rc={rc} {err!r}',
               rc == 1 and 'alpha' in err and "'ui-kit'" in err and '`areas: <name>, ...`' in err)
        with (ra / 'config').open('a', encoding='utf-8') as f:
            f.write('# ticket areas\nareas: ui-kit, back-end  # domains\n')
        edit(ra, 'alpha', r'^area:.*$', 'area: nope')
        rc, err = check_err(ra)
        expect(f'area: an unknown area fails naming the value and the list: rc={rc} {err!r}',
               rc == 1 and 'alpha' in err and "'nope'" in err and 'ui-kit, back-end' in err)
        edit(ra, 'alpha', r'^area:.*$', 'area: ui-kit')
        rc, _, err = run(ra, 'new', ('feature', 'beta', 'Beta'))
        rm = tr_text(ra / 'roadmap.md')
        expect(f'area: a listed area passes and an Area column appears, empty for a ticket without one: '
               f'rc={rc} {err!r} {rm!r}',
               rc == 0 and run(ra, 'check')[0] == 0
               and '| ID | Ticket | Title | Type | Area | Size | Pri | Depends on | Status |\n' in rm
               and '|---|---|---|---|---|---|---|---|---|\n' in rm
               and '| feature | ui-kit | ' in rm and '| feature |  | ' in rm)
        edit(ra, 'beta', r'^status:.*$', 'status: claimed')
        rc, err = check_err(ra)
        expect(f'claimed without claimed_by fails naming claimed_by: rc={rc} {err!r}',
               rc == 1 and 'beta' in err and 'claimed_by' in err)
        edit(ra, 'beta', r'^status:.*$', 'status: paused')
        rc, err = check_err(ra)
        expect(f'paused without paused_reason fails naming paused_reason: rc={rc} {err!r}',
               rc == 1 and 'beta' in err and 'paused_reason' in err)
        edit(ra, 'beta', r'^status:.*$', 'status: paused\npaused_reason: waiting on vendor | api')
        edit(ra, 'alpha', r'^status:.*$', 'status: claimed')
        rc_r, _, err_r = run(ra, 'roadmap')
        rm, st = tr_text(ra / 'roadmap.md'), stage_text(ra)
        expect(f'paused reason shows in the roadmap and the router, claimed counts: rc={rc_r} {err_r!r} {rm!r} {st!r}',
               rc_r == 0 and run(ra, 'check')[0] == 0
               and '| ⏸️ paused (waiting on vendor \\| api) |\n' in rm and '| \U0001f7e1 claimed |\n' in rm
               and '- claimed: 1\n  - T-0001 Alpha (alpha), claimed by claude 2026-10-11\n' in st
               and '- paused: 1\n  - T-0002 Beta (beta), paused: waiting on vendor | api\n' in st)
        b = block_of(ra / 'AGENTS.md')
        expect(f'router: the Ticket fields line lists every status in order: {b!r}',
               '\nstatus: proposed | ready | claimed | paused | blocked | done | dropped\n' in b)

        # text outside the block and existing CLAUDE.md content are kept; one block and one import after reruns
        rk = pathlib.Path(tmp) / 'rt-keep' / '.sdlc'
        rk.mkdir(parents=True)
        (rk / 'AGENTS.md').write_text('# Mine\n\nKeep me.', encoding='utf-8')
        (rk / 'CLAUDE.md').write_text('Hello', encoding='utf-8')
        run(rk, 'new', ('feature', 'alpha', 'Alpha'))
        with (rk / 'AGENTS.md').open('a', encoding='utf-8') as f:
            f.write('\n## After\n\nKeep me too.\n')
        run(rk, 'new', ('feature', 'beta', 'Beta'))
        run(rk, 'roadmap')
        run(rk, 'roadmap')
        a, c = tr_text(rk / 'AGENTS.md'), tr_text(rk / 'CLAUDE.md')
        expect(f'router: outside text and CLAUDE.md content kept, one block, one import: {a!r} {c!r}',
               a.startswith('# Mine\n\nKeep me.\n<!-- sdlc-lite:managed:start v1 sha256:')
               and a.endswith('<!-- sdlc-lite:managed:end -->\n\n## After\n\nKeep me too.\n')
               and a.count('sdlc-lite:managed:start') == 1 and c == 'Hello\n@AGENTS.md\n'
               and '  - T-0002 Beta (beta)\n' in a and run(rk, 'check')[0] == 0)

        # ticket_root: tickets: tickets/AGENTS.md and tickets/CLAUDE.md, identical procedures, .sdlc/tickets paths
        rt = tr_root('rt-tickets')
        run(rt, 'new', ('feature', 'alpha', 'Alpha'))
        tr_filer(rt, 'alpha', '- decide: Add retry to fetch')
        rc, out, _ = run(rt, 'close', ('alpha',), dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else 'none'
        rc, out, err = run(rt, 'close', ('alpha',), ticket=1, expect=token)
        top, nested = block_of(rt / 'AGENTS.md'), block_of(rt / 'tickets' / 'AGENTS.md')
        expect(f'router: ticket_root writes tickets/AGENTS.md and tickets/CLAUDE.md with the same procedures: '
               f'rc={rc} {err!r} {nested!r}',
               rc == 0 and nested.startswith('# Tickets\n') and tr_text(rt / 'tickets' / 'CLAUDE.md') == '@AGENTS.md\n'
               and ROUTER_TICKETS in top and nested[nested.index('## Procedures'):] == top[top.index('## Procedures'):]
               and '<plugin-root>/scripts/run.sh planner <level> .sdlc/tickets/<folder>/handoff.md' in nested
               and '--root .sdlc close <folder>' in nested
               and '  - T-0002 Add retry to fetch (add-retry-to-fetch)\n' in top and run(rt, 'check')[0] == 0)
        want = 'router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket'
        expect(f'router: ticket_root new and follow-up carry the tickets/ router line',
               router_line(rt / 'tickets' / 'alpha' / 'handoff.md') == want
               and router_line(rt / 'tickets' / 'add-retry-to-fetch' / 'handoff.md') == want)

        # negative controls, one per check cause, each next to its passing clean case
        def router_case(name, tickets_root=False):
            r = tr_root(name) if tickets_root else pathlib.Path(tmp) / name / '.sdlc'
            run(r, 'new', ('feature', 'alpha', 'Alpha'))
            return r

        for label, tickets_root, mutate, want in (
                ('missing block', False, lambda r: (r / 'AGENTS.md').unlink(), 'AGENTS.md: router block missing'),
                ('block removed', False, lambda r: (r / 'AGENTS.md').write_text('# Mine\n', encoding='utf-8'),
                 'AGENTS.md: router block missing'),
                ('stale count', False, lambda r: (r / 'AGENTS.md').write_text(
                    tr_text(r / 'AGENTS.md').replace('- proposed: 1\n', '- proposed: 2\n'), encoding='utf-8'),
                 'AGENTS.md: router block stale'),
                ('missing import', False, lambda r: (r / 'CLAUDE.md').write_text('Other\n', encoding='utf-8'),
                 'CLAUDE.md: no @AGENTS.md import'),
                ('missing tickets/AGENTS.md', True, lambda r: (r / 'tickets' / 'AGENTS.md').unlink(),
                 'tickets/AGENTS.md: router block missing'),
                ('missing tickets/CLAUDE.md import', True,
                 lambda r: (r / 'tickets' / 'CLAUDE.md').write_text('Other\n', encoding='utf-8'),
                 'tickets/CLAUDE.md: no @AGENTS.md import')):
            r = router_case('rt-neg-' + re.sub(r'\W+', '-', label), tickets_root)
            rc0, err0 = check_err(r)
            mutate(r)
            rc, err = check_err(r)
            expect(f'router: {label}: clean passes, then check fails with {want!r}: rc={rc0},{rc} {err0!r} {err!r}',
                   rc0 == 0 and rc == 1 and want in err and 'roadmap.md' not in err)
            run(r, 'roadmap')
            expect(f'router: {label}: roadmap repairs it', run(r, 'check')[0] == 0)

        # malformed block: new, close (dry run included) and roadmap refuse, writing nothing; check fails
        r = router_case('rt-malformed')
        filer('filer-L1.md', 'None', 'None')(r)
        (r / 'AGENTS.md').write_text('<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->\nno end\n',
                                     encoding='utf-8')
        before = snap(r)
        for cmd, args, kw in (('new', ('feature', 'beta'), {}), ('close', ('alpha',), {}),
                              ('close', ('alpha',), {'dry_run': True}), ('close', ('alpha',), {'reason': 'x'}),
                              ('roadmap', (), {}), ('number', (), {}), ('archive', (), {'numbered': True})):
            rc, _, err = run(r, cmd, args, **kw)
            expect(f'router: malformed block refuses {cmd} {kw}, writing nothing: rc={rc} {err!r}',
                   rc == 1 and 'AGENTS.md: router block malformed:' in err and err.endswith('nothing written')
                   and snap(r) == before)
        rc, err = check_err(r)
        expect(f'router: malformed block fails check: rc={rc} {err!r}',
               rc == 1 and 'AGENTS.md: router block malformed:' in err and 'fix its markers by hand' in err)

        # mailbox entry files: roadmap writes them under <root>/messages, restores edits, never under tickets/
        mbox_files = ['.gitignore', 'AGENTS.md', 'CLAUDE.md'] + [f'{s}/{n}' for s in ('new', 'read', 'done')
                                                                  for n in ('AGENTS.md', 'CLAUDE.md')]
        rm = pathlib.Path(tmp) / 'rt-mbox' / '.sdlc'
        rc, _, err = run(rm, 'roadmap')
        expect(f'router: roadmap writes the mailbox entry files: rc={rc} {err!r}',
               rc == 0 and all((rm / 'messages' / f).is_file() for f in mbox_files)
               and tr_text(rm / 'messages' / 'new' / 'CLAUDE.md') == '@AGENTS.md\n')
        want_new = tr_text(rm / 'messages' / 'new' / 'AGENTS.md')
        (rm / 'messages' / 'new' / 'AGENTS.md').write_text('edited\n', encoding='utf-8')
        (rm / 'messages' / 'read' / 'CLAUDE.md').unlink()
        rc, _, err = run(rm, 'roadmap')
        expect(f'router: roadmap restores an edited mailbox entry file: rc={rc} {err!r}',
               rc == 0 and tr_text(rm / 'messages' / 'new' / 'AGENTS.md') == want_new != 'edited\n'
               and tr_text(rm / 'messages' / 'read' / 'CLAUDE.md') == '@AGENTS.md\n')
        expect('router: ticket_root keeps the mailbox at <root>/messages',
               (rt / 'messages' / 'AGENTS.md').is_file() and not (rt / 'tickets' / 'messages').exists())
        rf = pathlib.Path(tmp) / 'rt-mbox-refused' / '.sdlc'
        rf.mkdir(parents=True)
        (rf / 'AGENTS.md').write_text('<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->\nno end\n',
                                      encoding='utf-8')
        rc, _, err = run(rf, 'roadmap')
        expect(f'router: a refused roadmap writes no mailbox entry files: rc={rc} {err!r}',
               rc == 1 and 'router block malformed' in err and not (rf / 'messages').exists())
        rc0 = run(rm, 'check')[0]
        shutil.rmtree(rm / 'messages')
        rc, err = check_err(rm)
        expect(f'router: check passes without the mailbox entry files: rc={rc0},{rc} {err!r}', rc0 == 0 and rc == 0)
        expect('router: the router links messages/AGENTS.md',
               any(ln.startswith('- Mailbox:') and 'messages/AGENTS.md' in ln
                   for ln in block_of(rm / 'AGENTS.md').splitlines()))

        # positive: zero tickets and no AGENTS.md passes check
        rz = pathlib.Path(tmp) / 'rt-zero' / '.sdlc'
        rz.mkdir(parents=True)
        rc, out, err = run(rz, 'check')
        expect(f'router: zero tickets and no AGENTS.md passes check: rc={rc} {out!r} {err!r}',
               rc == 0 and out.splitlines()[0] == 'ok: 0 tickets, roadmap current' and len(out.splitlines()) == 2
               and 'migrate-layout' in out)

        # ---- layout: topics: tickets/ (with roadmap.md), work/, notes/ (notes.md); strays at <root> fail check ----
        def tp_root(name, extra=''):
            return tr_root(name, 'layout: topics\n' + extra)

        tp = tp_root('tp-new')
        rc, out, err = run(tp, 'new', ('feature', 'alpha', 'Alpha'))
        rm = tr_text(tp / 'tickets' / 'roadmap.md')
        rc2, out2, err2 = run(tp, 'check')
        expect(f'layout topics: new writes tickets/roadmap.md linking alpha/handoff.md, the work/ and notes/ entry '
               f'files, and check passes: rc={rc},{rc2} {out!r} {err!r} {out2!r} {err2!r}',
               rc == 0 and rc2 == 0 and '| [alpha](alpha/handoff.md) |' in rm and not (tp / 'roadmap.md').exists()
               and all((tp / f).is_file() for f in ('work/AGENTS.md', 'work/CLAUDE.md', 'notes/AGENTS.md',
                                                    'notes/CLAUDE.md'))
               and 'tickets/roadmap.md' in block_of(tp / 'AGENTS.md')
               and f'go to `{router_paths(tp)[0]}/notes/notes.md`' in block_of(tp / 'AGENTS.md')
               and f'go to `{router_paths(tp)[0]}/notes/notes.md`' in block_of(tp / 'tickets' / 'AGENTS.md')
               and block_of(tp / 'work' / 'AGENTS.md') == WORK_TEMPLATE
               and block_of(tp / 'notes' / 'AGENTS.md') == NOTES_TEMPLATE
               and 'migrate-layout' not in out2 and 'stray' not in err2)
        (tp / '_templates').mkdir()
        (tp / '.DS_Store').write_text('', encoding='utf-8')
        (tp / 'board.md').write_text('', encoding='utf-8')
        rc, out, err = run(tp, 'check')
        expect(f'layout topics: _templates, .DS_Store and board.md at <root> are allowed: rc={rc} {err!r}', rc == 0)

        tp = tp_root('tp-close')
        run(tp, 'new', ('feature', 'alpha', 'Alpha'))
        tr_filer(tp, 'alpha', '- note: Keep this')
        rc, out, err = run(tp, 'close', ('alpha',))
        expect(f'layout topics: close appends the note: follow-up to notes/notes.md: rc={rc} {out!r} {err!r}',
               rc == 0 and 'note: Keep this' in tr_text(tp / 'notes' / 'notes.md') and not (tp / 'notes.md').exists()
               and run(tp, 'check')[0] == 0)

        for label, mutate, want in (
                ('stray dir', lambda r: (r / 'junk').mkdir(), 'junk: stray entry at the root'),
                ('root notes.md', lambda r: (r / 'notes.md').write_text('x\n', encoding='utf-8'),
                 'notes.md: stray entry at the root'),
                ('root .NNNN-x', lambda r: (r / '.0009-x').mkdir(), '.0009-x: stray entry at the root')):
            tp = tp_root(f'tp-stray-{label.replace(" ", "-")}')
            run(tp, 'new', ('feature', 'alpha', 'Alpha'))
            mutate(tp)
            rc, _, err = run(tp, 'check')
            rc_new = run(tp, 'new', ('feature', 'beta', 'Beta'))[0]
            expect(f'layout topics: a {label} at <root> fails check naming it, never new: rc={rc},{rc_new} {err!r}',
                   rc == 1 and want in err and 'layout: topics' in err and rc_new == 0)

        for label, cfg, want in (('topics without ticket_root', 'layout: topics\n', 'ticket_root: tickets'),
                                 ('unsupported value', 'ticket_root: tickets\nlayout: nested\n', 'layout: nested'),
                                 ('both values', 'ticket_root: tickets\nlayout: flat\nlayout: topics\n',
                                  'layout: topics conflicts with layout: flat')):
            lb = pathlib.Path(tmp) / f'tp-bad-{label.replace(" ", "-")}' / '.sdlc'
            lb.mkdir(parents=True)
            (lb / 'config').write_text(cfg, encoding='utf-8')
            rc, _, err = run(lb, 'check')
            rc_new, _, err_new = run(lb, 'new', ('feature', 'alpha'))
            expect(f'layout: {label} fails check and refuses new, writing nothing: rc={rc},{rc_new} {err!r} '
                   f'tree={tree(lb)}',
                   rc == 1 and want in err and rc_new == 1 and want in err_new and 'nothing written' in err_new
                   and tree(lb) == ['config'])

        tp = tp_root('tp-stale-work')
        run(tp, 'new', ('feature', 'alpha', 'Alpha'))
        (tp / 'work' / 'AGENTS.md').write_text(tr_text(tp / 'work' / 'AGENTS.md').replace('One folder', 'A folder'),
                                               encoding='utf-8')
        rc, _, err = run(tp, 'check')
        expect(f'layout topics: a stale work/AGENTS.md fails check: rc={rc} {err!r}',
               rc == 1 and 'work/AGENTS.md: router block stale' in err)

        fl = tr_root('tp-flat-optout', 'layout: flat\n')
        run(fl, 'new', ('feature', 'alpha', 'Alpha'))
        rc, out, err = run(fl, 'check')
        expect(f'layout: flat opts out of the migrate-layout warning and keeps the flat paths: rc={rc} {out!r} {err!r}',
               rc == 0 and out == 'ok: 1 tickets, roadmap current' and (fl / 'roadmap.md').is_file()
               and not (fl / 'work').exists() and not (fl / 'notes').exists())

        if shutil.which('git'):
            tp = tp_root('tp-git', 'ticket_folders: numbered\n')
            tenv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
            subprocess.run(['git', '-C', str(tp.parent), 'init', '-q'], env=tenv, capture_output=True)
            run(tp, 'new', ('feature', 'alpha', 'Alpha'))
            run(tp, 'new', ('feature', 'beta', 'Beta'))
            tr_filer(tp, '0001-alpha', 'None')
            linked = '](0001-alpha/handoff.md)' in tr_text(tp / 'tickets' / 'roadmap.md')
            rc, out, err = run(tp, 'close', ('0001-alpha',))
            expect(f'layout topics: the close reference scan skips tickets/roadmap.md: linked={linked} rc={rc} '
                   f'{out!r} {err!r}',
                   linked and rc == 0 and (tp / 'tickets' / '.0001-alpha').is_dir())
            edit(tp / 'tickets', '0002-beta', r'^status:.*$', 'status: done')
            run(tp, 'roadmap')
            linked = '](0002-beta/handoff.md)' in tr_text(tp / 'tickets' / 'roadmap.md')
            rc, out, err = run(tp, 'archive')
            expect(f'layout topics: the archive reference scan skips tickets/roadmap.md: linked={linked} rc={rc} '
                   f'{out!r} {err!r}',
                   linked and rc == 0 and (tp / 'tickets' / '.0002-beta').is_dir() and run(tp, 'check')[0] == 0)

        # ---- (skips): a solo, lean, fix, or full lane record needs the result or a ## Skipped entry per full-chain role ----
        PL = '- skip: planner; step: all; reason: no plan; decided: lane\n'
        FL = '- skip: filer; step: all; reason: closed by reason; decided: lane\n'

        def sk_root(name, lane_lines, skipped=None, files=(), status_done=True):
            r = pathlib.Path(tmp) / f'sk-{name}' / '.sdlc'
            run(r, 'new', ('feature', 'lean-a'))
            d = r / 'lean-a'
            for f in files:
                (d / f).parent.mkdir(parents=True, exist_ok=True)
                (d / f).write_text('', encoding='utf-8')
            if lane_lines is not None or skipped is not None:
                t = '# Skips\n'
                if lane_lines is not None:
                    t += '\n## Lane\n' + ''.join(f'- lane: {x}; point: p; reasons: r\n' for x in lane_lines)
                if skipped is not None:
                    t += '\n## Skipped\n' + skipped
                (d / 'skips.md').write_text(t, encoding='utf-8')
            if status_done:
                edit(r, 'lean-a', r'^status:\s*\S+', 'status: done')
            run(r, 'roadmap')
            return r

        built = ('step-1/builder-L1.md', 'step-1/verifier-L1.md')
        rc, _, err = run(sk_root('fix-miss', ['fix'], files=built), 'check')
        expect(f'(skips) check: fix ticket missing planner and filer fails: rc={rc} {err!r}',
               rc == 1 and 'lean-a: skips.md records lane fix but has no ## Skipped entry for planner, filer' in err)
        rc, _, err = run(sk_root('fix-ok', ['fix'], PL + FL, files=built), 'check')
        expect(f'(skips) check: entries for planner and filer pass: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(sk_root('none', None, files=built), 'check')
        expect(f'(skips) check: done ticket with no skips.md passes: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(sk_root('nolane', None, '', files=built), 'check')
        expect(f'(skips) check: only ## Skipped, no lane, passes: rc={rc} {err!r}', rc == 0)
        fullres = ('planner-L2.md', 'filer-L1.md', 'step-1/builder-L1.md', 'step-1/verifier-L1.md')
        rc, _, err = run(sk_root('tofull', ['lean', 'full'], files=fullres), 'check')
        expect(f'(skips) check: lane lean then full with every result passes: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(sk_root('tofull-miss', ['lean', 'full'], files=built), 'check')
        expect(f'(skips) check: lane full missing planner and filer fails: rc={rc} {err!r}',
               rc == 1 and 'lean-a: skips.md records lane full but has no ## Skipped entry for planner, filer' in err)
        rc, _, err = run(sk_root('solo-miss', ['solo']), 'check')
        expect(f'(skips) check: lane solo with no entries fails: rc={rc} {err!r}',
               rc == 1 and 'lean-a: skips.md records lane solo but has no ## Skipped entry for planner, filer' in err)
        rc, _, err = run(sk_root('solo-ok', ['solo'], PL + FL), 'check')
        expect(f'(skips) check: lane solo with planner and filer entries passes: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(sk_root('solo-open', ['solo'], status_done=False), 'check')
        expect(f'(skips) check: an open solo ticket without entries passes: rc={rc} {err!r}', rc == 0)
        sup = ('planner-L2.md', 'filer-L1.md', 'step-1/builder-L2.md', 'step-2.superseded-1/builder-L2.md')
        rc, _, err = run(sk_root('verif', ['lean'], files=sup), 'check')
        expect(f'(skips) check: step-1 without verifier fails, superseded step not named: rc={rc} {err!r}',
               rc == 1 and err.endswith('no ## Skipped entry for verifier step 1') and 'step 2' not in err)
        rc, _, err = run(sk_root('verif-all', ['lean'], '- skip: verifier; step: all; reason: x; decided: y\n',
                                 files=sup), 'check')
        expect(f'(skips) check: step: all covers a verifier: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(sk_root('empty-reason', ['fix'], '- skip: planner; step: all; reason: ; decided: y\n' + FL,
                                 files=built), 'check')
        expect(f'(skips) check: an empty reason does not count: rc={rc} {err!r}',
               rc == 1 and err.endswith('entry for planner'))
        r = sk_root('close-reason', ['fix'], files=built, status_done=False)
        rc, _, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(skips) close --reason without entries refuses, status unchanged: rc={rc} {err!r}',
               rc == 1 and 'no ## Skipped entry for planner, filer' in err and err.endswith('nothing written')
               and status(r, 'lean-a') == 'proposed')
        r = sk_root('close-filer', ['lean'], files=built, status_done=False)
        filer('filer-L1.md', 'None', 'None', slug='lean-a')(r)
        rc, _, err = run(r, 'close', ('lean-a',))
        expect(f'(skips) close (filer path) on lean ticket without planner refuses: rc={rc} {err!r}',
               rc == 1 and 'no ## Skipped entry for planner;' in err and status(r, 'lean-a') == 'proposed')
        r = sk_root('close-ok', ['fix'], PL + FL, files=built, status_done=False)
        rc, out, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(skips) close --reason with entries succeeds: rc={rc} {err!r}',
               rc == 0 and status(r, 'lean-a') == 'done' and run(r, 'check')[0] == 0)

        # ---- (docs-only) T-0429: a docs, records and reports only diff closes with no verifier result; anything else still needs one ----
        import subprocess as _sp

        def vs_root(name, change, handoff_tail='', base_files=(), recorded=True):
            r = sk_root(name, ['lean'], PL + FL, files=('step-1/builder-L1.md',), status_done=False)
            top = r.parent
            for rel, text in base_files:
                (top / rel).parent.mkdir(parents=True, exist_ok=True)
                (top / rel).write_text(text, encoding='utf-8')
            if handoff_tail:
                with open(r / 'lean-a' / 'handoff.md', 'a', encoding='utf-8') as fh:
                    fh.write(handoff_tail)
            git = lambda *a: _sp.run(['git', '-C', str(top), *a], capture_output=True, text=True, check=True)
            git('init', '-q')
            git('config', 'user.email', 't@t')
            git('config', 'user.name', 't')
            git('add', '-A')
            git('commit', '-qm', 'base')
            if recorded:
                (r / 'lean-a' / 'step-1' / 'base-sha').write_text(git('rev-parse', 'HEAD').stdout, encoding='utf-8')
            for rel, text in change:
                (top / rel).parent.mkdir(parents=True, exist_ok=True)
                (top / rel).write_text(text, encoding='utf-8')
            return r

        NOVER = 'no ## Skipped entry for verifier step 1'
        r = vs_root('vs-docs', [('docs/specs/x.md', '# x\n'), ('.sdlc/lean-a/notes.md', 'n\n')])
        rc, out, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(docs-only) close --reason on a docs and records diff needs no verifier: rc={rc} {err!r}',
               rc == 0 and status(r, 'lean-a') == 'done')
        sk = (r / 'lean-a' / 'skips.md').read_text(encoding='utf-8')
        expect('(docs-only) the waiver is recorded as a counting skip entry under ## Skipped',
               '- skip: verifier; step: all; reason: docs-only diff against ' in sk and sk.index('## Skipped') < sk.index('- skip: verifier'))
        expect(f'(docs-only) check passes after the waiver: {run(r, "check")[2]!r}', run(r, 'check')[0] == 0)
        r = vs_root('vs-script', [('docs/specs/x.md', '# x\n'), ('scripts/tool.py', 'x = 1\n')])
        rc, _, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(docs-only) a diff touching one script path still needs a verifier: rc={rc} {err!r}',
               rc == 1 and NOVER in err and status(r, 'lean-a') == 'proposed'
               and 'docs-only diff' not in (r / 'lean-a' / 'skips.md').read_text(encoding='utf-8'))
        for rel in ('plugins/p/skills/s/SKILL.md', 'plugins/p/agents/a.md'):
            r = vs_root('vs-md-' + rel.split('/')[2], [(rel, '# role\n')])
            rc, _, err = run(r, 'close', ('lean-a',), reason='x')
            expect(f'(docs-only) a Markdown file under {rel.split("/")[2]}/ still needs a verifier: rc={rc} {err!r}',
                   rc == 1 and NOVER in err and status(r, 'lean-a') == 'proposed')
        r = vs_root('vs-red', [('.sdlc/lean-a/notes.md', 'n\n')], base_files=[('docs/loose.md', '# loose\n')])
        rc, _, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(docs-only) a record-only diff that fails docs_check still needs a verifier: rc={rc} {err!r}',
               rc == 1 and NOVER in err and status(r, 'lean-a') == 'proposed')
        r = vs_root('vs-override', [('docs/specs/x.md', '# x\n')], handoff_tail='\nverifier: L2\n')
        rc, _, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(docs-only) a verifier: L2 line in the handoff keeps the verifier: rc={rc} {err!r}',
               rc == 1 and NOVER in err and status(r, 'lean-a') == 'proposed')
        r = vs_root('vs-nobase', [('docs/specs/x.md', '# x\n')], recorded=False)
        rc, _, err = run(r, 'close', ('lean-a',), reason='x')
        expect(f'(docs-only) no recorded base keeps the verifier: rc={rc} {err!r}', rc == 1 and NOVER in err)

        # ---- migrate-layout: flat to topics, with the cite rewrite ----
        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the migrate-layout cases')
        else:
            menv = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

            def mgit(cwd, *args):
                p = subprocess.run(['git', '-C', str(cwd), *args], env=menv, capture_output=True, text=True)
                if p.returncode:
                    raise AssertionError(f'selftest git fixture failed: git {" ".join(args)}: {p.stderr.strip()}')

            def mcommit(cwd, msg='x'):
                mgit(cwd, 'add', '-A')
                mgit(cwd, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                     'commit', '--no-verify', '-qm', msg)

            def mig_root(label, config=None, git=True):
                mr = pathlib.Path(tmp) / f'mig-{label}' / '.sdlc'
                mr.mkdir(parents=True)
                if config:
                    (mr / 'config').write_text(config, encoding='utf-8')
                if git:
                    mgit(mr.parent, 'init', '-q')
                return mr

            def wr(path, text):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')

            def mig_flat(label):
                mr = mig_root(label)
                top = mr.parent
                run(mr, 'new', ('chore', 'alpha', 'Alpha'))
                run(mr, 'new', ('chore', 'beta', 'Beta'))
                wr(mr / 'rel-x' / 'handoff.md', 'release record\n')
                wr(mr / 'notes.md', '# Notes\nsee ../README.md\n')
                wr(mr / 'alpha' / 'links.md', 'see ../rel-x/handoff.md and ../beta/handoff.md and ../../README.md\n')
                wr(mr / 'beta' / 'links.md', 'see ../alpha/handoff.md and ../../nowhere.md\n')
                wr(top / 'docs' / 'guide.md', 'see .sdlc/alpha/handoff.md and ../.sdlc/rel-x/handoff.md\n')
                wr(top / 'README.md', 'see .sdlc/roadmap.md and .sdlc/notes.md\n')
                wr(top / 'docs' / 'reports' / 'r.md', 'see .sdlc/alpha/handoff.md\n')
                wr(top / 'AGENTS.md', 'intro\n' + onboard.wrap_block('see .sdlc/roadmap.md and .sdlc/alpha/x\n'))
                mcommit(top)
                return mr

            mr = mig_flat('flat')
            top = mr.parent
            agents_before = (top / 'AGENTS.md').read_bytes()
            # negative controls first, each refusing with the tree unchanged
            with (top / 'README.md').open('a', encoding='utf-8') as fh:
                fh.write('x\n')
            rc, _, err = run(mr, 'migrate-layout', rewrite_refs=True)
            expect(f'(mig) a modified tracked file refuses: rc={rc} {err!r}',
                   rc == 1 and 'uncommitted changes' in err and err.endswith('nothing written')
                   and (mr / 'alpha').is_dir() and not (mr / 'tickets').exists())
            mgit(top, 'checkout', '-q', '--', 'README.md')
            wr(top / 'new.txt', 'x\n')
            rc, _, err = run(mr, 'migrate-layout', dry_run=True, rewrite_refs=True)
            expect(f'(mig) an untracked file refuses: rc={rc} {err!r}',
                   rc == 1 and 'uncommitted changes' in err and 'new.txt' in err)
            (top / 'new.txt').unlink()
            rc, _, err = run(mr, 'migrate-layout')
            el = err.splitlines()
            expect(f'(mig) cites without --rewrite-refs refuse, naming each file but not docs/reports: rc={rc} {err!r}',
                   rc == 1 and all(f'  {f}' in el for f in ('docs/guide.md', 'README.md', '.sdlc/alpha/links.md',
                                                            '.sdlc/notes.md'))
                   and not any(f'  {f}' in el for f in ('docs/reports/r.md', '.sdlc/beta/links.md', 'AGENTS.md',
                                                        '.sdlc/AGENTS.md'))
                   and '--rewrite-refs' in err and (mr / 'alpha').is_dir() and not (mr / 'tickets').exists())
            rc, out, err = run(mr, 'migrate-layout', dry_run=True, rewrite_refs=True)
            ol = out.splitlines()
            expect(f'(mig) dry run lists moves, rewrites, the docs/reports keep and config, writing nothing: '
                   f'rc={rc} {out!r} {err!r}',
                   rc == 0 and 'move alpha -> tickets/alpha' in ol and 'move rel-x -> work/rel-x' in ol
                   and 'move notes.md -> notes/notes.md' in ol and 'move roadmap.md -> tickets/roadmap.md' in ol
                   and 'keep docs/reports/r.md (dated record under docs/reports/)' in ol
                   and 'rewrite docs/reports/r.md' not in ol and 'config layout: topics' in ol
                   and not (mr / 'tickets').exists() and not (mr / 'config').exists())
            wr(mr / 'pause.md', 'x\n')
            mcommit(top)
            rc, _, err = run(mr, 'migrate-layout', rewrite_refs=True)
            expect(f'(mig) a loose root file refuses, named: rc={rc} {err!r}',
                   rc == 1 and 'pause.md' in err and (mr / 'alpha').is_dir())
            (mr / 'pause.md').unlink()
            wr(mr / 'work' / 'rel-x' / 'x.md', 'x\n')
            mcommit(top)
            rc, _, err = run(mr, 'migrate-layout', rewrite_refs=True)
            expect(f'(mig) an existing move target refuses: rc={rc} {err!r}',
                   rc == 1 and 'work/rel-x already exist' in err and (mr / 'rel-x').is_dir())
            shutil.rmtree(mr / 'work')
            mcommit(top)
            # positive: the full migration
            rc, out, err = run(mr, 'migrate-layout', rewrite_refs=True)
            rd = lambda p: (top / p).read_text(encoding='utf-8')
            expect(f'(mig) flat fixture migrates, rewrites cites, and check passes: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'ok: 2 tickets, roadmap current' in out.splitlines()
                   and all((mr / p).is_file() for p in ('tickets/alpha/handoff.md', 'tickets/beta/links.md',
                                                         'work/rel-x/handoff.md', 'notes/notes.md',
                                                         'tickets/roadmap.md'))
                   and not any((mr / p).exists() for p in ('alpha', 'beta', 'rel-x', 'notes.md', 'roadmap.md'))
                   and rd('docs/guide.md') == 'see .sdlc/tickets/alpha/handoff.md and ../.sdlc/work/rel-x/handoff.md\n'
                   and rd('README.md') == 'see .sdlc/tickets/roadmap.md and .sdlc/notes/notes.md\n'
                   and rd('.sdlc/tickets/alpha/links.md')
                   == 'see ../../work/rel-x/handoff.md and ../beta/handoff.md and ../../../README.md\n'
                   and rd('.sdlc/tickets/beta/links.md') == 'see ../alpha/handoff.md and ../../nowhere.md\n'
                   and rd('.sdlc/notes/notes.md') == '# Notes\nsee ../../README.md\n'
                   and rd('docs/reports/r.md') == 'see .sdlc/alpha/handoff.md\n'
                   and (top / 'AGENTS.md').read_bytes() == agents_before
                   and (mr / 'config').read_text(encoding='utf-8') == 'ticket_root: tickets\nlayout: topics\n'
                   and run(mr, 'check')[0] == 0)
            mcommit(top)
            rc, out, err = run(mr, 'migrate-layout')
            expect(f'(mig) a second run prints nothing to migrate: rc={rc} {out!r} {err!r}',
                   rc == 0 and out.splitlines()[0] == 'nothing to migrate' and 'ok: 2 tickets' in out)
            # ticket_root: tickets already set: ticket folders stay, only layout: topics is added
            tr = mig_root('tr', 'ticket_root: tickets\n')
            run(tr, 'new', ('chore', 'alpha', 'Alpha'))
            wr(tr / 'rel-x' / 'handoff.md', 'record\n')
            mcommit(tr.parent)
            rc, out, err = run(tr, 'migrate-layout')
            ol = out.splitlines()
            expect(f'(mig) ticket_root: tickets keeps its ticket folders and gains only layout: topics: '
                   f'rc={rc} {out!r} {err!r}',
                   rc == 0 and not any(x.startswith('move alpha') for x in ol) and 'move rel-x -> work/rel-x' in ol
                   and 'config layout: topics' in ol and 'config ticket_root: tickets' not in ol
                   and (tr / 'tickets' / 'alpha' / 'handoff.md').is_file()
                   and (tr / 'config').read_text(encoding='utf-8') == 'ticket_root: tickets\nlayout: topics\n')
            # a closed .NNNN-<slug> folder moves to tickets/
            cr = mig_root('closed')
            run(cr, 'new', ('chore', 'gamma', 'Gamma'))
            edit(cr, 'gamma', r'^status:.*$', 'status: done')
            (cr / 'gamma').rename(cr / '.0001-gamma')
            run(cr, 'roadmap')
            mcommit(cr.parent)
            rc, out, err = run(cr, 'migrate-layout')
            expect(f'(mig) a closed .NNNN-x folder moves to tickets/: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'move .0001-gamma -> tickets/.0001-gamma' in out.splitlines()
                   and (cr / 'tickets' / '.0001-gamma' / 'handoff.md').is_file() and run(cr, 'check')[0] == 0)
            # a skipped migration (topics config, folders still at the root) fails check, then is completed
            sr = mig_root('skipped')
            run(sr, 'new', ('chore', 'alpha', 'Alpha'))
            wr(sr / 'rel-x' / 'handoff.md', 'record\n')
            (sr / 'config').write_text('ticket_root: tickets\nlayout: topics\n', encoding='utf-8')
            mcommit(sr.parent)
            rc, _, err = run(sr, 'check')
            expect(f'(mig) topics config without the moves fails check, naming the stray root folder: rc={rc} {err!r}',
                   rc == 1 and 'rel-x: stray entry at the root' in err)
            rc, out, err = run(sr, 'migrate-layout')
            ol = out.splitlines()
            expect(f'(mig) a skipped migration is completed: rc={rc} {out!r} {err!r}',
                   rc == 0 and 'move alpha -> tickets/alpha' in ol and 'move rel-x -> work/rel-x' in ol
                   and not any(x.startswith('config ') for x in ol) and run(sr, 'check')[0] == 0)
            # a root outside git refuses
            nr = mig_root('nogit', git=False)
            run(nr, 'new', ('chore', 'alpha', 'Alpha'))
            rc, _, err = run(nr, 'migrate-layout', rewrite_refs=True)
            expect(f'(mig) a root outside git refuses: rc={rc} {err!r}',
                   rc == 1 and 'not inside a git work tree' in err and (nr / 'alpha').is_dir())

    # placeholder lint: a closed ticket that still holds template prompt text is a warning, never a failure
    with tempfile.TemporaryDirectory() as tmp:
        pr = pathlib.Path(tmp) / 'pl' / '.sdlc'

        def ph(root):
            rc, out, err = run(root, 'check')
            return rc, [x for x in out.splitlines() if 'template placeholder text' in x or 'more closed tickets' in x], err

        run(pr, 'new', ('bug', 'beta', 'Beta'))
        run(pr, 'new', ('bug', 'gamma', 'Gamma'))
        rc, got, err = ph(pr)
        expect(f'(ph) open tickets holding template text give no warning: rc={rc} {got} {err!r}', rc == 0 and got == [])
        run(pr, 'close', ('beta',), reason='done elsewhere')
        rc, got, err = ph(pr)
        expect(f'(ph) a closed unfilled bug ticket warns once, rc stays 0, open gamma stays quiet: rc={rc} {got} {err!r}',
               rc == 0 and len(got) == 1 and got[0].startswith('warning: beta/handoff.md:')
               and 'bug template placeholder text' in got[0] and 'gamma' not in got[0])
        expect(f'(ph) the warning names the line it found: {got}',
               bool(got) and (pr / 'beta' / 'handoff.md').read_text(encoding='utf-8').splitlines()[
                   int(got[0].split('handoff.md:')[1].split(':')[0]) - 1].startswith('1. Exact command'))
        for pat, repl in ((r'^1\. Exact command.*$', '1. run the failing test'), (r'^Paste the output.*$', 'rc=1'),
                          (r'^Where it was found.*$', 'tickets.py:10')):
            edit(pr, 'beta', pat, repl)
        rc, got, err = ph(pr)
        expect(f'(ph) a filled ticket that keeps the template default Goal and Constraints lines is clean: '
               f'rc={rc} {got} {err!r}',
               rc == 0 and got == [] and 'The failing test lands before or with the fix'
               in (pr / 'beta' / 'handoff.md').read_text(encoding='utf-8'))
        run(pr, 'close', ('gamma',), reason='dropped as a duplicate')
        edit(pr, 'gamma', r'^status: done', 'status: dropped')
        run(pr, 'roadmap')
        rc, got, err = ph(pr)
        expect(f'(ph) a dropped unfilled ticket warns too: rc={rc} {got} {err!r}',
               rc == 0 and len(got) == 1 and got[0].startswith('warning: gamma/handoff.md:'))
        # more than PLACEHOLDER_SHOWN: newest first, then one count line
        for i in range(PLACEHOLDER_SHOWN + 1):
            run(pr, 'new', ('chore', f'c{i}', 'C'))
            run(pr, 'close', (f'c{i}',), reason='x')
        rc, got, err = ph(pr)
        expect(f'(ph) {PLACEHOLDER_SHOWN} lines newest first then a count line: rc={rc} {got} {err!r}',
               rc == 0 and len(got) == PLACEHOLDER_SHOWN + 1
               and [x.split('/')[0] for x in got[:-1]] == [f'warning: c{i}' for i in range(PLACEHOLDER_SHOWN, 0, -1)]
               and got[-1].startswith('warning: 2 more closed tickets hold template placeholder text'))
        # a repo template under _templates overrides the shipped one, as `new` reads it
        ov = pathlib.Path(tmp) / 'ov' / '.sdlc'
        (ov / '_templates').mkdir(parents=True)
        (ov / '_templates' / 'chore.md').write_text(
            (PLUGIN / 'skills' / 'ticket' / 'templates' / 'chore.md').read_text(encoding='utf-8').replace(
                'One or two sentences: the outcome, not the method.', 'Say what and why in one line.'),
            encoding='utf-8')
        run(ov, 'new', ('chore', 'delta', 'Delta'))
        run(ov, 'close', ('delta',), reason='x')
        rc, got, err = ph(ov)
        expect(f'(ph) the repo template text is the placeholder: rc={rc} {got} {err!r}',
               rc == 0 and len(got) == 1 and "'Say what and why in one line.'" in got[0])
        # every default the lint exempts is still a line of a shipped template, so the list cannot go stale
        shipped = {prompt_text(l) for k in template_types(pr) if (PLUGIN / 'skills' / 'ticket' / 'templates' / f'{k}.md').is_file()
                   for _, l in body_lines((PLUGIN / 'skills' / 'ticket' / 'templates' / f'{k}.md').read_text(encoding='utf-8'))}
        expect(f'(ph) every PLACEHOLDER_KEEP line is in a shipped template: {sorted(PLACEHOLDER_KEEP - shipped)}',
               PLACEHOLDER_KEEP <= shipped)

    # (size) a ticket's size is its level L1 to L5; the 0.21.x SIZE_ALIASES are read aliases, stored as levels on write
    with tempfile.TemporaryDirectory() as tmp:
        sz = pathlib.Path(tmp) / '.sdlc'
        sz.mkdir()
        (sz / 'config').write_text('layout: flat\n', encoding='utf-8')
        rc, _, err = run(sz, 'new', ('chore', 'alpha', 'Alpha'))
        h = sz / 'alpha' / 'handoff.md'
        expect(f'(size) new stamps a level from the shipped template: {err}',
               rc == 0 and dict(load(sz))['alpha']['size'] in ENUMS['size'] and re.search(r'(?m)^size: L\d', h.read_text()))
        for alias, level in SIZE_ALIASES.items():
            expect(f'(size) alias {alias} reads as {level}', parse(f'---\nsize: {alias}\n---\n')['size'] == level)
        for level in ENUMS['size']:
            expect(f'(size) level {level} reads as itself', parse(f'---\nsize: {level}\n---\n')['size'] == level)
        h.write_text(re.sub(r'(?m)^size:.*$', 'size: M              # S | M | L | XL', h.read_text()), encoding='utf-8')  # ALIAS_OK
        rc, out, err = run(sz, 'check')
        expect(f'(size) an alias size passes check and reads as its level: rc={rc} {err}', rc == 0)
        before = h.read_bytes()
        rc, out, _ = run(sz, 'migrate-size')
        expect(f'(size) migrate-size is a dry run by default: {out!r}',
               rc == 0 and 'alpha/handoff.md: size M -> L2' in out and 'dry run' in out and h.read_bytes() == before)  # ALIAS_OK
        rc, out, _ = run(sz, 'migrate-size', apply=True)
        txt = h.read_text()
        expect(f'(size) migrate-size --apply writes the level and the level comment: {txt!r}',
               rc == 0 and re.search(r'(?m)^size: L2 +# L1 \| L2 \| L3 \| L4 \(L5 reserved\)$', txt)
               and txt.replace('L2             # L1 | L2 | L3 | L4 (L5 reserved)', 'M              # S | M | L | XL') == before.decode())  # ALIAS_OK
        expect('(size) migrate-size a second time has nothing to do', 'nothing to do' in run(sz, 'migrate-size')[1])
        expect('(size) check passes after migrate-size', run(sz, 'check')[0] == 0)
        h.write_text(re.sub(r'(?m)^size:.*$', 'size: XL', h.read_text()), encoding='utf-8')
        run(sz, 'roadmap')
        rc, out, _ = run(sz, 'close', ('alpha',), reason='done elsewhere')
        expect(f'(size) close stores the alias XL as L4 on write: {rc} {out}',
               rc == 0 and re.search(r'(?m)^size: L4$', h.read_text()) and re.search(r'(?m)^status: done', h.read_text()))
        h.write_text(re.sub(r'(?m)^size:.*$', 'size: XXL', h.read_text()), encoding='utf-8')
        rc, _, err = run(sz, 'check')
        expect(f'(size) negative control: an unknown size still fails check: {err}', rc == 1 and "size='XXL'" in err)

    if misses:
        print('tickets selftest: FAIL, these did not bite:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('tickets selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='tickets.py', description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.sdlc',
                    help='dir holding roadmap.md, config, notes.md, _templates and the ticket dirs (default: .sdlc '
                         'in the cwd); `ticket_root: tickets` in <root>/config moves the ticket dirs to <root>/tickets')
    sub = ap.add_subparsers(dest='cmd')
    p = sub.add_parser('new', help='stamp a typed ticket with the next id')
    p.add_argument('type')
    p.add_argument('slug')
    p.add_argument('title', nargs='?', default='')
    p.add_argument('--numbered', action='store_true',
                   help='name the folder NNNN-<slug> after the new id and persist '
                        '`ticket_folders: numbered` in <root>/config (also on via that config)')
    p = sub.add_parser('close', help='after /file: set the ticket done, file at most one decide: follow-up as a '
                                     'ticket (--ticket N) and append the rest to <root>/notes.md (skipping '
                                     'duplicates of existing tickets); --dry-run lists them first; '
                                     'or --reason TEXT: set it done without a filer file; '
                                     '--ack-warnings TEXT: close while filer warnings are open, with a reason')
    p.add_argument('slug')
    p.add_argument('--force', action='store_true', help='close even while the filer warnings are open')
    p.add_argument('--reason', metavar='TEXT',
                   help='close without a filer file (work done elsewhere): set done, append a ## Closed '
                        'section with the date and TEXT, file no follow-ups (refuses with --dry-run, --skip, --expect '
                        'or --ticket)')
    p.add_argument('--ack-warnings', metavar='TEXT',
                   help='close while the filer warnings are open: record TEXT and the quoted warnings in a '
                        '## Closed section, file follow-ups as normal (refuses with --force, with --reason, '
                        'with empty TEXT, or when no warnings are open)')
    p.add_argument('--dry-run', action='store_true',
                   help='apply the same refusals, then list each follow-up as <i>. <tag>: <title> with a mark: '
                        '[<slug>] ticket (the --ticket item), note (bound for notes.md), skip (--skip), or '
                        'duplicate of T-NNNN (<slug>), then one `open T-NNNN <title> [<slug>]` line per other proposed, '
                        'ready or blocked ticket, then one `open T-NNNN <title> [<slug>] (worktree <name>)` line per '
                        'open ticket found only in another git worktree\'s same-relative root (a ticket whose id '
                        'exists locally is decided by the local copy), then a last line `expect <digest>`; write nothing')
    p.add_argument('--skip', metavar='N[,N...]',
                   help='file every follow-up except these 1-based indices from the --dry-run listing; '
                        'an index out of range refuses and writes nothing; needs --expect')
    p.add_argument('--ticket', metavar='N', type=int,
                   help='file only this 1-based follow-up as a proposed idea ticket; it must be a decide: (or '
                        'untagged) item, in range, not in --skip and not a duplicate; needs --expect. Without it, '
                        'close files no ticket. Every other item that is not skipped or a duplicate goes to '
                        '<root>/notes.md')
    p.add_argument('--expect', metavar='DIGEST',
                   help='the digest from the --dry-run last line (expect <digest>); required with --skip and --ticket; '
                        'close refuses, writing nothing, when the Follow-ups list changed since that dry run')
    p.add_argument('--rewrite-refs', action='store_true',
                   help='numbered mode: when files outside the ticket folder reference <rel>/<slug>, rewrite them to '
                        '<rel>/.<slug> with the rename (--dry-run lists each as `rewrite <file>`) instead of '
                        'refusing; --force closes and leaves them')
    p.add_argument('--keep-refs', action='store_true',
                   help='numbered mode: close and leave the citing files as they are, without --force overriding '
                        'warnings; the ## Closed section lists the stale citations (--dry-run lists `keep <file>`)')
    p.add_argument('--numbered', action='store_true',
                   help='name each follow-up folder NNNN-<slug> after its own new id and, on success, persist '
                        '`ticket_folders: numbered` in <root>/config (also on via that config)')
    p = sub.add_parser('roadmap', help='regenerate roadmap.md')
    p.add_argument('--numbered', action='store_true',
                   help='also refuse on a NNNN-<slug> folder whose id is not T-NNNN (also on via <root>/config)')
    p = sub.add_parser('check', help='validate tickets and roadmap freshness')
    p.add_argument('--numbered', action='store_true',
                   help='also fail a NNNN-<slug> folder whose id is not T-NNNN (also on via <root>/config)')
    p = sub.add_parser('archive', help='numbered mode: rename done and dropped NNNN-<slug> folders to .NNNN-<slug>')
    p.add_argument('--dry-run', action='store_true',
                   help='print each <name> -> .<name> rename (and each rewrite <file> with --rewrite-refs); '
                        'write nothing')
    p.add_argument('--rewrite-refs', action='store_true',
                   help='rewrite files that reference an archived NNNN-<slug> folder to the .NNNN-<slug> form')
    p.add_argument('--force', action='store_true',
                   help='archive even when files reference a folder, leaving those references')
    p.add_argument('--numbered', action='store_true',
                   help='turn numbered mode on and, on success, persist it in <root>/config '
                        '(also on via that config)')
    p = sub.add_parser('number', help='convert plain <slug> ticket folders to NNNN-<slug>, rewrite their cites, '
                                      'and turn numbered mode on')
    p.add_argument('--dry-run', action='store_true',
                   help='print each <slug> -> NNNN-<slug> rename and each rewrite <file>; write nothing')
    p = sub.add_parser('migrate-layout', help='move a flat root to the topics layout (tickets/, work/, notes/), '
                                              'rewrite cites with --rewrite-refs, set layout: topics, run check')
    p.add_argument('--dry-run', action='store_true',
                   help='print each move, rewrite, keep and config line; write nothing')
    p.add_argument('--rewrite-refs', action='store_true',
                   help='rewrite files that cite a moved path to its new path instead of refusing')
    p = sub.add_parser('migrate-size', help='rewrite the 0.21.x alias sizes to levels (L1 to L4) in ticket and '
                                            'template front matter; a dry run unless --apply')
    p.add_argument('--apply', action='store_true', help='write the rewrites and regenerate the roadmap')
    sub.add_parser('selftest', help='prove every check failure fires')
    a = ap.parse_args(argv)
    cmd = a.cmd or 'check'
    if cmd == 'selftest':
        return selftest()
    args = {'new': lambda: (a.type, a.slug, a.title), 'close': lambda: (a.slug, a.force)}.get(cmd, tuple)()
    kw = {'numbered': getattr(a, 'numbered', False)} if cmd in ('new', 'close', 'roadmap', 'check', 'archive') else {}
    if cmd == 'number':
        kw['dry_run'] = a.dry_run
    if cmd == 'migrate-layout':
        kw['dry_run'] = a.dry_run
        kw['rewrite_refs'] = a.rewrite_refs
    if cmd == 'migrate-size':
        kw['apply'] = a.apply
    if cmd == 'archive':
        kw['dry_run'] = a.dry_run
        kw['rewrite_refs'] = a.rewrite_refs
        kw['force'] = a.force
    if cmd == 'close':
        kw['reason'] = a.reason
        kw['ack_warnings'] = a.ack_warnings
        kw['dry_run'] = a.dry_run
        kw['expect'] = a.expect
        kw['ticket'] = a.ticket
        kw['rewrite_refs'] = a.rewrite_refs
        kw['keep_refs'] = a.keep_refs
        try:
            kw['skip'] = None if a.skip is None else parse_skip(a.skip)
        except Fail as e:
            print(e, file=sys.stderr)
            return 1
    rc, out, err = run(pathlib.Path(a.root), cmd, args, **kw)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
