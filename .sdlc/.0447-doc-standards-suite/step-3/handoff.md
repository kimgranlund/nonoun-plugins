## Task goal
A role or person writing any document type in this repo or a consumer repo finds one registry row, one short card, and a template or schema, and the checkable parts are checked by a script.

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
