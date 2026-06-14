---
date: 2026-04-27
coverage: extended
peers:
  - adr-pattern.md
  - decisions-log.md
primary_sources:
  - https://sre.google/workbook/postmortem-culture/ — Google SRE postmortem culture
  - https://sre.google/sre-book/example-postmortem/ — Google SRE example postmortem
  - https://www.atlassian.com/incident-management/postmortem/templates — Atlassian postmortem templates
  - https://github.com/dastergon/postmortem-templates — most-cited template catalog
status: research-verified
---

# Post-mortem pattern

> **Storage convention.** This skill recommends `.agents/brain/postmortems/` (most common) or `.agents/brain/incidents/` (also common). Avoid `.agents/brain/traces/` — "traces" risks being read as observability traces (OpenTelemetry / Jaeger), which is a different concept.

## What a post-mortem is

A **dated write-up of an incident**: what happened, what the impact was, what caused it, what we did, what we learned. Filed after the incident is resolved; serves as **memory** so the same failure doesn't repeat.

The load-bearing principle is **blameless**: post-mortems describe systems failures, not personal failures. People did what felt reasonable given the information they had. The post-mortem looks for systemic improvements — process, tooling, alerting, documentation — not someone to blame.

Source: [Google SRE — Postmortem Culture: Learning from Failure](https://sre.google/workbook/postmortem-culture/).

## Two canonical templates

### Google SRE postmortem (the gold standard)

Sections (per Google's [example postmortem](https://sre.google/sre-book/example-postmortem/)):

- **Summary** — one paragraph
- **Impact** — users affected, duration, severity
- **Root causes** — the underlying _why_ (often plural)
- **Trigger** — the proximate event that fired the latent bug
- **Resolution** — what stopped the bleeding
- **Detection** — how we noticed (monitoring? user report? both?)
- **Action items** — concrete follow-ups, with owners + due dates
- **Lessons learned** — what went well / what went poorly / where we got lucky
- **Timeline** — chronological log with timestamps

Stored internally at Google as Google Docs, not Markdown — but the structure ports directly to Markdown.

### Atlassian postmortem template

Sections (per [Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)):

- **Summary**
- **Leadup** — what was happening before
- **Fault** — the specific failure
- **Impact**
- **Detection**
- **Response**
- **Recovery**
- **Five Whys** — recursive root-cause drill
- **Action items**

Atlassian's split between _Detection / Response / Recovery_ maps cleanly to incident-management process steps; the skill recommends this structure for teams with formal IM tooling.

## Filename + storage

Recommended:

```text
.agents/brain/postmortems/
├── 2026-04-12-checkout-outage.md
├── 2026-03-08-payment-double-charge.md
├── 2026-01-22-search-degradation.md
└── README.md   # index, sorted newest-first
```

Filename pattern: `YYYY-MM-DD-short-incident-name.md`. The date prefix sorts chronologically.

`.agents/brain/incidents/` is an accepted alias. `.agents/brain/post-mortems/` (with hyphen) also works. Pick one and stick with it.

## File template (Google SRE flavor)

```markdown
---
date: 2026-04-12
status: resolved
severity: SEV-2
duration: 47 minutes
---

# Checkout outage — 2026-04-12

## Summary

For 47 minutes on April 12 starting at 14:23 UTC, the checkout endpoint
returned 500s for ~30% of requests due to a database connection-pool
exhaustion triggered by a bot scrape.

## Impact

- ~12,000 affected users
- ~$40K in dropped revenue
- SEV-2 declared at 14:31 UTC

## Root causes

1. Connection pool sized for normal load only; no headroom.
2. Bot scrape was not detected by rate-limiter (User-Agent allow-listed
   in legacy config from 2024).
3. No alert on connection-pool saturation; alert fired only on response-
   latency p95.

## Trigger

GoogleBot-impersonating scrape from AS12345, 14:21 UTC, 800 req/s.

## Resolution

- Killed scrape via WAF rule (14:55 UTC).
- Connection pool drained naturally over 90s.

## Detection

User report at 14:27 UTC. Internal alert fired 14:29 UTC.

## Action items

- [ ] (Alice, due 2026-04-19) Add connection-pool-saturation alert.
- [ ] (Bob, due 2026-04-26) Review WAF allow-list; remove stale entries.
- [ ] (Charlie, due 2026-05-03) Right-size connection pool with headroom.

## Lessons learned

### What went well
- Time-to-resolution was 32 minutes once root cause identified.
- WAF tooling was usable without a vendor escalation.

### What went poorly
- 4 minutes between user report and our alert firing.
- WAF allow-list hadn't been reviewed in 18 months.

### Where we got lucky
- Scrape happened at 14:23 UTC (low-traffic window). At peak we'd have
  exhausted the pool faster.

## Timeline (UTC)

- 14:21 — bot scrape begins
- 14:23 — first checkout 500
- 14:27 — user report in #incidents
- 14:29 — internal latency alert fires
- 14:31 — SEV-2 declared
- 14:48 — root cause identified (DB connection pool)
- 14:55 — scrape blocked at WAF
- 15:10 — incident resolved
```

## How AGENTS.md should reference post-mortems

In the `Where to find things` section:

```markdown
- **Post-mortems:** `.agents/brain/postmortems/` — newest-first; read when investigating recurring issues
```

In the `Memory primitives` section:

```markdown
- **When debugging a production issue**, search `.agents/brain/postmortems/` for prior occurrences. Many "new" bugs are repeats of fixed-and-forgotten issues.
```

## Audit checks for post-mortems

1. **Folder exists** at `.agents/brain/postmortems/` (or `.agents/brain/incidents/` — accepted alias).
2. **Filename pattern is consistent** (`YYYY-MM-DD-name.md`).
3. **Each post-mortem has a `status:` field** (resolved / ongoing / blocked) and `date:`.
4. **An index file (`README.md`) exists** in the folder, sorted newest-first.
5. **`.agents/brain/postmortems/` is referenced from AGENTS.md**.

The audit should NOT flag a missing `.agents/brain/postmortems/` folder for projects that haven't had production incidents — heuristic: search commit log for `revert`, `incident`, `outage`, `hotfix` to estimate whether the project should have post-mortems.

## Trigger rules — when to write a post-mortem

A post-mortem is _not_ required for every bug. The skill recommends writing one when **any one** of:

1. **A `release(.*hotfix` commit lands within 24h of a non-hotfix `release(` commit.** This is the canonical trigger — the hotfix exists _because_ something escaped the prior release. The mechanism that allowed the escape needs writing down.
2. **A consumer-facing bug spent more than 1h in `latest` on npm** (or equivalent — the user-visible default channel for the package). The lag-to-detection is the unit of regret; capture how it happened and shorten the next loop.
3. **An audit emits a `severity: high` finding affecting anything outside `[Unreleased]`.** OPEN findings on shipped artifacts are incidents-in-waiting; if they trace to a published version, write the post-mortem.
4. **A trip-wire (CI gate, pre-commit hook) failed silently and the failure mode was discovered post-hoc.** "The check that should have caught this didn't" is exactly the class of process lesson post-mortems exist to capture.
5. **A user-reported runtime error against a tagged release.** External-detected runtime failures are the cleanest signal that internal verification missed.

The point isn't ceremony — it's that the _mechanism_ of failure is captured _once_, in plain text, so the next session inherits the diagnosis instead of re-walking it. A post-mortem that says "we'll be more careful" is failing the test; one that says "we'll add `<specific trip-wire>`" passes.

**Mapping to `repo-ops` artifacts.** When a post-mortem identifies a structural fix (new trip-wire, new convention, new generator), record the finding-to-fix pairing in `.agents/brain/findings/INDEX.md` under `## Graduations`. The post-mortem is the narrative; the graduations table is the structured index. See [`../recipes/findings-index-readout.md`](../recipes/findings-index-readout.md).

## Common anti-patterns

- **Folder named `.agents/brain/traces/`** — confused with observability traces.
- **No date prefix on filename** — files don't sort chronologically.
- **Post-mortem is a finger-pointing exercise** — violates blameless principle. Convert to systems-language.
- **Action items without owners or due dates** — they don't get done.
- **No timeline section** — losing the "what happened when" loses the chance to improve detection.
- **Not linked from AGENTS.md** — agent doesn't know to check.

## Cross-references

- ADR pattern (architecture decisions, separate concept): `adr-pattern.md`
- Decision log (collection of ADRs): `decisions-log.md`
- AGENTS.md "Memory primitives" section: `../standards/agents-md-spec.md`
- Memory-organization recipe: `../recipes/memory-organization.md`
