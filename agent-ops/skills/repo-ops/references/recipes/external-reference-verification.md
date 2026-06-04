---
date: 2026-04-27
coverage: canonical
peers:
  - ../audit-patterns/stale-content.md
  - ../audit-patterns/staleness-tooling.md
  - recommend-then-validate.md
  - ../audit-patterns/audit-history-ledger.md
primary_sources:
  - https://github.com/karpathy/autoresearch — autonomous propose-evaluate-iterate (spirit-source)
  - https://github.com/lycheeverse/lychee — link checker (the *liveness* check this recipe complements)
status: research-verified
---

# External-reference verification (WebFetch-powered)

> _"You're not touching any of the Python files like you normally would as a researcher. Instead, you are programming the `program.md` Markdown files that provide context to the AI agents."_ — Andrej Karpathy, [autoresearch](https://github.com/karpathy/autoresearch)

The premise: **`lychee` tells you a link is broken; it doesn't tell you the live link points to outdated content.** External-reference verification fetches the current state of cited URLs, library docs, and spec pages, compares to what the doc claims, and proposes specific corrections.

This recipe imports autoresearch's _spirit_ (focused research-survey question → fetch → evaluate → propose) into repo-fixer, scoped to the one place where its loop genuinely fits: external-reference verification.

## What it catches that other staleness tools miss

| Tool | Catches | Doesn't catch |
| --- | --- | --- |
| `lychee` | Dead links (404s, timeouts) | Live links pointing to outdated content |
| Git-mtime heuristic | Old files | New files with stale facts |
| LLM-on-diff | Code-doc drift in _this_ repo | External-world drift |
| **External-ref verification** | "AGENTS.md cites Promise.try as Stage 3; MDN now shows Stage 4 shipped" | (this — the gap the others leave) |

Examples of what it catches:

- "Use Node 18+" — Node 24 has been LTS for a year
- "ES2022 features" — should be ES2025 now
- "GitHub Copilot doesn't read AGENTS.md" — it does (since 2025-08-28)
- Cited library version that's three majors behind
- TC39 proposal Stage that's advanced
- WCAG / ARIA spec citation pointing at a superseded version

## The loop (autoresearch DNA)

```text
1. SCAN
   - Audit emits STALE-EXTERNAL-REF findings (per audit-patterns/stale-content.md)
   - Each finding: { file, line, cited_url, current_claim }

2. FETCH    ← the autoresearch step
   - For each finding, WebFetch the cited URL or canonical doc
   - Extract the current state (version, status, behavior)
   - Cap fetches per audit run (default: 30) to bound cost

3. COMPARE
   - ALIGNED: doc matches reality → no fix
   - STALE: doc disagrees with reality → propose fix
   - AMBIGUOUS: can't tell → flag for manual review

4. PROPOSE
   - Build a specific edit including:
     - File + line
     - Original text
     - Replacement text
     - Source URL + fetch date

5. VALIDATE (per recommend-then-validate.md)
   - Dry-run the edit against trip-wires
   - Verify the source URL is not on a deny-list

6. PR
   - Opens with verified corrections
   - Each correction cites the source URL it was verified against
```

## Sample finding → fix output

```markdown
## STALE-EXTERNAL-REF (severity: medium)

**File:** docs/POLYFILLS.md:47
**Cited URL:** https://github.com/tc39/proposal-promise-try
**Current claim in doc:** "Promise.try is at Stage 3"
**Verified state (fetched 2026-04-27):** "Stage 4, shipping in Chrome 128 / Safari 18.2 / Firefox 134"

**Proposed correction:**
- Line 47: replace "Stage 3" with "Stage 4 (shipping Chrome 128 / Safari 18.2 /
  Firefox 134, per [tc39/proposal-promise-try](https://github.com/tc39/proposal-promise-try)
  accessed 2026-04-27)"

**Validator check:** PASS (no broken links introduced; no entry-file length impact)
```

## Configuration

`.brain/config.toml`:

```toml
[repo-ops.external-ref-verification]
enabled = false                   # default: opt-in
max_fetches_per_run = 30          # cost ceiling
fetch_timeout_seconds = 15
cache_days = 7                    # share fetches across same-week audits
deny_list = ["pastebin.com", "*.s3.amazonaws.com/private-*"]
allow_list_only = false
allowed_domains = []              # used only when allow_list_only=true
```

Disabled by default — fetching costs money and time, and most repos don't need verification on every audit. Enable for repos with substantive external-reference surface (API integrations, browser-support tables, framework-version docs, language-spec citations).

## How autoresearch DNA maps in (and where it stops)

Autoresearch is **overnight hill-climbing on a single file with a single metric**, fully unattended. This recipe is **a focused research-survey probe per finding**, bounded and reviewed:

| Autoresearch | This recipe |
| --- | --- |
| Iterates over `train.py` | Iterates over external-ref findings |
| Metric: `val_bpb` | Metric: cited claim matches fetched reality (yes/no/ambiguous) |
| Search through candidates | One probe per finding (no candidate search) |
| Overnight unattended | Single CI run, human-reviewed PR |
| Hill-climbing | Direct lookup |

We import the _spirit_ — autonomous propose-evaluate within a budget, with WebFetch as the eval mechanism. We don't import the loop shape. Yegge-aligned shepherding stays intact.

## When to use it

- Docs that cite external APIs, frameworks, libraries, or specs (e.g., `expert-polyfills`-style reference repos)
- Quarterly cadence is enough for most teams (scheduled GitHub Action, not every PR)
- Useful for "stop external-world rot" — the audit history ledger then shows trend data on how often external refs go stale

## When NOT to use it

- **Internal-only repos** with no external citations
- **Cost-sensitive contexts** where 30 fetches per audit is a meaningful expense
- **Heavy-fetch repos** where the cap would miss most references — split into per-doc audits instead
- **Privacy-sensitive content** where fetching cited URLs leaks repo-internal information

## Privacy & cost considerations

- Don't fetch URLs from `.brain/postmortems/` (may contain incident-specific URLs that shouldn't leave the network)
- Don't fetch URLs matching common internal-hostname patterns
- Cap default at 30 fetches/run; tune via `max_fetches_per_run`
- Cache aggressively — same URL, same week, same result (the 15-minute WebFetch cache is too short for multi-doc audits; recipe layer adds a 7-day cache by default)

