<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0099: Opt-in numbered ticket folders (NNNN-<slug>)

## PR body
### Summary
Adds an opt-in numbered-folder mode to `scripts/tickets.py`. When it is on, `new` and `close` name each ticket folder `NNNN-<slug>` from the id they stamp, and `check` fails when a folder's `NNNN-` prefix does not match its front matter id. You turn it on for one call with `--numbered` on `new`, `close`, or `check`, or for the whole repo with a `ticket_folders: numbered` line in `<root>/config`. Plain slugs are still the default and behave exactly as before.

The first attempt at step 3 was blocked, and the step was replanned. An always-on prefix rule rejected digit-led plain slugs such as `0007-gamma`, which the constraints keep legal. The replanned rule runs only in numbered mode.

### Changes
1. **Numbered `new` and config parsing** (`tickets.py`)
   - Added `config_numbered(root)` and `folder_name(slug, tid, numbered)`.
   - `stamp()` now works out the id before it names the folder.
   - In numbered mode, `new` refuses a slug that already starts with `NNNN-`, because the tool adds the prefix itself.
2. **Numbered `close` follow-ups** (`tickets.py`)
   - Each follow-up folder gets `NNNN-<base>` from its own new id.
   - Name-clash suffixes (`-2`) are checked against the final numbered name.
   - A leading `NNNN-` in the base slug is dropped so the prefix is never doubled.
3. **Prefix/id rule in `check`, numbered mode only** (`tickets.py`)
   - `problems(ts, numbered)` enforces that folder `NNNN-` carries id `T-NNNN`.
   - `check` gains `--numbered` and also reads the config.
   - `new` and `close` pass the mode to their `problems()` calls.
   - Running with no subcommand still works.
4. **Docs**
   - `skills/ticket/SKILL.md`: `[--numbered]` added to the argument hint, plus one new rule.
   - Repo `CLAUDE.md`: the `tickets.py` bullet now describes numbered mode.
   - `sdlc-lite-author.md` and `board.py` are unchanged.

### Verification
Every step passed its independent verifier.

- **Step 1 (verifier L2):**
  - The selftest passes, and each new case failed at least once under deliberate code mutations: numbering always off, double-prefix guard removed, config ignored, guard applied in plain mode, config match loosened.
  - The CLI created `0001-foo` with `T-0001`, refused `0009-baz` with nothing written, and read the config correctly.
  - Plain mode was diffed against HEAD's script: output files, stdout, stderr and exit codes were identical.
- **Step 2 (verifier L1):**
  - The selftest passes with case (i): numbered close by flag and by config, and a plain-mode control that keeps bare slugs.
  - A mutated copy with numbering forced off went red.
- **Step 3 (verifier L2):**
  - The selftest passes.
  - Two mutations went red: one disabled the rule, the other made it always on.
  - In the CLI, `check --numbered` flagged `0001-foo: folder prefix 0001- does not match id 'T-0009' (want T-0001)` with rc 1, while plain `check` stayed rc 0.
  - `--root .sdlc check` and the no-subcommand form both printed `ok: 21 tickets, roadmap current`, matching HEAD.
- **Step 4 (verifier L1):**
  - The doc greps match, and the same greps against HEAD give 0, so they can go red.
  - Selftest, `scripts/check.sh`, and the repo ticket check all exit 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py`: new opt-in numbered ticket folders. Turn them on with `--numbered` on `new`, `close`, or `check`, or with `ticket_folders: numbered` in `<root>/config`. Folders are named `NNNN-<slug>` from the stamped id, and `check` flags a prefix that does not match the id. Plain slugs are still the default and unchanged.

## Follow-ups
- tickets.py `roadmap` does not apply the numbered prefix/id rule, so with `ticket_folders: numbered` on it can regenerate `roadmap.md` while `check` fails
- Numbered-mode `new` and `close` refuse when any existing `NNNN-` folder has a mismatched id, not only the ticket being written; decide whether to limit the refusal to the written ticket
- Planner criteria that grep for selftest labels should grep the source form (e.g. `numbered_ok('new --numbered'`), not the runtime-rendered label, which is not literal text in `tickets.py`
