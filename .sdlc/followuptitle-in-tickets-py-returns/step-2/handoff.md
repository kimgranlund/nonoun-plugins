## Task goal
`tickets.py close` never files a follow-up ticket with an empty or mangled title. (Ticket T-0014, `.sdlc/followuptitle-in-tickets-py-returns/handoff.md`; its Goal and Constraints sections are binding.) Repo root: the git work tree containing this `.sdlc/`.

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

- `plugins/sdlc-lite/scripts/check.sh` exits 0 from the repo root (planner Step 3, folded in here).

## Previous steps
Step 1 (empty first sentence in `follow_up_title`) is already built and verified; keep its selftest assertion passing.
