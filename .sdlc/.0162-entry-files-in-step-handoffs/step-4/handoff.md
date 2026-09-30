## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 4: check.py pins the Read first contract
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

In `plugins/sdlc-lite/scripts/check.py`, add a contract check that the phrase `Read first` appears in each of these files:
- `agents/planner.md`
- `agents/builder.md`
- `agents/verifier.md`
- `skills/fix/SKILL.md`
- `skills/chain/SKILL.md`
- `skills/handoff-format/SKILL.md`
- `scripts/steps.py`

Each miss is reported as `FAIL <rel>: read-first route missing "Read first"`. Add a negative control in the style of the finish-in-session and builder-scope checks: the check must flag the file when the phrase is removed from its text. Add a numbered item for it to the module docstring.
### Acceptance criteria
- ``d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && sed -i.bak "s/Read first/Read later/g" "$d/p/agents/builder.md" && { python3 "$d/p/scripts/check.py" "$d/p" > "$d/out" 2>&1; test $? -eq 1; } && grep -F agents/builder.md "$d/out" | grep -qF "Read first"``
- ``d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && sed -i.bak "s/Read first/Read later/g" "$d/p/skills/fix/SKILL.md" && { python3 "$d/p/scripts/check.py" "$d/p" > "$d/out" 2>&1; test $? -eq 1; } && grep -F skills/fix/SKILL.md "$d/out" | grep -qF "Read first"``
