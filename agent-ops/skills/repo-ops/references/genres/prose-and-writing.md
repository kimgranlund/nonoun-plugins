---
date: 2026-04-27
coverage: extended
peers:
  - ../recipes/greenfield-setup.md
  - ../recipes/memory-organization.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
primary_sources:
  - https://diataxis.fr/
  - https://www.amwa.org/page/style_guides
  - https://en.wikipedia.org/wiki/Series_bible
  - https://github.com/errata-ai/vale
status: research-verified
---

# Genre: prose and writing

> **Premise.** repo-ops was designed for code repositories, but five of the six promises (less-wasteful, token-and-context-optimized, less-prone-to-staleness, self-healing partial, continuously-learning) translate cleanly to prose, fiction, journalism, and documentation projects. The skill works — with a vocabulary swap and one fewer trip-wire.

## Where it fits

| Genre | Fit | Why |
| --- | --- | --- |
| Technical documentation | Excellent | Drift-vs-code is the same concern; ADRs map 1:1 to documentation decisions |
| Long-form non-fiction (book) | Excellent | Voice EDRs, source-of-fact registries, revision retrospectives all matter |
| Long-form fiction (novel/series) | Excellent | "Series bible" is exactly the brain metaphor; EDRs become world-building decisions |
| Academic / research-survey writing | Strong | Citation-stale (papers retracted, replaced) is the same as live-link-stale-content |
| Journalism / essays | Partial | Revision retrospectives become "what I'd revise"; EDRs less natural for one-off pieces |
| Screenplay / playwriting | Partial | Character-bible decisions are EDR-shaped; but writers' rooms don't usually want the process ceremony |
| Marketing / SEO copy | Low | Optimization is dominated by A/B testing; not a docs problem |
| Poetry | Poor | Wrong tool. Voice is not decomposable into decision records. |

## Vocabulary translation

| repo-ops (code) | Prose equivalent |
| --- | --- |
| `AGENTS.md` | `STYLE.md` or `VOICE.md` (the canonical style/voice guide) |
| ADR (Architecture Decision Record) | EDR (Editorial Decision Record) — voice/POV/structure decisions |
| Postmortem | Revision retrospective — "what broke in this draft" |
| Runbook | Process ritual — "how I plan a chapter," "submission checklist" |
| Architecture overview | Series bible / world bible (fiction) or content map (docs) |
| Trip-wire | Editorial gate (e.g., "no draft published without sensitivity check") |
| Audit | Manuscript health check |
| Browserslist baseline | House-style baseline (AP, Chicago, NYT, brand-specific) |

## Folder layout (prose adaptation)

```text
.agents/brain/
├── config.toml
├── edrs/                  # editorial decision records (was adrs/)
│   ├── 0001-pov-third-limited.md
│   ├── 0002-no-second-person.md
│   └── 0003-style-guide-AP-not-Chicago.md
├── retrospectives/        # was postmortems/
│   ├── draft-1-feedback-synthesis.md
│   └── reader-survey-q1.md
├── rituals/               # was runbooks/
│   ├── chapter-planning.md
│   └── pre-submission-checklist.md
├── bible/                 # was architecture/
│   ├── characters.md
│   ├── world.md
│   └── timeline.md
├── archive/               # superseded EDRs, abandoned drafts (not deleted)
└── audit-history/         # manuscript-health JSON ledgers
```

The dotfile prefix is _more_ useful for prose than for code: drafts live at the repo root or in `chapters/` / `posts/`, and `.agents/brain/` is structurally clearly the "out of band" memory layer that humans curate but don't read every day.

## Promise-by-promise applicability

| Promise | Applies to prose? | How |
| --- | --- | --- |
| 1. Less-wasteful | Yes | Style-guide drift detection (one canonical, no duplicated style rules across files) |
| 2. Token-and-context-optimized | Yes | Prose has the same agent-context-window problem; STYLE.md ≤200 lines |
| 3. Less-prone-to-staleness | Yes | Citation rot, character-name conflicts across drafts, world-bible vs current-draft drift |
| 4. Self-healing | Partial | Pre-commit hooks for spelling/style work (Vale, markdownlint); but most prose tooling is editor-internal not git-hook-internal |
| 5. Continuously-learning | Yes | Voice/POV decisions accumulate; series spans years; humans curate the editorial log |
| Reliability dial | Yes | A novelist working alone uses `lax`; a magazine staff with multiple writers uses `strict` |

