---
id: T-0667
title: "record --agent-id reads the final message from the transcript"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor records a role with `dispatch.py record --agent-id <id> <dispatch.json>` and nothing on stdin, and never scrapes a transcript by hand: the docs say `record` reads the result itself, and a selftest proves it.

## Intent
- Do: (1) Add a `dispatch.py` selftest case: CLI `record --agent-id <id>` with no result file, stdin from /dev/null, and a transcript at `<projects>/*/*/subagents/agent-<id>.jsonl` (via `SDLC_CLAUDE_PROJECTS`) writes the result from the transcript's last assistant message and exits 0; with an id that has no transcript it exits 2 `no result yet`. (2) Rewrite `agents/conductor.md` "How you run roles" step 3 and the record sentence in `skills/chain/SKILL.md:20`: run `record --agent-id <id>` with the notice figures; stdin is optional and only for a role whose transcript is missing; never extract the final message yourself. (3) Mention the same in `skills/fanout/SKILL.md` where it records a role.
- Non-goals: code changes to `record` beyond the selftest (the mechanism exists). Codex `run.sh`.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #27, ui-kit-neue audit 2026-10-20.
- Evidence: 33 hand-written transcript-scraping snippets in one 0.27.0 conductor session, against `agents/conductor.md:41`.
- Already implemented in this repo: with `--agent-id` and no `--transcript`, the CLI finds the transcript (`plugins/sdlc-lite/scripts/dispatch.py:1872-1873`, `find_subagent_transcript` at `dispatch.py:1469`, T-0446), and `record` takes the result from the transcript's last assistant message when the file and stdin are empty (`dispatch.py:1544-1560`, T-0343, refusing a `max_tokens` stop). The gap is the docs: `agents/conductor.md:41` says "pipe its final message to `record` on stdin (a quoted here-doc)", and `skills/chain/SKILL.md:20` says "with the sub-agent's final message on stdin", so conductors scrape the message to feed stdin.
- Existing coverage: the T-0343 case at `dispatch.py:3240-3253` uses `--transcript`; the T-0446 cases at `dispatch.py:3173-3197` use `--agent-id` but write the result file first. No case runs `--agent-id` alone with no file and no stdin.
- T-0645, T-0646 and T-0659 also edit `conductor.md:41` or `chain/SKILL.md`; do not run them in the same wave.

## Constraints
`record` behavior and exit codes are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case named `record --agent-id alone reads the result from the found transcript`. It passes before any script change (this confirms the mechanism); its negative control, the same call with an id that has no transcript, exits 2 and prints `no result yet`.
2. `grep -n 'quoted here-doc' plugins/sdlc-lite/agents/conductor.md` finds nothing, and `grep -n 'record --agent-id' plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/skills/chain/SKILL.md` finds a line in each.
3. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome
- Added the `dispatch.py` selftest case `record --agent-id alone reads the result from the found transcript` and its negative control (an id with no transcript exits 2, `no result yet`, no result written). Both pass with no `record` change, confirming the T-0446/T-0343 mechanism.
- Rewrote `agents/conductor.md` "How you run roles" step 3, `skills/chain/SKILL.md:20` and the `advance` sentence in `skills/fanout/SKILL.md`: `record --agent-id <id>` with the notice figures, nothing on stdin, stdin only for a role whose transcript is missing, never extract the final message. Regenerated `adapters/codex/agents/sdlc-conductor-l1.toml`.
- Left open (out of scope): 13 other skills still say "with the sub-agent's final message on stdin" (build, fix, agent, architect, dig, file, scout, research, verify, bench, fleet-retro, review-traces, plan/references/steps.md); a follow-up ticket should align them.
- Checks: selftest exit 0, check.py exit 0, `git diff --check` exit 0, `check-packaging.py` exit 0.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 67123bd857b3
- Changed: see commits
- Commits: ffd2ee5 T-0667: record --agent-id reads the final message from the transcript
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case `record --agen...: pass
- Check: 2 `grep -n 'quoted here-doc' plugins/sdlc-lite/agents/conductor.md` finds nothing, and `grep -n 're...: pass
- Check: 3 `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/skills/build/SKILL.md and 12 other skills fix... -> notes.md
- Follow-up: note: the scratch dir... -> notes.md
