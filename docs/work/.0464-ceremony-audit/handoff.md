---
id: T-0464
title: "Audit ceremony versus defects caught; rank candidate changes toward a resolve-and-ship posture"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 8
---

## Question
Which steps, warnings, skills and agent rules in SDLC Lite add ceremony without catching defects, what does each cost, what has each caught, and which small changes would move the system toward resolving and shipping without lowering quality?

## Goal
A dated report that ranks candidate ceremony cuts by measured cost and by what each step has actually caught, with a "what did it catch" count per step, and at most 5 changes marked "propose a ticket".

## Intent
- Do: (1) First named case, the filer-warning close refusal: for every closed ticket since T-0431 (`.sdlc/.NNNN-*` folders in this repo, and the sampled closed tickets of ui-kit-maison, agent-ui and ultimate-tokens, read-only), list each filer `## Warnings` entry by kind (`red-checkpoint: retrospective`, unverified claim, flake, other), whether the close was refused, how it was cleared (`--ack-warnings`, `--reason`, `--force`), whether the warning ever led to a fix, a reopened ticket or a later defect, and the minutes lost. Evidence so far, to confirm or correct: 9 of 11 filers since T-0431 carry a retrospective red-checkpoint deviation and about 6 tickets stalled a lane on a close refusal (fanout logs `/tmp/fanout-f51.log` to `/tmp/fanout-f59.log`; they are untracked, so quote the numbers you reproduce). (2) Sweep the other candidate ceremony sites with the same columns (cost, defects caught, manual acks): plan-reviewer by level, filer on solo and on chain tickets, a second verifier round, the full chain for L3, `inherited red` stops, gate-lock timeouts reported as red, replans, questions asked that did not change the output, and any skill or agent rule that tells a role to re-verify or re-run a green result. (3) Run `prompt_lint.py` over `agents/*.md`, `skills/*/SKILL.md` and `overlays/*.md` and add loop, verify and re-run wording counts as informational signals only. (4) For each candidate: the measured cost (minutes and dollars from `runs.jsonl`, `fleet_collect.py`, attempt records), the defects it caught (count, with the result path of each), the proposed change, the measure that must move, and the quality guard (K-005 first-pass rate, rework after close). Keep every check with at least one real catch; mark a removal with no recorded catch `[U]`. (5) Rank, and state what is already covered by shipped or filed work (T-0428 close-first, T-0456, T-0459, T-0446, T-0445, T-0457, T-0461, T-0462).
- Non-goals: editing any skill, agent file, script or ticket; filing the changes; removing the independent verifier; a model or effort change.
- Done when: `docs/reports/<date>-ceremony-audit.md` exists with the per-site table (cost, defects caught with pointers that resolve, manual acks), the first-case analysis, the ranked changes with at most 5 marked "propose a ticket", the quality guard for each, what is already covered, and what is unverified; the report passes `docs_check.py`; one independent verifier reproduces a sample of its counts.
- outcome metric: manual acks per wave (close refusals cleared by hand), before: about 6 tickets across waves 32 to 38 (2026-10-11)

## Context
Maintainer direction 2026-10-12: tune the system toward resolve-and-ship and away from ceremony-heavy plan, verify, build, verify loops. Posture measures proposed: ceremony ratio (plan, review, filer, re-verify and retry minutes and dollars over total), rounds to close, asks per ticket, manual acks, late failure, plus the quality guard. Evidence: `docs/reports/2026-10-11-solo-fails-and-blocks.md`, `docs/reports/2026-10-11-solo-campaign-baseline.md`, `docs/reports/2026-10-09-l4-full-chain-cost-replay.md`, `docs/reports/2026-10-10-verifier-minutes.md`, `.sdlc/.0428-close-first-doctrine/`, the filer files `.sdlc/.04NN-*/filer-L1*.md`, `docs/reports/2026-10-11-agent-prompt-lint-baseline.md`.

## Constraints
Read-only against every repo it inspects. No model or effort change. Cap $8; stop and report at it. A check that caught a real defect stays. State only what a file or command shows; mark inference `[U]`.

## Plan review
- plan defect: dispatch.py prepare builder refused step-1: steps.py lint: cited path does not exist: .sdlc/.0999-nope/ (the plan's settled-evidence line cites a probe fixture path as a code span; cite no nonexistent path in the step text)
