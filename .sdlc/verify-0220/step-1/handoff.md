## Task goal
Independently re-verify T-0212's fixed defect: scripts/check-packaging.py once pinned the PreToolUse route count at 3, which the new warn-handoff-edit.sh matcher broke. The T-0212 L3 verifier returned fail on that, the fix landed afterwards, and no re-verification was recorded.

## Step 1: Re-verify the check-packaging fix
level: L2

### Do
Read-only, in this worktree. Read .sdlc/.0212-handoff-freeze/step-1/verifier-L3.md (section For the next attempt), then the current scripts/check-packaging.py hook route check and adapters/claude/hooks.json. Confirm the route count is no longer pinned to 3 in a way the new matcher breaks, and that registering or unregistering the matcher changes the result. Then run the criteria.

### Acceptance criteria
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- `d=$(mktemp -d) && git worktree add -q --detach $d/w HEAD && python3 - $d/w <<'PY'
import json,sys,pathlib
p=pathlib.Path(sys.argv[1])/'plugins/sdlc-lite/adapters/claude/hooks.json'
h=json.loads(p.read_text())
h['hooks']['PreToolUse']=[e for e in h['hooks']['PreToolUse'] if 'warn-handoff-edit' not in json.dumps(e)]
p.write_text(json.dumps(h))
PY
(cd $d/w && ! python3 scripts/check-packaging.py && ! python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite); r=$?; git worktree remove --force $d/w; exit $r`
