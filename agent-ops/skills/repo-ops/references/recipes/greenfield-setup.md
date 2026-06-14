---
date: 2026-04-27
coverage: canonical
peers:
  - audit-existing-repo.md
  - adr-introduction.md
  - memory-organization.md
  - self-healing-hooks.md
  - continuous-learning-loop.md
primary_sources:
  - https://agents.md
  - https://github.com/typicode/husky
  - https://pre-commit.com/
  - https://adr.github.io/madr/
  - https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions
  - https://code.claude.com/docs/en/best-practices
status: research-verified
---

# Recipe: greenfield setup (delivers all 5 promises from day one)

> **The premise.** A new repo has no legacy debt — no fat CLAUDE.md, no orphan docs, no scattered decisions. This is the _only_ moment the repo can ship with all five promises pre-installed. Skip this and you'll be doing `audit-existing-repo.md` in six months.
>
> **Not a new repo?** If your repo is older than ~3 months and has any documentation at all, use `cold-start-harvest.md` instead. That recipe handles the inventory + triage + supersede pattern this one skips.
>
> **Existing `docs/` layout?** If you already have `docs/adrs/`, `docs/postmortems/`, etc., the v1.5 `.agents/brain/` layout is opt-in — both are recognized by the audit. The migration is one `git mv` documented in `audit-existing-repo.md` § Migration.

## What this recipe delivers

| Promise | Delivered by |
| --- | --- |
| 1. Less-wasteful | One canonical entry file, thin pointers, no duplicated commands |
| 2. Token-and-context-optimized | AGENTS.md ≤150 lines from day one; layered docs |
| 3. Less-prone-to-staleness | `_Last reviewed:_` lines, frontmatter dates, lychee CI |
| 4. Self-healing | Pre-commit hooks + PR-time CI + scheduled weekly audit |
| 5. Continuously-learning | ADR `0001` bootstrap, PR template architectural-impact checkbox, Memory primitives section |

## Step 1 — `AGENTS.md` skeleton (Promise 1, 2)

Use the recommended structure from `../standards/agents-md-spec.md`. Drop in the 8-section skeleton, customize what's true for the repo, target **80-120 lines**:

```markdown
# AGENTS.md

This file gives instructions to LLM coding agents (Codex, Devin, Cursor,
Windsurf, Copilot, Aider, Continue, Jules, Junie — and Claude Code via
symlink/pointer) working in this repo.

_Last reviewed: 2026-04-27_

## Project overview          (one paragraph)
## Build / test / run        (commands)
## Conventions               (bullet list)
## Trust boundaries          (DO NOT modify / DO modify)
## Where to find things      (pointers to .agents/brain/)
## Memory primitives         (when to read ADRs / postmortems)
```

Verify with `wc -l AGENTS.md`. The pre-commit hook from Step 5 will fail it past 200.

## Step 2 — `CLAUDE.md` as symlink (Promise 1)

