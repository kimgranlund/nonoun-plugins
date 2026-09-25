## Task goal
/chain turns a plan into step handoffs with a script, not per-session parsing.

## Step 2: Wire steps.py into check.sh, /chain, and the docs
level: L2
### Do
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/steps.py" selftest || fail=1` after the board selftest line, and mention the steps selftest in the header comment.
- `plugins/sdlc-lite/skills/chain/SKILL.md`:
  - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)` to `allowed-tools`.
  - Step 3: replace "For each `## Step n` block, write `step-<n>/handoff.md` per the step template" with a sentence that runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py split .sdlc/<task>` and says never to parse the plan by hand.
  - Step 4.2: keep the superseded rename as a conductor action. Replace "write fresh `step-<n>/handoff.md` files, rewriting the remaining step handoffs from the newest planner file" with running `steps.py split .sdlc/<task>` after the rename (optionally `--only N` for the steps being rewritten), noting that the script refuses a step dir that still holds builder or verifier output.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: under "Step handoff", add one line saying `scripts/steps.py split` writes these files from the newest planner file and that no one writes them by hand.
- Repo-root `CLAUDE.md`:
  - Add a Layout bullet for `scripts/steps.py`: `split <planner.md | task dir> [--only N]` writes `step-<n>/handoff.md` per the step template, refuses a step dir holding builder or verifier output, and `selftest` proves each failure; `/chain` steps 3 and 4.2 run it.
  - Add "the steps selftest" to the Commands check.sh list.
- `.claude/agents/sdlc-lite-author.md`: add "steps selftest" to the check.sh list on line 19.
- Audit: grep `agents/` and `skills/` for any other instruction to parse `## Step` blocks or to write step handoffs by hand, and point each one at the script. `agents/planner.md` only defines the output format, so leave it unchanged. At plan time no other hits were found.

### Acceptance criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0, and its output includes the steps.py selftest ok lines.
- Negative control: break the steps selftest temporarily (for example, make one assertion false), confirm `check.sh` exits nonzero, then revert.
- `grep -n 'steps.py' plugins/sdlc-lite/skills/chain/SKILL.md` shows the allowed-tools entry, a step 3 line, and a step 4.2 line.
- `grep -n 'write `step-<n>/handoff.md` per the step template' plugins/sdlc-lite/skills/chain/SKILL.md` returns nothing.
- `grep -n 'steps.py' plugins/sdlc-lite/skills/handoff-format/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` has at least one hit in each file.
- `grep -rn '## Step' plugins/sdlc-lite/agents plugins/sdlc-lite/skills` shows only `agents/planner.md` (the format definition) and the handoff-format template.
- The /chain 4.2 text still says the conductor moves step dirs to `step-<n>.superseded-<k>/`.
- The diff touches no file in `scripts/run.sh`, `scripts/board.py`, or `agents/planner.md`.
