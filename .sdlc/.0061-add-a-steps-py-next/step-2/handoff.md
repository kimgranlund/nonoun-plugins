## Task goal
After any builder or verifier run, `/chain` and the conductor get the next escalation action from code (`steps.py next <step dir>`) instead of re-deriving it from prose, so a `plan defect:` tag or a blocked build can no longer be routed to a rebuild by mistake.

## Step 2: Wire /chain, the conductor, and the records to `steps.py next`
level: L2
### Do
- `plugins/sdlc-lite/skills/chain/SKILL.md` section 4: after each builder run and each verifier run, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py next .sdlc/<task>/step-<n>` and follow its first-line action:
  - `build`/`rebuild`/`bump` → builder at that level
  - `verify` → verifier at that level
  - `replan` → the 4.2 path
  - `done` → next step
  - `stop` → ask the user
  - a nonzero exit → stop and report its stderr

  Keep the existing prose rules as the spec. Keep the literal phrases `plan defect` and `Plan review` that `check.py` guards. The frontmatter `allowed-tools` already covers `steps.py`.
- `plugins/sdlc-lite/agents/conductor.md`, escalation line: say that the next action comes from `steps.py next <step dir>` after every builder and verifier run.
- `CLAUDE.md` (repo root):
  - Layout `scripts/steps.py` line: add `next <step dir>` (read-only; prints the next action from the newest builder and verifier results by `order.py`; the action keywords; exit 1 with `steps next:` on stderr on a bad dir or result) and note that /chain step 4 runs it.
  - The "Escalation is enforced by /chain instructions" sentence under Roadmap: say that `steps.py next` now computes the step 4 action in code.
  - The Decisions plan-defect bullet: add that `steps.py next` routes a `plan defect:` tag or a blocked build to `replan`.
- `.claude/agents/sdlc-lite-author.md` line 18: add `steps.py next` to the plan-defect sync list.

No em dashes anywhere.
### Acceptance criteria
- `sed -n '/^## 4\./,/^## 5\./p' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'steps.py next'`
- `grep -q 'steps.py next' plugins/sdlc-lite/agents/conductor.md`
- `grep 'scripts/steps.py' CLAUDE.md | grep -q 'next <step dir>'`
- `grep 'Escalation is enforced' CLAUDE.md | grep -q 'steps.py next'`
- `grep -q 'steps.py next' .claude/agents/sdlc-lite-author.md`
- (guard) `! grep -n '—' plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/agents/conductor.md CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/scripts/steps.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
