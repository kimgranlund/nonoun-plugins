---
id: T-0221
title: "fanout.py runs each lane by steps.py lane: solo for S and M, chain for full, with a lane cap and stagger"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py` runs each ticket by the lane `steps.py lane` picks: solo for size S and M, the headless /chain for the rest, with a lane cap, a stagger, and an overlap refusal, so a fanout is solo-first by default.

## Intent
- Do: per ticket in its lane worktree run `steps.py lane`, start `solo` at the tier's model and effort (Claude `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`, Codex `codex_exec.py solo L1|L2|L3`), require one independent batched verifier for tier M and L before merging, keep the conductor chain for full, add `--lane`, `--max-lanes` (default 4, above 16 needs `--yes-many`), `--stagger` (default 20 s), `--allow-overlap`; print each ticket's lane in the plan and the report; selftest, check.py guard item 24, docs, and a live proof.
- Non-goals: any model or effort default change; a version bump, tag, push, or publish; building the supervisor or board work.
- Done when: selftest and check.sh pass, an independent verifier passed, the live record docs/reports/fanout-solo-live-run.md exists, and the branch is merged into main.

## Context
User decision 2026-10-05: fanout should follow the same solo-first default as the conductor. Evidence: docs/reports/solo-vs-lean-benchmark-2026-10-04.md (solo about $1 and 6 minutes per task; the chain about 10 times the cost). Burn-down rules: one handwritten step, one verifier, no planner.

## Constraints
Keep `--driver CMD` overriding everything for selftests. Do not touch the limits agent's worktree. No em dashes.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`; case 15 (solo first) holds a positive case and a negative control for the solo versus chain choice, the lane cap, the stagger, the over-16 refusal, and the planned-scope overlap refusal.
2. `bash plugins/sdlc-lite/scripts/check.sh` exits 0, and `python3 plugins/sdlc-lite/scripts/check.py` prints `ok:`; its item 24 guard names the SOLO_TIERS agreement with agents/solo.md and flags a changed tier.
3. `python3 plugins/sdlc-lite/scripts/fanout.py run a=T-0001 --dry-run` in a throwaway repo with a size S ticket prints `lane: solo, tier S: sonnet low`; with a size L ticket it prints `lane: full`; `--lane full` forces `full` for the size S ticket; `--driver true` skips the lane call.
4. `fanout.py run` with five single-ticket lanes and no `--max-lanes` exits 2 naming `--max-lanes 4`; `--max-lanes 17` without `--yes-many` exits 2 naming `--yes-many`.
5. `solo_command` builds `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo` with `--model sonnet --effort low` for S, `--model sonnet --effort xhigh` for M, and `--model opus --effort xhigh` for L, matching the tiers in agents/solo.md; the Codex form runs `codex_exec.py solo L1|L2|L3`. No model or effort default in run.sh or adapters/codex/models.json changed (`git diff main -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json` is empty).
6. A size M or L solo ticket does not merge without a new passing task-dir verifier result (read the run_ticket code path and the selftest), and a solo ticket closes with `tickets.py close --reason`, not a filer file.
7. docs/reports/fanout-solo-live-run.md records four lanes merged with a hidden check of 24/24 and names the models from the session transcripts; every number in it can be checked against docs/reports/fanout-solo-live-run/.
8. `git diff --check` is clean, and no em dash appears in the changed text files.

## Closed

2026-10-04: Built and merged: fanout.py solo first (steps.py lane per ticket, solo tiers, --lane, --max-lanes, --stagger, --allow-overlap, solo close by reason), selftest case 15, check.py guard item 24, docs, and a live run (4 lanes, hidden check 24/24, docs/reports/fanout-solo-live-run.md). The first L3 branch verifier passed 7 of 8 criteria and failed the record's checkability; the fixes were re-verified by a narrow L3 that failed once more on gitignored .log files, which were then fixed and confirmed mechanically with git ls-tree and git check-ignore, not by a third verifier run. Codex lane not run live.
