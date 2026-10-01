<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py`: `ENTRY_TEMPLATE` gets the `wait` paragraph in Read. In Messenger, the parenthetical now reads ``(`wait`, or `count` then `list`, then `read`)``, and a new paragraph about the parent running `wait` sits before Host limits. `case_entry_parses` `want` now includes `'wait'`. No heading was added.
- `plugins/sdlc-lite/agents/messenger.md`: the Loop is now the three `wait`-based items plus the closing sentence, and the Host limits Claude Code bullet is extended.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`: regenerated with `codex_roles.py generate`, not edited by hand.
- `docs/maintenance/sdlc-internals.md`: anchors (a) to (d) replaced in the `scripts/messages.py` entry.
- `docs/ticket-stages/design.md`: a T-0181 sentence added to the Status paragraph and to the Host limits bullet.

## Checks
- AC1, the template assertions in `python3 -B -c ...`: PASS
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest | grep -qxF "messages selftest: PASS"`: PASS
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS (exit 0)
- `grep -qF "messages.py wait --receiver <harness> --timeout 100 --interval 10" plugins/sdlc-lite/agents/messenger.md`: PASS
- `! grep -qF "Every 10 seconds, run" plugins/sdlc-lite/agents/messenger.md`: PASS
- (guard) loop over the three MESSENGER_WORDS in messenger.md: PASS
- `grep -qF "messages.py wait --receiver <harness> --timeout 100 --interval 10" .../sdlc-messenger-l1.toml`: PASS
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: PASS
- `grep -qF "exit 3 only when" docs/maintenance/sdlc-internals.md`: PASS
- `grep -qF "no new messages" docs/maintenance/sdlc-internals.md`: PASS
- `grep -qF "a claiming wait is caught as a negative control" docs/maintenance/sdlc-internals.md`: PASS
- `grep -qF "T-0181 adds" docs/ticket-stages/design.md`: PASS
- `grep -qF "does not wake an idle host" docs/ticket-stages/design.md`: PASS
- Scope check, `git diff --name-only "$SDLC_BASE_SHA"` against the allowlist plus no untracked files outside `.sdlc`: PASS
- Extra: `python3 plugins/sdlc-lite/scripts/check.py`: ok, 19 role levels and 9 agents checked
- Extra: `git diff --check`: clean, and no em dashes in the edited files.

## Notes
The diff in `messages.py` also contains step 1's uncommitted `wait` subcommand, which was already in the tree when this step started. Step 2 only added the template text and the `'wait'` entry in `want`.
