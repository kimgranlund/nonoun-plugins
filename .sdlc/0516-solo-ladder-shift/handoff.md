---
id: T-0516
title: "Solo ladder follows the builder ladder shifted down one: solo L1 Sonnet high, L2 Opus medium, L3 Opus high"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Claude solo table is the builder table shifted down one level: solo L1 = builder L2 (Sonnet high), solo L2 = builder L3 (Opus medium), solo L3 = builder L4 (Opus high). The maintainer decided this on 2026-10-12 (a request from the maison conductor; options chosen: "Shift the NEW builder ladder down one"). Codex solo rows are unchanged.

## Intent
- Do: change `plugins/sdlc-lite/adapters/claude/levels.json` `solo` to `{"L1": ["sonnet","high"], "L2": ["opus","medium"], "L3": ["opus","high"]}`; update every place that states or pins the old solo rows (was L1 Sonnet low, L2 Sonnet high, L3 Opus xhigh): `agents/solo.md` level table, `skills/level-rubric/SKILL.md` (the solo row near line 28 and any solo model text), `scripts/check.py` item 18 (`SOLO_WORDS`, `SOLO_CLAUDE`, the item text), `scripts/solo_run.py` selftest (about line 834, "level L3 is opus xhigh"), `scripts/run.sh` solo rows if any, `docs/` references that state the solo rows; regenerate with `claude_roles.py generate` and `codex_roles.py generate`. Add a new eval after `.sdlc/evals/0006-builder-progression-2026-10-12.md` (its date must be later than 0006: use the lane's real date) with `evals.py add` and `evals.py lock --eval`; the eval records the maintainer decision and that no replay ran.
- Verifier family rule: `dispatch.py prepare` keys on the solo record's model (a Sonnet solo gets an Opus L2 verifier, an Opus solo a Sonnet L2 verifier, L3 goes to Fable): confirm from the code and the existing selftest cases at `dispatch.py` around 1579 to 1607 that the new rows route correctly (solo L1 Sonnet to an Opus L2 verifier, solo L2 and L3 Opus to a Sonnet L2 verifier), and add a selftest case for solo L2 on Opus medium with an observed red. Do not change the rule unless a case fails; if one does, stop and report.
- Non-goals: Codex solo rows, builder rows, prices.json recalibration (note the stale price basis in the report if the file keys on model and effort).
- Done when: `claude_roles.py generate --check`, `codex_roles.py generate --check`, `evals.py check`, `dispatch.py selftest`, `solo_run.py selftest`, `check.py` and `check-packaging.py` exit 0 (check.py may fail only on the unrelated progressive-context link); the new dispatch case observed red before the change.

## Context
Origin: the maison conductor's message (its numbers assumed the old builder table, so the maintainer chose the rule over its literal numbers). Builder table now: L1 Opus low, L2 Sonnet high, L3 Opus medium, L4 Opus high, L5 Opus xhigh (T-0503 era commit 266cb9dc).

## Constraints
Model and effort are the maintainer's decision: change nothing beyond the three rows above. One writer on the model tables.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and `python3 -c "import json;print(json.load(open('plugins/sdlc-lite/adapters/claude/levels.json'))['solo'])"` prints `{'L1': ['sonnet', 'high'], 'L2': ['opus', 'medium'], 'L3': ['opus', 'high']}`
- [ ] `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/evals.py check` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and its output holds `ok: solo L2 is opus medium and its record keeps verifier L2 on sonnet`
- [ ] `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0
- [ ] `python3 scripts/check-packaging.py` exits 0
- [ ] `git grep -n -E "Sonnet low|Opus xhigh" -- plugins/sdlc-lite/agents/solo.md docs/specs/sdlc-lite/solo-lane-contract.md` exits 1 (no old solo row text remains)
