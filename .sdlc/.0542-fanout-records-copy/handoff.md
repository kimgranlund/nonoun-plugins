---
id: T-0542
title: "Lean records C: Fanout carries records by copy (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0540]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Fanout carries records by copy: part C of SDLC Lite 0.23.0 lean work records (wave 2).

## Intent
- Do: build part C of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for C, Interfaces and Risks). Files: `fanout.py` (`commit_lane_records` becomes a copy; `branch_verdict` and `host_branch_ticket` read the lane worktree's records dir, else git objects; the :1574 copy condition no longer keys on `filer-L*.md`; the :1199-1213 copy includes the records dir; the close commit untracks ignored records; integration records are copied to the main checkout's runtime; headless prompt :446-450 drops the filer), `lanes.py` (`copy_sdlc` archive includes `runtime/tasks/<name>`), `skills/fanout/SKILL.md`. An external lane with no worktree delivers its verdict by committing the verifier result into the ticket folder with `git add -f`, which is the prefix the git-objects fallback reads, and land untracks it in the close commit
- Non-goals: the other parts (A to F) of the same design.
- Done when: `fanout.py selftest` exits 0 with a land whose close commit tracks only `handoff.md` under the ticket folder, and a branch with no worktree still lands from git objects. Negative control: with the copy step removed, land reports `no verifier result`

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.

## Plan review
- plan defect: `dispatch.py prepare builder L3` refused step-1 (steps.py lint): cited path does not exist: `.sdlc/0540-records-dir/handoff.md` (the ticket is closed as `.sdlc/.0540-records-dir/`); `.sdlc/t1/`, `.sdlc/t2/`, `.sdlc/t1/skips.md` (selftest fixture paths, cite them as plain text such as "the fixture ticket folder t1" or without a repo path shape). Rewrite those citations; the plan content otherwise stands.
- plan defect: step 2 builder L2 blocked (`.sdlc/runtime/tasks/0542-fanout-records-copy/step-2/builder-L2.md`): the guard `bash plugins/sdlc-lite/scripts/check.sh` is red from inside any role run on this task. Its only failure is `traces selftest` case `corpus: this repo's .sdlc traces ingest whole` (`plugins/sdlc-lite/scripts/traces/selftest.py` lines 2024-2054), which lists every in-flight `.attempt.json` under `.sdlc/runtime/tasks/0542-fanout-records-copy/` as "attempts in no row". Confirmed by the conductor: `traces.py selftest` PASS once every attempt was recorded. The running builder's or verifier's own attempt is always in flight, so a bare in-tree `check.sh` guard reds again on the verifier. The gate must run where no live runtime records exist (for example a copy of HEAD with the working diff applied), or the plan must name another route; the corpus case only skips when `.sdlc` is absent under the git toplevel, and check.sh has no skip knob. `SDLC_TMP_WORKTREES` is unset in this session and `hooks/block-stray-worktree.sh` refuses a throwaway worktree without it (the step 1 verifier and step 2 builder both hit this), so do not depend on a role-created git worktree. Changing traces.py is out of scope (it belongs to the 0539 wave, D or E).
- builder premise correction: `git ls-files --others` without `--exclude-standard` already lists ignored files, so the second `--ignored` listing in `copy_sdlc` is redundant; the behavioural change is the `.log`/`.running`/`.run.lock` skip filter, and the row 9 `.log` assertion is the check that bites.
- lanes.py already carries the step-2 edits in the tree (row 9 runtime-record and `.log` assertions, skip filter, docstring), and lanes.py selftest, check-packaging.py and git diff --check passed; any new `(red)` criterion must be red against the current tree.

## Closed

2026-10-14: warnings acknowledged: step 2 replanned once and passed; traces in-flight attempt red is tracked as a follow-up

> - process deviation: red-checkpoint: retrospective: attempt 2c02f203c74b4bd5a39a31e0a13d27ab, handoff sha256 989b4f3a84dc, 2 of 2 (red) criteria without a pre-edit red control: `grep -qF "runtime/tasks" plugins/sdlc-lite/scripts/lanes.py`; `grep -qF "runtime records were not archived" plugins/sdlc-lite/scri...`. This is from the superseded step-2 attempt (`step-2.superseded-1`).
> - process deviation: red-checkpoint: retrospective: attempt 75d34d2020b74e7d89352c4ca8c27ad0, handoff sha256 6be6d17db00f, 1 of 1 (red) criteria without a pre-edit red control: `! grep -qF -- "'--ignored'" plugins/sdlc-lite/scripts/lanes.py`. This is from the final step-2 attempt. The verifier noted that the base sha has 0 matches for that pattern, so the only red it saw was against the superseded attempt's in-tree edits. The order "failing first, then edit" is unproven for the `lanes.py` change, and the passing verdict does not clear this.
> - Both steps passed verification. Step 1 was verified by verifier-L2 and step 2 by verifier-L1.
> - The planned step-2 route was replaced. The builder reported that `check.sh` is red from inside a role run, because the traces corpus case counts the role's own in-flight attempt records. The final step-2 verifier ran `check.sh` on a clone with TMPDIR unset and it passed. The traces check was not changed, as the handoff directed.

2026-10-14: kept stale refs to .sdlc/0542-fanout-records-copy in: .sdlc/runtime/tasks/0542-fanout-records-copy/filer-L1.md, .sdlc/runtime/tasks/0542-fanout-records-copy/step-1/builder-L3.md, .sdlc/runtime/tasks/0542-fanout-records-copy/step-1/verifier-L2.md, .sdlc/runtime/tasks/0542-fanout-records-copy/step-2/verifier-L1.md
