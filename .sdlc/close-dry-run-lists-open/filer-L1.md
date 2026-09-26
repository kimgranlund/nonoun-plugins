<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0079: close --dry-run also lists open tickets from other worktrees

## PR body
### Summary
`tickets.py close <slug> --dry-run` used to list open tickets from the local `--root` only. That meant `/file` could not tell when a follow-up duplicated an open ticket in a parallel worktree. The dry run now also lists proposed, ready, and blocked tickets that exist only in another git worktree's same-relative ticket root, one line each: `open T-NNNN <title> [<slug>] (worktree <name>)`. Follow-up from T-0066.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - New `worktree_pairs(root)` returns (worktree dir, root) pairs. `worktree_roots` now wraps it, and its existing callers work as before.
  - In the `cmd_close` dry run, other-worktree open lines print after the local open lines and before the rename and ack lines.
  - The worktree name is the basename of that worktree's toplevel.
  - An id that exists locally, at any status, is decided by the local copy only.
  - Each id is listed once across other worktrees. The first worktree in `git worktree list` order wins.
  - Other-worktree tickets are skipped when they are the closing ticket, have a bad id, or have a status other than proposed, ready, or blocked.
  - If another tree's tickets fail to load, that tree is skipped.
  - Local lines are byte-identical to before, and the `expect <digest>` value is unchanged. Outside git the output is unchanged. The dry run still writes nothing.
  - The module docstring and the `--dry-run` help describe the new lines.
  - New selftest cases: a sub-repo with a second worktree (fixture `wtdr`), and an outside-git case.
- Docs now say the dry-run listing covers other worktrees, including the literal `(worktree <name>)`:
  - `plugins/sdlc-lite/skills/file/SKILL.md`: step 1.1, plus step 1.2's likely-duplicate comparison.
  - `plugins/sdlc-lite/skills/ticket/SKILL.md`: item 4.
  - `CLAUDE.md`: the Layout bullet for `scripts/tickets.py`.
  - `.claude/agents/sdlc-lite-author.md`: line 17.

### Verification
- Step 1 (verifier L1, pass):
  - Scratch repo with a main tree and worktrees `wt` and `wt2`. The dry run printed exactly 4 lines. Delta had no suffix and Gamma appeared once as `(worktree wt)`. Beta (done locally, open in the worktree copies) was not listed, and the digest was `e3b0c44298fc`.
  - Outside git, the output matched the old output exactly.
  - `tickets.py selftest` passed.
  - Mutation check: with the other-worktree lines removed, the selftest printed FAIL and named the worktree dry-run case. The exit code was not captured directly.
- Step 2 (verifier L1, pass):
  - Each of the four docs contains `(worktree <name>)`. Each grep was red at HEAD and green in the tree.
  - The `open T-NNNN` and `likely duplicate` strings that `check.py` requires are still there.
  - No em dashes were added.
  - `scripts/check.sh` exited 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close --dry-run` now also lists open tickets that exist only in another git worktree, as `open T-NNNN <title> [<slug>] (worktree <name>)`, so `/file` can spot follow-ups that duplicate parallel work. Local lines and the `expect` digest are unchanged. (T-0079)

## Follow-ups
- tickets.py selftest checks that the `close --dry-run` expect digest ignores other-worktree open lines only when there are no follow-ups (fixed `e3b0c44298fc`); add a case with follow-ups present so the digest guarantee is actually tested.
