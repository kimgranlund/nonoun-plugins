---
date: 2026-04-27
coverage: canonical
peers:
  - greenfield-setup.md
  - memory-organization.md
  - audit-existing-repo.md
  - continuous-learning-loop.md
  - ../doc-types/adr-pattern.md
primary_sources:
  - https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
  - https://adr.github.io/madr/
  - https://github.com/joelparkerhenderson/architecture-decision-record
  - https://github.com/npryce/adr-tools
status: research-verified
---

# Recipe: introduce ADRs to an established repo (delivers Promise 5)

> **The premise.** A repo without ADRs has scattered architectural memory — decisions live in PR descriptions, Slack archives, code comments, and senior engineers' heads. The "continuously-learning" promise is broken until the repo has a place to land decisions _at decision time_. This recipe creates that place and seeds it just enough that the practice survives.

## What this recipe is _not_

- **Not** a backfill-everything-ever campaign. Reconstructing 10 years of decisions almost never finishes.
- **Not** a bureaucratic gate. Most PRs aren't architectural; most don't need ADRs.
- **Not** a tooling adoption. `adr-tools` (Pryce) is optional and lightly maintained as of April 2026. `mkdir .brain/adrs/` is enough to start.

## What this recipe _is_

A 60-minute setup that (1) creates `.brain/adrs/` with an index and the bootstrap ADR; (2) backfills 3-5 _load-bearing_ historical decisions; (3) wires the AGENTS.md `Memory primitives` section; (4) adds the architectural-impact checkbox to the PR template; (5) briefs the team in one paragraph.

## Step 1 — Create the ADR home + index

```bash
mkdir -p docs/adrs

cat > .brain/adrs/README.md <<'EOF'
# Architecture Decision Records

This folder captures architectural decisions. Each ADR is dated, numbered,
and immutable — decisions don't get edited; they get superseded.

Format: MADR 4.0.0 (https://adr.github.io/madr/) for new ADRs.
Read newest-first. See `../../AGENTS.md` "Memory primitives" for when
to consult.

## Index

| # | Title | Status | Date |
|---|---|---|---|
| 0001 | Record architecture decisions | Accepted | 2026-04-27 |

_Last reviewed: 2026-04-27_
EOF
```

## Step 2 — Bootstrap ADR 0001

Use the Nygard format ([cognitect.com 2011](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)) for the bootstrap; canonical templates in `../doc-types/adr-pattern.md`. The bootstrap ADR records the decision to _use ADRs_ — without it, future contributors don't know whether the practice is required.

Save as `.brain/adrs/0001-record-architecture-decisions.md` (full content in `greenfield-setup.md`). Update the README index.

## Step 3 — Backfill 3-5 load-bearing historical ADRs

This is where teams either succeed or burn out. **Do not try to backfill every past decision.** Pick the 3-5 commitments that (a) are still live, (b) get questioned by new contributors, (c) would change the agent's behavior if it knew them.

### How to find them — git archaeology in 20 minutes

```bash
# 1. Framework / library / runtime introductions
git log --diff-filter=A --name-only --pretty=format:'%h %ad %s' --date=short \
    -- 'package.json' 'Gemfile' 'requirements.txt' 'go.mod' 'Cargo.toml' \
       'pyproject.toml' '*.csproj' 'pom.xml' 'mix.exs' | head -50

# 2. DB-related decisions
git log --all --oneline --grep -E -i 'postgres|mysql|mongo|redis|sqlite|dynamo' | head -30

# 3. Deployment platform decisions
git log --all --oneline --grep -E -i 'deploy|kubernetes|cloud-run|fly|render|vercel|heroku' | head -30

# 4. Auth / security decisions
git log --all --oneline --grep -E -i 'auth|jwt|session|oauth|saml' | head -20
```

Triangulate with the team: "What three things do people ask about most often?"

### Typical high-value backfill candidates

| ADR # | Decision shape | Why it earns its place |
| --- | --- | --- |
| 0002 | Framework choice (e.g., Next.js over Remix) | Agent reaches for wrong framework conventions otherwise |
| 0003 | Database choice (e.g., Postgres over MySQL) | Affects schema design, query patterns |
| 0004 | Deployment platform (e.g., Cloud Run, not k8s) | Affects observability, CI, ops |
| 0005 | Auth provider (e.g., Auth0 over rolling our own) | Affects security model, user model |
| 0006 | Module boundaries (e.g., monorepo, not split repos) | Affects refactor blast radius |

### Backfill ADR template

Backfill ADRs **explicitly mark themselves as backfilled**. The team didn't go through the ADR process at the time — that's fine, just be honest.

