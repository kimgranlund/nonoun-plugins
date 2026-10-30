## Task goal
Closing a ticket in numbered mode never leaves main with broken references to its folder.

## Step 2: Sync the docs and the /file flow with the reference refusal
level: L2
### Do
Document the refusal, `--rewrite-refs` and the `--force` escape wherever the numbered-mode dot-prefix rule is already described:
- `CLAUDE.md`: the `scripts/tickets.py` bullet, and the `close` numbered-mode sentence.
- `plugins/sdlc/skills/ticket/SKILL.md`: the numbered-folders bullet.
- `plugins/sdlc/skills/handoff-format/SKILL.md`: the `.NNNN-<slug>` lines near 23 and 47.
- `.claude/agents/sdlc-lite-author.md`: add `--rewrite-refs` and the reference refusal to the sync line for the numbered-mode dot-prefix rule. Include the /file skill in that line.

In `plugins/sdlc/skills/file/SKILL.md` step 3.1, add a branch for when the dry run refuses because files cite the ticket folder. Show the listed files, then ask with AskUserQuestion, options in this order:
1. "Rewrite references" (recommended): add `--rewrite-refs` to every later call.
2. "Leave open": stop.
3. "Close anyway": add `--force` to every later call.

An unattended run stops on this refusal and never rewrites or forces. No silent rewrite. Change no code.
### Acceptance criteria
- `grep -qF -- '--rewrite-refs' CLAUDE.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/ticket/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/file/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/handoff-format/SKILL.md`
- `grep -qF -- '--rewrite-refs' .claude/agents/sdlc-lite-author.md`
- `grep -q 'Rewrite references' plugins/sdlc/skills/file/SKILL.md`
- (guard) `plugins/sdlc/scripts/check.sh`
- `git diff --quiet HEAD~1 -- plugins/sdlc/scripts/tickets.py` after the step's commit: this step changes no code. If the step does not commit, `git diff --quiet HEAD -- plugins/sdlc/scripts/tickets.py` holds instead.
