---
id: T-0162
title: "Planner names the entry files each step needs"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Intent
- Do:
  1. The planner adds a `### Read first` subsection to a step that needs one. It sits after the step's `level:` line and before `### Do`. Each item is one line of the form ``- `<path>` ``, with the path relative to the repository root. It lists, for each file the step changes, the nearest `AGENTS.md` in that file's folder or a folder above it. The root entry is left out. A step whose only entry is the root has no subsection.
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
Decision agreed with the user on 2026-09-29, recorded in `docs/specs/repo-onboarding/design.md` under "How roles reach an entry".

Reason: the loading probe (`docs/reports/nested-entry-file-loading.md`) showed that Codex loads entries only from the repository root down to its working directory, and roles start at the root. Claude Code loads a nested entry only through an import in a loaded `CLAUDE.md`.

Feasibility was checked in the second and third design reviews (`docs/reports/repo-onboarding-design-review-2.md` and `-3.md`): `parse_steps` in `scripts/steps.py` copies a step block up to the next `## ` line, and a `### Read first` subsection reached the step handoff unchanged with lint passing.

Handwritten step handoffs are described in `skills/fix/SKILL.md` step 2 and `skills/chain/SKILL.md` section 5 step 3. The lint command in `/fix` has a separate defect, T-0164.

The root entry is left out because both hosts load it at session start. On Claude Code that holds only when the root `CLAUDE.md` imports `AGENTS.md`, which T-0160 sets up.

On Claude Code a folder in `docs/` with a stub loads its entry automatically as well, so the entry is in context twice. That cost is accepted in the design.

The Codex live run needs a model the account accepts. See T-0163. In `adapters/codex/models.json`, builder L4 and verifier L3 map to `gpt-6-astra`, which the maintainer's account accepts. Run the Codex gate at those levels, or after T-0163.

## Constraints
The merge-step template stays consistent across planner and handoff-format. `steps.py` keeps ownership of next-action decisions. A plan without the subsection stays valid. Model and effort defaults are unchanged.

## Plan review
- step 5 builder blocked (`step-5/builder-L3.md`, `plan defect:`): the Codex verifier resolved to `gpt-6-sol`, which the maintainer's account rejects, so the Codex arm "verifier read the entry" could not run. Resolved outside this task by T-0163 (commits 1f25376 and the T-0163 step 2 commit): the user chose to replace `gpt-6-sol` with `gpt-6-astra` in `adapters/codex/models.json`, and with no alternate configured the Codex verifier now shares the builder's model. Any Codex level now runs on `gpt-6-astra`. Seven of eight arms already passed in the blocked attempt; its throwaway projects may be reused.
