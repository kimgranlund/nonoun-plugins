---
date: 2026-04-27
coverage: canonical
peers:
  - orphan-detection.md
  - token-waste-detection.md
  - ../standards/claude-md-convention.md
  - ../recipes/self-healing-hooks.md
primary_sources:
  - https://github.com/anthropics/claude-code/issues/31005
status: research-verified
---

# Redundancy detection (delivers Promise 1, "less-wasteful")

> **The premise.** Redundancy is waste _and_ drift waiting to happen. Two files saying "use pnpm" will, eventually, disagree — one will say `pnpm`, the other will say `npm` after a sloppy edit. The audit's job is to detect redundancy _before_ it drifts.

## What this pattern catches

Five classes of redundancy:

| Class | Example | Severity |
| --- | --- | --- |
| **Drift between entry files** | CLAUDE.md and AGENTS.md both fat with substantively different content | Critical |
| **Repeated commands** | Build commands listed in AGENTS.md, README.md, AND CONTRIBUTING.md | Medium |
| **Repeated facts** | "We use Postgres" stated in AGENTS.md, ARCHITECTURE.md, AND README.md | Low |
| **Verbose-vs-tabular duplication** | Same conventions written as prose AND as a table later in the same file | Low |
| **Generated content checked in alongside source** | API reference markdown alongside the docstrings it was generated from | Medium |

## Drift between entry files (the critical case)

This is the audit's single most-important check. Claude Code reads CLAUDE.md, every other agent reads AGENTS.md natively (per `cross-tool-matrix.md`). When the two files contain different instructions, the team has two failure modes simultaneously:

1. **Claude Code follows out-of-date rules** (because CLAUDE.md is stale).
2. **Cursor/Codex/Devin follow out-of-date rules** (because AGENTS.md is stale).

The fix is the canonical model from this skill: AGENTS.md fat, CLAUDE.md as symlink or thin pointer.

### Detection logic

```bash
# Pseudocode for the drift check
if [ ! -f AGENTS.md ] || [ ! -f CLAUDE.md ]; then
    # No drift possible
    exit 0
fi

if [ -L CLAUDE.md ] && [ "$(readlink CLAUDE.md)" = "AGENTS.md" ]; then
    # Symlink → identical content
    exit 0
fi

claude_lines=$(wc -l < CLAUDE.md)
if [ "$claude_lines" -le 15 ] && grep -qi 'AGENTS.md' CLAUDE.md; then
    # Thin pointer → no fat content to drift
    exit 0
fi

# Both fat → drift risk; emit finding
echo "DRIFT — CLAUDE.md ($claude_lines lines) vs AGENTS.md ($(wc -l <AGENTS.md) lines)"
echo "  Diff highlights:"
diff <(grep -v '^$' CLAUDE.md) <(grep -v '^$' AGENTS.md) | head -20
```

The full hook is in `../recipes/self-healing-hooks.md`.

### Recipe to fix

```bash
# Pick AGENTS.md as canonical (recommended).
# Move CLAUDE.md content into AGENTS.md, deduplicating.
# Then:

# Option A: symlink (cleanest)
rm CLAUDE.md
ln -s AGENTS.md CLAUDE.md
git add CLAUDE.md
git commit -m 'docs: CLAUDE.md → symlink to AGENTS.md (eliminate drift)'

# Option B: thin pointer (works on Windows, no symlink quirks)
cat > CLAUDE.md <<'EOF'
# CLAUDE.md

This repo's instructions for LLM coding agents live in [`AGENTS.md`](./AGENTS.md).
Please read that file. The contents apply identically to Claude Code.

_Last reviewed: 2026-04-27_
EOF
git add CLAUDE.md
git commit -m 'docs: CLAUDE.md → thin pointer to AGENTS.md'
```

## Repeated commands

A common pattern: build/test/run commands appear in AGENTS.md, README.md, and CONTRIBUTING.md. Each is true at the moment of writing; one will eventually drift.

### Detection

````bash
# Heuristic: extract code-fenced shell blocks from each file, hash them, find duplicates.
for f in AGENTS.md README.md CONTRIBUTING.md .agents/brain/**/*.md docs/**/*.md; do
    [ -f "$f" ] || continue
    awk '/^```(bash|sh|shell)/,/^```$/' "$f" | sha256sum | awk -v f="$f" '{print f, $1}'
done | sort -k2 | awk '{
    if ($2 == prev_hash) print "DUPLICATE: " prev_file " <-> " $1;
    prev_file = $1; prev_hash = $2
}'
````

