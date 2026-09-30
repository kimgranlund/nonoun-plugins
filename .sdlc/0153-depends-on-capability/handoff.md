---
id: T-0153
title: "Ticket depends can name a capability or file, not only a whole ticket"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A ticket can depend on the specific fix it needs (a capability or file) instead of a serial integration ticket, so parallel work is not blocked until a human overrides the dependency.

## Intent
Literal ask: Ticket depends can name a capability or file, not only a whole ticket, so parallel work is not blocked until a human overrides the dependency.
Deltas:
- Entry syntax undefined: gap: exact form for a non-ticket dependency; default: keep `T-NNNN` entries as today and add two new entry forms in the same `depends:` list, `file:<repo-relative path>` (satisfied once that path exists in the repo tree) and `cap:<name>` (satisfied once some ticket with `status: done` lists `<name>` in an optional new `provides: [...]` front matter list).
- Who consumes depends: defaulted: `scripts/tickets.py` is the sole parser (handoff-format SKILL.md); today depends drives only `check` (dangling ids, cycles) and `roadmap` ordering. The change lives there.
- Ordering semantics: defaulted: a `file:` entry never orders or blocks a ticket in the roadmap once the file exists, and is shown as unmet otherwise; a `cap:` entry orders the ticket after the ticket(s) that provide it (as a ticket edge), so cycles are still detected.
- Validation: defaulted: `check` fails on a malformed entry, and on a `cap:` name no ticket provides (like a dangling id); a `file:` path that does not exist yet is not an error (it names a fix still to land), but the roadmap marks it unmet.
- Backward compatibility: defaulted: every existing `depends: [T-NNNN]` ticket and roadmap renders byte-identical; `provides` is optional, never in REQUIRED.
Do: extend `scripts/tickets.py` so `depends:` accepts `T-NNNN`, `file:<path>`, and `cap:<name>` entries and tickets may declare an optional `provides: [<name>, ...]`; update check, roadmap ordering/rendering, and the selftest; document the forms in `skills/handoff-format/SKILL.md` front matter block, `skills/ticket/SKILL.md`, and the ticket templates where they show `depends`.
Non-goals: fanout lane scheduling on depends (fanout does not read depends today); auto-editing existing tickets; any capability registry beyond `provides:`.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with new cases proving a `cap:` edge orders after its provider, a `file:` entry does not block when the file exists, a malformed entry and an unprovided `cap:` fail `check` (negative controls), and existing `T-NNNN` fixtures are unchanged; `bash plugins/sdlc-lite/scripts/check.sh` passes.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 11 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
