## Task goal
Shipped skill prompts carry no ticket ids or dates that the loading model can't use.

## Step 1: Apply the prompt-audit wording hunks
level: L1
### Do
Done by the conductor as a trivial edit (no builder run). The diff is uncommitted in the work tree: `git diff -- plugins/sdlc-lite/skills`.
1. skills/level-rubric/SKILL.md: drop `(user decision, T-0005)`.
2. skills/checks-that-bite/SKILL.md: "Two measured NCs that went green instead, both from 2026-07-29:" becomes "Two that went green instead:"; "Each entry measured in the wild, each a check that passed while examining nothing." becomes "Each entry is a check that passed while examining nothing."
3. skills/file/SKILL.md step 3.2: "Example (T-0047): the follow-up `...` is a likely duplicate of T-0002 `div crashes on zero divisor`." becomes "For example, a follow-up `...` is a likely duplicate of an open ticket titled `div crashes on zero divisor`."
### Acceptance criteria
- `! grep -n 'T-0005' plugins/sdlc-lite/skills/level-rubric/SKILL.md` and `grep -q "build's model family: after a Fable or Sonnet build" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `! grep -nE '2026-07-29|measured in the wild|Two measured' plugins/sdlc-lite/skills/checks-that-bite/SKILL.md` and `grep -q 'Each entry is a check that passed while examining nothing.' plugins/sdlc-lite/skills/checks-that-bite/SKILL.md` and "Two that went green instead:" is present (it may wrap across a line break).
- `! grep -nE 'T-0047|T-0002' plugins/sdlc-lite/skills/file/SKILL.md` and `grep -q 'likely duplicate of an open ticket titled `div crashes on zero divisor`' plugins/sdlc-lite/skills/file/SKILL.md`
- The diff touches only those three files under plugins/sdlc-lite (`git diff --name-only -- plugins`), changes only the lines named above, and leaves surrounding meaning intact.
- (guard) `git diff --quiet HEAD -- CLAUDE.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