## What translates as-is

- `../standards/agents-md-spec.md` — replace `AGENTS.md` → `STYLE.md`; the 8-section skeleton works (Project overview = book/series overview, Build/test/run = build commands for the manuscript build, Conventions = style rules, etc.)
- `../audit-patterns/orphan-detection.md` — orphan files in `.agents/brain/` not reachable from STYLE.md
- `../audit-patterns/redundancy-detection.md` — same style rule repeated in two files
- `../audit-patterns/format-hygiene.md` — every EDR has a date and status
- `../audit-patterns/staleness-tooling.md` — Vale, lychee work for prose too (Vale is _primarily_ a prose tool)
- `../audit-patterns/token-waste-detection.md` — STYLE.md bloat is the same problem
- `../recipes/self-healing-hooks.md` — Vale + spell + style-rule hooks instead of code linters
- `../recipes/audit-existing-repo.md` — survey an existing manuscript repo
- `../recipes/cold-start-harvest.md` — same procedure for an old manuscript with style notes scattered everywhere
- `../guidance/context-budget.md` — same math; agent context is finite
- `../guidance/reliability-dial.md` — strictness picker

## What needs translation

- `../doc-types/adr-pattern.md` → EDR pattern. Change the `## Status` allowed values to `Drafted | Adopted | Superseded | Abandoned`. Keep the Y-statement / MADR templates.
- `../doc-types/postmortem-pattern.md` → revision retrospective. Replace "incident timeline" with "draft timeline"; keep "blameless" and "what we'd do differently."
- `../doc-types/architecture-md.md` → series bible. matklad's pattern translates: "what is where in this story-world."
- `../doc-types/decisions-log.md` → editorial decision log.

## What doesn't apply

- `../standards/cross-tool-matrix.md` — Cursor/Codex/Devin don't have prose equivalents. Use Claude/ChatGPT/Cursor-for-prose; one entry file (STYLE.md) plus one tool-specific pointer is enough.
- `../audit-patterns/entry-file-coverage.md` — partial. Fewer entry-file conventions in prose; just STYLE.md.
- `../audit-patterns/memory-fragmentation.md` — partial. Less likely to fragment when one author works alone.

## When NOT to use repo-ops for prose

- Single short essay or a one-week project. Overhead exceeds benefit.
- Pure ideation / brainstorming. Premature structuring kills exploration.
- Marketing copy where the "right answer" comes from A/B tests, not editorial decisions.
- Poetry. Voice is not decomposable into decision records.

## Examples in the wild

- **Fiction series bibles** — Brandon Sanderson's wikis, the WGA "showrunner bible" pattern — these are exactly `architecture-md.md` content, just predating the convention.
- **House style guides** — Chicago, AP, NYT, The Economist — these are STYLE.md / EDR collections.
- **Diátaxis / Divio documentation framework** — already practices most of repo-ops's promises; this skill names what's already happening in well-run docs orgs.

## Greenfield prose setup (analogue of `recipes/greenfield-setup.md`)

Drop these files at the repo root of a manuscript or docs repo:

```text
STYLE.md                                       # canonical style/voice guide (≤200 lines)
.agents/brain/
├── config.toml
├── edrs/0001-record-editorial-decisions.md   # bootstrap EDR
├── retrospectives/.gitkeep
├── rituals/.gitkeep
├── bible/.gitkeep
└── archive/.gitkeep
.github/pull_request_template.md               # "Editorial impact" checkbox
```

The 5 promises ship from day one. EDR 0001 records the decision to use EDRs, exactly mirroring ADR 0001 in the code-greenfield recipe.

## Cross-references

- AGENTS.md spec (the analogue of STYLE.md): `../standards/agents-md-spec.md`
- Greenfield setup (procedural): `../recipes/greenfield-setup.md`
- Memory organization (folder layout rationale): `../recipes/memory-organization.md`
- ADR pattern (the EDR template): `../doc-types/adr-pattern.md`
- Reliability dial: `../guidance/reliability-dial.md`
