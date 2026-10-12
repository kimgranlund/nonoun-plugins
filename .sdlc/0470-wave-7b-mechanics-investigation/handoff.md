---
id: T-0470
title: "P0 from ui-kit-maison: investigate the plugin mechanics behind wave 7b taking 36 hours (12 findings)"
type: spike           # feature | bug | chore | spike | idea
status: claimed      # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L4             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
claimed_by: claude 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 15
---

## Question
For each of the 12 findings in the ui-kit-maison P0, is it confirmed or refuted by the plugin code, which file and rule is at fault, what is the smallest change with a red check, and what is the ranked order by cost?

## Goal
A written investigation report that marks each of the 12 maison findings confirmed, refuted or unchecked from the code, names the file and rule at fault, proposes the smallest change with a red check, and ranks the changes by cost.

## Intent
- Do: read `.sdlc/0470-wave-7b-mechanics-investigation/source-p0.md` (a copy of the P0 from the ui-kit-maison conductor, 2026-10-12; the findings, collector numbers and Done-when are there; the evidence paths it cites live in that repo and are read-only for this spike). Start with the host and conductor agent definitions (`.claude/agents/sdlc-lite-author.md`, `plugins/sdlc-lite/agents/conductor.md`, the generated `-L<n>` files), then `dispatch.py`, `steps.py`, `gate_lock.py`, `fanout.py`, `results.py`, `redck.py`, `tickets.py`. For each finding, confirm or refute from the current code on main (`git log` shows what shipped after v0.22.4: maison may run an older version, so say which version a behavior belongs to), name the file and rule, propose the smallest change with a red check (a selftest case that fails now), and rank by cost using maison's numbers (36 hours, 4 plan versions, 303 verifier runs, $216.35, 867 minutes, 477 of 814 runs unmetered) and what this repo's collector shows. Check each finding against work already shipped or filed before proposing new work: T-0412, T-0413, T-0425, T-0430, T-0446 (record, prepare --tree, red checkpoint key, circular criteria, transcript pricing), T-0408 (held criteria, `deferred <owner>`), T-0421 (bounded plan correction), T-0445, T-0452, T-0455 to T-0457, T-0459 (lanes, gate lock, lint cited paths), and the fleet retro rows `docs/reports/2026-10-11-fleet-retro-12.md` and `docs/reports/2026-10-12-fleet-retro-00.md`; where one covers a finding, say so and what is still missing.
- Scope fence set by the requester and kept: mechanics only (gates, lint, record, dispatch, locks, criteria semantics, liveness). Change no prompt wording, report format text or tone. Record any fix that needs a wording change in a separate section of the report, marked for the language pass (T-0461, T-0465, T-0466 and the author output block); do not make it.
- Finding 11 (the repo-owned lane gate) is outside the plugin unless the plugin ships a gate template: say which. Finding 12 (long gates) may be a documented recipe: propose where it lives.
- Non-goals: editing any script, agent file or skill; filing tickets for the proposals (the maintainer files the top three after reading the report); editing the maison repo; a model or effort change.
- Done when: `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` exists with the 12 findings each marked confirmed, refuted or unchecked, the file and rule at fault with `file:line` pointers that resolve, the smallest change and its red check, the ranked list, what is already covered, the wording-dependent fixes listed apart, and what is unverified; the report passes `docs_check.py`; at most the top three changes are marked "file now".

## Context
Requester: the ui-kit-maison conductor, a P0 relayed 2026-10-12 (not user approval for cost; the maintainer decides what to file). Ask there was one Fable XHigh agent, read-only first. This spike runs the architect role (Fable, high), the strongest read-only row in `levels.json`; no Fable xhigh read-only row exists, and model and effort rows are user decisions, so none was changed. Related this session: the wave 7b retro rows (record no result, deferred owner, gate lock, fanout in a gitignored `.sdlc`), `docs/reports/2026-10-11-solo-fails-and-blocks.md`, T-0464 (ceremony audit, running), T-0460 (report skill with liveness and stall signals).

## Constraints
Read-only against every repo. No model or effort change. Budget cap $15; stop and report at it. Mark inference `[U]`. A fix that changes prompt wording or output text is recorded, not made.
