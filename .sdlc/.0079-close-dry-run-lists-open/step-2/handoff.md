## Task goal
`tickets.py close <slug> --dry-run` also lists proposed, ready, and blocked tickets that exist only in another git worktree's same-relative ticket root, so `/file` can spot a follow-up that duplicates open work in a parallel worktree.

## Step 2: Docs say the dry-run open listing covers other worktrees
level: L1
### Do
State that `close --dry-run` also lists open (proposed, ready, blocked) tickets that exist only in another git worktree's same-relative ticket root, as `open T-NNNN <title> [<slug>] (worktree <name>)` after the local lines, with a local copy deciding any id it holds. Include the literal `(worktree <name>)` text in each place:
- `plugins/sdlc-lite/skills/file/SKILL.md` step 1.1 (line 12), where it describes the `open T-NNNN` lines. Also let step 1.2's likely-duplicate comparison cover these lines. Keep the existing `open T-NNNN` and `likely duplicate` strings that `check.py` requires.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` item 4 (line 12), in the `--dry-run` sentence.
- `CLAUDE.md` Layout, `scripts/tickets.py` bullet, in the `close --dry-run lists ... open T-NNNN <title> [<slug>] line per other proposed, ready, or blocked ticket` clause.
- `.claude/agents/sdlc-lite-author.md` line 17, in the sentence "Keep `close --dry-run`/`--skip`/`--expect`, ... the dry run's `open T-NNNN` listing ...". Add that the listing includes other worktrees' open tickets as `(worktree <name>)`.

Make no code changes. No em dashes.
### Acceptance criteria
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/file/SKILL.md`
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF '(worktree <name>)' CLAUDE.md`
- `grep -qF '(worktree <name>)' .claude/agents/sdlc-lite-author.md`
- (guard) `grep -qF 'open T-NNNN' plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md | grep '^+' | grep -q '—'` (no em dashes added)
