#!/usr/bin/env python3
"""Consistency checks for the sdlc-lite plugin. Exit 1 on any mismatch.

1. Level tables agree: scripts/run.sh (source of truth) vs skills/level-rubric. Repository guidance links these sources instead of copying tables.
2. Every agents/<role>.md has run.sh cases, and every run.sh role has an agent file.
3. Every skill an agent declares (frontmatter skills:) exists under skills/.
4. Long role runs: chain, bench, fanout, and conductor state the interactive vs headless rule.
5. Plan-defect route: the `plan defect` tag, the `Plan review` section, and the planner's
   "no new findings" rule appear in every doc and script that carries the route, and the
   `recurring finding` rule (a repeat fail or block takes a replan) appears in every doc that routes it,
   the parallel-lane rules ("sha fixed at plan time", linted by steps.py, "owns that budget", a guard that
   "can go red", and "membership or structure" checks) appear in the planner, the planner's "gates green" rule
   (whole-suite gate guards go on one final step, never on every step) appears in agents/planner.md, and the one-criterion swap (`swap old:` and `swap new:` lines on a plan-defect
   fail, applied by `steps.py swap`) appears in agents/verifier.md and scripts/steps.py, and the
   `steps.py swap` route appears in the conductor, the chain, handoff-format, and level-rubric skills,
   and the build-start base `SDLC_BASE_SHA` appears in the planner, builder, verifier, run.sh, and steps.py.
6. Merge-step template: the fenced merge-step block in agents/planner.md and
   skills/handoff-format/SKILL.md is present and identical, passes `steps.py lint`,
   runs its conflict-marker guard (merge-introduced markers only) against a throwaway repo in seven
   cases (empty merge, merge-added marker, clean lane marker line, kept conflict markers,
   both-sides lane marker line, aligned kept marker, clean merge), and agents/builder.md
   names `git merge --no-ff`. The aligned-marker case pins a known miss: a kept marker textually
   identical to a parent line that aligns with it shows as `+ ` or ` +`, not `++`.
7. /file likely duplicates: skills/file/SKILL.md names the dry run's `open T-NNNN` lines and
   the `likely duplicate` marking of follow-ups that restate an open ticket.
8. Inherited-red route: the phrase `inherited red` (a gate already red at the pre-build HEAD) appears in
   agents/builder.md, agents/verifier.md, agents/conductor.md, skills/chain/SKILL.md, scripts/steps.py, scripts/board.py,
   scripts/run.sh, scripts/fanout.py, and skills/fanout/SKILL.md.
9. Finish-in-session: the follow-up tags `fix-now:` and `decide:` and the `notes.md` sink appear in
   agents/filer.md, scripts/tickets.py, skills/file/SKILL.md, and skills/ticket/SKILL.md; `fix-now:` also in
   skills/chain/SKILL.md and agents/conductor.md; `decide:` also there and in skills/open-questions/SKILL.md;
   `notes.md` also in skills/handoff-format/SKILL.md and agents/conductor.md; and `Loose ends` (/chain 5) in
   skills/chain/SKILL.md, agents/filer.md, skills/handoff-format/SKILL.md, skills/level-rubric/SKILL.md, and
   agents/conductor.md.
10. Read-first route: the phrase `Read first` (entry files a role reads before a step) appears in
   agents/planner.md, agents/builder.md, agents/verifier.md, skills/fix/SKILL.md, skills/chain/SKILL.md,
   skills/handoff-format/SKILL.md, and scripts/steps.py.
"""
import re, sys, pathlib, subprocess, tempfile, shutil

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

def compare(label, other):
    for k in sorted(set(run) | set(other)):
        if k not in other: errors.append(f'{label}: missing {k[0]}:{k[1]} (run.sh has {run[k]})')
        elif k not in run: errors.append(f'{label}: has {k[0]}:{k[1]} = {other[k]}, run.sh does not')
        elif run[k] != other[k]: errors.append(f'{label}: {k[0]}:{k[1]} = {other[k]}, run.sh = {run[k]}')
