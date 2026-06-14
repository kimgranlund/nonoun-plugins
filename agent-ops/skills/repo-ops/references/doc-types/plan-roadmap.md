---
date: 2026-04-27
coverage: canonical
peers:
  - decisions-log.md
  - changelog.md
  - architecture-md.md
primary_sources:
  - https://keepachangelog.com/en/1.1.0/ — Keep a Changelog 1.1.0 (date-stamp convention)
  - https://linear.app/docs/markdown-export — Linear Markdown export (issues / projects)
  - https://help.shortcut.com/hc/en-us/articles/360057451511 — Shortcut Markdown / API export
  - https://docs.basecamp.com/article/29-export-your-account — Basecamp project export
  - https://docs.github.com/en/issues/planning-and-tracking-with-projects — GitHub Projects (issue-tracker plan source)
  - https://www.atlassian.com/agile/project-management/program-roadmaps — Atlassian on roadmaps vs plans
status: research-verified
---

# PLAN.md and ROADMAP.md — active work vs forward-looking

> **PLAN.md is _now_ — what's in flight this week or sprint. ROADMAP.md is _next_ — what's coming this quarter or year.** They are two different documents with different update cadences and different audiences. Conflating them is the most common failure mode.

This pattern delivers **Promise 1 (less-wasteful)** and **Promise 3 (less-prone-to-staleness)**: when the boundary between active and forward-looking is clear, neither doc rots into a TODO graveyard.

## The split

|  | `.agents/brain/PLAN.md` | `.agents/brain/ROADMAP.md` |
| --- | --- | --- |
| **Horizon** | This week / sprint / current iteration | This quarter / half / year |
| **Granularity** | Specific tasks, owners, due dates | Themes, milestones, target months |
| **Cadence** | Updated weekly or per-sprint | Updated quarterly |
| **Audience** | The team doing the work; LLM agents picking up tasks | Stakeholders, leadership, contributors deciding whether to invest |
| **Status verbs** | "in progress", "blocked", "in review", "done" | "planned", "in progress", "shipped", "deferred" |
| **Source of truth** | Often a mirror/export of the issue tracker | Hand-maintained by leads/PMs |

If a team has only one of the two, **`PLAN.md` is the higher-value one for LLM agents** — the agent needs to know what to pick up, not what's coming in Q3. Skip `ROADMAP.md` until there is one to publish.

## PLAN.md — shape and conventions

### Minimal template

```markdown
---
updated: 2026-04-27
horizon: 2026-W17 (Apr 21 – Apr 27)
---

# Plan — Week of 2026-04-21

## In progress

- **[#412] Migrate auth to Auth.js v5** — @alice — due 2026-04-28
- **[#418] Replace Redis with Postgres LISTEN/NOTIFY** — @bob — due 2026-05-02
  - Blocked on ADR-0042 review

## Up next (this week)

- [#421] Cron worker → BullMQ — unassigned
- [#423] Strip dead `lib/legacy/` — @carol

## Done this week

- [x] [#405] Bump TypeScript 5.7 → 5.8 (@alice, merged 2026-04-23)
- [x] [#408] Drop Node 20 from CI matrix (@bob, merged 2026-04-25)

## Archive

See `.agents/brain/archive/plan-2026-W16.md`.
```

### Conventions

- **Date the doc**: Keep-a-Changelog-style `updated: YYYY-MM-DD` in YAML frontmatter, plus an English `Week of …` line in the H1. Without a date stamp the agent can't tell whether the plan is current. ([keepachangelog.com](https://keepachangelog.com/en/1.1.0/) date-stamp convention.)
- **Issue numbers**: link to the tracker so the plan is a _view_, not a parallel source of truth.
- **Owners**: an unowned item drifts. If no one will own it this week, push it to the roadmap.
- **Due dates**: explicit ISO dates beat "next week" — relative dates rot.
- **Archive completed work weekly**: copy the "Done" section to `.agents/brain/archive/plan-YYYY-Www.md` and clear it from `PLAN.md`. The archive is a free changelog.

### The TODO-graveyard anti-pattern

The most common failure: items accumulate, nothing leaves. After a year `PLAN.md` is 800 lines, half of it is "Up next" from 8 months ago, the agent doesn't know which items are real.

Mitigations:

1. **Time-box "Up next"** to the current iteration. Items that don't make it move to `ROADMAP.md` or get closed.
2. **Archive on a fixed cadence** (every Friday, end-of-sprint).
3. **Run a staleness audit**: any line item with a due date >30 days in the past, or unedited for >60 days, is flagged. See `../audit-patterns/staleness-tooling.md`.

## ROADMAP.md — shape and conventions

### Minimal template

