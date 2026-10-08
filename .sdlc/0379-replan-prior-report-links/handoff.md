---
id: T-0379
title: "Split and supersede keep references to a superseded step's reports pointing at the old attempt"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a step is superseded, every reference to its prior reports in the new step handoff points into the immutable `step-N.superseded-K` folder, and a link check runs before any role is dispatched.

## Intent
- Do: (1) Add a pre-dispatch link validator over a step handoff (in scripts/steps.py, run by `steps.py lint` and by `dispatch.py prepare`): every cited `.sdlc` path must exist, and a path that names a prior-attempt report (a `builder-L*.md`, `verifier-L*.md` or `plan-reviewer` file inside a step folder that now has a `step-N.superseded-K` sibling) must point into the superseded folder, not the current `step-N/`. (2) Make `steps.py split` (and the supersede-rename step of the chain skill) rewrite or flag such references in the new handoff when it creates it from a replanned plan: rewrite only the new handoff's references, never a finished report, and keep the intended attempt identity. (3) Keep stale-input warnings for real edits after a runner launch; do not suppress input hashing. The exact producer of the stale references in maison is not isolated, so reproduce on a fixture first and say which path writes them.
- Non-goals: model or effort changes; ignoring input hashes; rewriting historical reports.
- Done when:
  - Fixture tests (observed failing first): steps 3 and 4 reusing WIP and a step 9 fix citing its previous verifier all reference the correct superseded directories before runner input hashing; an absent path is refused; path reuse (a later new builder-L3.md must not satisfy a link meant for the previous build) is caught.
  - check.py, tickets.py check, steps and dispatch selftests, both generate --check pass.

## Context
Codex finding forwarded by the maison conductor, 2026-10-08 (maison's T-0288; copy at the maison repo .sdlc/tickets/0288-replan-prior-report-links/handoff.md, reporter priority P2, size L1, budget 30 USD). Evidence in maison: .sdlc/tickets/0152-manifest-driven-renderers/step-3, step-4 and step-9 handoffs cite step-N/builder-L3.md or step-N/verifier-L3.md, while the prior reports are under step-N.superseded-1; the pointers were corrected by amendment after the runner launched, which tripped a valid stale-input warning. The maison conductor groups this with T-0376 (stale base sha) and T-0377 (split in the wrong tree): all three are split and supersede bookkeeping, so they can share a lane or a design pass. Maison renumbering note: this repo's own T-0288 is the headless retirement; this ticket is T-0379 here.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and prints `ok: (L)` cases: split rewrites steps 3, 4 and 9 citations into step-N.superseded-K, lint refuses an absent path, lint refuses a live-step report path that has a superseded sibling (path reuse), a rewrite never touches a finished report.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and includes the `link check` cases (refusal exit 2 equal to run.sh, negative control with the `links` gate skipped).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0; `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0; `codex_roles.py generate --check` and `claude_roles.py generate --check` exit 0.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 (run.sh carries the same link gate as dispatch.py).
- Input hashing in dispatch.py record (stale input warning) is unchanged: `git diff` of plugins/sdlc-lite/scripts/dispatch.py touches only the `links` gate, GATES, the docstring and its selftest case.
