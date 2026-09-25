<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0026: tickets.py: check warns on unpersisted numbered folders, close --numbered persists the mode

## PR body
### Summary
Plain `tickets.py check` now prints a warning when every ticket folder has an `NNNN-` prefix but `<root>/config` has no `ticket_folders: numbered` line. The warning does not fail the check. `close --numbered` now writes that config line, as `new --numbered` already does. This PR also covers T-0027.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - `cmd_check`: when not in numbered mode and every folder in a non-empty root matches `PREFIX_RE`, a second stdout line starting with `warning:` tells the user how to persist the mode. The exit status stays 0, and the failure paths are unchanged.
  - `cmd_close`: calls `ensure_numbered_config` only after a successful close, and only when `--numbered` was passed. A refused close writes nothing.
  - The usage docstring's `check` and `close` lines are updated.
  - New selftest cases:
    - All-numbered folders with no config: `check` warns.
    - No warning with the config line present, with plain slugs, with mixed folders, or with an empty root.
    - A plain close writes no config.
    - `close --numbered` writes the config line.
    - A refused `close --numbered` writes nothing.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` and `CLAUDE.md`: the numbered-mode text now covers persistence by `close --numbered` and the new `check` warning.
- `.claude/agents/sdlc-lite-author.md`: one new Invariants line on numbered-mode persistence, the `check` warning, and keeping tickets.py, /ticket and CLAUDE.md in sync.

### Verification
- Step 1 (verifier L1: pass)
  - `tickets.py selftest` passes.
  - The verifier reverted each change in a separate copy of the script. Without the close persist, selftest failed on `(j) close --numbered writes config`. Without the check warning, it failed on `all-numbered folders, no config: check warns`.
  - Temp root with `0001-a`, `0002-b` and no config: `check` exits 0 and prints the warning. After adding the config line, the warning is gone.
  - A plain-slug fixture prints no warning.
- Step 2 (verifier L1: pass)
  - `grep "close --numbered"` and `grep warn` match in both SKILL.md and CLAUDE.md.
  - The author agent file has a `numbered` line.
  - All three greps fail at HEAD. One exception: the CLAUDE.md side of the `warn` grep already matched line 11 before this change.
  - No em dashes in the edited files.
  - `check.sh` exits 0, confirmed by its own exit status.

### Risks
When the warning fires, `check` prints two lines instead of one. The existing exact-match asserts still pass because none of their fixtures have only numbered folders.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py check` warns, without failing, when every ticket folder has an `NNNN-` prefix but `<root>/config` lacks `ticket_folders: numbered`. `close --numbered` now persists that line, like `new --numbered`. (T-0026, T-0027)

## Follow-ups
- tickets.py: the numbered-folder warning in `check` gives a false positive when every plain slug starts with 4 digits and a hyphen (e.g. `2024-plan`); consider requiring the prefix to match the ticket's front matter id
- tickets.py: the argparse `--numbered` help text for `close` does not mention that it persists `ticket_folders: numbered` to `<root>/config`
- T-0026 step 2 acceptance check `grep warn CLAUDE.md` can never fail because CLAUDE.md line 11 already contains "warning"; tighten it to match the new check-warning wording