## Anti-patterns

- **Fetching URLs without rate limiting.** Respect retry-after headers and the deny list.
- **Trusting the fetch blindly.** Fetched pages can themselves be stale (caching, mirrors). Pair with frontmatter dates on the citation.
- **Including fetched content verbatim in the PR.** Cite + summarize; don't dump pages of HTML.
- **Running on every PR.** Quarterly or weekly is usually right; the audit history ledger surfaces the trend.
- **Verifying without recording the fetch date.** Without a date, the corrected claim is itself unverifiable a year from now.

- **Fetching external content and writing fixes in the same agent context.** The agent that reads a fetched page and the agent that writes to AGENTS.md share a context window. Injected content in a fetched page (an attacker-controlled CDN, a redirected domain) can influence the writing step. Mitigation: treat all fetched page text as data only — extract the specific fact being verified, discard the rest. The recommend-then-validate pattern already provides partial structural isolation (the validator runs in a fresh context without the fetched content). Do not allow fetched prose to enter the correction text verbatim.

## Cross-references

- Stale-content audit pattern (the input): `../audit-patterns/stale-content.md`
- Recommend-then-validate (consumer pattern): `recommend-then-validate.md`
- Staleness tooling (lychee, Vale, markdownlint): `../audit-patterns/staleness-tooling.md`
- Audit history ledger (where verified-fix metadata lands): `../audit-patterns/audit-history-ledger.md`
- Reliability dial (where the fetch budget gets tuned per strictness): `../guidance/reliability-dial.md`
