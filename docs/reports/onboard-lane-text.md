# Onboard lane text

Recorded: 2026-10-05. Ticket T-0228. Branch `onboard-lane`.

## What changed

The root entry block that `onboard.py setup` writes into a repository's `AGENTS.md` told a harness to run work through `/sdlc-lite:chain`, `/sdlc-lite:fix`, or `/sdlc-lite:build`. That contradicted the lane rule this repository ships. The line (`plugins/sdlc-lite/scripts/onboard.py`, `ROOT_AGENTS_TEMPLATE`, and its copy in `docs/specs/repo-onboarding/design.md`) now reads:

> Pick the lane first with `steps.py lane <task dir>` (in the plugin's `scripts/` folder): `solo` is the default for size S and M, `/sdlc-lite:fix` runs only when asked or when the lane script prints `fix`, and the full chain (`/sdlc-lite:chain`) needs a stated reason (an L4 or L5 step, a merge step, or cross-cutting scope). Roles launch with `run.sh`. Do not spawn another plugin's builder, planner, or reviewer agent in their place.

The wording mirrors the root `AGENTS.md` lane rule; it adds no new rule.

## No version bump

The ticket asked for a managed-block version bump so existing blocks read as stale. That is not needed and would do harm:

- A block is `stale` by text, not by version: `decide()` row 6 (`_row_other_block`) replaces any well-formed block whose digest matches its own text and whose text differs from the template. `_row_current` (row 5) needs byte-equal text. A block written by the previous template therefore reads `stale` as soon as the template text changes.
- `onboard.TEMPLATE_VERSION` is shared. `tickets.py` writes and checks its router blocks (`.sdlc/AGENTS.md`, `tickets/AGENTS.md`, `messages/AGENTS.md`) with the same constant (`tickets.py:1122`, `f.block.version != onboard.TEMPLATE_VERSION`). A first attempt bumped it to 2: `tickets.py --root .sdlc check` then failed with `AGENTS.md: router block stale` and the `tickets` selftest case "router: outside text and CLAUDE.md content kept, one block, one import" no longer bit (`check.sh` rc=1). The bump was reverted in commit 3264439.

## Evidence

- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: new gate `lane-text` passes. Positive: a block with the old route text reports `stale AGENTS.md`, setup replaces it with the lane line and keeps the role line; a hand-edited block reports `edited AGENTS.md` and is not overwritten without `--force`. Negative controls (both rejected): a template that keeps the old route, and `labels a stale block current`.
- Read-only run against `/Users/kimgranlund/Projects/maison/ui-kit-maison` (`onboard.py check` and `setup --dry-run`, nothing written; `git status --short` there showed no change from this run): `AGENTS.md` moves from `current` (before this change) to `stale`; `setup --dry-run` prints a diff for it.

## Limits

- Existing consumers see the new text only after they run `onboard.py setup` (or the `onboard` skill) again; nothing updates them on its own.
- The line names `steps.py` without a path, because a consumer's plugin lives in the plugin cache; it says the script is in the plugin's `scripts/` folder.
