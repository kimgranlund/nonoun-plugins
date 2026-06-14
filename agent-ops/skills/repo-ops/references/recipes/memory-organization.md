---
date: 2026-04-27
coverage: canonical
peers:
  - greenfield-setup.md
  - adr-introduction.md
  - audit-existing-repo.md
  - continuous-learning-loop.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
  - ../doc-types/decisions-log.md
primary_sources:
  - https://adr.github.io/madr/
  - https://sre.google/workbook/postmortem-culture/
  - https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
  - https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
status: research-verified
---

# Recipe: organize ADRs, postmortems, runbooks, and decision logs (delivers Promise 5)

> **The premise.** Memory primitives only compound if they have _one_ obvious home each. The most common organizational failure is not absence — it's split-brain: `.agents/brain/adrs/` AND `docs/decisions/`, both half-populated, both authoritative-looking. The agent loads both, gets contradictions, and learns nothing. This recipe makes the layout decisive.

## The four memory primitives

| Primitive | What it captures | Storage | Lifecycle |
| --- | --- | --- | --- |
| **ADR** | A specific architectural commitment | `.agents/brain/adrs/NNNN-*.md` | Proposed → Accepted → (Superseded) |
| **Postmortem** | An incident retrospective | `.agents/brain/postmortems/YYYY-MM-DD-*.md` | Drafted → Resolved (mostly immutable) |
| **Runbook** | A repeatable operational procedure | `.agents/brain/runbooks/<verb-noun>.md` | Living; revised in place |
| **Decision log entry** (looser) | A non-architectural commitment too small for an ADR | `docs/decisions/YYYY-MM-DD-*.md` (optional) | Living, dated, lighter-weight |

Plus two adjacent (not memory but co-located):

| Document | Storage | Why it's not memory |
| --- | --- | --- |
| **Architecture overview** | `docs/ARCHITECTURE.md` (or `.agents/brain/architecture/`) | Describes current state, not decision history |
| **Spec / RFC / pre-decision draft** | `docs/drafts/` or `docs/rfcs/` | Pre-decision; converts to ADR when accepted |

## The decision tree (which folder does this go in?)

| If you can say... | It belongs in... |
| --- | --- |
| "We decided to use X instead of Y" (architectural) | `.agents/brain/adrs/` |
| "We picked library X over Y" (small, reversible) | `docs/decisions/` (optional) |
| "On April 12, the checkout broke because..." | `.agents/brain/postmortems/` |
| "To roll out a new region, run these 8 steps" | `.agents/brain/runbooks/` |
| "The system has these services and they talk like..." | `docs/ARCHITECTURE.md` |
| "Here's what we're considering for next quarter" | `docs/drafts/` or `docs/rfcs/` |

If the team can describe each new doc in one sentence, the right folder usually pops out.

## Should I have `.agents/brain/adrs/` AND `docs/decisions/`?

**Most teams: no.** Pick one. ADRs cover both architectural and non-architectural decisions just fine — especially since MADR 4.0.0 (Sept 2024) explicitly broadens scope to non-architectural by renaming the _A_ to _Any_.

**Some teams: yes.** When ADRs feel too heavy for routine choices ("we picked Vitest over Jest"), a lighter `docs/decisions/` folder reduces activation energy. Trade-off: now you have two places to look. Document the split in `.agents/brain/adrs/README.md`:

```markdown
# Decision logs

This repo splits decisions into two folders by weight:
- `.agents/brain/adrs/` — architectural commitments (MADR format, full context).
- `docs/decisions/` — lighter-weight (one-paragraph, dated).

When in doubt, prefer ADR.
```

The audit checks both layouts and flags neither as wrong — only flags when both exist _without_ a documented split rationale. See `../doc-types/decisions-log.md`.

## Where do design docs go?

A "design doc" is usually one of:

| Doc actually is... | Goes in... |
| --- | --- |
| A pre-decision proposal under discussion | `docs/drafts/` (delete after decided) or `docs/rfcs/` (keep with `Status:`) |
| The decision itself, after it's made | `.agents/brain/adrs/NNNN-*.md` |
| The current architecture | `docs/ARCHITECTURE.md` |
| A spec for a feature being built | `docs/specs/` |

The most common confusion: someone writes a "design doc", the team accepts it, and it sits there forever as both pre-decision artifact and post-decision record. Resolve by moving the _decision_ into an ADR (which references the design doc), and archiving the original.

## When is something a runbook vs a doc?

| If a person needs to follow steps to _do_ something | Runbook |
| --- | --- |
| If a person needs to _understand_ something | Architecture / README / docs |

Tells: imperative voice + numbered steps → runbook. Declarative voice + continuous prose → docs. Filename: `<verb>-<noun>.md` (`deploy-staging.md`, `rotate-secrets.md`, `roll-back.md`). Time-stamped runbooks are a smell — runbooks are living; postmortems handle "things that happened on a date".

