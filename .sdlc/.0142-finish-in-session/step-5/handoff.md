## Task goal
Small related work gets finished in the session that found it. A new ticket exists only for work that is out of scope, large, or needs the user.

## Step 5: Gates green and maintainer records
level: L2
### Do
1. Repo root `CLAUDE.md`, `## Decisions`: one bullet recording the user decision of 2026-09-26 (T-0142): small related work is finished in the session that found it; /chain's `Loose ends` step, the `/fix` fast lane, the filer's `fix-now:`/`decide:`/`note:` tags, and the code-enforced one-ticket cap in `tickets.py close` (`--ticket N`, the rest to `.sdlc/notes.md`); check.py guards the wording. Re-read the `scripts/tickets.py`, `/chain`, and skills bullets written by steps 1, 3, and 4 and make them agree with the shipped behavior.
2. `.claude/agents/sdlc-lite-author.md`, Invariants: extend the tickets sync bullet with the tags, `--ticket`, the cap, notes.md (in sync across tickets.py, the /ticket, /file, and /fanout skills, filer.md, and CLAUDE.md) and add one bullet for the `Loose ends` step and `/fix` fast lane wording (in sync across chain, fix, level-rubric, handoff-format, open-questions, conductor, filer.md, check.py, CLAUDE.md). Update the After every change list if check.sh's contents changed.
3. Run `bash plugins/sdlc-lite/scripts/check.sh` from the repo root and fix any red the earlier steps introduced (check.py wording, tickets selftest, fanout selftest, shellcheck, `claude plugin validate` on the new skill's frontmatter). It takes about 3 minutes here; `steps.py split --only 5` runs it under the 300 second default, so pass `--guard-timeout 600` if the host is loaded.
### Acceptance criteria
- `grep -q 'T-0142' CLAUDE.md`
- `grep -qF -- '--ticket' .claude/agents/sdlc-lite-author.md`
- `grep -q 'Loose ends' .claude/agents/sdlc-lite-author.md`
- `grep -qF '/fix' .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
