---
date: 2026-04-27
coverage: canonical
peers:
  - continuous-learning-loop.md
  - audit-existing-repo.md
  - ../audit-patterns/staleness-tooling.md
  - ../audit-patterns/redundancy-detection.md
primary_sources:
  - https://github.com/lycheeverse/lychee-action
  - https://github.com/typicode/husky
  - https://pre-commit.com/
  - https://docs.github.com/actions/using-workflows/triggering-a-workflow
  - https://djw.fyi/portfolio/preventing-drift/
status: research-verified
---

# Self-healing hooks (delivers Promise 4)

> **The premise.** A repo without trip-wires can't honor the "self-healing" promise — it can only be clean today and rotten tomorrow. This recipe installs the hooks that catch breakage before it lands and the workflows that keep watch on a schedule.

## What "self-healing" means concretely

A self-healing repo:

1. **Refuses to merge PRs** that introduce drift between CLAUDE.md and AGENTS.md.
2. **Refuses to merge PRs** with broken intra-repo or external links in `.brain/` or `docs/`.
3. **Refuses commits** that bloat AGENTS.md / CLAUDE.md past the 200-line ceiling.
4. **Auto-archives** orphaned docs after a 30-day grace period.
5. **Surfaces stale content** weekly (scheduled CI), not on a someone-remembered-to-look basis.
6. **Captures decisions** at the moment of decision (ADR-on-architectural-change), not retroactively.

The first three are pre-commit / PR-time gates. The fourth is a scheduled workflow. The fifth is a scheduled audit. The sixth is a `continuous-learning-loop.md` flow.

## The hook stack

### Layer 1 — pre-commit hooks (local; catch problems before they leave the machine)

Use `pre-commit` (Python) or `husky` (Node). The skill recommends `pre-commit` for cross-language repos and `husky` for Node-monoculture.

#### pre-commit (`.pre-commit-config.yaml`)

```yaml
# .pre-commit-config.yaml
repos:
  # Lint Markdown structure
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.42.0
    hooks:
      - id: markdownlint
        files: '\.(md|MD)$'

  # Repo-brain trip-wires (custom, local hooks)
  - repo: local
    hooks:
      # Trip-wire 1: AGENTS.md / CLAUDE.md must not drift
      - id: agents-claude-drift
        name: AGENTS.md / CLAUDE.md must not have drifted prose
        entry: bash -c 'bash scripts/check-agents-claude-drift.sh'
        language: system
        files: '^(AGENTS\.md|CLAUDE\.md)$'
        pass_filenames: false

      # Trip-wire 2: AGENTS.md / CLAUDE.md must stay <200 lines
      - id: entry-file-length
        name: Entry files <200 lines (warn at 150)
        entry: bash -c 'for f in AGENTS.md CLAUDE.md; do if [ -f "$f" ] && [ ! -L "$f" ]; then n=$(wc -l <"$f"); if [ "$n" -gt 200 ]; then echo "ERROR: $f is $n lines (>200)"; exit 1; elif [ "$n" -gt 150 ]; then echo "WARN: $f is $n lines (>150)"; fi; fi; done'
        language: system
        pass_filenames: false

      # Trip-wire 3: docs in .brain/ or docs/ must have a date
      - id: doc-frontmatter-date
        name: .brain/*.md and docs/*.md must have date frontmatter or "Last reviewed:" line
        entry: bash -c 'bash scripts/check-doc-dates.sh'
        language: system
        files: '^(\.brain|docs)/.*\.md$'
        pass_filenames: true
```

#### `scripts/check-agents-claude-drift.sh`

