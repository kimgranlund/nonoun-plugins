---
id: T-0791
title: "new design plugin from the user-level design skills"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A new `design` plugin ships the design skills for Claude Code and Codex, so UI work in every repo uses one version.

## Intent
- Do: create `plugins/design/` with `base-ui`, `mathematical-design-system`, `hct-palettes`, `ui-kit-inspector`, `component-variants`, `wireframe-review`, `design-crit` and `make-figma-agent-connector`; decide whether `inspector-panels` merges into `ui-kit-inspector` or ships separately; add an `AGENTS.md` for the plugin.
- Non-goals: changing the skills' design rules; the `wireframe-review` symlink on this Mac (`~/.claude/skills/wireframe-review -> ~/.codex/skills/wireframe-review`) is the user's to remove after install.
- Done when: `python3 scripts/check-packaging.py` passes, `node scripts/check-kit.mjs` passes inside `base-ui`, `node scripts/check-geometry.mjs` and `node scripts/check-curvature.mjs` pass inside `mathematical-design-system`, and every cross-skill link resolves inside the plugin.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Sources are the user-level skill folders, merged 2026-10-25 so every copy of a shared skill is identical: `~/.claude/skills/<name>` and `~/.codex/skills/<name>` on this Mac, and the same paths on the share mounted at `/Volumes/kimba`. A skill found only on the share is read from `/Volumes/kimba/.codex/skills/<name>`. Pre-merge backups: `~/skill-backups/2026-10-25-pre-merge/`. Each plugin ships for both hosts: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, a row in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (parity), and passes `python3 scripts/check-packaging.py` (it checks skill routes and sizes). Cross-skill links: `base-ui/SKILL.md` reads `../mathematical-design-system/assets/differential-forms/` and links `../closed-loop-run/references/ui-feedback.md`; `closed-loop-run` goes to the dev-tools plugin (T-0792), so that link needs a cross-plugin route or the page moves. `base-ui/kit.json` holds file hashes; run `node scripts/seal.mjs` after any change in `base-ui`.

## Constraints
Model, effort and permission defaults in the skills stay as they are.

## Outcome
`plugins/design/` ships eight skills for Claude Code and Codex (version 0.1.0): `base-ui`, `mathematical-design-system`, `hct-palettes`, `ui-kit-inspector`, `component-variants`, `wireframe-review`, `design-crit` and `make-figma-agent-connector`, with both host manifests, `AGENTS.md` (skill table, rules, checks) and `CLAUDE.md`. Sources: `~/.codex/skills/` for the first six (identical to the share and the Claude copies), `/Volumes/kimba/.codex/skills/` for `design-crit` and `inspector-panels`, `~/.claude/skills/` for `make-figma-agent-connector`. Both marketplace catalogs list `design`; `AGENTS.md`, `README.md` and `docs/README.md` each gained one route.

- inspector-panels merged into ui-kit-inspector, as `ui-kit-inspector/examples/inspector-panel/`. Reason: both trigger on the same asks (jig, tweak panel, inspector panel); ui-kit-inspector is the newer, framework-neutral skill with the jig contract, change-set schema and checker, while inspector-panels is one plain-DOM implementation of a panel; its SKILL.md was 38,926 characters, over the 18,000 skill limit, because it embedded copies of its own JS and CSS. Its SKILL.md became `README.md` without the embedded copies; `scripts/build.mjs` no longer syncs them and its test no longer checks them; both now reach `mathematical-design-system` four levels up. `npm test` there passes 3 of 3. ui-kit-inspector's SKILL.md and `examples/README.md` route to it.
- Cross-plugin route: base-ui's link to `../closed-loop-run/references/ui-feedback.md` is now plain text naming the `dev-tools:closed-loop-run` skill and its `references/ui-feedback.md` page, so it does not depend on a path into another plugin.
- Cross-skill links: `scripts/check-packaging.py` adds `check_design`: each skill's frontmatter name equals its folder, a link that leaves its skill (or names a sibling skill but climbs too little) must resolve inside the plugin, and a link into another plugin fails. Negative controls observed: the old closed-loop-run link, an under-climbing link, a link into `progressive-context`, a missing sibling skill and a renamed frontmatter each fail it. Two historical base-ui files (`references/pre-differential/geometry-spacing.md`, `skill-entry-history.md`) had cross-skill links one level too shallow; they now resolve. base-ui was resealed (`kit.json`: three hashes changed).
- `make-figma-agent-connector` runs its script from `${CLAUDE_PLUGIN_ROOT}/skills/make-figma-agent-connector/scripts/start-bridge.sh`, not `~/.claude/skills/`. It stays Claude Code only (`Monitor`, `allowed-tools`).
- Left out: `base-ui/resources/reports/` (5.4 MB) and `wireframe-review/resources/reports/` (4.1 MB) dated evidence, both outside the base-ui seal; `mathematical-design-system/assets/proportion-lab/.git` (a nested repository, 3.4 MB) and `.openai/hosting.json` (a hosting project id); every `.DS_Store`. No `node_modules`, `__pycache__` or symlinks were in the sources. `wireframe-review/references/reports/` ships because base-ui links into it.
- 56 broken relative links came over from the sources: links to a UI-KIT checkout on this Mac, historical files written from the skill root, five targets already missing in the source skills, and one to the dropped `resources/reports/`. They are listed in `docs/reports/broken-links-allowlist.md` with reasons so `check.py` item 32 stays green.
- Pre-existing, not changed: `component-variants/ui-kit.lock.json` (version 1.0.0) and `wireframe-review/ui-kit.lock.json` do not match base-ui's identity, so `component-variants/scripts/check-build.mjs` fails in the source and in the plugin alike; the locks say to update them only after a kit review.