Tighter heuristic: parse out individual commands (lines starting with `$` or matching `pnpm|npm|yarn|cargo|go run`) and find which appear in multiple files.

### Fix recipe

Pick a canonical home (AGENTS.md is typical). Other files reference it:

```markdown
# README.md (excerpt)

## Build / test / run

See [`AGENTS.md`](./AGENTS.md) for build, test, and run commands.
```

```markdown
# CONTRIBUTING.md (excerpt)

## Local setup

For build / test / run commands, see [`AGENTS.md`](./AGENTS.md). For
contribution conventions, continue below.
```

The agent reads AGENTS.md every session anyway, so this isn't a navigation cost.

## Repeated facts

Lower severity: same fact ("we use Postgres") appears in 3 places. The fact rarely changes, so drift risk is low — but tokens are wasted on each load.

### Detection

This is hard to automate well — paraphrased duplicates evade hashing. Practical approach: look for _named entities_ (technology names, version numbers, named services) that appear in multiple top-level docs, and surface as "consider consolidating."

```bash
# Heuristic: find tech names that appear in 3+ entry-level docs
grep -l -i -E '\b(postgres|mysql|redis|kafka|s3|aws|gcp|azure)\b' \
    AGENTS.md README.md CONTRIBUTING.md ARCHITECTURE.md 2>/dev/null \
    | sort | uniq -c | sort -rn | awk '$1 >= 3 { print "POSSIBLE-REDUNDANCY: " $2 }'
```

Treat as advisory; humans decide whether to consolidate.

## Verbose-vs-tabular duplication within one file

A surprisingly common pattern: AGENTS.md says

> "We use TypeScript with strict mode enabled. Our test runner is Vitest. We use Conventional Commits for commit messages. ESLint is configured for our coding style."

...and then _also_ has:

```markdown
| Tool | Choice |
|---|---|
| Language | TypeScript (strict) |
| Tests | Vitest |
| Commits | Conventional |
| Linting | ESLint |
```

Both communicate the same facts. Cut the prose, keep the table — bullets/tables are denser and the agent prefers them.

### Detection

Hard. Practical heuristic: flag files with both `^>` blockquotes longer than 100 chars AND a Markdown table covering similar content. Manual review.

## Generated content checked in

If the project generates API reference markdown (TypeDoc, sphinx, mkdocs-jsdoc, rustdoc → md, etc.), don't check in the output:

```text
# .gitignore (excerpt)
docs/api/                       # generated by `pnpm docs:generate`
docs/typedoc/                   # generated by TypeDoc
```

The audit signal: many `.md` files in `docs/api/` or `docs/typedoc/` that look auto-generated (template-driven structure, very uniform front-matter, mass-modified in single commits). These get loaded as orphan candidates by the orphan-detection pass — but the right fix is `.gitignore`, not archive.

## Severity rubric

| Finding | Severity | Why |
| --- | --- | --- |
| AGENTS.md / CLAUDE.md drift (both fat, divergent) | Critical | Causes Claude Code and other agents to follow different rules |
| Repeated build commands across 3+ files | Medium | High drift risk over time |
| Repeated facts (named entities) across 3+ docs | Low | Drift risk lower; tokens wasted |
| Verbose+tabular duplication in same file | Low | Internal redundancy; advisory |
| Generated content checked in | Medium | Bloats repo, confuses orphan detection |

## What this pattern is NOT for

- **Repeated _links_** are good. Linking to AGENTS.md from README.md is fine — it's _not_ duplicating content, it's pointing to it.
- **Repeated section headers** (every ADR has a "Status:" section) are not redundancy — they're structural convention.
- **Repeated examples** in docs (e.g., the same `pnpm install` shown in a setup walkthrough) are not redundancy if each appears in a different procedural context.

## Cross-references

- Orphan detection (sibling Promise 1 audit): `orphan-detection.md`
- Token-waste detection (sibling Promise 2 audit): `token-waste-detection.md`
- CLAUDE.md thin-pointer recipe: `../standards/claude-md-convention.md`
- Self-healing hooks (where the drift trip-wire lives): `../recipes/self-healing-hooks.md`
- Concurrent learnings merge (uses this trip-wire as the post-merge backstop): `../recipes/concurrent-learnings-merge.md`
- Cold-start harvest (uses this trip-wire to detect imported conflicts in phase 5): `../recipes/cold-start-harvest.md`
