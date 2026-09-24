## Task goal
Add an opt-in numbered-folder mode (`NNNN-<slug>`) to `scripts/tickets.py`'s `new`, `close`, and `check`, keeping plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/ticket-numbered-folders/handoff.md

## Step 2: Numbered `close` follow-ups
level: L2
### Do
In the same file, add `--numbered` to the `close` subparser and thread `numbered` through `cmd_close` (same on/off rule as Step 1: flag or `<root>/config`). When on, each follow-up ticket created from a `## Follow-ups` bullet gets a numbered folder `{its-own-new-id:04d}-<base-slug>` instead of a bare `<base-slug>`, using each follow-up's own freshly stamped id (not the parent's id being closed). Keep the "plan everything first" no-partial-write structure and the existing collision-avoidance behavior (append `-2`, `-3`, ... on a name clash), now checked against the final numbered directory name. `close`'s own folder argument continues to be read as-is from disk (a plain or already-numbered name); this step is only about follow-up tickets it creates. Plain mode (no flag, no config) must remain byte-for-byte identical to today.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes, including a new case that closes a ticket with `--numbered` (or config) on and multiple `## Follow-ups` bullets, and asserts each created follow-up folder matches `^\d{4}-` with digits equal to that follow-up's own stamped `id`.
- A selftest case confirms `close` without `--numbered`/config still creates bare-slug follow-up folders exactly as before (negative control / no regression on existing close cases (a)-(h)).

## Risks (from the plan)
Compute each new id once and derive the folder name from it; check existence against the final (numbered) directory name. A missing `<root>/config` means plain mode with no error; cover that in selftest.

## Notes from step 1
- `stamp()` already takes `numbered=False` and checks existence against the final folder name; `folder_name(slug, tid, numbered)` and `config_numbered(root)` exist. `cmd_close` still calls `stamp()` without `numbered`.
- The double-prefix guard lives only in `cmd_new`; a follow-up slug derived from a title that starts with four digits and a dash should not end up double-prefixed.