- Codex category values copy the peers (`Developer Tools` in the manifest, `Productivity` in the catalog), the only values with load evidence here; no check validates the field.
- `git diff --check` over the whole lane flags trailing whitespace only in copied files: the two font `OFL.txt` licenses, generated `geometry-runtime/` and `proportion-lab/dist/` modules, and a few base-ui, wireframe-review and proportion-lab sources. They stay byte-identical to the sources (base-ui is sealed).
- Left for the integrator after T-0791, T-0792 and T-0793 land: `README.md` line 3 says "Two independently installable plugins" and its Claude install line names two plugins; `docs/references/plugin-compatibility.md` lines 15 and 16 say "both".

Checks: `python3 scripts/check-packaging.py` exit 0; `node scripts/check-kit.mjs` (base-ui) exit 0; `node scripts/check-geometry.mjs` and `node scripts/check-curvature.mjs` (mathematical-design-system) exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `git diff --check` on the shared-file edits exit 0.

## Acceptance criteria
- `python3 scripts/check-packaging.py` exits 0 (catalogs, manifests, skill names and sizes, design cross-skill links).
- `cd plugins/design/skills/base-ui && node scripts/check-kit.mjs` exits 0.
- `cd plugins/design/skills/mathematical-design-system && node scripts/check-geometry.mjs` exits 0.
- `cd plugins/design/skills/mathematical-design-system && node scripts/check-curvature.mjs` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `test -z "$(find plugins/design -name .DS_Store -o -name node_modules -o -name __pycache__ -o -name .git -o -name resources -o -type l)"` exits 0.

## Outcome

2026-10-25 · lane: full L3 · verdict: pass · verifier: verifier-L3 (fable) · base: e64133fd12a4
- Changed: see commits
- Commits: a7a1dbf T-0791: record the solo L3 lane choice in skips.md; eccc80c T-0791: peer Codex categories and outcome notes; 11e172f T-0791: outcome and acceptance criteria; c4ce660 T-0791: allowlist broken links carried over from the design skills; 8ec1a88 T-0791: add the design plugin
- Check: 1 `python3 scripts/check-packaging.py` exits 0 (catalogs, manifests, skill names and sizes, design ...: pass
- Check: 2 `cd plugins/design/skills/base-ui && node scripts/check-kit.mjs` exits 0: pass
- Check: 3 `cd plugins/design/skills/mathematical-design-system && node scripts/check-geometry.mjs` exits 0: pass
- Check: 4 `cd plugins/design/skills/mathematical-design-system && node scripts/check-curvature.mjs` exits 0: pass
- Check: 5 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 6 `test -z "$(find plugins/design -name .DS_Store -o -name node_modules -o -name __pycache__ -o -na...: pass
- Follow-up: note: docs/reports/broken-links-allowlist.md:7 on conductor choice 1... -> notes.md
- Follow-up: decide: plugins/design/skills/base-ui/references/pre-differential/skill-ent... -> notes.md
- Follow-up: note: plugins/design/skills/ui-kit-inspector/examples/README.md:9 on... -> notes.md
- Follow-up: note: scripts/check-packaging.py:67 on conductor choice 3: check_design... -> notes.md
- Follow-up: note: scripts/check-packaging.py:30 the hardcoded catalog set... -> notes.md
- Follow-up: fix-now: README.md:3 says "Two independently installable plugins" above the... -> notes.md
- Follow-up: note: docs/references/plugin-compatibility.md:19 describes... -> notes.md
- Follow-up: note: plugins/design/skills/make-figma-agent-connector/intent.md:2 and... -> notes.md
- Follow-up: note: plugins/design/skills/wireframe-review/scripts/export-type-snapshot... -> notes.md
- Follow-up: note: plugins/design/skills/component-variants/ui-kit.lock.json:1 and... -> notes.md
