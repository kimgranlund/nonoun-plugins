## Task goal
A role or person writing any document type in this repo or a consumer repo finds one registry row, one short card, and a template or schema, and the checkable parts are checked by a script.

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
