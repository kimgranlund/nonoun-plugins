<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/messenger.md`: replaced Loop items 3 and 4 with the exact lines from the handoff. Item 3 now claims with `messages.py read <id> --receiver <harness>`. Item 4 now reports each claimed message's id and its path `read/<harness>/<id>.md`.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`: regenerated with `codex_roles.py generate`. It is the only TOML that changed.
- `docs/ticket-stages/design.md`: replaced the Message bus `Status:` line with the exact text from the handoff, which says the messenger is built in T-0178.

## Checks
All 17 acceptance criteria were run with `SDLC_BASE_SHA` read from the `base-sha` file in the step dir, and all passed:
- 1 to 7: passed with no edits. Items 1 to 4 were already committed at HEAD, so those files were left as they were.
- 8 to 12: passed. These cover the new messenger wording, the regenerated TOML, and the `design.md` status line.
- Guard, messenger literal strings: passed.
- Guard, no em dashes: passed.
- Guard, `git diff --check`: passed.
- Guard, `codex_roles.py generate --check`: passed ("Codex agent definitions verified").
- Changed-file allowlist: passed.

## Notes
None
