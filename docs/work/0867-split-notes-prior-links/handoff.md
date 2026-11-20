---
id: T-0867
title: "After `steps.py split --supersede`, every prior-report link in a step handoff, the folded `### Notes` included"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After `steps.py split --supersede`, every prior-report link in a step handoff, the folded `### Notes` included, names the superseded folder that holds the report, so `dispatch.py prepare` does not refuse it.

## Intent
- Do: fold the plan-review notes into the step body before `rewrite_prior_links` runs.
- Non-goals: changing `rewrite_prior_links` itself or the link lint.
- Done when: the criteria below hold.

## Context
- #88: "`steps.py:2758` `body, moved = rewrite_prior_links(body, ...)` runs on the step block, then `steps.py:2761-2762` appends `### Notes` from `folded` after it. Folded notes-fix text never passes through the rewrite." Suggested fix: "fold the notes first, then call `rewrite_prior_links` on the whole body." The reporter did not reproduce the refusal on disk; the code path is confirmed at HEAD.
- `plugins/sdlc/scripts/steps.py`: the split loop is at lines 2752-2765; `rewrite_prior_links` at line 2094 skips a path that exists and rewrites `step-<n>/<report>` to the newest `step-<n>.superseded-<k>/` holding it. The supersede renames run first (lines 2747-2750), so the order fix is enough.
- Existing selftest cases that check the Notes text: around lines 7849 and 7918.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Append the `### Notes` block before the `rewrite_prior_links` call.
2. Add a selftest case: a task with `step-1/builder-L2.md`, a plan review whose `notes-fix` finding cites that path, then `split --supersede`; the new `step-1/handoff.md` Notes name `step-1.superseded-1/builder-L2.md`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/steps.py selftest` exits 0 and includes the new case.
- With the old order restored (Notes appended after the rewrite), the new case fails (state the observed red).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- The printed `steps: step N: rewrote prior-report link` lines may now include Notes links; no other output changes.
