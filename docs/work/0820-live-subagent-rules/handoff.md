---
id: T-0820
title: "Live mode states when it uses sub-agents"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0819]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The live session agent (`plugins/sdlc/agents/live.md`, named `direct.md` before T-0819) says when it uses sub-agents: as tools for search, research, history and an independent check, never for the edit itself.

## Context
- Agreed with the user on 2026-10-30. Builds on the renamed tree (T-0819).
- Today the file has no sub-agent guidance. `hooks/block-role-spawn.sh` gates only factory sessions, so a live session may spawn any agent.

## Do
Add a short `## Sub-agents` section to `agents/live.md` with these rules:
1. Broad search: `Explore` or `sdlc:scout` when finding the code would mean reading many files; act on the conclusion.
2. Outside docs: `sdlc:researcher`; history before changing odd code: `sdlc:archaeologist`.
3. Second opinion: one `sdlc:verifier`, only on the user's request or the one offer before a risky change, through `dispatch.py prepare` and `record` (a different model family and a run record); the only sub-agent that goes through dispatch.
4. Independent side work: a background `general-purpose` agent for an unrelated question or long read while the session keeps editing.
5. Never delegate the edit: code written by a sub-agent is hybrid mode's lane. No sub-agent for anything 3 or 4 tool calls can do. Long checks run as background shell commands, not agents. Act on a sub-agent's summary; do not paste it to the user.
Regenerate the Codex agents.

## Acceptance criteria
- `grep -q '^## Sub-agents' plugins/sdlc/agents/live.md`
- `python3 plugins/sdlc/scripts/codex_roles.py generate --check` exits 0.
- `python3 plugins/sdlc/scripts/check.py` exits 0.
