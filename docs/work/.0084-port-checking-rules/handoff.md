---
id: T-0084
title: "Port harness checking-rules into sdlc-lite; add to verifier skills"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
The verifier applies review discipline: evidence to dismiss, run rather than trust a claim, steelman before filing.

## Intent
Literal ask: port harness checking-rules into sdlc-lite as a plugin skill (trimmed, sdlc-lite wording) and list it in agents/verifier.md `skills:` next to checks-that-bite.
Deltas:
- Which parts to keep: defaulted: keep the three-rule Procedure (evidentiary symmetry, runtime over claim, steelman before filing), the Output contract, Failure branches, and the Example, reworded for a verifier checking a builder's step. Drop the harness-only sections ("The invariant's unit", "Semantic-diff soft size budget") and every reference to harness skills or flows (write-handoff, dispatch-ticket, make-skill, check-all-*, skill_lint, docs_check), since sdlc-lite must not depend on harness.
- Skill name: defaulted: keep `checking-rules` (checks-that-bite kept its source name).
- How the verifier uses it: defaulted: agents/verifier.md body names it in one sentence (dismissals and builder claims need a cited check; steelman each fail reason before filing), without changing the verdict format or any other verifier rule.
- Stale records: defaulted: CLAUDE.md's Agent skills line (verifier <- checks-that-bite) and any matching line in .claude/agents/sdlc-lite-author.md name both skills; plugin version bumps 0.8.3 -> 0.8.4.
- Wording: defaulted: no em dashes, no bold inline labels, per repo style.
Do: add plugins/sdlc-lite/skills/checking-rules/SKILL.md (trimmed port), add it to verifier.md `skills:` and body, update CLAUDE.md and the author agent where they list verifier skills, bump plugin.json to 0.8.4.
Non-goals: porting other harness skills (T-0085..T-0087); changing run.sh, levels, or the verdict format; changing checks-that-bite.
Done when: `SDLC_DRY_RUN=1 scripts/run.sh verifier L1 <handoff>` shows checking-rules appended alongside checks-that-bite, the new SKILL.md has no harness references and no em dashes, and `scripts/check.sh` passes.

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/checking-rules/SKILL.md (131 lines). Add as a plugin skill (trimmed, sdlc-lite wording) and list it in agents/verifier.md `skills:` next to checks-that-bite; run.sh appends declared skills. Matters more now that verifier L2 runs on Sonnet high (0.8.3).

## Constraints
Verifier verdict format and all run.sh level tables stay unchanged. The shipped plugin never depends on harness.
