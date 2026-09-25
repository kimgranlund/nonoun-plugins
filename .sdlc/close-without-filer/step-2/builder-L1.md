<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: added `[--reason "<text>"]` to `argument-hint`, and a `--reason` sentence on the close item.
- `CLAUDE.md`: `tickets.py` bullet now mentions `close <slug> --reason "<text>"`.
- `.claude/agents/sdlc-lite-author.md`: line 16 now says to keep `--reason` in sync across tickets.py, the /ticket skill and CLAUDE.md.

## Checks
- `grep -c -- '--reason'` on the three files: SKILL.md 2, CLAUDE.md 1, sdlc-lite-author.md 1.
- `plugins/sdlc-lite/scripts/check.sh` exited 0. All selftests, shellcheck and plugin validate passed.
- `git diff --stat`: my three files plus `tickets.py` (step 1) and `.sdlc/close-without-filer/handoff.md`.

## Notes
- Two edits missed on the first attempt because my match strings were wrong. The first python script failed on an assert, and the follow-up `sed` errored on the slashes. The first script applied the SKILL.md and CLAUDE.md edits before hitting the assert. I redid the author-file edit with python and it applied once.
- `.sdlc/close-without-filer/handoff.md` shows a diff that this step did not make.
