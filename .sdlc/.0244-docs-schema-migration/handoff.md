---
id: T-0244
title: "Migrate this repository's docs/ to the schema through the reorganization tooling"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2
depends: [T-0242, T-0243, T-0246]   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
This repository's docs/ is migrated to the schema through the reorganization tooling: inventory, a plan, and a gated apply, except the `docs/reports/` rename, which is its own ticket, T-0246.

## Intent
- Do: (1) run the inventory script (plugins/sdlc-lite/scripts/inventory.py from the reorganization project) and docs_check.py on this repository; (2) have a solo session write the migration plan from the mapping table in the design (specs/, planning/, references/, guides/, other/, archive/ as listed, with `maintenance/` content split between `references/` and `guides/` by what it is; the validation and readiness-recovery-validation moves are NOT part of this ticket: T-0246 does them, and this ticket starts only after T-0246 has merged so the plan sees `docs/reports/`); (3) apply it in batches through the gated apply step (dry run, citing-file scan over tracked text files including check.py, root and plugin AGENTS.md, README.md and the HARNESS-NOTES.md files, one commit per batch, undo by git revert); (4) update docs/layout.md, docs/AGENTS.md, docs/README.md and entry files; (5) make docs_check.py a gate in check.sh for this repository. Depends on the gated apply ticket from the reorganization project, filed on the reorg-inventory branch as T-0233 (add it to `depends` once it is on main), and on T-0246 (add T-0246 to `depends` now).
- Non-goals: the validation rename (T-0246), a version bump, tag, push, or publish.
- Done when: docs_check.py passes on this repository, no link or code reference to a moved path is broken (check.sh and check-packaging.py pass), the plan and each batch are recorded in a validation doc with committed evidence, and an independent verifier passed.

## Context
Part of the docs schema design (docs/docs-schema/design.md v0.4 with the user's decisions of 2026-10-05 under Resolved decisions, ticket T-0240), reviewed once (v0.1) by an independent architect (docs/reports/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.

## Acceptance criteria
Run from the repository root. The record is `docs/reports/2026-10-06-docs-schema-migration.md`.
1. `python3 plugins/sdlc-lite/scripts/docs_check.py` exits 0 with 0 errors.
2. `python3 plugins/sdlc-lite/scripts/rename_refs.py links` reports 12 broken links, the same twelve as before the change (`docs/reports/broken-links-allowlist.md` lists them), and `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` prints no `FAIL`.
3. For each old path (`docs/maintenance`, `docs/sdlc-lite`, `docs/ticket-stages`, `docs/repo-onboarding`, `docs/generative-constructs`, `docs/docs-schema`, `docs/codex-role-execution.md`, `docs/plugin-compatibility.md`, `docs/claude-handoff.md`, `docs/claude-response.md`), `rename_refs.py check <path>` with the allowlist named in the record's Result section prints `0 stale references`; no tracked file outside the allowlist cites a moved path, `check.py` and the root and plugin `AGENTS.md`, `README.md` and both `HARNESS-NOTES.md` included.
4. The files moved as the record's Plan table says: `docs/specs/`, `docs/planning/`, `docs/references/` and `docs/other/` hold them, `docs/maintenance`, `docs/sdlc-lite`, `docs/ticket-stages`, `docs/repo-onboarding`, `docs/generative-constructs` and `docs/docs-schema` no longer exist, every `planning/` file has `status: proposed`, every `other/` file has `owner:` and `review-by:`, and `docs/reports/` changed only by path citations, the two link-allowlist rows, its entry files and the new record.
5. `docs/layout.md` exists and parses (`python3 plugins/sdlc-lite/scripts/onboard.py check` lists no `malformed` or `stale`), its `## Legacy` list holds exact paths (no glob that would exempt a new dated report), `docs/AGENTS.md` and `docs/README.md` describe the new homes, and the record holds the plan, each batch with counts, the baseline, and the deviations (T-0233 not built, no per-batch commit).
6. `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` and `python3 plugins/sdlc-lite/scripts/rename_refs.py selftest` print PASS; the B-1a change has a positive case and a negative control in the selftest (a generated name in an evidence folder is not flagged, the same name under `docs/specs/` is flagged, a variant that ignores the exemption fails the gate).
7. `plugins/sdlc-lite/scripts/check.sh` runs `docs_check.py --root` on this repository; with a stray `docs/stray-note.md` staged, the gate line exits 1 naming D-2, and without it exits 0.
8. `bash plugins/sdlc-lite/scripts/check.sh` fails only on what failed before the change (`codex_roles.py generate --check` drift, `FAILED (failures=5, errors=1)` in `codex-selftest.py`, `FAILED (failures=3)` in `lifecycle-selftest.py`); `python3 scripts/check-packaging.py` passes; `git diff --check HEAD` is clean.

## Closed

2026-10-06: built and merged by fanout lane
