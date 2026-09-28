<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/open-questions/SKILL.md` (new): the open-questions skill with the specified frontmatter, a four-part procedure (collect, nothing open, ask once, resolve), an unattended branch, and one good/bad example.

## Checks
- `test -f plugins/sdlc-lite/skills/open-questions/SKILL.md`: exit 0
- Frontmatter check (first line is `---`, `name: open-questions`, a non-empty description, `allowed-tools` includes AskUserQuestion): exit 0
- Forbidden names grep (`harness`, `write-handoff`, `find-intent`, `file-leftovers`, `close-session`, `find-open-questions`): no matches, exit 0
- Required phrases (`nothing open`, `unattended`, `Plan review`, `gap:`): exit 0
- Em dash grep: no matches, exit 0
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (all selftests, shellcheck and plugin validate reported ok)

## Notes
- The "Observable" criterion was checked by reading the file, not by a command. The body covers each required point:
  - exactly one AskUserQuestion call with 1 to 4 questions of 2 to 4 options
  - an option goes first as recommended only where a default or lean was stated
  - the top 4 items are asked and the count of the rest is named
  - stale items are dropped
  - a declined question is not asked again
- The harness source file was not read. The skill was written from the handoff's own description of it, which was complete enough to follow.
