<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt 7daccd26446647b1a721c047127d8456, handoff sha256 de94360d0e17, 5 of 5 (red) criteria without a pre-edit red control. The five criteria are the spec section 8.2 check, the handoff-format status line, the five ticket templates, the ticket SKILL `paused_reason`, and the sdlc-internals `paused_reason`. This is step 2. The builder says the checkpoint was marked retrospective only because step 1's uncommitted `tickets.py` and `board.py` changes were already in the tree. A passing verdict does not clear this deviation.
- Both steps passed. Step 1 (`tickets.py`, `board.py`, router block) passed with verifier L2. Step 2 (docs, skills, templates) passed with verifier L1. The step 2 verifier probed base content and found each (red) string absent, so the checks can go red.
- Step 1's red-first evidence rests on `step-1/red-checkpoint.jsonl` (8 pre-edit controls, red at base 222f817e), not on a rerun. The verifier could not rerun the criteria in a detached-HEAD worktree: the stray-worktree hook refused it because `SDLC_TMP_WORKTREES` was unset in that call.
- Step 1 never ran `check.sh`; the plan assigned it to step 2, which passed it. The step 2 builder and verifier both report `check.sh` exit 0, `check-packaging.py` exit 0 and `git diff --check` clean.

## PR title
T-0444: Ticket vocabulary: add area, status claimed and status paused

## PR body
Summary: A ticket can now carry a validated domain `area:`. Its status can be `claimed` or `paused`, and the roadmap, router block and `/board` show them. Existing tickets need no migration.

Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `ENUMS['status']` has 7 statuses: proposed, ready, claimed, paused, blocked, done, dropped.
  - `GLYPH` gains entries for claimed and paused, and `ACTIVE` includes both. The `cmd_close` follow-up dedupe now uses `ACTIVE` at both sites.
  - `status: claimed` needs a non-empty `claimed_by`, and `status: paused` needs a non-empty `paused_reason`. The rule runs one way only, so a `ready` ticket with `claimed_by` stays valid.
  - `area:` is checked against an `areas:` line in `<root>/config` (new `config_areas`). An unknown area is rejected, and so is any area when no `areas:` line exists.
  - `roadmap` adds an Area column only when some ticket has an area. A paused Status cell shows its reason, and `stage_lines` appends `, paused: <reason>`.
  - The router block gains a `Ticket fields:` section and claim, release and pause steps.
- `plugins/sdlc-lite/scripts/board.py`: `ALWAYS_SHOWN` gains claimed and paused. A new `area_of` helper sits beside `ticket_of`, whose tuple is unchanged. The Ticket cell shows `<status> · <area>` when the ticket has an area.
- `.sdlc/AGENTS.md`: managed block regenerated with the vocabulary and the `claimed` and `paused` stage lines.
- `docs/specs/sdlc-lite/lane-lifecycle.md`: new section 8.2 with the Linear and GitHub mapping table (mapping text only, no integration built) and a no-migration statement.
- `docs/references/sdlc-internals.md`, `skills/handoff-format/SKILL.md`, `skills/ticket/SKILL.md` and the five ticket templates now list the new statuses, `paused_reason:`, `area:` and `areas:`.

Verification
- Step 1, verifier L2: pass.
  - It ran all 12 criteria itself. Eight are (red) criteria with pre-edit red controls recorded at base 222f817e.
  - `tickets.py` and `board.py` selftests print PASS, and `tickets.py --root .sdlc check` exits 0.
  - Negative controls: an unknown area, `paused` without a reason and `claimed` without `claimed_by` are each rejected.
- Step 2, verifier L1: pass.
  - It ran 10 criteria, five of them (red) criteria, all green on the built tree.
  - `tickets.py check` printed "ok: 437 tickets, roadmap current".
  - `check-packaging.py`, `check.sh` and `git diff --check` all exit 0, and the scope guard found no stray files.
- Process deviation, step 2: the five (red) criteria have only retrospective red controls (see Warnings).

## Changelog entry
- Tickets can carry a validated `area:` (names listed in the `areas:` line of the `.sdlc` config) and the statuses `claimed` (needs `claimed_by:`) and `paused` (needs `paused_reason:`). `tickets.py roadmap`, the router block and `/board` show them. Existing tickets need no migration, and a Linear and GitHub mapping table is in the lane lifecycle spec section 8.2.

## Follow-ups
- fix-now: `plugins/sdlc-lite/scripts/traces/sources/tickets.py:31` calls `tickets.problems(...)` without `areas=`, so trace validation skips the area check. Pass `config_areas(root)` there.
- decide: `fanout.py prep` and the run-plan rules claim a lane with `claimed_by:` alone and leave `status: ready`. That stays valid, but the roadmap and `/board` never show `claimed` for fanout lanes until they also set `status: claimed`. A person must choose whether they should.
- note: `.sdlc/config` has no `areas:` line in this repo, so the area check and Area column are untested against a real populated root. The handoff names `ui-kit, front-end, back-end, data-lake, agent-os` as the intended list.
- note: The 7-status list is copied into the router block, the ticket templates and the handoff-format and ticket skills. A future status must be edited in each of those places.
