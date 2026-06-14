---
date: 2026-04-27
coverage: canonical
peers:
  - entry-file-coverage.md
  - redundancy-detection.md
  - token-waste-detection.md
  - staleness-tooling.md
  - ../doc-types/adr-pattern.md
  - ../doc-types/postmortem-pattern.md
  - ../recipes/self-healing-hooks.md
  - ../recipes/continuous-learning-loop.md
primary_sources:
  - https://agents.md — AGENTS.md canonical spec (AAIF / Linux Foundation, Aug 2025)
  - https://adr.github.io/ — Architectural Decision Records
  - https://github.com/joelparkerhenderson/architecture-decision-record
  - https://sre.google/sre-book/postmortem-culture/ — Google SRE Book, postmortem culture
  - https://increment.com/on-call/whats-the-incident/ — Incident response patterns
status: research-verified
---

# Coverage gaps (delivers Promise 1, "less-wasteful" + Promise 5, "continuously-learning")

> **The premise.** A repo without an AGENTS.md is invisible to multi-tool agents; a repo without ADRs has no memory of why anything is the way it is; a repo without postmortems is condemned to relearn the same outage. This audit catches the _missing_ canonical files — not the bloated ones, not the stale ones, the ones that aren't there at all.

## Why this is Promise 1 + Promise 5

| Promise | Why missing canonicals violate it |
| --- | --- |
| **1. Less-wasteful** | An agent that can't find AGENTS.md re-derives conventions every session. A missing CHANGELOG forces every agent into `git log` archaeology. |
| **5. Continuously-learning** | Without ADRs, decisions evaporate after PRs merge. Without postmortems, the org relearns the same outage. |

Sibling `entry-file-coverage.md` checks that AGENTS.md/CLAUDE.md/.cursorrules are well-formed. _This_ pattern checks the broader canonical set.

## The expected canonical set

