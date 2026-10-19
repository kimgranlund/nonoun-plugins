---
id: T-0629
title: "work_root t08b: fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0621]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor.

## Context
Part 9 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t08b` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/fleet_config.py`, `plugins/sdlc-lite/scripts/fleet_status.py`, `plugins/sdlc-lite/scripts/fleet_doctor.py`

Actions this ticket hosts:
-  read and append notes, evals, proposals and the fleet registry at their work-root paths

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` exits 0 with the case: under `work_root: docs/work` the default registry is docs/work/fleet.json and a blocked ticket's owner is read from docs/work/NOTES.md (red before); `fleet_config.py selftest` and `fleet_doctor.py selftest` exit 0

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: plugins/sdlc-lite/scripts/fleet_status.py:748 changes `rel` from relative-to-.sdlc to relative-to-repo, so worktree copies of a task folder resolve under the work root too. With no work_root line the path is the same as before (`.sdlc/<folder>`), and the existing collect fixtures still pass. | note: plugins/sdlc-lite/scripts/fleet_config.py:1 and docs/specs/sdlc-lite/fleet-config.md:3 still name only `.sdlc/fleet.json` as the registry. The docstring was updated, but the spec doc was outside the listed files, so the work_root location is not documented in the spec. | note: fleet_config.py `add` still needs an existing registry file (`docs/work/fleet.json: No such file or directory`, exit 1). Base behaves the same (`.sdlc/fleet.json: No such file or directory`), so this ticket did not cause it. With a seeded docs/work/fleet.json, `add` and `show --active` from a work_root repo used the new path (exit 0). | note: the scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0629-verifier-L2 was not removed because `rm` was denied. Both throwaway worktrees were removed.) · verifier: verifier-L2 (opus) · base: 6d6b28cf6bf0
- Changed: see commits
- Commits: ce0964a T-0629: work_root t08b: fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor
- Check: 1 `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` exits 0 with the case: under `work_r...: pass