compare('level-rubric', rubric)

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
for rel in ('skills/chain/SKILL.md', 'skills/bench/SKILL.md', 'skills/fanout/SKILL.md', 'agents/conductor.md',
            'skills/fix/SKILL.md'):
    f = root/rel
    if not f.is_file(): errors.append(f'{rel}: missing (long-run doc check)'); continue
    text = f.read_text()
    missing = [w for w in ('interactive', 'run_in_background', 'notification', 'sleep', 'SDLC_HEADLESS') if w not in text]
    if missing: errors.append(f'{rel}: long-run rule missing words: {", ".join(missing)}')
    if 'never `run_in_background`' in text or 'never run_in_background' in text:
        errors.append(f'{rel}: still says "never run_in_background" unqualified')
# Plan-defect route: a `plan defect` tag from the split lint, the builder, or the verifier goes to a replan.
PLAN_DEFECT_DOCS = {
    'plan defect': ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'agents/conductor.md',
                    'skills/chain/SKILL.md', 'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md',
                    'scripts/steps.py'),
    'Plan review': ('agents/planner.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md'),
    'no new findings': ('agents/planner.md',),
    'clean porcelain status': ('agents/planner.md', 'scripts/steps.py'),
    'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py'),
    'nonzero `exit`': ('agents/planner.md', 'scripts/steps.py'),
    'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py'),
    'changed the work tree': ('agents/planner.md', 'skills/chain/SKILL.md', 'scripts/steps.py'),
    'recurring finding': ('agents/planner.md', 'agents/conductor.md', 'skills/chain/SKILL.md',
                          'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md'),
    'sha fixed at plan time': ('agents/planner.md', 'scripts/steps.py'),
    'owns that budget': ('agents/planner.md',),
    'gates green': ('agents/planner.md',),
    'one Bash call': ('agents/planner.md',),
    'can go red': ('agents/planner.md',),
    'SDLC_BASE_SHA': ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'scripts/run.sh',
                      'scripts/steps.py'),
    'membership or structure': ('agents/planner.md',),
    'swap old:': ('agents/verifier.md', 'scripts/steps.py'),
    'swap new:': ('agents/verifier.md', 'scripts/steps.py'),
    'steps.py swap': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                      'skills/level-rubric/SKILL.md', 'scripts/steps.py'),
}
for word, rels in PLAN_DEFECT_DOCS.items():
    for rel in rels:
        f = root/rel
        if not f.is_file(): errors.append(f'{rel}: missing (plan-defect route check)'); continue
        if word not in f.read_text(): errors.append(f'{rel}: plan-defect route missing "{word}"')
# Inherited-red route: a builder Status `inherited red: <tests>` is routed, rendered, and accepted, never a fail.
INHERITED_RED_DOCS = ('agents/builder.md', 'agents/verifier.md', 'agents/conductor.md', 'skills/chain/SKILL.md',
                      'scripts/fanout.py', 'skills/fanout/SKILL.md',
                      'scripts/steps.py', 'scripts/board.py', 'scripts/run.sh')
for rel in INHERITED_RED_DOCS:
    f = root/rel
    if not f.is_file() or 'inherited red' not in f.read_text(): errors.append(f'{rel}: inherited-red route missing "inherited red"')
# Finish-in-session: follow-ups are tagged fix-now, decide, or note; only one decide item becomes a ticket.
FINISH_FILES = ('agents/filer.md', 'scripts/tickets.py', 'skills/file/SKILL.md', 'skills/ticket/SKILL.md')
CHAIN, CONDUCTOR, HANDOFF_FMT = 'skills/chain/SKILL.md', 'agents/conductor.md', 'skills/handoff-format/SKILL.md'
FINISH_DOCS = {'fix-now:': FINISH_FILES + (CHAIN, CONDUCTOR),
               'decide:': FINISH_FILES + (CHAIN, CONDUCTOR, 'skills/open-questions/SKILL.md'),
               'notes.md': FINISH_FILES + (HANDOFF_FMT, CONDUCTOR),
               'Loose ends': (CHAIN, 'agents/filer.md', HANDOFF_FMT, 'skills/level-rubric/SKILL.md', CONDUCTOR),
               'sdlc-lite:fix': (CONDUCTOR,),
               'fast lane': ('skills/fix/SKILL.md', CONDUCTOR, 'skills/level-rubric/SKILL.md')}
