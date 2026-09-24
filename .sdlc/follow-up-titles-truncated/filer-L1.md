<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0013: Cut follow-up ticket titles at a word boundary

## PR body
### Summary
`tickets.py close` made follow-up ticket titles by cutting the bullet text at 67 chars and adding `...`. That split words, so T-0007..T-0012 all had titles cut mid-word. Titles now end at a sentence or word boundary. The existing tickets were retitled and the roadmap regenerated.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`: a new `follow_up_title(plain)` helper replaces the one-line title rule in `cmd_close`:
  - text of 70 chars or less stays unchanged;
  - longer text uses its first sentence, if that sentence fits in 70 chars, with the final period dropped;
  - otherwise it cuts at the last space at or before index 67, strips trailing punctuation and adds `...`;
  - if the first 67 chars have no space, it hard-cuts at 67.
- Selftest close case (a) has a new fixture bullet with a short first sentence. New assertions check that the title is that sentence, and that a long single-sentence title is a whole-word prefix ending in `...` and at most 70 chars.
- The `title:` line was updated in T-0007, T-0009, T-0010 and T-0011. T-0008 and T-0012 already matched the new rule and are unchanged.
- `.sdlc/roadmap.md` was regenerated.

### Verification
The verifier returned pass on every criterion.
- Test first: the new assertions failed on the old title line. The builder reported the two failing assertions. The verifier restored the old line in a throwaway worktree and got `tickets selftest: FAIL` on the same two assertions. A second control cut mid-word on purpose and failed the long-item assertion on its own.
- `tickets.py selftest` prints `tickets selftest: PASS`.
- `scripts/check.sh` passes: role levels, selftest, tickets selftest, shellcheck, plugin validate.
- `tickets.py check` prints `ok: 13 tickets, roadmap current`. Roadmap titles for T-0007..T-0012 are 60, 70, 50, 35, 39 and 70 chars. The two titles ending in `...` are cut at whole words. The verifier ran `follow_up_title` on all six bullets and each result matched the ticket's `title:` line.
- `git diff --stat` touches only the allowed files, and each handoff diff changes only its `title:` line.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: follow-up tickets created by `/file` (`tickets.py close`) now get readable titles that end at a sentence or word boundary, not mid-word. Existing follow-up tickets T-0007..T-0012 were retitled.

## Follow-ups
- `follow_up_title` in tickets.py returns an empty title when the bullet starts with `. `: it should skip an empty first sentence as the T-0013 step spec says (e.g. `follow_up_title('. ' + 'x'*80)` returns `''`)
