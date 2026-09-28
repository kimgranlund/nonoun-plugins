<!-- role=planner level=L1 model=sonnet effort=medium -->
Good, confirms `tickets.py selftest` is run by `check.sh`. Now producing the plan.

## Goal
Fix `follow_up_title` returning an empty title for a bullet with an empty first sentence, and stop the follow-up cleanup regex from deleting underscores inside code names, in `plugins/sdlc-lite/scripts/tickets.py`, with red-then-green selftest coverage for both.

## Step 1: Skip an empty first sentence in `follow_up_title`
level: L1

### Do
In `plugins/sdlc-lite/scripts/tickets.py`, `follow_up_title` (around line 310): the current logic does `m = re.search(r'[.!?] ', plain)` then, if `m.start() <= 70`, returns `plain[:m.start()]` unconditionally — this fires even when `m.start() == 0` (empty first sentence, e.g. input `'. ' + 'x'*80`), returning `''`. Change the check so an empty match (`m.start() == 0`) is treated as "no usable first sentence" and falls through to the existing whole-word `...` cut logic below it (the `cut = plain.rfind(' ', 0, 68)` branch). Do not change behavior for any non-empty first sentence that is `<= 70` chars, and do not change the `<= 70` chars whole-input early return.

In `selftest()` in the same file, add a case that fails against the current code and passes after the fix: call `follow_up_title('. ' + 'x'*80)` directly (or via the existing close-flow fixture pattern used in case (a), by adding a bullet whose first sentence is empty) and assert the result is non-empty and does not start with `.`. Prefer a direct unit-style `expect(...)` call on `follow_up_title(...)` for minimal blast radius, placed near the other `follow_up_title`-adjacent assertions in case (a) (around the `short_first_sentence_item` checks, line ~538).

### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from tickets import follow_up_title as f; print(repr(f('. ' + 'x'*80)))"` prints a non-empty string that is not `''` and does not start with `'.'`.
- Reverting only the `follow_up_title` fix (keeping the new selftest assertion) makes `python3 plugins/sdlc-lite/scripts/tickets.py selftest` fail on that assertion; with the fix applied it passes.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0.
- Existing cases stay correct: `follow_up_title('x'*50)` still returns the input unchanged, and the `short_first_sentence_item` and `long_item` assertions in case (a) still pass unchanged.

## Step 2: Keep underscores inside words when cleaning follow-up bullet text
level: L1

### Do
In `plugins/sdlc-lite/scripts/tickets.py`, `cmd_close` (around line 360): `plain = ' '.join(re.sub(r'[`*_\[\]()]', '', item).split())` strips every underscore, turning `follow_up_title` into `followuptitle`. Change the regex (or add a preceding/following step) so underscores used as markdown emphasis delimiters (`_word_`, `__word__`) are stripped but underscores inside a word (e.g. `follow_up_title`) survive. A working approach: first strip paired emphasis underscores with something like `re.sub(r'(?<!\w)_{1,2}(\S.*?\S|\S)_{1,2}(?!\w)', r'\1', item)` (or equivalent word-boundary-aware pattern), then run the existing cleanup regex with `_` removed from its character class (`re.sub(r'[`*\[\]()]', '', ...)`). Keep the change local to this cleanup step; do not touch slug generation (`re.findall(r'[a-z0-9]+', plain.lower())`), which already drops underscores as word separators and is explicitly out of scope per the handoff.

In `selftest()`, add a case that fails against current code and passes after the fix: a follow-up bullet containing a bare code-style token with an underscore, e.g. `` `follow_up_title` in tickets.py returns ... `` (mirroring this ticket's own origin bug), and assert the resulting filed ticket's title contains `follow_up_title` (not `followuptitle`). Add it alongside the other bullets in the `good` fixture in case (a) (~line 538-542) or as its own case, and add the corresponding `expect(...)` near the existing title assertions (~line 556-560).

### Acceptance criteria
- `python3 -c "import re; item='\`follow_up_title\` in tickets.py'; print(re.sub(r'[\`*\[\]()]','', item))"` style check: after the fix, cleaning that bullet text yields a string containing `follow_up_title`, not `followuptitle`.
- A bullet like `_emphasized_` or `__bold__` still has its surrounding underscores stripped after the fix (emphasis delimiters removed, inner word kept).
- Reverting only the `cmd_close` regex fix (keeping the new selftest assertion) makes `python3 plugins/sdlc-lite/scripts/tickets.py selftest` fail on that assertion; with the fix applied it passes.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0.

## Step 3: Full check
level: L1

### Do
No code change. Run the project's full check to confirm both fixes and the level-table/skill/manifest checks all agree, per the handoff's "Done when" clause (`scripts/check.sh` passes).

### Acceptance criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0 from the repo root.

## Risks
Step 1 and Step 2 touch adjacent lines in the same functions (`follow_up_title` and `cmd_close`) and the same `selftest()` block, so building them out of order or in parallel risks a merge conflict in the selftest fixture; build them sequentially. The regex suggested for Step 2 is illustrative, not prescriptive — the builder should verify it against the emphasis-vs-code-name distinction with the selftest cases rather than trusting it verbatim.
