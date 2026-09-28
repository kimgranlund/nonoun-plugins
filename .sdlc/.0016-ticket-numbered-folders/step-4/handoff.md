## Task goal
Finish the opt-in numbered-folder mode in `plugins/sdlc-lite/scripts/tickets.py` by making the NNNN-/id rule fire only in numbered mode (`check --numbered` or `<root>/config`), then update the docs, with plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/0016-ticket-numbered-folders/handoff.md
Previous blocked attempt of this step: .sdlc/0016-ticket-numbered-folders/old-step-3/

## Step 4: Docs for numbered mode
level: L1
### Do
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: change `argument-hint` to `new <type> <slug> "title" [--numbered] | close <slug> [--force] [--numbered] | roadmap | check [--numbered]`. Add one rule bullet under `Rules:`: numbered folders are opt-in, by `--numbered` on `new`, `close`, or `check` for one call, or a `ticket_folders: numbered` line in `.sdlc/config` for the repo; in numbered mode `new` names the folder `NNNN-<slug>` after the id it assigns (give the bare slug), `close` does the same for each follow-up with its own id, and `check` fails on a `NNNN-` folder whose id is not `T-NNNN`; without either, plain slugs, as before.
- Repo root `CLAUDE.md`, the `scripts/tickets.py` bullet in Layout: add a clause with the same content in one sentence (`--numbered` on `new`/`close`/`check` or `<root>/config` `ticket_folders: numbered`; `NNNN-<slug>` from the stamped id; `check` enforces the prefix only in numbered mode; plain slugs are the default).
- `.claude/agents/sdlc-lite-author.md` does not describe `tickets.py` command shapes (its only mention is `check.sh` in "After every change"); leave it untouched.
- Do not edit `tickets.py` (its docstring was updated in steps 1 to 3), `board.py`, the roadmap `HEADER`, `skills/file/SKILL.md` (`close <slug>` with the on-disk dir name still holds), or any `.sdlc/` folder name.
### Acceptance criteria
- `grep -n "numbered" plugins/sdlc-lite/skills/ticket/SKILL.md` shows the `argument-hint` line with `[--numbered]` after `new`, `close`, and `check`, plus one rule bullet mentioning `ticket_folders: numbered` and `NNNN-<slug>`.
- `grep -n "ticket_folders: numbered" CLAUDE.md` matches inside the `scripts/tickets.py` bullet.
- `git diff --stat HEAD -- .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/scripts/board.py` is empty.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0; `plugins/sdlc-lite/scripts/check.sh` exits 0; `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.

## Risks (from the replan)
- Step 3 makes numbered-mode `new` and `close` refuse on any existing mismatched `NNNN-` folder, not only on the ticket they write. This follows the existing "fix the problems above first" contract; if the user wanted the rule only on the written ticket, drop `numbered` from the two pre-check `problems(ts)` calls and cases 7 and 8.
- `roadmap` does not apply the rule (the Intent lists `new`, `close`, `check`), so with the config on, `roadmap` can regenerate while `check` fails. A follow-up ticket if that matters.
- Steps 1 and 2 exist only as uncommitted working-tree changes; any `git checkout`, `git restore`, or `git stash` in the step-3 build loses them. Step 3's criteria grep for their labels to catch that.
- The default no-subcommand path (`cmd = a.cmd or 'check'`) has no `numbered` attribute; a builder that reads `a.numbered` directly breaks `python3 tickets.py --root .sdlc`, which the statusline and `/ticket` with no args use. The criterion runs that form.
- The repo ticket count (21) in a criterion can drift if the conductor files tickets meanwhile; the check is rc 0 and matching lines from both forms, not the number.
