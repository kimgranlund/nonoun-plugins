---
id: T-0076
title: "Headless conductors can still abandon work through the Agent tool's..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0072
---

## Goal
A headless sdlc-lite session (SDLC_ROLE set, or SDLC_HEADLESS=1) cannot launch a background subagent through the Agent tool and then end its turn, abandoning the work; interactive sessions are unaffected.

## Intent
Literal ask: block-background.sh matches only Bash, so extend the guard to Agent in headless sessions.
Deltas:
- Agent's run_in_background defaults to background when the field is absent (the Agent tool description: "Subagents run in the background by default"), unlike Bash where absent means foreground: defaulted: in a headless session an Agent call is denied unless tool_input.run_in_background is explicitly false; the deny message tells the model to pass run_in_background: false. (gap: whether the hook should instead rewrite the input via hookSpecificOutput.updatedInput; default: deny with exit 2, matching the existing Bash guard's style.)
- Matcher scope: defaulted: register block-background.sh for the Agent tool in hooks/hooks.json (a separate PreToolUse entry or matcher "Bash|Agent"); block-publish.sh stays Bash-only. The hook must tell Bash and Agent apart by tool_name so the Bash semantics (absent = allowed) do not change.
- Other backgrounding tools (Workflow, Monitor): gap: out of scope; default: not covered by this ticket.
Do: extend hooks/block-background.sh and hooks/hooks.json to cover Agent in headless sessions; extend scripts/hook-selftest.sh with Agent cases (headless + absent -> 2, headless + true -> 2, headless + false -> 0, interactive + absent/true -> 0) while all existing Bash cases keep passing; update every doc that describes the guard as Bash-only (repo CLAUDE.md Layout entry for hooks/block-background.sh, agents/conductor.md, skills/chain/SKILL.md, .claude/agents/sdlc-lite-author.md, and any other hit of grep -rn block-background) so they name Agent too.
Non-goals: guarding Workflow or Monitor; changing block-publish.sh; changing interactive-session behavior.
Done when: bash scripts/hook-selftest.sh prints PASS with the new Agent cases, scripts/check.sh passes, and no doc still describes block-background.sh as Bash-only.

## Context
Follow-up from T-0072 (headless-background-abandon/filer-L1.md):

Headless conductors can still abandon work through the Agent tool's `run_in_background`, which defaults to background. `block-background.sh` matches only Bash, so extend the guard to Agent in headless sessions.

## Constraints
Interactive sessions (no SDLC_ROLE, SDLC_HEADLESS unset or not 1) must be unaffected for both Bash and Agent. Existing Bash behavior and selftest cases must not change. No em dashes in any edited text.
