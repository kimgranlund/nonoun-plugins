<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py`: everything for this step is in this file.
  - Templates: added `ENTRY_TEMPLATE` and `STAGE_TEMPLATES`, plus the `CLAUDE_IMPORT` and `GITIGNORE` constants.
  - Writer: added `entry_files()` and `write_entries(mbox)`. `cmd_send` and `cmd_reply` call `write_entries` after `compose` and before `deliver`.
  - Docstring: added an `Entry files` section, replaced the old Layout sentence about which folders each command creates, and changed the ignored-entries note to say "the entry files".
  - Selftest: added six `entry files:` cases with helpers, and extended `worktree: one shared mailbox`. In the race case, the leftovers check now skips the state-level `AGENTS.md`/`CLAUDE.md` (explained in Notes). Added `import shlex`.

## Checks
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: all 24 cases ok, `messages selftest: PASS`.
- Each acceptance criterion was run verbatim from the repo root:
  - AC1 (`.gitignore` and `CLAUDE.md` bytes, four `AGENTS.md`): exit 0.
  - AC2 (headings, no `{{`, rendered script path): exit 0.
  - AC3 (the three handle-section command tails): exit 0.
  - AC4 (required strings in the root `AGENTS.md`): exit 0.
  - AC5 (stage files: 3 lines, `../AGENTS.md`, their commands): exit 0.
  - AC6 (`reply` rewrites the removed entry files): exit 0.
  - AC7 (`count`, `list` and `expire` ignore the entry files): exit 0.
  - AC8 (the six selftest labels and PASS): exit 0.
  - AC9 (a copied file passes its selftest, then fails after the `ack` to `acknowledge` sed): exit 0. A manual rerun shows the failing case is `entry files: every command parses` (`acknowledge --help exited 2`).
  - AC10 (`Entry files` line in `--help`): exit 0.
  - AC11 (old sentence gone from `--help`): exit 0.
  - AC12 guard (refused sends leave no mailbox): exit 0.
  - AC14 guard (no em dash in added lines, with `SDLC_BASE_SHA` set to caf98aa): exit 0.
  - AC15 guard (only `messages.py` changed outside `.sdlc`): exit 0.
- AC13 guard `bash plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, `run selftest: PASS`.
- Extra checks: `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `git diff --check` clean.

## Notes
- **Change to an existing case.** `race: one winner` failed with entry files present, because it walks `new/` and `done/` for leftover files and found the generated `new/AGENTS.md` and `CLAUDE.md`. Its leftovers check now skips exactly `AGENTS.md` and `CLAUDE.md` sitting directly in a state folder. Files inside receiver folders still count, so a torn claim is still caught.
- **Handle-section wording.** The three steps are prefixed "Claim it:", "Only when `follow_up_requested: true`, reply:" and "Acknowledge it:". Each holds exactly the three required `python3` spans, in order.
- **How the selftest runs the commands.** `entry files: every command parses` and the two scripted-run cases run the generated commands as written: `python3` from PATH plus the rendered absolute path. `<path>` is substituted with `shlex.quote`. The parses case also requires that the entry files together use all seven subcommands (`send`, `list`, `read`, `ack`, `reply`, `expire`, `count`).
- **Docstring names a later step.** The `Entry files` section says `tickets.py roadmap` writes the same files, as the handoff asked. That writer is step 2 and is not implemented yet.