| Tier | Path | Severity if missing | Why |
| --- | --- | --- | --- |
| **Required** | `AGENTS.md` | Critical | Multi-tool entry point; without it, no agent knows the repo |
| **Required** | `CLAUDE.md` (or symlink → `AGENTS.md`) | Critical | Claude Code does not read AGENTS.md natively (issue #31005) |
| **Required** | `README.md` | High | Human + LLM landing; GitHub renders it; first thing every search hits |
| **Required** | `CHANGELOG.md` | High | Append-only history; without it, "what changed" is git-archaeology |
| **Required** | `.agents/brain/adrs/` | Medium | Decision memory; promise 5 home |
| **Conditional** | `.agents/brain/postmortems/` | Medium _if production-facing_ | Incident memory; only meaningful if the repo deploys |
| **Recommended** | `ARCHITECTURE.md` | Low | Big-picture reference (matklad pattern, repo root); substitutable with well-organized ADRs |
| **Recommended** | `PLAN.md` | Low | Forward-looking roadmap; substitutable with issues |
| **Recommended** | `.agents/brain/runbooks/` | Low _if production-facing_ | Operational memory; on-call counterpart to postmortems |
| **Recommended** | `CONTRIBUTING.md` | Low | Contributor guide; collapsible into AGENTS.md |
| **Recommended** | `SECURITY.md` | Low | Vuln-disclosure pointer; GitHub surfaces it natively |

The conditional tier triggers on the production-facing heuristic below. The recommended tier is advisory — emit a finding, don't fail the audit.

## The production-facing heuristic

Postmortems and runbooks only matter if the repo runs in production. The audit infers production-facing from any of:

| Signal | What it says |
| --- | --- |
| `Dockerfile` (or `Containerfile`) | Builds a container — likely deployable |
| `.github/workflows/*deploy*.yml` (or `*release*.yml`, `*publish*.yml`) | CI deploys this |
| `kubernetes/`, `k8s/`, `helm/`, `charts/` | Deploys to k8s |
| `terraform/`, `*.tf`, `pulumi/`, `cdk.json` | Manages live infrastructure |
| `fly.toml`, `vercel.json`, `netlify.toml`, `render.yaml`, `railway.json`, `app.yaml` | Deploys to a PaaS |
| `serverless.yml`, `sam.yaml`, `template.yaml` | Deploys serverless |

Any one signal flips the conditional tier on. Library-only repos skip postmortems and runbooks — but still get ADRs.

## Detection logic

```bash
#!/usr/bin/env bash
# coverage-gaps.sh — emit findings for missing canonical docs
set -euo pipefail

emit() {
  # severity, path, message
  printf 'COVERAGE-GAP\t%s\t%s\t%s\n' "$1" "$2" "$3"
}

# 1. Required tier — always checked
[ -f AGENTS.md ] || emit critical AGENTS.md \
  "No AGENTS.md at repo root. Multi-tool agents have no entry point."

if [ ! -f CLAUDE.md ] && [ ! -L CLAUDE.md ]; then
  emit critical CLAUDE.md \
    "No CLAUDE.md (Claude Code does not read AGENTS.md natively as of Apr 2026). Symlink or thin pointer required."
fi

[ -f README.md ] || emit high README.md \
  "No README.md at repo root. Human and LLM landing surface missing."

[ -f CHANGELOG.md ] || emit high CHANGELOG.md \
  "No CHANGELOG.md. 'What changed lately' becomes git-archaeology for every agent."

[ -d .agents/brain/adrs ] || [ -d docs/adrs ] || [ -d docs/adr ] || [ -d docs/decisions ] || emit medium .agents/brain/adrs/ \
  "No ADR directory. Decision memory will evaporate after PRs merge. (Promise 5)"

# 2. Conditional tier — production-facing check
production=false
for signal in Dockerfile Containerfile fly.toml vercel.json netlify.toml \
              render.yaml railway.json app.yaml serverless.yml sam.yaml \
              template.yaml docker-compose.prod.yml cdk.json pulumi.yaml; do
  [ -e "$signal" ] && production=true && break
done
[ "$production" = false ] && compgen -G ".github/workflows/*deploy*"  >/dev/null 2>&1 && production=true
[ "$production" = false ] && compgen -G ".github/workflows/*release*" >/dev/null 2>&1 && production=true
[ "$production" = false ] && compgen -G ".github/workflows/*publish*" >/dev/null 2>&1 && production=true
[ "$production" = false ] && [ -d kubernetes ] && production=true
[ "$production" = false ] && [ -d k8s ]        && production=true
[ "$production" = false ] && [ -d helm ]       && production=true
[ "$production" = false ] && [ -d terraform ]  && production=true
[ "$production" = false ] && compgen -G "*.tf" >/dev/null 2>&1 && production=true

if [ "$production" = true ]; then
  [ -d .agents/brain/postmortems ] || [ -d docs/postmortems ] || [ -d docs/incidents ] || emit medium .agents/brain/postmortems/ \
    "Production-facing repo (deploy artifacts detected) but no postmortems directory. Incident memory will be lost. (Promise 5)"
  [ -d .agents/brain/runbooks ] || [ -d docs/runbooks ] || [ -d docs/operations ] || emit low .agents/brain/runbooks/ \
    "Production-facing repo but no runbooks directory. On-call response memory missing."
fi

# 3. Recommended tier — advisory only
[ -f ARCHITECTURE.md ] || emit low ARCHITECTURE.md \
  "No ARCHITECTURE.md. Big-picture reference missing (matklad pattern, repo root; substitutable with ADR set)."
[ -f PLAN.md ] || emit low PLAN.md \
  "No PLAN.md. Forward-looking roadmap missing (substitutable with issues)."
[ -f CONTRIBUTING.md ] || emit low CONTRIBUTING.md \
  "No CONTRIBUTING.md. Contributor guide can be collapsed into AGENTS.md for small repos."
[ -f SECURITY.md ] || emit low SECURITY.md \
  "No SECURITY.md. Vulnerability-disclosure pointer missing."
```

The output is one tab-separated finding per line, ready to fold into the audit report. The full hook lives in `../recipes/self-healing-hooks.md`.

## Output shape (the gap-report row)

```markdown
- **MISSING — `.agents/brain/postmortems/`** (severity: medium)
  - Production-facing: `Dockerfile`, `.github/workflows/deploy.yml`, `terraform/` present.
  - **Promise impact:** Promise 5 — the repo will relearn the same outage.
  - **Recommendation:** create `.agents/brain/postmortems/` from `../doc-types/postmortem-pattern.md`; backfill one recent incident.

- **MISSING — `CHANGELOG.md`** (severity: high)
  - **Promise impact:** Promise 1 — every agent re-derives "what changed lately" from `git log`.
  - **Recommendation:** Keep-a-Changelog format; seed with `## [Unreleased]` if history is unrecoverable.
```

## Substitution rules (when "missing" is actually OK)

The audit is opinionated, not pedantic. Three substitutions are accepted:

| Expected | Acceptable substitute | Why |
| --- | --- | --- |
| `.agents/brain/adrs/` | `docs/decisions/` or `docs/adr/` (legacy) | Naming variant; same content shape |
| `.agents/brain/postmortems/` | `docs/incidents/` (legacy) | Naming variant |
| `ARCHITECTURE.md` | Populated `.agents/brain/adrs/` of 5+ entries | ADRs collectively _are_ the architecture story |

## What this pattern is NOT for

- **Content quality** — coverage-gaps checks _presence_. `format-hygiene.md` and `stale-content.md` catch quality.
- **Bloated files** — `token-waste-detection.md` handles oversize.
- **Drift between two existing files** — `redundancy-detection.md` handles drift.
- **Orphans** — `orphan-detection.md` (sibling, Promise 1).

## Severity rubric (consolidated)

| Finding | Severity | Promise impacted |
| --- | --- | --- |
| AGENTS.md missing | Critical | 1 |
| CLAUDE.md missing (no symlink) | Critical | 1 |
| README.md missing | High | 1 |
| CHANGELOG.md missing | High | 1, 5 |
| `.agents/brain/adrs/` missing | Medium | 5 |
| `.agents/brain/postmortems/` missing (production-facing) | Medium | 5 |
| `.agents/brain/runbooks/` missing (production-facing) | Low | 5 |
| `ARCHITECTURE.md` missing | Low | 1 |
| `CONTRIBUTING.md`, `SECURITY.md`, `PLAN.md` | Low | advisory |

## Cross-references

- Entry-file shape (sibling audit, AGENTS.md/CLAUDE.md form): `entry-file-coverage.md`
- Format hygiene (does each canonical have the right shape?): `format-hygiene.md`
- Redundancy between existing canonicals: `redundancy-detection.md`
- Stale content within existing canonicals: `staleness-tooling.md`, `stale-content.md`
- ADR shape: `../doc-types/adr-pattern.md`
- Postmortem shape: `../doc-types/postmortem-pattern.md`
- Self-healing hook (where these checks run on commit): `../recipes/self-healing-hooks.md`
- Continuous learning loop (Promise 5 home): `../recipes/continuous-learning-loop.md`
