<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/filer.md`: `## Follow-ups` now requires a tag on every bullet. The tags are `fix-now:` (run by /chain's `Loose ends` step), `decide:` (the user is asked once; an unanswered one goes to `.sdlc/notes.md`) and `note:` (appended to notes.md, never a ticket). The section keeps `None` and "two strong follow-ups beat five weak ones", allows at most one ticket per task, and makes a failed, blocked or no-verdict `Loose ends` step a `note:` item instead of a Warning.
- `plugins/sdlc-lite/skills/file/SKILL.md`: steps 3.1 to 3.6 rewritten.
  - 3.1: the dry run's item lines are now `<i>. <tag>: <title>` with `ticket`, `note`, `skip (--skip)` and `duplicate of T-NNNN` marks.
  - 3.2: artifact-answered items and likely duplicates go to `--skip`.
  - 3.3: one decide question with up to 3 `decide:` options plus `None: notes only`. Under /chain it shares /chain's close-out call with the publish question; standalone it shares one call with step 4's publish question.
  - 3.4: runs `close --ticket N --expect`, or plain `close`.
  - 3.5 (unattended): uses `--ticket` only when exactly one `decide:` item names a defect or risk.
  - 3.6: reports the ticket, the notes.md lines, the skips and the duplicates.
  - Step 4 is unchanged.
- `plugins/sdlc-lite/scripts/check.py`: added check 9 to the docstring and a `FINISH_DOCS` dict. It checks that `fix-now:`, `decide:` and `notes.md` appear in all four files the handoff names. It has a negative control (`finish_missing` run on the text with the word removed) and uses the message `<rel>: finish-in-session wording missing "<word>"`.

## Checks
- `grep -q 'fix-now' plugins/sdlc-lite/agents/filer.md`: passed
- `grep -q 'notes.md' plugins/sdlc-lite/agents/filer.md`: passed
- `grep -q 'Loose ends' plugins/sdlc-lite/agents/filer.md`: passed
- `grep -qF 'decide:' plugins/sdlc-lite/skills/file/SKILL.md`: passed
- `grep -q -- '--ticket' plugins/sdlc-lite/skills/file/SKILL.md`: passed
- `grep -q 'notes.md' plugins/sdlc-lite/skills/file/SKILL.md`: passed
- The mutation criterion (copy the plugin to a temp dir, replace `fix-now` with `fix-later` in filer.md, run check.py, grep the output): passed. check.py printed `FAIL agents/filer.md: finish-in-session wording missing "fix-now:"`.
- (guard) `grep -q 'at most 4 options per question' plugins/sdlc-lite/skills/file/SKILL.md`: passed
- (guard) `grep -q 'likely duplicate' plugins/sdlc-lite/skills/file/SKILL.md`: passed
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: passed ("ok: 18 role levels, 8 agents checked")

## Notes
- `scripts/tickets.py` and `skills/ticket/SKILL.md` already contained all three words at the start of this step, so `FINISH_DOCS` names all four files the handoff asks for and none of them fails.
- Step 4 of skills/file/SKILL.md is unchanged as the handoff asked. It still says "Follow-ups are already tickets", which no longer holds now that only one follow-up becomes a ticket; a later step may want to reword it.
