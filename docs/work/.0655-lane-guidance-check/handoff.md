---
id: T-0655
title: "prepare checks lane guidance against main and named guidance paths"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role dispatched into a lane works from the lane's own guidance: its brief tells it when the lane's AGENTS.md differs from the auto-attached main checkout copy, and `dispatch.py prepare` refuses to send a role toward a repo skill or guidance file that does not exist in the lane tree.

## Intent
- Do: (1) In `prepare` (`plugins/sdlc-lite/scripts/dispatch.py`), when the execution tree's toplevel is a linked worktree (not the main checkout from `git rev-parse --git-common-dir`), compare `AGENTS.md` and `CLAUDE.md` at both tops; for each that differs, append `Guidance: read <lane tree>/AGENTS.md; it overrides the auto-attached main checkout copy` to the brief and print a `lane guidance differs: <file>` line on stderr. (2) Collect the backticked repo-relative paths in the handoff that end in `SKILL.md`, `AGENTS.md` or `CLAUDE.md` or start with `.agents/` or `.claude/skills/`; any that is missing in the lane tree refuses with exit 5 (the lane exit code) and prints `guidance missing in lane: <path> (present on <branch> at <sha7>)` when the main checkout or the lane's `into` branch holds it, else `guidance missing in lane: <path>`; nothing is written. (3) Document both in the dispatch.py docstring Brief section and add selftest cases.
- Non-goals: syncing the missing guidance into the lane (that is T-0654 `fanout.py sync --paths`). Resolving paths named only in AGENTS.md routing (T-0648 owns routing). `fanout.py prep` solo briefs.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #15, ui-kit-neue audit 2026-10-20.
- Evidence: all 379 lane roles got the main checkout's AGENTS.md by auto-attach; only 62 also read the lane copy, and main's AGENTS.md changed 5 times that day while lagging the integration branch. 58 lane roles made 163 reads in the main checkout. A T-0065 ui-designer review in a lane found only three of four repo skills under `.agents/skills/`, hit "`.agents/skills/geometry-authoring/SKILL.md`: No such file or directory", and wrote its verdict anyway; the step was reviewed 5 times.
- In this repo: `prepare` is at `plugins/sdlc-lite/scripts/dispatch.py:944`; the execution tree is settled at `dispatch.py:983` (`run_tree`, from `exec_tree` at `dispatch.py:384` or `--tree`); the brief is assembled at `dispatch.py:1117` from `toplevel` (`dispatch.py:1103`). The existing `lane_gate` (`dispatch.py:529`) is the precedent for a lane refusal, and exit 5 is documented as "lane" at `dispatch.py:109`. Refusals before the lock write no record (the `--tree` check at `dispatch.py:981` is the pattern).
- Lane `into` branch: `.lane.json` at the lane top, as `lane_start` reads it (`dispatch.py:418`).

## Constraints
A dispatch from the main checkout, or from a lane whose guidance matches main and holds every named path, produces the same brief and exit code as today. No refusal writes a record.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases on a throwaway repo with a linked worktree: (a) the lane's AGENTS.md differs from main's: the brief holds `overrides the auto-attached main checkout copy` and stderr says `lane guidance differs: AGENTS.md`; (b) a handoff naming `` `.agents/skills/x/SKILL.md` `` that exists on main but not in the lane: prepare exits 5, prints `guidance missing in lane: .agents/skills/x/SKILL.md (present on`, and writes no attempt or dispatch record; (c) the same handoff with the file present in the lane passes. Case (b) fails with the path check removed (observed negative control, recorded in the Outcome).
2. A main-checkout dispatch in the existing prepare parity cases is unchanged: the run.sh dry-run parity case in the selftest still passes.
3. `git diff --check` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/dispatch.py`: new `lane_guidance(top, handoff)` and a `guidance` gate in `prepare`, after the time gate and before the lock. In a linked worktree, each differing `AGENTS.md`/`CLAUDE.md` prints `lane guidance differs: <file>` and adds `Guidance: read <Tree>/<file>; it overrides the auto-attached main checkout copy` to the brief; a backticked guidance path absent from the lane refuses with exit 5, `guidance missing in lane: <path> (present on <branch> at <sha7>)` (main checkout, else the `.lane.json` `into` branch), writing no record. The main checkout is never checked. Docstring gate list and Brief section updated.
- Selftest: five `lane guidance:` cases in their own block (matching lane, differing AGENTS.md, missing skill exit 5 with no record, skill present passes, main checkout unchecked).
- Negative control observed: with the refusal disabled (`if missing and False:`), `dispatch.py selftest` exits 1 with `FAIL: lane guidance: a handoff naming a skill on main but not in the lane refuses, exit 5, and writes no record`; restored, it passes.
- Checks: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0 (run.sh dry-run parity cases all ok); `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `git diff --check` exit 0.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 67123bd857b3
- Changed: see commits
- Commits: 231a82a T-0655: prepare checks lane guidance against main and named guidance paths
- Check: 1 selftest exits 0 with the lane guidance cases (a), (b), (c) and a bitten negative control: pass
- Check: 2 main-checkout parity cases unchanged: pass
- Check: 3 `git diff --check`: pass
- Follow-up: note: the redck.py deviations run printed no process deviation: lines... -> notes.md
- Follow-up: note: the harness denied rm -rf of the scratch dirs tmp:0655-verifier-L2... -> notes.md
