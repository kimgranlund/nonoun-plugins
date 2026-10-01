<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Template assertion (`python3 -B -c ...` on `ENTRY_TEMPLATE`): pass. Evidence: exit 0 on the built tree. At base `bc21b53` the same read-section assertion raised `AssertionError: read`, so the check can go red.
- (guard) messages selftest prints `messages selftest: PASS`: pass. Evidence: the `grep -qxF` pipeline exited 0. The output tail includes `ok: wait: a claiming wait is caught` and `ok: wait: never prints a body`.
- (guard) `tickets.py selftest`: pass. Evidence: printed `tickets selftest: PASS` and exited 0. This is a guard, so I did not rerun it at base.
- `grep -qF "messages.py wait --receiver <harness> --timeout 100 --interval 10"` on messenger.md: pass. Evidence: exit 0. At base the same pattern (`messages.py wait`) gives exit 1.
- `! grep -qF "Every 10 seconds, run"` on messenger.md: pass. Evidence: exit 0, and the diff shows the old Loop item 1 removed.
- (guard) the three `MESSENGER_WORDS` are present in messenger.md: pass. Evidence: the loop printed no `MISSING`. `check.py` also printed `ok: 19 role levels, 9 agents checked`.
- Same grep on `sdlc-messenger-l1.toml`: pass. Evidence: exit 0. The diff shows the new Loop text inside `developer_instructions`.
- (guard) `codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`, exit 0.
- `grep -qF "exit 3 only when"`, `"no new messages"` and `"a claiming wait is caught as a negative control"` in sdlc-internals.md: pass. Evidence: all three exited 0.
- `grep -qF "T-0181 adds"` and `"does not wake an idle host"` in design.md: pass. Evidence: both exited 0. At base `T-0181 adds` gives exit 1.
- Scope check (the `git diff --name-only` allowlist plus no untracked files outside `.sdlc`): pass. Evidence: exit 0. The changed files are exactly the five allowed ones.

Claims I checked in the Do beyond the acceptance criteria:
- The text for sdlc-internals.md anchors (a) to (d) matches the Do verbatim. `grep -cF` returned 1 for each.
- The Messenger parenthetical was replaced: the new ``(`wait`, or `count` then `list`, then `read`)`` occurs once and the old text occurs 0 times.
- `want` in `case_entry_parses` now includes `'wait'` (diff line seen), and the messages selftest passes with it.
- The two new template paragraphs match the Do text, and I saw no added heading.
- No em dash in the added lines, and `git diff --check` is clean.

## Out of scope changes
None. The diff outside `.sdlc` is the five allowed files.

The `messages.py` diff also contains step 1's uncommitted `wait` subcommand and selftest cases. That is expected: the Do says step 2 depends on step 1, and the builder's notes say the same.

## For the next attempt
None
