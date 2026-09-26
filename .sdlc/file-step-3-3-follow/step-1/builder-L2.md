<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`: only step 3.3 changed. It now says:
  - a question has at most 4 options, and one call has at most 4 questions
  - follow-ups are split into questions in order, recommended items first
  - no question gets fewer than 2 options (5 becomes 3 and 2)
  - a single follow-up gets "File it" and "Skip it"
  - past 16 follow-ups, the rest go to further calls
  - anything left unselected is skipped
- `plugins/sdlc-lite/scripts/check.py`: added the `step33_bad` guard on the step 3.3 line, with a negative control, just before the step 4 guards. The step 4 guards themselves are unchanged.

## Checks
- `grep -n "When a person is present" ... | grep -q "at most 4 options per question"`: exit 0
- `grep -q "at most 4 options per question" plugins/sdlc-lite/scripts/check.py`: exit 0
- `git show HEAD:... | grep "When a person is present" | grep -vq ...`: exit 0
- (guard) `grep -q "at most 4 options" ...SKILL.md`: exit 0
- (guard) `grep -q "\-\-expect" ...SKILL.md`: exit 0
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0 ("ok: 18 role levels, 8 agents checked")
- `git diff -U0 HEAD -- ...SKILL.md | grep '^+' | grep -c "—"`: printed 0
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (fanout, run, and hook selftests PASS; shellcheck ok; plugin validate ok)

## Notes
None
