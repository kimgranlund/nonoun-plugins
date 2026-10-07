---
id: T-0353
title: "Move every Haiku 4.5 agent to Claude Haiku 5.5 (claude-haiku-5-5), by user decision"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every sdlc-lite agent, script and doc that pins Claude Haiku 4.5 (`claude-haiku-4-5`) pins Claude Haiku 5.5 (`claude-haiku-5-5`) instead, with the eval lock updated.

## Intent
- Do (user decision 2026-10-07, "update any agents that use haiku model to the new haiku 5.5"; this is the authorization AGENTS.md requires for a model change): sources checked on 2026-10-07 at platform.claude.com/docs/en/about-claude/models/overview: Claude Haiku 5.5, API id and alias `claude-haiku-5-5`, 1M context, 128K output, adaptive thinking, default effort `medium`, price from $0.10 per MTok input and $0.50 output (Haiku 4.5 was $1 and $5), retirement not before 2027-10-07. Change the model only: keep effort `low` where it is `low` today (do not move to the new default). Sites: `adapters/claude/levels.json` scout L1, `scripts/run.sh` scout:L1 row, `agents/scout-L1.md` and `agents/messenger.md` front matter (regenerate Claude agents with `claude_roles.py generate`), `scripts/supervisor.py` claude messenger row, `scripts/messages.py` messenger text, `scripts/hook-live-probe.sh` docs, `skills/level-rubric/SKILL.md` ("Haiku 4.5 low" becomes "Haiku 5.5 low" and the alias sentence), `scripts/check.py` (the messenger word list, the cap() expectations, the scout mismatch control: use 5.5), the `dispatch.py` selftests that quote `claude-haiku-4-5`, `hooks/block-role-spawn.sh` (family alias compare still works for haiku), `adapters/claude/prices.json` (haiku family blended rate: refit from recorded runs if any exist for 5.5, else keep the key, say it is unrefit, and note the list price fell 10x so the estimate will overstate), and every non-report doc under docs/ and the skills that names Haiku 4.5. Do not touch dated reports, closed tickets, bench results, or Progressive Context unless it pins haiku. Per the repo rule add an eval `.sdlc/evals/NNNN-haiku-5-5.md` (role scout and messenger, level L1, model claude-haiku-5-5, effort low, host claude; honest pass_rate and cost_usd from the live proof below, `unknown` where not measured) and run `evals.py lock`. Codex has no Haiku row; confirm and say so.
- Non-goals: any other model or effort change; the Sonnet or Opus rows; Codex models.
- Done when:
  - `check.py`, `tickets.py check`, `evals.py check`, `claude_roles.py generate --check`, `codex_roles.py generate --check`, `docs_check.py`, `check-packaging.py` pass, and selftests for dispatch, supervisor, messages, hooks pass.
  - `grep -rIn "haiku-4-5\|Haiku 4.5" plugins docs scripts` outside reports, bench, closed tickets returns nothing except one deliberate historical line in the level rubric if needed.
  - Live proof (observed): a headless conductor in a throwaway project under /tmp (no "claude" in the path) with `claude -p --plugin-dir <worktree>/plugins/sdlc-lite` runs one scout L1 through dispatch.py prepare, Agent and record; the transcript model field reads `claude-haiku-5-5` (or says what it resolved to). If the alias `haiku` resolves to something else, say so and stop short of claiming Haiku 5.5.

## Context
Haiku 5.5 is new (retirement date implies release 2026-10-07). The alias sentence in the level rubric records that `haiku` once resolved to Sonnet 5.5 on the maintainer's login; the 0.21.1 live proof resolved it to claude-haiku-4-5-20251001. Re-check with the new id.

## Constraints
No em or en dashes. No push or publish. Other repos' agents are handled by their conductors, not here.
