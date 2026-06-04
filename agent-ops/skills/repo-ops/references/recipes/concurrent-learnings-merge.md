---
date: 2026-04-27
coverage: canonical
peers:
  - cold-start-harvest.md
  - self-healing-hooks.md
  - recommend-then-validate.md
  - ../audit-patterns/redundancy-detection.md
  - ../doc-types/adr-pattern.md
primary_sources:
  - https://github.com/changesets/changesets — Atlassian-originated changeset pattern (the borrowed convention)
  - https://github.com/googleapis/release-please — alternative changeset/release tool
status: research-verified
---

# Concurrent learnings merge ("sync-and-reason")

> **The premise.** When multiple users (or agents) log learnings to the same `repo-ops` folders, **textual merges hide semantic conflicts.** Person A's PR adds "Tests: Vitest" to AGENTS.md; Person B's PR adds "Tests: Jest" in a different region of the same file. Git accepts both. The repo now contradicts itself, and no merge tool will tell you. This recipe makes the semantic conflicts _visible_.

## What's already trivially mergeable (and what isn't)

| Artifact | Merge story | Conflict risk |
| --- | --- | --- |
| ADRs (`.brain/adrs/<file>.md`) | One file per decision | **Only the next-number race** (two PRs both want `0042-`) |
| Postmortems (`.brain/postmortems/YYYY-MM-DD-*.md`) | Date-prefixed, one per incident | Same-day collision → suffix `-2` |
| Audit-history ledger (`.brain/audit-history/<date>.json`) | Append-only, dated | None — can't conflict |
| **AGENTS.md** (single file) | Standard git merge | **Semantic conflict undetected** |
| **CHANGELOG.md** (single file) | Standard git merge | **Same problem** — and solved by the changesets ecosystem |
| Runbooks, postmortems, ADRs being _edited_ (rare; they should be immutable) | Standard git merge | Should not be common; immutability is the design |

The hard cases are **single-file artifacts that multiple PRs want to extend simultaneously**, and **conflicting decisions** in artifacts git can't see as conflicts.

## Three conventions that solve it

### Convention 1 — Timestamp-prefixed ADR filenames

Replace `.brain/adrs/0042-postgres-choice.md` with **`.brain/adrs/2026-04-27-1342-postgres-choice.md`**.

```text
.brain/adrs/
├── 2026-04-12-1342-use-postgres.md
├── 2026-04-15-0930-deprecate-redis.md
├── 2026-04-27-1100-rest-not-graphql.md
└── README.md     # auto-generated index; assigns ADR-N labels by chronological position
```

The next-number race disappears. ADR-N labels for human reading get computed at index-generation time from chronological order, recorded in `README.md`. The numeric identity ("ADR-42") survives in the _index_, not the filename.

Backwards-compat: existing repos with sequential ADRs don't need to renumber. The convention applies to new ADRs going forward.

### Convention 2 — AGENTS.md changeset pattern

