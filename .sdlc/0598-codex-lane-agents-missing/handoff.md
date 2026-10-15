---
id: T-0598
title: "Codex verifier in a fresh lane refuses: the lane has no .codex/agents"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A Codex verifier step runs in a lane that `lanes.py open` just made, without a hand-run `codex_roles.py install` in the lane first. A test that failed before the fix passes after it.

## Repro
1. In a repo onboarded with `codex_roles.py install <repo>` (the generated `.codex/agents/` are git-ignored), file an L1 ticket, claim it, and run `lanes.py open <name> --kind solo --ticket <id>`.
2. In the lane: `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent bash <plugin>/scripts/run.sh verifier L1 .sdlc/<slug>/handoff.md`.

## Expected
The runner writes `verifier-L1.request.json` and waits, as `solo_run.py run --backend codex` does in the same lane.

## Actual
Exit 2 before any request: `agents missing or stale: sdlc-archaeologist-l1.toml, ... .gitignore; run python3 ".../codex_roles.py" install "<lane>" and start a fresh Codex chat.`

## Context
Found by the T-0570 live run (codex-cli 0.162.1, full access), report `docs/reports/2026-10-15-codex-live-lane.md`. `codex_roles.py install` ignores every file it writes, so a new worktree never has them; `solo_run.py` does not check, `run.sh` does. Guess: either `lanes.py open` installs the agents in a Codex lane, or `run.sh` checks the main checkout that holds the session's catalog. Running the install in the lane made the retry pass.

## Constraints
The failing test lands before or with the fix, never after.