def finish_missing(text, word): return not re.search(re.escape(word) + r'(?![\w-])', text)
for word, rels in FINISH_DOCS.items():
    for rel in rels:
        f = root/rel
        if not f.is_file(): errors.append(f'{rel}: missing (finish-in-session check)'); continue
        text = f.read_text()
        if finish_missing(text, word): errors.append(f'{rel}: finish-in-session wording missing "{word}"')
        elif not finish_missing(text.replace(word, ''), word):
            errors.append(f'{rel}: finish-in-session negative control not flagged for "{word}"')
# Merge-step template: one block, kept identical in the planner and handoff-format, that lints clean.
def merge_block(rel):
    f = root/rel
    if not f.is_file(): return None
    out, inside = [], False
    for line in f.read_text().splitlines():
        if not inside and line == '```merge-step': inside = True; continue
        if inside and line == '```': return '\n'.join(out)
        if inside: out.append(line)
    return None
blocks = {rel: merge_block(rel) for rel in ('agents/planner.md', 'skills/handoff-format/SKILL.md')}
for rel, b in blocks.items():
    if not b or not b.strip(): errors.append(f'{rel}: merge-step block missing or empty')
pb, hb = blocks['agents/planner.md'], blocks['skills/handoff-format/SKILL.md']
if pb and hb and pb != hb: errors.append('merge-step block differs between agents/planner.md and skills/handoff-format/SKILL.md')
if pb and pb.strip():
    tmp = tempfile.mkdtemp()
    try:
        plan = pathlib.Path(tmp)/'planner-L2.md'
        plan.write_text(pb.replace('<n>', '1') + '\n')
        r = subprocess.run(['python3', str(root/'scripts/steps.py'), 'lint', str(plan)], capture_output=True, text=True)
        if r.returncode != 0: errors.append(f'merge-step block fails steps.py lint: {r.stderr.strip()}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
# Behavior probe: the conflict-marker guard fails only on markers the merge commit introduced.
# Seven cases: it passes an empty merge, fails on a marker the merge commit added (file name
# with a space), passes a lane line starting with >>>>>>> that merged cleanly, fails on kept git
# conflict markers, passes a lane line starting with >>>>>>> when both sides changed the file,
# passes an aligned kept marker, and passes a clean merge. The aligned-marker case pins a known
# miss: a kept marker textually identical to a parent line that aligns with it shows as `+ ` or
# ` +` in `git diff-tree --cc`, not `++`.
if pb and pb.strip():
    guard = next((l for l in pb.splitlines() if l.startswith('- (guard) ') and '<<<<<<<' in l), None)
    if guard is None or guard.count('`') < 2:
        errors.append('merge-step conflict-marker guard: criterion line missing')
    else:
        span = guard[guard.index('`') + 1:guard.rindex('`')]
        tmp = tempfile.mkdtemp()
        try:
            def g(*a):
                return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp,
                                      capture_output=True, text=True, check=True).stdout.strip()
            def span_rc():
                return subprocess.run(['bash', '-c', span], cwd=tmp, capture_output=True, text=True).returncode
            g('init', '-q', '-b', 'main')
            pathlib.Path(tmp, 'untouched.txt').write_text('<<<<<<< legit fixture\n')
            pathlib.Path(tmp, 'sp ace.txt').write_text('a\n')
            g('add', '-A'); g('commit', '-qm', 'base')
            g('checkout', '-qb', 'empty'); g('commit', '-q', '--allow-empty', '-m', 'empty')
            g('checkout', '-q', 'main'); g('merge', '-q', '--no-ff', '-m', 'merge empty', 'empty')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: empty merge flagged')
            pre = g('rev-parse', 'HEAD^1')
            def gr(*a):
                return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp,
                                      capture_output=True, text=True)
            def app(s):
                with open(pathlib.Path(tmp, 'sp ace.txt'), 'a') as fh: fh.write(s)
            g('checkout', '-qb', 'marker', pre)
            pathlib.Path(tmp, 'm.txt').write_text('m\n')
            g('add', '-A'); g('commit', '-qm', 'marker lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            g('merge', '-q', '--no-ff', '--no-commit', 'marker')
            app('>>>>>>> evil\n'); g('add', '-A'); g('commit', '-qm', 'merge marker')
            if span_rc() == 0: errors.append('merge-step conflict-marker guard: marker in touched file not flagged')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'legit', pre)
            app('>>>>>>> lane\n'); g('commit', '-qam', 'legit')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            g('merge', '-q', '--no-ff', '-m', 'merge legit', 'legit')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: legit lane line flagged')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'conflict', pre)
            pathlib.Path(tmp, 'sp ace.txt').write_text('lane\n'); g('commit', '-qam', 'lane side')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            pathlib.Path(tmp, 'sp ace.txt').write_text('main\n'); g('commit', '-qam', 'main side')
            gr('merge', '-q', '--no-ff', 'conflict')
            g('add', '-A'); g('commit', '-qm', 'merge conflict kept')
            if span_rc() == 0: errors.append('merge-step conflict-marker guard: kept conflict markers not flagged')
            g('reset', '-q', '--hard', pre)
            sp = pathlib.Path(tmp, 'sp ace.txt')
            g('checkout', '-qb', 'both', pre)
            sp.write_text('a\n>>>>>>> lane\n'); g('commit', '-qam', 'both lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', pre)
            sp.write_text('top\na\n'); g('commit', '-qam', 'both main')
            g('merge', '-q', '--no-ff', '-m', 'merge both', 'both')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: both-sides legit lane line flagged')
            g('reset', '-q', '--hard', pre)
            sp.write_text('a\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned base')
            b2 = g('rev-parse', 'HEAD')
            g('checkout', '-qb', 'aligned', b2)
            sp.write_text('lane\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned lane')
            g('checkout', '-q', 'main'); g('reset', '-q', '--hard', b2)
            sp.write_text('main\n>>>>>>> aligned\n'); g('commit', '-qam', 'aligned main')
            gr('merge', '-q', '--no-ff', 'aligned')
            sp.write_text(''.join(l for l in sp.read_text().splitlines(True) if not l.startswith(('<<<<<<<', '======='))))
            g('add', '-A'); g('commit', '-qm', 'merge aligned kept')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: aligned kept marker flagged; the documented limitation changed, update the merge-step docs')
            g('reset', '-q', '--hard', pre)
            g('checkout', '-qb', 'clean')
            pathlib.Path(tmp, 'ok file.txt').write_text('ok\n')
            g('add', '-A'); g('commit', '-qm', 'clean')
            g('checkout', '-q', 'main'); g('merge', '-q', '--no-ff', '-m', 'merge clean', 'clean')
            if span_rc() != 0: errors.append('merge-step conflict-marker guard: clean merge flagged')
        except subprocess.CalledProcessError as e:
            errors.append(f'merge-step conflict-marker guard: probe setup failed: {e.stderr.strip()}')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
