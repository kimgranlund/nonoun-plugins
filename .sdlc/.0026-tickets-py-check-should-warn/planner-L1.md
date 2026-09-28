<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
`tickets.py check` warns, without failing, when every ticket folder has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered`, and `close --numbered` persists that config line as `new --numbered` does.

## Step 1: close --numbered persists config, and check warns
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`:
- `cmd_close`: capture `flag = numbered` before `numbered = numbered or config_numbered(root)`, as `cmd_new` does. After a successful close (after the `write_roadmap` call, right before the return), call `ensure_numbered_config(root)` when `flag` is true. Refusals must still write nothing, so the call goes only on the success path.
- `cmd_check`: after the roadmap staleness check passes, compute `warn`. It is true when `not numbered`, `ts` is non-empty, and every folder name in `ts` (the slug in each `(slug, meta)` pair) matches `PREFIX_RE`. Then return the `ok:` line plus a second line: `warning: every ticket folder has an NNNN- prefix but <root>/config lacks 'ticket_folders: numbered'; add that line (or run new/close --numbered once) to enforce it`. The run() contract is `(rc, out, err)`, so the warning may ride in `out`, since `main` prints `out` to stdout and check still exits 0. The failure paths are untouched.
- Add selftest cases near the existing `new --numbered` persistence cases (around line 615) and the numbered close cases (around line 841). Fixtures: rename the base tickets to `0001-alpha` and `0002-beta` with a regenerated roadmap. The existing `renamed()` helper and `both()` combinator show how.
  - Numbered folders with no config: `check` returns rc 0 and `out` contains `warning`.
  - Same fixture with `ticket_folders: numbered` config: no warning.
  - Plain slugs: no warning.
  - Mixed (one numbered, one plain): no warning.
  - Empty root: no warning.
  - `close alpha --numbered` with a filer fixture: `<root>/config` exists and `config_numbered(root)` holds.
  - `close` without the flag: writes no config.
  - Refused close (open warnings) with `--numbered`: writes no config.
- Update the usage docstring at the top (the `check` line and the `close` line, which should now say close persists like new).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints PASS.
- Red-then-green: temporarily revert the `cmd_check` warning and the `cmd_close` persist. Selftest then fails and names the new cases as not biting. Restore both after.
- In a temp root with tickets `0001-a` and `0002-b`, a roadmap, and no config, `tickets.py --root <tmp> check` exits 0 and prints a line containing `warning`. After adding `ticket_folders: numbered` to the config, the warning is gone.
- With a plain-slug fixture, `check` prints no `warning` and exits 0.
- `close <slug> --numbered` on a fixture with a filer file leaves `<root>/config` containing `ticket_folders: numbered`. The exit code and the follow-up files are unchanged.

## Step 2: Sync the docs
level: L1
### Do
- `plugins/sdlc-lite/skills/ticket/SKILL.md` line 15: say a successful `new --numbered` or `close --numbered` appends the config line when it is missing. Also say plain `check` warns, without failing, when every folder has an NNNN- prefix but the config lacks the line.
- `CLAUDE.md` line 25 (the `tickets.py` bullet): make the same two changes. Its `check` description gets the warning, and its persistence sentence covers `close --numbered`.
- `.claude/agents/sdlc-lite-author.md`: it has no numbered-mode text today. Add one short line to the invariants or hazards section. It should say numbered mode persists via `new` and `close --numbered`, that `check` warns on numbered folders with no config, and that these must stay in sync with tickets.py, the /ticket skill and CLAUDE.md.
- No em dashes.

### Acceptance criteria
- `grep -n "close --numbered" plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` matches in both files, and the same grep for `warn` matches in both.
- `grep -n -i "numbered" .claude/agents/sdlc-lite-author.md` matches at least one line.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The `claude plugin validate` warning about CLAUDE.md is expected.

## Risks
- The `check` warning rides in stdout (`out`) because `run()` has no warning channel. Anything that parses `check` output for the exact `ok: N tickets` string would see an extra line. The selftest only uses `startswith('ok: 0 tickets')`, but grep other callers (`check.sh`, skills) for `check` output parsing.
- Whether `close --numbered` also persists on refusal is a judgment call. This plan says no, so a refused close leaves no trace.
- The "every folder" test uses `PREFIX_RE`. Check it matches exactly 4 digits followed by a hyphen. A digit-led plain slug like `2024-plan` would trigger a false warning, but only when every folder looks like that.
