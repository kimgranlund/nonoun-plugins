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
A repository that adopts SDLC Lite gets entry files that route into `docs/` and `.sdlc/` and a stated docs layout, without losing anything it already wrote.

## Intent
- Do: build the `onboard` skill and its script as specified in `docs/repo-onboarding/design.md` (v0.4).
  1. Setup mode: upsert the root `AGENTS.md` and `CLAUDE.md`, `.sdlc/AGENTS.md`, `docs/AGENTS.md`, topic entries, and the `CLAUDE.md` stubs in `docs/`, from the templates in the design.
  2. Managed blocks with a template version, starter text written once, and the five upsert states.
  3. The check that refuses a ticket folder path in a managed block.
  4. Check mode: report managed blocks older than the installed template version and write nothing.
- Non-goals: moving or rewriting existing documents (T-0161); changing the planner or handoff format (T-0162); monorepo support; converting an existing `README.md` index; a `CLAUDE.md` in `.sdlc/`; creating contracts, assessments, or lifecycle states; any dependency on ICM.
- Done when: every gate in the design's validation table has a passing positive case and an observed negative control, including the live run on both hosts.

## Context
Design: `docs/repo-onboarding/design.md`. Index of the topic: `docs/repo-onboarding/README.md`. Decisions agreed with the user on 2026-09-29: the skill lives in SDLC Lite and is named `onboard`, navigation follows Progressive Context, the layout is an overridable default, number prefixes express order only, existing `README.md` indexes stay, and monorepos are out of scope for version 1.

Evidence: `docs/validation/repo-onboarding-design-review.md` and `docs/validation/nested-entry-file-loading.md`. The probe showed that Claude Code loads a nested `AGENTS.md` only through a `CLAUDE.md` beside it, that the import works between the managed block markers, and that Codex loads entries only from the repository root down to its working directory.

The Codex install in `scripts/codex_roles.py` already uses managed files, an ownership receipt, and `install --check`. Follow that pattern.

Unsettled: whether an installed plugin can read its own template version on both hosts, and the token cost of nested entries in a real role run. The live run on Codex is affected by T-0163.

## Constraints
Progressive Context core files stay domain-neutral and keep the rule against a prescribed folder tree. Existing user content in an entry file stays byte-identical. Generated files are not edited by hand. Model and effort defaults are unchanged.
