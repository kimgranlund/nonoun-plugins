## Task goal
Add an opt-in numbered-folder mode (`NNNN-<slug>`) to `scripts/tickets.py`'s `new`, `close`, and `check`, keeping plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/ticket-numbered-folders/handoff.md

## Step 4: Docs and full verification
level: L1
### Do
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: update `argument-hint` to mention `--numbered` on `new` and `close`, and add a rule line noting the `<root>/config` `ticket_folders: numbered` key and the always-on prefix/id check.
- the repo root `CLAUDE.md` (there is no plugins/sdlc-lite/CLAUDE.md), the `scripts/tickets.py` bullet: add a clause describing numbered mode (config key, `--numbered` flag, `NNNN-<slug>` naming, and that `check` always enforces prefix/id agreement).
- `.claude/agents/sdlc-lite-author.md`: update only if it describes `tickets.py new`/`close` command shapes; otherwise leave untouched.
- Do not touch `board.py`, roadmap rendering, or `.sdlc/` folder names in this repo (non-goals).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes (full run, all cases from Steps 1-3 together).
- `plugins/sdlc-lite/scripts/check.sh` passes.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (repo root) passes.
- `grep -n "numbered" plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` shows the new mentions.
