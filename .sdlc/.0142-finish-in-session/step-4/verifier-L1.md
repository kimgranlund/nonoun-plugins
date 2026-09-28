<!-- role=verifier level=L1 model=sonnet effort=medium -->
Confirmed: at pre-build HEAD, the criterion is red (file absent, exit 1); on the built tree it's green. Check bites. All criteria confirmed with real evidence.

## Verdict
pass

## Criteria
- `test -f plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: ran in repo tree, exit 0; ran in throwaway worktree at pre-build HEAD (`$SDLC_TMP_WORKTREES/base`), exit 1 (file absent) — check bites.
- `grep -q '^name: fix$' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: command exit 0; file:2 `name: fix`.
- `grep -q '^description: ' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: command exit 0; file:3 `description: Fast lane for a size-S item...`.
- `grep -q '^allowed-tools: ' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: command exit 0; file:5 lists `Bash(...run.sh:*)`, `Bash(python3 ...steps.py:*)`, `Bash(python3 ...tickets.py:*)`, `Bash(python3 ...board.py:*)`, Read, Write, Grep, Glob, AskUserQuestion.
- `grep -q -- '--reason' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: command exit 0; step 4 body uses `tickets.py --root .sdlc close <slug> --reason "..."`.
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: command exit 0; step 2 body: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint .sdlc/<slug>`.
- `grep -q 'sdlc-lite:fix' plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: command exit 0; new Route bullet: "Size S ... → `/sdlc-lite:fix`, the fast lane with no planner, filer, or follow-up tickets."
- `grep -qi 'fast lane' plugins/sdlc-lite/skills/level-rubric/SKILL.md`: pass. Evidence: command exit 0; new `### Loose ends step` section: "The `/fix` fast lane runs builder L1 or L2 (never higher) and verifier L1."
- `grep -qF '/fix' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: command exit 0; "and so does `/fix` for its single `step-1/`."
- `grep -qF 'skills/fix/SKILL.md' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: command exit 0; added to the long-run docs tuple (line ~96) and `FINISH_DOCS['fast lane']`.
- `grep -qF '/fix' CLAUDE.md`: pass. Evidence: command exit 0; Launcher skills bullet now lists `/fix (fast lane for a size-S item: ...)`.
- Negative control (`run_in_background`→`rib` mutation, expect check.py to flag `skills/fix/SKILL.md ... run_in_background`): pass. Evidence: ran the exact criterion command in a throwaway copy, exit 0 (match found).
- Negative control (`sdlc-lite:fix`→`sdlc-lite:fixx` mutation, expect check.py to flag `agents/conductor.md ... sdlc-lite:fix`): pass. Evidence: ran the exact criterion command in a throwaway copy, exit 0 (match found); confirmed via `finish_missing`'s word-boundary regex (`check.py` diff) that this negative control could go red before the builder's regex fix, per the builder's own stated reasoning, and independently verified the current regex source at check.py (`re.search(re.escape(word) + r'(?![\w-])', text)`) does reject `fixx` as a match for `fix`.
- `(guard)` `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: `ok: 18 role levels, 8 agents checked`, exit 0, run directly on the built tree.

## Out of scope changes
`agents/filer.md`, `scripts/tickets.py`, `skills/chain/SKILL.md`, `skills/fanout/SKILL.md`, `skills/file/SKILL.md`, `skills/open-questions/SKILL.md`, `skills/ticket/SKILL.md`, `.sdlc/0142-finish-in-session/handoff.md` show as modified in `git status`, but none of these are in step 4's Do list. Checked: these are accounted for by step-1's and step-2's and step-3's own builder-*.md `## Changes` sections (read directly), matching each file 1:1 to an earlier step, and this step's builder-L2.md lists only the 5 files the Do calls for. Diffed each of those 5 files (`conductor.md`, `level-rubric/SKILL.md`, `handoff-format/SKILL.md`, `check.py`, `CLAUDE.md`) directly and confirmed every hunk matches only step 4's Do items (the `/fix` route bullet, the Loose-ends-step subsection plus the new `/fix` paragraph, the step-handoff writer sentence, the `FINISH_DOCS`/long-run-docs additions, and the Launcher-skills bullet). Not out of scope; dismissing.

## For the next attempt
None.