```markdown
# 2. Use Postgres over MySQL

Date: 2026-04-27 (decision made: 2024-03-12; backfilled retroactively)

## Status
Accepted

## Context
[Reconstructed from git log + PR #142 + memory of who was around. Some
of the original constraint analysis is unrecoverable; this ADR captures
the load-bearing context.]

In Q1 2024, we needed a relational database for the user-account service.
Drivers: JSONB for flexible user-profile fields, mature partitioning for
the multi-tenant rollout, team familiarity (3 of 5 had Postgres experience).

## Decision
Postgres 15. Hosted on RDS in us-east-1.

## Consequences
- Locked into Postgres dialect (we use JSONB ops + LATERAL joins).
- Migrating later requires schema rewrite + data backfill.
- Connection pool management is a known op concern (see
  `.brain/postmortems/2026-04-12-checkout-outage.md`).
```

The "(decision made: ... ; backfilled retroactively)" tag is critical — tells the next reader the ADR isn't reconstructing perfect history, just the load-bearing summary.

**Stop at 3-5.** A 6th tempting backfill is usually scope creep. Add to the backlog and let it appear when someone next touches the relevant area.

## Step 4 — Wire AGENTS.md Memory primitives

If AGENTS.md doesn't have a `Memory primitives` section, add one. If it does, add the ADR pointer:

```markdown
## Where to find things
(...)
- **Architecture Decision Records:** `.brain/adrs/` (index: `.brain/adrs/README.md`)

## Memory primitives
- **Before architectural decisions**, read `.brain/adrs/` newest-first.
  If your proposed change conflicts with an `Accepted` ADR, write a new
  ADR superseding it; don't silently override.
```

Without this section, the ADRs exist but the agent doesn't know to read them — single most-common loop break (see `continuous-learning-loop.md`).

## Step 5 — Update the PR template

Add the architectural-impact checkbox to `.github/pull_request_template.md`:

```markdown
## Architectural impact
- [ ] No architectural change (no ADR needed)
- [ ] Architectural change — ADR added at: `.brain/adrs/NNNN-*.md`
- [ ] Architectural change — ADR exemption granted by: [name]
      Reason: [why no ADR]
```

Optionally add the auto-detection CI workflow from `continuous-learning-loop.md` that warns when architectural files change without an accompanying ADR.

## Step 6 — Brief the team

One paragraph. Post in #engineering:

> We've added `.brain/adrs/` for architectural decisions. New decisions that change framework / DB / deployment / auth / module boundaries get an ADR alongside the PR. The PR template has a checkbox to remind. We've backfilled 5 historical ones (Postgres, Cloud Run, Next.js, Auth0, monorepo). Format is MADR 4.0.0 — see `.brain/adrs/README.md`. AGENTS.md now points to this folder so LLM agents read it before architectural changes.

Don't send a 500-word memo — short, factual, links.

## Verification checklist

- [ ] `.brain/adrs/` exists with `README.md` index
- [ ] `0001-record-architecture-decisions.md` is `Accepted`
- [ ] 3-5 backfill ADRs landed, each marked retroactive in the date line
- [ ] AGENTS.md `Where to find things` references `.brain/adrs/`
- [ ] AGENTS.md `Memory primitives` instructs newest-first reading
- [ ] `.github/pull_request_template.md` has architectural-impact checkbox
- [ ] Team brief sent

## When to choose Nygard vs MADR vs Y-statements

| Format | When to use |
| --- | --- |
| **Nygard** (Title / Date / Status / Context / Decision / Consequences) | Small teams, fast cadence, straightforward decisions |
| **MADR 4.0.0** (adds Deciders / Considered Options / Decision Drivers) | Larger teams, audit-trail matters, multi-option |
| **Y-statements** (Zimmermann SATURN 2012) | One-line reversible choices; or summary atop a longer ADR |

The audit treats all three as valid; `../doc-types/adr-pattern.md` covers detection.

## Common mistakes

- **Backfilling everything.** Past 5 ADRs you're doing archaeology, not setup.
- **No bootstrap ADR.** Without `0001`, future contributors don't know whether ADRs are mandatory.
- **Backfill ADRs that pretend they were written contemporaneously.** Reads as historical revisionism.
- **Adding ADRs but not the AGENTS.md pointer.** Corpus exists; agent doesn't read it.
- **PR template without the checkbox.** New decisions don't get captured.

## Cross-references

- ADR pattern (templates, anti-patterns, audit checks): `../doc-types/adr-pattern.md`
- Memory organization (where ADRs sit relative to runbooks/postmortems): `memory-organization.md`
- Greenfield setup (the day-one version): `greenfield-setup.md`
- Continuous-learning loop (the system this plugs into): `continuous-learning-loop.md`
- AGENTS.md Memory primitives section: `../standards/agents-md-spec.md`
