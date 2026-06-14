---
date: 2026-04-27
coverage: canonical
peers:
  - greenfield-setup.md
  - audit-existing-repo.md
  - concurrent-learnings-merge.md
  - recommend-then-validate.md
  - ../audit-patterns/redundancy-detection.md
  - ../audit-patterns/staleness-tooling.md
  - ../doc-types/adr-pattern.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices
status: research-verified
---

# Cold-start harvest (importing existing learnings into `repo-ops`)

> **The premise.** Existing repos already have buried learnings: a fat `CLAUDE.md` from 2024, ADRs trapped in PR descriptions, post-mortems in Slack screenshots, an old `NOTES.md` in root, multiple competing convention docs. The destructive default — _delete it all and start fresh_ — loses signal. The trusting default — _import everything_ — imports stale and contradictory content. Cold-start harvest is the opinionated middle path: **inventory, triage, archive-the-junk, rehome-the-good, supersede-the-conflicts, preserve-the-archaeology**.

## How this differs from `greenfield-setup.md`

|  | Greenfield | Cold-start harvest |
| --- | --- | --- |
| Existing docs | None | Many, varying age and quality |
| Conflicts | Impossible | Likely; resolution is the hard part |
| Default disposition | Create canonical artifacts | Triage existing artifacts; _then_ create canonical |
| Time | Hours | Days (with iteration) |
| Bounding | Linear procedure | Heuristic-bounded — don't try to harvest everything |

If your repo is genuinely new, use `greenfield-setup.md`. If it's older than ~3 months and has any documentation at all, use this recipe.

## Where the buried learnings live (inventory targets)

```bash
# Likely-stale top-level files
find . -maxdepth 3 -type f \( \
  -name '*NOTES*' -o -name '*WIP*' -o -name '*PLAN*' -o \
  -name '*OLD*' -o -name '*LEGACY*' -o -name '*BACKUP*' -o \
  -name 'STYLEGUIDE*' -o -name 'CONVENTIONS*' \
\)

# Markdown not in canonical locations
find . -name '*.md' -type f \
  -not -path './.agents/brain/adrs/*' \
  -not -path './.agents/brain/postmortems/*' \
  -not -path './.agents/brain/runbooks/*' \
  -not -path './.agents/brain/architecture/*' \
  -not -path './.agents/brain/archive/*' \
  -not -path './node_modules/*' \
  -not -path './.git/*'

# Commits that look like recorded decisions
git log --all --grep='decided\|migrate\|switch from\|chose\|deprecate' \
  --pretty=format:'%h %s' | head -50

# PR bodies with ADR-shaped content (requires gh CLI)
gh pr list --state all --limit 200 --json number,title,body --jq '
  .[] | select(.body | test("## (Status|Decision|Consequences)"; "i"))
       | {n: .number, t: .title}'

# Issues labeled as incidents / postmortems
gh issue list --state all --label 'incident,post-mortem,postmortem' --limit 100
```

## The triage matrix

For each found artifact, classify:

| Disposition | Meaning | Default action |
| --- | --- | --- |
| **`keep`** | Already in the right place, current, correct | Leave alone; date-stamp if needed |
| **`rehome`** | Good content, wrong location | Move to canonical location with provenance |
| **`archive`** | Out of date but historically valuable | Move to `.agents/brain/archive/` with provenance |
| **`supersede`** | Conflicts with another artifact | Write resolving ADR; mark both `Superseded` |
| **`reconcile`** | Two artifacts both partially correct, partially wrong | Most expensive: extract truths, write merged canonical, archive originals |
| **`delete`** | Never had value (e.g., `*-copy.md`, generated junk) | Move to archive, not delete (preserve the audit trail) |

### Triage rules of thumb

