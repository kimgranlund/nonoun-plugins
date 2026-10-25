---
id: T-0779
title: "The host-lane solo brief says which criteria the sandbox blocks"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The host-lane solo brief tells the solo that its sandbox refuses git and any Bash command with a quoted argument, so a criterion needing either is reported `not run (host sandbox)` for the verifier to run, instead of being rewritten or skipped silently.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: T-0002 `Criterion 3 (git diff against the base sha): not run, the sandbox refuses git.`; T-0001 `The worktree sandbox refused the quoted command ("too complex to verify")`; T-0003 wrote its own runner `.sdlc/runtime/tasks/add-div/criteria.py`. The verifier runs outside the host sandbox and runs them verbatim.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`SOLO_SUBAGENT_PROMPT` in `plugins/sdlc-lite/scripts/fanout.py` now tells the host-lane solo that the sandbox refuses a Bash command with a quoted argument (and git), and to report such a criterion as `<exact command> not run (host sandbox)`, never rewritten, for the verifier to run. `results.py solo_report_error` accepts that line in place of `exit <n>` beside `verify: needed`. Docs: `docs/references/sdlc-internals.md`.
- Red: fanout selftest case 30d with the brief sentence removed fails: `case 30d host brief: it names the sandbox limits and the `not run (host sandbox)` report line, got ...`; results selftest with the regex change reverted fails: `MISS: T-0779: a span reported not run (host sandbox) beside verify: needed passes`.
- Green: `fanout.py selftest` PASS, `results.py selftest` PASS, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check e8490aab` exit 0.
