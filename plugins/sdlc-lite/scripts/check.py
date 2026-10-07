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
11. Plan-review route (in the plan-defect route dict): `plan-reviewer` appears in scripts/run.sh, the level-rubric,
   chain, plan, and handoff-format skills, agents/conductor.md, and scripts/steps.py; `steps.py review` in the chain,
   plan, level-rubric, and handoff-format skills, agents/conductor.md, and scripts/steps.py; `## Assumptions` and
   `unresolved:` in agents/planner.md, agents/plan-reviewer.md, and scripts/steps.py; `Missing decisions` in
   agents/plan-reviewer.md, skills/chain/SKILL.md, and agents/conductor.md; and `plan review:` in agents/planner.md,
   skills/chain/SKILL.md, skills/handoff-format/SKILL.md, and agents/conductor.md.
12. Messenger agent: agents/messenger.md exists, pins `model: claude-haiku-4-5`, and names `messages.py` and
   `.sdlc/messages/AGENTS.md`; adapters/codex/models.json has a `messenger` entry; and the generated
   adapters/codex/agents/sdlc-messenger-l1.toml exists. Negative controls: empty text, no `messenger` key, no TOML.
13. Result schema: for each role in results.SCHEMA, agents/<role>.md has every declared section as a `## <Section>`
   line, first occurrences in declared order; scripts/run.sh and scripts/steps.py hold no copy of the schema table.
   Negative controls: builder body with `## Changes` and `## Checks` swapped; run.sh with an `allowed='x'` line.
14. Lean lane text: `## Lean chain` and `always runs the filer` appear in skills/chain/SKILL.md;
   `independently verifiable outcome` appears in agents/planner.md; and `steps lint: warning:` appears in
   agents/planner.md and scripts/steps.py. Each pair has a negative control (the phrase removed must be flagged).
15. Evals lock: when `<plugin>/../../.sdlc` exists, `scripts/evals.py check` must pass for it: every eval is valid,
   and `evals/table-lock.json` holds the current model-table hash and cites a valid eval dated later than its
   `previous_eval`. Each problem line prints as `FAIL evals: <line>`. With no such folder, the guard prints
   `skip: evals lock guard`. Negative control: run.sh with the builder:L1 model changed gives `model table changed`.
16. Spec gate: `guard timeout:` appears in agents/planner.md, skills/handoff-format/SKILL.md, scripts/steps.py,
   and scripts/specgate.py; `specgate.py check` appears in scripts/run.sh, skills/chain/SKILL.md, and
   agents/conductor.md; `specgate.py red` (the red-first control for a `(red)` criterion) appears in
   agents/solo.md, agents/planner.md, and scripts/steps.py; and the first `specgate.py check` line of run.sh comes before its
   `exec python3 "$plugin_root/scripts/run_lifecycle.py"` line. Negative controls: each phrase removed, and the
   two run.sh lines swapped, must be flagged.
17. Carry forward: `## Carry forward` appears in agents/scout.md, agents/researcher.md, agents/architect.md,
   agents/archaeologist.md, agents/planner.md, and agents/builder.md; `at most 15 lines` in the four producing
   contracts (scout, researcher, architect, archaeologist); `search only what it does not answer` in
   agents/planner.md and agents/builder.md; and `cite the result path` in agents/planner.md. Each pair has a
   negative control (the phrase removed must be flagged). results.SCHEMA declares `Carry forward` last for the
   four producing roles, so item 13 also requires the `## Carry forward` heading line there.
18. Solo agent: agents/solo.md exists and names tiers S, M, and L with `Sonnet low`, `Sonnet xhigh`, and
   `Opus xhigh`; adapters/codex/models.json has the `solo` entry L1 gpt-6.1-sol low, L2 gpt-6.1-sol high,
   L3 gpt-6.1-sol xhigh; and the generated adapters/codex/agents/sdlc-solo-l1..l3.toml exist. Negative controls:
   each phrase removed, no `solo` key, a changed `solo` entry, and one TOML missing must be flagged.
19. Conductor rules: agents/conductor.md names (1) the philosophy line and the objective line `cheapest path that
   still passes independent verification`, (2) lane-first routing (`Lane first: run` then `steps.py lane`) and the
   dispatch line `Lane: <lane> because <reason>`, (3) the stop rules `hard stop that comes to the user`, and (4) the
   thin-conductor rule `take back conclusions, not file contents or logs`. Each has a negative control (the phrase
   removed must be flagged).
20. Handoff freeze (warn mode): scripts/run_lifecycle.py names `SDLC_HANDOFF_SHA256` and `handoff_sha256`; scripts/run.sh
   names `SDLC_HANDOFF_SHA256`, `stale_input`, and `stale input:`; hooks/warn-handoff-edit.sh exists and is executable;
   adapters/claude/hooks.json registers it under an `Edit|Write|NotebookEdit` matcher; docs/references/claude-hooks.md names
   it. Each has a negative control (the phrase, file, or registration removed must be flagged).
21. Solo start path: agents/solo.md holds the start command `--agent sdlc-lite:solo`, and the routing texts send size
   S and M to `solo`: agents/conductor.md, skills/fix/SKILL.md, AGENTS.md, and (from the repository root)
   .claude/agents/sdlc-lite-author.md. Negative control: each phrase removed must be flagged.
22. Ticket budget: `budget.py set` appears in skills/ticket/SKILL.md; `budget.py` and the `4 ticket budget` exit line
   in scripts/run.sh; and `budget.py` in scripts/board.py. Each pair has a negative control (the phrase removed
   must be flagged).
23. Guard numbers: the docstring's numbered guards run 1..N once each, and every `docstring item N` comment names an
   existing one. Negative controls: a duplicated number, and a comment citing a missing item, must be flagged.
24. Fanout solo first: scripts/fanout.py names `sdlc-lite:solo`, `solo_command(`, `SOLO_VERIFIER`, `--max-lanes`,
   `--stagger`, `--yes-many`, and `--allow-overlap`; its SOLO_TIERS agree with the tiers in agents/solo.md (S `Sonnet
   low`, M `Sonnet xhigh`, L `Opus xhigh`) and the Codex levels L1..L3; skills/fanout/SKILL.md names `Solo first`,
   `--max-lanes`, and `--stagger`. Negative controls: a changed tier, and each phrase removed, must be flagged.
