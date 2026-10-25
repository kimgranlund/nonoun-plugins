---
id: T-0791
title: "new design plugin from the user-level design skills"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
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
