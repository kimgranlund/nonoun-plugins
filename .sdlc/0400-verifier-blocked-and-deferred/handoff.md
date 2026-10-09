---
id: T-0400
title: "verifier reports unmet dependency and deferred-to-owner apart from fail"
type: feature
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier report separates a real failure from an unmet prerequisite and from a criterion owned by a later stage, without allowing premature closure.

## Intent
- Do: design first (Markdown-only, no code in this ticket), then file the build as its own ticket. Read scripts/results.py (the verifier schema), agents/verifier.md, handoff-format and steps.py next-action logic. Propose: criteria carry an optional stage, owner and prerequisite subject; each criterion line may read pass, fail, `unmet-dependency <subject>` or `deferred <owner>`; the overall verdict stays pass or fail, and a ticket cannot close while any criterion is unmet or deferred. Decide how steps.py routes an unmet dependency (wait or reorder, not a replan) and how a deferred criterion is closed by its owner. Write the design to docs/specs/sdlc-lite/ with a status line and the rejected alternatives.
- Non-goals: implementing it; changing verdict values the runner already parses.
- Done when:
  - The design names the exact changes to results.py, verifier.md, handoff-format and steps.py, a negative control for premature closure, and a migration note for existing results.
  - check.py and docs_check.py pass.

## Context
Maison and Codex, 2026-10-09: 11 component lanes had rows 7 to 12 of the component-request template fail in every lane build because they are integration or testing owned, and one lane failed on a prerequisite from merge order (T-0307 schema). Evidence: maison .sdlc/tickets/0301-lean-template-bootstrap-design/codex-progress-bar-stage-evidence.md. Related: T-0386 and T-0385 template work.

## Constraints
Design only. The maintainer approved the design on 2026-10-09 ("fold those into 0.22.2"); a build still needs its own ticket. No em or en dashes. No push or publish.

## Acceptance criteria
- `test -f docs/specs/sdlc-lite/verifier-held-criteria.md && grep -q '^Status: design' docs/specs/sdlc-lite/verifier-held-criteria.md`
- `grep -c 'Rejected alternatives' docs/specs/sdlc-lite/verifier-held-criteria.md | grep -qv '^0$'`
- `for f in results.py verifier.md handoff-format steps.py; do grep -q "$f" docs/specs/sdlc-lite/verifier-held-criteria.md || exit 1; done`
- `grep -q 'Negative controls (premature closure)' docs/specs/sdlc-lite/verifier-held-criteria.md && grep -q '^## 8. Migration' docs/specs/sdlc-lite/verifier-held-criteria.md`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/docs_check.py`
- `python3 -c "import sys; sys.exit(any(c in open('docs/specs/sdlc-lite/verifier-held-criteria.md',encoding='utf-8').read() for c in '–—'))"`
- Prose: the design keeps the Verdict values pass, fail and inherited red unchanged and makes a held criterion force Verdict fail; no code file is changed.
