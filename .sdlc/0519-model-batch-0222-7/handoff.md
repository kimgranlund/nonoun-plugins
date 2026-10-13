---
id: T-0519
title: "Model batch: planner, architect, plan-reviewer, verifier, scout, researcher, filer, messenger, conductor (maintainer decisions 2026-10-12)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0516, T-0517]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One model-table change records the maintainer's decisions of 2026-10-12 for the roles not yet changed, with one new eval and one lock. Builder and solo rows are already changed (commit 266cb9dc, T-0516, T-0517).

## Intent
- Do (Claude, `adapters/claude/levels.json`, `scripts/run.sh` case rows, `skills/level-rubric/SKILL.md` tables, generated agents):
  planner L1 sonnet high, L2 opus medium, L3 opus high (was sonnet medium, opus medium, opus xhigh);
  architect L1 opus xhigh (was fable high);
  plan-reviewer L1 fable high (was opus high; off Opus so it differs from the Opus planners);
  verifier L1 opus low, L2 sonnet high, L3 fable xhigh unchanged (was L1 sonnet medium, L2 sonnet high);
  scout L1 sonnet low (was claude-haiku-5-5 low);
  researcher L1 sonnet high (was sonnet medium; L2 and L3 unchanged);
  filer L1 sonnet low (was sonnet medium);
  messenger: `model: sonnet` and `effort: low` in `agents/messenger.md` frontmatter (was claude-haiku-5-5);
  conductor: `model: opus` and `effort: medium` in `agents/conductor.md` frontmatter (was unpinned).
  Codex (`adapters/codex/models.json`): scout L1 gpt-6.1-sol low (was gpt-5.6-terra low). Every other Codex row unchanged.
- Verifier family rule: `dispatch.py prepare` keeps a verifier off the builder's or solo's model family. Builders are now Opus at L1, L3, L4 and L5 and Sonnet at L2; solos Sonnet L1, Opus L2 and L3. Add selftest cases proving: an Opus build gets a Sonnet verifier at L1 and L2, an Opus L4 or L5 build gets the Fable L3 verifier, a Sonnet build gets an Opus L2 verifier; observed red where the code needs a change. Stop and report if a case cannot pass.
- Update every pin of the old rows (`check.py` items and constants, `dispatch.py` and `solo_run.py` selftest expectations, docs that state them). Add one new eval (`evals.py add`, then `evals.py lock --eval`) recording the decisions and that no replay ran; The Pareto read is from Artificial Analysis blogs, secondary, unverified (`docs/reports/` has no copy; cite the maintainer decision).
- Non-goals: any other row; Codex rows other than scout; the Codex conductor (stays gpt-6-astra medium); prices.json recalibration (note it).
- Done when: `claude_roles.py generate --check`, `codex_roles.py generate --check`, `evals.py check`, `dispatch.py selftest`, `solo_run.py selftest`, `codex-selftest.py`, `check.py` and `check-packaging.py` exit 0 (check.py may fail only on the unrelated progressive-context link); the family-rule cases observed red where a code change was needed.

## Context
Decisions are in `.sdlc/notes.md` (2026-10-12 entries) and the Pareto read in this session's chat: Sonnet 5.5 is competitive at high effort and dominated at xhigh and max; Opus medium beats Sonnet high for about $1 more per task; Opus xhigh matches Sonnet max for about half the cost. Sources are third-party summaries of Artificial Analysis.

## Constraints
Model and effort are the maintainer's decision: change exactly the rows above. One writer on the model tables; runs after T-0516 and T-0517 merge, and after the evals same-day fix if it has landed (else use a new eval with the date trick the builder change used: reset the lock file to the version before the last lock commit and lock the extended latest eval).
