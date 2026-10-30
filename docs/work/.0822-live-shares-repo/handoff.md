---
id: T-0822
title: "Live agent works as a worker beside a factory session"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0819, T-0821]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: sdlc-lite-author 2026-10-30
branch: lane/T-0822-t0822
worktree: ../sdlc-lite.worktrees/T-0822-t0822
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc/agents/live.md` says how a live session works when a factory session is active in the same repo, and `agents/factory.md` says how the factory lands a live lane.

## Context
- Design agreed with the user on 2026-10-30: with a factory session in the repo, a live session works as a worker in its own lane; the factory stays the only writer of main (the "Hosts in one repo" bullet of `plugins/sdlc/AGENTS.md`). Builds on the renamed tree (T-0819; plugin `sdlc`, agents `sdlc:factory`, `sdlc:live`, `sdlc:hybrid`).
- Helpers from T-0821: `lanes.py who`, `lanes.py list --overlap`, `lanes.py finish --no-ticket`.

## Do
1. `live.md`, new section `## Sharing a repo with a factory`: before the first edit run `lanes.py who`; when it names a factory, open `lanes.py open live-<slug> --no-claim` and work only in that worktree; claim a ticket when the work matches one; run `lanes.py list --overlap <paths>` before editing and tell the user about any overlap; when done run `lanes.py ready`; after a factory land notice, rebase the lane. With no factory, work on main as before.
2. `factory.md`: a live lane that reports ready is landed with `lanes.py finish <lane> --no-ticket`; after each land, send one land notice to any live session's mailbox.
3. Regenerate the Codex agents.

## Acceptance criteria
- `grep -q '^## Sharing a repo with a factory' plugins/sdlc/agents/live.md`
- `grep -q 'finish .*--no-ticket' plugins/sdlc/agents/factory.md`
- `python3 plugins/sdlc/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc/scripts/check.py` exit 0.

## Outcome

2026-10-30 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: 52d914bd02c8
- Changed: see commits
- Commits: 6ffbf72 T-0822: live agent works as a worker beside a factory; 4307dbd T-0822: record lane T-0822-t0822
- Check: 1 `grep -q '^## Sharing a repo with a factory' plugins/sdlc/agents/live.md`: pass
- Check: 2 `grep -q 'finish .*--no-ticket' plugins/sdlc/agents/factory.md`: pass
- Check: 3 `codex_roles.py generate --check` and `check.py` exit 0: pass
