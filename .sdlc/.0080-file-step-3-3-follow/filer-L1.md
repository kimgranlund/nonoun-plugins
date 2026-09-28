<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0080: /file step 3.3 asks for at most 4 follow-up options per question

## PR body
### Summary
Step 3.3 of `/file` asks the user which follow-ups to file, using one multiSelect question in AskUserQuestion. That tool allows at most 4 options per question. When a filer file listed more than 4 follow-ups, the question went over that limit. Step 3.3 now splits the follow-ups across several questions, and `check.py` fails if the rule is removed.

### Changes
- `plugins/sdlc-lite/skills/file/SKILL.md` (only the step 3.3 line changed):
  - A question has at most 4 options, and one call has at most 4 questions.
  - Follow-ups are split into questions in order, recommended items first.
  - No question has fewer than 2 options: 5 follow-ups become 3 and 2, never 4 and 1.
  - A single follow-up is asked as one question with "File it" and "Skip it".
  - Past 16 follow-ups, the rest are asked in further calls.
  - A follow-up left unselected is skipped, as before.
  - Step 3's dry run, the `--skip`/`--expect` digest, and the unattended path are unchanged, and so are step 4 and its guards.
- `plugins/sdlc-lite/scripts/check.py`: a new `step33_bad` guard requires `at most 4 options per question` on the step 3.3 line. It includes an in-memory negative control and sits just before the step 4 guards, which are unchanged.

### Verification
Step 1 was built at L2, and the verifier L1 verdict is pass.
- All grep criteria passed: the phrase is present in SKILL.md and check.py, the HEAD text lacks it, and the existing `at most 4 options` and `--expect` guards still pass.
- `python3 plugins/sdlc-lite/scripts/check.py` exited 0 ("ok: 18 role levels, 8 agents checked").
- `plugins/sdlc-lite/scripts/check.sh` exited 0: the selftests passed, and shellcheck and plugin validate were ok. The verifier did not run a baseline at HEAD, so "no new findings" rests on the run ending all-ok.
- No em dashes were added.
- The guard fires: in a throwaway worktree at HEAD with the new check.py, the check printed `FAIL skills/file/SKILL.md: step 3.3 missing "at most 4 options per question"` and exited 1.
- The verifier read the step 3.3 prose and confirmed each batching rule above.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/file`: the follow-up question in step 3.3 now splits follow-ups into questions of 2 to 4 options each, with up to 4 questions per call, so it stays within AskUserQuestion's limits. A `check.py` guard keeps the rule in place.

## Follow-ups
- check.py's step 3.3 guard finds its line by the literal prefix `   3. When a person is present`; make it fail loudly when no line matches, so rewording that prefix cannot silently turn the guard off.
