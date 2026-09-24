## Task goal
`tickets.py close` never files a follow-up ticket with an empty or mangled title. (Ticket T-0014, `.sdlc/followuptitle-in-tickets-py-returns/handoff.md`; its Goal and Constraints sections are binding.) Repo root: the git work tree containing this `.sdlc/`.

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

