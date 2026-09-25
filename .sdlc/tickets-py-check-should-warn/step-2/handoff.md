## Task goal
`tickets.py check` warns, without failing, when every ticket folder has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered`, and `close --numbered` persists that config line as `new --numbered` does.

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
