## Task goal
Follow-up tickets created by `tickets.py close` keep a readable title: never cut mid-word. (Ticket T-0013, `.sdlc/0013-follow-up-titles-truncated/handoff.md`.)

## Step 1: Word-boundary follow-up titles, test first, and retitle T-0007..T-0012
level: L1

### Do
Repo root: the git work tree containing this `.sdlc/`. Script: `plugins/sdlc-lite/scripts/tickets.py`.

1. Test first. In `selftest()`, close case (a) (around line 540, `titles = sorted(...)`), add assertions that fail on the current code. Add a third follow-up bullet to the `good` filer fixture whose first sentence is short and whose full text is over 70 chars, e.g. `- Optional id and status columns in board.py. T-0001 listed this as optional, and the plan left it out of scope.`, and update the `(a)` expectations that count follow-ups (2 becomes 3, and the `out.startswith('T-0001 done; 2 follow-up ticket(s): ')` text). Assert:
   - the short-first-sentence bullet's title is exactly `Optional id and status columns in board.py`;
   - the long single-sentence `long_item` title ends with `...`, is <= 70 chars, and the text before `...` is a whole-word prefix of `long_item` (i.e. `long_item.startswith(prefix)` and `long_item[len(prefix)] == ' '`), with no trailing space or punctuation before `...`;
   - every title is <= 70 chars and has no backtick (existing check).
   Run `python3 plugins/sdlc-lite/scripts/tickets.py selftest` and confirm it FAILS on the old title code before you fix it. Record that failing output in your result.
2. Fix. Replace the one-line title rule in `cmd_close` (`title = plain if len(plain) <= 70 else plain[:67].rstrip() + '...'`) with a small helper `follow_up_title(plain)`:
   - if `len(plain) <= 70`: return it unchanged;
   - else if the first sentence (text up to the first `. `, `! ` or `? `) is non-empty and <= 70 chars: return it without its final `.`;
   - else cut at the last space at or before index 67, strip trailing spaces and `,;:.-` punctuation, append `...`;
   - if there is no space in the first 67 chars, hard-cut at 67 and append `...`.
   Result is always <= 70 chars.
3. Retitle the existing follow-up tickets T-0007..T-0012 (`.sdlc/{run-the-filer-headless-on,check-this-repo-s-live,optional-id-and-status-columns,t-0001-still-shows-status,bring-this-repo-s-backlog,add-close-to-tickets-py}/handoff.md`): compute the new title by applying `follow_up_title` to the bullet under "Follow-up from ..." in each body, after the same cleanup `cmd_close` does (`' '.join(re.sub(r'[`*_\[\]()]', '', item).split())`). Change only the `title:` line in front matter; nothing else in those files. Keep `"` quoting as `stamp` does (double quotes, inner `"` become `'`).
4. Regenerate the roadmap: `python3 plugins/sdlc-lite/scripts/tickets.py roadmap` from the repo root.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS`.
- The builder result shows the new selftest assertions failing against the old title line before the fix.
- `plugins/sdlc-lite/scripts/check.sh` passes (the known CLAUDE.md validate warning is expected).
- `python3 plugins/sdlc-lite/scripts/tickets.py check` passes and `.sdlc/roadmap.md` shows no title for T-0007..T-0012 ending in a partial word before `...`; every title is <= 70 chars.
- `git diff --stat` touches only `plugins/sdlc-lite/scripts/tickets.py`, the six ticket handoffs, and `.sdlc/roadmap.md` (plus files under `.sdlc/0013-follow-up-titles-truncated/`).

### Constraints
- No commit, push, or stash. Do not change `stamp`, `close` behavior beyond the title, or any other ticket field.
