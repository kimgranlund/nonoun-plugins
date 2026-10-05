---
id: T-0244
title: "Migrate this repository's docs/ to the schema through the reorganization tooling"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2
depends: [T-0242, T-0243]   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
This repository's docs/ is migrated to the schema through the reorganization tooling: inventory, a plan, and a gated apply, with `docs/validation/` kept as a legacy home.

## Intent
- Do: (1) run the inventory script (plugins/sdlc-lite/scripts/inventory.py from the reorganization project) and docs_check.py on this repository; (2) have a solo session write the migration plan from the mapping table in the design (specs/, planning/, references/, other/, archive/ as listed; `docs/validation/` and `docs/readiness-recovery-validation.md` stay and are listed in `## Legacy` with `validation/` bound to `reports` in `## Kinds`); (3) apply it in batches through the gated apply step (dry run, citing-file scan over tracked text files including check.py, root and plugin AGENTS.md, README.md and the HARNESS-NOTES.md files, one commit per batch, undo by git revert); (4) update docs/layout.md, docs/AGENTS.md, docs/README.md and entry files; (5) make docs_check.py a gate in check.sh for this repository. Depends on the gated apply ticket from the reorganization project, filed on the reorg-inventory branch as T-0233 (add it to `depends` once it is on main).
- Non-goals: moving docs/validation, a version bump, tag, push, or publish.
- Done when: docs_check.py passes on this repository, no link or code reference to a moved path is broken (check.sh and check-packaging.py pass), the plan and each batch are recorded in a validation doc with committed evidence, and an independent verifier passed.

## Context
Part of the docs schema design (docs/docs-schema/design.md v0.2, ticket T-0240), reviewed once by an independent architect (docs/validation/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.
