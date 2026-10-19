---
id: T-0444
title: "Ticket vocabulary: add area, status claimed and status paused"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket can carry a domain `area:`, and its status can say `claimed` and `paused`, with the roadmap, board and tracker mapping showing them.

## Intent
- Do: (1) `area:` front-matter field, free text from a list kept in `.sdlc/config` (`areas: ui-kit, front-end, back-end, data-lake, agent-os`), validated by `tickets.py check`, shown in `roadmap` and `/board`, and kept distinct from a worktree lane (`lane/<ticket>-<slug>`); (2) `status: claimed` set when a `claimed_by:` line is added (and cleared on release), and `status: paused` with a one-line `paused_reason:`; both accepted by `tickets.py`, `roadmap` stages, `steps.py`, `board`, `fleet_status.py` and `fleet_collect.py` counters; (3) a mapping table to Linear and GitHub (status to state or label, area to label or team, size L1 to L4 to estimate) in the lane lifecycle spec section 8.1 or a new reference; (4) a `tickets.py migrate` or a no-migration statement for existing tickets (absent `area` is valid; existing statuses stay valid).
- Non-goals: renaming size L1 to L4 to xs to xl (size is the model level, see `skills/level-rubric`); changing model or effort rows; building any Linear or GitHub integration beyond the mapping text.
- Done when: selftests for each new field and status with a negative control (an unknown area, a `paused` with no reason, and `claimed` with no `claimed_by` are rejected), `tickets.py roadmap` shows the new values, `check.sh` exits 0, and the README or `.sdlc/AGENTS.md` managed block lists the vocabulary.

## Context
Today: status is `proposed | ready | blocked | done | dropped`; a claim is a `claimed_by: <who> <date>` line and progress shows only on `/board`; size is `L1` to `L4` (`L5` reserved) and doubles as the model level; priority `P1 | P2 | P3`; type `feature | bug | chore | spike | idea`. Files: `plugins/sdlc-lite/scripts/tickets.py`, `steps.py`, `fleet_status.py`, `fleet_collect.py`, `.sdlc/AGENTS.md` (router, generated block), `skills/*` ticket and file skills. Related: lane lifecycle spec section 8.1 (every lane has a ticket), T-0422.

## Constraints
Existing tickets stay valid with no migration required. Keep the status set small; do not add a status the board cannot show. No model or effort change.

## Plan review
- plan defect: dispatch.py prepare builder L3 step-1: steps.py lint refused cited paths `.sdlc/0001-a` and `.sdlc/0001-a/handoff.md` (cited path does not exist). The fixture spans write `"$d/.sdlc/0001-a/handoff.md"`, and the link lint reads the `.sdlc/...` part as a repo path. Replan so no criterion or Do text spells a nonexistent repo-relative `.sdlc/<dir>` path (for example build the fixture dir from a variable such as `t="$d/.sdlc"; mkdir -p "$t/0001-a"`), and recheck each step handoff with `steps.py lint`.

## Closed

2026-10-11: warnings acknowledged: red controls recorded after the edit for steps 2 and 3 on shared base; the verifiers probed the base content and all three steps passed, check.sh exit 0 on the integration branch

> - process deviation: red-checkpoint: retrospective: attempt 7daccd26446647b1a721c047127d8456, handoff sha256 de94360d0e17, 5 of 5 (red) criteria without a pre-edit red control. The five criteria are the spec section 8.2 check, the handoff-format status line, the five ticket templates, the ticket SKILL `paused_reason`, and the sdlc-internals `paused_reason`. This is step 2. The builder says the checkpoint was marked retrospective only because step 1's uncommitted `tickets.py` and `board.py` changes were already in the tree. A passing verdict does not clear this deviation.
> - process deviation: red-checkpoint: retrospective: attempt 00d75ee6dc4948c8a5bcf8911cba8158, handoff sha256 eb36df0ac8ea, 1 of 1 (red) criteria without a pre-edit red control. The criterion is the `areas=tickets.config_areas(root)` grep in `traces/sources/tickets.py`. This is step 3. Eleven paths from steps 1 and 2 already differed from the base, so the record could not be pre-edit. A passing verdict does not clear this deviation.
> - All three steps passed. Step 1 passed with verifier L2, step 2 with verifier L1, and step 3 with verifier L1.
> - Step 1's red-first evidence rests on `step-1/red-checkpoint.jsonl` (8 pre-edit controls, red at base 222f817e). The step 1 verifier could not rerun the criteria in a detached-HEAD worktree: the stray-worktree hook refused it because `SDLC_TMP_WORKTREES` was unset in that call.
> - Steps 2 and 3 verifiers probed the base content. Each (red) string is absent at 222f817e, so those checks can go red.
> - Step 1 never ran `check.sh`. The plan assigned it to step 2, which passed it, with `check.sh` exit 0, `check-packaging.py` exit 0 and `git diff --check` clean.
> - The step 3 builder did not run the changed-files guard. The step 3 verifier ran it and it passed. The verifier also ran a negative control with only 2 exclusions, which failed as it should.
