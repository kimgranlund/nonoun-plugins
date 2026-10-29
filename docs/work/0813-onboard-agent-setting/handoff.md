---
id: T-0813
title: "onboard declares the conductor agent in .claude/settings.json"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`onboard.py setup --init` also declares the conductor as the session agent for Claude Code, so a newly onboarded repository opens in `sdlc-lite:conductor` without a hand edit; `onboard.py check` reports that declaration's state.

## Context
- The user asked (2026-10-29): "the `onboard` skill should also create the local settings.json or settings.local.json with the appropriate orchestrator agent declaration".
- The declaration is `{"agent": "sdlc-lite:conductor"}`. `plugins/sdlc-lite/agents/conductor.md` description already says: Declare per repo with `"agent": "sdlc-lite:conductor"` in `.claude/settings.json`.
- Code: `plugins/sdlc-lite/scripts/onboard.py` (setup, `--dry-run`, `--init`, `check` labels); skill: `plugins/sdlc-lite/skills/onboard/SKILL.md`.
- This repo's own `.claude/settings.json` holds `"agent": "sdlc-lite-author"`: a repository that already names an agent keeps it.

## Do
1. `setup --init` writes `"agent": "sdlc-lite:conductor"` into `.claude/settings.json` (shared, committed: the whole team gets the conductor). A `--local` flag writes it into `.claude/settings.local.json` instead (personal, not committed).
2. Merge, never replace: keep every other key in an existing file; when the file already has an `"agent"` key with any value, leave it and print one `agent: kept <value> in <path>` line. A malformed JSON file is reported and left untouched.
3. `--dry-run` shows the settings change in its diff like the other files. Without `--init`, setup prints `--init would set agent in <path>` on stderr when the declaration is missing.
4. `check` prints one line for the declaration: `current <path>` when either file names `sdlc-lite:conductor`, `other <path>` when it names another agent, `missing .claude/settings.json` when neither does. A missing declaration does not change the exit code.
5. Update the onboard skill's Arguments table and commands for `--local`, and the `check` labels.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with new cases: init on an empty repo writes the declaration; an existing settings file keeps its other keys; an existing `"agent"` value is kept; `--local` writes `settings.local.json`; `check` reports `missing`, `current` and `other`. Each new case fails before the change.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.

## Constraints
- Claude Code only; Codex has no session-agent setting, so the Codex path writes nothing and says so in one line.
- Never overwrite a value the repository set.
