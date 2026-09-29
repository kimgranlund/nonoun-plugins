---
id: T-0160
title: "Onboard skill: entry files, docs layout, and check mode"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

## Intent
- Do: build the `onboard` skill and its script as specified in `docs/repo-onboarding/design.md` (v0.5).
  1. Setup mode: create or update the files in the design's Files table from its templates. One script writes every file.
  2. The upsert table, rows 1 to 8, first match wins. Start markers carry a template version and a content hash.
  3. Check mode with the six labels and a nonzero exit when any file is not current.
  4. One sentence in `plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md` that names the `onboard` skill without a path link.
- Non-goals: moving or rewriting existing documents (T-0161); changing the planner or handoff format (T-0162); monorepo support; converting an existing `README.md` index; any file inside `.sdlc/`; adding starter text to a file that exists; text written by the model; a receipt file; creating contracts, assessments, or lifecycle states; any dependency on ICM.
- Done when: the existing checks named in the design pass, every new gate in the design's validation table has a passing positive case and an observed negative control in the script's selftest, and the live run gate passes on Claude Code and on Codex.

## Context
Design: `docs/repo-onboarding/design.md`. Index of the topic: `docs/repo-onboarding/README.md`. Decisions agreed with the user on 2026-09-29: the skill lives in SDLC Lite and is named `onboard`, navigation follows Progressive Context, the layout is an overridable default kept in `docs/layout.md`, number prefixes express order only, existing `README.md` indexes stay, monorepos are out of scope for version 1, and the guidance for `.sdlc/` lives in the root managed block because `.sdlc/` is ignored by Git by default.

Evidence: `docs/validation/repo-onboarding-design-review.md`, `docs/validation/repo-onboarding-design-review-2.md`, and `docs/validation/nested-entry-file-loading.md`. The probe showed that Claude Code loads a nested `AGENTS.md` only through an import in a loaded `CLAUDE.md`, that the import works between the managed block markers, and that Codex loads entries only from the repository root down to its working directory.

`scripts/codex_roles.py` has an `install --check` that compares generated content and returns before any write. Check mode follows that behavior. It does not use that script's receipt file.

The Codex live run needs a model the account accepts. On the maintainer's machine `gpt-6-astra` works and `gpt-6-sol` and `gpt-6-luna` do not (T-0163). Run the Codex gate at a level mapped to an accepted model, or after T-0163.

Unsettled: whether an installed plugin can read its own template version on both hosts, and the token cost of nested entries in a real role run.

## Constraints
Progressive Context core files stay domain-neutral and keep the rule against a prescribed folder tree. Existing user content in an entry file stays byte-identical. Generated files are not edited by hand. Model and effort defaults are unchanged.
