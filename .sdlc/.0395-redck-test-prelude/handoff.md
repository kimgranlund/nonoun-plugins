---
id: T-0395
title: "redck treats a declared new regression test as an implementation edit"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`redck.py record` accepts a declared test-only prelude, so writing the required failing test before any implementation still records a pre-edit red checkpoint.

## Intent
- Do: in scripts/redck.py (`dirty_paths`, about lines 87 to 96, and `record`, about line 148) separate the regression-fixture prelude from the implementation base. The step handoff may declare test paths (a `tests:` line, choose the shape that fits the handoff format and lint it). A dirty path that is a declared test, and only that, is hashed into the checkpoint as a prelude and does not make the phase retrospective; any other dirty path still does. Bind the test content hash to the later green check. No blanket ignore of tests or tests/ directories; an undeclared test file still counts as an edit.
- Non-goals: model or effort changes; changing what a red criterion is.
- Done when:
  - Selftest cases, each observed failing first: a declared new test with implementation untouched records pre-edit and stores its sha256; a declared test plus one source edit is retrospective; an undeclared new test is retrospective; a declared test whose content changes after recording fails the later green binding.
  - redck.py selftest, steps.py selftest, check.py and tickets.py check pass; update the handoff-format skill line that describes the red checkpoint.

## Context
Maison and Codex, 2026-10-08, 0.22.0: report at maison .sdlc/tickets/0310-contract-view-schema-agreement/sdlc-bug-new-test-red-checkpoint.md. Distinct from T-0389 and T-0287.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/redck.py selftest`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `grep -q 'tests: <path>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- Behavior: a declared dirty test is a hashed prelude (phase stays pre-edit), an undeclared test or any source path makes the phase retrospective, and a declared test changed after recording makes `redck.py audit` report prelude-changed.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
