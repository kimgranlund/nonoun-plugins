---
id: T-0160
title: "Onboard skill: entry files, docs layout, and scan-then-ticket reorganization"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and `.sdlc/`, a stated docs layout, and a safe way to reorganize existing documents to match it.

## Intent
- Do: build the `onboard` skill and its script as specified in `docs/repo-onboarding/design.md` (v0.3).
  1. Setup mode: upsert root `AGENTS.md` and `CLAUDE.md`, `.sdlc/AGENTS.md`, `docs/AGENTS.md`, and topic entries, using versioned managed blocks and the five upsert states in the design.
  2. Check mode: report managed blocks older than the installed template version and write nothing.
  3. Scan mode: read-only inventory, classification by path and name rules, link graph, and frozen-path candidates.
  4. Plan: a move plan filed as a normal ticket, carrying the inventory digest.
  5. Apply and check: `git mv`, a dedicated link rewriter, digest recheck, and the four refusals under Move safety.
- Non-goals: creating capability contracts, assessments, or lifecycle states; moving or rewriting frozen material; reusing the `tickets.py` link rewriting; trimming an entry file that is over the size target; any dependency on ICM.
- Done when: every gate in the design's validation table has a passing positive case and an observed negative control, and the end-to-end run passes in a throwaway project on both hosts.

## Context
Design: `docs/repo-onboarding/design.md`, committed in 3ac677c. It records the decisions, the default layout, the frozen set, and the validation gates. Decisions agreed with the user on 2026-09-29: the skill lives in SDLC Lite, navigation follows Progressive Context, the layout is an overridable default, number prefixes express order only, and reorganization goes scan, then plan ticket, then approval.

An independent review of v0.1 found that `tickets.py` link rewriting replaces only the last path component of a cite and that the close scan does not see a git-ignored `.sdlc/`. Both are handled since v0.2. The number prefix section was added after that review started and has not been reviewed.

The Codex install in `scripts/codex_roles.py` already uses managed files, an ownership receipt, and `install --check`. Follow that pattern for the managed blocks and check mode.

A live probe on Claude Code (`docs/validation/nested-entry-file-loading.md`) showed that a nested `AGENTS.md` loads only with a `CLAUDE.md` stub beside it and that an `@` import of a child entry loads at once. The same probe on Codex showed that it loads entries from the root down to its working directory only, so a role started at the root reaches a nested entry by link. Design v0.3 reflects these.

Unsettled, to resolve at plan time or by a spike first: the input token cost of nested entries in a real role run, whether `.sdlc/` gets a `CLAUDE.md` stub, monorepo handling, whether an existing `README.md` index is converted, and the skill name. Split into setup plus check, then scan plus apply, if the plan needs it.

## Constraints
Progressive Context core files stay domain-neutral and keep the rule against a prescribed folder tree. Existing user content in an entry file stays byte-identical. Generated files are not edited by hand. No move runs while a `.run.lock` or `*.running` marker exists under `.sdlc/`. Model and effort defaults are unchanged.
