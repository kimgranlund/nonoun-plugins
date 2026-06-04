---
date: 2026-04-27
coverage: canonical
peers:
  - redundancy-detection.md
  - ../guidance/context-budget.md
  - ../guidance/llm-doc-writing.md
  - ../recipes/self-healing-hooks.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices
  - https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
status: research-verified
---

# Token-waste detection (delivers Promise 2, "token-and-context-optimized")

> **The premise.** A token loaded into context is a token not available for the work being done. Every byte of AGENTS.md / CLAUDE.md / loaded docs has to _earn its place_ — by changing agent behavior in a way no other doc does. This audit catches the bytes that aren't earning.

## The five token-waste smells

| # | Smell | What it looks like | Severity |
| --- | --- | --- | --- |
| 1 | **Bloated entry file** | AGENTS.md or CLAUDE.md > 200 lines | High |
| 2 | **Bloated subfolder doc** | `docs/<not-adrs-or-postmortems>/<file>.md` > 500 lines | Medium |
| 3 | **Verbose prose** | Long paragraphs where bullets / tables work | Low |
| 4 | **Cross-doc repetition** | Same content in 3+ files | Medium (handled in `redundancy-detection.md`) |
| 5 | **Redundant frontmatter / boilerplate** | Long YAML frontmatter, license headers, generated tables of contents in every file | Low |

## Smell 1 — bloated entry files (the critical one)

**The check:** `wc -l AGENTS.md CLAUDE.md`. Anthropic's published guidance is `<200 lines`; we warn at 150 and fail at 200.

**Why it matters:** entry files are loaded _every session_. A 400-line AGENTS.md costs ~5K tokens _every time the agent starts work_. Across a hundred sessions in a year, that's 500K tokens spent on metadata — a meaningful chunk of any per-developer LLM budget, before doing any work.

**Auto-detection:**

```bash
# Pre-commit hook (also in self-healing-hooks.md)
for f in AGENTS.md CLAUDE.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    n=$(wc -l < "$f")
    if [ "$n" -gt 200 ]; then
        echo "ERROR: $f is $n lines (>200). See guidance/context-budget.md."
        exit 1
    elif [ "$n" -gt 150 ]; then
        echo "WARN: $f is $n lines (>150). Consider compression."
    fi
done
```

**Fix recipe:** see `../guidance/context-budget.md` "How to reduce a bloated AGENTS.md (the recipe)" — the 8-step compression pass typically takes a 600-line entry file to 150 without losing instructional value.

## Smell 2 — bloated subfolder docs

**The check:** `find .brain docs -name '*.md' -not -path '.brain/adrs/*' -not -path '.brain/postmortems/*' -not -path '.brain/architecture/*'` and any file with `wc -l > 500`.

**Why it matters:** unlike entry files, subfolder docs aren't loaded every session — but a bloated `docs/setup.md` (1200 lines) is a sign the doc has become a dumping ground rather than a focused unit. Split into a folder.

**Exceptions:**

- `.brain/adrs/<one>.md` can be any length — one ADR captures one decision in full.
- `.brain/postmortems/<one>.md` can be any length — incidents need depth.
- `.brain/architecture/<one>.md` may be long; consider splitting into multiple files in the folder if so.
- `CHANGELOG.md` is append-only; it grows without bound.

**Auto-detection:**

```bash
find .brain docs -name '*.md' -type f \
    -not -path '.brain/adrs/*' \
    -not -path '.brain/postmortems/*' \
    -not -path '.brain/architecture/*' \
    -not -path '.brain/archive/*' \
    | while read f; do
        n=$(wc -l < "$f")
        if [ "$n" -gt 500 ]; then
            echo "$f: $n lines (consider splitting into a folder)"
        fi
    done
```

**Fix recipe:** if `docs/setup.md` is 1200 lines covering "first-time setup", "deployment", "troubleshooting", "FAQ" — split:

```text
docs/setup/
├── README.md           (~30 lines: index)
├── first-time.md       (~150)
├── deployment.md       (~200)
├── troubleshooting.md  (~300)
└── faq.md              (~150)
```

Update entry-file pointers from `docs/setup.md` → `docs/setup/`.

## Smell 3 — verbose prose

**The check:** prose-vs-bullet ratio. A heuristic: paragraphs longer than 4 sentences, especially in the `Conventions` or `Build` sections of AGENTS.md, are usually compressible.

**Why it matters:** the agent doesn't need narrative — it needs constraints. "We use TypeScript with strict mode enabled because we value type safety and prefer to catch errors at compile time rather than runtime" is twice the tokens of "TypeScript: strict" and worse for the agent.