```bash
#!/usr/bin/env bash
# Trip-wire: AGENTS.md and CLAUDE.md must not have drifted prose.
# Pass cases:
#   (a) CLAUDE.md is a symlink to AGENTS.md → identical content.
#   (b) CLAUDE.md is a thin pointer (≤15 lines) referencing AGENTS.md.
#   (c) AGENTS.md exists, CLAUDE.md does not.
# Fail: both exist as fat (>15 lines) divergent files.

set -euo pipefail

if [ ! -f AGENTS.md ] && [ ! -f CLAUDE.md ]; then
    exit 0  # Neither exists; not this hook's problem
fi

if [ ! -f AGENTS.md ]; then
    echo "ERROR: CLAUDE.md exists but AGENTS.md does not. Promote CLAUDE.md → AGENTS.md."
    exit 1
fi

if [ ! -f CLAUDE.md ]; then
    exit 0  # AGENTS.md only; fine
fi

# CLAUDE.md is a symlink? (clean)
if [ -L CLAUDE.md ]; then
    target="$(readlink CLAUDE.md)"
    if [ "$target" = "AGENTS.md" ]; then
        exit 0
    else
        echo "ERROR: CLAUDE.md is a symlink to '$target', not AGENTS.md."
        exit 1
    fi
fi

# CLAUDE.md is thin? (clean)
claude_lines=$(wc -l < CLAUDE.md)
if [ "$claude_lines" -le 15 ]; then
    if grep -q -i "AGENTS\.md" CLAUDE.md; then
        exit 0
    else
        echo "ERROR: CLAUDE.md is short but doesn't reference AGENTS.md."
        exit 1
    fi
fi

# Both fat → drift risk.
echo "ERROR: Both AGENTS.md ($(wc -l <AGENTS.md) lines) and CLAUDE.md ($claude_lines lines) are fat."
echo "       Demote one to a thin pointer or symlink. See repo-ops/standards/claude-md-convention.md."
exit 1
```

#### `scripts/check-doc-dates.sh`

```bash
#!/usr/bin/env bash
# Trip-wire: every .brain/*.md and docs/*.md must have a date.
set -euo pipefail
fail=0
for f in "$@"; do
    if grep -qE '^date:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$f"; then
        continue  # YAML frontmatter date OK
    fi
    if grep -qE '_Last reviewed:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$f"; then
        continue  # Inline "Last reviewed:" line OK
    fi
    echo "ERROR: $f has no date frontmatter or 'Last reviewed:' line."
    fail=1
done
exit $fail
```

### Layer 2 — PR-time CI (catch problems before merge)

#### `.github/workflows/repo-brain-pr.yml`

```yaml
name: Repo-brain (PR)

on:
  pull_request:
    paths: ['**.md', '.brain/**', 'docs/**', 'AGENTS.md', 'CLAUDE.md', '.cursor/**', '.windsurfrules', '.github/copilot-instructions.md']

jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lychee link check
        uses: lycheeverse/lychee-action@v2
        with:
          args: --cache --max-cache-age=1d --no-progress '.brain/**/*.md' 'docs/**/*.md' '*.md'
          fail: true

  drift-and-length:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/check-agents-claude-drift.sh
      - run: bash scripts/check-entry-file-length.sh

  doc-dates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: |
          changed=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- '.brain/**/*.md' 'docs/**/*.md' || true)
          if [ -n "$changed" ]; then
            bash scripts/check-doc-dates.sh $changed
          fi

  llm-doc-drift:
    if: ${{ vars.LLM_DOC_DRIFT_ENABLED == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Ask LLM if code diff requires doc updates
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: bash scripts/llm-doc-drift-check.sh
```

The `llm-doc-drift` job is opt-in (gated on `vars.LLM_DOC_DRIFT_ENABLED`) — costs API calls per PR. Worth it for high-traffic repos; overkill for hobby projects.

### Layer 3 — scheduled CI (find problems no commit triggered)

#### `.github/workflows/repo-brain-weekly.yml`