Claude Code does not read AGENTS.md natively as of April 2026 (issue [#31005](https://github.com/anthropics/claude-code/issues/31005)). Symlink is cleanest:

```bash
ln -s AGENTS.md CLAUDE.md
git add CLAUDE.md
```

Windows + WSL teams often hit symlink-in-git issues — fall back to the thin-pointer alternative from `../standards/claude-md-convention.md`. Either is fine; never have both files fat.

## Step 3 — `.agents/brain/` directory tree + `.gitignore` (Promise 2, 5)

```bash
mkdir -p .agents/brain/{adrs,postmortems,runbooks,archive,architecture}
touch .agents/brain/{adrs,postmortems,runbooks,archive,architecture}/.gitkeep
```

Add an index `README.md` in each memory home (~10-20 lines each, `_Last reviewed:_` stamped). See `memory-organization.md` for the rationale on which folders go where and what each index file contains.

Then add transient-state homes to `.gitignore`. `.agents/brain/cache/` is the WebFetch cache populated by external-reference verification. `.agents/brain/cold-start/working/` is the harvest-session scratch space. The persistent state (`adrs/`, `postmortems/`, `runbooks/`, `archive/`, `architecture/`, `audit-history/`, `changesets/`, `config.toml`) gets committed.

```bash
cat >> .gitignore << 'EOF'

# repo-ops transient state
.agents/brain/cache/
.agents/brain/cold-start/working/
EOF
```

> **Want `.agents/brain/` entirely local?** Set `mode = "local-only"` in `.agents/brain/config.toml` and gitignore the whole `.agents/brain/` directory (instead of just the cache/cold-start subdirs). See `../guidance/reliability-dial.md` § Git sync. Promise 5 then applies to your local clone only — multi-contributor recipes and the auto-archive PR workflow become moot.

## Step 4 — Bootstrap ADR `0001` (Promise 5)

The first ADR records the decision to use ADRs. Without it, the practice itself isn't decided. Use the Nygard format ([cognitect.com 2011](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)); template in `../doc-types/adr-pattern.md`:

```markdown
# 1. Record architecture decisions

Date: 2026-04-27

## Status
Accepted

## Context
We need to record architectural decisions made on this project so future
contributors (human and LLM agent) can understand why the codebase looks
the way it does.

## Decision
We will use Architecture Decision Records as described by Michael Nygard.
ADRs live in `.agents/brain/adrs/` as `NNNN-kebab-case-title.md` with a `Status:`
field. The collection is the decision log.

## Consequences
- Architectural decisions are captured at decision time, not retroactively.
- New contributors read `.agents/brain/adrs/` newest-first to understand commitments.
- Decisions become harder to silently override — supersession requires a new ADR.
```

Save as `.agents/brain/adrs/0001-record-architecture-decisions.md`. Update `.agents/brain/adrs/README.md`.

## Step 5 — Pre-commit hooks + CI (Promise 3, 4)

Install the full stack from `self-healing-hooks.md`:

```bash
cp ~/.repo-brain-templates/.pre-commit-config.yaml .
mkdir -p scripts && cp ~/.repo-brain-templates/scripts/*.sh scripts/
chmod +x scripts/*.sh

pip install pre-commit && pre-commit install

mkdir -p .github/workflows
cp ~/.repo-brain-templates/.github/workflows/*.yml .github/workflows/
```

Five files land: `.pre-commit-config.yaml`, `scripts/check-agents-claude-drift.sh`, `scripts/check-doc-dates.sh`, `.github/workflows/repo-brain-pr.yml`, `.github/workflows/repo-brain-weekly.yml`. The verbatim contents are in `self-healing-hooks.md`.

Citations: [pre-commit.com](https://pre-commit.com/), [Husky](https://github.com/typicode/husky) (Node monocultures), [Lychee](https://github.com/lycheeverse/lychee-action).

## Step 6 — PR template (Promise 5)

The architectural-impact checkbox closes the continuous-learning loop. Drop in `.github/pull_request_template.md`:

```markdown
## What
[summary]

## Why
[motivation]

## Architectural impact
- [ ] No architectural change (no ADR needed)
- [ ] Architectural change — ADR added at: `.agents/brain/adrs/NNNN-*.md`
- [ ] Architectural change — ADR exemption granted by: [name]
      Reason: [why no ADR]

## Docs touched
- [ ] AGENTS.md updated if conventions / commands changed
- [ ] ADR added if architectural commitment made
- [ ] Runbook added if new ops procedure introduced
```

See `continuous-learning-loop.md` for the auto-detection workflow that warns when architectural files change without an accompanying ADR.

## Step 7 — `_Last reviewed:_` lines (Promise 3)

Every doc gets a date — YAML frontmatter `date:` or inline `_Last reviewed: YYYY-MM-DD_`. The greenfield seed:

```bash
TODAY=$(date +%F)
for f in AGENTS.md README.md CONTRIBUTING.md SECURITY.md .agents/brain/**/*.md; do
    [ -f "$f" ] || continue
    grep -q "_Last reviewed:" "$f" || \
        printf "\n_Last reviewed: %s_\n" "$TODAY" >> "$f"
done
```

The pre-commit hook from Step 5 enforces this on future edits.

## Step 8 — `.agents/brain/config.toml` (optional: tune the strictness dial)

The hooks installed in Step 5 default to `strictness = "normal"`. To tune up or down, drop a `.agents/brain/config.toml`:

```toml
[repo-ops]
strictness = "normal"  # lax | normal | strict
version = "1.1"
```

- **`lax`** — side projects, prototypes (warnings, no blocking)
- **`normal`** — most production repos (default)
- **`strict`** — regulated codebases, monorepos (every trip-wire blocks; multi-agent review for apply-mode fixes)

See `../guidance/reliability-dial.md` for what each position changes per trip-wire. Skip this step entirely to use `normal` defaults — `.agents/brain/config.toml` is an override, not a requirement.

## Step 9 — Verification checklist

- [ ] `AGENTS.md` exists, ≤150 lines, has all 8 sections
- [ ] `CLAUDE.md` is a symlink to `AGENTS.md` OR a ≤15-line pointer
- [ ] `.agents/brain/{adrs,postmortems,runbooks,archive,architecture}/` exist with README index files
- [ ] `.agents/brain/adrs/0001-record-architecture-decisions.md` is `Accepted`
- [ ] `.gitignore` excludes `.agents/brain/cache/` and `.agents/brain/cold-start/working/`
- [ ] `.pre-commit-config.yaml` present; `pre-commit install` ran
- [ ] `scripts/check-*.sh` present and executable
- [ ] `.github/workflows/repo-brain-{pr,weekly}.yml` present
- [ ] `.github/pull_request_template.md` has architectural-impact checkbox
- [ ] Every `.md` has `_Last reviewed:_` or YAML `date:`
- [ ] `README.md` references `AGENTS.md` once (no duplicated build commands; see `../standards/readme-conventions.md`)
- [ ] (Optional) `.agents/brain/config.toml` present if non-default strictness desired
- [ ] `pre-commit run --all-files` passes

12 boxes ticked → all 5 promises ship from day one.

## First commit message

```text
chore: bootstrap repo-brain-compliant doc surface

- AGENTS.md (canonical), CLAUDE.md → symlink
- .agents/brain/{adrs,postmortems,runbooks,archive,architecture}/
- .gitignore for .agents/brain/cache/, .agents/brain/cold-start/working/
- ADR 0001 — Record architecture decisions
- pre-commit hooks (drift, length, doc-date)
- CI (PR-time link-check + weekly audit)
- PR template with architectural-impact checkbox

Delivers all 5 repo-ops promises from day one.
```

## Common greenfield mistakes

- **Setting up `CLAUDE.md` as canonical.** Works for Claude Code only; other agents (Codex, Cursor, Devin, Copilot) ignore it. Always make AGENTS.md canonical.
- **Skipping ADR 0001.** Without the bootstrap, the next contributor wonders if ADRs are required.
- **Pre-commit installed but not run.** `pre-commit install` writes `.git/hooks/pre-commit`; clones don't pick it up. Document the install in `CONTRIBUTING.md`.
- **Lychee with `fail: false` on PR.** Defeats the gate. `fail: true` on PR; `fail: false` only in scheduled audits.
- **Stamping `_Last reviewed:_` programmatically and never touching it again.** The date should be re-stamped on real edits, not just the seed.
- **Committing `.agents/brain/cache/` or `.agents/brain/cold-start/working/`.** Transient state belongs in `.gitignore`.

## Cross-references

- AGENTS.md spec (the skeleton's source): `../standards/agents-md-spec.md`
- CLAUDE.md convention: `../standards/claude-md-convention.md`
- README/CONTRIBUTING/SECURITY conventions: `../standards/readme-conventions.md`
- ADR pattern: `../doc-types/adr-pattern.md`
- Self-healing hooks (Step 5 detail): `self-healing-hooks.md`
- Continuous-learning loop (Step 6 detail): `continuous-learning-loop.md`
- Memory organization (folder layout rationale): `memory-organization.md`
- Token-budget rationale for length caps: `../guidance/context-budget.md`
- Migration recipe for existing `docs/` layouts: `audit-existing-repo.md` § Migration