## File-naming conventions

| Folder | Convention | Why |
| --- | --- | --- |
| `.agents/brain/adrs/` | `NNNN-kebab-case-title.md` (4-digit, sequential) | Numbered for sequence; immutable after Accepted |
| `.agents/brain/postmortems/` | `YYYY-MM-DD-incident-name.md` | Sorts chronologically; date is the unique identifier |
| `docs/decisions/` | `YYYY-MM-DD-decision-name.md` | Sorts chronologically; small enough that numbering is overkill |
| `.agents/brain/runbooks/` | `<verb>-<noun>.md` | No date — runbooks are living |
| `.agents/brain/architecture/` | `<topic>.md` (kebab-case) | Topical, not temporal |
| `docs/drafts/` | freeform | Not yet committed |
| `.agents/brain/archive/` | `original-name-YYYY-MM-DD.md` | Provenance preserved for moved-orphans |

## Index files (`README.md` in each folder)

Every memory folder gets a `README.md` index:

```markdown
# Architecture Decision Records

(...one-paragraph orientation...)

## Index

| # | Title | Status | Date |
|---|---|---|---|
| 0001 | Record architecture decisions | Accepted | 2026-04-27 |
| 0002 | Use Postgres over MySQL | Accepted | 2026-04-27 |

_Last reviewed: 2026-04-27_
```

Postmortems use a similar table sorted newest-first. Runbooks use a flat list grouped by area (deployment / observability / security / data). Auto-generation tools (`adr-log`) work but are optional — hand-curated tables stay accurate longer than people fear.

## Lifecycle: Proposed → Accepted → Superseded

ADR statuses are load-bearing:

- **Proposed** — under discussion. Audit flags Proposed >30 days (probably abandoned).
- **Accepted** — committed. Immutable; only edited for typos, never substance.
- **Rejected** — considered and chosen against. Recorded so it doesn't get re-proposed without context.
- **Deprecated** — no longer active but not yet replaced.
- **Superseded by ADR-NNNN** — replaced by a newer decision. Both ADRs stay; the older one stays in place with the supersession note.

Postmortems: Drafted → Resolved. After Resolved, edits are limited to typos. Runbooks: continuously edited; `_Last reviewed:_` line is the freshness signal.

## How AGENTS.md exposes all of this

The `Where to find things` section enumerates the homes:

```markdown
## Where to find things
- **Architecture:** `docs/ARCHITECTURE.md`
- **Architecture Decision Records:** `.agents/brain/adrs/` (index: `.agents/brain/adrs/README.md`)
- **Decision log (lighter-weight):** `docs/decisions/` (only if your team uses both)
- **Post-mortems:** `.agents/brain/postmortems/` (index: `.agents/brain/postmortems/README.md`)
- **Runbooks:** `.agents/brain/runbooks/` (index: `.agents/brain/runbooks/README.md`)
- **Drafts / RFCs:** `docs/drafts/` (pre-decision; do not treat as committed)
```

The `Memory primitives` section instructs _when_ to read each:

```markdown
## Memory primitives
- **Before architectural decisions**, read `.agents/brain/adrs/` newest-first.
- **When debugging production issues**, search `.agents/brain/postmortems/`.
- **When running operational procedures**, look in `.agents/brain/runbooks/`
  before improvising. If missing, write the runbook *while* doing it.
- **Drafts in `docs/drafts/` are not commitments** — do not implement
  them as if they were ADRs.
```

This closes the continuous-learning loop — see `continuous-learning-loop.md`.

## Common organizational anti-patterns

- **`.agents/brain/adrs/` and `docs/decisions/` both half-populated, no documented split.** Pick one or document the split.
- **Postmortems in `docs/traces/`.** "Traces" reads as observability traces (OpenTelemetry / Jaeger). Use `.agents/brain/postmortems/` or `docs/incidents/`.
- **Runbooks under date-prefix names.** Runbooks are living; date-prefixes lie.
- **Design docs that became ADRs without archiving the originals.** Two sources of truth on the same decision.
- **No index files.** Folder is technically populated but undiscoverable without `ls`.
- **Postmortems in private docs (Notion, Confluence).** Unreachable from the agent; aggressively link from AGENTS.md.

## Cross-references

- ADR pattern: `../doc-types/adr-pattern.md`
- Postmortem pattern: `../doc-types/postmortem-pattern.md`
- Decision log: `../doc-types/decisions-log.md`
- Greenfield setup (creates this layout day one): `greenfield-setup.md`
- ADR introduction (retrofit): `adr-introduction.md`
- Continuous-learning loop: `continuous-learning-loop.md`
- AGENTS.md Memory primitives section: `../standards/agents-md-spec.md`
