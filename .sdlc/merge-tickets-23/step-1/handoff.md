# Handoff: merge tickets-23 into main

## Goal
Merge branch `tickets-23` (T-0119..T-0139 follow-ups) into main, which already holds batch 22 (T-0105, T-0141, T-0132, T-0110, 0.14.0). Both batches edited the same prompts and scripts; keep both sides' intent.

## Context
Conflicts on a trial merge: .claude/agents/sdlc-lite-author.md, .sdlc/roadmap.md, CLAUDE.md, plugins/sdlc-lite/agents/planner.md, plugins/sdlc-lite/agents/verifier.md, plugins/sdlc-lite/scripts/run-selftest.sh, plugins/sdlc-lite/scripts/run.sh, plugins/sdlc-lite/skills/ticket/SKILL.md.
- `.sdlc/roadmap.md` is generated: resolve it by running `python3 plugins/sdlc-lite/scripts/tickets.py roadmap` after the other files are resolved, never by hand.
- In prompts (planner.md, verifier.md, SKILL.md, CLAUDE.md, sdlc-lite-author.md), keep both sides' rules. Where both sides renumber a list, keep every rule once and number them in order.
- In run.sh and run-selftest.sh, keep both sides' behavior and every selftest case. main's T-0105 Bash timeout floor (at least 3600000 ms) and result-event pick stay.
- Do not bump the plugin version; the merger does that after.

## Step 1: Merge tickets-23
level: L3
### Do
Run `git merge --no-ff tickets-23` on a tree with no uncommitted tracked changes. Resolve every conflict so both lanes' intent survives, run the gates below, and create the merge commit. Never push.
### Acceptance criteria
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`
- `git merge-base --is-ancestor tickets-23 HEAD`
- (guard) `! git rev-parse -q --verify MERGE_HEAD`
- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check` exits 0.
