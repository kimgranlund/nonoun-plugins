---
id: T-0428
title: "Close-first doctrine: builders, solo and conductor lean toward closing and merging, not layered verification"
type: chore           # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Roles lean toward closing tickets, answering requests and merging lanes, and stop at "done and checked once" instead of auditing the checks.

## Intent
- Do: change the role wording in plugins/sdlc-lite/agents/ (builder.md, solo.md, verifier.md, planner.md, plan-reviewer.md, conductor.md; never the generated `*-L<n>.md`), then run claude_roles.py generate and codex_roles.py generate. Say it once, short, in each role's own terms, no copied block: (1) the goal of a role is a closed ticket and a merged lane; the default after a pass is to close and merge, not to look for more to check; (2) builder and solo: run the checks the handoff names, once, fix what fails, report, stop; do not add criteria, do not re-run a green check, do not widen to "be safe"; (3) verifier: judge only the criteria in the handoff against the built tree, one pass; a pass is final; never spawn or request another verifier on your own report; a defect in the handoff itself (a Done-when that contradicts Non-goals, a criterion that can only pass after your own verdict) is a `plan defect`, reported once, not a fail that restarts the chain; (4) planner and plan-reviewer: a plan that is a mechanical copy of a passed plan is checked as a diff, once; a cosmetic finding is noted, not a replan; (5) conductor: after a verifier pass, close the ticket and merge the lane in the same turn, then run the lane sweep; no reverify of a pass unless a verified file changed since; count agent runs on a step and stop and ask the maintainer at the cascade cap (T-0427 sets it; until then 6). Keep each role file's length near what it is today; cut a sentence when you add one.
- Non-goals: changing models, efforts or levels; dropping the ticket-close verifier; hooks or scripts.
- Done when:
  - The wording above is present once per role (grep for a short fixed phrase per role, listed in the report), generated copies and Codex TOMLs regenerated, claude_roles.py and codex_roles.py generate --check, check.py and tickets.py check pass; no dashes.
  - A focused live run in a throwaway project is reported (a small solo ticket and a deliberately imperfect plan), or listed unverified with the reason; AGENTS.md requires it for a role behavior change.

## Context
Maintainer direction 2026-10-10: tune builders and agents toward closing issues and requests and merging worktrees, and away from verifying things that do not need verification yet; "a cancer to be avoided at all cost". Evidence: planning and plan review was 53 percent of agent-ui spend before any code (collector, 2026-10-09); maison counted 11 agent runs on T-0378 steps 1 and 2 and two plan reviews per copied plan (maison report, 2026-10-10); verifier minutes 43 to 56 each (ultimate-tokens). Decision: doctrine plus hard caps; hard caps are T-0427. Philosophy line in plugins/sdlc-lite/AGENTS.md: done is better than perfect.

## Constraints
No em or en dashes. No push or publish. Model and effort defaults are the maintainer's: change none. Independent verification at ticket close stays; this ticket removes layers above it, not that verifier.

## Acceptance criteria
- Each role file carries its close-first wording once: `grep -c -F "The goal is a closed step" plugins/sdlc-lite/agents/builder.md` and the same count of 1 for "Your goal is a closed ticket" in solo.md, "a pass is final" in verifier.md, "mechanical copy of a passed plan" in planner.md and plan-reviewer.md, and "close the ticket and merge the lane in the same turn" in conductor.md.
- Generated agents are current: `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
- Repo checks pass: `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0, and `git diff --check` exits 0.
- No em or en dashes were added: `git diff -U0 | grep '^+' | grep -c '[—–]'` prints 0 for the changed agent files.
- Only role wording changed: no edit to levels.json, models.json, hooks or scripts.

## Closed

2026-10-10: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