**Auto-detection:** hard to automate cleanly. Practical approach: a script that flags any AGENTS.md / CLAUDE.md paragraph >300 characters as a review candidate.

```bash
# Find long paragraphs (>300 chars between blank lines) in AGENTS.md
awk -v RS='' -v ORS='\n\n' '{ if (length($0) > 300 && !/^#/) print NR": "$0 }' AGENTS.md
```

**Fix recipe:** convert prose to bullets or tables. Test: can you read it as instructions to follow? If yes, bullets. If no (it's actually motivation/context), move to a different file.

## Smell 4 — cross-doc repetition

Detailed in `redundancy-detection.md`. Token cost is 2× / 3× / Nx of the same content loaded N times.

## Smell 5 — redundant frontmatter / boilerplate

**The check:** YAML frontmatter that's longer than 5-10 lines per file, or boilerplate (license headers, "this file is auto-generated", boilerplate ToCs) that adds bytes without information.

**Why it matters:** small per-file but it adds up. A 50-line license header in every doc, across 80 docs, is 4000 lines of pure tax.

**Auto-detection:**

```bash
# Find files with YAML frontmatter >10 lines
for f in .brain/**/*.md docs/**/*.md *.md; do
    [ -f "$f" ] || continue
    if head -1 "$f" | grep -q '^---'; then
        end=$(awk '/^---/{i++; if(i==2) print NR}' "$f")
        [ -n "$end" ] && [ "$end" -gt 12 ] && echo "$f: frontmatter is $end lines"
    fi
done
```

**Fix recipe:**

- Trim YAML frontmatter to: `date`, `coverage`, `peers`, `primary_sources`, `status`. That's it.
- Move license headers into a single `LICENSE` file at the root (which is the convention anyway).
- Generate ToCs at render time, not commit time. (For GitHub-rendered docs, the GitHub UI renders the ToC; don't commit one.)

## What does NOT count as token waste

- **Long ADRs** — one architectural decision captured in full is the right shape; don't compress for its own sake.
- **Long post-mortems** — incidents with complex root causes need depth.
- **Long CHANGELOG.md** — append-only history.
- **Long ARCHITECTURE.md (within reason)** — under ~1500 lines, the depth is earning its tokens. Past that, split.
- **Code examples** — if an example illustrates a non-obvious pattern, it's earning its place. If it's restating something obvious, cut it.

## The full audit pass

```bash
# 1. Entry file length
for f in AGENTS.md CLAUDE.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    n=$(wc -l < "$f")
    [ "$n" -gt 150 ] && echo "ENTRY-FILE-LENGTH: $f = $n lines"
done

# 2. Subfolder bloat
find .brain docs -name '*.md' -type f \
    -not -path '.brain/adrs/*' \
    -not -path '.brain/postmortems/*' \
    -not -path '.brain/architecture/*' \
    -not -path '.brain/archive/*' \
    | while read f; do
        n=$(wc -l < "$f")
        [ "$n" -gt 500 ] && echo "SUBFOLDER-BLOAT: $f = $n lines"
    done

# 3. Verbose prose in entry files
for f in AGENTS.md CLAUDE.md; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    awk -v f="$f" -v RS='' '{ if (length($0) > 300 && !/^#/) print "VERBOSE-PARA: "f": "substr($0,1,80)"..." }' "$f"
done

# 4. Frontmatter bloat
for f in $(find . -name '*.md' -type f -not -path '*/node_modules/*'); do
    head -1 "$f" 2>/dev/null | grep -q '^---' || continue
    end=$(awk '/^---/{i++; if(i==2){ print NR; exit }}' "$f")
    [ -n "$end" ] && [ "$end" -gt 12 ] && echo "FRONTMATTER-BLOAT: $f = $end lines"
done
```

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| Entry file >200 lines | High | Loaded every session; per-session waste |
| Entry file 150-200 | Medium | Approaching ceiling |
| Subfolder doc >500 (non-ADR/postmortem) | Medium | One-off cost when loaded; structural smell |
| Verbose prose in entry file | Low | Per-session waste, individually small |
| Frontmatter bloat | Low | Per-file waste, individually small |

## Cross-references

- Context budget (the math behind these limits): `../guidance/context-budget.md`
- Redundancy detection (cross-doc repetition): `redundancy-detection.md`
- LLM-doc-writing (content-quality companion): `../guidance/llm-doc-writing.md`
- Self-healing hooks (where these checks run automatically): `../recipes/self-healing-hooks.md`
