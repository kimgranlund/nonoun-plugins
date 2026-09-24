<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- The `SKILL.md` argument-hint has `[--numbered]` after `new`, `close` and `check`, plus one rule bullet naming `ticket_folders: numbered` and `NNNN-<slug>`: pass. Evidence: `grep -n "numbered" plugins/sdlc-lite/skills/ticket/SKILL.md` returned two lines. Line 4 is `argument-hint: new <type> <slug> "title" [--numbered] | close <slug> [--force] [--numbered] | roadmap | check [--numbered]`. Line 15 is the rule bullet under `Rules:` and contains both `ticket_folders: numbered` and `NNNN-<slug>`. The check can go red: `git show HEAD:plugins/sdlc-lite/skills/ticket/SKILL.md | grep -c numbered` gives 0. The doc claims match the code: `tickets.py` lines 831, 836 and 840 add `--numbered` to the three subcommands, and `CONFIG_RE` at line 46 reads the `ticket_folders: numbered` config line.
- `CLAUDE.md` has `ticket_folders: numbered` inside the `scripts/tickets.py` bullet: pass. Evidence: `grep -n "ticket_folders: numbered" CLAUDE.md` matched line 25, which is the `- \`scripts/tickets.py\`: backs \`/ticket\`...` bullet. The new sentence covers `--numbered` on `new`/`close`/`check`, `<root>/config`, `NNNN-<slug>` from the stamped id, `check` enforcing the prefix only in numbered mode, and plain slugs as the default. The check can go red: the same grep against `HEAD:CLAUDE.md` gives 0.
- `.claude/agents/sdlc-lite-author.md` and `board.py` are unchanged: pass. Evidence: `git diff --stat HEAD -- .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/scripts/board.py | wc -c` gives 0. The same command on `tickets.py` gives 132, so the command does detect changes.
- Selftest, `check.sh` and the repo ticket check exit 0: pass. Evidence:
  - `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exited 0 (`tickets selftest: PASS`).
  - `plugins/sdlc-lite/scripts/check.sh` exited 0: tickets and board selftests PASS, `ok: shellcheck`, `ok: plugin validate`, `ok: 21 tickets, roadmap current`.
  - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exited 0.

## Out of scope changes
None. `git diff --stat HEAD` also shows `plugins/sdlc-lite/scripts/tickets.py` (+257/-48) and `.sdlc/ticket-numbered-folders/handoff.md`. These come from steps 1 to 3 and the task's replan, as the handoff says (the steps are uncommitted working-tree changes). Step 4 touched only `CLAUDE.md` and `skills/ticket/SKILL.md`.

## For the next attempt
None
