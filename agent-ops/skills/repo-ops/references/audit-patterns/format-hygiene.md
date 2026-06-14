---
date: 2026-05-30
coverage: canonical
peers:
  - coverage-gaps.md
  - staleness-tooling.md
  - entry-file-coverage.md
  - pointer-validation.md
  - orphan-detection.md
  - stale-content.md
  - memory-fragmentation.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
  - ../recipes/self-healing-hooks.md
  - ../guidance/context-budget.md
primary_sources:
  - https://adr.github.io/ — ADR `Status:` field convention
  - https://github.com/joelparkerhenderson/architecture-decision-record
  - https://sre.google/sre-book/postmortem-culture/ — Postmortem severity + duration metadata
  - https://djw.fyi/portfolio/preventing-drift/ — Daryl White, "Avoiding the Silent Stale Doc Problem"
  - https://keepachangelog.com/ — Keep a Changelog format
status: research-verified
---

# Format hygiene (delivers Promise 3, "less-prone-to-staleness")

> **The premise.** Staleness is invisible without dates. Ownership is invisible without owners. A doc that doesn't _say_ when it was last reviewed cannot be flagged as stale by any automated audit — it's not that the audit is wrong, it's that the doc has refused to answer the question. Format hygiene is the precondition for every staleness check downstream.

## Form vs. content

This is a **form check**, not a **content check**:

| Form check (this file) | Content check (elsewhere) |
| --- | --- |
| Does the file have a `date:` field? | Is the date recent? → `stale-content.md` |
| Does the ADR have a `Status:` field? | Is the status accurate? → manual review |
| Does AGENTS.md have a `_Last reviewed:_` line? | Is AGENTS.md telling the truth? → `redundancy-detection.md` |

Form is mechanizable; content mostly is not. **Enforce form first** — without it, the staleness tooling in `staleness-tooling.md` runs blind.

## Why this is Promise 3's home

Promise 3 depends on _visibility_ of staleness:

```text
date frontmatter → mtime threshold → audit flags stale → human reviews → re-dates or archives
```

Break the first link (no date), break the chain. `git log -1 --format=%cs` is a noisy fallback — a typo fix on a 3-year-old doc looks "fresh." The `_Last reviewed:_` line is the explicit affirmation that someone _reread_ the doc.

## The six hygiene checks

| # | Check | Where it applies | Severity |
| --- | --- | --- | --- |
| 1 | Doc has `date:` YAML frontmatter OR `_Last reviewed:_` line | All canonical docs | High |
| 2 | Doc has YAML frontmatter at all | Canonical reference docs (skills-style) | Medium |
| 3 | AGENTS.md has `_Last reviewed:_` or version line | AGENTS.md, CLAUDE.md (if fat) | High |
| 4 | ADR has `Status:` field | `.agents/brain/adrs/*.md` | High |
| 5 | Postmortem has `severity:` and `duration:` | `.agents/brain/postmortems/*.md` | High |
| 6 | Release-scoped working note has `created:` + `last_edited:` | `.agents/brain/notes/{version}-*.md` | High |

Ownership (`_Owner:_` or `owner:`) is a sixth concern — emit as Medium where missing; small repos can accept "team that owns the parent directory."

## Check 1 — every canonical doc is dated

Two acceptable forms; either passes. **Form A — YAML frontmatter** (`date: 2026-04-27`). **Form B — inline reviewed-line** (`_Last reviewed: 2026-04-27 by @kimba_`).

### Detection

```bash
# A doc is "dated" if it has either form. Otherwise emit finding.
check_dated() {
  local f="$1"
  # Form A: YAML date: field within first frontmatter block
  if head -20 "$f" | awk '/^---$/{i++; if(i==2) exit} i==1' | grep -qE '^date:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
    return 0
  fi
  # Form B: _Last reviewed:_ line anywhere in the file
  if grep -qE '_Last reviewed:_?\s*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$f"; then
    return 0
  fi
  return 1
}

for f in AGENTS.md CLAUDE.md README.md CHANGELOG.md \
         $(find .agents/brain docs -name '*.md' -not -path '.agents/brain/archive/*' -not -path 'docs/archive/*' 2>/dev/null); do
  [ -f "$f" ] && [ ! -L "$f" ] || continue
  if ! check_dated "$f"; then
    echo "UNDATED: $f"
  fi
done
```

CHANGELOG.md is special — it's append-only and dates live per-entry. The check passes if _any_ entry has a date heading like `## [1.2.3] - 2026-04-27`.

