"""Plan-quality detectors: acceptance criteria that never went red, steps that break an earlier
step's contract, scope widened in prose instead of in the plan, and a ui-designer guidance gap
that recurs across tickets.

detect(rows, aux, thresholds) returns a list of findings (findings.make, family "plan", of the
kinds DETECTORS names) over the persisted rows (events.jsonl dicts) and aux.json. Paths in rows
are relative to aux["repo"]; the raw files opened are result files a row's sources names, the
task <task_dir>/handoff.md, and a step dir's handoff.md.

A path a note names: each code-span text in it, and each whitespace token holding `/` (with
surrounding quotes, brackets, and trailing punctuation stripped). A builder's note is the first
non-blank line under ## Notes; a verifier's is the first under ## For the next attempt.

Detectors (cause_hint files are plugin-relative):
  criteria-never-red   each aux["criteria_reruns"] record (rerun.run, only present when the
                       ingest ran with rerun_criteria) whose span exited 0 at the step's
                       base-sha: the criterion was green before the build, so it proves nothing
                       about the step. Evidence the step handoff path and criterion line. Cause
                       agents/planner.md. Without the key the detector is quiet.
  contract-dependents  a live verifier fail row in step m whose note names a path that the
                       ## Changes code spans of a live done builder in an earlier step n < m of
                       the same task list; evidence the verifier result (its note line) and the
                       builder result (the Changes line naming the path). One finding per
                       (verifier, builder) pair. Cause agents/planner.md.
  scope-prose          two or more blocked builder rows in one step dir whose notes name the same
                       path, when the task handoff has no `scope widened:` line under
                       ## Plan review and the step handoff has no ## Scope widened section;
                       evidence each such builder result at its note line. Cause
                       skills/chain/SKILL.md.
  guidance-gap         a ui-designer proposal `Rule: gap (proposed: "<text>")` (each bullet of
                       ## Guidance gaps, the quoted text when the bullet holds the form, else
                       the bullet; else each such item under ## Findings) seen in at least
                       guidance_gap_tickets distinct tickets (a row's ticket, else its task_dir),
                       grouped by the text lowercased, whitespace collapsed, and trailing
                       punctuation stripped. Layer project, no cause file, the proposal as the
                       rule; evidence the first result and line per ticket.
"""
import re

import steps  # same scripts/ dir: section and span helpers

from .. import findings
from .escalation import _Ctx, _build_status, _result, _row_dir, plan_review_entries

FAMILY = 'plan'
LAYER = 'sdlc'

SCOPE_WIDENED_RE = re.compile(r'^\s*(?:[-*+]\s+)?scope widened:', re.IGNORECASE)
STRIP = '`\'"()[]{}<>'
TRAIL = '.,;:!?'
GAP_RE = re.compile(r'Rule:\s*gap\s*\(proposed:\s*"([^"]*)"\)', re.IGNORECASE)


def _make(ctx, detector, cause, rule, evidence, summary):
    return findings.make(detector, FAMILY, ctx.sev(detector), LAYER, cause, rule, evidence,
                         summary)


def _clean(token):
    t = token.strip().strip(STRIP).rstrip(TRAIL).strip(STRIP)
    return t[2:] if t.startswith('./') else t


def note_paths(note):
    """The set of paths a note line names (code spans, and tokens holding /)."""
    out = set()
    for m in steps.SPAN_RE.finditer(note or ''):
        t = _clean(m.group(2))
        if t:
            out.add(t)
    for tok in steps.SPAN_RE.sub(' ', note or '').split():
        if '/' in tok:
            t = _clean(tok)
            if t and t != '/':
                out.add(t)
    return out


def _note(lines, heading):
    """(line number, text) of the first non-blank line under ## heading, else (None, '')."""
    inside = False
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            if inside:
                break
            inside = line.rstrip() == f'## {heading}'
            continue
        if inside and line.strip():
            return i, line.strip()
    return None, ''


def _changes(lines):
    """[(line number, path)] of the code spans under ## Changes."""
    out, inside = [], False
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            inside = line.rstrip() == '## Changes'
            continue
        if inside:
            for m in steps.SPAN_RE.finditer(line):
                t = _clean(m.group(2))
                if t:
                    out.append((i, t))
    return out


def _live_steps(rows):
    return [r for r in rows if r.get('step') is not None and not r.get('superseded')
            and r.get('task_dir')]


# --- detectors ---------------------------------------------------------------------------------

def criteria_never_red(ctx, aux):
    recs = aux.get('criteria_reruns') if isinstance(aux, dict) else None
    out = []
    for r in recs if isinstance(recs, list) else []:
        if not isinstance(r, dict) or r.get('exit_code') != 0:
            continue
        path, line = r.get('handoff'), r.get('line')
        if not isinstance(path, str) or not path or not isinstance(line, int):
            continue
        base = str(r.get('base_sha') or '')[:12]
        out.append(_make(ctx, 'criteria-never-red', 'agents/planner.md',
                         'a criterion must be red before the build',
                         [{'path': path, 'line': line}],
                         f'{path}:{line}: criterion already passes at base {base}: '
                         f'{str(r.get("span") or "")[:120]}'))
    return out


