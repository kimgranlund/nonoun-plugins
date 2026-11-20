---
id: T-0863
title: "Run the ui-explore-variants browser check with Playwright"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0863-t0863
worktree: ../sdlc-lite.worktrees/T-0863-t0863
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `ui-explore-variants` browser check has run for real against the shipped template, and the way to run it here is written down.

## Intent
- Do: run `scripts/check.mjs` with a Playwright project, fix what it finds in repo-side wiring only, and document the command.
- Non-goals: editing the synced skill files; adding Playwright to the repository's tracked dependencies.
- Done when: the criteria below hold.

## Context
- `plugins/design/skills/ui-explore-variants/scripts/check.mjs` takes a project that has Playwright (`node scripts/check.mjs <project-with-playwright>`; read its header and `check.page.html`). It has never run here: no Playwright project exists in the tree. `assets/feedback.js` came from an uncommitted source edit (T-0856).
- Make a throwaway project under your scratch dir (`npm init -y`, `npm i playwright` or `playwright-core`, `npx playwright install chromium`); this needs the network. If the network or the browser download is unavailable, report blocked with the exact error.
- If the check fails because of the skill's own files, do not edit them: record the failing checks in the report as a finding for the user's source copy.
- Document the working command, with the scratch-project steps, in the `ui-explore-variants` row or checks section of `plugins/design/AGENTS.md`, and add a `### Changed` line under `## [Unreleased]` in `plugins/design/CHANGELOG.md` only if a tracked file changed.
- The same scratch project can run `plugins/design/skills/ui-kit-inspector/examples/test.mjs` (the inspector browser suite, also never run here, needs `playwright-core`): run it too and report its result; it is not a criterion.

## Do
1. Build the scratch Playwright project.
2. Run the check and the inspector suite.
3. Document the command.

## Acceptance criteria
- The report holds the full summary output of `node scripts/check.mjs <scratch project>` run in `ui-explore-variants`, with its exit code, and names each failing check if any.
- `plugins/design/AGENTS.md` names the command and its Playwright prerequisite.
- No file under `plugins/design/skills/ui-explore-variants/` changed (`git status --short plugins/design/skills/ui-explore-variants` prints nothing), no `node_modules` or lockfile is tracked, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Scratch files stay outside the repository.
