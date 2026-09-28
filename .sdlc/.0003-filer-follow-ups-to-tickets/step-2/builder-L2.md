<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/filer.md`: the PR title starts with `T-NNNN: ` when the handoff front matter has an id. Follow-ups are one-line `- ` bullets or exactly `None`. Warnings are exactly `None` when every step passed.
- `plugins/sdlc-lite/skills/file/SKILL.md`: added `tickets.py` to `allowed-tools`. New step 3 closes the ticket only when the handoff has ticket front matter. On a warnings refusal it asks with AskUserQuestion ("Leave open" first) and adds `--force` only if the user approves. It then reports the new follow-up tickets. Publishing moved to step 4 and is still gated by AskUserQuestion. Filing follow-ups as GitHub issues is now optional.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the argument-hint now includes `close <slug> [--force]`, plus one line saying `/file` normally runs it.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: one sentence saying `tickets.py close` sets `done` and stamps `from: <id>` on follow-up idea tickets.
- `CLAUDE.md`: the `scripts/tickets.py` bullet under Layout now documents `close <slug> [--force]`.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. Role levels, agents, selftest, tickets selftest, shellcheck and plugin validate all printed ok or PASS.
- `grep -n 'T-NNNN\|None' plugins/sdlc-lite/agents/filer.md`: found the PR-title rule (line 15) and the bullet-or-None rule under Follow-ups (line 23).
- `grep -n 'tickets.py\|--force\|AskUserQuestion' plugins/sdlc-lite/skills/file/SKILL.md`: found the allowed-tools entry (line 5) and the close invocation (line 12). `--force` and AskUserQuestion are on the same line (13). The publish step (line 15) still asks with AskUserQuestion and still says "Never publish on your own".
- `grep -c 'close'` on the ticket skill, the handoff-format skill and `CLAUDE.md`: 2, 1 and 1 matches, so all three files match.
- `grep -rn '—'` on the filer agent, the file skill and the ticket skill: no matches.

## Notes
- `.claude/agents/sdlc-lite-author.md` does not list `tickets.py` commands, so I left it unchanged.
- The `git diff` also shows changes to `tickets.py` from step 1. I did not touch that file.
