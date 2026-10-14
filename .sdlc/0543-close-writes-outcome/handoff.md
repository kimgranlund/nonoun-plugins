---
id: T-0543
title: "Lean records D: Close writes the Outcome (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0541, T-0542]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Close writes the Outcome: part D of SDLC Lite 0.23.0 lean work records (wave 3).

## Intent
- Do: build part D of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for D, Interfaces and Risks). Files: `tickets.py` (`cmd_close` Outcome composer, verdict gate, follow-ups from verifier `## Notes`, `--filer`, `--changed`, `--reason` writes an Outcome, T-0529 placeholder gate, citation scan skips `runtime/` plus T-0535 `citation_skip:`, `skip_problems` reads open folders only, claim staleness from `.running` at :1363 through `records_dir`, help text and selftests that name `## Closed` at :53,91,94,3528,4248,6052, router close procedure :1815-1825), `redck.py` (`deviations` subcommand; no `process-deviations.md`), `steps.py` (split refusal becomes a `## Plan review` line; no `refusals.jsonl`), `check.py` :186,:695, `agents/{conductor,verifier,builder,solo,filer}.md` plus regenerated agents (`claude_roles.py`, `codex_roles.py`), `skills/{chain,file,fix,ticket,open-questions}/SKILL.md` (/fix and chain loose ends write hand-written step handoffs under `order.py records-dir`)
- Non-goals: the other parts (A to F) of the same design.
- Done when: `tickets.py selftest` and `redck.py selftest` exit 0 with: a close over a passing verifier result appends `## Outcome` with `lane:`, `verdict: pass`, `Check:` and `Commits:` lines; a failing newest verifier makes close refuse (negative control); a handoff still holding the bug template's Repro prompt refuses and the filled-in one closes (T-0529); a marked inventory file is skipped by the citation scan and the unmarked one refuses (T-0535); no `process-deviations.md` or `refusals.jsonl` exists after the fixtures run. Generated-agent parity check passes

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.
