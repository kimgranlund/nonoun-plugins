## Task goal
A verifier output with no pass/fail verdict is reported as an error (no verdict), reruns the verifier, and never counts as a build fail.

## Step 3: /chain, conductor, and repo docs describe the reverify action
level: L1
### Do
- `plugins/sdlc-lite/skills/chain/SKILL.md`, section 4:
  - In the `steps.py next` paragraph (line 30), add `reverify` → verifier at that level to the action list.
  - In rule 4 (or a new sentence next to it), state the rule: a verifier result with no pass/fail `## Verdict` is "no verdict". It reruns the verifier at the same level, is never a fail, never counts toward "a second fail", and never adds `## Previous attempt`. A second consecutive no-verdict at the same build is a stop, so ask the user.
- `plugins/sdlc-lite/agents/conductor.md` line 22: add the same rule in one clause: verifier with no verdict → `reverify` at the same level, never counted as a fail, and a second in a row → stop.
- Repo `CLAUDE.md` `scripts/steps.py` bullet:
  - Add `reverify` to the listed `next` actions.
  - Drop "or result" from the error clause only as far as a no-verdict verifier is concerned. A builder with no Status still errors.
  - Add that a no-verdict verifier result is never counted as a fail and that two in a row stop.
- `.claude/agents/sdlc-lite-author.md`: add a one-line invariant that a verifier result with no verdict maps to `reverify` in `steps.py next` and to 🟡 no verdict in `board.py`, is never counted as a fail, and must stay in sync across steps.py, board.py, chain SKILL.md, conductor.md, and CLAUDE.md.

Do not use em dashes.
### Acceptance criteria
- `grep -q 'reverify' plugins/sdlc-lite/skills/chain/SKILL.md && grep -q 'no verdict' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q 'reverify' plugins/sdlc-lite/agents/conductor.md`
- `grep -q 'reverify' CLAUDE.md`
- `grep -q 'reverify' .claude/agents/sdlc-lite-author.md`
- `! git diff HEAD -- plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/agents/conductor.md CLAUDE.md .claude/agents/sdlc-lite-author.md | grep '^+' | grep -q '—'`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
