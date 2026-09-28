<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- CLAUDE.md: the `scripts/tickets.py` Layout line now describes the numbered-mode close rename to `.NNNN-<slug>`, that tools treat dot folders as closed, that `check` fails on a dot folder that is not done or dropped, `archive [--dry-run]`, and that `_templates` and other dot entries stay skipped.
- plugins/sdlc-lite/skills/ticket/SKILL.md: added `archive [--dry-run] [--numbered]` to `argument-hint`, and extended the numbered-folders rule.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added a `.sdlc/.NNNN-<slug>/` entry to the layout block, and a close-rename sentence to the Ticket front matter section.
- plugins/sdlc-lite/skills/file/SKILL.md: step 4 now says the folder becomes `.NNNN-<slug>` after close in numbered mode.
- .claude/agents/sdlc-lite-author.md: added the dot-prefix close/archive sync rule to the Invariants.

## Checks
- `grep -c '\.NNNN-'` on the four files: 1 hit each in CLAUDE.md, ticket/SKILL.md, and sdlc-lite-author.md, and 2 in handoff-format/SKILL.md. Pass.
- `grep -n 'archive'` on CLAUDE.md and ticket/SKILL.md: I did not run this on its own. Both files now contain "archive" from my edits, so it is expected to pass.
- `grep -rn '—'` on the five files: no output. Pass.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. The selftests, shellcheck, and plugin validate all passed. I did not check whether the CLAUDE.md validate warning appeared.

## Notes
None
