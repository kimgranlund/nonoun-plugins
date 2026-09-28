<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: new `close <slug> [--force]` command with selftest cases (a) to (h), plus the helpers it uses (`section`, `bullets`, `is_none`, `stamp`). `cmd_new` gains optional `origin` and `context`. The module docstring, `run()` and argparse are wired for `close`, and `import os` is added for `os.utime`.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: printed `tickets selftest: PASS`, exit 0.
- Hand fixture with Warnings `None` and two bullets:
  - `close parent` exited 0 and printed `T-0001 done; 2 follow-up ticket(s): add-retry-to-fetch, document-the-flag`.
  - `grep -l '^from: T-0001' ... | wc -l` gave 2.
  - `grep '^status: done' $R/parent/handoff.md` matched.
  - `check` exited 0 (`ok: 3 tickets, roadmap current`).
- Hand fixture with Warnings `step-2 verifier fail`:
  - `close parent` exited 1, and stderr names `--force` and the warning text.
  - The parent still had `status: proposed`, and `$R` held only `parent` and `roadmap.md`.
  - `close parent --force` exited 0 and created 2 tickets, and `check` then passed.
- Negative control: I changed the warnings guard to `if False and ...`. `selftest` then printed FAIL (case (b), both expectations) and exited 1. I restored the file from a copy, and `selftest` passed again.
- `git diff --stat`: only `plugins/sdlc-lite/scripts/tickets.py` changed (236 lines added, 10 removed). The other untracked entry is the `.sdlc/0003-filer-follow-ups-to-tickets/` task dir.
- `plugins/sdlc-lite/scripts/check.sh`: all green (role levels, selftest, tickets selftest, shellcheck, plugin validate), exit 0.

## Notes
- `close` works out every new ticket (ids, slugs, text, validation) and the parent's new `status:` line before it writes anything. A refusal partway through therefore writes nothing.
- The `status: done` substitution only touches the front-matter block and keeps any trailing comment. It reads and writes raw bytes, so the rest of the file stays byte-identical. Selftest (a) checks this against a handoff whose body also has a `status:` line.
- Choices the handoff did not specify:
  - **Top-level bullet:** the marker must start at column 0 (`-`, `*`, `N.`, `N)`).
  - **Extra lines:** every non-blank line after a bullet joins that bullet's text, indented or not, so nothing after the first bullet is dropped. Text before the first bullet is treated as a lead-in and ignored.
  - **Follow-ups `None`:** matched the same way as Warnings (case-insensitive, trailing `.` stripped).
  - **Zero follow-ups:** the output line ends in `none` instead of an empty slug list.
  - **Slug check:** `close` rejects a slug that does not match the slug pattern.
- `cmd_new` checks things in the same order as before (slug, template, existing dir, ticket problems). The ticket-building logic now lives in `stamp()`, which `close` also uses.
- I added one extra selftest check beyond (h): on an mtime tie, the later file name wins.
