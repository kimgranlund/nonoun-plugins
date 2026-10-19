---
id: T-0640
title: "onboard: ask instead of dead-ending outside a git work tree"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When `onboard.py` stops with `not a Git work tree`, the onboard skill asks the user one question instead of ending with advice to run `git init`.

## Repro
1. `mkdir /tmp/x && cd /tmp/x`, then run `/sdlc-lite:onboard`.

## Expected
One AskUserQuestion round: `Run git init here (Recommended)`, `Use another folder`, `Stop`. On the first, the skill runs `git init`, then continues at step 2 with `--init`; on the second it reruns from the folder the user names.

## Actual
"Onboarding still can't run ... /Users/kimba/Projects/ui-kit-neue isn't a Git repository ... To fix it, run git init in that folder, or tell me which folder holds the real repository." (user screenshot, 2026-10-19). The skill rule says "Outside a Git work tree the script exits 1 and writes nothing; report the reason.", and `allowed-tools` permits only `onboard.py`.

## Context
- `plugins/sdlc-lite/skills/onboard/SKILL.md` (Rules list, `allowed-tools` frontmatter).
- `plugins/sdlc-lite/scripts/onboard.py` prints the message; the script does not change.
- Question rules: `docs/specs/doc-standards/prompts.md#skill-arguments-and-questions`.

## Constraints
- Skill text and frontmatter only; `onboard.py` is unchanged.
- Never run `git init` without the user choosing it.

## Acceptance criteria
- `grep -q 'Bash(git init' plugins/sdlc-lite/skills/onboard/SKILL.md`
- `grep -q 'Run git init here' plugins/sdlc-lite/skills/onboard/SKILL.md`
- `! grep -q 'writes nothing; report the reason' plugins/sdlc-lite/skills/onboard/SKILL.md`
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0
- `python3 scripts/check-packaging.py` exits 0
- `git diff --name-only $SDLC_BASE_SHA -- plugins/sdlc-lite/scripts/onboard.py | grep -c . | grep -qx 0`
