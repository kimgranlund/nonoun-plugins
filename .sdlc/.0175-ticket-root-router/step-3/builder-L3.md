<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Adds `import onboard`.
  - Adds the router templates (`ROUTER_TEMPLATE`, `TICKETS_TEMPLATE`, `ROUTER_PROCEDURES`, `ROUTER_PLUGIN_LINE`, `ROUTER_HERE`, `ROUTER_TICKETS`).
  - Adds the helpers `router_paths`, `router_files`, `stage_lines`, `router_bodies`, `read_text`, `router_preflight`, `write_router` and `router_problems`. `write_roadmap` now calls `write_router`.
  - `stamp()` inserts the `router:` front matter line.
  - new, close, roadmap, archive and number run the malformed-block preflight. `cmd_check` reports router problems after the stale-roadmap check.
  - Adds docstring text for the router files, the CLAUDE.md import, `claimed_by`, the `router:` line and the check causes.
  - Appends selftest cases. No existing case changed.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS. It passed before the new cases were added and again after.
- Template check: a script compared `ROUTER_TEMPLATE` and `TICKETS_TEMPLATE` with the two handoff templates (indent removed, placeholders filled). Both are byte-identical.
- Acceptance criteria 1 to 21: I pulled each command out of the handoff and ran it with `bash -c`. All 21 pass, including the three guards.
  - Criteria 16 and 17 put defects into a copy of the scripts: `router_problems` returning `[]`, and `write_router` doing nothing once AGENTS.md exists. The clean copy's selftest passed and the defective copy's failed in both.
  - Before the new selftest cases were added, criterion 16 failed. That was expected.
- `python3 plugins/sdlc-lite/scripts/{board,fanout,traces}.py selftest`: all rc=0. This was for information only; the handoff leaves these to the final step.
- `git diff --check`: clean.

## Notes
- If a managed AGENTS.md holds a malformed block, `write_router` leaves that file alone instead of raising. The preflight refuses before any write, so this branch only runs if something gets past the preflight.
- `archive` checks for numbered mode before the preflight, so in plain mode it refuses with the numbered-mode message rather than the malformed one. The malformed-block selftest case runs archive with `numbered=True`.
- A ticket with an empty title gets a router line with two spaces, `  - T-0001  (alpha)`. This follows the `<id> <title> (<folder>)` format exactly.
- I wrote the throwaway criteria file to `$SDLC_TMP_WORKTREES` and deleted it afterwards. No worktree was created.
