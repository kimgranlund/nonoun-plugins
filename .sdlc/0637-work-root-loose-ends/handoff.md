---
id: T-0637
title: "work_root loose ends: planner untracked exclude, fleet Source column, registry and usage text"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Close the work_root loose ends found while building T-0621 to T-0635, so this repository can migrate with every reader and agent text correct.

## Context
Split from T-0636 on 2026-10-19 so the migration ticket stays one move. Each item below was reported by the solo or verifier of the named ticket. Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md`.

## Constraints
- Old layouts stay the default: with no `work_root:` line every path and every pinned selftest string is unchanged; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.

## Acceptance criteria
- Loose ends from earlier tickets, fold in here: `docs/specs/sdlc-lite/fleet-config.md` and the `fleet_config.py` header still name only `.sdlc/fleet.json` (T-0629); `fleet_status.py` render Source cells print `<repo>/.sdlc/<task>` for work-root tickets, pinned by its selftest (T-0629); the `tickets.py` usage docstring describes only the old layouts (T-0623).
- From T-0625: `docs/specs/repo-onboarding/design.md` does not yet describe the work-root root block (`docs/work/AGENTS.md` entry pointing at `.sdlc/AGENTS.md`).
- From T-0633: `agents/planner.md` builds its untracked-files scope check with `":(exclude).sdlc"`; under `work_root` task folders in `docs/work` are not excluded and would count as untracked. Exclude the work root too (via `roots.record_prefixes` in the generated check, or the planner text), with a case.
- `python3 plugins/sdlc-lite/scripts/check.py`, `claude_roles.py generate --check`, `codex_roles.py generate --check`, and the selftests of every script touched exit 0.
