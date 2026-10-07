## Task goal
Add a merge-time file-overlap check to fanout.py.

## Step 3: Internals doc and gates green
level: L2
### Do
Target: the `scripts/fanout.py` entry in `docs/references/sdlc-internals.md`. This is the owning doc per the handoff, and its fanout entry is at line 47. Depends on: steps 1 and 2.

In that entry, add:
- the merge-time overlap behavior: a later lane in spec order waits outside the lock for an earlier, unfinished lane whose pending files overlap its own, with the event `waiting for lane <name> (overlap: <files>)`;
- the report's `- Overlap:` lines (`- Overlap: none` when no lanes overlap);
- the dry run's `overlap (planned scope)` lines, read from the step handoffs' scope allow-lists in the forms `steps.py widen` recognizes;
- the remaining limit: an overlap first visible after a later lane has started its merge is not reordered.

Keep the docstring in `fanout.py` and this entry consistent; do not copy a table. `skills/fanout/SKILL.md` stays unchanged, because it prints report.md verbatim and is outside the owning files.

Then run every gate below. Fix any red that steps 1 and 2 introduced, in `fanout.py` or this doc only. A gate already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- `grep -qF -- '- Overlap:' docs/references/sdlc-internals.md`
- `grep -qF 'overlap (planned scope)' docs/references/sdlc-internals.md`
- `grep -qF 'waiting for lane' docs/references/sdlc-internals.md`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py -e docs/references/sdlc-internals.md)"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
