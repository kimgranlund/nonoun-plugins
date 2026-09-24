<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0014: Stop follow-up tickets getting empty or mangled titles

## PR body
### Summary
`tickets.py close` could file a follow-up ticket with an empty title or a mangled one. This PR fixes both defects in `plugins/sdlc-lite/scripts/tickets.py`. Each fix comes with a selftest assertion that fails on the old code and passes on the new code.

### Changes
- **Empty first sentence (`follow_up_title`).** When a bullet starts with `. `, the function no longer returns `''`. It now recurses on the text after the empty sentence. For example, `follow_up_title('. ' + 'x'*80)` returns 67 `x` characters followed by `...`. The plan asked for a plain fall-through to the whole-word cut. The verifier found that a plain fall-through would return `'....'`, and the recursion avoids that. The recursion always ends because each call removes at least 2 characters. A new selftest assertion covers this case.
- **Underscores in code names (`cmd_close` cleanup).** Paired emphasis underscores (`_word_`, `__word__`) are stripped first. After that, `_` is no longer in the cleanup character class, so `follow_up_title` stays as it is instead of becoming `followuptitle`. The slug rules did not change. The selftest `good` fixture gets a new bullet with an underscore name and an assertion on the filed title. Two fixture counts in existing assertions went up by one: follow-ups from 3 to 4, tickets from 5 to 6.

### Verification
Each step was checked by an independent verifier at L1 (Opus medium), and both passed.
- Step 1: the direct call returns a non-empty title with no leading `.`, where HEAD returned `''`. In a throwaway worktree, removing only the fix made selftest fail on the new assertion (rc=1). With the fix it passes (rc=0). `follow_up_title('x'*50)` still returns its input unchanged.
- Step 2: the new cleanup turns `` `follow_up_title` in tickets.py `` into `follow_up_title in tickets.py`, while the old regex produced `followuptitle`. `_emphasized_`, `__bold__`, and `x _a_ y` still lose their emphasis underscores. In a throwaway worktree, putting back only the old regex made selftest fail on exactly the new assertion (rc=1).
- `scripts/check.sh` exits 0: all selftests, shellcheck, and plugin validate pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `tickets.py close` no longer files follow-up tickets with an empty title when a bullet starts with `. `, and no longer strips underscores from code names such as `follow_up_title` in titles (T-0014).

## Follow-ups
None
