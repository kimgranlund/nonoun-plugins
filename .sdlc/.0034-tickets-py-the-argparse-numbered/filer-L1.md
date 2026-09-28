<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
No plan, builder, or verifier artifacts exist, so no independent verifier checked this change. The handoff says the change went in as a trivial conductor edit with no plan, build, or verify role. The only evidence of checking is the conductor's own record: it ran `close -h` and `scripts/check.sh` passed.

## PR title
T-0034: tickets.py: close --numbered help mentions persisting ticket_folders config

## PR body
### Summary
The help for `tickets.py close --numbered` now says that a successful close writes `ticket_folders: numbered` to `<root>/config`. The help for `new --numbered` and the module docstring already said this. The change touches help text only and does not change behavior. This is a follow-up from T-0026.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`: new help for the `close` subparser's `--numbered` flag: "name each follow-up folder NNNN-<slug> after its own new id and, on success, persist `ticket_folders: numbered` in <root>/config (also on via that config)". The words "on success" match the `close()` docstring and selftest case (j), which checks that a refused close writes no config.

### Verification
This was a conductor trivial edit, so no independent verifier ran. The conductor recorded two checks:
- `python3 scripts/tickets.py close -h` prints the new text.
- `scripts/check.sh` passes: level tables, selftest, tickets selftest, board selftest, shellcheck and plugin validate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- tickets.py: `close --numbered` help now says that a successful close writes `ticket_folders: numbered` to `<root>/config` (T-0034).

## Follow-ups
None
