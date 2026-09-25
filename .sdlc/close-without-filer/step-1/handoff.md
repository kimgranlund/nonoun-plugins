## Task goal
A ticket whose work was done by other tickets can be closed with a stated reason, without a filer file.

## Step 1: Implement `--reason` in tickets.py, with selftest cases
level: L2
### Do
Edit `plugins/sdlc-lite/scripts/tickets.py`.
- `cmd_close(root, slug, force=False, numbered=False, reason=None)`: accept a `reason`.
- After the existing already-done check (line ~404), branch on `reason is not None`, which skips the filer lookup and the warnings and follow-up handling:
  - If `reason.strip()` is empty, raise `Fail` ("empty --reason ...; nothing written").
  - Compute the new `head` with the same status-line regex used at line 443. Raise `Fail` if there is no status line.
  - Write the handoff as `head + raw[fm.end():]`, with a `\n## Closed\n\n<YYYY-MM-DD> (<date.today().isoformat()>): <reason.strip()>\n` section appended to the end of the body. Make sure a newline separates it from the existing text.
  - Call `write_roadmap(root, load(root))`, and `ensure_numbered_config(root)` if `flag` is set.
  - Return `f'{pid} done (closed by reason: <reason>); no follow-ups filed'`.
  - Existing refusals for slug, not a ticket, problems and already-done come first. Each writes nothing, and the order stays as is.
- Refactor `fm`/`head` so both paths share them if that is simple.
- `--force` with `--reason` is accepted and has no effect.
- `main`: add `--reason` with `metavar='TEXT'` to the `close` parser, and pass it through. Change the `'close'` lambda to `(a.slug, a.force)` and put `reason` in `kw` for close, for example `kw['reason'] = a.reason`. Make sure `run(..., 'close', args, **kw)` still works when `reason` is None.
- Update the usage docstring (line 5 and the `close` paragraph) and the argparse help for `close`.
- Add selftest cases after (j), reusing the `case`, `filer`, `snap`, `status` and `run` helpers. Call `run(root, 'close', ('alpha',), reason='...')`:
  - (k) A case with no filer file, closed with a reason: rc 0, status done, `## Closed` and the reason are in the handoff, the output says "reason", and `check` passes.
  - (l) A filer with open warnings and follow-ups is ignored: rc 0, done, `fresh(root, {'alpha','beta'})` is empty, and no follow-up tickets exist.
  - (m) An empty reason and a whitespace-only reason each refuse with rc 1, and `snap(root)` is unchanged.
  - (n) A done ticket with a reason still refuses ("already closed"), and `snap(root)` is unchanged.
  - (o) `--force` together with a reason closes, and `--numbered` with a reason persists the config.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS`.
- Negative control: run `git stash push -- plugins/sdlc-lite/scripts/tickets.py`, or temporarily make `cmd_close` ignore `reason`. Then the new (k) to (o) cases are reported as misses and selftest fails. Restore the file afterwards.
- In a temp `.sdlc` with a ticket that has no filer file, `tickets.py --root <tmp> close alpha --reason "done by T-0002"` exits 0 and sets `status: done`. The handoff ends with a `## Closed` section containing today's date and the reason. `roadmap.md` is regenerated, and `tickets.py --root <tmp> check` passes.
- `close alpha --reason "  "` exits 1 and writes nothing.
- `close alpha` with no filer still refuses, mentioning `/file`, as before.

## Note from the conductor
For the negative control, never use git stash (the stash stack is shared with other worktrees and sessions). Copy tickets.py aside, edit the copy or temporarily neuter reason handling, run selftest, then restore the file.
