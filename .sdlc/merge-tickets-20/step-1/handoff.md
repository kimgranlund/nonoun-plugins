# Handoff: merge tickets-20 into main

## Goal
Merge branch `tickets-20` (17 finished tickets: T-0092..T-0118 follow-ups) into this branch, which already holds batch 21 (T-0123..T-0126, 0.12.0). Both batches edited the same docs and scripts; keep both sides' intent.

## Context
Conflicts on a trial merge: .claude/agents/sdlc-lite-author.md, .sdlc/.0105-find-out-why-the-t/handoff.md, .sdlc/roadmap.md, CLAUDE.md, plugins/sdlc-lite/agents/conductor.md, plugins/sdlc-lite/scripts/check.py, plugins/sdlc-lite/scripts/fanout.py, plugins/sdlc-lite/scripts/steps.py, plugins/sdlc-lite/skills/chain/SKILL.md.
- `.sdlc/roadmap.md` is generated: resolve it by running `python3 plugins/sdlc-lite/scripts/tickets.py roadmap` after the other files are resolved, never by hand.
- For `.sdlc/.0105-find-out-why-the-t/handoff.md`, keep every section from both sides (the ticket body plus the evidence note added on main).
- In code files (steps.py, fanout.py, check.py), keep both sides' functions, lint rules, and selftest cases; where both edited the same list or dict, take the union.
- Do not bump the plugin version; the merger does that after.

## Step 1: Merge tickets-20
level: L3
### Do
Run `git merge --no-ff tickets-20` on a tree with no uncommitted tracked changes. Resolve every conflict so both lanes' intent survives, run the gates below, and create the merge commit. Never push.
### Acceptance criteria
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`
- `git merge-base --is-ancestor tickets-20 HEAD`
- (guard) `! git rev-parse -q --verify MERGE_HEAD`
- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check` exits 0.
