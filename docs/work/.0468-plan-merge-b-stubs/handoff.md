---
id: T-0468
title: "Merge plan skills B: redirect stubs for the four retired names and retargeted checks"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0467]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The four retired names (`plan-goal`, `plan-campaign`, `plan-doc`, `plan-fanout`) redirect to `/plan <kind>` for one release, and every check and reference points at the new skill.

## Intent
- Do: ticket B of the design: the four stub `SKILL.md` files (keep the folder and `name:`; the description reads "Redirect: run `/sdlc-lite:plan <kind>`; removed in the next minor" with none of the old trigger phrases); delete the four old `references/`; update `scripts/check.py` items 31, 48, 51 and add the stub item, each with its negative control observed red; `agents/conductor.md:21`; `skills/sdlc-lite/SKILL.md` rows 29 to 32 and 48; `codex_roles.py generate`; the two specs' and `docs/README.md` references; a changelog and compatibility note.
- Non-goals: the cost `--summary` and lint rules (C); deleting the stubs (D, next minor).
- Done when: `check.py` with each negative control observed red, `check-packaging.py`, `codex_roles.py generate --check`, `rename_refs.py links` against the item 32 allowlist, and `check.sh` exit 0.

## Context
Approved design: `.sdlc/.0462-plan-skills-merge-design/architect-L1.md` (read all of it: Approach, Interfaces with the overlap table and the dry-run shape, Constraints, Rejected alternatives, Risks, Carry forward). Maintainer decision 2026-10-12: file A to C, and put the `compaction` kind (T-0465) after A so `skills/plan/SKILL.md` has one writer at a time. Hot files one writer at a time: `plan_check.py`, `check.py`, `core.md`. If the merged `SKILL.md` passes 130 lines, stop and report: the design lists "keep seven skills" as the first alternative to reconsider.

## Constraints
No model or effort change. Old skills stay working until B. The skill stays self-contained (`check.py` item 42). Controlled language per T-0461 for plan artifacts. State only what a file or command shows; the replay is unverified if it was not an independent run.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and item 58 flags each of these planted defects when applied to the real stubs (observe red, then restore): a stub that regrows `## 1. Gather`, a stub whose `plan <kind>` token is replaced, a stub folder that regains `references/`, a missing stub.
2. `python3 scripts/check-packaging.py` exits 0.
3. `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
4. `test -z "$(git grep -l 'plan-goal/references\|plan-doc/references\|plan-campaign/references\|plan-fanout/references' -- plugins)"` exits 0: no plugin file points at a deleted old reference.
5. `test -z "$(ls plugins/sdlc-lite/skills/plan-goal/references plugins/sdlc-lite/skills/plan-campaign/references plugins/sdlc-lite/skills/plan-doc/references plugins/sdlc-lite/skills/plan-fanout/references 2>/dev/null)"` exits 0.
6. `grep -c 'Redirect: run' plugins/sdlc-lite/skills/plan-goal/SKILL.md plugins/sdlc-lite/skills/plan-campaign/SKILL.md plugins/sdlc-lite/skills/plan-doc/SKILL.md plugins/sdlc-lite/skills/plan-fanout/SKILL.md` prints four lines ending `:1`, and each stub is under 15 lines.
7. `grep -c '/sdlc-lite:plan doc' plugins/sdlc-lite/agents/conductor.md` prints a count of 1 or more, and `python3 plugins/sdlc-lite/scripts/rename_refs.py links` reports only rows of docs/reports/broken-links-allowlist.md.
8. `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
verifier: L3

## Closed

2026-10-12: built and merged (wave 52 wip lane): verifier L3 passed 7 of 8 criteria with observed controls; criterion 7 is a plan defect (its span was green before and after, so it could not go red), not a build defect
