---
id: T-0665
title: "Drop redirect stub skills and shorten level-variant agent descriptions"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
SDLC Lite takes less of the host's capped skill listing and agent catalog: the four plan redirect stubs are gone, and each level-variant agent carries a one-line description under 200 characters instead of repeating its role's full description.

## Intent
- Do: (1) Delete `plugins/sdlc-lite/skills/plan-campaign/`, `plan-doc/`, `plan-fanout/` and `plan-goal/`; remove `plugins/sdlc-lite/scripts/check.py` item 58 and its code (`plan_stubs_bad`, `check.py:1548`, plus the H-2 to H-6 stub exemption noted at `check.py:257`), repoint the planted-budget-list case at `check.py:1403` from `skills/plan-fanout/SKILL.md` to `skills/plan/SKILL.md` (or its fanout reference), and update `docs/references/plugin-compatibility.md:26` and the CHANGELOG. (2) `plugins/sdlc-lite/scripts/claude_roles.py` `definitions()` writes a level variant's description as one short line, `<role> at level <Ln>: <model> <effort>.` plus at most a short pointer to the base role, under 200 characters; update the selftest case that pins the old text and regenerate with `claude_roles.py generate`. (3) Run `codex_roles.py generate` if any generated Codex file changes.
- Non-goals: any model or effort change (`adapters/claude/levels.json` and `adapters/codex/models.json` stay byte-identical); trimming base role or skill descriptions (here 22 sdlc-lite skill descriptions and 12 base agent files exceed 200 characters; that is a routing change and a separate ticket); renaming any agent.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #25, ui-kit-neue audit 2026-10-20.
In the audited session sdlc-lite had 39 skill entries using 13.4K of the 30K-capped skill listing (45%); level variants repeated role descriptions for about 83K characters of agent-catalog deltas; the skill listing cost about 28.3M cache_read (3%) and the agent catalog about 10.7M (1.1%).
Confirmed here: the redirect stubs are four, not five: `grep -l 'Redirect' plugins/sdlc-lite/skills/*/SKILL.md` lists plan-campaign, plan-doc, plan-fanout and plan-goal. Each says "removed in the next minor"; `check.py` item 58 (`plugins/sdlc-lite/scripts/check.py:244`) pins them and says "Ticket D deletes the stubs and this item". Other references to the stub names: `check.py:1403` (a planted-budget negative control that edits `skills/plan-fanout/SKILL.md`) and `docs/references/plugin-compatibility.md:26` (changelog note); CHANGELOG entries are history and stay.
Level variants are generated, never hand-edited: `claude_roles.py:193` builds `'%s Level %s: %s %s.' % (desc, level, model, effort)` from the base role's description; selftest case `claude_roles.py:297` pins that text. Today builder-L2's description is 243 characters and solo-L1's 408. Codex already uses a short line (`plugins/sdlc-lite/scripts/codex_roles.py:163`, `SDLC Lite {role} {level}. Read the handoff; ...`), a precedent for the form. The conductor and `dispatch.py prepare` choose a variant by name, not by description.

## Constraints
No model or effort changes. Agent names, `levels.json`, `models.json` and every generated model and effort line are unchanged. Base role descriptions are unchanged.

## Acceptance criteria
1. `ls plugins/sdlc-lite/skills | grep -cE '^plan-(campaign|doc|fanout|goal)$'` prints 0.
2. `python3 plugins/sdlc-lite/scripts/claude_roles.py selftest` exits 0 and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0; the selftest asserts a level-variant description under 200 characters that names the level, model and effort. That case fails with the change reverted.
3. `python3 -c "import glob,re; L=[len(re.search(r'^description: (.+)$',open(p).read(),re.M).group(1)) for p in glob.glob('plugins/sdlc-lite/agents/*-L[0-9].md')]; print(max(L)); raise SystemExit(max(L)>=200)"` exits 0 (red before the change: prints 408).
4. `git diff <base> -U0 -- plugins/sdlc-lite/agents plugins/sdlc-lite/adapters | grep -E '^[-+](model|effort|model_reasoning_effort)'` prints nothing (base: the build-start sha).
5. `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0, `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exits 0.
6. `python3 scripts/check-packaging.py` exits 0 and `git diff --check` exits 0.

## Outcome
Built by solo (Opus) on base 9e54d63d.
- Deleted `plugins/sdlc-lite/skills/plan-{campaign,doc,fanout,goal}/`. `check.py` item 58 is now a retired line; its code, `PLAN_STUB_KINDS`, `HINT_STUBS` and the H-2 to H-6 exemption are gone; the planted-budget negative control points at `skills/plan/references/fanout.md`.
- `claude_roles.py` `variant_description()` writes `<role> at level <Ln>: <model> <effort>. Same role as the <role> agent.`; the selftest pins the builder-L2 text and asserts under 200 characters naming level, model and effort (both cases FAIL with a 250-character description planted). 23 variants regenerated; no Codex file changed.
- Docs: `plugin-compatibility.md` retired-names note, `prompts.md` hint-rule exemption removed, CHANGELOG `[Unreleased]` entry. Links to the deleted stubs in `docs/reports/2026-10-12-sdlc-lite-astra-review.md` (docs_check S-6 errors) and two specs (D-10 warnings) became code spans naming `/sdlc-lite:plan <kind>`; these files were outside the named scope.
- Criteria: 1 prints 0; 2 selftest PASS, generate --check 0; 3 prints 81, exit 0; 4 prints nothing; 5 codex check 0, check.py 0, prompt_lint 0; 6 packaging 0, diff --check 0. docs_check 0 errors.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: docs/specs/sdlc-lite/plan-doc-executor.md:262 and docs/specs/sdlc-lite/plan-verification.md:96-97 still name `skills/plan-doc/SKILL.md` and `skills/plan-goal/...` as plain-text file paths in historical build tables; they are design history, not links, and no check flags them.) · verifier: verifier-L2 (sonnet) · base: 9e54d63dc092
- Changed: see commits
- Commits: e5bb24b T-0665: Drop redirect stub skills and shorten level-variant agent descriptions
- Check: 1 skills dir holds no plan-(campaign|doc|fanout|goal): pass
- Check: 2 claude_roles selftest and generate --check: pass
- Check: 3 every *-L[0-9].md description under 200 characters: pass
- Check: 4 no model or effort line changed: pass
- Check: 5 codex check, check.py, prompt_lint: pass
- Check: 6 packaging and diff --check: pass
