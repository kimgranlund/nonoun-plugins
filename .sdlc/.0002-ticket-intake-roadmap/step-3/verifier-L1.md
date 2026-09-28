<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -n 'roadmap.md'` and `grep -n '/ticket'` in handoff-format/SKILL.md each print ≥1 line: pass. Evidence: `grep -n 'roadmap.md' plugins/sdlc-lite/skills/handoff-format/SKILL.md` → line 21; `grep -n '/ticket' ...` → lines 22, 45, 49.
- `grep -n 'tickets.py' CLAUDE.md` and `grep -n '/ticket' CLAUDE.md` each print ≥1 line: pass. Evidence: line 25 (tickets.py); lines 25, 28, 49 (/ticket).
- `grep -n 'sdlc-lite:ticket' plugins/sdlc-lite/agents/conductor.md` prints one line: pass. Evidence: line 14, `- New ticket, or roadmap → /sdlc-lite:ticket`.
- The "neither `run.sh` nor `board.py` requires or parses" sentence is still present/accurate and no sentence claims nothing parses front matter: pass. Evidence: `plugins/sdlc-lite/skills/handoff-format/SKILL.md:45`: "...and neither `run.sh` nor `board.py` requires or parses it. `/ticket new` stamps these fields, `/ticket check` validates them, and `scripts/tickets.py` is the only parser of front matter."
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: ran it directly — output `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `tickets selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, exit code 0.
- `git diff --stat` for this step touches only the files named in Do: pass (with explanation). Evidence: `git diff --stat` shows 5 files: the 4 named in Do (`.claude/agents/sdlc-lite-author.md`, `CLAUDE.md`, `plugins/sdlc-lite/agents/conductor.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md`) plus `plugins/sdlc-lite/scripts/check.sh`. Cross-checked `.sdlc/0002-ticket-intake-roadmap/step-2/builder-L3.md`: that step's own log states "`plugins/sdlc-lite/scripts/check.sh`: added `python3 ... tickets.py selftest ...` and updated the header comment" — the exact diff present now, matching `git diff plugins/sdlc-lite/scripts/check.sh` content. This confirms the check.sh change predates step 3 and step 3 itself only touched the 4 files named in its own Do.

## Out of scope changes
None beyond the pre-existing untracked artifacts from steps 1–2 (`plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/skills/ticket/`), which are not part of step 3's diff and were verified against step-1/step-2 builder logs as belonging to earlier steps.

## For the next attempt
None.
