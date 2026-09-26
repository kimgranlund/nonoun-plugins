## Task goal
When `tickets.py close` (numbered mode) or `tickets.py archive` renames `NNNN-<slug>` to `.NNNN-<slug>`, its reference scan also finds (and with `--rewrite-refs` rewrites) references to the folder written as a path relative to the citing file (`../0003-x/`, `../../.sdlc/0003-x/handoff.md`) or as an absolute path (`/abs/toplevel/.sdlc/0003-x`), not only the literal toplevel-relative `<rel>/<slug>`, so those references no longer break silently on rename.

## Step 2: Document the widened scan
level: L1
### Do
Describe the widened scan, and its limits, wherever the scan is described. The new rule: the scan finds the folder name, then keeps files with a literal `<rel>/<slug>` or a path token that resolves to the folder, whether toplevel-relative, relative to the citing file's directory, or absolute. The limits: only matched tokens are rewritten, keeping their form; there is no case folding, symlink resolution, `~` expansion or self-reference handling.

Places to update:
- `plugins/sdlc-lite/scripts/tickets.py` module help: the `close` paragraph around lines 23 to 29 and the `archive` paragraph around lines 52 to 59.
- The `scripts/tickets.py` entry in the repo-root `CLAUDE.md` Layout section.
- `.claude/agents/sdlc-lite-author.md`, in the place where it describes the numbered close and archive scan.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`, only if it describes the scan.

Use the phrase "relative to the citing file" in each updated text. No em dashes.
### Acceptance criteria
- `grep -qF "relative to the citing file" CLAUDE.md`
- `grep -qF "relative to the citing file" plugins/sdlc-lite/scripts/tickets.py`
- `grep -qF "relative to the citing file" .claude/agents/sdlc-lite-author.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- `git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills plugins/sdlc-lite/scripts/tickets.py | grep "^+" | grep -c "—"` prints 0
