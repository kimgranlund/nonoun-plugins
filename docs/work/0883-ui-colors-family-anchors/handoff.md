---
id: T-0883
title: "ui-colors: family anchors, role-name checks, one bright-hue verdict, families.mjs"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-colors` takes the user's patch from the MacBook share: `familyAnchors`, checked role names, one bright-hue verdict per run, and `scripts/families.mjs`, with their checks and docs.

## Intent
- Do: apply `/Volumes/kimba/Downloads/ui-colors-updates/0001-ui-colors-family-anchors-role-name-checks-one-bright.patch` with `git am`, add an Unreleased changelog line, run the skill's checks.
- Non-goals: the PR's open items (step 10 of cusp-bright solids in dark, bundled Radix scales, warm text steps); the `tokens 2/` output folder; editing the MacBook copy.
- Done when: the criteria below hold.

## Context
- Source folder (read-only, never write under `/Volumes/kimba`): `/Volumes/kimba/Downloads/ui-colors-updates/` holds the patch (one commit, 7 files, base `729a475`), `PR.md` (changes, checks, open items) and `ui-colors-pr.md` (the original write-up). The patch applies cleanly to `main` at `49f390f0`.
- The patch adds `docs/reports/2026-11-24-ui-colors-radix-match.md` (evidence), `plugins/design/skills/ui-colors/scripts/families.mjs`, and changes `system.mjs`, `check.mjs`, `references/system.md`, `SKILL.md` and the `ui-colors` row of `plugins/design/AGENTS.md`.
- The author reports `node scripts/check.mjs` at 73 of 74 checks and 134 of 134 negative controls; the one failure, `neutrals: default run byte-identical to the recorded digest`, failed identically on the unmodified skill under Node 22.23.5.
- `SKILL.md` must stay under 18,000 characters (packaging check).

## Do
1. `git am` the patch in the lane.
2. Add an `### Added` (or `### Changed`) line under `## [Unreleased]` in `plugins/design/CHANGELOG.md`.
3. Run the checks below.

## Acceptance criteria
- `git log --format=%s -2` in the lane includes `ui-colors: family anchors, role-name checks, one bright-hue verdict, families.mjs`.
- `cd plugins/design/skills/ui-colors && node scripts/check.mjs` passes every check except at most the default-output digest; if the digest fails, it fails identically on `main` at `49f390f0` (same check, same digests).
- A request with an unknown `roles` key exits 2, and a request with `familyAnchors` for one family moves that family's step 9 to the given value while the six roles keep their families.
- `grep -q familyAnchors plugins/design/CHANGELOG.md` exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check 49f390f0` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Default output (`{}` request) stays byte-identical to `main`.
