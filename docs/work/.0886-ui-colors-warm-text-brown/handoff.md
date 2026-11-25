---
id: T-0886
title: "ui-colors: warm text steps 11 and 12 read brown at the default targets"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide and apply how `ui-colors` handles warm text steps 11 and 12 reading brown at the default targets.

## Intent
- Do: keep the defaults (user decision 2026-11-25: document the request) and make the existing Plain-word request ("text looks brown") in `references/system.md` give exact request values for steps 11 and 12 (about Lc 75 / 90), with the light orange 11 and 12 they produce, measured with `scripts/system.mjs`.
- Decision: the user chose to document the request, not to lower the defaults.
- Non-goals: other steps.
- Done when: the criteria below hold.

## Context
- Default targets put steps 11 and 12 at about Lc 83 / 95 against the page; warm hues read brown (light orange 11 `#842c00`, 12 `#270600`; Radix `#cc4e00`, `#582d1d`).
- T-0883 documented it as a Plain-word request in `plugins/design/skills/ui-colors/references/system.md`; defaults unchanged.
- Source write-up: `/Volumes/kimba/Downloads/ui-colors-updates/ui-colors-pr.md` (read-only; never write under `/Volumes/kimba`), "Note on text steps".

## Acceptance criteria
- `references/system.md` names the request values that give the lighter text and the light orange 11 and 12 hex values they produce; running that request with `scripts/system.mjs` reproduces those hex values.
- A `{}` request's output is byte-identical to `main`.
- `node scripts/check.mjs` passes; packaging passes.

## Constraints
- No default change. Edit only `references/system.md` (and `SKILL.md` only if its mapping row must change, staying under 18,000 characters). T-0884 runs in parallel on `system.mjs` and `check.mjs`: do not touch them, `plugins/design/AGENTS.md` or any CHANGELOG.

## Outcome

2026-11-25 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: 091b18ac4159
- Changed: see commits
- Commits: 6641f1a T-0886: ui-colors text looks brown request with measured orange 11 and 12; e7b5d2c T-0886: record lane T-0886-t0886
- Check: 1 `references/system.md` names the request values and the light orange 11 and 12 hex values; runnin...: pass
- Check: 2 A `{}` request's output is byte-identical to `main`: pass
- Check: 3 `node scripts/check.mjs` passes; packaging passes: pass
- Follow-up: note: docs/work/0886-ui-colors-warm-text-brown/handoff.md Context lists... -> notes.md
