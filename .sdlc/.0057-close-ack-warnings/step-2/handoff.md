## Task goal
A resolved filer warning can be acknowledged with a reason instead of a blanket --force.

## Step 2: Sync docs for `--ack-warnings`
level: L1
### Do
- `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1: replace the open-warnings sentence. On a refusal for open Warnings, show the warnings and ask with AskUserQuestion, with three options:
  - "Leave open" (recommended, first): stop.
  - "Acknowledge with a reason": the user supplies the why, then add `--ack-warnings "<why>"` to every later call (dry run and real close).
  - "Force close": add `--force` to every later call.

  Also state that an unattended run stops on open warnings and never acks or forces.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`:
  - `argument-hint`: add `[--ack-warnings "<why>"]`.
  - Item 4: add a sentence covering what `--ack-warnings "<why>"` does, what it refuses, and its dry-run behavior. It closes while warnings are open, files follow-ups normally, and appends a `## Closed` section with the date, the reason and the quoted warnings. It refuses with `--force` or `--reason`, with empty text, or when no warnings are open. With `--dry-run` it passes the gate and writes nothing.
- Repo `CLAUDE.md`, the `scripts/tickets.py` paragraph under Layout: add one clause for `close --ack-warnings "<why>"`, with the same facts and in the same style as the `--reason` clause.
- `.claude/agents/sdlc-lite-author.md` line 16: add a sentence keeping `--ack-warnings` in sync across tickets.py, the /ticket skill, the /file skill, and CLAUDE.md.
- No em dashes in any edited text.
### Acceptance criteria
- `grep -c -- "--ack-warnings" plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` reports at least 1 for every file.
- `grep -n "Acknowledge with a reason" plugins/sdlc-lite/skills/file/SKILL.md` matches, and on that step the options appear in this order: "Leave open", then "Acknowledge with a reason", then "Force close".
- `grep -n "never acks or forces\|never ack" plugins/sdlc-lite/skills/file/SKILL.md` matches, because the unattended rule is stated.
- `grep -nP "\x{2014}" <edited files>` finds no new em dashes on the changed lines (`git diff | grep -P "^\+.*\x{2014}"` is empty).
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only warning allowed is the existing validate warning about CLAUDE.md.
