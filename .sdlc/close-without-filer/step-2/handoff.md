## Task goal
A ticket whose work was done by other tickets can be closed with a stated reason, without a filer file.

## Step 2: Update docs and records
level: L1
### Do
- `plugins/sdlc-lite/skills/ticket/SKILL.md`:
  - Add `[--reason "<text>"]` to the `close` part of `argument-hint` (line 4).
  - Extend the line 12 close item: `--reason "<text>"` closes a ticket finished by other work, skips the filer, files no follow-ups, and appends a `## Closed` section.
- Repo-root `CLAUDE.md`, `tickets.py` bullet (line 25): mention `close <slug> --reason "<text>"`.
- `.claude/agents/sdlc-lite-author.md`, line 16 area: add one clause saying to keep `--reason` in sync across tickets.py, the /ticket skill and CLAUDE.md.
- Leave `skills/file/SKILL.md` alone. It needs no pointer.
### Acceptance criteria
- `grep -c -- '--reason' plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` shows at least 1 in each file.
- `plugins/sdlc-lite/scripts/check.sh` passes. Only the expected CLAUDE.md validate warning is allowed.
- `git diff --stat` touches only the four files named in the two steps, plus `.sdlc` if the ticket was closed.
