## Task goal
Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).

## Step 5: Loose ends
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
- The external lane's report Commit cell wording is looser than the code: for a ticket whose merge brings nothing new (a later ticket on the same branch), the cell is the integration HEAD after the no-op merge, the previous `close` commit, not a merge commit. In `plugins/sdlc-lite/scripts/fanout.py` (docstring line starting `An external lane's Commit cell is the merge commit when merged`) and in `docs/maintenance/sdlc-internals.md` (the sentence `its Commit cell is the merge commit when merged, else the branch tip's sha7`), replace that wording with: the Commit cell is the merge commit when the merge made one, the integration HEAD (the previous `close` commit) when it merged nothing new, else the branch tip's sha7. Change no code and no other text.
### Acceptance criteria
- `grep -qF 'merged nothing new' plugins/sdlc-lite/scripts/fanout.py && grep -qF 'merged nothing new' docs/maintenance/sdlc-internals.md`
- `! grep -qF 'is the merge commit when merged, else' plugins/sdlc-lite/scripts/fanout.py && ! grep -qF 'is the merge commit when merged, else' docs/maintenance/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `git diff --check -- plugins docs`