def contract_dependents(ctx):
    live = _live_steps(ctx.rows)
    builders, fails = {}, []
    for r in live:
        rel = _result(r)
        if not rel:
            continue
        if r.get('role') == 'builder' and _build_status(ctx, r) == 'done':
            builders.setdefault(r['task_dir'], []).append((r['step'], rel))
        elif r.get('role') == 'verifier' and r.get('verdict') == 'fail':
            fails.append((r['task_dir'], r['step'], rel))
    out, seen = [], set()
    for task, m, vrel in sorted(fails):
        vline, note = _note(ctx.lines(vrel), 'For the next attempt')
        named = note_paths(note)
        if not named:
            continue
        for n, brel in sorted(builders.get(task, [])):
            if n >= m or (vrel, brel) in seen:
                continue
            hits = [(i, p) for i, p in _changes(ctx.lines(brel)) if p in named]
            if not hits:
                continue
            seen.add((vrel, brel))
            paths = sorted({p for _, p in hits})
            out.append(_make(ctx, 'contract-dependents', 'agents/planner.md',
                             'a later step depends on an earlier step\'s contract',
                             [{'path': vrel, 'line': vline or 1},
                              {'path': brel, 'line': hits[0][0]}],
                             f'{task}: step {m} failed on {", ".join(paths)}, '
                             f'which step {n} changed'))
    return out


def _scope_widened_in_plan(ctx, task):
    for _, body in plan_review_entries(ctx.lines(f'{task}/handoff.md')):
        if any(SCOPE_WIDENED_RE.match(line) for line in body):
            return True
    return False


def _scope_widened_in_step(ctx, d):
    return any(line.rstrip() == '## Scope widened' for line in ctx.lines(f'{d}/handoff.md'))


def scope_prose(ctx):
    by_dir = {}
    for r in _live_steps(ctx.rows):
        d, rel = _row_dir(r), _result(r)
        if d and rel and r.get('role') == 'builder' and _build_status(ctx, r) == 'blocked':
            by_dir.setdefault(d, (r['task_dir'], []))[1].append(rel)
    out = []
    for d, (task, rels) in sorted(by_dir.items()):
        named = {}
        for rel in sorted(set(rels)):
            line, note = _note(ctx.lines(rel), 'Notes')
            for p in note_paths(note):
                named.setdefault(p, []).append((rel, line or 1))
        shared = {p: hits for p, hits in named.items() if len(hits) >= 2}
        if not shared:
            continue
        if _scope_widened_in_plan(ctx, task) or _scope_widened_in_step(ctx, d):
            continue
        evidence = sorted({(rel, line) for hits in shared.values() for rel, line in hits})
        out.append(_make(ctx, 'scope-prose', 'skills/chain/SKILL.md',
                         'widen scope with a scope widened: line, not in prose',
                         [{'path': rel, 'line': line} for rel, line in evidence],
                         f'{d}: {len(evidence)} blocked builds name {", ".join(sorted(shared))} '
                         'and the plan never widened the scope'))
    return out


def _gap_key(text):
    return ' '.join(text.lower().split()).rstrip(TRAIL + ' ')


def _gaps(lines):
    """[(line number, proposed text)] of a ui-designer result's Rule: gap proposals."""
    out, section = {'Guidance gaps': [], 'Findings': []}, None
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            section = line[3:].strip()
            continue
        if section not in out:
            continue
        hits = GAP_RE.findall(line)
        if hits:
            out[section] += [(i, h) for h in hits]
        elif section == 'Guidance gaps' and line.lstrip().startswith(('- ', '* ')):
            text = line.lstrip()[2:].strip().strip('`"\'')
            if text and text.lower() != 'none':
                out[section].append((i, text))
    return out['Guidance gaps'] or out['Findings']


def guidance_gap(ctx):
    groups = {}
    for r in ctx.rows:
        rel = _result(r)
        if r.get('role') != 'ui-designer' or r.get('superseded') or not rel:
            continue
        ticket = r.get('ticket') or r.get('task_dir')
        if not ticket:
            continue
        for line, text in _gaps(ctx.lines(rel)):
            key = _gap_key(text)
            if key:
                groups.setdefault(key, {}).setdefault(ticket, []).append((rel, line, text))
    out = []
    for key, by_ticket in sorted(groups.items()):
        if len(by_ticket) < ctx.t['guidance_gap_tickets']:
            continue
        first = [min(hits) for _, hits in sorted(by_ticket.items())]
        out.append(findings.make('guidance-gap', FAMILY, ctx.sev('guidance-gap'), 'project',
                                 None, first[0][2],
                                 [{'path': rel, 'line': line} for rel, line, _ in first],
                                 f'{len(by_ticket)} tickets report the guidance gap '
                                 f'"{first[0][2]}"'))
    return out


DETECTORS = ('criteria-never-red', 'contract-dependents', 'scope-prose', 'guidance-gap')


def detect(rows, aux, thresholds=None):
    ctx = _Ctx(rows, aux, thresholds)
    out = criteria_never_red(ctx, aux)
    out += contract_dependents(ctx)
    out += scope_prose(ctx)
    out += guidance_gap(ctx)
    return [f for f in out if f['detector'] in DETECTORS]
