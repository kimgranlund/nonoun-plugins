# Broken Markdown links cleanup (T-0257)

Measured with `python3 plugins/sdlc-lite/scripts/rename_refs.py links` from the repository root, before and after.

| Measure | Before | After |
|---|---|---|
| Links checked | 829 | 753 (after this record and the allowlist were added) |
| Reported broken | 96 | 8 |

What changed:

- The counter treated link-shaped text inside code fences and inline code as links. The analysis flagged 81 of the 96 as inside code (`slug/handoff.md`, `./0001-x/handoff.md`). The counter now blanks code first, which dropped about 79 from the checked total and the broken list (87 to 8 after the nine fixes).
- Nine real links pointed at moved or mis-deepened targets (`validation/` before the rename to `reports/`, and `../.sdlc/...` at the wrong depth). Their path text was corrected; the rest of those dated records is untouched.
- Eight links stay, listed with reasons in [the allowlist](broken-links-allowlist.md): two quoted README lines in frozen handoffs, two bare names relative to the ticket they described, two links to a sibling repository, and two to files of a throwaway project.

Guard: `scripts/check.py` item 32 compares the live broken set with the allowlist rows. An unlisted broken link fails, and so does an allowlist row that no longer matches. Both negative controls run in the check.

Limits: the guard runs only where the repository root is a git work tree. Anchor-only links were not checked. A link inside an inline code span that a person meant as a real link is not counted.
