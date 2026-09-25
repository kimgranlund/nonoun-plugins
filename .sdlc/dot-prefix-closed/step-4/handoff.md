## Task goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Step 4: Docs describe dot-prefix closed folders and `archive`
level: L1
### Do
Update the records that describe tickets.py behavior:
- `/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets9/CLAUDE.md`, the Layout `scripts/tickets.py` line:
  - in numbered mode, `close` renames `NNNN-<slug>` to `.NNNN-<slug>`
  - every tool treats a `.NNNN-<slug>` folder as a closed ticket
  - `check` fails on a dot folder that is not done or dropped
  - `archive [--dry-run]` renames existing done/dropped numbered folders
  - `_templates` and other dot entries stay skipped
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add `archive [--dry-run] [--numbered]` to `argument-hint`, and extend the numbered-folders rule to match.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block (lines about 9 to 24), add a `.sdlc/.NNNN-<slug>/` closed-ticket entry. In the Ticket front matter paragraph, add the close rename.
- `plugins/sdlc-lite/skills/file/SKILL.md`, step 4: add one clause saying that in numbered mode the folder becomes `.NNNN-<slug>` after close.
- `.claude/agents/sdlc-lite-author.md`, Invariants: add the dot-prefix close/archive rule to the numbered-mode sync line.

Use no em dashes.
### Acceptance criteria
- `grep -n '\.NNNN-' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md .claude/agents/sdlc-lite-author.md` finds at least one hit in each file.
- `grep -n 'archive' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md` finds a hit in each.
- `grep -rn '—' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/skills/file/SKILL.md .claude/agents/sdlc-lite-author.md` prints nothing.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.
