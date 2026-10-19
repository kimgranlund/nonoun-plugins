---
id: T-0633
title: "work_root t11: agent and skill prose names record paths layout-neutrally; regenerate Claude level agents"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0625, T-0632]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
agent and skill prose names record paths layout-neutrally; regenerate Claude level agents and Codex TOMLs.

## Context
Part 13 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t11` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/agents/*.md (planner, filer, conductor)`, `plugins/sdlc-lite/skills/{chain,handoff-format,ticket,ask,fix,file,decompose,handoff,clarify,grill,open-questions,agent,fleet-status,fleet-doctor,plan,plan-loop}/**`, `plugins/sdlc-lite/AGENTS.md`, `plugins/sdlc-lite/scripts/check.py (phrase pins only)`, `plugins/sdlc-lite/adapters/codex/agents/*.toml (generated)`

Actions this ticket hosts:
-  agent and skill texts name record paths without assuming .sdlc; generated Claude and Codex agents stay in parity

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `grep -rlE '\.sdlc/(notes\.md|roadmap\.md|evals/|proposals/|fleet\.json|<slug>/|<task>/)' plugins/sdlc-lite/agents plugins/sdlc-lite/skills | wc -l` prints 0 (red before: about 30 files), and `bash plugins/sdlc-lite/scripts/check.sh` exits 0 including generated-agent parity; the check.py notes pin accepts NOTES.md

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: no new em dashes in the diff (0 added lines contain one). | note: the red-first order is not recorded as a `redck.py` deviation (the command printed none); the failing state was reproduced by the base-sha grep (27 files) and the base regex.) · verifier: verifier-L2 (sonnet) · base: e4c243ccb1c9
- Changed: see commits
- Commits: 27e2543 T-0633: work_root t11: agent and skill prose names record paths layout-neutrally; regenerate Claude level agents
- Check: 1 grep of hardcoded `.sdlc/` record paths in agents and skills prints 0; check.sh exits 0 including...: pass