| Found | Likely disposition |
| --- | --- |
| Current fat `CLAUDE.md` and no `AGENTS.md` | `rehome`: rename to AGENTS.md, generalize wording, demote CLAUDE.md to symlink/pointer |
| `STYLEGUIDE.md` overlapping with AGENTS.md "Conventions" | `reconcile`: pick canonical, demote other |
| `NOTES.md` in root | Read carefully. ADR-shaped sections → extract to `.agents/brain/adrs/` (`rehome`); rest → `archive` |
| `WIP_PLAN.md` | Almost always `archive`. If active work, extract goals into `docs/PLAN.md` |
| `docs/legacy/`, `docs/old/`, `docs/_old_/` | `archive` to `.agents/brain/archive/legacy-import-<date>/` |
| `*_BACKUP*.md`, `*-copy*.md` | `archive` (don't delete; weird ones may have unique content) |
| GitHub issues with `incident` / `post-mortem` label | Read each. Substantive ones → `rehome` to `.agents/brain/postmortems/` with provenance link to original issue |
| PR descriptions with ADR-shaped content | `rehome`: extract to `.agents/brain/adrs/` with provenance pointer to original PR |
| Two `Accepted` ADRs about the same subject (after rehoming) | `supersede`: human reviews, writes resolving ADR |

## The 7 phases

### Phase 1 — Inventory (mechanical)

Run the inventory commands above. Collect into a single `.agents/brain/cold-start-inventory.md` (transient — deleted after phase 7):

```markdown
# Cold-start inventory — 2026-04-27

| Path | Last modified | Size | Triage |
|---|---|---|---|
| ./CLAUDE.md | 2024-09-12 | 240 lines | rehome → AGENTS.md |
| ./NOTES.md | 2023-11-04 | 60 lines | archive (extract `### Postgres decision` → ADR first) |
| ./STYLEGUIDE.md | 2024-03-01 | 90 lines | reconcile with `CONTRIBUTING.md` |
| ./docs/old/architecture-v1.md | 2022-06-15 | 410 lines | archive |
| PR #144 body | (closed 2024-08-22) | — | rehome decision section → .agents/brain/adrs/2024-08-22-graphql-rejection.md |
```

This file is the working artifact. Update it as triage progresses.

### Phase 2 — Triage (human-reviewed)

Walk the inventory in time-bounded sessions. **Set a budget**: 4 hours. Stop when budget exhausted; the rest waits for next iteration. Don't try to harvest everything in one pass.

Triage signals to escalate:

- Anything that says "DO NOT MODIFY" or "SOURCE OF TRUTH" — flag for explicit confirmation before any action
- Anything containing what looks like secrets (API keys, internal hostnames) — flag, don't process automatically
- Anything in a language other than the repo's primary language — out of automated scope; flag for human review

### Phase 3 — Bulk-archive obvious junk (PR)

Anything matching the bulk-archive heuristics (legacy folders, \*\_BACKUP, untouched > 2 years AND unreferenced from any entry file) gets a single PR:

```text
docs: cold-start harvest — bulk-archive 23 stale artifacts

Moved to .agents/brain/archive/legacy-import-2026-04-27/:
- CLAUDE-OLD.md (last modified 2023-04)
- NOTES_2023.md
- docs/old/* (12 files)
- ...

No content lost — preserved with provenance.
```

Each archived file gets a `_Harvested from <original-path> on 2026-04-27 (cold-start harvest, untouched since <date>)_` line at the top.

### Phase 4 — Rehome obviously-good content (per-artifact PRs)

For each `rehome` disposition: separate PR, single artifact at a time.

Example: `CLAUDE.md` (fat, current-ish) → `AGENTS.md`:

1. `git mv CLAUDE.md AGENTS.md`
2. Edit: replace "Claude Code" / "Claude" with "LLM coding agents (Claude Code, Codex, Devin, Cursor, Windsurf, Copilot, …)"
3. Add `_Last reviewed: 2026-04-27_` line + `_Harvested from CLAUDE.md (cold-start)_`
4. Create new thin `CLAUDE.md` (or symlink) per `claude-md-convention.md`
5. PR with title `docs: harvest — rehome CLAUDE.md → AGENTS.md`

For ADRs extracted from PR descriptions: each new ADR includes:

```markdown
---
date: 2026-04-27        # harvest date
status: accepted
harvested_from: PR #144 (closed 2024-08-22)
original_decision_date: 2024-08-22
---

# 2024-08-22-1500-graphql-rejection

_Harvested from PR #144 (https://github.com/example/repo/pull/144) on 2026-04-27 during cold-start harvest. Original decision was made 2024-08-22; this ADR file backfills the artifact._

## Status
Accepted

## Context
[from PR description]
...
```

Provenance is non-negotiable — future audits need to distinguish original artifacts from imported ones.

### Phase 5 — Conflict resolution (ADR-by-ADR, human approval)

After phases 3-4, run the redundancy-detection trip-wire from v1.0 against the rehomed state. Findings will surface:

- Two ADRs with overlapping subject matter
- AGENTS.md sections with internal contradiction
- Conflicting style claims across CONTRIBUTING.md and AGENTS.md

For each conflict: follow the **supersession protocol** from `concurrent-learnings-merge.md`:

1. Surface the conflict
2. Human picks resolution
3. Write a new superseding ADR with full citation
4. Mark originals as `Superseded by <new-ADR>` (do not delete or edit content beyond the status field)

**This phase cannot be auto-applied even at `lax` strictness.** Supersession is a content decision affecting what future agents believe. The recipe forces `recommend-then-validate` with explicit human approval per supersession PR.

### Phase 6 — Provenance pass

Every harvested artifact must carry a provenance line:

```text
_Harvested from <original-path-or-source> on 2026-04-27 (cold-start harvest)._
```

Run a sanity check: every file in `.agents/brain/` modified during the harvest period either has a `_Last reviewed:_` line or a `_Harvested from..._` line. Files missing provenance get flagged.

### Phase 7 — Re-audit

Run the full audit (`audit-existing-repo.md`) against the post-harvest state. Confirm:

- Promise 1 (less-wasteful): no orphans; CLAUDE.md is symlink/pointer to AGENTS.md
- Promise 2 (token-optimized): AGENTS.md ≤200 lines
- Promise 3 (less-stale): all docs dated; no broken cross-refs
- Promise 4 (self-healing): hooks installed (per `self-healing-hooks.md`)
- Promise 5 (continuously-learning): `.agents/brain/adrs/` populated with both new and harvested ADRs; supersession chain intact

If the post-audit shows any `critical` findings, return to phase 5. Iterate until clean.

After phase 7 passes: delete `.agents/brain/cold-start-inventory.md` (it's transient working state, not preserved memory).

## The non-negotiables

1. **No deletes.** Every disposition is `archive` (move to `.agents/brain/archive/`) or `rehome` (move with provenance). Even the "delete" disposition in the triage matrix is implemented as archive. Future archaeology may need the original.
2. **No silent supersession.** When two artifacts conflict, the resolution writes a NEW ADR; the originals are _marked_ `Superseded`, not edited beyond the status field.
3. **Provenance for everything imported.** No exceptions.
4. **Time-bounded passes.** A 6-hour cold-start session is fine; a 6-week project is not. Iterate weekly until clean rather than blocking indefinitely.
5. **Human-in-the-loop for every supersession.** Apply-mode never resolves a content conflict.

## Cost-bounding heuristic

Repos vary wildly in legacy-doc surface. A pragmatic floor:

- **20-doc rule**: triage the 20 most-recently-modified candidate artifacts first. If they cover the substantive learnings, stop. The rest go to bulk-archive without per-artifact triage.
- **6-month rule**: artifacts unmodified for 6 months get default-archived unless they're explicitly referenced from an active entry file.
- **2-year rule**: artifacts unmodified for 2 years AND unreferenced get bulk-archived without review.
- **Half-day budget per session**. If triage takes longer, split into multiple sessions across days.

These rules are conservative — they preserve learnings rather than compressing them. They also don't try to be exhaustive on the first pass.

## Cross-system imports (out of scope)

This recipe assumes everything you want to harvest lives **in the repo today**. Not in scope:

- **Slack post-mortems** — the recipe can't fetch them. Two paths: (a) one-time manual import (effort scales with volume); (b) maintain `.agents/brain/postmortems/external-index.md` linking to authoritative external locations
- **Notion / Confluence pages** — same
- **GitHub issues from a different repo** — same
- **Scattered Slack DMs / email** — never going to be harvested; the institutional knowledge that lives only there will need to be re-derived through the iterate pattern

For external sources, document the _pointer_, not the content. The repo-ops's stance: institutional memory that isn't in the repo isn't reliably consultable by an LLM agent, but a pointer is better than nothing.

## Anti-patterns

- **Bulk-importing without triage.** Imports the staleness alongside the truth. Future audits surface conflicts you could have avoided.
- **Skipping provenance lines** to save effort. You will regret this in 6 months when an audit asks "is this still current?" and there's no way to tell.
- **Auto-superseding conflicts.** Forbidden. Humans pick.
- **Trying to harvest everything in one pass.** Half-day budget rule. Iterate.
- **Treating archived artifacts as deleted.** They're preserved; future agents may consult them. The archive is part of the brain.
- **Forgetting to delete the cold-start-inventory.md** after phase 7. It's working state, not memory.

## Cross-references

- Concurrent learnings merge (related; ongoing operations after cold-start): `concurrent-learnings-merge.md`
- Greenfield setup (the alternative path for new repos): `greenfield-setup.md`
- Audit existing repo (the post-harvest verification step): `audit-existing-repo.md`
- Redundancy detection (where conflict findings come from): `../audit-patterns/redundancy-detection.md`
- ADR pattern (supersession protocol): `../doc-types/adr-pattern.md`
- Recommend-then-validate (the gating mechanism for supersession PRs): `recommend-then-validate.md`
