---
id: T-0378
title: "Record required red checks before a builder implements, and record a deviation when a run lacks them"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder run records its tagged `(red)` criteria before it edits source, and a completed run without that checkpoint records a process deviation instead of passing silently.

## Intent
- Do: inspect agents/builder.md, scripts/specgate.py, scripts/run.sh and the Codex native exchange, and reuse the existing red-control facility where it applies. Record the exact handoff criterion, base sha, command, exit and timestamp before new implementation changes, bound to the current attempt and the handoff content hash. A criterion already green on the baseline is surfaced, not called a successful red control. A resumed build distinguishes a preserved original red checkpoint from a retrospective base control. A completed run missing the checkpoint records a process deviation; do not infer ordering from a final report or a later baseline run. Keep three things distinct in the record: runner format acceptance, builder test success, and independent verification. State per host whether enforcement is procedural or mechanically guaranteed: on Claude a hook could enforce it, on Codex no hook exists, so say procedural and do not invent a Codex hook.
- Non-goals: model or effort changes; resetting other agents' work; changing any repo's implementation; claiming red-before-edit for the observed run.
- Done when:
  - Tests cover: no tagged criteria, valid pre-edit controls, missing evidence, post-edit retrospective controls, and resumed work with evidence from an earlier attempt (observed failing first).
  - A run that completes without the checkpoint writes a process-deviation line that the verifier handoff and the filer read.
  - check.py, tickets.py check, the affected selftests, codex-selftest and both generate --check pass.

## Context
Idea forwarded by the maison conductor from Codex, 2026-10-08 (maison's T-0287; copy at the maison repo .sdlc/tickets/0287-codex-builder-red-checkpoint/handoff.md, reporter priority P2, budget 30 USD). Evidence: T-0152 step 9 fix pass in maison: a native sdlc-builder-l4 implemented items 9 to 11 and ran green checks before running either `(red)` command on the base; it disclosed this; both commands then failed on a clean base snapshot and passed on the changed tree, which shows the tests discriminate but cannot show red-before-edit ordering. Files there: .sdlc/tickets/0152-manifest-driven-renderers/step-9/{builder-L4.md,native-base-controls.md,builder-L4.attempt.json}, branch codex/0152-s9, base 5a096cc72, fix 512e3ec7. Independent Claude L3 verification of that step was running; its finding is not in this ticket. Related: T-0366 and T-0376 (base sha), which the checkpoint depends on for the recorded base.

## Constraints
No em or en dashes. No push or publish. The Codex host cannot be run live here; mark live Codex behavior unverified.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/redck.py selftest | tail -n 1 | grep -qx "redck selftest: PASS"`
- `out=$(python3 plugins/sdlc-lite/scripts/redck.py selftest) && for k in "no tagged criteria" "valid pre-edit control" "missing evidence" "post-edit control" "resumed work" "a handoff changed after the original checkpoint" "an unbound control"; do printf '%s\n' "$out" | grep -qF "ok: $k" || exit 1; done`
- `python3 plugins/sdlc-lite/scripts/check.py >/dev/null && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check >/dev/null && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check >/dev/null && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check >/dev/null`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n 1 | grep -qx "steps selftest: PASS" && python3 plugins/sdlc-lite/scripts/specgate.py selftest | tail -n 1 | grep -qx "specgate selftest: PASS" && python3 plugins/sdlc-lite/scripts/dispatch.py selftest | tail -n 1 | grep -qx "dispatch selftest: PASS" && python3 plugins/sdlc-lite/scripts/codex-selftest.py >/dev/null`
- A builder that completes through `dispatch.py record` with a `(red)` handoff criterion and no `redck.py record` leaves `process-deviations.md` beside the handoff holding a `process deviation: red-checkpoint: missing` line: `grep -n "redck.py" plugins/sdlc-lite/scripts/dispatch.py plugins/sdlc-lite/scripts/run.sh` shows the audit call in both, and `agents/verifier.md` and `agents/filer.md` name `process-deviations.md`.
- `agents/builder.md` rule 11 tells the builder to run `redck.py record` before the first edit and states that enforcement is procedural; `scripts/redck.py` states per host (Claude hook possible but not registered, Codex no hook, live Codex unverified) and keeps runner acceptance, builder checks, and independent verification as separate records.
- No em or en dash in the lines added to the hand-edited files or the new script: `! git diff -U0 -- plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/filer.md plugins/sdlc-lite/scripts docs/references/sdlc-internals.md | grep '^+' | grep -qF -e "$(printf '\342\200\224')" -e "$(printf '\342\200\223')" && ! grep -qF -e "$(printf '\342\200\224')" -e "$(printf '\342\200\223')" plugins/sdlc-lite/scripts/redck.py`

## Closed

2026-10-08: Merged and verified pass in .sdlc/verify-0.22-batch3/verifier-L3.md; shipped in v0.22.0
