## Task goal
Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).

## Step 3: Skill and reference text for external lanes and the registration line
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only these three files, keeping every word `check.py` and `check-packaging.py` require in them (the long-run words, `inherited red`, the Codex route line).
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: `argument-hint` gains `<lane>@<branch>=<ids>` after `<lane>=<ids>...`. A new paragraph on its own line (after the lanes-dir paragraph) says: an external lane names a branch an outside agent (for example Codex) owns, registered with an `external_branch: <branch>` line in `.sdlc/config`; fanout runs no driver on it, creates no worktree and no `<integration>-<lane>` branch, and never writes that branch; it is merged `--no-ff` into the integration branch under the lock, gated, and its tickets are closed there (a second ticket on the same branch merges nothing new and skips the gates); a `merge conflict` outcome means the outside agent merges the integration branch on their side before the run is repeated; the lane shows in `report.md` but not in `board.py --lanes`, which lists worktrees.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: in the "Ids are allocated across worktrees" rule, add one sentence: an `external_branch: <branch>` line in `.sdlc/config` (one per line) registers a branch checked out nowhere; `new` and `close` follow-ups also count the ticket ids committed on it, and `check` warns (exit 0) when the name is not a local branch.
- `docs/references/sdlc-internals.md`: the `scripts/tickets.py` entry gains the registration line, what `id_floor` counts, and the `check` warning; the `scripts/fanout.py` entry's usage gains `<lane>@<branch>=<id>[,<id>...]` and the entry states the external lane path (registered in `<root>/config`, no worktree, no driver, never written, gates only when the merge made a commit, the refusals, the report line).
### Acceptance criteria
- `grep -E '^argument-hint:' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -qF '<lane>@<branch>=<ids>'`
- `grep -qF 'external_branch: <branch>' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -qF 'no driver' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `test "$(grep -c -- '--lanes' plugins/sdlc-lite/skills/fanout/SKILL.md)" -gt "$(git show "$SDLC_BASE_SHA":plugins/sdlc-lite/skills/fanout/SKILL.md | grep -c -- '--lanes')"`
- `grep -qF 'external_branch: <branch>' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF 'external_branch' docs/references/sdlc-internals.md && grep -qF '<lane>@<branch>=<id>[,<id>...]' docs/references/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/skills/fanout/SKILL.md -e plugins/sdlc-lite/skills/ticket/SKILL.md -e docs/references/sdlc-internals.md)"`