b = root/'agents/builder.md'
if not b.is_file() or 'git merge --no-ff' not in b.read_text(): errors.append('agents/builder.md: missing "git merge --no-ff"')
f = root/'skills/file/SKILL.md'
ft = f.read_text() if f.is_file() else ''
for w in ('likely duplicate', 'open T-NNNN'):
    if w not in ft: errors.append(f'skills/file/SKILL.md: missing "{w}"')
# AskUserQuestion allows at most 4 options per question; the publish question must fit.
if 'at most 4 options' not in ft: errors.append('skills/file/SKILL.md: publish question missing "at most 4 options"')
# Step 3.3 follow-ups must batch within AskUserQuestion's 4-option limit.
def step33_bad(text):
    l33 = next((l for l in text.splitlines() if l.startswith('   3. When a person is present')), '')
    return 'at most 4 options per question' not in l33
if step33_bad(ft): errors.append('skills/file/SKILL.md: step 3.3 missing "at most 4 options per question"')
if not step33_bad(ft.replace('at most 4 options per question', '')): errors.append('check.py: step 3.3 guard negative control not flagged')
# Builder scope rules: formatters only on the files this step changed; kill only the PIDs you started.
SCOPE_PHRASES = ('files this step changed', 'PIDs you started')
def builder_scope_missing(text): return [s for s in SCOPE_PHRASES if s not in text]
bf = root/'agents/builder.md'
bt = bf.read_text() if bf.is_file() else ''
for s in builder_scope_missing(bt): errors.append(f'agents/builder.md: builder scope rule missing "{s}"')
for s in SCOPE_PHRASES:
    if s not in builder_scope_missing(bt.replace(s, '')): errors.append('check.py: builder scope guard negative control not flagged')