```markdown
---
updated: 2026-04-15
horizon: 2026-Q2 / Q3
---

# Roadmap

## Now (Q2 2026)

- **Multi-tenant scoping** — required for enterprise GA. Owner: @alice. Target: 2026-05.
- **Webhook delivery v2** — exponential backoff, replay tooling. Owner: @bob. Target: 2026-06.

## Next (Q3 2026)

- **Self-serve billing portal** — Stripe Customer Portal integration.
- **OpenTelemetry instrumentation** — replace ad-hoc logging.

## Later (2026-H2 and beyond)

- Federated SSO
- Audit-log export to customer S3

## Recently shipped

- 2026-Q1 — SAML SSO (Enterprise tier)
- 2025-Q4 — Async webhook delivery v1
```

### Conventions

- **Now / Next / Later** is the standard public-roadmap shape ([ProductPlan](https://www.productplan.com/learn/now-next-later-roadmap/) popularized this; widely adopted). Keeps things vague enough to ship.
- **No daily-task granularity.** If an item belongs in a sprint, it belongs in `PLAN.md`.
- **Recently shipped** doubles as a release-notes pointer — link to `CHANGELOG.md`.
- **Quarterly review** ritual: at end of quarter, move "Now" → "Recently shipped", promote "Next" → "Now", review "Later".

## Issue-tracker exports — when the plan IS the export

Many teams treat the issue tracker as truth and `PLAN.md` as a generated view. This works well — and the agent gets a Markdown view it can read without API access.

| Tool | Export mechanism | Notes |
| --- | --- | --- |
| **Linear** | [Markdown export](https://linear.app/docs/markdown-export) per issue or project; API for bulk | Project view exports clean Markdown with status grouping |
| **Shortcut (formerly Clubhouse)** | [API + Markdown rendering in CLI](https://help.shortcut.com/hc/en-us/articles/360057451511) | Iteration views map to weekly plans |
| **GitHub Projects** | [GraphQL API](https://docs.github.com/en/graphql/reference/objects#projectv2); community scripts dump views to Markdown | Native to GitHub — no separate auth |
| **Jira** | REST API; `jira-cli`, `gojira` | Heavier setup; usually only worth it for Jira-mandated orgs |
| **Basecamp** | [Account export](https://docs.basecamp.com/article/29-export-your-account) | Coarser; better for archive than weekly plan |

The pattern: a CI job (or pre-commit hook) regenerates `.agents/brain/PLAN.md` from the tracker on a cron schedule, commits the diff. Now the agent reads a current plan without an API token.

## How AGENTS.md links them

In the `Where to find things` section:

```markdown
- **Active plan:** `.agents/brain/PLAN.md` — what's in flight this week
- **Roadmap:** `.agents/brain/ROADMAP.md` — quarterly horizon
```

In the `Memory primitives` section:

```markdown
- **When picking up work**, start at `.agents/brain/PLAN.md`. Items there are scoped for the current iteration.
- **For longer-horizon questions** ("are we going to support X?"), check `.agents/brain/ROADMAP.md` before proposing new work.
```

## Audit checks

1. **Date stamps present** — `updated:` frontmatter or visible date in H1. A `PLAN.md` without a date is unverifiable.
2. **PLAN.md updated within the last 14 days** (sprint cadence). Older = staleness flag.
3. **ROADMAP.md updated within the last 90 days** (quarterly cadence). Older = staleness flag.
4. **No items in PLAN.md with due dates >30 days past** (TODO graveyard).
5. **`.agents/brain/PLAN.md` and `.agents/brain/ROADMAP.md` are referenced from AGENTS.md.**
6. **Archive folder exists** if the team is using weekly archival (`.agents/brain/archive/plan-YYYY-Www.md`).

## Common anti-patterns

- **One file called `TODO.md`** at repo root, mixing this-week and someday. Split it into PLAN.md + ROADMAP.md or kill it.
- **No date on either doc** — agent can't tell if the plan is from last sprint or last year.
- **PLAN.md as immortal backlog** — items added, never removed. Time-box and archive.
- **ROADMAP.md with weekly-task granularity** — wrong horizon. Push detail to PLAN.md.
- **PLAN.md and the issue tracker disagree** — pick one as truth (usually the tracker) and generate the other.
- **Roadmap contains commitments without owners or target months** — it's a wishlist, not a roadmap.

## Cross-references

- Decision log (decisions, not plans): `decisions-log.md`
- Changelog (shipped, not planned): `changelog.md`
- Self-healing PLAN.md regeneration: `../recipes/self-healing-hooks.md`
- Staleness detection: `../audit-patterns/staleness-tooling.md`
- AGENTS.md "Where to find things" section: `../standards/agents-md-spec.md`