```yaml
name: Repo-brain (weekly audit)

on:
  schedule:
    - cron: '0 13 * * 1'  # Mondays 13:00 UTC
  workflow_dispatch:

jobs:
  full-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: External link check (full)
        uses: lycheeverse/lychee-action@v2
        with:
          args: --no-progress '.brain/**/*.md' 'docs/**/*.md' '*.md'
          fail: false  # Don't fail; report

      - name: Stale-doc detection (mtime + frontmatter)
        run: bash scripts/find-stale-docs.sh > stale-report.md

      - name: Orphan detection
        run: bash scripts/find-orphan-docs.sh > orphan-report.md

      - name: Open issue if findings
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const stale = fs.readFileSync('stale-report.md', 'utf8');
            const orphans = fs.readFileSync('orphan-report.md', 'utf8');
            if (stale.trim() || orphans.trim()) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `[repo-ops] Weekly audit findings — ${new Date().toISOString().slice(0,10)}`,
                body: `## Stale docs\n\n${stale}\n\n## Orphans\n\n${orphans}`,
                labels: ['docs', 'repo-ops']
              });
            }
```

### Layer 4 — auto-archive (the orphan grace-period flow)

#### `scripts/find-orphan-docs.sh`

```bash
#!/usr/bin/env bash
# Find docs in .brain/ or docs/ not referenced by any entry file or other doc.
set -euo pipefail
all_docs=$(find .brain docs -type f -name '*.md' 2>/dev/null)
referenced=$(
  cat AGENTS.md CLAUDE.md README.md .brain/**/*.md docs/**/*.md 2>/dev/null \
  | grep -oE '\[[^]]+\]\(([^)]+)\)' \
  | grep -oE '\(([^)]+)\)' \
  | tr -d '()' \
  | sort -u
)
for f in $all_docs; do
    base=$(basename "$f")
    # Disambiguate shared basenames (the two-README.md-in-different-dirs false negative):
    # if >1 doc shares this basename, match on parent-dir/basename so a link to one does
    # not falsely mark the other "referenced." grep -F keeps the match a literal.
    if [ "$(printf '%s\n' $all_docs | grep -cF "/$base")" -gt 1 ]; then
        needle=$(printf '%s' "$f" | rev | cut -d/ -f1-2 | rev)   # parent-dir/basename
    else
        needle="$base"
    fi
    if ! printf '%s\n' "$referenced" | grep -qF "$needle"; then
        # Orphan candidate. (Residual: a unique basename that is a substring of an
        # unrelated referenced path can still false-negative; resolving links to repo-
        # relative paths is the full fix.)
        last_modified=$(git log -1 --format=%cs -- "$f")
        echo "- $f (last modified: $last_modified)"
    fi
