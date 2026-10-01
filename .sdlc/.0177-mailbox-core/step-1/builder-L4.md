<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py` (new, untracked): the mailbox CLI with `send`, `list`, `read`, `ack`, `reply`, `expire` and `count`. It has the global `--root`, root resolution through `git rev-parse --git-common-dir`, schema validation, the `fcntl.flock` mailbox lock, the rename claim, and a module docstring that `--help` prints (usage, layout, root, schema, reply rule, trust rule, transition table). It uses only the standard library and runs on Python 3.9.6. There is no `selftest`; that is step 2.

## Checks
- All 13 acceptance criteria, pulled verbatim from the handoff and run from the repo root with `bash c<N>.sh`: every one exited 0 with no output. I ran the full set twice, the second time after a small temp-file cleanup fix in `deliver`.
  - Criterion 11 (worktree) ran with the role's `SDLC_TMP_WORKTREES`. I then removed `$SDLC_TMP_WORKTREES/mbox-wt`, and the directory is now empty.
  - Criterion 13 (guard): passed. The only change outside `.sdlc` is `messages.py`.
- Negative control: I made a mutant copy with the `ack` follow-up gate replaced by `if False:` and ran criterion 5 against it. It exited 1, so that criterion catches a missing gate.
- Extra probes in throwaway repos, all as intended:
  - Usage errors exit 2: no subcommand, missing body, the abbreviations `--rec` and `--ro`.
  - Bad input exits 1 with one stderr line and no traceback: ttl `0d`, `5x`, `999999999d` and empty; an invalid `--now`; a bad `--kind`; a 41-character name; a non-UTF-8 body or topic; a topic with outer whitespace, a tab, or 201 characters.
  - Sending from a subdirectory lands in the top-level mailbox. Outside git the mailbox is `./.sdlc/messages`. `--root` works.
  - In a detached worktree of a bare repo (under `$SDLC_TMP_WORKTREES`, then removed), `git status --porcelain --ignored` stays empty after `count`, `list` and `expire`.
  - Six concurrent `read` calls on one message: one wins, five exit 1 with `already claimed`.
  - With the time pinned, a clashing id gets `-2`, then `-3` in another receiver's folder, and no temp file is left behind.
  - These are ignored: `AGENTS.md` files, temp files, folders with invalid names, and a symlinked message file.
  - A hand-written file with keys out of order is refused by `count` and `read`.
  - Reading an empty body prints nothing between the markers.
- `git diff --check`: clean. The file has no non-ASCII bytes and no trailing whitespace.

## Notes
- Choices where the handoff was silent:
  - Front matter keys must appear in the canonical order, otherwise the file is invalid (`keys out of order`).
  - `key: ` with a trailing space and no value is malformed.
  - A message file must be a regular file; symlinks are ignored.
  - Files over 16384 bytes are invalid.
  - The marker-line check compares each stripped line from `str.splitlines()`.
  - `--ttl` must be 1 to 9 digits and greater than zero.
  - `ack` on a missing mailbox refuses with `not found` and creates nothing.
  - An empty body gets no added newline in `read` output.
- In path mode, `read` also accepts a path that points elsewhere in the same mailbox and then gives the id-based refusal (`already claimed`, `already done`, `not the receiver`). It still succeeds only when the realpath is in `new/<receiver>/`.
- For step 2: the claim is the single function `claim(src, dst)`, which is where the `SDLC_MESSAGES_TEST_*` hooks go. The time source is `utcnow()`.
- On macOS's case-insensitive filesystem, `new/Bob` and `new/bob` are the same folder. That comes from the filesystem, not from `messages.py`.
- One scratch directory with my copies of the criteria and their outputs is left in the system temp dir (`/var/folders/.../T/tmp.l5rWNuIrn4`); the request to remove it was denied. It is outside the repo.