Borrowed directly from [`changesets/changesets`](https://github.com/changesets/changesets) (the Atlassian/Atlaskit tool used by every monorepo of consequence).

**The rule:** PRs that want to modify AGENTS.md don't edit AGENTS.md. They drop a file:

```text
.brain/changesets/2026-04-27-vitest-replaces-jest.md
```

```markdown
---
date: 2026-04-27
author: alice@example.com
target_section: conventions
operation: replace        # add | replace | remove
---

## Replace in "Conventions" section:

- "Tests: Jest" → "Tests: Vitest"

## Why

Migrated from Jest to Vitest in PR #389 (commit a3b4c5d). The "Jest" line in
AGENTS.md is now wrong; this changeset corrects it.
```

A **merge-time consolidation job** (run as a GitHub Action on every push to main, or on a scheduled cadence):

1. Reads all `.brain/changesets/*.md` files in chronological order.
2. **Validates:** do any changesets target the same `target_section` with conflicting `operation`s?
   - Two `add` to "Conventions" with semantically-overlapping content → CONFLICT
   - One `add "use Vitest"` + one `add "use Jest"` for "Tests" → CONFLICT
   - One `replace X→Y` + one `replace X→Z` → CONFLICT
3. **If conflicts:** emit findings, halt consolidation, require human resolution. PR a "consolidation blocker" with the conflict report.
4. **If clean:** apply each changeset to AGENTS.md in chronological order; delete the changeset files; commit `[repo-ops] Consolidate N changesets to AGENTS.md`.

The conflict-detection step is the load-bearing one. It's where "Vitest vs Jest" gets caught — _before_ both land. Use the LLM-on-diff pattern from `staleness-tooling.md` as the conflict-detector.

Same pattern for CHANGELOG.md additions (and `release-please`-style consolidation if release-cadence is the trigger).

### Convention 3 — Post-merge redundancy scan as a scheduled trip-wire

Already exists per `self-healing-hooks.md` (the weekly scheduled audit). The weekly job runs `redundancy-detection.md`'s checks across the merged state and opens an issue when contradictions are found.

This is the _backstop_ for cases where the changeset pattern wasn't used (e.g., direct edits to AGENTS.md by repo maintainers, or runbook edits). It catches:

- AGENTS.md sections with internal contradiction
- Two ADRs with overlapping subject matter (both `Accepted`, both addressing the same decision)
- Repeated facts across docs (Promise 1 redundancy detection)

Output: a `CONFLICT-DETECTED` finding in the audit history ledger and an open GitHub issue tagged `repo-ops`.

## The supersession protocol (when conflict IS found)

The recipe **does not** auto-resolve conflicts. Resolution is a content decision that affects what future agents believe. Process:

1. **Detect** — redundancy-scan or changeset-validator finds the conflict.
2. **Surface** — emit a `CONFLICT-DETECTED` finding with both source paths and the contradiction quoted.
3. **Prompt** — the audit's PR includes a template asking the human reviewer:
   - Which decision is current?
   - Was the older one superseded silently? (If yes, the older one needs `Status: Superseded`.)
   - Or should both be archived in favor of a fresh decision?
4. **Human picks resolution.**
5. **Write a new superseding ADR** (`.brain/adrs/<timestamp>-resolve-X-vs-Y.md`) with:
   - Full citation of both originals
   - Resolution decision + reasoning
   - References both originals in `Supersedes:` field
6. **Mark originals** as `Status: Superseded by <new-ADR>`. Do not delete or edit beyond the status field — preservation is the invariant per `adr-pattern.md`.
7. **Update AGENTS.md** (via a new changeset) to reflect the resolved fact.

This protocol stays human-in-the-loop. Per the v1.1 Yegge alignment: _artifacts compound, not agents._

## Configuration

`.brain/config.toml`:

```toml
[repo-ops.merge]
adr_naming = "timestamp"          # "timestamp" | "sequential" | "hybrid"
agents_md_changesets = true       # require .brain/changesets/ for AGENTS.md edits
changeset_consolidation = "merge" # "merge" (on merge to main) | "manual" | "release"

[repo-ops.merge.conflict_detection]
llm_on_diff = true                # use LLM-on-diff for semantic conflict detection
llm_on_diff_threshold = "medium"  # severity floor for opening blocker PR

[repo-ops.merge.supersession]
require_human_approval = true     # cannot be set to false; documented as hard rule
```

## Anti-patterns

- **Auto-resolving semantic conflicts.** The recipe explicitly forbids this. Conflict resolution is a content decision; humans must own it.
- **Editing AGENTS.md directly when changesets are enabled.** The merge-time job will detect the orphan edits and warn, but discipline matters.
- **Letting changesets accumulate without consolidation.** Once `.brain/changesets/` has >5 files unconsolidated, the audit emits a finding. Consolidate at least weekly.
- **Renumbering ADRs after-the-fact** (sequential scheme). Breaks every link to the old number. If you must use sequential, lock the number at PR-merge time, not PR-creation time.
- **Treating textual merge success as semantic merge success.** Git is a content-addressable store, not a semantic-conflict resolver.

## Cross-references

- Cold-start harvest (related but distinct: importing existing learnings): `cold-start-harvest.md`
- Redundancy detection (the conflict-detection trip-wire): `../audit-patterns/redundancy-detection.md`
- Self-healing hooks (where the scheduled scan runs): `self-healing-hooks.md`
- Recommend-then-validate (consumer of conflict findings): `recommend-then-validate.md`
- ADR pattern (supersession invariants): `../doc-types/adr-pattern.md`
- Audit history ledger (where conflicts get recorded): `../audit-patterns/audit-history-ledger.md`
