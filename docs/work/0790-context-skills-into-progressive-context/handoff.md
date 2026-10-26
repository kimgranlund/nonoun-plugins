---
id: T-0790
title: "move the context skills into the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789, T-0793]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `context` plugin (renamed from progressive-context by T-0793) ships the context skills, so every repo and both machines load one version instead of drifting user-level copies.

## Intent
- Do: add `context-fog-of-war`, `context-routing-review`, `generative-systems`, `system-atlas` and `icm-architect` under `plugins/context/skills/`; update the plugin's `AGENTS.md`, manifests and version; record which user-level copy each came from.
- Non-goals: rewriting the skills' content; deleting the user-level copies (the user does that after install).
- Done when: `python3 scripts/check-packaging.py` passes, each skill's description routes (no duplicate trigger with `context:progressive-context`), and every relative link inside the moved skills resolves.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Sources are the user-level skill folders, merged 2026-10-25 so every copy of a shared skill is identical: `~/.claude/skills/<name>` and `~/.codex/skills/<name>` on this Mac, and the same paths on the share mounted at `/Volumes/kimba`. A skill found only on the share is read from `/Volumes/kimba/.codex/skills/<name>`. Pre-merge backups: `~/skill-backups/2026-10-25-pre-merge/`. Each plugin ships for both hosts: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, a row in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (parity), and passes `python3 scripts/check-packaging.py` (it checks skill routes and sizes). `generative-systems` carries a large `resources/reports/` tree (739 differing files in the 2026-10-25 comparison) and one dangling symlink (`resources/reports/split-consumption-followup-2026-10-11/main-evidence/author/evaluator-alias`); decide what ships and what stays out of the package. Read `plugins/context/AGENTS.md` first.

## Constraints
The plugin's existing skill behavior does not change.

## Outcome
`plugins/context/` (version 0.3.0) ships five more skills beside `progressive-context`, for Claude Code and Codex: `context-fog-of-war`, `context-routing-review`, `generative-systems`, `system-atlas` and `icm-architect`. Sources: `~/.claude/skills/` for `context-fog-of-war`, `generative-systems` and `system-atlas` (identical to `~/.codex/skills/` and both share copies apart from `.DS_Store`); `/Volumes/kimba/.codex/skills/` for `context-routing-review` (the only copy); `~/.claude/skills/` for `icm-architect` (the only copy; upstream RinDig/icm-architect, MIT, per its `SOURCE`). `AGENTS.md` gained a skill table with sources and the shared rules; both manifests went to 0.3.0 with a wider description; the Claude catalog description, `HARNESS-NOTES.md`, `CHANGELOG.md` and the README row name the new skills.

- Left out: `generative-systems/resources/reports/` (12 MB of dated evidence, the 739-file tree, with the dangling `evaluator-alias` symlink inside it); every `.DS_Store`; `context-fog-of-war/scripts/__pycache__/`. No `.git` or `node_modules` were in the sources. `context-fog-of-war/updates-log/` ships: it is that skill's change log, and its `AGENTS.md` says to record each change there.
- Link fixes, content otherwise unchanged. `scripts/check-packaging.py` fails any broken link in context skills (no allowlist), so 27 broken links became plain text with the path in a code span: 22 into the dropped `resources/reports/` (evidence index, split spec, eight revision proposals), of which 4 point into design skills' reports and now name `design:wireframe-review` or `design:base-ui`, and 5 to a file in the author's Downloads folder. `check.py` item 42 (self-contained skills) fails any link starting with `../` even when it stays inside the skill, so 17 such links (two in `context-fog-of-war` references, fifteen in `generative-systems/revisions/proposals/`) became code spans naming the file from the skill root. No allowlist rows were needed.
- Routing: a blind routing judge given the six descriptions and twelve prompts picked `progressive-context` for all four of its prompts (split a large AGENTS.md, intent stub and assessment, prepare for reuse, bloated navigation) and a moved skill, with no tie, for each of the others. One tie, between two moved skills: "map this repo" is in `icm-architect`'s trigger list and in `system-atlas`'s scope. Descriptions were not edited (content unchanged).
- Hard-coded paths, not links, kept as written: `icm-architect/README.md` install line (`~/.claude/skills/icm-architect/`, upstream text) and author-machine paths in code spans in `generative-systems` evidence files.
- `git diff --check` flags only copied files, kept byte-identical: `system-atlas/assets/vendor/mermaid-11.12.0.min.js` (sha256-pinned in its `manifest.json`), the embedded OFL font license in `context-fog-of-war/assets/shell.html`, and a blank line at the end of `fragment.html` and four `context-fog-of-war` references. Every other added or edited file is clean.

Checks: `python3 scripts/check-packaging.py` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 -B -m unittest discover -s tests` in `context-fog-of-war` 51 tests OK; `python3 -B scripts/test_atlas_renderer.py` in `system-atlas` OK; `git diff --cached --check` exit 0 outside the copied files listed above.

Open: the item 42 rule rejects `../` links that resolve inside the skill (a nested reference linking its own `SKILL.md`); relaxing it is a separate ticket. Remove the user-level copies of the five skills after installing 0.3.0.

## Acceptance criteria
verifier: L3
- `python3 scripts/check-packaging.py` exits 0 (catalog parity, identity, skill sizes, every relative link in context skills resolves).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 (item 42: no context skill link leaves its folder).
- `test -z "$(find plugins/context \( -name .DS_Store -o -name __pycache__ -o -name node_modules -o -name .git -o -path '*/resources/reports' -o -type l \))"` exits 0.
- `test -f plugins/context/skills/context-fog-of-war/SKILL.md -a -f plugins/context/skills/context-routing-review/SKILL.md -a -f plugins/context/skills/generative-systems/SKILL.md -a -f plugins/context/skills/system-atlas/SKILL.md -a -f plugins/context/skills/icm-architect/SKILL.md` exits 0.
- `cd plugins/context/skills/context-fog-of-war && python3 -B -m unittest discover -s tests` exits 0.
- `cd plugins/context/skills/system-atlas && python3 -B scripts/test_atlas_renderer.py` exits 0.
- `grep -q '"version": "0.3.0"' plugins/context/.claude-plugin/plugin.json && grep -q '"version": "0.3.0"' plugins/context/.codex-plugin/plugin.json` exits 0.
