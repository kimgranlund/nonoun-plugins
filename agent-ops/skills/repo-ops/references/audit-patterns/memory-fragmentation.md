---
date: 2026-04-27
coverage: canonical
peers:
  - orphan-detection.md
  - stale-content.md
  - entry-file-coverage.md
  - ../recipes/continuous-learning-loop.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
primary_sources:
  - https://adr.github.io — ADR conventions; canonical folder layout
  - https://sre.google/workbook/postmortem-culture/ — Google SRE postmortem culture
  - Michael Nygard, "Documenting Architecture Decisions" (cognitect.com/blog/2011/11/15)
  - https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
status: research-verified
---

# Memory-fragmentation detection (delivers Promise 5, "continuously-learning")

> **The premise.** A repo's memory primitives — ADRs, post-mortems, decision logs, RFCs — only compound if they live in **one canonical place per kind** and are reachable from AGENTS.md. When decisions live in PR descriptions, post-mortems live in Slack, and runbooks live in Notion, the agent (and every new human) starts from zero on every session. This audit detects the fragmentation and points at the consolidation recipe.

## Where this fits

`../recipes/continuous-learning-loop.md` describes the _flow_ — how decisions and incidents become persistent memory. `../doc-types/adr-pattern.md` and `../doc-types/postmortem-pattern.md` describe the _artifacts_. This file is the _audit_: how to detect that the flow is broken or the artifacts are scattered.

## Four signals of memory fragmentation

| # | Signal | What it looks like | Severity |
| --- | --- | --- | --- |
| 1 | **No `.brain/adrs/` folder despite architectural-shape commits** | `git log --grep='migrate\|switch from\|adopt'` returns 20 hits; `.brain/adrs/` doesn't exist | High |
| 2 | **No `.brain/postmortems/` despite incident-shape commits** | `git log --grep='hotfix\|revert\|incident\|outage'` returns matches; `.brain/postmortems/` empty | High |
| 3 | **Decision/RFC/ADR text scattered outside the canonical folders** | `grep -ri 'decision\|ADR\|RFC' docs/` finds matches in random `docs/notes-*.md` files, not `.brain/adrs/` | Medium |
| 4 | **AGENTS.md missing a "Memory primitives" section** | Agent doesn't know to consult ADRs / post-mortems / runbooks | **Critical** (closes-the-loop check) |

Signal 4 is the most damaging. A repo can have an exemplary `.brain/adrs/` folder with 40 decisions, and if AGENTS.md doesn't tell the agent to _read it_, the artifacts are dead weight on disk.

## The bash check

```bash
#!/usr/bin/env bash
# scripts/check-memory-fragmentation.sh
set -euo pipefail
fail=0

# Signal 1: ADR folder vs architectural-commit volume.
arch=$(git log --since='2 years ago' \
       --grep='migrate\|switch\|adopt\|introduce\|deprecate\|replace.*with' \
       --oneline 2>/dev/null | wc -l | tr -d ' ')
if [ ! -d .brain/adrs ] && [ ! -d docs/adrs ] && [ ! -d docs/architecture/decisions ] && [ ! -d adrs ]; then
    [ "$arch" -gt 5 ] && { echo "FRAGMENT-NO-ADR-FOLDER: $arch arch-shape commits in 2y; no .brain/adrs/."; fail=1; }
else
    n=$(find .brain/adrs docs/adrs docs/architecture/decisions adrs -name '*.md' \
        -not -name 'README.md' -not -name 'INDEX.md' 2>/dev/null | wc -l | tr -d ' ')
    yrs=$(( ($(date +%s) - $(git log --reverse --format=%ct | head -1)) / 31536000 ))
    [ "$yrs" -lt 1 ] && yrs=1
    [ "$n" -lt "$yrs" ] && echo "FRAGMENT-SPARSE-ADRS: $n ADRs for ${yrs}y repo (expected >=$yrs)."
fi

# Signal 2: postmortems vs incident-shape commits.
inc=$(git log --grep='hotfix\|revert\|incident\|outage\|rollback\|emergency' \
      --oneline 2>/dev/null | wc -l | tr -d ' ')
if [ ! -d .brain/postmortems ] && [ ! -d docs/postmortems ] && [ ! -d docs/incidents ] && [ ! -d docs/post-mortems ]; then
    [ "$inc" -gt 3 ] && { echo "FRAGMENT-NO-POSTMORTEM-FOLDER: $inc incident-shape commits; none filed."; fail=1; }
fi

# Signal 3: decision/RFC/postmortem text outside canonical folders.
canonical_re='\.brain/(adrs|postmortems|architecture)/|docs/(adrs|architecture/decisions|postmortems|incidents|post-mortems)/'
find .brain docs -type f -name '*.md' -not -path '.brain/archive/*' -not -path 'docs/archive/*' | while read -r f; do
    echo "$f" | grep -qE "$canonical_re" && continue
    case "$(basename "$f")" in README.md|INDEX.md) continue ;; esac
    if grep -qE '^## (Status|Decision|Consequences)' "$f" 2>/dev/null \
       || grep -qiE '\b(post-?mortem|RFC[- ]?[0-9]|architecture decision record)\b' "$f"; then
        echo "FRAGMENT-MISPLACED: $f is decision/postmortem/RFC-shaped but outside canonical folders."
    fi
done

# Signal 4: AGENTS.md "Memory primitives" section (hard fail).
c=AGENTS.md; [ ! -f "$c" ] && [ -f CLAUDE.md ] && c=CLAUDE.md
if [ -f "$c" ] && [ ! -L "$c" ]; then
    grep -qiE '^## *(memory primitives|memory|where to find|key documents)' "$c" \
        || { echo "FRAGMENT-NO-MEMORY-SECTION: $c lacks a Memory primitives section."; fail=1; }
fi
exit $fail
```

