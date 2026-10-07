<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0153: Ticket depends can name a capability or file, not only a whole ticket

## PR body
### Summary
A ticket's `depends:` list now accepts `file:<path>` and `cap:<name>` entries as well as `T-NNNN`. Tickets can also declare an optional `provides: [name, ...]` list. A ticket can wait on the specific fix it needs, so it is not held behind a whole serial integration ticket. Existing `T-NNNN` tickets and their roadmap output are unchanged.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Each `depends` entry is classified as `T-NNNN`, `file:<path>` or `cap:<name>`. A `file:` path must be non-empty, relative, and free of `..`. A `cap:` name must match `[A-Za-z0-9][A-Za-z0-9._-]*`.
  - `provides` is an optional front matter list and is not in `REQUIRED`.
  - `check` now fails on a malformed entry, on a `cap:` that no ticket provides, and on a `provides` that is not a list or has a bad item. A `file:` path that does not exist yet is not an error.
  - `order()` makes a `cap:` entry wait on every ticket that provides it, so cycles through capabilities are still detected. `file:` entries add no ordering.
  - The roadmap marks an unmet `file:` or `cap:` entry `(unmet)` and escapes `|` in entries. File paths resolve against the git toplevel.
  - The module docstring covers all three forms and says to rerun `roadmap` when a named file appears or a provider closes.
  - New selftest cases.
- Docs: `skills/handoff-format/SKILL.md` (front matter block plus a paragraph on what satisfies each form), `skills/ticket/SKILL.md` (one Rules bullet), the five ticket templates (trailing comment on the `depends:` line only), and `docs/references/sdlc-internals.md` (one sentence).

Behavior changes to know about:
- A malformed entry such as `T-12` used to report "which no ticket has". It now gets the malformed-entry error.
- A ticket that both depends on `cap:x` and provides `x` is reported as a self-cycle.
- `render` now takes a required `root` argument. Its only callers are `write_roadmap` and `stale`, both in `tickets.py`.

### Verification
- Step 1 (verifier pass):
  - All 11 acceptance criteria ran with rc=0.
  - Criteria 1 and 4 fail at the base commit in a throwaway worktree, so those checks can go red.
  - A T-only roadmap is byte-identical to the base output (`cmp` rc=0).
  - `tickets.py selftest`, `board.py selftest` and `fanout.py selftest` pass.
  - `tickets.py --root .sdlc check` reports ok for 170 tickets.
  - The builder ran the selftest against 7 mutated copies of `tickets.py`, and it failed on each. The verifier did not re-run these.
- Step 2 (verifier pass):
  - The greps for `cap:<name>` and `provides:` pass on the built tree and fail at the base commit.
  - The template loop covers all 5 templates.
  - `tickets.py selftest`, `check.py` and `codex_roles.py generate --check` pass.
- Step 3 (verifier pass), gates on the final tree:
  - `bash plugins/sdlc-lite/scripts/check.sh` rc=0.
  - `check.py` rc=0.
  - `codex_roles.py generate --check` rc=0.
  - `scripts/check-packaging.py` rc=0.
  - `git diff --check` against the base commit rc=0.
  - The shellcheck part of `check.sh` was skipped because shellcheck is not installed, so it is unverified.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Ticket `depends:` now accepts `file:<path>` and `cap:<name>` entries alongside `T-NNNN`, and tickets may declare an optional `provides: [name, ...]`. `tickets.py check` rejects malformed entries and `cap:` names that no ticket provides. The roadmap orders a ticket after the providers of its `cap:` entries and marks unmet `file:` and `cap:` entries `(unmet)`. Existing `T-NNNN` tickets render unchanged.

## Follow-ups
- note: shellcheck is not installed on the build machine, so the shellcheck part of `check.sh` was skipped and is unverified.
- note: fanout lane scheduling does not read `depends`, so `file:` and `cap:` entries do not affect lane scheduling. The ticket lists this as a non-goal.
