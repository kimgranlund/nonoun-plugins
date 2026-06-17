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

## Four upgrades, specified

These four were once "someday" bullets; each now has a grounded spec, ready for `audit-skills.mjs` to implement. They refine the detection signals above — upgrade 1 adds a lifecycle **axis**, 2 fills the telemetry gap, 3 makes signal 5 precise, 4 adds a graph signal. By design they are **signals + edges, not auto-actions**: the recipe's "no auto-archive" discipline holds — a verdict is surfaced for the operator, never enacted.

### 1 · Skill lifecycle states in frontmatter

Add a `status:` field — a 6-state machine the audit transitions **explicitly**, on evidence:

`candidate → draft → active → stale → {superseded | archived}`, plus a reversible `stale → active`.

| Edge | The evidence that moves it (never a vibe) |
| --- | --- |
| `candidate → draft` | authoring begins — a SKILL.md body exists with valid frontmatter |
| `draft → active` | **a certification act** — passes `check:skills` + the routing bar. Active is _earned_, not automatic on authoring (the data-catalog `certified` model; the RFC "Proposed Standard" tier) |
| `active → stale` | a staleness signal fires (telemetry · drift · age) — _flagged for review_, verdict pending (the ROT "yellow" light) |
| `stale → active` | re-certified after an `iterate skill --update` fixes the cause — the **recovery edge**. Stale is reversible; this is _why_ the recipe forbids auto-archive |
| `stale → superseded` | a **named replacement** covers the same trigger surface — the entry records the successor; the skill stays _loadable but deprioritized_ (RFC 8594 "deprecated, not yet sunset") |
| `stale → archived` | no successor, no demand — obsolete or trivial (ROT) |
| `superseded → archived` | the successor has been stable for a grace window (RFC 8594 "sunset elapsed") |

A `permanent: true` tag exempts an evergreen skill from the staleness sweep (the feature-flag "permanent gate" model — some skills are kill-switch infrastructure, not candidates for decay). _Grounding: API deprecation lifecycles incl. RFC 8594's `Deprecation`/`Sunset` signals; the ROT content triage (redundant/obsolete/trivial); feature-flag lifecycle practice; data-catalog certify/deprecate tags. The biggest correction the research forced: `active` is reached by an explicit **certification gate**, not by default on authoring — and the `stale → active` recovery edge must exist._

### 2 · Telemetry-based utility detection

When the harness logs `Skill({skill: X})`, low-utility skills become detectable — but **invocation count alone is a trap**: it cannot tell _useless_ from _undiscovered_. Use a **two-signal gate**:

- **Signal A — invocations.** Zero (or below a floor) over **N consecutive periods _windowed to the skill's own cadence_** — a quarterly/episodic skill reads "dead" on a monthly window (seasonality is a real false-positive source). Emit `active → stale`, never straight to archive, and only after a confirmation window (the dead-code "log → wait → confirm-zero → act" discipline).
- **Signal B — matched demand.** Of sessions whose intent fell in the skill's trigger domain, what fraction routed _elsewhere or nowhere_? **High match + zero invoke = a discoverability defect** → fix the `description`/`trigger` (the routing-eval signal), do **not** retire. **Zero match + zero invoke = no demand** → a legitimate archive candidate.

The reason-tag (no-demand vs. matched-but-lost) _determines_ the verdict edge (archive vs. fix-routing) rather than leaving it to a guess. _Grounding: dead-feature/dead-code detection (confirm-zero-over-a-window before action), feature-usage "keep/improve/retire" sunsetting, dynamic thresholds keyed to seasonality._

### 3 · Description-vs-body diff (precise, not a line count)

Today's "body churned ≥ N lines since the description was edited" is a _volume_ heuristic — a typo trips it; a semantic rename doesn't. Replace it with a **referential set-difference** (the Darglint missing/extraneous check, adapted to Markdown — stdlib-cheap, no AST needed): extract the concrete tokens the `description`/`trigger` _promise_ — trigger phrases, named modes/commands, capability nouns — and assert each still appears in the SKILL.md body + `references/`; then the inverse — body capabilities the description never mentions. The signal is a **directional, citable list** (_promised-but-absent_ / _present-but-unadvertised_), not a drift score. Run it **edit-paired** (on the body change) so drift is caught in the same commit, not a later sweep; keep the line-count delta only as a cheap pre-filter. _Grounding: docstring-vs-signature drift tooling (Darglint's missing/extraneous parameters); just-in-time comment-code inconsistency detection (the (doc, change) pair is the right unit)._

### 4 · Cross-skill `pairs-with` graph audit

`pairs with` is a **symmetric relation**, which gives two clean stances (the OWL-symmetric vs. SHACL-validate fork):

- **Audit + auto-fix (recommended where links are stored both ways):** build the directed edge set from every skill's `pairs with`; (a) flag a target that doesn't resolve (the **dangling/broken-link** half — run it first); (b) flag any `A → B` where `B → A` is missing (**asymmetric**); (c) **auto-fix** by materializing the reciprocal `B → A` — safe and deterministic, since the relation is symmetric by definition; (d) surface **orphans** (a skill with no inbound or outbound edges). Gate it in CI exactly as a broken-link check runs in CI.
- **Or compute the inverse:** treat a single declaration as the source of truth and _derive_ the reverse at read time — asymmetry becomes unrepresentable and no audit is needed. _Grounding: bidirectional-link tracking (Obsidian computes the inverse rather than storing it); OWL `owl:SymmetricProperty`/`owl:inverseOf` (infer the inverse) vs. SHACL (validate the reciprocal); broken-link checkers (lychee) for the existence half._
