<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Add `tickets.py close <slug> --reason "<text>"` so a ticket finished by other work can be closed with a recorded reason and no filer file.

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

## Risks
- `cmd_close` is called as `run(root, 'close', (slug, force), numbered=..., reason=...)`. If `reason` is not passed cleanly as a keyword, or `run` mishandles it, the existing selftest call sites could break.
- The line 5 usage string is likely checked by `check.sh` or another test. Confirm nothing else parses it.
- `--reason ""` is falsy, so branch on `is not None`, not on truthiness. Otherwise an empty reason would fall through to the filer path instead of refusing.
