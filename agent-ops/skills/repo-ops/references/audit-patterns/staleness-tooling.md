---
date: 2026-04-27
coverage: extended
peers:
  - stale-content.md
  - pointer-validation.md
  - ../guidance/llm-doc-writing.md
primary_sources:
  - https://github.com/lycheeverse/lychee — fast Markdown/HTML link checker (Rust)
  - https://github.com/lycheeverse/lychee-action — GitHub Action
  - https://vale.sh/ — markup-aware prose linter
  - https://github.com/DavidAnson/markdownlint — Markdown structure linter
  - https://djw.fyi/portfolio/preventing-drift/ — Daryl White, "Avoiding the Silent Stale Doc Problem"
  - https://docuwriter.ai/ — commercial code-doc-drift product
status: research-verified
---

# Tooling for staleness detection

> **What to actually run** when the audit needs help finding stale links, broken references, prose smells, and code/doc drift. The skill itself implements the simplest checks (existence, last-modified, broken pointers); for deeper coverage, reach for these tools.

## Link checking — `lychee`

**`lychee`** ([lycheeverse/lychee](https://github.com/lycheeverse/lychee)) is a fast Markdown/HTML/RST/text link checker written in Rust. It's the de-facto standard.

Run locally:

```bash
lychee --offline --no-progress '.brain/**/*.md' 'docs/**/*.md' '*.md' '*.MD'
# --offline skips network; useful for fast intra-repo link audit
# drop --offline to also check external URLs
```

GitHub Actions:

```yaml
# .github/workflows/links.yml
name: Links
on:
  pull_request: { paths: ['**.md'] }
  schedule: [{ cron: '0 0 * * 1' }]  # Mondays
jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --cache --max-cache-age=1d --no-progress '.brain/**/*.md' 'docs/**/*.md' '*.md'
          fail: true
```

The cache is essential — without it, GitHub rate-limits external link checks quickly.

Older alternative: `markdown-link-check` (Node). Slower; lychee is preferred.

## Prose linting — `Vale`

**`Vale`** ([vale.sh](https://vale.sh/)) is a markup-aware prose linter — used by Datadog, Grafana, Elastic, Microsoft, and others. Custom rule packs let you enforce a style guide (sentence length, weasel words, branding terms, Markdown conventions).

Useful for the audit only when the project has a content style guide. If not, skip.

```bash
vale .brain/ docs/
```

## Markdown structure linting — `markdownlint`

**`markdownlint`** ([DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint)) checks Markdown structure (heading levels, list indentation, blank lines, etc.). Doesn't check freshness; complements lychee.

```bash
markdownlint .brain/ docs/ *.md
```

## Code/doc drift detection — the genuinely hard one

There's no canonical OSS tool for "this code change should have updated this doc." Two pragmatic approaches in 2026:

### LLM-on-diff (the popular DIY)

Per [Daryl White's "Avoiding the Silent Stale Doc Problem"](https://djw.fyi/portfolio/preventing-drift/): a GitHub Action that, on each PR, asks an LLM whether the code diff requires doc updates and which docs.

Sketch:

```yaml
# .github/workflows/doc-drift.yml
name: Doc drift
on: pull_request
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: |
          git diff origin/${{ github.base_ref }}...HEAD --stat > /tmp/diff.txt
          # Pipe /tmp/diff.txt + AGENTS.md + .brain/ + docs/ index into an LLM that
          # returns "no doc changes needed" or "consider updating: <list>".
          # Post as a PR comment.
```

This is bespoke per project but cheap to maintain.

### DocuWriter.ai (commercial)

[docuwriter.ai](https://docuwriter.ai/) — uses git diff webhooks + LLM analysis to flag doc-relevant code changes. Useful for large repos where the DIY pattern is too noisy.

## Git-heuristic staleness (DIY, baseline)

The simplest staleness signal: file last-modified date. The skill itself can implement this directly:

```bash
# Files in .brain/ + docs/ older than 6 months without a "Last reviewed" line:
find .brain docs -name '*.md' -mtime +180 | while read f; do
  if ! grep -q '_Last reviewed:' "$f"; then
    echo "STALE: $f (last modified: $(git log -1 --format=%cs -- "$f"))"
  fi
done
```

Use `git log` mtime rather than filesystem mtime — filesystem mtime can be misleading after `git clone` or rebase.

## Composing the staleness pass

Recommended order:

1. **Existence + entry-file pointers** (skill internal) — what does the entry say, what's actually there
2. **lychee** — flag broken intra-repo and external links
3. **markdownlint** — flag structural issues
4. **Git-heuristic mtime check** — flag undated docs older than threshold
5. **Vale** (if project has style guide) — flag prose smells
6. **LLM-on-diff** (in CI, ongoing) — flag PRs that should have updated docs

The first four are fast; run them on every audit. The last two are slower / more bespoke; run them in CI.

## What to put in the audit report

For each stale finding:

```markdown
- **STALE — `docs/architecture.md`** (severity: medium)
  - Last modified: 2024-09-12 (583 days ago).
  - No `_Last reviewed:_` line.
  - References `class FooHandler` which was renamed to `RequestHandler` in commit `abc123` (2025-03-15).
  - **Tools that flagged this:**
    - mtime-heuristic (older than 6mo, undated)
    - intra-repo grep (referenced symbol no longer exists)
  - **Recommendation:** review and re-date, OR archive to `.brain/archive/architecture-2024.md`.
```

## Cross-references

- General staleness audit pattern: `stale-content.md`
- Pointer validation: `pointer-validation.md`
- LLM-doc-writing guidance: `../guidance/llm-doc-writing.md`
- Full audit recipe: `../recipes/audit-existing-repo.md`