# Builder and verifier keep gates in the foreground: a headless run ends with the turn.
FG_PHRASE = 'never end the turn while background work runs'
for rel in ('agents/builder.md', 'agents/verifier.md'):
    fp = root/rel
    if not fp.is_file() or FG_PHRASE not in fp.read_text(): errors.append(f'{rel}: foreground rule missing "{FG_PHRASE}"')
step4 = next((l for l in ft.splitlines() if l.startswith('4. ')), '')
m = re.search(r'\(([^)]*)\)', step4)
if (m and 'issue' in m.group(1).lower()) or 'optional item' in step4: errors.append('skills/file/SKILL.md: step 4 lists GitHub issues among the publish options')
# /fix lints its handwritten step handoff, not the task folder (a folder lint needs a planner file /fix never writes).
def fix_lint_bad(text):
    targets = re.findall(r'steps\.py lint (\S+?)`', text)
    return not targets or any(not t.endswith('/step-1/handoff.md') for t in targets)
fx = root/'skills/fix/SKILL.md'
fxt = fx.read_text() if fx.is_file() else ''
if fix_lint_bad(fxt): errors.append('skills/fix/SKILL.md: steps.py lint target is not .sdlc/<slug>/step-1/handoff.md')
if not fix_lint_bad(fxt.replace('/step-1/handoff.md`', '`')): errors.append('check.py: /fix lint-target guard negative control not flagged')
# The conductor forbids substituting other plugins' agents for run.sh roles.
SUBST_PHRASE = "Other plugins' agents are not substitutes"
def subst_missing(text): return SUBST_PHRASE not in text
ct = (root/CONDUCTOR).read_text() if (root/CONDUCTOR).is_file() else ''
if subst_missing(ct): errors.append(f'{CONDUCTOR}: run.sh-only rule missing "{SUBST_PHRASE}"')
if not subst_missing(ct.replace(SUBST_PHRASE, '')): errors.append('check.py: substitute-agent guard negative control not flagged')
# Read-first route: every role and doc that carries step entry files names `Read first`.
READ_FIRST = 'Read first'
READ_FIRST_FILES = ('agents/planner.md', 'agents/builder.md', 'agents/verifier.md', 'skills/fix/SKILL.md',
                    'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py')
def read_first_missing(text): return READ_FIRST not in text
for rel in READ_FIRST_FILES:
    f = root/rel
    text = f.read_text() if f.is_file() else ''
    if read_first_missing(text): errors.append(f'{rel}: read-first route missing "{READ_FIRST}"')
    elif not read_first_missing(text.replace(READ_FIRST, '')):
        errors.append(f'{rel}: read-first negative control not flagged')
for e in errors: print('FAIL', e)
print(f'{"FAIL" if errors else "ok"}: {len(run)} role levels, {len(agents)} agents checked')
sys.exit(1 if errors else 0)
