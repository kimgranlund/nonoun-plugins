---
id: T-0859
title: "Roles run the checks for their change, once, never the full suite mid-ticket"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0858]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Builders, solos and verifiers test a change with the checks that cover it, once, and never run the full suite mid-ticket.

## Intent
- Do: reword the role and skill text about testing, and the factory's own rule about lane-time full runs.
- Non-goals: script behaviour (T-0858, T-0860, T-0861).
- Done when: the criteria below hold.

## Context
- User feedback 2026-11-19 (see T-0858). T-0858 landed `check.sh --changed [<base>]`, which runs only the jobs a diff touches.
- Text to align, in `plugins/sdlc/`: `agents/builder.md`, `agents/solo.md`, `agents/verifier.md`, `agents/factory.md`, `agents/hybrid.md`, `skills/build`, `skills/verify`, `skills/fix`, `skills/chain`, `skills/handoff-format` (how acceptance criteria name checks), and `plugins/sdlc/AGENTS.md`. The rule to state, in each role's own words: run the check a criterion names, or for this repository `check.sh --changed $SDLC_BASE_SHA`; run it once after the change, again only after a fix; do not rerun a passing check for reassurance; the full `check.sh` belongs to the land gate and a release, not to a role.
- Also `.claude/agents/nonoun-author.md` rule 11 in "Running waves" ("A ticket that changes a shared default also runs it in its lane"): change it to run `check.sh --changed` in the lane, with the full run at release. This file is the maintainer session's instructions; edit only that sentence.
- Agent files generate Codex definitions: run `python3 plugins/sdlc/scripts/claude_roles.py generate` and `codex_roles.py generate` if the sources change, and `check.py` pins some phrases (`prompt_lint.py`, `reply_lint.py`, check.py items): when a pinned phrase must change, change its check in the same commit. Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Reword the testing guidance in the files above.
2. Regenerate the agent definitions.
3. Add a CHANGELOG `[Unreleased]` line.

## Acceptance criteria
- `grep -l 'check.sh --changed' plugins/sdlc/agents/builder.md plugins/sdlc/agents/solo.md plugins/sdlc/agents/verifier.md plugins/sdlc/AGENTS.md` lists all four files.
- No role or skill file tells a role to run the full `check.sh` during a ticket: `git grep -n 'check.sh' -- plugins/sdlc/agents plugins/sdlc/skills` shows only `--changed`, `--fast`, land-gate, release or "never run the full" contexts (list the hits in the report).
- `bash plugins/sdlc/scripts/check.sh --changed $SDLC_BASE_SHA` exits 0 and `git diff --check` is clean.

## Constraints
- Verifier independence and the one-verifier rule stay as they are.
- Model and effort tables do not change.

## Outcome

2026-11-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 1b03ee5568b8
- Changed: see commits
- Commits: 3a814bf T-0859: roles run the checks for their change, once
- Check: 1 `grep -l 'check.sh --changed'` lists all four files: pass
- Check: 2 No role or skill file tells a role to run the full check.sh during a ticket: pass
- Check: 3 `bash plugins/sdlc/scripts/check.sh --changed $SDLC_BASE_SHA` exits 0 and `git diff --check` is c...: pass
- Follow-up: decide: plugins/sdlc/agents/solo.md:18: Run-verbatim reads "exactly as... -> notes.md
- Follow-up: decide: plugins/sdlc/skills/fanout/SKILL.md:39: "a role inside a lane runs .. -> notes.md
- Follow-up: decide: plugins/sdlc/agents/builder.md:16 and... -> notes.md
