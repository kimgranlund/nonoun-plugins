---
id: T-0827
title: "Live mode picks a branch and a lane, and cleans up after merge"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: nonoun-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc/agents/live.md` says which branch and which checkout a live session works in when it is alone in the repo, and how it cleans up, and its gate rule names a path that exists in a consumer repo.

## Context
- Agreed with the user on 2026-10-30: one ticket for agent text, no new hook.
- Today `live.md` gives branch and worktree rules only beside a factory (`## Sharing a repo with a factory`); alone it edits whatever branch the session opened on, so in a repo that lands through pull requests (main tracks a remote) its commits land on local main.
- Lane helpers: `lanes.py open <name> --no-claim`, `lanes.py ready`, `lanes.py close <name>`; worktree root rule: `wtroot.py root` (the Lanes section of `plugins/sdlc/AGENTS.md`).
- The rule "Heavy gates ... run through `scripts/gate_lock.py`" lacks the plugin root; the `lanes.py who` line uses `${CLAUDE_PLUGIN_ROOT}/scripts/`.

## Do
In `agents/live.md`, keeping it short:
1. On the first edit, when the repository lands through pull requests (main tracks a remote and `.sdlc/config` has no `lane_landing: local`) or the user asks for a branch, create and work on `live/<slug>`; otherwise stay on the current branch.
2. A second task in parallel gets its own lane (`lanes.py open live-<slug> --no-claim`); two tasks never share one checkout. Worktrees live under the root `wtroot.py root` prints.
3. After the user merges a live branch or lane, close it with `lanes.py close <name>`; never delete an unmerged branch.
4. Fix the gate rule path to `${CLAUDE_PLUGIN_ROOT}/scripts/gate_lock.py`.
Regenerate the Codex agents.

## Acceptance criteria
- `grep -q 'live/<slug>' plugins/sdlc/agents/live.md && grep -q 'lanes.py close' plugins/sdlc/agents/live.md`
- `grep -q 'CLAUDE_PLUGIN_ROOT}/scripts/gate_lock.py' plugins/sdlc/agents/live.md`
- `python3 plugins/sdlc/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc/scripts/check.py` exit 0.
