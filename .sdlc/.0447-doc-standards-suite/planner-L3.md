<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Build the document standards suite (registry, core rules, seven family cards, glossary, schemas, templates) with docs_check rules S-1 to S-7 and a new prompt_lint.py (rules P-1 to P-6), each rule backed by an observed-red selftest control, then add the reach pointers and leave every gate green.

## Step 1: prompt_lint.py, its check.py and check.sh wiring, and the broken references it finds
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/prompt_lint.py`. Use the standard library only and write it for this repo, not as a port. The upstream prompt-wording-rules skill (github.com/kimgranlund/claude-plugins, harness/skills/prompt-wording-rules, commit 5f9819b86b4dc77934fd36226025cec2e2a88d81, copies in `.sdlc/0447-doc-standards-suite/upstream/`) is prior art to read. Vendor none of it, and name it in the module docstring. Follow the shape of `docs_check.py`: its `<level> <rule> <path>: <message>` finding line, and its `selftest()` with a positive case and `drops <rule>` negative variants per gate (docs_check.py:657-699).
- CLI: `prompt_lint.py [FILE ...]` and `prompt_lint.py selftest`. With no FILE, lint the plugin's `agents/*.md`, `skills/*/SKILL.md`, and `overlays/*.md`; the plugin root is the parent of the script's folder. Print one line per finding as `<error|warning|info> <rule> <path>: <message>`, with the path as given on the command line (defaults relative to the current directory), then one summary line. Exit 1 on any error, 0 otherwise, and 2 on a usage error.
- P-1, error, agents and overlays only: each cite matching `\brules? (\d+)((?:, \d+)*(?:,? (?:and|or|to) \d+)?)` names numbers that are top-level numbered lines (`^N\. `, outside fenced blocks) of the role body. The role body of `overlays/<role>.md` and of a generated `agents/<role>-L<n>.md` is `agents/<role>.md`. Any other agent file is its own role body.
- P-2, error, all covered files: inside inline code spans and fenced code lines, take each `<name>.py` token whose basename is a plugin script (`scripts/*.py` or `skills/*/scripts/*.py`). When the next token is a subcommand (`[a-z][a-z0-9-]*`), that subcommand appears in the script's module docstring or as a quoted string literal in its source. Each `--flag` after it in the same command (up to `|`, `;`, `&&`, `>`) appears in the docstring or as a quoted literal. Skip a basename that is not a plugin script.
- P-3, error, all covered files: each `${CLAUDE_PLUGIN_ROOT}/<path>` with no `<`, `*`, or `$` in the path exists under the plugin root. Resolve each bare `scripts/<name>.py`, `scripts/<name>.sh`, or `skills/<skill>/scripts/<name>` path against the file's own skill folder first (skill files only), then against the plugin root. An unresolved bare path is an error when a file with that basename exists elsewhere in the plugin. Skip it when the basename exists nowhere, as for the quoted example `scripts/util.sh` in skills/checking-rules/SKILL.md:74.
- P-4, warning: in `overlays/<role>.md`, the `## L<n>` section for the role's smallest level key in `adapters/claude/levels.json` (a dict of role to level to [model, effort]) holds a `### Gap defaults` heading. The section for its largest level key holds `### Goal`, `### KPI`, and `### Budget`. Skip absent sections and roles with one level. overlays/builder.md already meets this rule.
- P-5, warning: covers each role body `agents/<name>.md` with no `-L<n>` suffix, for the roles in `results.SCHEMA` plus `solo` and `conductor`; skip `messenger`. Each such body has a line matching `(?i)\bclosed (step|ticket)\b`. For a role whose `results.SCHEMA[role]['allowed']` is not empty, each ` | `-separated value on the first non-blank line under the body's `## <results.key(role)>` heading is one of that role's allowed display strings. Read the statuses through `import results`, because results.py is their only copy (plugins/sdlc-lite/AGENTS.md); keep no status list in prompt_lint.
- P-6, info, every file: print one line, `info P-6 <path>: prohibitions <n>, NEVER <n>, vague <n>`. Prohibitions are case-insensitive whole-word `never`, `do not`, `don't`, `must not`, and `cannot`. NEVER is case-sensitive `\bNEVER\b`. Vague are case-insensitive whole-word `a few`, `several`, `some`, `many`, `various`, `appropriate`, `appropriately`, `reasonable`, `reasonably`, `as needed`, `if needed`, and `etc`. The counts never change the exit code; the baseline is docs/reports/2026-10-11-agent-prompt-lint-baseline.md.
- Severity tiers, settled: P-1 to P-3 are the resolution errors the handoff names. P-4 and P-5 are warnings, because eight role bodies lack the predicate and this build rewrites no role file; only builder, conductor, and solo have one (`grep -n -i "closed step\|closed ticket" plugins/sdlc-lite/agents/*.md`). P-6 is info.
- `selftest`: for each rule, build a temp plugin fixture with agents/, skills/x/SKILL.md, overlays/, a scripts/ fake script with a usage docstring, and adapters/claude/levels.json. The clean fixture reports no error and no warning. A planted defect is reported under exactly that rule, and a variant that drops the rule must be rejected. Print `gate P-<n>: positive ok, negative ok` per rule, then `prompt_lint selftest: PASS` or `FAIL`, and exit 1 on FAIL. Add one case proving that a P-5 warning and P-6 counts leave the exit at 0.

Wiring:
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/prompt_lint.py" selftest || fail=1` beside the docs_check.py selftest line, and name prompt_lint.py in the header comment.
- `plugins/sdlc-lite/scripts/check.py`: add docstring item 53 "Prompt references (T-0447)" and code after item 52, in the pattern of check.py:1274-1284. The code does `import prompt_lint` (check.py:549 already puts scripts/ on sys.path) and fails on any P-1 to P-3 error over the covered files. It checks that check.sh holds `prompt_lint.py" selftest`. It runs three negative controls on planted texts: an unresolved `rule 99` cite in an overlay, an unknown `--flag` on a real script, and a bare `scripts/coverage_check.py` in an agent file. P-4 to P-6 never fail check.py.
- `plugins/sdlc-lite/AGENTS.md`: add one line under Verification naming `python3 plugins/sdlc-lite/scripts/prompt_lint.py` and its `selftest`.

Broken references: run the lint. The plan-time prototype found no P-1 cite and no P-2 subcommand or flag out of 1013 that fails to resolve. Under the rule above, P-3 finds `scripts/coverage_check.py` in agents/architect.md:15 and skills/architect/SKILL.md:15 (the script lives at skills/decompose/scripts/coverage_check.py). Replace each with `${CLAUDE_PLUGIN_ROOT}/skills/decompose/scripts/coverage_check.py`. That keeps `Markdown-only design` and `coverage_check.py`, which check.py:752-757 pins. Then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`, which rewrite agents/architect-L1.md and adapters/codex/agents/sdlc-architect-l1.toml; never edit those by hand. A finding on a reference that does exist is a lint defect: fix the lint, not the file. Fix any other real broken reference the same way, changing only the reference. Rewrite nothing to meet a count. Write no em or en dash in any line you add or edit.

Depends on: none. Validation scope: `prompt_lint.py selftest`, the lint over the covered files, both `generate --check`, and `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` (item 53 and the check.py:752 pin). The full check.sh runs in step 4.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py selftest) && for n in 1 2 3 4 5 6; do printf '%s\n' "$out" | grep -qF "gate P-$n: positive ok, negative ok" || exit 1; done` exits 0: the selftest has an observed-red negative control for each rule.
- (red) `python3 plugins/sdlc-lite/scripts/prompt_lint.py plugins/sdlc-lite/agents/*.md plugins/sdlc-lite/skills/*/SKILL.md plugins/sdlc-lite/overlays/*.md` exits 0.
- (red) `out=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py plugins/sdlc-lite/agents/planner.md) && printf '%s\n' "$out" | grep -qE '^warning P-5 plugins/sdlc-lite/agents/planner\.md: ' && printf '%s\n' "$out" | grep -qE '^info P-6 plugins/sdlc-lite/agents/planner\.md: '` exits 0: the advisory tiers report and do not fail.
- (red) `grep -qF 'prompt_lint.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (red) `python3 -c "import re; t=open('plugins/sdlc-lite/scripts/check.py').read(); assert re.search(r'(?m)^53\. .*prompt_lint', t), 'no item 53'; assert 'import prompt_lint' in t, 'no import'"`
- (red) `for f in plugins/sdlc-lite/agents/architect.md plugins/sdlc-lite/skills/architect/SKILL.md; do grep -qF 'skills/decompose/scripts/coverage_check.py' "$f" || exit 1; done`
- (red) `grep -qF 'prompt_lint.py' plugins/sdlc-lite/AGENTS.md`
- (red) `python3 -c "import sys, pathlib; args=[pathlib.Path(a) for a in sys.argv[1:]]; assert all(a.exists() for a in args), 'missing'; bad=[str(q) for q in args if any(ch in q.read_text(encoding='utf-8') for ch in (chr(0x2013), chr(0x2014))) or any(l != l.rstrip() for l in q.read_text(encoding='utf-8').splitlines())]; assert not bad, bad" plugins/sdlc-lite/scripts/prompt_lint.py` exits 0: the new file exists and has no em or en dash and no trailing whitespace.
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(prompt_lint|check)\.py|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/AGENTS\.md|plugins/sdlc-lite/agents/[^/]+\.md|plugins/sdlc-lite/skills/[^/]+/SKILL\.md|plugins/sdlc-lite/overlays/[^/]+\.md|plugins/sdlc-lite/adapters/codex/agents/[^/]+\.toml')"`

## Step 2: docs_check standards rules S-1 to S-7
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
In `plugins/sdlc-lite/scripts/docs_check.py`, add rules S-1 to S-7, all at `error` level. `--only` selects them by id or by the new group `standards` (S-*); update `on()` (docs_check.py:192), the `--only` help text, and the docstring, which names `docs/specs/doc-standards/README.md` as the rules' home. Give each rule a case in `_cases()`, so `selftest` builds its `drops S-<n>` negative control (docs_check.py:676). None may fire on the `_clean` fixture. The S-1 case writes a schema into its fixture, and the S-7 case writes a registry into its fixture.
- S-1: each kpi-kind `NNN-*.md` file has, in its front matter, every key listed in `required` of `docs/assets/schemas/kpi.json`. The rule is silent when that file is absent, as in a consumer repo or on this tree before step 3.
- S-2: in a docs Markdown file with front matter `doc-type: requirements`, each line outside fences that contains the word `shall` starts with a stable ID `[A-Z][A-Z0-9]*-\d+` and a colon (an optional `- ` may come first). Before the next ID line or heading, each ID line is followed by a line whose stripped text starts with `Acceptance:`.
- S-3: flags a decisions-kind file (not an entry file) with more than one line equal to `## Decision`.
- S-4: flags a docs Markdown file with `doc-type: runbook` that has no `^\d+\. ` line outside fences.
- S-5: in a docs Markdown file with `doc-type: policy`, flags each line with a whole-word must, shall, should, or may in any case other than all upper case, outside front matter, fences, and inline code. One finding per line.
- S-6: in a reports-kind file with `doc-type: report`, flags a relative Markdown link outside fences that does not resolve. It also flags a whole code span that is a relative path (it holds `/`, ends in `.<ext>`, and has no space, `<`, `*`, `$`, or `:`) and resolves neither from the repository root nor from the report's folder.
- S-7: when `docs/specs/doc-standards/README.md` exists, each `.md` file directly in that folder, other than README.md, AGENTS.md, and CLAUDE.md, is a link target in it. Each of its links to a sibling card or into `assets/` resolves. Each row of the registry table (the table whose first header cell is `Type`, with header `| Type | Home | Standard | Card | Template or schema | Check | Enforcement |`) has Enforcement `enforced` or `advisory`, and a row whose Check is `-` is `advisory`. The rule is silent when the registry is absent.

These paths, the header, and the `doc-type:` values (`requirements`, `runbook`, `policy`, `report`) are the contract that step 3 writes against. The opt-in `doc-type:` keeps the rules off every existing document, since rewriting existing docs is a non-goal, and off consumer repos that never set the key. S-3 flags only a second `## Decision`, so an ADR in another format is not an error. Keep every phrase that check.py pins through `DOCS_CHECK_NEEDS` in docs_check.py. Write no em or en dash in any line you add.

Depends on: none. Validation scope: `docs_check.py selftest`, `docs_check.py --root .` (green, because every S rule is silent or opt-in on this tree), and `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` for the `DOCS_CHECK_NEEDS` pins. The full check.sh runs in step 4.
### Acceptance criteria
- (red) `python3 -B -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import docs_check; ids={c[0] for c in docs_check._cases()}; miss=[r for r in ('S-1', 'S-2', 'S-3', 'S-4', 'S-5', 'S-6', 'S-7') if r not in ids]; assert not miss, miss"` exits 0: each S rule has a selftest case, so the selftest builds its `drops` negative control.
- (red) `python3 -B -c "import sys, tempfile, os; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import docs_check; t=tempfile.TemporaryDirectory(); d=t.name; os.makedirs(d + '/docs/guides'); open(d + '/docs/guides/p.md', 'w').write('---\ndoc-type: policy\n---\n# P\n\nYou must log in.\n'); f=docs_check.run(d, only={'standards'}); assert [x.rule for x in f if x.level == 'error'] == ['S-5'], [x.line() for x in f]"` exits 0: the `standards` group runs, and a policy with a lowercase `must` gets exactly one S-5 error.
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(prompt_lint|check|docs_check)\.py|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/AGENTS\.md|plugins/sdlc-lite/agents/[^/]+\.md|plugins/sdlc-lite/skills/[^/]+/SKILL\.md|plugins/sdlc-lite/overlays/[^/]+\.md|plugins/sdlc-lite/adapters/codex/agents/[^/]+\.toml')"`

## Step 3: Standards documents: registry, core, seven cards, glossary, schemas, templates
level: L3
### Read first
- `docs/AGENTS.md`
- `docs/specs/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Write these from `docs/planning/doc-standards/source-list.md`, the dated source, which stays as it is. Avoid the product-name spellings that check.py item 34 bans (`NAME_BANNED`). Write no em or en dash.
- `docs/specs/doc-standards/README.md`, the registry, is one table with the header `| Type | Home | Standard | Card | Template or schema | Check | Enforcement |`. S-7 from step 2 checks it.
  - Rows: one per source-list bullet, whose Type cell is the bullet label verbatim (the text before its first colon: 30 labels, `Goals` to `Release / milestone`). Add the rows `Agent file`, `Skill`, `Overlay`, `Handoff`, and `Tool description` for prompts.md.
  - Card and Template or schema cells are Markdown links, such as `[intent.md](intent.md)` and `[bug.tmpl](../../assets/templates/bug.tmpl)`, or `-` when there is none.
  - Check cells name rule ids (`docs_check S-1`, `prompt_lint P-1`, and the existing `docs_check G-1` to `G-5` on the Goals and KPI rows) or `-`.
  - Enforcement is `enforced` when a check.sh gate fails on the rule: docs_check S-* and G-* errors through check.sh's repository gate, and prompt_lint P-1 to P-3 through check.py item 53. It is `advisory` otherwise: P-4 to P-6, and every row whose Check is `-`. Take the tiers from the built prompt_lint.py (step 1).
  - Cards per row:
    - intent.md: Goals; KPI / metric definitions; PRD; Spec / requirements (SPEC, SRS); Epic / parent issue.
    - design.md: HLD / architecture; LLD; API docs; Decision records.
    - work-items.md: Agent task / ticket / work order; Bug report; Feature request / enhancement; Task / chore ticket; Spike / investigation; Issue titles; Issue / PR labels; Definition of done / acceptance checklist.
    - delivery.md: Commit messages; PR title and body; PR review comments; Changelog / release notes; Release / milestone.
    - knowledge-ops.md: Runbooks / procedures; Test plans / cases; Report / analysis; Research notes / literature; Postmortem / incident; Policies / guardrails; Glossary / ontology.
    - prompts.md: System prompts / agent instructions, plus the five prompt rows. The prompts amendment is later and more specific, so knowledge-ops.md points to prompts.md for system prompts.
  - Below the table, list every S and P rule id with one line each.
- `core.md` holds the shared rules: Simplified Technical English and Plain Language rules, EARS templates, RFC 2119 meanings, stable IDs (`G-NNN`, `K-NNN`, `T-NNNN`, `REQ-NNN`, decision `NNNN`), the evidence marks `[V]` and `[U]`, and status words. It cites the user-level `doc-writing-rules` as the prose authority and copies none of it. It defines the front matter key `doc-type:` with the four values that step 2's rules read: `requirements`, `runbook`, `policy`, and `report`.
- `intent.md`, `design.md`, `work-items.md`, `delivery.md`, and `knowledge-ops.md` are short cards for the families the handoff lists.
  - work-items.md reconciles and does not copy: it maps this repo's ticket template (`plugins/sdlc-lite/skills/ticket/templates/*.md` front matter: type feature, bug, chore, spike, idea; status proposed, ready, claimed, paused, blocked, done, dropped; size L1 to L4; priority P1 to P3) to the ticket schema.
  - delivery.md says this repo's commits stay plain imperative subjects with the `Co-Authored-By` trailer, and marks Conventional Commits as the consumer-repo standard, not this repo's.
- `prompts.md` states the seven points of the handoff's prompt-standards amendment.
  - It cites the overlay design `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` as a code span, not a link, because B-3a warns on links into `.sdlc/`.
  - It cites the gap-default evidence `docs/reports/2026-10-11-plan-doc-live-run.md`, and close-first as T-0428.
  - Statuses: results.py's key values (done, blocked, `inherited red: <tests>`, pass, fail, replan). `plan defect:` and `stale lane:` are Notes prefixes that steps.py routes. `unverified` is the report word for a check that could not run (root AGENTS.md). results.py defines none of those three: `grep -n "plan defect\|unverified" plugins/sdlc-lite/scripts/results.py` prints nothing.
  - It names the upstream prompt-wording-rules skill as prior art by repository (claude-plugins) and commit, never by the `.sdlc/0447-*` path, which moves when the ticket closes.
  - Point 7: a wording change is judged better only by the replay A/B (cost, first-pass rate, blocked rate).
  - Each P rule that enforces a point names its id.
- `docs/references/glossary.md` is a table `| Term | Part of speech | Definition | Unapproved aliases |` with one row per term. Seed it with ticket, lane, step, level, handoff, verifier, close-first, and plan doc, each with one definition from this repo's sources.
- `docs/assets/schemas/ticket.json`, `kpi.json`, and `test-case.json` are JSON Schema (draft 2020-12) objects with `required` and `properties`.
  - kpi.json `required` equals `KPI_REQUIRED` (docs_check.py:46), so the four existing docs/kpi files pass S-1. The source list's metric fields (quantity, numerator, denominator, filters, window, source) are optional properties.
  - ticket.json requires id, title, type, status, size, priority, depends, and created. Its enums take this order, from skills/ticket/templates/bug.md: status [proposed, ready, claimed, paused, blocked, done, dropped]; size [L1, L2, L3, L4]; type [feature, bug, chore, spike, idea]; priority [P1, P2, P3].
  - test-case.json requires id, precondition, action, expected, and traces.
- `docs/assets/templates/` holds `bug.tmpl`, `feature-request.tmpl`, `spike.tmpl`, `pr-body.tmpl`, `postmortem.tmpl`, `runbook.tmpl`, and `adr.tmpl`. They end in `.tmpl`, not `.md`: D-9 (docs_check.py:260) errors on any Markdown file in assets/, and the assets row in docs/layout.md says "not: Markdown". The stems stay kebab-case for D-12. Fill each template from the source list. The bug template has environment, numbered reproduction steps, expected, actual, evidence, and severity. The ADR template is the Nygard shape (context, decision, consequences) with one `## Decision`.
- `docs/specs/doc-standards/AGENTS.md` and `CLAUDE.md` are required: D-7 (docs_check.py:320) errors on a specs topic with two or more documents and no entry file, and `ENTRY_THRESHOLD = 2` (onboard.py:530). Write the cards first, because the managed block lists them, then write each entry file from `onboard.plan(root)` as below. Add a one-line purpose above the managed block, as in docs/specs/repo-onboarding/AGENTS.md. Never run `onboard.py setup`: its plan-time dry run added a managed block to the root AGENTS.md, which the handoff forbids.
```python
import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import onboard
want = {'docs/specs/doc-standards/AGENTS.md', 'docs/specs/doc-standards/CLAUDE.md'}
for c in onboard.plan('.'):  # Change(path, row, action, label, old, new, notes), onboard.py:868
    if c.path in want and c.new is not None and c.new != c.old:
        open(c.path, 'w').write(c.new)
```

Depends on: step 1 (the registry records prompt_lint's rule ids and tiers as built) and step 2 (the registry, schemas, and opt-in keys must pass S-1 to S-7). Validation scope: `docs_check.py --root .` (now enforcing S-7 on the real registry and S-1 against the real schema), `docs_check.py --root . --only standards`, and `onboard.py check` for the two new entry files. The full check.sh runs in step 4.
### Acceptance criteria
- (red) `for f in README core intent design work-items delivery knowledge-ops prompts AGENTS CLAUDE; do test -f "docs/specs/doc-standards/$f.md" || exit 1; done`
- (red) `python3 -c "import re; src=open('docs/planning/doc-standards/source-list.md').read(); types=[m.group(1).strip() for m in re.finditer(r'(?m)^- ([^:\n]+):', src)]; reg=open('docs/specs/doc-standards/README.md').read(); cells={l.strip().strip('|').split('|')[0].strip() for l in reg.splitlines() if l.lstrip().startswith('|')}; miss=[t for t in types if t not in cells]; ids=['S-%d' % i for i in range(1, 8)] + ['P-%d' % i for i in range(1, 7)]; assert len(types) >= 25 and not miss, miss; assert all(i in reg for i in ids), [i for i in ids if i not in reg]; assert all(c + '.md' in reg for c in ('core', 'intent', 'design', 'work-items', 'delivery', 'knowledge-ops', 'prompts'))"` exits 0: the registry has a row for every source-list type, names all seven cards and core, and lists every S and P rule.
- (red) `test -f docs/specs/doc-standards/README.md && python3 plugins/sdlc-lite/scripts/docs_check.py --root . --only standards` exits 0: S-1 to S-7 hold on the real registry, schema, and cards.
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (red) `python3 -c "t=open('docs/references/glossary.md').read(); rows=[l.strip().strip('|').split('|')[0].strip().lower() for l in t.splitlines() if l.lstrip().startswith('|')]; miss=[w for w in ('ticket', 'lane', 'step', 'level', 'handoff', 'verifier', 'close-first', 'plan doc') if w not in rows]; assert not miss, miss; assert 'unapproved' in t.lower()"`
- (red) `python3 -B -c "import json, sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import docs_check; L=lambda n: json.load(open('docs/assets/schemas/%s.json' % n)); k, t, c = L('kpi'), L('ticket'), L('test-case'); assert set(k['required']) == set(docs_check.KPI_REQUIRED), k['required']; assert {'id', 'title', 'type', 'status', 'size', 'priority', 'depends', 'created'} <= set(t['required']), t['required']; assert t['properties']['status']['enum'] == ['proposed', 'ready', 'claimed', 'paused', 'blocked', 'done', 'dropped']; assert t['properties']['size']['enum'] == ['L1', 'L2', 'L3', 'L4']; assert t['properties']['type']['enum'] == ['feature', 'bug', 'chore', 'spike', 'idea']; assert t['properties']['priority']['enum'] == ['P1', 'P2', 'P3']; assert {'id', 'precondition', 'action', 'expected', 'traces'} <= set(c['required'])"`
- (red) `for n in bug feature-request spike pr-body postmortem runbook adr; do test -f "docs/assets/templates/$n.tmpl" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/onboard.py check 2>/dev/null); for f in AGENTS CLAUDE; do printf '%s\n' "$out" | grep -qx "current docs/specs/doc-standards/$f.md" || exit 1; done`
- (red) `python3 -c "P='docs/specs/doc-standards/'; need={'prompts.md': ['prompt-wording-rules', 'claude-plugins', '2026-10-11-plan-doc-live-run.md', '.0440-per-tier-agent-prompts/architect-L1.md', 'results.py', 'T-0428', 'replay'], 'delivery.md': ['Conventional Commits', 'Co-Authored-By'], 'core.md': ['EARS', 'RFC 2119', '[V]', '[U]', 'doc-type:', 'doc-writing-rules'], 'work-items.md': ['skills/ticket/templates/', 'claimed', 'paused']}; miss=[(f, p) for f, ps in need.items() for p in ps if p not in open(P + f).read()]; assert not miss, miss"`
- (red) `python3 -c "import sys, pathlib; args=[pathlib.Path(a) for a in sys.argv[1:]]; assert all(a.exists() for a in args), 'missing'; fs=[q for a in args for q in (sorted(x for x in a.rglob('*') if x.is_file()) if a.is_dir() else [a])]; bad=[str(q) for q in fs if any(ch in q.read_text(encoding='utf-8') for ch in (chr(0x2013), chr(0x2014))) or any(l != l.rstrip() for l in q.read_text(encoding='utf-8').splitlines())]; assert not bad, bad" docs/specs/doc-standards docs/references/glossary.md docs/assets` exits 0: every new file exists and has no em or en dash and no trailing whitespace.
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(prompt_lint|check|docs_check)\.py|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/AGENTS\.md|plugins/sdlc-lite/agents/[^/]+\.md|plugins/sdlc-lite/skills/[^/]+/SKILL\.md|plugins/sdlc-lite/overlays/[^/]+\.md|plugins/sdlc-lite/adapters/codex/agents/[^/]+\.toml|docs/specs/doc-standards/[^/]+\.md|docs/references/glossary\.md|docs/assets/templates/[a-z0-9-]+\.tmpl|docs/assets/schemas/[a-z0-9-]+\.json')"`

## Step 4: Reach pointers and gates green
level: L3
guard timeout: 1900
### Read first
- `docs/AGENTS.md`
- `docs/specs/AGENTS.md`
- `docs/references/AGENTS.md`
- `plugins/sdlc-lite/AGENTS.md`
### Do
- `plugins/sdlc-lite/scripts/onboard.py`: add item 5 to `## Adding a document` in `DOCS_AGENTS_TEMPLATE` (onboard.py:401). It names the registry as a code span, not a link, so a consumer repo without the file gets no dangling link: "5. Find the document's type in `specs/doc-standards/README.md`, when this repository has it, and follow the card its row names." Keep `TEMPLATE_VERSION = 1`; docs/reports/onboard-lane-text.md records the precedent of no version bump for a text change. Then write only `docs/AGENTS.md`, `docs/specs/AGENTS.md`, and `docs/references/AGENTS.md` from `onboard.plan(root)`, with the step 3 snippet and those three paths. Never run `onboard.py setup`, which would add a block to the root AGENTS.md. A consumer's block reads `stale` until its next setup; that is the existing contract.
- `docs/README.md`: add one bullet, `[Document standards](specs/doc-standards/README.md)`, with a one-line description.
- Skills: add one Read-first line to each of `plugins/sdlc-lite/skills/plan-goal`, `ticket`, `file`, `fleet-retro`, and `plan-doc` SKILL.md. Make it the first body line after the front matter, after the H1 when there is one.
  - The line names the card as a code span, never a link, because check.py item 42 flags any skill link that starts with `docs/`. The cards: plan-goal and plan-doc cite `docs/specs/doc-standards/intent.md`, ticket cites `docs/specs/doc-standards/work-items.md`, file cites `docs/specs/doc-standards/delivery.md`, and fleet-retro cites `docs/specs/doc-standards/knowledge-ops.md`.
  - Word it as applying when that file exists in the repository, since consumers have none. The line cites the card and restates no rule.
  - Run both `generate --check`; when either reports stale, run its `generate`. Never edit a generated file by hand.
- Write no em or en dash in any line you add or edit.
- Gates: run every criterion below and fix any red that steps 1 to 3 introduced, inside the files they own. A gate already red at this step's build-start HEAD is reported as `inherited red`. check.sh took 615 s in the longest recorded run (.sdlc/plan-reliability-docs/planner-L3.md, step 8) and 226 to 382 s in recent builder and verifier records, hence the guard timeout of 1900.

Depends on: steps 1, 2, and 3.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/onboard.py check 2>/dev/null); for f in docs/AGENTS.md docs/specs/AGENTS.md docs/references/AGENTS.md; do printf '%s\n' "$out" | grep -qx "current $f" || exit 1; done`
- (red) `python3 -c "t=open('docs/AGENTS.md').read(); b=t[t.index('sdlc-lite:managed:start'):t.index('sdlc-lite:managed:end')]; assert 'specs/doc-standards/README.md' in b"`
- (red) `python3 -B -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import onboard; t=onboard.DOCS_AGENTS_TEMPLATE; assert chr(96) + 'specs/doc-standards/README.md' + chr(96) in t; assert '](specs/doc-standards/' not in t"` exits 0: the template names the registry as a code span and never as a link.
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- (red) `grep -qF '](specs/doc-standards/README.md)' docs/README.md`
- (red) `for p in plan-goal:intent ticket:work-items file:delivery fleet-retro:knowledge-ops plan-doc:intent; do grep -qF "docs/specs/doc-standards/${p#*:}.md" "plugins/sdlc-lite/skills/${p%%:*}/SKILL.md" || exit 1; done`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(prompt_lint|check|docs_check|onboard)\.py|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/AGENTS\.md|plugins/sdlc-lite/agents/[^/]+\.md|plugins/sdlc-lite/skills/[^/]+/SKILL\.md|plugins/sdlc-lite/overlays/[^/]+\.md|plugins/sdlc-lite/adapters/codex/agents/[^/]+\.toml|docs/specs/doc-standards/[^/]+\.md|docs/references/glossary\.md|docs/assets/templates/[a-z0-9-]+\.tmpl|docs/assets/schemas/[a-z0-9-]+\.json|docs/AGENTS\.md|docs/README\.md|docs/specs/AGENTS\.md|docs/references/AGENTS\.md')"`

## Assumptions
- results.py defines the key values done, blocked, `inherited red: <tests>`, pass, fail, and replan, but not `plan defect` or `unverified`, although the handoff says it does. Verified: `grep -n "plan defect\|unverified" plugins/sdlc-lite/scripts/results.py` printed nothing; SCHEMA is at results.py:30-50. prompts.md states where each word is defined.
- Templates cannot be `.md` under docs/assets/. Verified at docs_check.py:260 (D-9), docs_check.py:287-300 (D-12 stem rule), and the assets Kinds row in docs/layout.md.
- docs/specs/doc-standards/ needs its own entry files. Verified at docs_check.py:320-337 (D-7) and onboard.py:530 (`ENTRY_THRESHOLD = 2`).
- `onboard.py setup` would add a block to the root AGENTS.md: `setup --dry-run` printed a new managed block for AGENTS.md. At base, `onboard.py check` printed `stale` for docs/AGENTS.md and docs/references/AGENTS.md and `current` for docs/specs/AGENTS.md. `Change` has the fields path, row, action, label, old, new, and notes (onboard.py:868).
- The KPI schema can require exactly `KPI_REQUIRED` without breaking a file: `docs_check.py --root .` exits 0 today with G-2 enforcing that set (docs_check.py:46).
- prompt_lint's expected findings on the current tree, from plan-time prototypes of the settled rules:
  - P-1: no failing cite, including multi-number cites.
  - P-2: none of 1013 code-span subcommand refs fails against a docstring or quoted-literal match.
  - P-3: five hits. Three are real: agents/architect.md, its generated agents/architect-L1.md, and skills/architect/SKILL.md. skills/decompose/SKILL.md:3 resolves inside its own skill folder, and skills/checking-rules/SKILL.md:74 is a quoted example skipped by the basename rule.
  - Fenced code lines were not prototyped.
- Only builder, conductor, and solo hold a `closed step` or `closed ticket` line (grep of the role bodies), so P-5 must stay a warning while role files are frozen.
- `adapters/claude/levels.json` maps role to level to [model, effort]; builder's levels run L1 to L5. Verified with python3 json.load.
- No check.py item requires every script to have a check.sh line or a sdlc-internals section. Items 49 and 50 pin named scripts only (grep of check.py), so prompt_lint.py needs no internals section.
- No role preloads plan-goal, ticket, file, fleet-retro, or plan-doc (grep of agent front matter). Step 4's regeneration is therefore expected to be a no-op; the Do still runs `generate --check`.
- check.sh is green at the base HEAD: unverified at plan time, because the broad suite was not run. Recent builder and verifier records show `rc=0`. Every other guard was dry-run green at the base: both `generate --check`, `docs_check.py selftest`, `docs_check.py --root .`, `onboard.py selftest`, `check-packaging.py`, `git diff --check`, and all four scope guards.
- Each red criterion was run at base and failed for the missing behavior (a missing file, rule, line, or S rule). The dash check, scope guard, and `git diff --check` shapes were each observed red on a planted or dashed input.
- `scripts/__pycache__` is gitignored (`git check-ignore`), so python criteria leave the scope guards green.

## Risks
- Consumer reach is partial. The skills, the managed docs block, and docs/README.md name repo-relative card paths, and the plugin ships no card, so a consumer repo sees the pointer but not the standards unless it copies them. Shipping the cards in the plugin would be a follow-up ticket.
- Every consumer's docs/AGENTS.md block reads `stale` after the template edit, until its next `onboard.py setup`. This is the existing contract, with no version bump.
- P-3 skips a bare path whose basename exists nowhere in the plugin, so a reference to a deleted script passes unless it is written with `${CLAUDE_PLUGIN_ROOT}/`. This is a settled trade-off that keeps quoted examples (skills/checking-rules/SKILL.md:74) from failing.
- P-2 and P-3 over fenced code lines were not prototyped and may surface more references. The Do routes a false positive to a lint fix and a real break to a reference-only edit; a large real set would widen step 1's edits inside its scope allow-list.
- New S-3 errors fire in a consumer repo whose decision file holds two `## Decision` headings. That is intended, but it is a new error for consumers.
- The criteria pin output formats that the Do settles: `gate P-<n>: positive ok, negative ok`, `warning P-5 <path>: `, `info P-6 <path>: `, the registry header, and registry Type cells equal to the source-list labels.
- Step 3 is the heaviest step: about 20 new files against a builder budget of about 60 tool calls. The docs_check rules were split out to step 2 to keep it inside that budget.
- All four steps are L3, so no plan review runs although the ticket is L4. The open readiness concerns above go to the builders as notes.
- A plan-time probe created one scratch git repo under `$TMPDIR` (mktemp), outside the given throwaway dir. It was not deleted, per the no-delete rule.
