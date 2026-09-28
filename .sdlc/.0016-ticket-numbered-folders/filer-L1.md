<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0016: Opt-in numbered ticket folders (NNNN-<slug>)

## PR body
### Summary
This adds an opt-in numbered-folder mode to `plugins/sdlc-lite/scripts/tickets.py`. You turn it on for a single call with `--numbered` on `new`, `close` or `check`. You turn it on for the whole repo with a `ticket_folders: numbered` line in `<root>/config`. In numbered mode:
- `new` names the folder `NNNN-<slug>` from the id it assigns.
- `close` does the same for each follow-up, and each follow-up gets its own id.
- `check` fails when a `NNNN-` folder's id is not `T-NNNN`.

Plain slugs stay the default, and plain-mode output is unchanged.

The first version of step 3 made the prefix check run in both modes. The builder stopped (status blocked) because that rule rejected plain-mode folders like `0007-gamma`, which the task's constraints keep legal. The step was replanned so the check runs only in numbered mode, and the replan passed.

### Changes
- **Step 1: config parsing and numbered `new`** (builder L3, verifier L2 pass)
  - New `config_numbered()` and `folder_name()` helpers.
  - `stamp()` works out the id once and checks that the final folder name doesn't already exist.
  - In numbered mode, `new` refuses a slug that already starts with `NNNN-`, so the prefix can't be doubled.
- **Step 2: numbered `close` follow-ups** (builder L2, verifier L1 pass)
  - Each follow-up gets `NNNN-<base>` from its own new id.
  - A name clash is checked against the numbered name and gets `-2`, `-3` and so on.
  - A leading `NNNN-` is stripped from the base slug.
- **Step 3: prefix/id check, numbered mode only** (replanned at planner L3; builder L3, verifier L2 pass)
  - `problems(ts, numbered)` gets the new rule.
  - `check` accepts `--numbered` and also reads the config.
  - `new` and `close` in numbered mode apply the rule and refuse if an existing folder breaks it.
  - Running with no subcommand still works: the flag is read with `getattr`.
- **Step 4: docs** (builder L1, verifier L1 pass)
  - `skills/ticket/SKILL.md`: the argument hint and one new rule bullet.
  - Repo `CLAUDE.md`: the `tickets.py` bullet.
  - `sdlc-lite-author.md` and `board.py` are untouched.

### Verification
- **Selftest:** `tickets.py selftest` passes. It has new cases for numbered `new` (by flag and by config), the double-prefix refusal, numbered `close` follow-ups including a name clash, the prefix mismatch (by flag and by config), and plain-mode controls.
- **Checks can fail:** the verifiers ran broken copies of the script and each one failed the selftest:
  - rule removed
  - rule applied in both modes
  - folder never numbered
  - double-prefix guard removed
  - config ignored
- **Plain mode unchanged:** the step 1 verifier ran the same plain-mode commands with the HEAD script and the new script. The produced files, stdout, stderr and exit codes were identical. The step 3 verifier got the same `check` output from both scripts on this repo's `.sdlc`.
- **CLI run in a temp dir:** `new --numbered` made `0001-foo` with id `T-0001`. After the id was changed to `T-0009`, `check --numbered` exited 1 with `0001-foo: folder prefix 0001- does not match id 'T-0009' (want T-0001)`, while plain `check` still passed.
- **Repo checks:** `scripts/check.sh` exits 0. `tickets.py --root .sdlc check` prints `ok: 21 tickets, roadmap current`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py`: opt-in numbered ticket folders. Use `--numbered` on `new`, `close` or `check`, or add `ticket_folders: numbered` to `.sdlc/config`. `new` and `close` then name folders `NNNN-<slug>` from the id they assign, and `check` fails when a folder's prefix doesn't match its id. Plain slugs are still the default and behave as before.

## Follow-ups
- tickets.py `roadmap` skips the numbered prefix/id check, so with `ticket_folders: numbered` set it can rebuild the roadmap while `check` fails
- In numbered mode, tickets.py `new` and `close` refuse when any existing `NNNN-` folder has the wrong id, not only the ticket being written; confirm this is the intended scope
