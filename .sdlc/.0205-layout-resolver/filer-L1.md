<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0205: layout key and one resolver for ticket dir, roadmap, notes

## PR body
### Summary
Adds a `layout: topics|flat` line to `.sdlc/config` and one resolver, `layout_paths(root)` in `tickets.py`. It returns the ticket dir, roadmap path, notes path and work dir. Flat repos, which are the default, keep byte-identical generated text. Topics repos get `tickets/roadmap.md`, `notes/notes.md` and a `work/` dir. `onboard.py` now renders its managed block from the resolved roadmap path.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - **Resolver:** `LAYOUT_RE`, `LayoutPaths` and `layout_paths`.
    - A bad value, both values in one file, or `layout: topics` without `ticket_root: tickets` fails with `nothing written`.
  - **Callers:** every `cmd_*`, `render`, `write_roadmap`, `stale`, `append_notes` and the three `outside_refs` calls go through the resolver.
  - **Router:** topics variants of the router text, plus the `work/` and `notes/` entry files. Flat output is unchanged.
  - **`check`:** under topics, `check` fails on stray root entries (`root_strays`). On a flat repo with no `layout:` line it warns and exits 0, naming `migrate-layout`. `layout: flat` silences the warning.
  - **Selftest:** topics cases and three stray controls. Three bad-config controls, a stale `work/AGENTS.md`, the flat opt-out and the git-backed close and archive scans are covered too. The flat `ok:` asserts are updated.
- `plugins/sdlc-lite/scripts/onboard.py`:
  - `Model.roadmap` and `_roadmap_path`, which turns a `tickets.Fail` into a `SetupError`.
  - The managed block shows the resolved roadmap path.
  - `TEMPLATE_VERSION` stays at 1, so existing flat blocks stay `current`.
  - New `layout-variant` selftest gate with two negative render variants.

### Verification
- **Step 1** (tickets.py, verifier L2): pass. The verifier ran the resolver, bad-config, topics `new` and `check`, router, stray, notes and flat-warning criteria. It also ran the `tickets.py selftest` and base-archive flat and nested guards.
  - A flat-output comparison against base differed only in absolute plugin paths inside `messages/**/AGENTS.md`.
  - The builder ran a negative control: stubbing `root_strays` turns the selftest red. The verifier did not re-run it.
- **Step 2** (onboard.py, verifier L1): pass.
  - A topics setup names only `.sdlc/tickets/roadmap.md`, and `layout: nested` is rejected with nothing written.
  - Blocks written by the base `onboard.py` stay `current`.
  - `onboard.py selftest` passes all 14 gates.
- **Ticket-level guards:** both verifiers report these passing: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `codex_roles.py generate --check` and `tickets.py --root .sdlc check`. The last prints the flat-layout warning and exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- sdlc-lite: new `layout: topics|flat` config key and a single path resolver for the ticket dir, roadmap and notes. `tickets.py check` fails on stray root entries under `topics` and warns (exit 0) on flat repos, pointing to `migrate-layout`. `onboard.py` renders the managed block from resolved paths. Flat repos are unchanged.

## Follow-ups
- decide: this repo's own `.sdlc/config` has no `layout:` line, so every `tickets.py check` now prints the migrate-layout warning; choose between adding `layout: flat` and migrating (T-0206 or T-0207).
- note: `ROUTER_FLAT_INTRO` duplicates the first paragraph still inside `ROUTER_TEMPLATE`, and `router_bodies` swaps them by string match; editing one without the other leaves a topics tree with the flat paragraph (the `tp-new` selftest case catches it).
- note: the builder edited two selftest asserts the handoff did not list, in the numbered-config warning block. Each now checks `'ticket_folders: numbered' not in out + err`, because every flat root now warns.
- note: `check.py` guards, listed among the ticket's owning files, were not touched, and the artifacts show no guidance-doc update (the AGENTS.md files). The Done-when line says affected guidance is updated, so confirm whether anything was needed.