Heuristics are conservative — most findings are advisory. Only signal 4 is gated as a hard finding because it always indicates a closed-loop break.

## What each signal recommends

### Signal 1 — no `.brain/adrs/` despite architectural commits

**Recommendation.** Bootstrap the folder with `recipes/adr-introduction.md` (planned per the INDEX). The first ADR (`0001-record-architecture-decisions.md`) is the meta-decision: "we will record architectural decisions". Then back-fill 3-5 of the most-impactful past architectural changes as historical ADRs.

### Signal 2 — incidents without post-mortems

**Recommendation.** Create `.brain/postmortems/` (or `docs/incidents/`). For commits matching the incident heuristic (`hotfix`, `revert`, `outage`), do _not_ try to retroactively reconstruct post-mortems for events the team didn't review. Instead: install the convention going forward, and as the next SEV-1 / SEV-2 happens, run the post-mortem flow per `../doc-types/postmortem-pattern.md`.

### Signal 3 — misplaced decision/RFC/postmortem text

**Recommendation.** Move the file. The audit emits a `git mv` suggestion:

```bash
# For each FRAGMENT-MISPLACED file, the recommendation is:
git mv docs/notes-on-postgres-decision.md .brain/adrs/0014-use-postgres-not-mysql.md
# Then re-number to fit the existing sequence; update any inbound links.
```

Re-numbering is mandatory if the canonical folder uses sequential numbering. The audit does not auto-rename — too easy to break links — but it lists all candidates so the consolidation can be batched in one PR.

### Signal 4 — no Memory primitives section in AGENTS.md

**Recommendation.** Add the section using the template from `../recipes/continuous-learning-loop.md`:

```markdown
## Memory primitives

- **Before architectural changes**, read `.brain/adrs/` newest-first. If your
  proposed change conflicts with an `Accepted` ADR, write a new ADR
  superseding it; don't silently override.

- **When debugging a production issue**, search `.brain/postmortems/` for
  prior occurrences. Many "new" bugs are repeats.

- **When you make a mistake the user has to correct**, ask: "Should I add
  this to AGENTS.md so I don't repeat it?" Most of the time the answer is
  yes. Add a one-line correction with a dated parenthetical.

- **When a runbook is needed for a recurring operation**, file it in
  `.brain/runbooks/` rather than embedding it in AGENTS.md.
```

This is the single highest-leverage edit in any audit — without it, Promise 5 isn't being delivered no matter how many ADRs the repo has.

## Out-of-repo memory (the harder problem)

A category of fragmentation the bash check can't detect: decisions and post-mortems that live _outside_ the repo entirely — in Slack threads, Notion pages, Confluence, Linear comments, Google Docs, meeting notes, individual engineers' brains.

The audit can't grep these. What it _can_ do is emit an advisory finding:

```text
ADVISORY: Repo has 47 PRs in 12 months that mention "RFC", "decision", or "design doc"
in their description but no ADRs were written. Consider whether decisions are
being captured durably, or only in transient PR descriptions.
```

```bash
# Heuristic for the advisory
gh pr list --state merged --limit 200 --search "RFC OR decision OR \"design doc\"" \
    --json number,title --jq '. | length' 2>/dev/null
```

The fix is cultural, not mechanical: the team agrees that "decision in a PR description" → "ADR in `.brain/adrs/`" before merge. The PR template change is in `../recipes/continuous-learning-loop.md` (Flow 2).

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| AGENTS.md missing Memory primitives section | **Critical** | Closes-loop check; artifacts on disk are dead weight without it |
| `.brain/adrs/` missing AND repo has architectural-shape commits | High | Decisions are evaporating into PR descriptions |
| `.brain/postmortems/` missing AND repo has incident-shape commits | High | Lessons aren't compounding |
| Decision-shaped content outside canonical folders | Medium | Discoverability breaks; agent won't find it |
| Sparse ADRs (<1 per year of repo age) for repos >2 years old | Medium | Likely under-capture; advisory |
| Out-of-repo memory (Slack/Notion) | Advisory | Cultural fix; audit emits a recommendation, not a hard finding |

## What this pattern is NOT for

- **Detecting whether individual ADRs are well-written** — that's a content-quality check, not a fragmentation check. See `../doc-types/adr-pattern.md` for the format rubric.
- **Detecting stale ADRs** — ADRs are immutable; "stale" doesn't apply. An ADR replaced by a newer one is `Superseded`, not `stale`. The audit explicitly excludes `.brain/adrs/` from `stale-content.md`'s heuristic 1.
- **Detecting that a post-mortem is blameless** — the convention is in `../doc-types/postmortem-pattern.md`; the audit doesn't enforce it because language analysis is unreliable.
- **Runbooks** — `.brain/runbooks/` is mentioned in the Memory primitives template but isn't its own audit category yet (could be added in v0.3.0).

## Cross-references

- Continuous-learning loop (the flow this audit verifies): `../recipes/continuous-learning-loop.md`
- ADR pattern (the canonical artifact format): `../doc-types/adr-pattern.md`
- Post-mortem pattern (the other canonical artifact format): `../doc-types/postmortem-pattern.md`
- Orphan detection (sibling — finds unreachable docs, here we find scattered ones): `orphan-detection.md`
- Stale-content (sibling Promise 3 audit): `stale-content.md`
- Entry-file coverage (precondition — AGENTS.md exists to host Memory primitives section): `entry-file-coverage.md`
