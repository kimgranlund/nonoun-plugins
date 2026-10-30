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

An unattended run stops on this refusal and never rewrites or forces. No silent rewrite.

Change no code. Step 1's `plugins/sdlc/scripts/tickets.py` change is uncommitted in the tree, because only a merge step commits, so `tickets.py` differs from HEAD by design: leave it exactly as step 1 left it, and never revert, restage, or commit it to satisfy a criterion. The tree may already hold these doc edits from a superseded attempt; then confirm each criterion, fix any gap, and report done.
### Acceptance criteria
- `grep -qF -- '--rewrite-refs' CLAUDE.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/ticket/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/file/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/handoff-format/SKILL.md`
- `grep -qF -- '--rewrite-refs' .claude/agents/sdlc-lite-author.md`
- `grep -q 'Rewrite references' plugins/sdlc/skills/file/SKILL.md`
- (guard) `bash plugins/sdlc/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only HEAD -- plugins/sdlc/scripts plugins/sdlc/hooks | grep -v '^plugins/sdlc/scripts/tickets.py$')"`: under `scripts/` and `hooks/`, the only file that differs from HEAD is step 1's `tickets.py`.
- (guard) `python3 plugins/sdlc/scripts/tickets.py close --help | grep -qF -- '--rewrite-refs'`: the flag the docs describe is in the tree's code, so step 1's change was not reverted to make `tickets.py` match HEAD.
- Observable: `git diff HEAD -- plugins/sdlc/scripts/tickets.py` holds only step 1's work: the `outside_refs` helper, the `rewrite_refs` kwarg with its refusal, rewrite, and dry-run `rewrite <file>` lines in `cmd_close`, the `--rewrite-refs` flag in the parser and `main`, the `(u) refs:` selftest cases, and the docstring and `Usage:` edits. No hunk in that diff does anything else. The verifier reads the diff itself and never compares `tickets.py` against a commit, because step 1's change stays uncommitted until the lane's merge.
