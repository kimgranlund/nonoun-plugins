---
id: T-0778
title: "settle names the push and the leftover host branches"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After settle moves main, it prints the next steps a sub-agent fanout needs: `git push origin main` before the next prep (T-0756 refuses an unpushed base) and a `git branch -d` line for each landed `worktree-agent-*` branch it leaves.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: round 2 prep refused (`base ... is not on origin/main ... push it first`) because settle had fast-forwarded main locally; settle and sweep left `worktree-agent-a0c9e143dcc776478`, `worktree-agent-a6133857ac30d72e1`, `worktree-agent-a098b45af8ca1f151` in place. Print the lines; never push or delete branches itself.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`fanout.py settle` now ends with a `next:` line naming the remote update for the branch (only when the branch is ahead of its remote default) and one `git branch -d worktree-agent-<id>` per landed host branch still present, when host lane records (worktree-agent-*) point into the integration branch and settle moved the branch. Both exit-0 paths print them; nothing is sent to the remote or deleted. Selftest cases `T-0778` (3 cases) cover the full close, no host lane (no lines), and a kept integration with a landed and an unlanded host branch. Negative control: with the print neutralised the selftest exits 1 and lists both T-0778 host-lane FAIL lines. Checks: fanout selftest, check.py, check-packaging.py, `git diff --check 34c60d88` all exit 0. Docs: fanout.py header and `skills/fanout/references/main.md`.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 34c60d88f86f
- Changed: see commits
- Commits: 780b171 T-0778: settle names the next steps after a host fanout
- Check: 1 A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fa...: pass
- Check: 2 gate_lock fanout selftest exits 0, check.py exits 0, check-packaging.py passes, `git diff --check...: pass
- Follow-up: note: plugins/sdlc-lite/hooks/block-publish.sh:29 matches git push text... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:3270 compares only against... -> notes.md
