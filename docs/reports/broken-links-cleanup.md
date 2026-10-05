# Broken Markdown links cleanup (T-0257)

Measured with `python3 plugins/sdlc-lite/scripts/rename_refs.py links` from the repository root.

| Measure | Before | After |
|---|---|---|
| Links checked | 829 | 747 |
| Reported broken | 96 | 12 |

What changed:

- The counter treated link-shaped text inside code as links. It now blanks fenced blocks (indented up to three spaces, backtick or tilde) and inline code spans (any backtick count, one line) first. That removed 84 broken reports.
- No dated record was edited. A first attempt rewrote nine targets; an independent verifier showed they were quoted text addressed to other files, one rewrite made a recorded command false, and the attempt was reverted.
- The 12 that remain are listed with reasons in [the allowlist](broken-links-allowlist.md): quoted text addressed to another file, frozen records of pre-rename commands, bare names relative to the ticket they described, a sibling repository, and files of a throwaway project.

Guard: `scripts/check.py` item 32 compares the live broken set with the allowlist rows. An unlisted broken link fails, and so does a row that no longer matches. Both negative controls run in the check.

Limits: the guard runs only where the repository root is a git work tree. Anchor-only links are not checked. Unbalanced backticks, or a code span split across lines, can still leak a link into the count.
