---
id: T-0408
title: "Build verifier unmet-dependency and deferred-to-owner verdicts (design T-0400)"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The verifier can report a criterion as `unmet-dependency <subject>` or `deferred <owner>` apart from `fail`, and a ticket cannot close while any criterion is unmet or deferred.

## Intent
- Do: build exactly what docs/specs/sdlc-lite/verifier-held-criteria.md specifies across scripts/results.py, agents/verifier.md (and its generated copies), the handoff-format skill, scripts/steps.py next-action routing, and the migration note for existing results. Include the negative control for premature closure.
- Non-goals: other verdict values; model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: an unmet-dependency criterion routes to wait or reorder, not a replan; a deferred criterion is closed by its owner; a ticket with an unmet or deferred criterion is refused at close; existing pass and fail results still parse.
  - results, steps, dispatch and tickets selftests, check.py, claude_roles.py and codex_roles.py generate --check pass.

## Context
Maison and Codex, 2026-10-09: 11 component lanes failed on template rows 7 to 12 that a lane build cannot meet (2 to 3 hours). Design approved 2026-10-09 (T-0400); build approved in the same session.

## Constraints
No em or en dashes. No push or publish. The design is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
- Result parsing: `python3 plugins/sdlc-lite/scripts/steps.py selftest`, `results.py selftest`, `tickets.py selftest` and `dispatch.py selftest` each exit 0, and a verifier result with Verdict `pass` beside a held or failed criterion line is rejected by results validation while an old pass result and an old fail result still validate unchanged.
- Routing: in a throwaway repo, a step whose verified result holds one criterion as `unmet-dependency <subject>` gets next action `wait` from `steps.py next`, never a rebuild or replan, and `steps.py open --explain` names the held criterion; once the subject is met the action is `reverify`.
- Premature closure: in the same throwaway repo, `tickets.py close` for that ticket exits non-zero and writes nothing, with `--reason` and with `--force`; after a settling result exists the close goes through.
- Deferred-to-owner: a criterion `deferred <owner>` is closed by the owner's settling result and not by the builder's.
- `python3 plugins/sdlc-lite/scripts/check.py`, `claude_roles.py generate --check`, `codex_roles.py generate --check` and `tickets.py check` exit 0; `git diff --check` is clean and the added lines hold no em or en dashes.
- The design deviations in section 10 of docs/specs/sdlc-lite/verifier-held-criteria.md are real: the `#k` ordinal counts bullet lines, and `fanout.py land` stops a held lane with `verifier fail (held ...)`. Report both as confirmed or not; they do not fail the ticket.

## Closed

2026-10-09: delivered by the solo agent (level L2); verified pass by an independent L3 verifier