done
```

#### `.github/workflows/repo-brain-auto-archive.yml`

```yaml
name: Repo-brain (auto-archive orphans after 30-day grace)
on:
  schedule:
    - cron: '0 13 * * 1'  # Mondays
  workflow_dispatch:

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Move stale orphans to .brain/archive/
        run: |
          # An orphan unmodified for 30+ days AND not in /archive/ → archive it.
          while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            f=$(echo "$line" | cut -d' ' -f2)
            [[ "$f" == .brain/archive/* ]] && continue
            [[ "$f" == docs/archive/* ]] && continue
            mtime=$(git log -1 --format=%ct -- "$f")
            now=$(date +%s)
            age_days=$(( (now - mtime) / 86400 ))
            if [ "$age_days" -gt 30 ]; then
              mkdir -p .brain/archive
              git mv "$f" ".brain/archive/$(basename "$f")"
              echo "Archived: $f (orphan for ${age_days}d)"
            fi
          done < <(bash scripts/find-orphan-docs.sh)
      - name: Open PR
        uses: peter-evans/create-pull-request@v6
        with:
          base: main           # see the gotcha below — required for tag-push triggers
          title: '[repo-ops] Auto-archive stale orphan docs'
          body: 'Auto-archived orphan docs untouched for 30+ days. Review and merge or revert.'
          branch: repo-ops/auto-archive
```

The PR step is critical — **never silently delete or move docs**. Always open a PR so a human can review.

### Gotcha — `peter-evans/create-pull-request` needs `base: main` on tag-push

If your workflow also triggers on tag pushes (e.g., a build-log harvest that fires on every release tag), the GitHub Actions runner checks out the _tag_ — which is a detached HEAD, not a branch. Without an explicit `base` input, `create-pull-request` exits with:

```text
##[error]When the repository is checked out on a commit instead of a branch,
the 'base' input must be supplied.
```

**Symptom**: every tag-push run of the workflow fails at the PR-opening step. Cron and `workflow_dispatch` runs (which check out the branch) succeed; tag-push runs fail. The audit ledger drops entries silently — the harvester writes the JSON, but the PR never opens, so the entry never lands on `main`.

**Fix**: always set `base: main` (or your default branch). It's a no-op on cron / dispatch runs (the action would auto-detect `main` anyway) and load-bearing on tag-push runs.

Observed in the wild on 2026-04-28 — a build-log workflow at `adiahealth/gen-ui-kit` failed for 8 consecutive tag-push runs because the action wouldn't open the PR. The cron path worked but the entry sat in an unmerged PR (`repo-ops/build-log` branch) for 2 days, so the ledger appeared frozen at the last manually-merged entry. The fix is one line.

## What the audit verifies

Self-healing has **two halves** — _presence_ (the trip-wire exists) and _liveness_ (it has actually fired recently). Presence without liveness is a config that ships green and rots: a `.pre-commit-config.yaml` nobody ran `pre-commit install` on, or a workflow that's been failing silently. The audit checks both.

**Presence** — the trip-wire is wired:

1. ✅ `.pre-commit-config.yaml` exists OR `.husky/` has equivalent hooks.
2. ✅ The `agents-claude-drift`, `entry-file-length`, `doc-frontmatter-date` hooks are wired.
3. ✅ `.github/workflows/repo-brain-pr.yml` (or equivalent) exists and includes lychee.
4. ✅ `.github/workflows/repo-brain-weekly.yml` (or equivalent scheduled audit) exists.
5. ✅ `scripts/check-agents-claude-drift.sh` and the other helper scripts exist.

**Liveness** — the trip-wire has _fired_ within its freshness window. Each run (pre-commit, PR CI, weekly CI) appends a record to the audit-history ledger:

```json
{ "kind": "trip-wire-fired", "trip_wire": "pre-commit|repo-brain-pr|repo-brain-weekly",
  "at": "2026-05-30T13:00:00Z", "result": "pass" }
```

The audit then confirms, per promised trip-wire, that a `trip-wire-fired` record exists within its window — routed by the reliability dial (`../guidance/reliability-dial.md` § resolver, row "trip-wire liveness window": lax 90d / normal 30d / strict 8d):

1. ✅ a pre-commit firing within the window (else the hooks are present but **never installed/run**).
2. ✅ a `repo-brain-weekly` firing within the window (else the scheduled audit is silently dead).

A trip-wire **present but with no recent firing** emits a `STALE TRIP-WIRE` finding (severity routed by the dial) — distinct from `MISSING TRIP-WIRE`. This is what makes "self-healing" mean _demonstrably healing_, not _clean today by luck_. A trip-wire missing entirely is still `MISSING TRIP-WIRE` (severity = high).

## Common anti-patterns

- **Hooks defined but not installed** — `.pre-commit-config.yaml` exists but no one ran `pre-commit install`. The **liveness check catches this**: a present hook with no `trip-wire-fired` record in its window is flagged `STALE TRIP-WIRE` (present ≠ installed). (Installing the hook is still a `setup` step in `recipes/greenfield-setup.md`.)
- **Auto-archive without PR step** — silently moving files breaks links. Always go through PR.
- **Lychee with `fail: false` everywhere** — defeats the gate. Use `fail: true` on PR; `fail: false` only on scheduled audits where issue-opening is the action.
- **No grace period on orphans** — files get archived on the first scan after they go orphaned. 30 days is the recommended floor.

## Cross-references

- Continuous-learning loop (Promise 5): `continuous-learning-loop.md`
- Staleness tooling deep dive: `../audit-patterns/staleness-tooling.md`
- Redundancy detection: `../audit-patterns/redundancy-detection.md`
- Full audit recipe: `audit-existing-repo.md`
