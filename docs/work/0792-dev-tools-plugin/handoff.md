---
id: T-0792
title: "new dev-tools plugin from the user-level machine and harness skills"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A new `dev-tools` plugin ships the machine, repo and harness care skills for Claude Code and Codex.

## Intent
- Do: create `plugins/dev-tools/` with `closed-loop-run`, `flaky-gates`, `port-zombie-sweep`, `git-bare-repo-setup`, `macos-build-and-verify`, `author-cross-harness-plugins` and `skill-report-card`, plus an `AGENTS.md` for the plugin.
- Non-goals: the duplicates T-0789 names for fold or retire; content rewrites.
- Done when: `python3 scripts/check-packaging.py` passes and every relative link inside the moved skills resolves, including `closed-loop-run/references/ui-feedback.md` that `base-ui` (T-0791) links to.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Sources are the user-level skill folders, merged 2026-10-25 so every copy of a shared skill is identical: `~/.claude/skills/<name>` and `~/.codex/skills/<name>` on this Mac, and the same paths on the share mounted at `/Volumes/kimba`. A skill found only on the share is read from `/Volumes/kimba/.codex/skills/<name>`. Pre-merge backups: `~/skill-backups/2026-10-25-pre-merge/`. Each plugin ships for both hosts: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, a row in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (parity), and passes `python3 scripts/check-packaging.py` (it checks skill routes and sizes). `closed-loop-run` was three-way merged on 2026-10-25 (this Mac's 10-17 edits plus the share's 10-24 `ui-feedback` page). `macos-build-and-verify` exists only on the share. `flaky-gates` and `port-zombie-sweep` reference each other by name.

## Constraints
None.

## Outcome
New plugin `plugins/dev-tools/` (version 0.1.0) with both host manifests, `AGENTS.md`, `CLAUDE.md`, and one entry in each marketplace catalog. Seven skills copied verbatim from the user-level folders: `closed-loop-run`, `flaky-gates`, `port-zombie-sweep`, `git-bare-repo-setup`, `author-cross-harness-plugins` from `~/.claude/skills`, `skill-report-card` from `~/.codex/skills`, and `macos-build-and-verify` from `/Volumes/kimba/.codex/skills` (readable; note it is specific to the LG Controls Mac app). `closed-loop-run/references/ui-feedback.md` ships at that path.

Changes beyond the copy:
- `closed-loop-run/SKILL.md` was 21,515 characters, over the 18,000 limit. The bodies of sections 7, 14, 15 and 20 moved unchanged into `references/taxonomy-and-hardening.md`; each heading stays with a one-line link (now 16,615).
- Eight links from `closed-loop-run` references to `../../context-fog-of-war/references/learnings/*.md` point into another plugin (T-0790), so they became by-name references: `context:context-fog-of-war` plus the file path.
- One trailing space removed in `skill-report-card/assets/dashboard.html` line 52 (`git diff --check`).
- `scripts/check-packaging.py`: `dev-tools` added to the catalog set; the same-named entry-point skill is waived for `dev-tools` (a skill collection); the relative-link check now walks `dev-tools` skills too and ignores inline code spans as well as fenced blocks (`skill-report-card` shows a pointer snippet in inline code). Negative controls: an added broken link and the original 21.5K `SKILL.md` each made it exit 1.
- `AGENTS.md`: dev-tools no longer marked planned; its Read-for-the-task row links `plugins/dev-tools/AGENTS.md`; design's row unchanged. `README.md`: one table row, the install line, and "Two" dropped from the intro.

Left out: `.DS_Store` files (closed-loop-run, skill-report-card), `skill-report-card/resources/` (dated evidence under `resources/reports/` with two tar.gz archives near 1 MB, and the 188K `resources/example/` demo that no script or reference loads). No symlinks, `__pycache__` or `node_modules` shipped. Prose in `skill-report-card/references/spec.md` and `handoff.md` still names `resources/reports/` files as history; not links.

Open: `skill-report-card/scripts/test_traces.py` exits 1 in the source folder too (pre-existing); the other seven tests pass in the plugin copy.

## Acceptance criteria
- `python3 scripts/check-packaging.py` exits 0 (catalog parity, identity, skill sizes, relative links in dev-tools skills).
- `test -f plugins/dev-tools/skills/closed-loop-run/references/ui-feedback.md` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `test -z "$(find plugins/dev-tools \( -name .DS_Store -o -name __pycache__ -o -name node_modules -o -type l \))"` exits 0.
