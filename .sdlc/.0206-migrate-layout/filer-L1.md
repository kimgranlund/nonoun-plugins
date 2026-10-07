<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0206: tickets.py migrate-layout

## PR body
## Summary
Adds `tickets.py migrate-layout [--dry-run] [--rewrite-refs]`. It moves a flat `.sdlc/` into the topics layout. Ticket folders go to `tickets/`, task folders without a ticket go to `work/`, `roadmap.md` goes to `tickets/`, and `notes.md` goes to `notes/`. It also finds every file that cites a moved path. Citing files are reported, or rewritten with `--rewrite-refs`. Dated records under `docs/reports/` are never rewritten. The command writes `ticket_root: tickets` and `layout: topics`, regenerates the router and roadmap, and ends on `check`. A second run prints `nothing to migrate`.

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `cmd_migrate_layout`, `migrate_text` and `ensure_topics_config`, the `migrate-layout` subparser and its `run` branch, and the docstring Usage text.
  - Preconditions: the config must parse, the root must be inside a git work tree, the tree must be clean, there must be no loose root files, and no move target may already exist. Each refusal ends `nothing written`.
  - Managed blocks in `AGENTS.md` files are frozen rather than rewritten. After the move, `onboard.py check` reports `stale`, and `onboard.py setup` brings it back to `current`.
  - `ensure_topics_config` keeps existing `layout: topics` lines so a topics config stays byte-identical.
  - New `(mig)` selftest cases cover the dirty-tree, cite, loose-file and stray-folder controls listed under Verification.
- `docs/references/sdlc-internals.md`: a `migrate-layout` passage in the `scripts/tickets.py` entry.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `migrate-layout` in the argument-hint, plus an upgrade-note bullet.

## Verification
- Step 1 (verifier L2, pass):
  - All 10 fixture criteria passed. They cover refusal without `--rewrite-refs`, dry-run, a real migration, rewritten text, the frozen managed block, idempotence, dirty-tree and loose-file refusal, stray-folder `check` failure, and the `ticket_root: tickets` fixture.
  - `tickets.py selftest` passed.
  - Only `tickets.py` changed outside `.sdlc`.
  - The verifier replaced the block-freeze branch with `if False:` in a throwaway copy. Criteria 1 and 5 then failed, so the check can go red.
  - The outside-git refusal was run directly and returned rc 1 with the root unchanged.
- Step 2 (verifier L1, pass):
  - The doc and SKILL.md greps passed.
  - The passage matches the code at the `tickets.py` docstring.
  - The changed-files allowlist and `git diff --check` passed.
- Guards, run by the step 2 builder and verifier (rc 0): `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, and `tickets.py --root .sdlc check`. The last printed `ok: 309 tickets, roadmap current` and the expected flat-layout warning.
- The command was not run on this repository's `.sdlc`, as the handoff requires. All migration checks used fixtures.

## Changelog entry
- Added `tickets.py migrate-layout [--dry-run] [--rewrite-refs]` to move a flat `.sdlc/` into the topics layout. It refuses on a dirty tree, scans and optionally rewrites citing files (never `docs/reports/`), regenerates the router and roadmap, and is idempotent.

## Follow-ups
- note: This repo's `.sdlc` has not been migrated. The command would refuse today because the tree is dirty and `.sdlc/pause-2026-10-06.md` is a loose root file. Move or remove that file and commit before any real run.
- note: After a migration the managed `AGENTS.md` block reads `stale` until `onboard.py setup` runs. This is by design and is stated in the upgrade note.
- note: The `ticket_root` bullet and the `.sdlc/roadmap.md` and `.sdlc/notes.md` path text in the docs were left to T-0207 (readers and docs).
- note: The tickets selftest now takes about 37 s, up from about 31 s at HEAD.