## Check 2 — canonical reference docs have YAML frontmatter

For reference material in `.agents/brain/` (not narrative READMEs in `docs/`), missing frontmatter is a smell. The repo-ops convention mirrors this skills library: `date`, `coverage`, `peers`, `primary_sources`, `status`.

### Detection

```bash
# A doc has frontmatter if line 1 is exactly `---`.
for f in $(find .agents/brain docs -name '*.md' -not -path '.agents/brain/archive/*' -not -path 'docs/archive/*' 2>/dev/null); do
  [ -f "$f" ] || continue
  if [ "$(head -1 "$f")" != "---" ]; then
    echo "NO-FRONTMATTER: $f"
  fi
done
```

Medium severity — narrative docs legitimately don't need frontmatter. Reference docs and ADRs/postmortems definitely should.

## Check 3 — AGENTS.md has `_Last reviewed:_` or version line

AGENTS.md is loaded every session; if it can't be cheaply freshness-checked, the staleness story collapses for the most-loaded file in the repo.

### Detection

```bash
for f in AGENTS.md CLAUDE.md; do
  [ -f "$f" ] && [ ! -L "$f" ] || continue
  # Skip thin pointers (≤15 lines)
  [ "$(wc -l < "$f")" -le 15 ] && continue
  # Require either a Last-reviewed line or a Version line
  if ! grep -qE '_Last reviewed:_?\s*[0-9]{4}-[0-9]{2}-[0-9]{2}|^Version:\s*[0-9]+\.[0-9]+' "$f"; then
    echo "NO-REVIEW-LINE: $f"
  fi
done
```

A version line (`Version: 2026.04`) is acceptable — calendar-versioning AGENTS.md is valid for repos that re-cut docs per release.

## Check 4 — every ADR has a `Status:` field

