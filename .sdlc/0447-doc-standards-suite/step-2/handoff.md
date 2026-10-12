## Task goal
A role or person writing any document type in this repo or a consumer repo finds one registry row, one short card, and a template or schema, and the checkable parts are checked by a script.

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
