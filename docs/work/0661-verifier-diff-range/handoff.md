---
id: T-0661
title: "Verifier brief carries a base..end diff range per built step"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier checks exactly one built step: `record` stores where the build ended, and the verifier brief carries `base..end` for that step, so later steps or merges in the lane no longer leak into its diff.

## Intent
- Do: (1) `dispatch.py record` for a builder that exits 0 writes `end-sha` in the step's records dir: HEAD of the execution tree when the tree is clean, else a tree hash of the working tree built with a temporary index (`GIT_INDEX_FILE=<tmp> git add -A && git write-tree`), never `git stash`. (2) `dispatch.py prepare verifier` reads that file when present and adds `Diff range: <base>..<end>` to the brief (for a tree hash: `git diff <base> <tree>`), stores it as `diff_range` in the dispatch record, and changes "diff against Base sha, not HEAD" to name the range. No `end-sha` keeps today's brief. (3) Selftest cases, and one sentence in `skills/handoff-format/SKILL.md` (or the records section of `docs/references/sdlc-internals.md`) naming `end-sha`.
- Non-goals: Codex `run.sh` (it writes `base-sha` but no `end-sha`; a separate ticket if wanted). Solo lanes, which have no builder record. Rewriting scope criteria.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #21, ui-kit-neue audit 2026-10-20.
- Evidence: T-0029 step-1 verifier-L2-2 wrote "#11 cannot pass as written... diff from it now holds steps 2 and 3"; several verifiers note "base is the merge commit" and re-derive the range by hand.
- Base selection: `build_base` at `plugins/sdlc-lite/scripts/dispatch.py:429` (named base, recorded `base-sha`, newest resync merge at `dispatch.py:485`, HEAD or lane start). `prepare` writes `base-sha` at `dispatch.py:1110-1115` and adds `Base sha:` at `dispatch.py:1132-1133`; the verifier run rules, including "diff against Base sha, not HEAD", are at `dispatch.py:1129-1131`. The dispatch record keys are at `dispatch.py:1147-1150` (`base_sha`, `review_sha`).
- `record` is `dispatch.py:1503`; write `end-sha` only on the success path (attempt completed, role builder).
- A verifier with a ready ref already gets `Review sha:` (`dispatch.py:1134-1136`, T-0590); when both exist, the review sha wins as the end and the brief says so.
- Existing base selftests: `dispatch.py:2421` (builder base sha in dispatch, base-sha and brief) and `dispatch.py:2459` (solo base).

## Constraints
`Base sha:` keeps its value and wording for every existing case. Never use `git stash` or touch the shared index. A step with no builder record gets the current brief.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: (a) a builder recorded on a committed step writes `end-sha` equal to the tree's HEAD, and a verifier prepared after a second commit lands in the tree gets `Diff range: <base>..<that end sha>`, not the new HEAD; (b) an uncommitted build writes a tree hash and the brief names `git diff <base> <tree>`; (c) a verifier with no `end-sha` gets no `Diff range:` line. Cases (a) and (b) fail with the change reverted.
2. `git stash list` is unchanged by `dispatch.py selftest` (the selftest asserts the stash stack is the same before and after case (b)).
3. `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0.
4. `git diff --check` exits 0, and `python3 scripts/check-packaging.py` exits 0 if a skill changed.