Per [adr.github.io](https://adr.github.io/), an ADR without `Status:` is uninterpretable — readers can't tell if it's `proposed`, `accepted`, `deprecated`, or `superseded`. See `../doc-types/adr-pattern.md`.

### Detection

```bash
# Status field can be in frontmatter (status:) OR in body (## Status: accepted).
for f in $(find .agents/brain/adrs docs/adrs docs/adr docs/decisions -name '*.md' 2>/dev/null); do
  [ -f "$f" ] || continue
  # README/index files are not ADRs
  case "$(basename "$f")" in README.md|index.md|INDEX.md) continue ;; esac
  if ! grep -qE '^status:\s+(proposed|accepted|deprecated|superseded|rejected)|^##\s+Status' "$f"; then
    echo "ADR-NO-STATUS: $f"
  fi
done
```

Accept `proposed | accepted | deprecated | superseded | rejected` (case-insensitive). Custom workflows pass with a warning.

## Check 5 — every postmortem has `severity:` and `duration:`

Per Google's [SRE Book postmortem culture](https://sre.google/sre-book/postmortem-culture/) and `../doc-types/postmortem-pattern.md`, a postmortem without severity + duration is _narrative_ — it can't be aggregated ("incidents per quarter at SEV-1" needs these).

### Detection

```bash
for f in $(find .agents/brain/postmortems docs/postmortems docs/incidents -name '*.md' 2>/dev/null); do
  [ -f "$f" ] || continue
  case "$(basename "$f")" in README.md|index.md|INDEX.md|TEMPLATE.md) continue ;; esac
  has_sev=false; has_dur=false
  grep -qE '^severity:\s*(SEV-?[0-9]|P[0-9]|critical|high|medium|low)' "$f" && has_sev=true
  grep -qE '^duration:\s+' "$f" && has_dur=true
  [ "$has_sev" = false ] && echo "POSTMORTEM-NO-SEVERITY: $f"
  [ "$has_dur" = false ] && echo "POSTMORTEM-NO-DURATION: $f"
done
```

`status:` (resolved / ongoing / blocked) and `date:` fall under Check 1 and Check 2 above.

## Check 6 — release-scoped working notes carry `created:` + `last_edited:`

`.agents/brain/notes/` accumulates the narrative artifacts a release/build cycle produces — release notes, plans, punchlists, peer hand-offs — the markdown complement to the structured `audit-history/*.json`. Without dated frontmatter these rot silently (the Check-1 premise applied to the busiest churn surface in the brain).

**The convention** (transferable; first instantiated in chat-ui, adia-ui-release v1.10.0):

- **Naming** — release-scoped notes are `{release-version}-{topic}.md` (e.g. `0.6.49-release-notes.md`). Version-first sorts the directory by cut and makes `ls .agents/brain/notes/ | grep <version>` the natural query. Non-release working notes keep `{topic}-YYYY-MM-DD.md`; pre-convention files are grandfathered.
- **Frontmatter** — `created:` (set once) + `last_edited:` (bump every edit), both ISO-8601, plus `title` / `version` / `topic` / `status` (`draft|active|final|resolved|superseded`) / `author`. Divergent `created`/`last_edited` with a non-final `status` flags a stale note.
- **Lifecycle** — resolved punchlists/hand-offs are integrated (resolution recorded in the cycle ledger) then **deleted**; release notes settle at `status: final` as the durable per-version record that the Slack/GH-release body derives from.

### Detection

Enforce frontmatter on version-named notes; grandfather the rest. Reference implementation: chat-ui's `scripts/audit/check-brain-notes-frontmatter.mjs` (wired into `npm run check`). Shell equivalent:

```bash
for f in $(find .agents/brain/notes -maxdepth 1 -name '*.md' 2>/dev/null); do
  base="$(basename "$f")"
  case "$base" in README.md) continue ;; esac
  # Release-scoped = leading X.Y.Z- (or X.Y.Z-X.Y.Z- rollup)
  echo "$base" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+\.[0-9]+\.[0-9]+)?[-.]' || continue
  head -1 "$f" | grep -qx -- '---' || { echo "NOTE-NO-FRONTMATTER: $f"; continue; }
  grep -qE '^created:'     "$f" || echo "NOTE-NO-CREATED: $f"
  grep -qE '^last_edited:' "$f" || echo "NOTE-NO-LAST-EDITED: $f"
done
```

The naming convention itself (version-prefix) is a Medium form check; the missing-timestamp finding is High (it's the staleness-invisibility failure).

## Output shape (the gap-report row)

```markdown
- **NO-REVIEW-LINE — `AGENTS.md`** (severity: high)
  - 187 lines of fat instructions, no `_Last reviewed:_` and no `Version:` line.
  - **Promise 3 impact:** the most-loaded file in the repo is invisible to the audit.
  - **Recommendation:** add `_Last reviewed: 2026-04-27 by @kimba_` near the top.

- **ADR-NO-STATUS — `.agents/brain/adrs/0007-pick-postgres.md`** (severity: high)
  - **Recommendation:** add `Status: accepted` (or `superseded by 0014`). See `../doc-types/adr-pattern.md`.

- **POSTMORTEM-NO-SEVERITY — `.agents/brain/postmortems/2026-03-15-checkout-outage.md`** (severity: high)
  - **Recommendation:** add `severity: SEV-2` and `duration: 47 minutes`.
```

## Severity rubric (consolidated)

| Finding | Severity | Why |
| --- | --- | --- |
| AGENTS.md / CLAUDE.md (fat) without `_Last reviewed:_` | High | Most-loaded file invisible to staleness tooling |
| ADR without `Status:` | High | ADR uninterpretable; readers can't tell what's current |
| Postmortem without `severity:` | High | Cannot aggregate; loses analytical value |
| Postmortem without `duration:` | High | Same as above |
| Canonical reference doc without `date:` or `_Last reviewed:_` | High | Invisible to staleness tooling |
| Reference doc in `.agents/brain/` without YAML frontmatter | Medium | Convention drift; advisory for narrative docs |
| Doc without `_Owner:_` or implicit team owner | Medium | Ownership gap; advisory |

## What this pattern is NOT for

- **Content correctness** — `severity: SEV-2` passes hygiene even if the real severity was SEV-1. Content question.
- **Schema validation** — shape only; a typed-skill schema validator is a different tool.
- **Markdown structure** — heading levels, list indentation live in `markdownlint`, called from `staleness-tooling.md`.

## Cross-references

- Coverage gaps (does the file even exist?): `coverage-gaps.md`
- Stale content (is the date recent enough?): `stale-content.md`, `staleness-tooling.md`
- Entry-file shape (AGENTS.md sectional checks): `entry-file-coverage.md`
- Pointer validation (do referenced files resolve?): `pointer-validation.md`
- Orphan detection (is this file linked from anywhere?): `orphan-detection.md`
- Memory fragmentation (are ADRs scattered across folders?): `memory-fragmentation.md`
- ADR template: `../doc-types/adr-pattern.md`
- Postmortem template: `../doc-types/postmortem-pattern.md`
- Self-healing hook (run on commit): `../recipes/self-healing-hooks.md`
- Context budget (AGENTS.md shape rules): `../guidance/context-budget.md`
