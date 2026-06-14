---
date: 2026-05-06
---

# Skill stewardship loop

The continuously-learning loop for procedural memory (skills) — the analog of `harvest repo-ops` for the doc surface.

**Authored:** 2026-05-02 — implements Step 2 of the repo-ops v2.0 skill-stewardship evolution. Pairs with the four stewardship scripts under `scripts/skills/` — `audit-skills.mjs`, `check-skill-frontmatter.mjs`, `draft-skill.mjs`, `iterate-skill.mjs` — each invoked via its `npm run` alias (`audit:skills`, `check:skills`, `draft:skill`, `iterate:skill`). This is the canonical invocation; SKILL.md references the same four by logical name.

## The cadence

Run `npm run audit:skills` at three triggers:

1. **Session-end** of any major work (release cut, multi-day arc, postmortem). Surfaces candidates from procedures the session walked.
2. **Quarterly** as part of the `/repo-ops` audit. Catches accumulated drift — stale refs, redundancy, low-utility skills.
3. **On-demand** when the user asks "is anything stale?" or "what skills should we have?".

Each run produces 0–N findings. Triage by severity:

- **Errors** (currently none from `audit:skills`; `check:skills` produces errors for missing frontmatter).
- **Warns** — stale refs, description redundancy. Fix immediately or document as deferred.
- **Info** — procedure-recurrence candidates, graduation gaps, description-divergence hints. Review; promote to drafts via `npm run draft:skill <name>` when appropriate.

## The 6 detection signals (recap)

| # | Signal | Threshold | What it surfaces |
| --- | --- | --- | --- |
| 1 | Pattern recurrence in journals | ≥ 2 sessions | Procedures walked enough to deserve a skill |
| 2 | Graduations without skills | row mentions script but no skill | Permanent infrastructure that lacks procedural skill capture |
| 3 | Memory citation count | ≥ 3 citations | Memory entries hot enough to warrant skill promotion |
| 4 | Stale path/tag refs in SKILL.md | path doesn't resolve | Skills referencing renamed code |
| 5 | Description-vs-body divergence | body churn ≥ 100 lines | Skills whose body has evolved beyond the description |
| 6 | Pairwise description similarity | Jaccard ≥ 0.6 | Likely-redundant skill pairs |

Thresholds are **defined by the reliability-dial resolver** (`../guidance/reliability-dial.md` § "The resolver") per strictness — the single source of truth. `audit-skills.mjs` reads them from `.agents/brain/config.toml` rather than hardcoding; the values above are the resolver's `normal`-level defaults.

## The triage flow

```text
audit-skills (read-only)
    │
    ▼
finding cluster
    │
    ├─→ stale-skill-ref ──────→ iterate skill --update (fix paths)
    │                            (or: just edit SKILL.md directly)
    │
    ├─→ description-similarity ──→ iterate skill --merge OR
    │                              edit descriptions to differentiate
    │
    ├─→ procedure-recurrence ──→ draft-skill <name> --journal-section ...
    │                            (operator reviews + commits)
    │
    ├─→ graduation-without-skill → draft-skill <name> --audit-finding ...
    │                              (or: skip if mechanical infra is enough)
    │
    └─→ description-divergence-hint ──→ review SKILL.md description vs body;
                                        edit description if stale
```

## Anti-patterns

- **Acting on every info finding.** Info-level signals are advisory. Procedure-recurrence in journals doesn't _always_ mean a skill is warranted — sometimes the recurring section is "Verification" which is just session-end discipline, not a procedure. Triage before promoting.

- **Auto-archiving stale skills.** `audit-skills` doesn't have an `archive` mode for the same reason `repo-ops` doesn't auto-delete orphan docs: a stale skill might just need an `iterate skill --update` pass, not deletion. Archive only after explicit superseded-by designation.

- **Filling out the skeleton in one pass.** `draft-skill` produces a TODO-heavy SKILL.md. The skeleton lays the canvas; **synthesis is a separate pass**, ideally invoking a skill-authoring tool against the skeleton. Don't ship a draft as if it were a finished skill — `check:skills` catches the description-too-short and trigger-phrases-thin cases, but only after you ask CI to validate.

- **Treating user-level skills as in scope.** This audit walks `.claude/skills/` (project-local) only. User-level skills at `~/.claude/skills/` are managed by a separate cadence — they travel across projects and shouldn't be governed by any single project's audit. Run a separate user-level audit quarterly if needed.

## Pairs with

- `lockstep-release` — every coordinated cut graduates infrastructure; the post-publish admin should include `audit:skills` to capture any procedures the cut walked.
- `stale-audit` — sibling sweep for the doc surface.
- `ops-postmortem` — postmortems often surface graduation candidates that map to skills.
- `ops-memory` — when memory entries are superseded by skills, the entry's description should flag the supersession.

## Future evolution

- **Telemetry-based utility detection.** When the harness logs `Skill({skill: X})` invocations, low-utility skills (zero invocations across N sessions despite matching prompts) become detectable. Today only the heuristic divergence-hint exists.
- **Description-vs-body diff.** Today's body-churn-since-description-edit is approximate. A real diff would track which lines of the description haven't been touched since the body changes.
- **Cross-skill pairs-with graph audit.** When skill A says "pairs with B" but B doesn't say "pairs with A", the graph is asymmetric. An audit signal could flag.
- **Skill lifecycle states in frontmatter.** Adding `status: candidate | draft | active | stale | superseded | archived` would let the audit transition skills explicitly through the graph.
