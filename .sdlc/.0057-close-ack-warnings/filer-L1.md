<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0057: close --ack-warnings records why stale filer warnings no longer apply

## PR body
### Summary
Before this change, if a ticket's filer file still had open Warnings, `tickets.py close` refused to close it, and `--force` was the only way past. A warning can go stale (for example "nothing committed yet" after the work was committed). The new `close --ack-warnings "<why>"` closes the ticket anyway and writes down the reason. Follow-ups are still filed as in a normal close.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - New `--ack-warnings TEXT` option on `close`. It passes the open-warnings gate and appends a `## Closed` section to the ticket handoff.md. The section holds the date, `warnings acknowledged: <why>`, and each Warnings line quoted verbatim with `> `. In numbered mode the section is written before the archive rename.
  - Follow-up filing works as before: duplicates, `--skip`/`--expect` and numbered archive are unchanged. The success message ends with `; warnings acknowledged: <why>`.
  - `--dry-run --ack-warnings` passes the gate, prints an `ack warnings:` line and writes nothing. `expect <digest>` stays the last line.
  - It refuses and writes nothing in these cases: combined with `--force`, combined with `--reason`, empty or whitespace-only text, or no open warnings (the error says to rerun without `--ack-warnings`).
  - The open-warnings refusal now names `--ack-warnings "<why>"` first and `--force` second.
  - Updated the usage docstring, argparse help and close subparser help.
  - Selftest: case (b) has a new assert, and new cases (w1) to (w9) cover the flag.
- `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1: when warnings are open, the skill asks with AskUserQuestion: "Leave open" (recommended), "Acknowledge with a reason" or "Force close". An unattended run stops and never acks or forces.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `argument-hint` and item 4 now document the flag.
- `CLAUDE.md`: new `--ack-warnings` clause in the tickets.py paragraph, next to the `--reason` clause.
- `.claude/agents/sdlc-lite-author.md`: new sentence keeping the flag in sync across tickets.py, /ticket, /file and CLAUDE.md.

### Verification
- Step 1 (verifier L2: pass)
  - `tickets.py selftest` prints PASS.
  - Negative control in a throwaway worktree: with the ack gate turned into a no-op, the selftest fails on (w1), (w2), (w7), (w8) and (w9).
  - Manual temp-dir run of `close demo --ack-warnings "committed later"`:
    - exit 0 and `status: done`
    - one proposed idea ticket `add-retry`
    - the handoff ends with `## Closed`, `2026-09-25: warnings acknowledged: committed later` and `> nothing committed yet`
  - Refusals in the same temp setup, checked with sha256 tree snapshots:
    - plain `close` exits 1 and stderr names `--ack-warnings` before `--force`
    - `--ack-warnings x --force` exits 1 and changes no files
    - whitespace-only text exits 1 and changes no files
  - `close --help` lists `--ack-warnings TEXT`; at HEAD it does not.
  - `check.sh` exits 0.
- Step 2 (verifier L1: pass)
  - All four doc files contain `--ack-warnings`; at HEAD none do.
  - The three /file options appear in the required order, and the unattended rule is stated.
  - The diff adds no em dashes (the grep pattern was checked against a positive control).
  - `check.sh` exits 0 with no warning lines.
  - The doc text matches the step-1 code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `tickets.py close --ack-warnings "<why>"`: closes a ticket whose filer Warnings are open but stale and files its follow-ups as normal. It records the reason and the quoted warnings in a `## Closed` section. It refuses with `--force` or `--reason`, with empty text, or when no warnings are open. `/file` now offers it as an option when warnings are open.

## Follow-ups
None
