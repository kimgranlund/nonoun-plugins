---
id: T-0551
title: "Builders run the step's own checks, not the full check.sh, when the land gate runs it anyway"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder runs the checks its step's acceptance criteria name, plus the narrow suites the change touches, and does not run the full `check.sh` when the land gate (fanout `--gate`, `/chain` final verify) runs it anyway.

## Intent
- Do: change the builder contract (and its generated variants) so the full `check.sh` is run only when a criterion names it or the step is the ticket's last step with no land gate; otherwise the builder runs the named criteria and the touched suites. Same review for solo where a verifier and a land gate follow.
- Non-goals: removing `check.sh` from any verifier or gate; changing what the land gate runs.
- Done when: the contract says so, `claude_roles.py generate --check` and `check.py` pass, and one lane run in a throwaway project shows a builder step finishing without a full `check.sh` while the land gate still runs it.

## Context
Maintainer request 2026-10-14 ("proceed 1-4" on the slow-lane analysis). T-0543 wave 70: step 3 builder took 50 min, about 47 of it a full `check.sh` (normally 18 min) on an overloaded machine (load average 54 on 20 cores); step 2's verifier and the land gate ran it again. Run records: `.worktrees/fanout70/d/.sdlc/runtime/tasks/0543-close-writes-outcome/runs.jsonl`.

## Constraints
A step whose criterion names `check.sh` still runs it.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `grep -c 'Run the full .check.sh. only when a criterion names it' plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/solo.md` prints 1 for each file.
- Live: one lane run in a throwaway project shows a builder step finishing without a full `check.sh` while the land gate still runs it (maintainer run; not done by solo).

## Outcome

2026-10-14 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: none
- Changed: see commits
- Commits: none
- Check: 1 `claude_roles.py generate --check` exits 0: pass
- Check: 2 `codex_roles.py generate --check` exits 0: pass
- Check: 3 `check.py` exits 0: pass
- Check: 4 grep -c prints 1 for builder.md and solo.md: pass
- Follow-up: decide: Throwaway worktree and scratch under the tmp prefix were removed... -> notes.md
