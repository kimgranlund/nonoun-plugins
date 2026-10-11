---
id: T-0447
title: "Document standards: registry, core rules, six family cards, schemas, templates, glossary, checks, and pointers"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L4             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role or person writing any document type in this repo or a consumer repo finds one registry row, one short card, and a template or schema, and the checkable parts are checked by a script.

## Intent
- Do (one ticket, one build): from the maintainer's source list `docs/planning/doc-standards/source-list.md`, build `docs/specs/doc-standards/` as designed in the thread: `README.md` (the registry: type, home, standard, template or schema, check, advisory or enforced), `core.md` (shared rules: Simplified Technical English and Plain Language rules, EARS, RFC 2119 meanings, stable IDs, evidence marks `[V]` and `[U]`, status words), and six family cards `intent.md` (goals as OKR with KPI IDs, KPIs, PRD, spec/SRS, epic), `design.md` (HLD with C4, LLD, API docs, ADR), `work-items.md` (agent task and ticket schema, bug, feature request, chore, spike, issue titles, labels, definition of done), `delivery.md` (commits, PR title and body, review comments, changelog, release), `knowledge-ops.md` (runbooks, test plans, reports, research notes, postmortems, policies, system prompts, glossary rules). Add `docs/references/glossary.md` (one term, one definition, aliases marked unapproved; seeded with this repo's own terms: ticket, lane, step, level, handoff, verifier, close-first, plan doc), `docs/assets/schemas/` (ticket, KPI and test-case schemas as JSON or YAML) and `docs/assets/templates/` (bug, feature request, spike, PR body, postmortem, runbook, ADR).
- Checks: add `docs_check.py` rules only for what a script can verify, each with a positive case and an observed negative control: a KPI file has every schema field; a requirement has an ID and an acceptance criterion; an ADR file holds one decision; a runbook has numbered steps; RFC 2119 keywords in a policy are uppercase; a report's evidence pointers resolve; the registry lists every card and every template path exists. Registry rows with no check stay marked advisory.
- Reach: add one pointer line to the managed docs block (through `onboard.py`, never `onboard setup` over the root AGENTS.md) and to `docs/README.md`; `skills/plan-goal`, `ticket`, `file` and `fleet-retro` each gain a Read-first line citing their card instead of restating rules; `plan-doc` cites the intent card.
- Reconcile, do not copy: the registry maps this repo's existing ticket template and vocabulary (status proposed, ready, blocked, done, dropped plus claimed and paused from T-0444; size L1 to L4; type feature, bug, chore, spike, idea; priority P1 to P3) to the work-items card; commits in this repo stay plain subjects with the Co-Authored-By trailer, and the delivery card marks Conventional Commits as the consumer-repo standard and not this repo's, unless the maintainer changes it; the user-level `doc-writing-rules` is cited as the prose authority, not copied.
- Non-goals: rewriting existing docs to the new standards; Conventional Commits enforcement; a role overlay for doc writing (a later ticket, gated on T-0442); any model or effort change.
- Done when: `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` exits 0 with the new rules, each new rule has an observed-red negative control in `docs_check.py selftest`, `python3 scripts/check-packaging.py` and `bash plugins/sdlc-lite/scripts/check.sh` exit 0, the registry lists every type of the source list with a card, every template and schema path in it exists, no em or en dash in any new file, and `git diff --check` is clean.

## Context
Source: `docs/planning/doc-standards/source-list.md`. Existing contracts: `docs/AGENTS.md` and its managed block, `docs/layout.md`, `docs/planning/docs-schema/design.md`, `docs_check.py` (D, G, B and R rules), `plugins/sdlc-lite/skills/{plan-goal,plan-verification,plan-doc,ticket,file,fleet-retro}`, the ticket templates under `skills/ticket/templates/`, `docs/specs/sdlc-lite/lane-lifecycle.md` section 8.1 (ticket and tracker directive). The user-level doc contract is `doc-writing-rules` (harness and docs plugins).

## Constraints
One lane, one build, hot files one writer at a time (`docs_check.py`, `check.py`, `onboard.py`). Never edit a generated file. Docs edits to `docs/AGENTS.md` only inside the managed block via `onboard.py`. State only what a file or command shows; mark unverified claims. If the build passes its budget, stop and report.
