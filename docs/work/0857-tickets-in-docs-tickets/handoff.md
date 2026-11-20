---
id: T-0857
title: "New repos keep tickets in docs/tickets"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0857-t0857
worktree: ../sdlc-lite.worktrees/T-0857-t0857
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A repository onboarded to sdlc keeps its tickets under `docs/tickets/` by default, not in `.sdlc/` folders.

## Intent
- Do: make `onboard.py` write `work_root: docs/tickets` for a new install, and update the docs and templates that describe the default.
- Non-goals: changing what a repo with no `work_root` line reads (it keeps the `.sdlc/` paths); migrating this repository, which stays on `work_root: docs/work`; changing `.sdlc/runtime/` run records.
- Done when: the criteria below hold.

## Context
- User decision 2026-11-19: "use /docs/tickets/ for tickets instead of .sdlc/ folders", scoped to "Default for new repos": existing repos keep their current path until they migrate.
- The mechanism exists: `.sdlc/config` `work_root: <path>` (`plugins/sdlc/scripts/roots.py`), `tickets.py migrate-work-root`. `onboard.py` creates the config and entry files; find where it writes or proposes the config and what it does when a config already exists (it must not change an existing repo's config).
- Update the places that state the default: `onboard.py` templates and its selftest, `skills/onboard`, `skills/ticket`, `skills/handoff`, `docs/specs/ticket-stages/` and `docs/specs/repo-onboarding/` where they name the default ticket home, and `plugins/sdlc/CHANGELOG.md` or the root `CHANGELOG.md` `[Unreleased]` (`### Changed`), whichever the plugin uses.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Make a fresh onboard write `work_root: docs/tickets`; leave an existing config untouched.
2. Add selftest cases: a fresh repo gets the line and `tickets.py new` then creates `docs/tickets/<NNNN>-<slug>/handoff.md`; a repo with an existing config (with and without `work_root`) is unchanged.
3. Update the docs that name the default.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/onboard.py selftest` exits 0 and includes the two new cases; removing the new default line from `onboard.py` makes the fresh-repo case fail (state the observed red in the report).
- In a throwaway git repo under your scratch dir, onboarding then `tickets.py --root .sdlc new chore x "x"` creates a path under `docs/tickets/`.
- `python3 plugins/sdlc/scripts/roots.py selftest` and `python3 plugins/sdlc/scripts/tickets.py selftest` exit 0.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- This repo's `.sdlc/config` stays `work_root: docs/work`.
- A repo with no `work_root` line behaves as before.
