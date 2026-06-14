---
date: 2026-04-27
coverage: canonical
peers:
  - ../recipes/self-healing-hooks.md
  - ../recipes/continuous-learning-loop.md
  - ../recipes/recommend-then-validate.md
  - ../guidance/reliability-dial.md
primary_sources:
  - Steve Yegge, "Welcome to Gas City" — versioned action ledger pattern
  - https://www.dolthub.com/ — Dolt git-versioned database (Yegge's reference implementation)
status: research-verified
---

# Audit history ledger (the persistent record of every fix)

> _"Every agent action recorded in both a database and version history… Your SOC2 story, sitting right there in the database, already written."_ — Steve Yegge, "Welcome to Gas City"

## What this delivers

Every audit run produces a queryable, versioned artifact. The repo _itself_ becomes its own audit log of how it was fixed over time. This compounds **Promise 5 (continuously-learning)** — the artifacts that accumulate aren't just ADRs and post-mortems, but also a structured record of how the doc surface evolved.

Falls out as a free benefit: SOC2 / compliance / "show me what changed in the last quarter" queries become trivial.

## The ledger structure

```text
.agents/brain/
├── audit-history/
│   ├── 2026-04-27.json
│   ├── 2026-05-04.json
│   ├── 2026-05-11.json
│   └── ...
├── README.md           # generated index, sorted newest-first
└── trends.md           # quarterly summary (optional)
```

One file per audit run, named `YYYY-MM-DD.json` (or `YYYY-MM-DD-HHMM.json` if multiple per day). **Append-only — never modified after the run completes** (immutable, like ADRs and post-mortems).

## The schema

```json
{
  "$schema": "https://repo-ops.dev/schemas/audit-history.v1.json",
  "audit_id": "2026-04-27T13:42:00Z",
  "repo": "github.com/example/example",
  "commit": "abc123def456",
  "strictness": "normal",
  "skill_version": "1.1.0",
  "promises_evaluated": [1, 2, 3, 4, 5],
  "findings": [
    {
      "id": "DRIFT-CLAUDE-AGENTS",
      "promise": 1,
      "severity": "critical",
      "category": "redundancy",
      "file": "CLAUDE.md",
      "message": "CLAUDE.md (240 lines) and AGENTS.md (180 lines) have substantively divergent content."
    },
    {
      "id": "STALE-2026-04-15",
      "promise": 3,
      "severity": "medium",
      "category": "staleness",
      "file": "docs/old-plan.md",
      "message": "Last modified 2024-09-12 (583 days ago); no '_Last reviewed:_' line."
    }
  ],
  "fixes_proposed": 12,
  "fixes_applied": 8,
  "fixes_vetoed": 4,
  "veto_reasons": [
    {"fix_id": "delete-orphan-1", "rule": "delete-always-vetoed"},
    {"fix_id": "edit-agents-md", "rule": "would-exceed-200-lines"}
  ],
  "trip_wires": {
    "lychee": "pass",
    "entry_file_length": "pass",
    "agents_claude_drift": "fail",
    "doc_dates": "pass",
    "orphan_count": 4
  }
}
```

The schema is intentionally simple — no nested objects beyond two levels, no free-text bodies. The whole file should fit in <2KB for a typical run.

## Why JSON, not Markdown

- **Queryable.** `jq '.findings[] | select(.severity=="critical")' audit-history/*.json` answers compliance questions in seconds.
- **Diff-friendly.** Git diff highlights actual content changes, not prose reflow.
- **Schema-validatable.** The `$schema` URL anchors the format; CI can reject malformed entries.
- **Token-cheap.** A structured record consumes a fraction of the tokens Markdown narration would.

For human readers, the generated `audit-history/README.md` summarizes:

```markdown
# Audit history

| Date | Strictness | Findings | Critical | Fixes applied |
|---|---|---|---|---|
| [2026-05-11](2026-05-11.json) | normal | 8 | 0 | 4 |
| [2026-05-04](2026-05-04.json) | normal | 11 | 1 | 6 |
| [2026-04-27](2026-04-27.json) | normal | 23 | 2 | 8 |

_Trend: critical findings down 100% over 14 days. Total findings down 65%._
```

Generated weekly by the scheduled CI workflow.

## How it integrates with the other promises

| Promise | What the ledger adds |
| --- | --- |
| 1. Less-wasteful | Trend data shows whether redundancy is increasing or decreasing |
| 2. Token-optimized | Tracks entry-file line counts over time |
| 3. Less-stale | Tracks % of docs with valid `date:` frontmatter over time |
| 4. Self-healing | Records which trip-wires fired and which hooks caught them |
| 5. Continuously-learning | The ledger _is_ part of the institutional memory; not just curated artifacts but the operational record |

## Privacy considerations

Some teams will not want every audit run committed to a public repo:

- **Public repos:** Either commit the ledger (most useful) or `.gitignore` it (preserves history locally only).
- **Private repos:** Always commit; this is where compliance value compounds.
- **Sensitive findings:** Never put PII or secrets in audit messages. The schema's `message` field should describe categories, not content (✅ "broken link in marketing copy"; ❌ "broken link to <https://internal.example.com/finance/q4-revenue.pdf>").

The audit emits warnings if any finding message contains URL fragments matching common secret patterns (API keys, tokens, internal hostnames).

## Closing the read side — `.agents/brain/findings/INDEX.md`

The ledger is _write-rich, read-poor_. Every audit emits structured findings, but nothing surfaces them — a future session would have to `cat` every JSON to know what's still open. The read-side closure is a generated `.agents/brain/findings/INDEX.md` that folds every `findings[]` entry across the ledger into one sortable view, plus a hand-curated `## Graduations` table tracking finding-to-permanent-infrastructure pairs.

Recipe: [`../recipes/findings-index-readout.md`](../recipes/findings-index-readout.md). Wire it into the same harvest cron that writes the ledger; the index regenerates on every run, the ledger stays append-only.

This is the load-bearing closure for _capture-without-action_ drift — an audit ledger that nobody reads might as well not exist.

## Compliance / SOC2 framing (the free benefit)

Auditors increasingly ask:

- "Show me changes to documented procedures."
- "Demonstrate the last review of [X]."
- "Provide a record of how doc-quality issues were detected and resolved."

The audit history ledger answers all three trivially. It's not a _replacement_ for compliance docs, but it materially reduces the "gather evidence" cost.

## Anti-patterns

- **Manually editing past audit-history files.** Defeats the immutability invariant. Like editing accepted ADRs.
- **Letting the ledger grow without index/trend files.** A flat folder of 200 JSON files is unreadable. The README.md and trends.md surface what's worth seeing.
- **Storing findings _content_ (the actual broken link, the actual stale text)** rather than findings _categories_. Privacy hazard.
- **Including the ledger in token budget calculations.** It's not loaded by agents in normal sessions; it's an out-of-band artifact.
- **Running the audit so often the ledger fills with noise** — once-weekly is the sweet spot for most repos. Daily is overkill outside high-velocity production.

## Cross-references

- Self-healing hooks (where the audit runs): `../recipes/self-healing-hooks.md`
- Continuously-learning loop (the broader context): `../recipes/continuous-learning-loop.md`
- Recommend-then-validate (which writes vetoes into the ledger): `../recipes/recommend-then-validate.md`
- Reliability dial (recorded with each audit run): `../guidance/reliability-dial.md`
