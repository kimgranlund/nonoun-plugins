<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
`/file` step 3.3 never asks AskUserQuestion for more than 4 options per question, however many follow-ups the filer lists, and `check.py` fails if that rule is removed from the skill.

## Step 1: Batch step 3.3 follow-ups and add a guarded check
level: L2
### Do
In `plugins/sdlc-lite/skills/file/SKILL.md`, edit only sub-step 3.3.
- Keep the multiSelect ask, the recommended set first, and the `--skip` rule for unselected likely duplicates.
- Add this rule: a question names at most 4 options per question, and one AskUserQuestion call takes at most 4 questions.
- Split the follow-ups into questions in order, recommended items first.
- Balance the split so no question has fewer than 2 options. For example, 5 follow-ups become 3 and 2, never 4 and 1. A single follow-up is asked as one question with two options, "File it" and "Skip it".
- With more than 16 follow-ups, ask the rest in further calls.
- Any follow-up not selected in any question is skipped, exactly as before.
- Use no em dashes.

In `plugins/sdlc-lite/scripts/check.py`, next to the existing publish-question guard (around line 219), add these checks.
- Take the step 3.3 line as the line in `ft` that starts with `   3. When a person is present`. Require the literal text `at most 4 options per question` on that line.
- Add a negative control in the same block. It removes that phrase from the step 3.3 text in memory, runs the same predicate, and appends an error if the predicate does not flag the mutated text.

Do not touch the step 4 guards, and do not touch step 3's dry-run, digest, or unattended text.
### Acceptance criteria
- `grep -n "When a person is present" plugins/sdlc-lite/skills/file/SKILL.md | grep -q "at most 4 options per question"` (red now: the phrase is absent from 3.3)
- `grep -q "at most 4 options per question" plugins/sdlc-lite/scripts/check.py` (red now: the guard is missing)
- `git show HEAD:plugins/sdlc-lite/skills/file/SKILL.md | grep "When a person is present" | grep -vq "at most 4 options per question"` (guard: the pre-change text lacks the phrase, so the check.py predicate flags it. Green now, and unchanged by the step.)
- (guard) `grep -q "at most 4 options" plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) `grep -q "\-\-expect" plugins/sdlc-lite/skills/file/SKILL.md`
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 on the changed tree.
- `plugins/sdlc-lite/scripts/check.sh` exits 0, with no new findings versus HEAD.
- `git diff -U0 HEAD -- plugins/sdlc-lite/skills/file/SKILL.md | grep '^+' | grep -c "—"` prints 0.
- Verifier check, by observation: the 3.3 text says that follow-ups batch in order, that no question has fewer than 2 options (5 becomes 3+2), that a call holds at most 4 questions, and that overflow goes to a further call.

## Risks
The negative control mutates text in memory, so it proves only that the predicate fires, not that the skill's prose is followed. The verifier should read the prose. The line prefix `   3. When a person is present` must stay stable, or the check.py lookup silently finds no line.
