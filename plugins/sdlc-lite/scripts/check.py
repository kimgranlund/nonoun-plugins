#!/usr/bin/env python3
"""Consistency checks for the sdlc-lite plugin. Exit 1 on any mismatch.

1. Level tables agree: scripts/run.sh (source of truth) vs skills/level-rubric vs CLAUDE.md.
2. Every agents/<role>.md has run.sh cases, and every run.sh role has an agent file.
3. Every skill an agent declares (frontmatter skills:) exists under skills/.
"""
import re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent)
errors = []

def cap(m): return m.capitalize()

# run.sh: "  builder:L1)  model=sonnet; effort=low ;;"
run = {}
for role, lvl, model, effort in re.findall(r'^\s*(\w+):(L\d)\)\s*model=(\w+);\s*effort=(\w+)', (root/'scripts/run.sh').read_text(), re.M):
    run[(role, lvl)] = f'{cap(model)} {effort}'
if not run: errors.append('run.sh: no role:level cases parsed')

# level-rubric: per-role sections "## builder (...)" with rows "| L1 | Sonnet low | ...",
# plus the single-level table rows "| architect | L1 | Fable high |".
rubric = {}
role = None
for line in (root/'skills/level-rubric/SKILL.md').read_text().splitlines():
    h = re.match(r'^## (\w+) \(L', line)
    if h: role = h.group(1); continue
    if line.startswith('## '): role = None
    m = re.match(r'^\| (L\d) \| (\w+ \w+) \|', line)
    if m and role: rubric[(role, m.group(1))] = m.group(2)
    m = re.match(r'^\| (\w+) \| (L\d) \| (\w+ \w+) \|', line)
    if m: rubric[(m.group(1), m.group(2))] = m.group(3)

# CLAUDE.md: builder table "  | L1 | Sonnet | low |", role table "  | Researcher | Sonnet medium | ... |",
# and roadmap rows for single-level roles "| scout | `/scout` | L1 Haiku low ...".
claude_md_path = next((p for p in (root/'CLAUDE.md', root.parent.parent/'CLAUDE.md') if p.exists()), None)
if claude_md_path is None: errors.append('CLAUDE.md not found at the plugin root or the repo root'); claude_md = ''
else: claude_md = claude_md_path.read_text()
doc = {}
for lvl, model, effort in re.findall(r'^\s*\| (L\d) \| (\w+) \| (\w+) \|\s*$', claude_md, re.M):
    doc[('builder', lvl)] = f'{model} {effort}'
for name, *cells in re.findall(r'^\s*\| (Researcher|Planner|Verifier) \| (\w+ \w+) \| (\w+ \w+) \| (\w+ \w+) \|', claude_md, re.M):
    for i, c in enumerate(cells): doc[(name.lower(), f'L{i+1}')] = c
for name, lvl, me in re.findall(r'^\| (\w+) \| `/\w+` \| (L\d) (?!to )(\w+ \w+)', claude_md, re.M):
    doc[(name, lvl)] = me

def compare(label, other):
    for k in sorted(set(run) | set(other)):
        if k not in other: errors.append(f'{label}: missing {k[0]}:{k[1]} (run.sh has {run[k]})')
        elif k not in run: errors.append(f'{label}: has {k[0]}:{k[1]} = {other[k]}, run.sh does not')
        elif run[k] != other[k]: errors.append(f'{label}: {k[0]}:{k[1]} = {other[k]}, run.sh = {run[k]}')
compare('level-rubric', rubric)
compare('CLAUDE.md', doc)

SESSION_AGENTS = {'conductor'}  # run as the main session (settings "agent"), not through run.sh
agents = {p.stem for p in (root/'agents').glob('*.md')} - SESSION_AGENTS
roles = {r for r, _ in run}
for r in sorted(agents - roles): errors.append(f'agents/{r}.md has no run.sh case')
for r in sorted(roles - agents): errors.append(f'run.sh role {r} has no agents/{r}.md')

for p in sorted((root/'agents').glob('*.md')):
    fm = p.read_text().split('---')[1] if p.read_text().startswith('---') else ''
    for sk in re.findall(r'^  - (\S+)$', fm.split('skills:', 1)[1], re.M) if 'skills:' in fm else []:
        if not (root/'skills'/sk/'SKILL.md').exists():
            errors.append(f'agents/{p.name} declares missing skill: {sk}')

# Long role runs: interactive sessions background them; headless sessions keep them in the foreground.
for rel in ('skills/chain/SKILL.md', 'skills/bench/SKILL.md', 'agents/conductor.md'):
    f = root/rel
    if not f.is_file(): errors.append(f'{rel}: missing (long-run doc check)'); continue
    text = f.read_text()
    missing = [w for w in ('interactive', 'run_in_background', 'notification', 'sleep') if w not in text]
    if missing: errors.append(f'{rel}: long-run rule missing words: {", ".join(missing)}')
    if 'never `run_in_background`' in text or 'never run_in_background' in text:
        errors.append(f'{rel}: still says "never run_in_background" unqualified')
for e in errors: print('FAIL', e)
print(f'{"FAIL" if errors else "ok"}: {len(run)} role levels, {len(agents)} agents checked')
sys.exit(1 if errors else 0)