25. Agent command: skills/agent/SKILL.md names every agents/*.md stem in backticks, its start table names only
   agents that exist and have a Codex entry in adapters/codex/models.json, and it names `block-role-spawn.sh`.
   Negative controls: a stem removed from the skill, a table row for a name with no agent file, and a table row
   with no Codex entry must each be flagged.
26. Solo lane skips: scripts/steps.py names `solo_skips_text`, `write_solo_skips`, and calls `write_solo_skips(task)` in
   `record_lane`; scripts/fanout.py calls `steps.write_solo_skips`; agents/conductor.md says a solo ticket closes with
   `tickets.py close --reason`. Negative controls: each phrase removed must be flagged.
27. Solo cost capture: scripts/solo_run.py names `sdlc-lite:solo`, `SDLC_ROLE`, `cost_usd`, `cost_reason`, and `total_cost_usd`;
   its TIERS agree with the tiers in agents/solo.md and with fanout.py SOLO_TIERS; agents/solo.md names `solo_run.py` as the
   start path. Negative controls: a changed tier, a phrase removed from solo_run.py, and solo.md without `solo_run.py`, must be flagged.
28. Solo budget gate: scripts/solo_run.py names `budget_hold`, `budget.py ack`, `--new-task`, and returns 4 when it holds;
   scripts/fanout.py names `budget gate: budget.py ack`; agents/solo.md, skills/agent/SKILL.md, and skills/fanout/SKILL.md name
   the gate and `--new-task` where they start solo. Negative controls: each phrase removed from each file must be flagged.
29. Ask skill: skills/ask/SKILL.md names `## 1. Sweep`, `## 2. Reason the options`, `## 3. Ask once`, `## 4. Take prose`, `Write it in chat`,
   `Nothing open.`, `AskUserQuestion`, the sweep searches (blocked tickets and `## Verdict` results), and the plain-text fallback
   `If AskUserQuestion is unavailable`, and holds no `harness:` reference; skills/sdlc-lite/SKILL.md and agents/conductor.md route to
   `ask`. Negative controls: each phrase removed, a harness reference added, and a routing line removed must be flagged.
30. Document inventory: scripts/inventory.py names the flags `orphan`, `stale`, `duplicate`, `oversized`, `misplaced`, and `broken_links`, the options
   `--include-sdlc` and `--out`, and refuses to write inside the repository; scripts/check.sh runs `inventory.py selftest`;
   docs/planning/repo-onboarding/reorganization-plan-procedure.md names `inventory.py`. Negative controls: each phrase removed from each file must be flagged.
31. Plan skills: skills/plan-goal, plan-loop, and plan-fanout each name `## 1. Gather`, `plan_check.py`, `AskUserQuestion`, `Why this plan`,
   `You must authorize`, `Unattended`, and `Codex host`, hold no `harness:` reference, and are routed from skills/sdlc-lite/SKILL.md.
   Negative controls: each phrase removed, a harness reference added, and a routing line removed must be flagged.
32. Broken-link baseline: the broken relative Markdown links that rename_refs.py `links` reports (code fences and inline code excluded)
   equal the rows of docs/reports/broken-links-allowlist.md. Negative controls: an extra broken link and a stale allowlist row must be flagged.
33. Docs check: scripts/docs_check.py names rules `D-1` to `D-12`, `B-1a`, `B-2a`, `B-3a`, the options `--root` and `--only`, and `Legacy`; scripts/check.sh runs
   `docs_check.py" selftest` and `docs_check.py" --root` on this repository. Negative controls: each phrase removed from each file must be flagged.
34. Product name: live tracked files hold none of the retired spellings of SDLC Lite listed in NAME_BANNED, outside the NAME_ALLOW history paths
   (docs/reports, closed tickets, run workspaces under .sdlc, bench results). Negative control: a planted spelling must be flagged and an allowlisted path must not.
35. Gate lock: scripts/gate_lock.py names `SLOT-CAP`, `SDLC_GATE_WORKERS`, `SDLC_GATE_SLOTS`, and `sdlc-gate-locks`; scripts/check.sh runs `gate_lock.py" selftest`;
   scripts/fanout.py names `gate_lock.py` and `--no-gate-lock`; agents/conductor.md names `gate_lock.py run`; and, where docs/references/sdlc-internals.md exists,
   it names `gate_lock.py`. Negative controls: each phrase removed from each file must be flagged.
36. Fleet retro: skills/fleet-retro/SKILL.md names `fleet_collect.py`, `fleet_detect.py`, `SendMessage`, `interview.md`, `rubric.md`, `AskUserQuestion`,
   `review-traces`, `Codex host`, `SDLC_HEADLESS`, and the stages `## 1. Collect` to `## 6. File`, and holds no `harness:` reference; skills/fleet-retro/rubric.md names
   gates `G1` to `G5`, criteria `C1` to `C5`, `7 of 10`, and `Outcome check`; skills/fleet-retro/fixtures.md names `F1`, `F2`, `F3`; skills/sdlc-lite/SKILL.md and
   agents/conductor.md route to `fleet-retro`; and, where docs/references/sdlc-internals.md exists, it names `fleet-retro`. Negative controls: each phrase removed
   from each file, a harness reference added, and a missing route must be flagged.
37. Fleet status: skills/fleet-status/SKILL.md names `fleet_status.py render`, `## 1. Render`, `## 2. Print it`, `## 3. Ask once`, `## 4. Relay, do not act`,
   `Render, never compose`, `AskUserQuestion`, `If AskUserQuestion is unavailable`, `--ping`, `sends nothing`, and `Codex host`, and holds no `harness:` reference;
   skills/sdlc-lite/SKILL.md routes to `fleet-status`; scripts/fleet_status.py names `RenderError`, `def render(`, `def schema_errors`, and `def selftest_render`;
   scripts/check.sh runs `fleet_status.py" selftest`; skills/fleet-status/SKILL.md links `resources/fleet-status.schema.json`, and that file exists, parses as
   JSON, declares draft 2020-12, and requires the `machine`, `repos`, `needs_you`, and `delta` keys. Negative controls: each phrase removed from each file, a
   harness reference added, the routing line removed, and a missing, unparsable, wrong-draft, or key-less schema file must be flagged.
"""
import os, re, sys, json, pathlib, subprocess, tempfile, shutil

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent)
errors = []

def cap(m):
    """Alias -> "Sonnet"; pinned id claude-<family>-<major>-<minor> -> "Haiku 4.5"."""
    pin = re.fullmatch(r'claude-([a-z]+)-(\d+)-(\d+)', m)
    return f'{pin.group(1).capitalize()} {pin.group(2)}.{pin.group(3)}' if pin else m.capitalize()

# run.sh: "  builder:L1)  model=sonnet; effort=low ;;"
run = {}
for role, lvl, model, effort in re.findall(r'^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)', (root/'scripts/run.sh').read_text(), re.M):
    run[(role, lvl)] = f'{cap(model)} {effort}'
if not run: errors.append('run.sh: no role:level cases parsed')

# level-rubric: per-role sections "## builder (...)" with rows "| L1 | Sonnet low | ...",
# plus the single-level table rows "| architect | L1 | Fable high |".
rubric = {}
role = None
for line in (root/'skills/level-rubric/SKILL.md').read_text().splitlines():
    h = re.match(r'^## ([\w-]+) \(L', line)
    if h: role = h.group(1); continue
    if line.startswith('## '): role = None
    m = re.match(r'^\| (L\d) \| (\w+(?: \d+\.\d+)? \w+) \|', line)
    if m and role: rubric[(role, m.group(1))] = m.group(2)
    m = re.match(r'^\| ([\w-]+) \| (L\d) \| (\w+(?: \d+\.\d+)? \w+) \|', line)
    if m: rubric[(m.group(1), m.group(2))] = m.group(3)

def compare(label, other):
    for k in sorted(set(run) | set(other)):
        if k not in other: errors.append(f'{label}: missing {k[0]}:{k[1]} (run.sh has {run[k]})')
        elif k not in run: errors.append(f'{label}: has {k[0]}:{k[1]} = {other[k]}, run.sh does not')
        elif run[k] != other[k]: errors.append(f'{label}: {k[0]}:{k[1]} = {other[k]}, run.sh = {run[k]}')
compare('level-rubric', rubric)
# Scout pin guard: run.sh scout row and rubric scout row agree, with a built-in negative control.
def scout_mismatch(run_text, rubric_text):
    m = re.search(r'^\s*scout:L1\)\s*model=([\w-]+);\s*effort=(\w+)', run_text, re.M)
    r = re.search(r'^\| scout \| L1 \| (\w+(?: \d+\.\d+)? \w+) \|', rubric_text, re.M)
    return not (m and r and f'{cap(m.group(1))} {m.group(2)}' == r.group(1))
_rs, _rb = (root/'scripts/run.sh').read_text(), (root/'skills/level-rubric/SKILL.md').read_text()
if scout_mismatch(_rs, _rb): errors.append('run.sh scout:L1 and level-rubric scout row disagree')
if cap('claude-haiku-4-5') != 'Haiku 4.5' or cap('sonnet') != 'Sonnet':
    errors.append('check.py: cap() pinned-id mapping broken')
if not scout_mismatch(re.sub(r'(scout:L1\)\s*model=)[\w-]+', r'\g<1>claude-haiku-9-9', _rs), _rb):
    errors.append('check.py: scout pin guard negative control not flagged')

SESSION_AGENTS = {'conductor', 'messenger', 'solo'}  # all run as session agents (main session or its sub-agent), not through run.sh
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
    'contract dependents': ('agents/planner.md', 'agents/verifier.md'),
    'steps.py widen': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                       'skills/level-rubric/SKILL.md', 'scripts/steps.py'),
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
    # Plan-review route (docstring item 11): a plan the rubric names is reviewed before any split.
    'plan-reviewer': ('scripts/run.sh', 'skills/level-rubric/SKILL.md', 'skills/chain/SKILL.md', 'agents/conductor.md',
                      'skills/plan/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py'),
    'steps.py review': ('skills/chain/SKILL.md', 'agents/conductor.md', 'skills/plan/SKILL.md',
                        'skills/level-rubric/SKILL.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py'),
    '## Assumptions': ('agents/planner.md', 'agents/plan-reviewer.md', 'scripts/steps.py'),
    'unresolved:': ('agents/planner.md', 'agents/plan-reviewer.md', 'scripts/steps.py'),
    'Missing decisions': ('agents/plan-reviewer.md', 'skills/chain/SKILL.md', 'agents/conductor.md'),
    'plan review:': ('agents/planner.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md',
                     'agents/conductor.md'),
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
if fix_lint_bad(fxt): errors.append('skills/fix/SKILL.md: steps.py lint target is not <ticket dir>/<slug>/step-1/handoff.md (.sdlc/<slug>/..., or .sdlc/tickets/<slug>/... with ticket_root: tickets)')
if not fix_lint_bad(fxt.replace('/step-1/handoff.md`', '`')): errors.append('check.py: /fix lint-target guard negative control not flagged')
# /fix step 5 stops at publish when unattended: no push, no pull request.
def fix_unattended_bad(text):
    m = re.search(r'^5\. .*$', text, re.M)
    return not m or 'Unattended' not in m.group(0) or 'never push' not in m.group(0)
if fix_unattended_bad(fxt): errors.append('skills/fix/SKILL.md: step 5 lacks the Unattended rule with "never push"')
if not fix_unattended_bad(fxt.replace('never push', 'push')): errors.append('check.py: /fix unattended-publish guard negative control not flagged')
# The conductor forbids substituting other plugins' agents for run.sh roles.
SUBST_PHRASE = "Other plugins' agents are not substitutes"
def subst_missing(text): return SUBST_PHRASE not in text
ct = (root/CONDUCTOR).read_text() if (root/CONDUCTOR).is_file() else ''
if subst_missing(ct): errors.append(f'{CONDUCTOR}: run.sh-only rule missing "{SUBST_PHRASE}"')
if not subst_missing(ct.replace(SUBST_PHRASE, '')): errors.append('check.py: substitute-agent guard negative control not flagged')
# Plan-reviewer role: run.sh holds its L1 row and validates every result through results.py, whose schema gives
# plan-reviewer the key section Verdict with the allowed values pass, replan, blocked.
sys.path.insert(0, str(root/'scripts'))
import results
PR_VALIDATE = 'results.py" validate'
def plan_reviewer_missing(runs, text, schema):
    out = []
    if ('plan-reviewer', 'L1') not in runs: out.append('no plan-reviewer:L1 row')
    spec = schema.get('plan-reviewer', {})
    if spec.get('key') != 'Verdict' or [a[0] for a in spec.get('allowed', ())] != ['pass', 'replan', 'blocked']:
        out.append('results.py SCHEMA plan-reviewer is not key Verdict with allowed pass, replan, blocked')
    if PR_VALIDATE not in text: out.append(f'no result check "{PR_VALIDATE}"')
    return out
rt = (root/'scripts/run.sh').read_text()
for e in plan_reviewer_missing(run, rt, results.SCHEMA): errors.append(f'scripts/run.sh: plan-reviewer role: {e}')
bad_schema = dict(results.SCHEMA)
bad_schema['plan-reviewer'] = dict(bad_schema['plan-reviewer'], allowed=(('pass', r'pass', 'pass'), ('fail', r'fail', 'fail')))
no_pr_row = {k: v for k, v in run.items() if k[0] != 'plan-reviewer'}
for name, args, want in (('L1 row', (no_pr_row, rt, results.SCHEMA), 'no plan-reviewer:L1 row'),
                         ('schema', (run, rt, bad_schema), 'results.py SCHEMA'),
                         ('validate call', (run, rt.replace(PR_VALIDATE, 'results.py" schema'), results.SCHEMA),
                          'no result check')):
    if not any(e.startswith(want) for e in plan_reviewer_missing(*args)):
        errors.append(f'check.py: plan-reviewer run.sh guard negative control ({name}) not flagged')
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
# Lean lane text (docstring item 14): the lean chain section and the coarse-step rule name their phrases.
LEAN_LANE = {'## Lean chain': ('skills/chain/SKILL.md',),
             'always runs the filer': ('skills/chain/SKILL.md',),
             'independently verifiable outcome': ('agents/planner.md',),
             'steps lint: warning:': ('agents/planner.md', 'scripts/steps.py')}
def lean_missing(text, phrase): return phrase not in text
for phrase, rels in LEAN_LANE.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if lean_missing(text, phrase): errors.append(f'{rel}: lean lane text missing "{phrase}"')
        elif not lean_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: lean-lane negative control not flagged')
# Spec gate text (docstring item 16): the guard timeout line and the run.sh gate are named where they route.
SPEC_GATE = {'guard timeout:': ('agents/planner.md', 'skills/handoff-format/SKILL.md', 'scripts/steps.py', 'scripts/specgate.py'),
             'specgate.py check': ('scripts/run.sh', 'skills/chain/SKILL.md', 'agents/conductor.md'),
             'specgate.py red': ('agents/solo.md', 'agents/planner.md', 'scripts/steps.py')}
def spec_gate_missing(text, phrase): return phrase not in text
for phrase, rels in SPEC_GATE.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if spec_gate_missing(text, phrase): errors.append(f'{rel}: spec gate text missing "{phrase}"')
        elif not spec_gate_missing(text.replace(phrase, ''), phrase):
            errors.append(f'check.py: spec gate text negative control not flagged for {rel}')
SPEC_GATE_EXEC = 'exec python3 "$plugin_root/scripts/run_lifecycle.py"'
def spec_gate_order_bad(lines):
    gate = next((i for i, l in enumerate(lines) if 'specgate.py check' in l), None)
    run = next((i for i, l in enumerate(lines) if SPEC_GATE_EXEC in l), None)
    return gate is None or run is None or gate > run
rs_lines = (root/'scripts/run.sh').read_text().split('\n') if (root/'scripts/run.sh').is_file() else []
if spec_gate_order_bad(rs_lines):
    errors.append('scripts/run.sh: specgate.py check does not come before exec run_lifecycle.py')
else:
    gi = next(i for i, l in enumerate(rs_lines) if 'specgate.py check' in l)
    ri = next(i for i, l in enumerate(rs_lines) if SPEC_GATE_EXEC in l)
    swapped = list(rs_lines); swapped[gi], swapped[ri] = swapped[ri], swapped[gi]
    if not spec_gate_order_bad(swapped): errors.append('check.py: spec gate order negative control not flagged')
# Carry forward (docstring item 17): producer contracts end with the section; planner and builder read it first.
CF_PRODUCERS = ('agents/scout.md', 'agents/researcher.md', 'agents/architect.md', 'agents/archaeologist.md')
CARRY_FORWARD = {'## Carry forward': CF_PRODUCERS + ('agents/planner.md', 'agents/builder.md'),
                 'at most 15 lines': CF_PRODUCERS,
                 'search only what it does not answer': ('agents/planner.md', 'agents/builder.md'),
                 'cite the result path': ('agents/planner.md',)}
def carry_forward_missing(text, phrase): return phrase not in text
for phrase, rels in CARRY_FORWARD.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if carry_forward_missing(text, phrase): errors.append(f'{rel}: carry-forward text missing "{phrase}"')
        elif not carry_forward_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: carry-forward negative control not flagged')
# Ticket budget (docstring item 22): filing sets it, run.sh gates on it (exit 4), board.py renders it.
TICKET_BUDGET = {'budget.py set': ('skills/ticket/SKILL.md',),
                 'budget.py': ('scripts/run.sh', 'scripts/board.py'),
                 '4 ticket budget': ('scripts/run.sh',)}
def ticket_budget_missing(text, phrase): return phrase not in text
for phrase, rels in TICKET_BUDGET.items():
    for rel in rels:
        f = root/rel
        text = f.read_text() if f.is_file() else ''
        if ticket_budget_missing(text, phrase): errors.append(f'{rel}: ticket-budget text missing "{phrase}"')
        elif not ticket_budget_missing(text.replace(phrase, ''), phrase):
            errors.append(f'{rel}: ticket-budget negative control not flagged')
# Messenger agent (docstring item 12): a session sub-agent with a Claude file, a Codex mapping, and a generated TOML.
MESSENGER_WORDS = ('model: claude-haiku-4-5', 'messages.py', '.sdlc/messages/AGENTS.md')
def messenger_missing(agent_text, codex_models, toml_present):
    out = []
    if not agent_text.strip(): out.append('messenger: agents/messenger.md missing or empty')
    else: out += [f'messenger: agents/messenger.md missing "{w}"' for w in MESSENGER_WORDS if w not in agent_text]
    if 'messenger' not in codex_models: out.append('messenger: adapters/codex/models.json has no messenger entry')
    if not toml_present: out.append('messenger: adapters/codex/agents/sdlc-messenger-l1.toml missing')
    return out
mf, mj = root/'agents/messenger.md', root/'adapters/codex/models.json'
mt = mf.read_text() if mf.is_file() else ''
mc = json.loads(mj.read_text()) if mj.is_file() else {}
mtoml = (root/'adapters/codex/agents/sdlc-messenger-l1.toml').is_file()
errors.extend(messenger_missing(mt, mc, mtoml))
if (not messenger_missing('', mc, mtoml) or not messenger_missing(mt, {k: v for k, v in mc.items() if k != 'messenger'}, mtoml)
        or not messenger_missing(mt, mc, False)):
    errors.append('check.py: messenger guard negative control not flagged')
# Solo agent (docstring item 18): a session agent with tiers S, M, L, a Codex mapping, and three generated TOMLs.
SOLO_WORDS = ('| S |', '| M |', '| L |', 'Sonnet low', 'Sonnet xhigh', 'Opus xhigh')
SOLO_CODEX = {'L1': ['gpt-6.1-sol', 'low'], 'L2': ['gpt-6.1-sol', 'high'], 'L3': ['gpt-6.1-sol', 'xhigh']}
def solo_missing(agent_text, codex_models, tomls):
    out = []
    if not agent_text.strip(): out.append('solo: agents/solo.md missing or empty')
    else: out += [f'solo: agents/solo.md missing "{w}"' for w in SOLO_WORDS if w not in agent_text]
    if codex_models.get('solo') != SOLO_CODEX: out.append(f'solo: adapters/codex/models.json solo entry is not {SOLO_CODEX}')
    out += [f'solo: adapters/codex/agents/sdlc-solo-{l}.toml missing' for l in ('l1', 'l2', 'l3') if l not in tomls]
    return out
sf = root/'agents/solo.md'
st = sf.read_text() if sf.is_file() else ''
stomls = {l for l in ('l1', 'l2', 'l3') if (root/f'adapters/codex/agents/sdlc-solo-{l}.toml').is_file()}
errors.extend(solo_missing(st, mc, stomls))
if not solo_missing(st, mc, stomls) and (
        any(not solo_missing(st.replace(w, ''), mc, stomls) for w in SOLO_WORDS)
        or not solo_missing('', mc, stomls)
        or not solo_missing(st, {k: v for k, v in mc.items() if k != 'solo'}, stomls)
        or not solo_missing(st, dict(mc, solo=dict(SOLO_CODEX, L2=['gpt-6.1-sol', 'xhigh'])), stomls)
        or not solo_missing(st, mc, stomls - {'l3'})):
    errors.append('check.py: solo guard negative control not flagged')
# Conductor rules (docstring item 19): philosophy and objective, lane first, stop rules, thin conductor.
CONDUCTOR_RULES = ('Done is better than perfect. Trust that modern, advanced models are very capable if given useful '
                   'context and instruction.',
                   'cheapest path that still passes independent verification',
                   'Lane first: run `steps.py lane',
                   'Lane: <lane> because <reason>',
                   'hard stop that comes to the user',
                   'take back conclusions, not file contents or logs')
def conductor_rule_missing(text, phrase): return phrase not in text
for phrase in CONDUCTOR_RULES:
    if conductor_rule_missing(ct, phrase): errors.append(f'{CONDUCTOR}: conductor rules missing "{phrase}"')
    elif not conductor_rule_missing(ct.replace(phrase, ''), phrase):
        errors.append(f'check.py: conductor rules negative control not flagged for "{phrase}"')
# Result schema (docstring item 13): agent bodies carry results.SCHEMA sections in order; no script copies the table.
def schema_section_errors(text, sections):
    lines = [l.rstrip() for l in text.splitlines()]
    out, pos = [], []
    for sec in sections:
        h = f'## {sec}'
        if h not in lines: out.append(f'missing {h}')
        else: pos.append((lines.index(h), sec))
    for (a, x), (b, y) in zip(pos, pos[1:]):
        if b < a: out.append(f'## {y} before ## {x}')
    return out
for role, spec in results.SCHEMA.items():
    af = root/f'agents/{role}.md'
    for e in schema_section_errors(af.read_text() if af.is_file() else '', spec['sections']):
        errors.append(f'agents/{role}.md: result schema: {e}')
_bt = (root/'agents/builder.md').read_text() if (root/'agents/builder.md').is_file() else ''
_swapped = _bt.replace('## Changes', '## TMPX').replace('## Checks', '## Changes').replace('## TMPX', '## Checks')
if not schema_section_errors(_swapped, results.SCHEMA['builder']['sections']):
    errors.append('check.py: result-schema agent guard negative control not flagged')
SCHEMA_COPY = {'scripts/run.sh': r"allowed='|sect=[A-Z]",
               'scripts/steps.py': r"REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'"}
for rel, rx in SCHEMA_COPY.items():
    f = root/rel
    if f.is_file() and re.search(rx, f.read_text()): errors.append(f'{rel}: holds a copy of the result schema')
if not re.search(SCHEMA_COPY['scripts/run.sh'], rt + "\nallowed='x'\n"):
    errors.append('check.py: result-schema copy guard negative control not flagged')
sdlc = root.resolve().parent.parent / '.sdlc'
if sdlc.is_dir():
    def _evals(plugin):
        return subprocess.run([sys.executable, str(root/'scripts/evals.py'), '--root', str(sdlc), '--plugin', str(plugin), 'check'],
                              capture_output=True, text=True)
    _r = _evals(root)
    if _r.returncode != 0:
        _lines = [l for l in (_r.stdout + '\n' + _r.stderr).splitlines() if l.strip() and not l.startswith('evals check:')]
        errors.extend(f'evals: {l}' for l in _lines) if _lines else errors.append(f'evals: evals.py check exited {_r.returncode}')
    else:
        with tempfile.TemporaryDirectory() as _td:
            _tp = pathlib.Path(_td)
            (_tp/'scripts').mkdir(); (_tp/'adapters/codex').mkdir(parents=True)
            (_tp/'scripts/run.sh').write_text(re.sub(r'(builder:L1\)\s*model=)[\w-]+', r'\g<1>evals-negative-control', rt))
            shutil.copy(root/'adapters/codex/models.json', _tp/'adapters/codex/models.json')
            _n = _evals(_tp)
            if 'model table changed' not in _n.stdout + _n.stderr:
                errors.append('check.py: evals lock guard negative control not flagged')
else:
    print(f'skip: evals lock guard (no {sdlc})')
# Handoff freeze (docstring item 20): runner, lifecycle, hook file, registration, and the hooks doc agree.
FREEZE_RUN = ('SDLC_HANDOFF_SHA256', 'stale_input', 'stale input:')
FREEZE_LIFE = ('SDLC_HANDOFF_SHA256', 'handoff_sha256')
def freeze_missing(run_text, life_text, hook_ok, hooks_json, docs_text):
    out = [f'handoff freeze: scripts/run.sh missing "{w}"' for w in FREEZE_RUN if w not in run_text]
    out += [f'handoff freeze: scripts/run_lifecycle.py missing "{w}"' for w in FREEZE_LIFE if w not in life_text]
    if not hook_ok: out.append('handoff freeze: hooks/warn-handoff-edit.sh missing or not executable')
    if not re.search(r'"matcher":\s*"Edit\|Write\|NotebookEdit"[^]]*warn-handoff-edit\.sh', hooks_json):
        out.append('handoff freeze: adapters/claude/hooks.json does not register warn-handoff-edit.sh under Edit|Write|NotebookEdit')
    if 'warn-handoff-edit.sh' not in docs_text: out.append('handoff freeze: docs/references/claude-hooks.md does not name warn-handoff-edit.sh')
    return out
def _rd(path): return path.read_text() if path.is_file() else ''
_hook = root/'hooks/warn-handoff-edit.sh'
_hook_ok = _hook.is_file() and os.access(_hook, os.X_OK)
_fr = (_rd(root/'scripts/run.sh'), _rd(root/'scripts/run_lifecycle.py'), _hook_ok, _rd(root/'adapters/claude/hooks.json'),
       _rd(root.resolve().parent.parent/'docs/references/claude-hooks.md'))
errors.extend(freeze_missing(*_fr))
for _i, _w in ((0, FREEZE_RUN[1]), (1, FREEZE_LIFE[1]), (4, 'warn-handoff-edit.sh'), (3, 'warn-handoff-edit.sh')):
    _args = list(_fr); _args[_i] = _args[_i].replace(_w, '')
    if not freeze_missing(*_args): errors.append(f'check.py: handoff freeze guard negative control not flagged for "{_w}"')
if not freeze_missing(_fr[0], _fr[1], False, _fr[3], _fr[4]): errors.append('check.py: handoff freeze guard negative control not flagged for the hook file')
# Solo start path (docstring item 21): solo.md holds the start command; every routing text sends S and M to solo.
SOLO_ROUTE = (('agents/solo.md', '--agent sdlc-lite:solo'),
              (CONDUCTOR, 'Size S and M go to `solo` by default'),
              ('skills/fix/SKILL.md', 'size S and M go to `solo`'),
              ('AGENTS.md', 'Size S and M plugin work goes to `solo` by default'),
              ('.claude/agents/sdlc-lite-author.md', '`solo` for size S and M by default'))
def solo_route_missing(text, phrase): return phrase not in text
for rel, phrase in SOLO_ROUTE:
    srt = _rd(root.resolve().parent.parent/rel) if rel.startswith('.claude/') else _rd(root/rel)
    if solo_route_missing(srt, phrase): errors.append(f'{rel}: solo start path missing "{phrase}"')
    elif not solo_route_missing(srt.replace(phrase, ''), phrase):
        errors.append(f'check.py: solo start path negative control not flagged for "{phrase}"')
# Guard numbers (docstring item 23): the docstring's numbered guards run 1..N once each, and every "docstring item N" comment names one.
def guard_numbers_bad(doc, src):
    nums = [int(n) for n in re.findall(r'(?m)^(\d+)\. ', doc)]
    bad = []
    if nums != list(range(1, len(nums) + 1)): bad.append(f'docstring guard numbers are not 1..{len(nums)} once each: {nums}')
    bad += [f'comment cites docstring item {n}, which does not exist' for n in sorted({int(n) for n in re.findall(r'docstring item (\d+)', src)} - set(nums))]
    return bad
_src = pathlib.Path(__file__).read_text()
for _b in guard_numbers_bad(__doc__, _src): errors.append(f'check.py: {_b}')
_dup = __doc__.replace('\n19. Conductor rules', '\n18. Conductor rules', 1)
if not guard_numbers_bad(_dup, _src): errors.append('check.py: guard numbers negative control not flagged for a duplicated number')
if not guard_numbers_bad(__doc__, _src + '\n# x (docstring ' + 'item 99)'): errors.append('check.py: guard numbers negative control not flagged for a missing item')
# Fanout solo first (docstring item 24): fanout.py picks the lane per ticket and starts solo at the solo.md tiers.
FANOUT_PHRASES = ('sdlc-lite:solo', 'solo_command(', 'SOLO_VERIFIER', '--max-lanes', '--stagger', '--yes-many', '--allow-overlap')
FANOUT_SKILL_PHRASES = ('Solo first', '--max-lanes', '--stagger')
def fanout_solo_bad(fan, solo, skill):
    bad = [f'fanout.py missing "{ph}"' for ph in FANOUT_PHRASES if ph not in fan]
    bad += [f'skills/fanout/SKILL.md missing "{ph}"' for ph in FANOUT_SKILL_PHRASES if ph not in skill]
    tiers = re.findall(r"'([SML])': \('(\w+)', '(\w+)', '(L\d)'\)", fan)
    if sorted(t[0] for t in tiers) != ['L', 'M', 'S']: bad.append('fanout.py SOLO_TIERS does not list S, M, and L')
    for tier, model, effort, level in tiers:
        if not re.search(rf'^\| {tier} \| {tier} \| {model.capitalize()} {effort} \|', solo, re.M): bad.append(f'SOLO_TIERS {tier} {model} {effort} is not the tier {tier} row of agents/solo.md')
        if level != {'S': 'L1', 'M': 'L2', 'L': 'L3'}[tier]: bad.append(f'SOLO_TIERS {tier} has Codex level {level}')
    return bad
_ff, _fs, _fk = _rd(root/'scripts/fanout.py'), _rd(root/'agents/solo.md'), _rd(root/'skills/fanout/SKILL.md')
errors.extend(fanout_solo_bad(_ff, _fs, _fk))
for _mut in (lambda t: t.replace("'M': ('sonnet', 'xhigh', 'L2')", "'M': ('sonnet', 'low', 'L2')"), lambda t: t.replace('--stagger', '--pause')):
    if not fanout_solo_bad(_mut(_ff), _fs, _fk): errors.append('check.py: fanout solo first negative control not flagged for a changed fanout.py')
if not fanout_solo_bad(_ff, _fs, _fk.replace('Solo first', '')): errors.append('check.py: fanout solo first negative control not flagged for the skill')
# Agent command (docstring item 25): the /agent skill's names agree with agents/*.md and the Codex mapping.
def agent_cmd_bad(skill, stems, codex_keys):
    if not skill.strip(): return ['skills/agent/SKILL.md missing or empty']
    bad = [f'skills/agent/SKILL.md does not name `{n}`' for n in sorted(stems) if f'`{n}`' not in skill]
    rows = re.findall(r'(?m)^\| `([a-z][\w-]*)` \|', skill)
    bad += [f'skills/agent/SKILL.md table row `{n}` has no agents/{n}.md' for n in rows if n not in stems]
    bad += [f'skills/agent/SKILL.md table row `{n}` has no Codex entry in models.json' for n in rows if n in stems and n not in codex_keys]
    if 'block-role-spawn.sh' not in skill: bad.append('skills/agent/SKILL.md does not name block-role-spawn.sh')
    return bad
_ak = _rd(root/'skills/agent/SKILL.md')
_as = {p.stem for p in (root/'agents').glob('*.md')}
errors.extend(agent_cmd_bad(_ak, _as, set(mc)))
if not agent_cmd_bad(_ak.replace('`archaeologist`', 'archaeologist'), _as, set(mc)): errors.append('check.py: agent command negative control not flagged for a removed stem')
if not agent_cmd_bad(_ak + '\n| `ghost` | x | x |\n', _as, set(mc)): errors.append('check.py: agent command negative control not flagged for a row with no agent file')
if not agent_cmd_bad(_ak, _as, set(mc) - {'scout'}): errors.append('check.py: agent command negative control not flagged for a row with no Codex entry')
# Solo lane skips (docstring item 26): the lane script itself writes the skipped planner and filer for lane solo.
SOLO_SKIPS_PHRASES = (('scripts/steps.py', 'solo_skips_text'), ('scripts/steps.py', 'write_solo_skips(task)'),
                      ('scripts/fanout.py', 'steps.write_solo_skips'), ('agents/conductor.md', 'tickets.py close --reason'))
def solo_skips_missing(text, phrase): return phrase not in text
for rel, phrase in SOLO_SKIPS_PHRASES:
    sst = _rd(root/rel)
    if solo_skips_missing(sst, phrase): errors.append(f'{rel}: solo lane skips missing "{phrase}"')
    elif not solo_skips_missing(sst.replace(phrase, ''), phrase):
        errors.append(f'check.py: solo lane skips negative control not flagged for "{phrase}"')
# Solo cost capture (docstring item 27): solo_run.py records the solo session's cost; solo.md names it as the start path.
SOLO_RUN_PHRASES = ('sdlc-lite:solo', 'SDLC_ROLE', 'cost_usd', 'cost_reason', 'total_cost_usd')
def solo_cost_bad(run_py, solo, fan):
    bad = [f'solo_run.py missing "{ph}"' for ph in SOLO_RUN_PHRASES if ph not in run_py]
    if 'solo_run.py' not in solo: bad.append('agents/solo.md does not name solo_run.py as the start path')
    mine = re.findall(r"'([SML])': \('(\w+)', '(\w+)', '(L\d)'\)", run_py)
    if sorted(t[0] for t in mine) != ['L', 'M', 'S']: bad.append('solo_run.py TIERS does not list S, M, and L')
    for tier, model, effort, level in mine:
        if not re.search(rf'^\| {tier} \| {tier} \| {model.capitalize()} {effort} \|', solo, re.M): bad.append(f'solo_run.py TIERS {tier} {model} {effort} is not the tier {tier} row of agents/solo.md')
    if sorted(mine) != sorted(re.findall(r"'([SML])': \('(\w+)', '(\w+)', '(L\d)'\)", fan)): bad.append('solo_run.py TIERS differ from fanout.py SOLO_TIERS')
    return bad
_sr = _rd(root/'scripts/solo_run.py')
errors.extend(solo_cost_bad(_sr, _fs, _ff))
for _mut in (lambda t: t.replace("'M': ('sonnet', 'xhigh', 'L2')", "'M': ('sonnet', 'low', 'L2')"), lambda t: t.replace('cost_reason', 'cost_why')):
    if not solo_cost_bad(_mut(_sr), _fs, _ff): errors.append('check.py: solo cost capture negative control not flagged for a changed solo_run.py')
if not solo_cost_bad(_sr, _fs.replace('solo_run.py', 'the wrapper'), _ff): errors.append('check.py: solo cost capture negative control not flagged for solo.md')
# Solo budget gate (docstring item 28): solo_run.py stops at 80 percent with no ack, fanout names the outcome, the docs say so.
_sa, _fk2 = _rd(root/'skills/agent/SKILL.md'), _fk
SOLO_GATE_NEEDS = (('solo_run.py', ('budget_hold', 'budget.py ack', '--new-task', 'return 4')), ('fanout.py', ('budget gate: budget.py ack',)),
                   ('solo.md', ('budget.py ack', '--new-task')), ('agent SKILL.md', ('--new-task', 'budget.py ack')), ('fanout SKILL.md', ('budget gate', 'budget.py ack')))
def solo_gate_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in SOLO_GATE_NEEDS for ph in phrases if ph not in texts[name]]
_gate_texts = {'solo_run.py': _sr, 'fanout.py': _ff, 'solo.md': _fs, 'agent SKILL.md': _sa, 'fanout SKILL.md': _fk2}
errors.extend(f'check.py: solo budget gate: {m}' for m in solo_gate_bad(_gate_texts))
for _name, _phrases in SOLO_GATE_NEEDS:
    for _ph in _phrases:
        if not solo_gate_bad(dict(_gate_texts, **{_name: _gate_texts[_name].replace(_ph, '')})): errors.append(f'check.py: solo budget gate negative control not flagged for {_name} without "{_ph}"')
# Ask skill (docstring item 29): self-contained sweep, reasoned options, one round, a prose path, routed from the entry skill and the conductor.
_ask, _entry, _cond = _rd(root/'skills/ask/SKILL.md'), _rd(root/'skills/sdlc-lite/SKILL.md'), _rd(root/'agents/conductor.md')
ASK_NEEDS = ('## 1. Sweep', '## 2. Reason the options', '## 3. Ask once', '## 4. Take prose', 'Write it in chat', 'Nothing open.', 'AskUserQuestion', "grep -rl '^status: blocked'", '## Verdict', 'If AskUserQuestion is unavailable')
def ask_bad(ask, entry, cond):
    out = [f'ask SKILL.md missing "{ph}"' for ph in ASK_NEEDS if ph not in ask]
    if re.search(r'harness:', ask): out.append('ask SKILL.md references harness:')
    if '/ ask |' not in entry: out.append('skills/sdlc-lite/SKILL.md does not route to ask')
    if '/sdlc-lite:ask' not in cond: out.append('agents/conductor.md does not route to /sdlc-lite:ask')
    return out
errors.extend(f'check.py: ask skill: {m}' for m in ask_bad(_ask, _entry, _cond))
for _ph in ASK_NEEDS:
    if not ask_bad(_ask.replace(_ph, ''), _entry, _cond): errors.append(f'check.py: ask skill negative control not flagged for "{_ph}"')
if not ask_bad(_ask + ' see harness:find-open-questions', _entry, _cond): errors.append('check.py: ask skill negative control not flagged for a harness reference')
if not ask_bad(_ask, _entry.replace('/ ask |', '|'), _cond): errors.append('check.py: ask skill negative control not flagged for a missing entry route')
if not ask_bad(_ask, _entry, _cond.replace('/sdlc-lite:ask', '')): errors.append('check.py: ask skill negative control not flagged for a missing conductor route')
# Document inventory (docstring item 30): the read-only inventory script, its selftest wiring, and the plan procedure.
INVENTORY_NEEDS = (('inventory.py', ('orphan', 'stale', 'duplicate', 'oversized', 'misplaced', 'broken_links', '--include-sdlc', '--out', 'refusing to write inside the repository')),
                   ('check.sh', ('inventory.py" selftest',)), ('procedure', ('inventory.py',)))
def inventory_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in INVENTORY_NEEDS for ph in phrases if ph not in texts[name]]
_inv_texts = {'inventory.py': _rd(root/'scripts/inventory.py'), 'check.sh': _rd(root/'scripts/check.sh'),
              'procedure': _rd(root/'../../docs/planning/repo-onboarding/reorganization-plan-procedure.md')}
errors.extend(f'check.py: document inventory: {m}' for m in inventory_bad(_inv_texts))
for _name, _phrases in INVENTORY_NEEDS:
    for _ph in _phrases:
        if not inventory_bad(dict(_inv_texts, **{_name: _inv_texts[_name].replace(_ph, '')})): errors.append(f'check.py: document inventory negative control not flagged for {_name} without {_ph}')
# Plan skills (docstring item 31): three self-contained planning skills that return a validated paste-ready block, each routed from the entry skill.
PLAN_NEEDS = ('## 1. Gather', 'plan_check.py', 'AskUserQuestion', 'Why this plan', 'You must authorize', 'Unattended', 'Codex host')
def plan_bad(texts, entry):
    out = []
    for name, body in texts.items():
        out += [f'{name} SKILL.md missing "{ph}"' for ph in PLAN_NEEDS if ph not in body]
        if re.search(r'harness:', body): out.append(f'{name} SKILL.md references harness:')
        if f'plan-{name}' not in entry: out.append(f'skills/sdlc-lite/SKILL.md does not route to plan-{name}')
    return out
_plans = {n: _rd(root/f'skills/plan-{n}/SKILL.md') for n in ('goal', 'loop', 'fanout')}
errors.extend(f'check.py: plan skills: {m}' for m in plan_bad(_plans, _entry))
for _n in _plans:
    for _ph in PLAN_NEEDS:
        if not plan_bad(dict(_plans, **{_n: _plans[_n].replace(_ph, '')}), _entry): errors.append(f'check.py: plan skills negative control not flagged for {_n} without "{_ph}"')
    if not plan_bad(dict(_plans, **{_n: _plans[_n] + ' harness:x'}), _entry): errors.append(f'check.py: plan skills negative control not flagged for a harness reference in {_n}')
    if not plan_bad(_plans, _entry.replace(f'plan-{_n}', 'x')): errors.append(f'check.py: plan skills negative control not flagged for a missing entry route to {_n}')
# Broken-link baseline (docstring item 32): runs only where the repository root is a git work tree (not in a consumer install).
def links_bad(broken, allowed):
    got, want = set(broken), set(allowed)
    return [f'unlisted broken link {f} -> {t}' for f, t in sorted(got - want)] + [f'stale allowlist row {f} -> {t}' for f, t in sorted(want - got)]
_repo = (root/'../..').resolve()
if (_repo/'.git').exists() and (_repo/'docs/reports/broken-links-allowlist.md').is_file():
    sys.path.insert(0, str(root/'scripts'))
    import rename_refs as _R
    _broken = [tuple(b) for b in _R.link_report(str(_repo))[1]]
    _allowed = [tuple(c.strip('` ') for c in ln.split('|')[1:3]) for ln in (_repo/'docs/reports/broken-links-allowlist.md').read_text().splitlines() if ln.startswith('| `')]
    errors.extend(f'check.py: broken links: {m}' for m in links_bad(_broken, _allowed))
    if not links_bad(_broken + [('x.md', 'nope.md')], _allowed): errors.append('check.py: broken links negative control not flagged for an extra broken link')
    if not links_bad(_broken, _allowed + [('x.md', 'nope.md')]): errors.append('check.py: broken links negative control not flagged for a stale allowlist row')
# Docs check (docstring item 33): the docs schema checker, its rule ids, and its selftest wiring.
DOCS_CHECK_NEEDS = (('docs_check.py', tuple(f'D-{i}' for i in range(1, 13)) + ('B-1a', 'B-2a', 'B-3a', '--root', '--only', 'Legacy')),
                    ('check.sh', ('docs_check.py" selftest', 'docs_check.py" --root')))
def docs_check_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in DOCS_CHECK_NEEDS for ph in phrases if ph not in texts[name]]
_dc_texts = {'docs_check.py': _rd(root/'scripts/docs_check.py'), 'check.sh': _rd(root/'scripts/check.sh')}
errors.extend(f'check.py: docs check: {m}' for m in docs_check_bad(_dc_texts))
for _name, _phrases in DOCS_CHECK_NEEDS:
    for _ph in _phrases:
        if not docs_check_bad(dict(_dc_texts, **{_name: _dc_texts[_name].replace(_ph, '')})): errors.append(f'check.py: docs check negative control not flagged for {_name} without {_ph}')
# Product name guard (docstring item 34): runs only where the repository root is a git work tree.
NAME_BANNED = ('Lean ' + 'SDLC', 'lean ' + 'SDLC', 'SDLC' + '-Lite', 'sdlc ' + 'lite')
NAME_ALLOW = ('docs/reports/*', '.sdlc/.[0-9]*', '.sdlc/verify-*', '.sdlc/*0309*', 'plugins/sdlc-lite/bench/results/*')
def name_bad(texts):
    import fnmatch
    return [f'{rel}: retired spelling "{b}"' for rel, t in sorted(texts.items()) if not any(fnmatch.fnmatchcase(rel, g) for g in NAME_ALLOW) for b in NAME_BANNED if b in t]
if (_repo/'.git').exists():
    _names = {}
    for _rel in subprocess.run(['git', 'ls-files', '-z'], cwd=_repo, capture_output=True, text=True).stdout.split('\0'):
        if _rel and (_repo/_rel).is_file():
            try: _names[_rel] = (_repo/_rel).read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError): pass
    errors.extend(f'check.py: product name: {m}' for m in name_bad(_names))
    if not name_bad(dict(_names, **{'docs/x.md': 'a ' + NAME_BANNED[0] + ' b'})): errors.append('check.py: product name negative control not flagged for a planted spelling')
    if name_bad({'docs/reports/x.md': 'a ' + NAME_BANNED[1] + ' b'}): errors.append('check.py: product name allowlist did not suppress a docs/reports path')
# Gate lock (docstring item 35): the semaphore script, its selftest wiring, the fanout wrapper, and the conductor and internals mentions.
GATE_LOCK_NEEDS = (('gate_lock.py', ('SLOT-CAP', 'SDLC_GATE_WORKERS', 'SDLC_GATE_SLOTS', 'sdlc-gate-locks')),
                   ('check.sh', ('gate_lock.py" selftest',)), ('fanout.py', ('gate_lock.py', '--no-gate-lock')),
                   ('conductor', ('gate_lock.py run',)), ('internals', ('gate_lock.py',)))
def gate_lock_bad(texts):
    return [f'{name} missing "{ph}"' for name, phrases in GATE_LOCK_NEEDS for ph in phrases if name in texts and ph not in texts[name]]
_gl_texts = {'gate_lock.py': _rd(root/'scripts/gate_lock.py'), 'check.sh': _rd(root/'scripts/check.sh'), 'fanout.py': _rd(root/'scripts/fanout.py'),
             'conductor': _rd(root/'agents/conductor.md')}
if (root/'../../docs/references/sdlc-internals.md').is_file(): _gl_texts['internals'] = _rd(root/'../../docs/references/sdlc-internals.md')
errors.extend(f'check.py: gate lock: {m}' for m in gate_lock_bad(_gl_texts))
for _name, _phrases in GATE_LOCK_NEEDS:
    for _ph in _phrases:
        if _name in _gl_texts and not gate_lock_bad(dict(_gl_texts, **{_name: _gl_texts[_name].replace(_ph, '')})): errors.append(f'check.py: gate lock negative control not flagged for {_name} without {_ph}')
# Fleet retro (docstring item 36): the skill, its rubric and fixtures, and the routes to it.
FLEET_NEEDS = (('skill', ('fleet_collect.py', 'fleet_detect.py', 'SendMessage', 'interview.md', 'rubric.md', 'AskUserQuestion', 'review-traces', 'Codex host',
                          'SDLC_HEADLESS', '## 1. Collect', '## 2. Detect', '## 3. Interview', '## 4. Report', '## 5. Verify', '## 6. File')),
               ('rubric', tuple(f'G{i}' for i in range(1, 6)) + tuple(f'C{i}' for i in range(1, 6)) + ('7 of 10', 'Outcome check')),
               ('fixtures', ('F1', 'F2', 'F3')), ('entry', ('fleet-retro',)), ('conductor', ('fleet-retro',)), ('internals', ('fleet-retro',)))
def fleet_bad(texts):
    out = [f'{name} missing "{ph}"' for name, phrases in FLEET_NEEDS for ph in phrases if name in texts and ph not in texts[name]]
    if 'harness:' in texts['skill']: out.append('skill references harness:')
    return out
_fl_texts = {'skill': _rd(root/'skills/fleet-retro/SKILL.md'), 'rubric': _rd(root/'skills/fleet-retro/rubric.md'), 'fixtures': _rd(root/'skills/fleet-retro/fixtures.md'),
             'entry': _entry, 'conductor': _rd(root/'agents/conductor.md')}
if (root/'../../docs/references/sdlc-internals.md').is_file(): _fl_texts['internals'] = _rd(root/'../../docs/references/sdlc-internals.md')
errors.extend(f'check.py: fleet retro: {m}' for m in fleet_bad(_fl_texts))
for _name, _phrases in FLEET_NEEDS:
    for _ph in _phrases:
        if _name in _fl_texts and not fleet_bad(dict(_fl_texts, **{_name: _fl_texts[_name].replace(_ph, '')})): errors.append(f'check.py: fleet retro negative control not flagged for {_name} without {_ph}')
if not fleet_bad(dict(_fl_texts, skill=_fl_texts['skill'] + ' harness:x')): errors.append('check.py: fleet retro negative control not flagged for a harness reference')
# Fleet status (docstring item 37): the skill prints the renderer's output and asks once; the renderer refuses a row with no source.
FLEET_STATUS_NEEDS = (('skill', ('fleet_status.py render', '## 1. Render', '## 2. Print it', '## 3. Ask once', '## 4. Relay, do not act', 'Render, never compose',
                                 'AskUserQuestion', 'If AskUserQuestion is unavailable', '--ping', 'sends nothing', 'Codex host',
                                 'resources/fleet-status.schema.json')),
                      ('script', ('RenderError', 'def render(', 'def schema_errors', 'def selftest_render')), ('check.sh', ('fleet_status.py" selftest',)))
FLEET_SCHEMA_KEYS = ('machine', 'repos', 'needs_you', 'delta')
def fleet_schema_bad(text):
    if not text.strip(): return ['skills/fleet-status/resources/fleet-status.schema.json is missing or empty']
    try: doc = json.loads(text)
    except ValueError as e: return [f'fleet-status.schema.json does not parse as JSON: {e}']
    if not isinstance(doc, dict): return ['fleet-status.schema.json is not a JSON object']
    out = [] if doc.get('$schema') == 'https://json-schema.org/draft/2020-12/schema' else ['fleet-status.schema.json does not declare draft 2020-12']
    return out + [f'fleet-status.schema.json does not require "{k}"' for k in FLEET_SCHEMA_KEYS if k not in (doc.get('required') or [])]
def fleet_status_bad(texts, entry):
    out = [f'{name} missing "{ph}"' for name, phrases in FLEET_STATUS_NEEDS for ph in phrases if ph not in texts[name]]
    out += fleet_schema_bad(texts['schema'])
    if re.search(r'harness:', texts['skill']): out.append('fleet-status SKILL.md references harness:')
    if '| fleet-status |' not in entry: out.append('skills/sdlc-lite/SKILL.md does not route to fleet-status')
    return out
_fs_texts = {'skill': _rd(root/'skills/fleet-status/SKILL.md'), 'script': _rd(root/'scripts/fleet_status.py'), 'check.sh': _rd(root/'scripts/check.sh'),
             'schema': _rd(root/'skills/fleet-status/resources/fleet-status.schema.json')}
errors.extend(f'check.py: fleet status: {m}' for m in fleet_status_bad(_fs_texts, _entry))
for _name, _phrases in FLEET_STATUS_NEEDS:
    for _ph in _phrases:
        if not fleet_status_bad(dict(_fs_texts, **{_name: _fs_texts[_name].replace(_ph, '')}), _entry): errors.append(f'check.py: fleet status negative control not flagged for {_name} without "{_ph}"')
if not fleet_status_bad(dict(_fs_texts, skill=_fs_texts['skill'] + ' harness:x'), _entry): errors.append('check.py: fleet status negative control not flagged for a harness reference')
if not fleet_status_bad(_fs_texts, _entry.replace('| fleet-status |', '|')): errors.append('check.py: fleet status negative control not flagged for a missing entry route')
for _why, _bad in (('a missing schema file', ''), ('an unparsable schema file', _fs_texts['schema'][:-20]), ('a schema file that is not an object', '[]'),
                   ('a schema file with the wrong draft', _fs_texts['schema'].replace('2020-12', '2019-09')),
                   ('a schema file that does not require repos', _fs_texts['schema'].replace('"repos", ', '', 1))):
    if not fleet_status_bad(dict(_fs_texts, schema=_bad), _entry): errors.append(f'check.py: fleet status negative control not flagged for {_why}')
for e in errors: print('FAIL', e)
print(f'{"FAIL" if errors else "ok"}: {len(run)} role levels, {len(agents)} agents checked')
sys.exit(1 if errors else 0)
