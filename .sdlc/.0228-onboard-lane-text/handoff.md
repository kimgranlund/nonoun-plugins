---
id: T-0228
title: "onboard.py's root entry block still routes work to chain and fix, not solo"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The managed block that `onboard.py setup` writes into a consumer repo's root AGENTS.md routes work by the current lane rule (solo by default for size S and M), not only to /chain, /fix and /build.

## Intent
- Do: change the template line at plugins/sdlc-lite/scripts/onboard.py (line 249: "Plan, build, and verify work runs through SDLC Lite: /sdlc-lite:chain, /sdlc-lite:fix, or /sdlc-lite:build ...") to say: pick the lane first with `steps.py lane <task dir>`; solo is the default for size S and M (start it as agents/solo.md says); /fix only when asked or the lane script prints fix; the full chain (/sdlc-lite:chain) only with a stated reason; keep "Do not spawn another plugin's builder, planner ..." intact. Bump the managed block version so existing consumers see their block as stale (check how onboard.py versions blocks; the 0.20.2 note says bumping must not make every existing consumer's block unmanageable: follow the existing stale/edited/current rules and test them), update the onboard selftest, docs/specs/repo-onboarding/design.md if it quotes the line, and the maison repo is the first consumer (do not edit maison; run onboard.py check there read-only to confirm it reports stale).
- Non-goals: other onboarding text; model or effort defaults; a version bump, tag, push, or publish.
- Done when: setup writes the new line in a throwaway repo, check reports a repo with the old block as stale, a hand-edited block is still reported edited (not overwritten without --force), the selftest has a negative control, and an independent verifier passed.

## Context
Found while building T-0227 (root AGENTS.md orientation): the consumer block contradicts the lane rule this repo now ships. Goes in 0.20.8. Size S, solo lane. Philosophy: "Done is better than perfect."

## Constraints
One authoritative wording for the lane rule: link or mirror the root AGENTS.md section, do not invent new text. No em dashes.

## Closed

2026-10-04: Built on branch onboard-lane (3264439, validation note docs/reports/onboard-lane-text.md): the root entry block routes by steps.py lane, solo default for S and M; no template version bump (TEMPLATE_VERSION is shared with the router blocks, text difference already makes a block stale); lane-text gate with negative controls; independent L3 Fable verifier passed 5 of 5; full check.sh rc=0; maison read-only check reports AGENTS.md stale.
