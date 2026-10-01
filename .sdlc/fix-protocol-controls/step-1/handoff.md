## Task goal
Close two selftest coverage gaps in `plugins/sdlc-lite/scripts/messages.py`: nothing currently fails if the `protocol` value check or the `follow_up_requested` boolean check is removed.

## Step 1: Add two negative-control selftest cases
level: L2

### Do
Change only `plugins/sdlc-lite/scripts/messages.py`. Add two cases to `SELFTEST_CASES`, written in the style of the existing cases: (1) a hand-written file in `new/<receiver>/` whose `protocol` value is not `.sdlc/messages/AGENTS.md` is refused by `read` (exit 1, the file stays in `new/`, `read_time` still empty); (2) a hand-written file whose `follow_up_requested` is `maybe` is refused by `read` the same way, and `send --follow-up maybe` is refused with the count unchanged. Do not change any production check. Focused check: `python3 plugins/sdlc-lite/scripts/messages.py selftest`.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- `python3 plugins/sdlc-lite/scripts/messages.py selftest 2>&1 | grep -c 'ok: .*protocol' | grep -qv '^0$'`
- `python3 plugins/sdlc-lite/scripts/messages.py selftest 2>&1 | grep -c 'ok: .*follow_up_requested' | grep -qv '^0$'`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/messages.py" | { ! grep -q .; }`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
