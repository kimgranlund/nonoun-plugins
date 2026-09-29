---
id: T-0162
title: "Planner names the entry files each step needs"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Intent
- Do:
  1. The planner adds a `### Read first` subsection to each step. It lists, for each file the step changes, the nearest `AGENTS.md` in that file's folder or a folder above it. The root entry is left out, because both hosts load it.
  2. `steps.py split` already copies the subsection into the step handoff. `steps.py lint` refuses a listed path that does not exist.
  3. The builder and the verifier read the listed files before they start.
  4. The skills that write a step handoff by hand, `fix` and the loose-ends step of `chain`, add the same subsection.
  5. The handoff-format step template documents the subsection as optional.
- Non-goals: relying on host loading; listing entries for files the step only reads; listing the root entry; a read rule in roles other than builder and verifier.
- Done when:
  - `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/steps.py selftest`, and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` pass.
  - The `steps.py` selftest shows lint accepting an existing listed path and refusing a missing one.
  - In a live run on each host, a step that changes a file under a folder whose nearest entry is not the root produces a step handoff that lists that entry, and the builder and verifier transcripts show a read of it.
  - In the same run, a step whose nearest entry is the root has no `### Read first` subsection.

## Context
Decision agreed with the user on 2026-09-29, recorded in `docs/repo-onboarding/design.md` under "How roles reach an entry".

Reason: the loading probe (`docs/validation/nested-entry-file-loading.md`) showed that Codex loads entries only from the repository root down to its working directory, and roles start at the root. Claude Code loads a nested entry only through an import in a loaded `CLAUDE.md`.

Feasibility was checked in the second design review (`docs/validation/repo-onboarding-design-review-2.md`): `parse_steps` in `scripts/steps.py` copies a step block up to the next `## ` line, and a `### Read first` subsection reached the step handoff unchanged with lint passing.

Handwritten step handoffs are described in `skills/fix/SKILL.md` step 2 and `skills/chain/SKILL.md` section 5 step 3.

On Claude Code a folder in `docs/` with a stub loads its entry automatically as well, so the entry is in context twice. That cost is accepted in the design.

The Codex live run needs a model the account accepts. See T-0163. Run it at a level mapped to an accepted model, or after T-0163.

## Constraints
The merge-step template stays consistent across planner and handoff-format. `steps.py` keeps ownership of next-action decisions. A plan without the subsection stays valid. Model and effort defaults are unchanged.
