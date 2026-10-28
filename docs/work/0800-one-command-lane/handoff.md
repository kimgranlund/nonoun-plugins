---
id: T-0800
title: "one command opens and one finishes a solo lane: claim, record from the transcript, prune, land, close, background backup"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor runs a solo lane with two plugin commands instead of a hand-made script chain: one opens it (claim, commit, lane), one finishes it (record the verifier from its transcript, prune, land, close, backup in the background).

## Intent
- Do: `lanes.py open --claim` claims the ticket, commits the claim and opens the lane in one call. `lanes.py finish` gains `--verifier-agent-id <id>` (and `--solo-agent-id <id>`), which finds the sub-agent transcript, derives tokens, tool uses and duration from it, records the verifier result (as `dispatch.py record` does) and prunes it before landing. `--backup` pushes in a detached background process and prints the log path, so finish does not wait on the push. Update the conductor and fanout guidance that names the old sequence.
- Non-goals: changing land, close or gate behavior; changing what a record holds.
- Done when: the acceptance criteria below pass.

## Context
Evidence (2026-10-28 retro and this session): verifier spend is 53% of sdlc-lite ($266.98 of $499.84), 50% of agent-ui ($546.32 of $1094.69), 28% of maison; on L1 and L2 solo tickets the verifier often took as long as the build (T-0796 build about 25 min, verify 21 min; T-0798 about 8 and 10 min). Analysis: the conductor's answer on 2026-10-28 ("make sdlc as fast as a single session"), theory 1 and 3.
Today the maintainer conductor runs session scripts `open.sh` (tickets.py claim, git commit, lanes.py open), `prep.sh` (dispatch.py prepare verifier), `rec.sh` (reads the transcript JSONL for tokens, tool uses, duration and the last text, then `dispatch.py record`), and `fin.sh` (rec.sh, `dispatch.py prune --done`, `lanes.py finish --transcript --verifier-transcript --backup`). One backup push took over 600 s in the foreground on 2026-10-25. Code: `plugins/sdlc-lite/scripts/lanes.py` (open, finish), `dispatch.py` (record, prune). Guidance: `plugins/sdlc-lite/agents/conductor.md` "How you run roles", the fanout skill.

## Acceptance criteria
1. A lanes selftest case: `open --claim` on a proposed ticket leaves it claimed in a commit and the lane open; reverted, the case fails (state the FAIL line).
2. A lanes selftest case: `finish --verifier-agent-id` with a fixture transcript records the verifier result with tokens, tool uses and duration taken from the transcript, prunes it, then lands; reverted, it fails.
3. A selftest case: `finish --backup` returns before the push completes and prints the background log path.
4. lanes and dispatch selftests through gate_lock exit 0, `check.py` exits 0.

## Constraints
The failing tests land before or with the change.
